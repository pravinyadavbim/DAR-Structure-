from Autodesk.Revit.DB import BuiltInCategory, FilteredElementCollector, BuiltInParameter
from pyrevit import forms

def move_elements_to_workset(elements, workset_name):
    for element in elements:
        param = element.get_Parameter(BuiltInParameter.ELEM_PARTITION_PARAM)
        if param and not param.IsReadOnly:
            param.Set(workset_name)

def get_elements(category):
    collector = FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
    return collector if collector else []

def process_structural_elements():
    try:
        # Get structural elements by category
        columns = get_elements(BuiltInCategory.OST_StructuralColumns)
        beams = get_elements(BuiltInCategory.OST_StructuralFraming)
        foundations = get_elements(BuiltInCategory.OST_StructuralFoundation)
        walls = get_elements(BuiltInCategory.OST_StructuralWalls)
        
        # Move elements to corresponding worksets
        if columns:
            move_elements_to_workset(columns, 'ST_Columns')
        
        if beams:
            move_elements_to_workset(beams, 'ST_Beams')
        
        if foundations:
            move_elements_to_workset(foundations, 'ST_Foundations')
        
        if walls:
            move_elements_to_workset(walls, 'ST_Walls')

    except Exception, e:  # Exception handling for IronPython
        forms.alert('Error processing structural elements: {0}'.format(e))

def main():
    if not doc.IsWorkshared:
        forms.alert("File not Workshared - Create a Workshared Model First!", title='Script Cancelled')
        return
    
    # Process structural elements
    process_structural_elements()
    forms.alert("Structural elements have been successfully assigned to worksets!", title='Process Complete')

if __name__ == '__main__':
    main()
