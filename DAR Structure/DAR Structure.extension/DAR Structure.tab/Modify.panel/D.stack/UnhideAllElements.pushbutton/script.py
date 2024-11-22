# -*- coding: utf-8 -*-
__title__ = "UnhideAllElements"
__version__ = 'Version = 1.0'
__doc__ = """Version = 1.0
Date    = 11.11.2024
_____________________________________________________________________
Description:
Unhide all Elements in the active view
_____________________________________________________________________
Last update:11.11.2024
_____________________________________________________________________
To-Do:-
_____________________________________________________________________
Author: IT-BIM TEAM"""

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
# ==================================================
from Autodesk.Revit.DB import *

# .NET Imports
import os, clr
clr.AddReference("System")
from System.Collections.Generic import List

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝ VARIABLES
# ==================================================
doc   = __revit__.ActiveUIDocument.Document

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
# ==================================================
if __name__ == '__main__':
    all_elements = FilteredElementCollector(doc).WhereElementIsNotElementType().ToElementIds()
    unhide_elements = List[ElementId](all_elements)

    with Transaction(doc,__title__) as t:
        t.Start()
        doc.ActiveView.UnhideElements(unhide_elements)
        t.Commit()