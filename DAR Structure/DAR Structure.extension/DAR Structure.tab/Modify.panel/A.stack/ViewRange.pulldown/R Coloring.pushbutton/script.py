# Import necessary Revit API and pyRevit modules
from pyrevit import revit, DB
from Autodesk.Revit.DB import BuiltInCategory, OverrideGraphicSettings, Color, ElementId

# Start Revit transaction
doc = revit.doc
view = doc.ActiveView

# Ensure the view is 3D
def is_3d_view(view):
    return isinstance(view, DB.View3D)

# Function to get color based on height range
def get_color_for_height_range(height_diff):
    if height_diff > 5.0:  # Elements above the top plane
        return Color(0, 255, 0)  # Green
    elif 0.0 <= height_diff <= 5.0:  # Elements near the selected level
        return Color(0, 0, 255)  # Blue
    elif height_diff < 0.0:  # Elements below the bottom plane
        return Color(255, 0, 0)  # Red
    return Color(128, 128, 128)  # Grey for any others

# Apply graphical override to elements in the 3D view based on height difference
def apply_graphical_override_to_elements(elements, selected_level):
    level_elevation = selected_level.Elevation  # Get the selected level's elevation
    
    for elem in elements:
        bbox = elem.get_BoundingBox(view)  # Get the bounding box of the element
        if bbox:
            elem_height = bbox.Min.Z  # Use the minimum Z value of the bounding box for height comparison
            height_diff = elem_height - level_elevation  # Calculate the height difference relative to the level
            
            color = get_color_for_height_range(height_diff)  # Get color based on the height difference
            
            # Set the graphical overrides with the determined color
            ogs = OverrideGraphicSettings()
            ogs.SetProjectionLineColor(color)  # Set line color
            # Set fill pattern ID to None (no fill)
            doc.ActiveView.SetElementOverrides(elem.Id, ogs)

# Remove graphical overrides from elements
def remove_graphical_overrides(elements):
    ogs_clear = OverrideGraphicSettings()  # Clear overrides by passing an empty settings object
    for elem in elements:
        doc.ActiveView.SetElementOverrides(elem.Id, ogs_clear)

# Get elements in the view (for example, structural columns or other categories)
def get_elements_in_view(view, category):
    collector = DB.FilteredElementCollector(doc, view.Id)
    collector.OfCategory(category)
    collector.WhereElementIsNotElementType()
    return collector.ToElements()

# Toggle the view range coloring: apply or remove overrides
def toggle_view_range_coloring_in_3d_view(view, selected_level):
    if not is_3d_view(view):
        print("This script only works for 3D Views.")
        return
    
    # Get elements in the 3D view (e.g., structural columns or walls)
    elements_in_view = get_elements_in_view(view, BuiltInCategory.OST_StructuralColumns)

    # Check if the elements are already colored, and remove overrides if they are
    ogs_check = doc.ActiveView.GetElementOverrides(elements_in_view[0].Id)  # Check one element for existing overrides
    if ogs_check.IsValidObject:  # If overrides exist, remove them
        remove_graphical_overrides(elements_in_view)
        print("Coloring removed.")
    else:  # Otherwise, apply coloring
        apply_graphical_override_to_elements(elements_in_view, selected_level)
        print("Coloring applied.")

# Allow the user to select a level
def select_level():
    level_collector = DB.FilteredElementCollector(doc).OfClass(DB.Level)
    levels = list(level_collector)
    if levels:
        print("Select a level:")
        for i, level in enumerate(levels):
            print("{0}: {1}".format(i + 1, level.Name))  # Corrected string formatting
        while True:
            try:
                level_index = int(input("Enter the number corresponding to the level: ")) - 1
                if 0 <= level_index < len(levels):
                    return levels[level_index]
                else:
                    print("Invalid selection. Please choose a number from the list.")
            except ValueError:
                print("Please enter a valid number.")
    else:
        print("No levels found in the project.")
        return None

# Start the transaction and toggle view range coloring in 3D view
with revit.Transaction("Toggle View Range Coloring in 3D View"):
    selected_level = select_level()
    if selected_level:
        toggle_view_range_coloring_in_3d_view(view, selected_level)
