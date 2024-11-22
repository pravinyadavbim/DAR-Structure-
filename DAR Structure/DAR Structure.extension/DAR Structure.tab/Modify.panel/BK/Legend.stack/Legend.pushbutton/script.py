import os
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.DB import Transaction, ViewFamilyType, ViewSheet, DWGImportOptions, ImportInstance
from Autodesk.Revit.DB import FilteredElementCollector, ViewFamily, ImportInstance, Document, XYZ
import pyrevit.forms  # Importing the forms module

# Function to create legend views from DWG files
def create_legend_views(doc, dwg_file_paths):
    # Start a transaction in Revit
    with Transaction(doc, "Create Legend Views") as tx:
        tx.Start()

        # Get the legend view family type
        view_family_type = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
        legend_view_type = None
        for vft in view_family_type:
            if vft.ViewFamily == ViewFamily.Legend:
                legend_view_type = vft
                break

        if not legend_view_type:
            TaskDialog.Show("Error", "No Legend View Family Type found.")
            return

        for dwg_file in dwg_file_paths:
            # Get the file name without extension to use as legend view name
            legend_view_name = os.path.splitext(os.path.basename(dwg_file))[0]

            # Create a new legend view
            legend_view = ViewSheet.Create(doc, legend_view_type.Id)
            legend_view.Name = legend_view_name

            # Import the DWG file into the legend view
            import_options = DWGImportOptions()
            import_options.Placement = ImportInstance.Placement.Origin  # Correcting placement option
            import_options.UseCurrentViewSize = True
            
            # Set the position for the imported DWG file
            position = XYZ(0, 0, 0)  # Adjust the position as needed
            
            # Import the DWG file
            try:
                # Using ImportInstance to import the DWG
                dwg_import = ImportInstance.Create(doc, legend_view.Id, import_options)
                if dwg_import is None:
                    TaskDialog.Show("Error", "Failed to import " + dwg_file + ".")
                    continue
                
                # Set the location of the imported instance
                dwg_import.Location.Move(position)

            except Exception as e:
                TaskDialog.Show("Error", "Failed to import " + dwg_file + ": " + str(e))
                continue

        tx.Commit()  # Commit the transaction

# Example usage (you need to provide the doc and dwg_file_paths)
# doc = __revit__.ActiveUIDocument.Document
# dwg_file_paths = [r"C:\path\to\your\file1.dwg", r"C:\path\to\your\file2.dwg"]
# create_legend_views(doc, dwg_file_paths)
