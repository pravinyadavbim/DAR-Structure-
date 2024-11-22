from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

# Ensure that we can access the Revit API
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')

from RevitServices.Persistence import DocumentManager

# Function to toggle visibility of categories
def toggle_visibility(doc, view, categories_to_toggle, visibility):
    # Access the categories of the view
    for category in categories_to_toggle:
        # Get category by name
        category_element = get_category_by_name(doc, category)
        if category_element:
            # Set visibility of the category
            view.Categories.get_Item(category_element.Id).SetVisibility(visibility)

# Function to get category by name
def get_category_by_name(doc, category_name):
    # Use FilteredElementCollector to find the category
    collector = FilteredElementCollector(doc)
    categories = collector.OfClass(Category).ToElements()
    for category in categories:
        if category.Name == category_name:
            return category
    return None

# Main function
def main():
    # Get the active UIDocument and Document
    uidoc = __revit__.ActiveUIDocument
    doc = uidoc.Document
    
    # Start a transaction
    t = Transaction(doc, "Toggle Analytical Model Visibility")
    t.Start()
    
    try:
        # Define the categories to turn off (all except analytical categories)
        all_model_categories = [
            "Walls",
            "Floors",
            "Roofs",
            "Structural Framing",
            "Structural Columns",
            "Ceilings",
            "Casework",
            "Furniture",
            "Lighting Fixtures",
            "Site",
            # Add other categories as necessary
        ]
        
        # Define analytical categories to turn on
        analytical_categories = [
            "Analytical Links",
            "Analytical Members",
            "Analytical Nodes",
            "Analytical Openings",
            "Analytical Panels",
            "Analytical Pipe Connections",
            "Analytical Spaces",
            "Analytical Surfaces",
            "Boundary Conditions",
            "Electrical Analytical Loads",
            "Structural Internal Loads",
            "Structural Load Cases",
            "Structural Loads",
            "System Zones",
        ]
        
        # Get the active 3D view
        active_view = doc.ActiveView
        
        # Turn off all model categories
        toggle_visibility(doc, active_view, all_model_categories, False)
        
        # Turn on analytical categories
        toggle_visibility(doc, active_view, analytical_categories, True)

        # Create a new 3D view for the analytical model
        new_view_name = "Analytical Model View"
        new_3d_view = View3D.CreateIsometric(doc, active_view.GetTypeId())
        new_3d_view.Name = new_view_name
        
        # Set the view to show only analytical categories
        toggle_visibility(doc, new_3d_view, analytical_categories, True)
        
        # Turn off all other categories in the new 3D view
        toggle_visibility(doc, new_3d_view, all_model_categories, False)
    
    except Exception as e:
        # Handle exceptions (optional)
        print("Error: ", e)
    
    finally:
        # Commit the transaction
        t.Commit()

# Execute the main function
if __name__ == "__main__":
    main()
