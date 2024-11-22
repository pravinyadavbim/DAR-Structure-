# -*- coding: utf-8 -*-
'''Phaser'''
__title__ = "Phaser"
__author__ = "prajwalbkumar"


# Imports
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script

ui_doc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document # Get the Active Document
app = __revit__.Application # Returns the Revit Application Object


# MAIN

selection = ui_doc.Selection.GetElementIds()
selected_elements = []

if len(selection) > 0:
    for id in selection:
        selected_elements.append(doc.GetElement(id))

else:
    forms.alert("Select few elements first!", title = "Script Exiting", warn_icon = True)
    script.exit()    


phase_category = forms.alert("Select Phase action", title = "Open Excel File", warn_icon = False, options=["Phase Constructed", "Phase Demolished"])

if not phase_category:
    script.exit()


all_phases = FilteredElementCollector(doc).OfClass(Phase)

target_phases = []
for phase in all_phases:
    target_phases.append(phase.Name)

if phase_category == "Phase Demolished":
    target_phases.append("None")

user_phase = forms.SelectFromList.show(target_phases, title="Select Relevent Phase", width=300, height=300, button_name="Select Phase", multiselect=False)

if not user_phase:
    script.exit()


for phase in all_phases:
    if user_phase == phase.Name:
        user_phase_id = phase.Id
        break
    if user_phase == "None":
        user_phase_id = ElementId(-1)


t = Transaction(doc, "Update Phase")
t.Start()

for element in selected_elements:
    if not element.HasPhases():
        continue

    else:
        if not element.ArePhasesModifiable():
            continue
        
        else:
                if phase_category == "Phase Constructed":
                    if(element.IsCreatedPhaseOrderValid(user_phase_id)):
                        element.CreatedPhaseId = user_phase_id
                else:
                    if element.IsDemolishedPhaseOrderValid(user_phase_id):
                        element.DemolishedPhaseId = user_phase_id

t.Commit()

