__doc__ = "This addin splits selected walls by levels without changing the height"
__title__ = "WallSplit"
__author__ = "Pravin Yadav"

from pyrevit import forms
from pyrevit import revit, DB

doc = revit.doc
uidoc = revit.uidoc

# Function to split walls at levels without changing height
def split_wall_by_levels(wall, level, next_level):
    wall_location = wall.Location
    if isinstance(wall_location, DB.LocationCurve):
        wall_curve = wall_location.Curve
        
        # Calculate height from the base level to the next level for splitting
        level_elevation = level.Elevation
        next_level_elevation = next_level.Elevation
        wall_height = next_level_elevation - level_elevation  # The section's height between levels

        # Create the new wall section based on the calculated height, but keeping the original base height
        new_wall = DB.Wall.Create(doc, wall_curve, wall.WallType.Id, level.Id, wall_height, 0, False, False)
        return new_wall

# Get the selected elements (walls) in the model
selection = uidoc.Selection.GetElementIds()
selected_walls = [doc.GetElement(id) for id in selection if isinstance(doc.GetElement(id), DB.Wall)]

# Check if any walls were selected
if not selected_walls:
    forms.alert("No walls selected. Please select walls to split.", ok=True, exitscript=True)

# Collect all levels and sort them by elevation
levels_collector = DB.FilteredElementCollector(doc).OfClass(DB.Level)
levels = sorted(levels_collector.ToElements(), key=lambda x: x.Elevation)

# Start a single transaction to process all wall splitting
with DB.Transaction(doc, "Split Walls") as trans:
    trans.Start()
    try:
        for wall in selected_walls:
            wall_base_level_id = wall.LevelId
            wall_base_level = doc.GetElement(wall_base_level_id)
            wall_top_constraint = wall.get_Parameter(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()
            wall_height = wall_top_constraint

            # Find where to split: between the base level and next level for the wall
            for i in range(len(levels) - 1):
                level = levels[i]
                next_level = levels[i + 1]

                # Only split if the level is within the wall's height range
                if level.Elevation < wall_height and next_level.Elevation <= wall_height:
                    # Perform the split without adjusting the original height
                    split_wall_by_levels(wall, level, next_level)
                
            # Once all splits are done, remove the original wall
            doc.Delete(wall.Id)

        trans.Commit()
    except Exception as e:
        trans.RollBack()
        forms.alert("Error during wall splitting: {}".format(str(e)), title="Error", ok=True)

forms.alert("Selected walls split by levels successfully, height preserved.", ok=True)
