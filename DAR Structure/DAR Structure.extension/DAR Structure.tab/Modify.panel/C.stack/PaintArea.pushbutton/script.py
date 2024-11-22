# Import necessary Revit API modules
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Options
from Autodesk.Revit.UI import TaskDialog
from pyrevit import revit, DB

# Get the current Revit document
doc = revit.doc

def calculate_paint_area_for_steel():
    # Prepare options for getting the geometry of the elements
    options = Options()
    options.ComputeReferences = True
    options.IncludeNonVisibleObjects = False

    # Collect all structural steel columns and framings
    structural_elements = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().ToElements()

    total_paint_area = 0.0
    steel_elements_count = 0

    # Loop through all elements to calculate the surface area (paint area)
    for element in structural_elements:
        try:
            # Get the geometry of the element
            geometry = element.get_Geometry(options)
            if geometry is not None:
                # Accumulate the surface areas
                for geomObj in geometry:
                    if hasattr(geomObj, 'SurfaceArea'):
                        total_paint_area += geomObj.SurfaceArea
                        steel_elements_count += 1

        except Exception as e:
            print("Error processing element {0}: {1}".format(element.Id, str(e)))

    # Convert the area from square feet to square meters (if needed)
    total_paint_area_in_sqm = total_paint_area * 0.092903  # 1 sqft = 0.092903 sqm

    # Display the result to the user
    if steel_elements_count == 0:
        message = "No steel columns or framings found in the model."
    else:
        message = "Total paint area for steel columns and framings: {0:.2f} square meters.".format(total_paint_area_in_sqm)

    TaskDialog.Show("Paint Area Calculation", message)

# Call the function to calculate paint area
calculate_paint_area_for_steel()
