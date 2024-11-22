# -*- coding: utf-8 -*-
__title__ = 'Zoom Base Point'
__doc__ = """Zoom in active view to Project base point. If it's hidden - enables "Reveal Hidden" mode.

IT-BIM TEAM"""

__helpurl__ = "https://dar-tools-documentation.gitbook.io/dar-tools-documentation"

try:
    from pyrevit.versionmgr import PYREVIT_VERSION
except:
    from pyrevit import versionmgr
    PYREVIT_VERSION = versionmgr.get_pyrevit_version()

pyRevitNewer44 = PYREVIT_VERSION.major >=4 and PYREVIT_VERSION.minor >=5

if pyRevitNewer44:
    from pyrevit import script, revit
    output = script.get_output()
    logger = script.get_logger()
    linkify = output.linkify
    doc = revit.doc
    uidoc = revit.uidoc
    selection = revit.get_selection()
else:
    from scriptutils import logger, this_script
    from revitutils import doc, selection, uidoc

    output = this_script.output

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementId, Transaction

cl = FilteredElementCollector(doc, uidoc.ActiveView.Id).WhereElementIsNotElementType()

if __shiftclick__:
    category = BuiltInCategory.OST_SharedBasePoint
else:
    category = BuiltInCategory.OST_ProjectBasePoint

elements = cl.OfCategory(category).ToElementIds()

if len(elements)==0:
    t = Transaction(doc, "[%s] Reveal hidden" % __title__)
    t.Start()
    try:
        uidoc.ActiveView.EnableRevealHiddenMode()
        cl = FilteredElementCollector(doc, uidoc.ActiveView.Id).WhereElementIsNotElementType()
        elements = cl.OfCategory(category).ToElementIds()
    except:
        elements = []

    if len(elements) == 0:
        t.RollBack()
        cl = FilteredElementCollector(doc).WhereElementIsNotElementType()
        elements = cl.OfCategory(category).ToElementIds()
    else:
        t.Commit()

uidoc.ShowElements(elements[0])