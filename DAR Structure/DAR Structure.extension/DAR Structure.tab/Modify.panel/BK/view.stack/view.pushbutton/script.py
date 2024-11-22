from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import FilteredElementCollector, SectionBox, BoundingBoxXYZ, XYZ, Level

# Get the current Revit document
doc = DocumentManager.Instance.CurrentDBDocument

# Function to create section boxes based on levels
def create_section_boxes(levels):
    TransactionManager.Instance.EnsureInTransaction(doc)  # Start transaction
    try:
        for level in levels:
            # Create a new section box
            section_box = SectionBox()
            
            # Set section box parameters (you'll need to define bounds based on your requirements)
            bbox = BoundingBoxXYZ()
            bbox.Min = XYZ(-10, -10, level.Elevation - 5)  # Adjust as needed
            bbox.Max = XYZ(10, 10, level.Elevation + 5)  # Adjust as needed
            section_box.SetBoundingBox(bbox)
            
            # Add section box to the document
            doc.Create.NewElement(section_box)
    except Exception as e:
        print("An error occurred: " + str(e))  # Use string concatenation
    finally:
        TransactionManager.Instance.TransactionTaskDone()  # End transaction

# Get all levels in the project
levels = FilteredElementCollector(doc).OfClass(Level).ToElements()
create_section_boxes(levels)
