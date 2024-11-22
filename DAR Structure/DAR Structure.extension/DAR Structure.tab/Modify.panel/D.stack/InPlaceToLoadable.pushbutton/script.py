__title__ = "InPlaceToLoadable"
__doc__ = "Select an In-Place element to convert into a Loadable family and place it in the same location. " \
          "Subcategories will be respected."

from pyrevit import revit, DB, HOST_APP, forms, script
import tempfile
from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter
from Autodesk.Revit import Exceptions
from os.path import isfile

output = script.get_output()


# Selection filter for In-Place elements
class InPlaceFilter(ISelectionFilter):
    """Filter to allow selection of only In-Place elements."""
    def AllowElement(self, elem):
        try:
            if elem.Symbol.Family.IsInPlace:
                return True
            return False
        except AttributeError:
            return False

    def AllowReference(self, reference, position):
        return False


# Pick and Select Function
def pick_inplace_element():
    """Allows the user to pick an In-Place element directly in the model."""
    try:
        with forms.WarningBar(title="Pick an In-Place element to transform"):
            picked_ref = revit.uidoc.Selection.PickObject(ObjectType.Element, InPlaceFilter())
            selected_element = revit.doc.GetElement(picked_ref)
            return selected_element
    except Exceptions.OperationCanceledException:
        forms.alert("Selection canceled. Exiting script.", ok=True, warn_icon=False, exitscript=True)


# Helper functions
def get_fam_by_name_and_cat(some_name, category=DB.BuiltInCategory.OST_GenericModel):
    """Placeholder function for family retrieval."""
    return []


def sk_plane(curve):
    """Create a sketch plane for a given curve."""
    try:
        p1 = curve.Evaluate(0, True)
    except Exceptions.ArgumentOutOfRangeException:
        return None
    if isinstance(curve, DB.Line):
        p1 = curve.Evaluate(0, True)
        tangent = curve.ComputeDerivatives(0, True).BasisX
        normal = tangent.CrossProduct(p1)
        plane = DB.Plane.CreateByNormalAndOrigin(normal, p1)
        sketch_plane = DB.SketchPlane.Create(new_family_doc, plane)
    else:
        deriv = curve.ComputeDerivatives(1, True)
        normal = deriv.BasisZ.Normalize()
        plane = DB.Plane.CreateByNormalAndOrigin(normal, p1)
        sketch_plane = DB.SketchPlane.Create(new_family_doc, plane)
    return sketch_plane


def get_subcat_name(element):
    """Get the subcategory name of an element."""
    subcat_id = element.GraphicsStyleId
    if str(subcat_id) != "-1":
        return revit.doc.GetElement(subcat_id).Name
    else:
        return None


def inverted_transform_by_ref(reference):
    """Get the inverse transformation for a reference."""
    transform = DB.Transform.CreateTranslation(reference)
    return transform.Inverse


# Main script logic
source_element = pick_inplace_element()

solids_dict = {}
curves = []
geo_element = source_element.get_Geometry(DB.Options())
bb = geo_element.GetBoundingBox()
family_origin = bb.Min

for instance_geo in geo_element:
    geometry_element = instance_geo.GetInstanceGeometry()
    for geometry in geometry_element:
        if isinstance(geometry, DB.Solid) and geometry.Volume > 0:
            new_solid = DB.SolidUtils.CreateTransformed(geometry, inverted_transform_by_ref(bb.Min))
            solids_dict[new_solid] = get_subcat_name(geometry)
        elif isinstance(geometry, DB.Curve):
            new_curve = geometry.CreateTransformed(inverted_transform_by_ref(bb.Min))
            curves.append(new_curve)

el_cat_id = source_element.Category.Id.IntegerValue

# Language and template handling
language = "English"  # Placeholder for `database.get_family_template_language`
fam_template_path = None

# Simulate template retrieval
match_template_by_category_language = None
if match_template_by_category_language:
    fam_template_path = __revit__.Application.FamilyTemplatePath + match_template_by_category_language
else:
    fam_template_path = __revit__.Application.FamilyTemplatePath + "Generic Model.rft"

if not isfile(fam_template_path):
    forms.alert(title="No Generic Template Found", msg="Cannot find Generic Model Template.", ok=True)
    fam_template_path = forms.pick_file(file_ext="rft")

try:
    new_family_doc = revit.doc.Application.NewFamilyDocument(fam_template_path)
except:
    forms.alert(msg="No Template", sub_msg="Cannot open family template.", ok=True, warn_icon=True, exitscript=True)

project_number = revit.doc.ProjectInformation.Number or "000"
fam_name = "{}_{}".format(project_number, source_element.Symbol.Family.Name).strip(" ")

if get_fam_by_name_and_cat(fam_name):
    while get_fam_by_name_and_cat(fam_name):
        fam_name = "{}_Copy 1".format(fam_name)

fam_path = tempfile.gettempdir() + "/" + fam_name + ".rfa"
saveas_opt = DB.SaveAsOptions()
saveas_opt.OverwriteExistingFile = True
new_family_doc.SaveAs(fam_path, saveas_opt)

with revit.Transaction("Load Family", revit.doc):
    try:
        loaded_f = revit.db.create.load_family(fam_path, doc=revit.doc)
        revit.doc.Regenerate()
    except Exceptions.InvalidOperationException:
        forms.alert("Unable to Load Family", exitscript=True)

# Copy geometry
with revit.Transaction(doc=new_family_doc, name="Copy Geometry"):
    parent_cat = new_family_doc.OwnerFamily.FamilyCategory
    new_mat_param = None  # Placeholder for `database.add_material_parameter`
    for geometry, subcat_name in solids_dict.items():
        copied_geo = DB.FreeFormElement.Create(new_family_doc, geometry)
        if subcat_name:
            subcat = parent_cat.Subcategories.get_Item(subcat_name) or \
                     new_family_doc.Settings.Categories.NewSubcategory(parent_cat, subcat_name)
            copied_geo.Subcategory = subcat
    for curve in curves:
        if isinstance(curve, DB.Line) and sk_plane(curve):
            line_sk_plane = DB.SketchPlane.Create(new_family_doc, DB.Plane.CreateByNormalAndOrigin(
                curve.ComputeDerivatives(0, True).BasisX, curve.Evaluate(0, True)))
            new_family_doc.FamilyCreate.NewModelCurve(curve, line_sk_plane)
    new_family_doc.Regenerate()

save_opt = DB.SaveOptions()
new_family_doc.Save(save_opt)
new_family_doc.Close()

with DB.Transaction(revit.doc, "Reload Family") as t:
    t.Start()
    loaded_f = revit.db.create.load_family(fam_path, doc=revit.doc)
    revit.doc.Regenerate()
    if not loaded_f:
        t.RollBack()
        forms.alert("Error loading family", exitscript=True)
    fam_symbol = None
    get_fam = DB.FilteredElementCollector(revit.doc).OfClass(DB.FamilySymbol).WhereElementIsElementType().ToElements()
    for fam in get_fam:
        if fam.get_Parameter(DB.BuiltInParameter.SYMBOL_NAME_PARAM).AsString().strip() == fam_name:
            fam_symbol = fam
            if not fam_symbol.IsActive:
                fam_symbol.Activate()
                revit.doc.Regenerate()
    new_fam_instance = revit.doc.Create.NewFamilyInstance(family_origin, fam_symbol, DB.Structure.StructuralType.NonStructural)
    t.Commit()

print("Created and placed family instance: {}".format(fam_name))
