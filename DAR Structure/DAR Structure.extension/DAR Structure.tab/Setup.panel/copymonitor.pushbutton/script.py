import clr
import sys
from Autodesk.Revit.DB import FilteredElementCollector, Grid, Level, Transaction, CopyPasteOptions, ElementTransformUtils, RevitLinkInstance
from Autodesk.Revit.UI import TaskDialog

clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
clr.AddReference('RevitNodes')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Get active Revit document
doc = DocumentManager.Instance.CurrentDBDocument

# Get all linked documents in the project
linked_docs = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()

# Check if any linked documents are found
if not linked_docs:
    TaskDialog.Show('Error', 'No linked models found.')
    sys.exit()

# Create a list of linked document names
linked_doc_names = []
for i, link in enumerate(linked_docs):
    linked_doc_names.append(str(i+1) + ". " + link.Name)

# Show selection dialog for linked document
selected_link_index = TaskDialog.Show('Linked Model Selection', "\n".join(linked_doc_names))

try:
    selected_link_index = int(selected_link_index) - 1
    linked_doc_instance = linked_docs[selected_link_index]
    linked_doc = linked_doc_instance.GetLinkDocument()
    
    # Check if linked document is valid
    if linked_doc is None:
        TaskDialog.Show('Error', 'The linked document could not be loaded.')
        sys.exit()

except Exception as e:
    TaskDialog.Show('Error', 'Invalid selection or error retrieving linked document.')
    sys.exit()

# Get grids and levels from the linked document
linked_grids = FilteredElementCollector(linked_doc).OfClass(Grid).ToElements()
linked_levels = FilteredElementCollector(linked_doc).OfClass(Level).ToElements()

# Start transaction for copying elements
TransactionManager.Instance.EnsureInTransaction(doc)

# Copy Grids
for grid in linked_grids:
    try:
        ElementTransformUtils.CopyElements(linked_doc, [grid.Id], doc, None, CopyPasteOptions())
    except Exception as e:
        print("Failed to copy grid {}: {}".format(grid.Id, e))

# Copy Levels
for level in linked_levels:
    try:
        ElementTransformUtils.CopyElements(linked_doc, [level.Id], doc, None, CopyPasteOptions())
    except Exception as e:
        print("Failed to copy level {}: {}".format(level.Id, e))

# Commit transaction
TransactionManager.Instance.TransactionTaskDone()

TaskDialog.Show('Complete', 'Grids and Levels copied successfully.')
