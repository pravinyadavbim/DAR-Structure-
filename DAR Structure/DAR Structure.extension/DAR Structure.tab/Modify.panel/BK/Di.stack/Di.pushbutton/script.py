from pyrevit import forms, script, revit
from Autodesk.Revit.DB import *

# Get the active document
doc = revit.doc

# Start a transaction
with revit.Transaction("Auto-Dimensioning of Structural Grids"):
    try:
        # Filter to get grid lines in the project
        grid_collector = FilteredElementCollector(doc).OfClass(Grid)
        grids = grid_collector.ToElements()

        # Check if there are enough grids
        if len(grids) < 2:
            forms.alert("Not enough grid lines to create dimensions. Found: {}".format(len(grids)))
            script.exit()

        # Create a reference array for the dimension
        reference_array = ReferenceArray()
        for grid in grids:
            reference = Reference(grid)
            reference_array.Append(reference)

        # Get the start and end points for the dimension line
        start_curve = grids[0].Curve
        end_curve = grids[-1].Curve
        
        start_point = start_curve.GetEndPoint(0)
        end_point = end_curve.GetEndPoint(1)

        location_line = Line.CreateBound(start_point, end_point)

        # Get the dimension type (replace with an actual dimension type from your project)
        dimension_type_collector = FilteredElementCollector(doc).OfClass(DimensionType)
        dimension_type = dimension_type_collector.FirstElement()  # Get the first available dimension type

        # Create the dimension
        if dimension_type:
            # Create the dimension in the active view
            dimension = doc.Create.NewDimension(doc.ActiveView, location_line, reference_array, dimension_type)
            forms.alert("Auto-Dimensioning of Structural Grids Completed!")
        else:
            forms.alert("No Dimension Type found in the project.")
            script.exit()

    except Exception as e:
        forms.alert("Error: {}".format(str(e)))
