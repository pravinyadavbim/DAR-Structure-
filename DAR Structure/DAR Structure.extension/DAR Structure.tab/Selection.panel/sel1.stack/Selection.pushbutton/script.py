import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("PresentationFramework")  # Only if needed for UI

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, ElementId
from Autodesk.Revit.UI import UIApplication
from System.Collections.Generic import List  # Import List from System.Collections.Generic
from System.Windows import Window
from System.Windows.Controls import ComboBox, Button, StackPanel

# Get the active Revit document from PyRevit's __revit__ variable
uiapp = __revit__  
uidoc = uiapp.ActiveUIDocument
doc = uidoc.Document if uidoc else None

# Check if document is available
if not doc:
    pass  # Do nothing if no document is found
else:
    # Define category options for selection (Reordered here)
    category_dict = {
        "Structural Columns": BuiltInCategory.OST_StructuralColumns,
        "Structural Framing": BuiltInCategory.OST_StructuralFraming,
        "Structural Foundations": BuiltInCategory.OST_StructuralFoundation,
        "Floors": BuiltInCategory.OST_Floors,
        "Walls": BuiltInCategory.OST_Walls,
        "Tags": BuiltInCategory.OST_Tags
    }

    # UI Selection Window
    class CategorySelectionWindow(Window):
        def __init__(self):
            self.Title = "Select Structural Category"
            self.Width = 300
            self.Height = 150

            # Create stack panel for UI layout
            stack_panel = StackPanel()
            self.combo = ComboBox()
            # Populate ComboBox with ordered categories
            self.combo.ItemsSource = list(category_dict.keys())  # This ensures the order is based on the dictionary above
            stack_panel.Children.Add(self.combo)

            # OK Button
            self.ok_button = Button()
            self.ok_button.Content = "OK"
            self.ok_button.Click += self.ok_clicked
            stack_panel.Children.Add(self.ok_button)

            # Cancel Button
            self.cancel_button = Button()
            self.cancel_button.Content = "Cancel"
            self.cancel_button.Click += self.cancel_clicked
            stack_panel.Children.Add(self.cancel_button)

            self.Content = stack_panel
            self.selection_made = False

        def ok_clicked(self, sender, args):
            self.selection_made = True
            self.Close()

        def cancel_clicked(self, sender, args):
            self.Close()

    # Show the window and get selection
    window = CategorySelectionWindow()
    window.ShowDialog()

    if window.selection_made:
        # Obtain the selected category
        selected_category_name = window.combo.SelectedItem
        selected_category = category_dict[selected_category_name]

        # Begin transaction for element selection
        trans = Transaction(doc, "Select Elements by Category")
        try:
            trans.Start()
            
            # Collect elements from the selected category
            elements = FilteredElementCollector(doc).OfCategory(selected_category).WhereElementIsNotElementType().ToElements()
            
            # Select the elements
            selection_ids = List[ElementId]([elem.Id for elem in elements])
            uidoc.Selection.SetElementIds(selection_ids)
            
            trans.Commit()
        except Exception as e:
            trans.RollBack()  # Rollback transaction in case of error
