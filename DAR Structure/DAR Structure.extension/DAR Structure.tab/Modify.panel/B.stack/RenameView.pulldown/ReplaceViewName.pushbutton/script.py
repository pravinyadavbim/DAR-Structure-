from pyrevit import revit, DB, forms
from Autodesk.Revit.DB import Transaction, FilteredElementCollector, View

# Function to list all view names
def list_all_views():
    doc = revit.doc  # Get the active Revit document
    # Collect all views that are not templates
    all_views = FilteredElementCollector(doc).OfClass(View).WhereElementIsNotElementType().ToElements()

    # Print all view names for debugging
    existing_views = []
    for view in all_views:
        if not view.IsTemplate:  # Check if it is not a template view
            existing_views.append(view.Name)
    
    return existing_views

# Function to rename views based on search and replace terms
def rename_views(search_term, replace_term):
    doc = revit.doc  # Get the active Revit document
    # Collect all views that are not templates
    all_views = FilteredElementCollector(doc).OfClass(View).WhereElementIsNotElementType().ToElements()

    renamed_count = 0  # Counter to keep track of renamed views

    # Start a transaction for renaming views
    with Transaction(doc, 'Rename Views') as t:
        t.Start()

        for view in all_views:
            if not view.IsTemplate:  # Check if it is not a template view
                old_name = view.Name
                if search_term in old_name:  # If the search term is found in the name
                    new_name = old_name.replace(search_term, replace_term)  # Replace the old word with the new word
                    if new_name != old_name:  # Only rename if the name has actually changed
                        view.Name = new_name  # Update the view name
                        renamed_count += 1
                        print('Renamed "{0}" to "{1}"'.format(old_name, new_name))

        t.Commit()

    # Provide feedback on the number of views renamed
    if renamed_count > 0:
        print("{0} views were renamed.".format(renamed_count))
    else:
        print("No views were found with the term '{0}'. Please check if the term is correct.".format(search_term))
        print("Available views:")
        for view in list_all_views():
            print(view)  # List all available views to help identify the issue

# List existing views before renaming
existing_views = list_all_views()
print("Existing Views:")
for view_name in existing_views:
    print(view_name)

# Popup to ask for the term to search for in the view names
search_term = forms.ask_for_string(
    prompt="Enter the word to search in view names",
    title="Search Term",
    default="AAAA"  # You can set a default value here
)

# Popup to ask for the new term to replace the search term with
replace_term = forms.ask_for_string(
    prompt="Enter the new word to replace it with",
    title="Replace Term",
    default="BBBB"  # You can set a default value here
)

# Ensure the user provided both inputs before proceeding
if search_term and replace_term:
    rename_views(search_term, replace_term)
else:
    print("Both search and replace terms are required to proceed.")
