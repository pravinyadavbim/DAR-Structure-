__doc__ = "This addin finds coordinates of all piles/columns in meters"
__title__ = "Coord"
__author__ = "Sandip Chavan Dar"

from pyrevit import forms
from pyrevit import revit, DB
from pyrevit import HOST_APP
import math
import sys

def rotate(x, y, theta):
    rotated = [
        math.cos(theta) * x + math.sin(theta) * y,
        -math.sin(theta) * x + math.cos(theta) * y
    ]
    return rotated

def find_cord(x, y, theta, bp_x, bp_y):
    rotated = rotate(x, y, theta)
    result = [rotated[0] + bp_x, rotated[1] + bp_y]
    return (result[1], result[0])

def parameter_exists(group, name):
    return any(definition.Name == name for definition in group.Definitions)

doc = revit.doc
app = doc.Application

X = []
Y = []

sharedParameterFile = app.OpenSharedParameterFile()
if sharedParameterFile:
    myGroups = sharedParameterFile.Groups
else:
    forms.alert('Shared parameter file does not exist', ok=True, exitscript=True)

# Option to select coordinate reference
coordinate_reference = forms.CommandSwitchWindow.show(
    ['Project Base Point', 'Survey Point'],
    message='Select coordinate reference point:'
)

# Creating a dictionary for categories
options_category = {
    'Structural Columns': DB.BuiltInCategory.OST_StructuralColumns,
    'Foundation': DB.BuiltInCategory.OST_StructuralFoundation
}

selected_switch_category = forms.CommandSwitchWindow.show(
    sorted(options_category.keys()),
    message='Search for tag in category:'
)

target_category = options_category[selected_switch_category]

selection = DB.FilteredElementCollector(doc) \
    .OfCategory(target_category) \
    .WhereElementIsNotElementType() \
    .ToElements()

# Check if the group "pystructure" already exists
group_name = "pystructure"
existing_group = None
for group in myGroups:
    if group.Name == group_name:
        existing_group = group
        break

if existing_group:
    myGroup = existing_group
else:
    try:
        myGroup = myGroups.Create(group_name)  # Create new group
    except Exception as e:
        forms.alert('Error creating parameter group: {}'.format(str(e)), title="Error", ok=True)
        sys.exit()

# Define parameters
param_name_1 = "DAR_SHARED_COORDINATES_X"
param_name_2 = "DAR_SHARED_COORDINATES_Y"
param_description = "Coordinates of piles/column"

if HOST_APP.is_newer_than(2021):
    param_type = DB.SpecTypeId.Length
else:
    param_type = DB.ParameterType.Length

# Create parameters if they do not exist
if not parameter_exists(myGroup, param_name_1):
    option_1 = DB.ExternalDefinitionCreationOptions(param_name_1, param_type)
    option_1.UserModifiable = False
    option_1.Description = param_description
    try:
        externalDefinition_1 = myGroup.Definitions.Create(option_1)
    except Exception as e:
        forms.alert('Error creating {} parameter: {}'.format(param_name_1, str(e)), title="Error", ok=True)
        sys.exit()
else:
    externalDefinition_1 = myGroup.Definitions.get_Item(param_name_1)

if not parameter_exists(myGroup, param_name_2):
    option_2 = DB.ExternalDefinitionCreationOptions(param_name_2, param_type)
    option_2.UserModifiable = False
    option_2.Description = param_description
    try:
        externalDefinition_2 = myGroup.Definitions.Create(option_2)
    except Exception as e:
        forms.alert('Error creating {} parameter: {}'.format(param_name_2, str(e)), title="Error", ok=True)
        sys.exit()
else:
    externalDefinition_2 = myGroup.Definitions.get_Item(param_name_2)

# Get the category and build a category set
cats = app.Create.NewCategorySet()
cats.Insert(doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_StructuralFoundation))
cats.Insert(doc.Settings.Categories.get_Item(DB.BuiltInCategory.OST_StructuralColumns))

with DB.Transaction(doc, 'Add Parameter') as t:
    try:
        t.Start()
        newInstanceBinding = app.Create.NewInstanceBinding(cats)
        doc.ParameterBindings.Insert(externalDefinition_1, newInstanceBinding, DB.BuiltInParameterGroup.PG_LENGTH)
        doc.ParameterBindings.Insert(externalDefinition_2, newInstanceBinding, DB.BuiltInParameterGroup.PG_LENGTH)

        for element in selection:
            params_1 = element.GetParameters(param_name_1)
            params_2 = element.GetParameters(param_name_2)
            if len(params_1) > 1 or len(params_2) > 1:
                forms.alert('Remove North_Coord & East_Coord from Project parameters and try again', ok=True, exitscript=True)

        t.Commit()
    except Exception as e:
        t.RollBack()
        forms.alert('Error adding parameters: {}'.format(str(e)), title="Error", ok=True)
        sys.exit()

for ele in selection:
    try:
        x = ele.Location.Point.X
        y = ele.Location.Point.Y
        X.append(x)
        Y.append(y)
    except AttributeError:  # Handle elements without Location or Location.Point
        X.append(None)
        Y.append(None)

# Find the correct Base Point or Survey Point
locations = DB.FilteredElementCollector(doc).OfClass(DB.BasePoint).ToElements()
bp_nsouth = 0
bp_ewest = 0
angle = 0

for loc in locations:
    if coordinate_reference == 'Project Base Point' and loc.IsShared:  # Use Survey Point (previously 'Project Base Point')
        bp_nsouth = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM).AsDouble() * 0.3048
        bp_ewest = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_EASTWEST_PARAM).AsDouble() * 0.3048
    elif coordinate_reference == 'Survey Point' and not loc.IsShared:  # Use Project Base Point (previously 'Survey Point')
        if loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_ANGLETON_PARAM) is not None:
            angle = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_ANGLETON_PARAM).AsDouble()
            bp_nsouth = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM).AsDouble() - \
                        rotate(loc.Position.X, loc.Position.Y, angle)[1]
            bp_ewest = loc.get_Parameter(DB.BuiltInParameter.BASEPOINT_EASTWEST_PARAM).AsDouble() - \
                       rotate(loc.Position.X, loc.Position.Y, angle)[0]

with DB.Transaction(doc, 'Assign Coords') as t:
    try:
        t.Start()
        for element, x, y in zip(selection, X, Y):
            if x is not None and y is not None:  # Ignore data of pile caps and others with no coordinates
                tup = find_cord(x, y, angle, bp_ewest, bp_nsouth)
                north = round(float(tup[0]), 3)
                east = round(float(tup[1]), 3)
                params_1 = element.GetParameters(param_name_1)
                params_2 = element.GetParameters(param_name_2)
                for param_1, param_2 in zip(params_1, params_2):
                    if param_1.IsShared and param_2.IsShared:
                        param_1.Set(north)
                        param_2.Set(east)
        t.Commit()
    except Exception as err:
        t.RollBack()
        forms.alert('Error assigning coordinates: {}'.format(str(err)), title="Error", ok=True)
    else:
        forms.alert('Task Successfully Completed', ok=True)
