# -*- coding: utf-8 -*-
'''Insert Worksets'''
__title__ = "Insert Worksets"
__author__ = "prakritisrimal"

from pyrevit import forms
from Autodesk.Revit.DB import *
from Autodesk.Revit.Exceptions import InvalidOperationException

doc = __revit__.ActiveUIDocument.Document

# Check if the document is workshared
worksharing_enabled = doc.IsWorkshared

if worksharing_enabled:
    a = forms.ask_for_string(default='Enter the name', prompt='Enter new workset name:', title='Workset Name')

    if a.isspace() or not a:
        forms.alert('Enter a proper workset name', title='Invalid Workset Name')
    else:
        Ws = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset).ToWorksets()
        Exw = [i.Name for i in Ws]

        if a in Exw:
            forms.alert('Workset already exists', title='Duplicate Workset Name')
        else:
            t = Transaction(doc, "Create Workset")
            try:
                t.Start()
                Workset.Create(doc, a)
                t.Commit()
                message = 'Workset "' + a + '" created successfully'
                forms.alert(message, title="Script Completed", warn_icon=False)
            except InvalidOperationException as e:
                t.RollBack()
                message = "Failed to create workset: " + str(e)
                forms.alert(message, title="Error")
            except Exception as e:
                t.RollBack()
                message = "An unexpected error occurred: " + str(e)
                forms.alert(message, title="Error")
else:
    forms.alert("File not Workshared - Create a Workshared Model First!", title='Script Cancelled')
    script.exit()
