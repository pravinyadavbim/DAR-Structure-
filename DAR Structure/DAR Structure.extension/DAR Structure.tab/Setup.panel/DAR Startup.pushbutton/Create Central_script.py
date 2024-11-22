# -*- coding: utf-8 -*-
'''Create Central'''
__title__ = "Create Central"
__author__ = "PravinYadav"

# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.ApplicationServices import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import os

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document  # Get the Active Document
output = script.get_output()
app = __revit__.Application  # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)

# Define structure types and their templates
structure_types = {
    "Structural Concrete": {
        2023: r"K:\BIM\2023\Revit\Dar\Templates\SC_Template_Dar_R23.rte",
        2022: r"K:\BIM\2023\Revit\Dar\Templates\SC_Template_Dar_R23.rte",
    },
    "Structural Steel": {
        2023: r"K:\BIM\2023\Revit\Dar\Templates\SS_Template_Dar_R23.rte",
        2022: r"K:\BIM\2023\Revit\Dar\Templates\SS_Template_Dar_R23.rte",
    },
}

# Prompt the user to select a structure type
structure_type = forms.SelectFromList.show(
    ["Structural Concrete", "Structural Steel"],
    title="Choose Structure Type",
    button_name="Select"
)

# Check if the user made a selection
if structure_type:
    template_path = structure_types[structure_type][rvt_year]
else:
    forms.alert("No structure type selected. Exiting the script.", title="Error", warn_icon=True)
    script.exit()

# Creating a new Document
new_document = app.NewProjectDocument(template_path)

# Create a Workshared Model
new_document.EnableWorksharing("Shared Levels and Grids", "Scope Boxes")

# Folder selection dialog
save_folder = forms.pick_folder(title="Select Destination Folder")
if not save_folder:
    forms.alert("No folder selected. Exiting the script.", title="File Not Created", warn_icon=True)
    script.exit()

# File name input dialog with validation
while True:
    file_name = forms.ask_for_string(
        title="Enter Revit File Name",
        prompt=("Refer to the BIM Manual - N:\\BIM-AUTOMATION\\Documents\\BIM Manual.pdf\n\n"
                "Example Name: SH22XXX-01XXD-DAR-AL-AL-M3-AR-0001.rvt\n\n"
                "Revit File Name"),
        default="PRJ-ORG-FUN-SPA-FRM-DSC-NUM"
    )
    if file_name:
        break
    forms.alert("No project name entered. Please enter a valid name.", title="File Name Required", warn_icon=True)

# Set the save path for the new project file
save_path = os.path.join(save_folder, file_name + ".rvt")

# Save the newly created document
save_options = SaveAsOptions()
worksharing_save_option = WorksharingSaveAsOptions()
worksharing_save_option.SaveAsCentral = True

save_options.SetWorksharingOptions(worksharing_save_option)
save_options.OverwriteExistingFile = True  # Allow overwriting an existing file

new_document.SaveAs(save_path, save_options)

# Open and activate the saved document
ui_doc.Application.OpenAndActivateDocument(save_path)

# Give final prompt
forms.alert("New Project File Created Successfully!", title="File Created", warn_icon=False)
