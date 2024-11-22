from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementId, Element, UnitUtils, DisplayUnitType
from Autodesk.Revit.DB.Structure import StructuralType
from pyrevit import script

# Function to convert cubic feet to cubic meters
def convert_to_cubic_meters(value):
    return UnitUtils.ConvertFromInternalUnits(value, DisplayUnitType.DUT_CUBIC_METERS)

# Material Densities (kg/m³)
STEEL_DENSITY = 7850  # Steel density in kg/m³
CONCRETE_DENSITY = 2400  # Concrete density in kg/m³

# Function to calculate weight of an element
def calculate_weight(element, density):
    volume = element.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble()
    volume_m3 = convert_to_cubic_meters(volume)
    weight_kg = volume_m3 * density
    return weight_kg

# Collect all structural framing and columns (Steel & Concrete)
def collect_structural_elements(doc):
    framing_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType()
    column_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType()
    return list(framing_collector) + list(column_collector)

# Main script execution
doc = __revit__.ActiveUIDocument.Document
output = script.get_output()

elements = collect_structural_elements(doc)
total_steel_weight = 0
total_concrete_weight = 0

for elem in elements:
    # Check the material of the element (Assuming that Steel or Concrete is part of the material name)
    material = elem.get_Parameter(BuiltInParameter.STRUCTURAL_MATERIAL_PARAM).AsValueString().lower()
    
    if "steel" in material:
        weight = calculate_weight(elem, STEEL_DENSITY)
        total_steel_weight += weight
    elif "concrete" in material:
        weight = calculate_weight(elem, CONCRETE_DENSITY)
        total_concrete_weight += weight

# Output results
output.print_md(f"**Total Weight of Steel Elements:** {total_steel_weight/1000:.2f} tonnes")
output.print_md(f"**Total Weight of Concrete Elements:** {total_concrete_weight/1000:.2f} tonnes")
