# -*- coding: utf-8 -*-
'''URS Checker'''
__title__ = "Check Live"
__author__ = "prakritisrimal - prajwalbkumar"

# IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.ApplicationServices import *
from Autodesk.Revit.UI import UIDocument
from pyrevit import revit, forms, script, output
import os
import math

script_dir = os.path.dirname(__file__)
ui_doc  = __revit__.ActiveUIDocument
doc     = __revit__.ActiveUIDocument.Document # Get the Active Document
app     = __revit__.Application # Returns the Revit Application Object
rvt_year = int(app.VersionNumber)
output = script.get_output()

# Function to get the bounding box of a grid
def get_bounding_box(grid):
    location_curve = grid.Curve
    curve_start = location_curve.GetEndPoint(0)
    curve_end = location_curve.GetEndPoint(1)
    
    # Create a bounding box that encompasses the curve
    bbox = BoundingBoxXYZ()
    
    # Extend the box to include the grid's full extent
    min_x = min(curve_start.X, curve_end.X)
    min_y = min(curve_start.Y, curve_end.Y)
    max_x = max(curve_start.X, curve_end.X)
    max_y = max(curve_start.Y, curve_end.Y)
    bbox.Min = XYZ(min_x, min_y, -100000000000000000000)  # Extend downward to cover vertical extent
    bbox.Max = XYZ(max_x, max_y, 1000000000000000000000)   # Extend upward to cover vertical extent
    
    return bbox


# Collect all linked instances
linked_instance = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
link_name = []
for link in linked_instance:
    link_name.append(link.Name)

urs_instance_name = forms.SelectFromList.show(link_name, title = "Select URS File", width=600, height=600, button_name="Select File", multiselect=False)

if not urs_instance_name:
    script.exit()

for link in linked_instance:
    if urs_instance_name == link.Name:
        urs_instance = link
        break

urs_doc = urs_instance.GetLinkDocument()

if not urs_doc:
    forms.alert("No instance found of the selected URS File.\n"
                "Use Manage Links to Load the Link in the File!", title = "Link Missing", warn_icon = False)
    script.exit()



# Metadata for the report
report_metadata = {
    'Title': 'URS Comparison Report',
    'URS File Path': urs_doc.PathName,
    'Test File': doc.PathName
}

# Print results
output.print_md('# {}'.format(report_metadata['Title']))
output.print_md('**URS File Path:** {}'.format(report_metadata['URS File Path']))
output.print_md('**Test File Path:** {}'.format(report_metadata['Test File']))

# Check for Site Locations

active_site_location = doc.SiteLocation
urs_site_location = urs_doc.SiteLocation


urs_current_location = urs_doc.ActiveProjectLocation
urs_project_position = urs_current_location.GetProjectPosition(XYZ(0,0,0))

urs_northSouth = urs_project_position.NorthSouth * 304.8
urs_eastWest = urs_project_position.EastWest * 304.8
urs_elevation = urs_project_position.Elevation * 304.8
urs_trueNorth = round(urs_project_position.Angle / (math.pi / 180), 3)

active_current_location = doc.ActiveProjectLocation
active_project_position = active_current_location.GetProjectPosition(XYZ(0,0,0))

active_northSouth = active_project_position.NorthSouth * 304.8
active_eastWest = active_project_position.EastWest * 304.8
active_elevation = active_project_position.Elevation * 304.8
active_trueNorth = round(active_project_position.Angle / (math.pi / 180), 3)

# print(urs_northSouth)
# print(urs_eastWest)
# print(urs_elevation)
# print(urs_trueNorth)
# print("")
# print(active_northSouth)
# print(active_eastWest)
# print(active_elevation)
# print(active_trueNorth)

failed_geo_data = []
failed_project_data = []
failed_location = False


if not active_elevation == urs_elevation:
    failed_location = True

elif not active_trueNorth == urs_trueNorth:
    failed_location = True

elif not active_eastWest == urs_eastWest:
    failed_location = True

elif not active_northSouth == urs_northSouth:
    failed_location = True

if not active_site_location.Elevation == urs_site_location.Elevation:
    failed_location = True

elif not active_site_location.GeoCoordinateSystemDefinition == urs_site_location.GeoCoordinateSystemDefinition:
    failed_location = True

elif not active_site_location.Latitude == urs_site_location.Latitude:
    failed_location = True

elif not active_site_location.Longitude == urs_site_location.Longitude:
    failed_location = True

elif not active_site_location.PlaceName == urs_site_location.PlaceName:
    failed_location = True

elif not active_site_location.TimeZone == urs_site_location.TimeZone:
    failed_location = True

elif not active_site_location.WeatherStationName == urs_site_location.WeatherStationName:
    failed_location = True


if failed_location:
    failed_geo_data.append(["Site Elevation", urs_site_location.Elevation, active_site_location.Elevation])
    failed_geo_data.append(["Geo Coordinate System", urs_site_location.GeoCoordinateSystemId, active_site_location.GeoCoordinateSystemId])
    failed_geo_data.append(["Latitude", urs_site_location.Latitude, active_site_location.Latitude])
    failed_geo_data.append(["Longitude", urs_site_location.Longitude, active_site_location.Longitude])

    failed_project_data.append(["N/S", urs_northSouth, active_northSouth])
    failed_project_data.append(["E/W", urs_eastWest, active_eastWest])
    failed_project_data.append(["Elev", urs_elevation, active_elevation])
    failed_project_data.append(["Angle to True North", urs_trueNorth, active_trueNorth])

if failed_geo_data:
    output.print_md("##⚠️ URS LOCATION - Checks Completed. Issues Found ☹️") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
    output.print_table(table_data=failed_geo_data, columns=["GEO LOCATION DATA", "URS DATUM VALUES", "DOCUMENT DATUM VALUES"]) # Print a Table
    print("\n\n")
    output.print_table(table_data=failed_project_data, columns=["BASE POINT DATA", "URS DATUM VALUES", "DOCUMENT DATUM VALUES"]) # Print a Table
    output.print_md("---") # Markdown Line Break
    output.print_md("**LOCATION MISMATCH**  - The document location must match the URS location.") # Print a Quote
    output.print_md("---") # Markdown Line Break
else:
    output.print_md("##✅ URS LOCATION Checks Completed. No Issues Found 😃") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break


# Check for Grids
active_grids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
urs_grids = FilteredElementCollector(urs_doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()

if not active_grids:
    forms.alert("No grids found in the active document", title = "Grids Missing", warn_icon = True)
    script.exit()

active_grids_name = []
urs_grids_name = []
for grid in active_grids:
    active_grids_name.append(grid.Name)

for grid in urs_grids:
    urs_grids_name.append(grid.Name)


# Check if all URS Grid Names are present in the Active Doc Grids List
failed_data = []
for grid in urs_grids:
    failed_urs_grid = []
    if not grid.Name in active_grids_name:
        failed_urs_grid.append(output.linkify(grid.Id))
        failed_urs_grid.append(grid.Name) # Grid Name
        failed_urs_grid.append("GRID MISSING IN ACTIVE DOCUMENT") # Error Code
        failed_data.append(failed_urs_grid)

# Check if all Active Grid Names are present in the URS Doc Grids List
for grid in active_grids:
    failed_urs_grid = []
    if not grid.Name in urs_grids_name:
        failed_urs_grid.append(output.linkify(grid.Id))
        failed_urs_grid.append(grid.Name) # Grid Name
        failed_urs_grid.append("GRID MISSING IN URS DOCUMENT") # Error Code
        failed_data.append(failed_urs_grid)

# Check the location of all Active grids against the URS Grids
for active_grid in active_grids:
    failed_urs_grid = []
    for urs_grid in urs_grids:
        if active_grid.Name == urs_grid.Name:
            urs_grid_bbox = get_bounding_box(urs_grid)
            active_grid_bbox = get_bounding_box(active_grid)
            urs_grid_outline = Outline(urs_grid_bbox.Min, urs_grid_bbox.Max)
            active_grid_outline = Outline(active_grid_bbox.Min, active_grid_bbox.Max)
            if not urs_grid_outline.Intersects(active_grid_outline, 0.0001):
                failed_urs_grid.append(output.linkify(active_grid.Id))
                failed_urs_grid.append(active_grid.Name) # Grid Name
                failed_urs_grid.append("GRID LOCATION INCORRECT") # Error Code
                failed_data.append(failed_urs_grid)


if failed_data:
    output.print_md("##⚠️ URS GRIDS - Checks Completed. Issues Found ☹️") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
    output.print_table(table_data=failed_data, columns=["ELEMENT ID", "GRID NAME", "ERROR CODE"]) # Print a Table
    print("\n\n")
    output.print_md("---") # Markdown Line Break
    output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
    output.print_md("---") # Markdown Line Break
    output.print_md("**GRID MISSING IN ACTIVE DOCUMENT**  - The active document has missing grids. It must match the URS.") # Print a Quote
    output.print_md("**GRID MISSING IN URS DOCUMENT**     - There are extra grids or grids with incorrect names in the active document. They must match the URS.") # Print a Quote
    output.print_md("**GRID LOCATION INCORRECT**          - The grid location in the active document is incorrect. It must match the URS") # Print a Quote
    output.print_md("---") # Markdown Line Break

else:
    output.print_md("##✅ URS GRIDS Checks Completed. No Issues Found 😃") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break

##############################################

# Check for Levels
active_levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
urs_levels = FilteredElementCollector(urs_doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()

if not active_levels:
    forms.alert("No levels found in the active document", title = "Levels Missing", warn_icon = True)
    script.exit()

active_levels_name = []
urs_levels_name = []

for level in active_levels:
    active_levels_name.append(level.Name)

for level in urs_levels:
    urs_levels_name.append(level.Name)


# Check if all URS Levels Names are present in the Active Doc Levels List
failed_data = []
for level in urs_levels:
    failed_urs_level = []
    if not level.Name in active_levels_name:
        failed_urs_level.append(output.linkify(level.Id))
        failed_urs_level.append(level.Name) # Level Name
        failed_urs_level.append("LEVEL MISSING IN ACTIVE DOCUMENT") # Error Code
        failed_data.append(failed_urs_level)

# Check if all Active Level Names are present in the URS Doc Levels List
for level in active_levels:
    failed_urs_level = []
    if not level.Name in urs_levels_name:
        failed_urs_level.append(output.linkify(level.Id))
        failed_urs_level.append(level.Name) # Level Name
        failed_urs_level.append("LEVEL MISSING IN URS DOCUMENT") # Error Code
        failed_data.append(failed_urs_level)

# Check the location of all Active levels against the URS Levels
for active_level in active_levels:
    failed_urs_level = []
    for urs_level in urs_levels:
        if active_level.Name == urs_level.Name:
            if not urs_level.LookupParameter("Elevation").AsValueString() == active_level.LookupParameter("Elevation").AsValueString():
                failed_urs_level.append(output.linkify(active_level.Id))
                failed_urs_level.append(active_level.Name) # Level Name
                failed_urs_level.append("LEVEL LOCATION INCORRECT") # Error Code
                failed_data.append(failed_urs_level)


if failed_data:
    output.print_md("##⚠️ URS LEVELS Checks Completed. Issues Found ☹️") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break
    output.print_md("❌ There are Issues in your Model. Refer to the **Table Report** below for reference")  # Print a Line
    output.print_table(table_data=failed_data, columns=["ELEMENT ID", "LEVEL NAME", "ERROR CODE"]) # Print a Table
    print("\n\n")
    output.print_md("---") # Markdown Line Break
    output.print_md("***✅ ERROR CODE REFERENCE***")  # Print a Line
    output.print_md("---") # Markdown Line Break
    output.print_md("**LEVEL MISSING IN ACTIVE DOCUMENT**  - The active document has missing levels. It must match the URS.") # Print a Quote
    output.print_md("**LEVEL MISSING IN URS DOCUMENT**     - There are extra levels or levels with incorrect names in the active document. They must match the URS.") # Print a Quote
    output.print_md("**LEVEL LOCATION INCORRECT**          - The level location in the active document is incorrect. It must match the URS") # Print a Quote
    output.print_md("---") # Markdown Line Break

else:
    output.print_md("##✅ URS LEVELS Checks Completed. No Issues Found 😃") # Markdown Heading 2
    output.print_md("---") # Markdown Line Break