# -*- coding: utf-8 -*-
'''Create Worksets'''
__title__ = "Create Worksets"
__author__ = "PravinYadav"


# Import Libraries
from Autodesk.Revit.DB import *
from Autodesk.Revit.ApplicationServices import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script
import csv
import os

script_dir = os.path.dirname(__file__)

# Read all the Rows from the CSV Files as Lists
def readfile(selected_option, ops):
    if selected_option == ops[0]:
        csv_filename = "WorksetLists_Structural_Concrete.csv"
    elif selected_option == ops[1]:
        csv_filename = "WorksetLists_Structural_Steel.csv"
    
    source_file = os.path.join(script_dir, csv_filename)
    
    workset_names = []
    if os.path.exists(source_file):
        with open(source_file) as csvfile: 
            reader = csv.DictReader(csvfile)
            for row in reader:
                workset_names.append(row["Worksets"])
    return workset_names

# Create Worksets from the List
def create_worksets(doc, workset_names):
    counter = 0
    for name in workset_names:
        if WorksetTable.IsWorksetNameUnique(doc, name):
            Workset.Create(doc, name)
            counter += 1
    return counter

# Main Function
doc = __revit__.ActiveUIDocument.Document

if not doc.IsWorkshared:
    try:
        doc.EnableWorksharing("Shared Levels and Grids", "Scope Boxes")
    except:
        forms.alert("File not Workshared - Create a Workshared Model First!", title='Script Cancelled')
        script.exit()

# Prompt user for trade selection
ops = ['Structural Concrete', 'Structural Steel']
selected_option = forms.SelectFromList.show(
    ops,
    multiselect=False, width=300, height=300,
    title='Select the trade for which the worksets should be created',
    default=ops[0]
)

if not selected_option:
    script.exit()

else:
    # Read the appropriate CSV file based on the selected trade
    workset_names = readfile(selected_option, ops)

    if not workset_names:
        forms.alert("No worksets found for " + selected_option + ".", title="Script Cancelled")
        script.exit()

    # Create worksets within a transaction
    with revit.Transaction("Create Workset"):
        count = create_worksets(doc, workset_names)

    # Display a message with the results
    message = str(count) + " Worksets Created for " + selected_option
    forms.alert(message, title="Script Completed", warn_icon=False)
