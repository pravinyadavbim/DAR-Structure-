import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitServices")

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Get the current document and UI document
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = uiapp.ActiveUIDocument

def split_column_by_levels(column, levels):
    """Split a column by levels."""
    column_location = column.Location
    if not isinstance(column_location, LocationCurve):
        return []  # Only split columns with LocationCurve

    curve = column_location.Curve
    base_level_id = column.LookupParameter("Base Level").AsElementId()
    base_offset = column.LookupParameter("Base Offset").AsDouble()
    top_level_id = column.LookupParameter("Top Level").AsElementId()
    top_offset = column.LookupParameter("Top Offset").AsDouble()

    # Calculate base and top elevations
    base_level = doc.GetElement(base_level_id)
    top_level = doc.GetElement(top_level_id)
    base_elevation = base_level.Elevation + base_offset
    top_elevation = top_level.Elevation + top_offset

    # Filter levels within the column's range
    levels_in_range = [lvl for lvl in levels if base_elevation < lvl.Elevation < top_elevation]
    levels_in_range.sort(key=lambda lvl: lvl.Elevation)

    new_columns = []
    start_point = curve.GetEndPoint(0)

    # Split at each level
    for lvl in levels_in_range:
        mid_point = XYZ(start_point.X, start_point.Y, lvl.Elevation)
        new_curve = Line.CreateBound(start_point, mid_point)
        new_column = doc.Create.NewFamilyInstance(new_curve, column.Symbol, column.StructuralType)
        new_columns.append(new_column)
        start_point = mid_point

    # Create the final segment
    final_curve = Line.CreateBound(start_point, curve.GetEndPoint(1))
    final_column = doc.Create.NewFamilyInstance(final_curve, column.Symbol, column.StructuralType)
    new_columns.append(final_column)

    # Delete the original column
    doc.Delete(column.Id)

    return new_columns

try:
    # Get selected elements
    selected_ids = uidoc.Selection.GetElementIds()
    if not selected_ids:
        raise Exception("No elements selected. Please select one or more structural columns.")

    selected_elements = [doc.GetElement(el_id) for el_id in selected_ids]
    structural_columns = [el for el in selected_elements if isinstance(el, FamilyInstance) and el.StructuralType == StructuralType.Column]

    if not structural_columns:
        raise Exception("No valid structural columns selected. Please select structural columns.")

    # Get all levels in the document
    all_levels = FilteredElementCollector(doc).OfClass(Level).ToElements()

    # Start a transaction to modify the model
    TransactionManager.Instance.EnsureInTransaction(doc)

    # Split each selected column by levels
    for column in structural_columns:
        split_column_by_levels(column, all_levels)

    TransactionManager.Instance.TransactionTaskDone()

    # Show completion message
    TaskDialog.Show("Success", "Selected columns have been split by levels.")

except Exception as e:
    TaskDialog.Show("Error", str(e))
