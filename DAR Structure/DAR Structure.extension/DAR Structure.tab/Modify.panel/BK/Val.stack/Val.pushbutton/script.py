from pyrevit import forms
from pyrevit import revit, DB
from pyrevit.revit import doc

# Define validation rules for connections
VALID_MATERIALS = ["Steel", "Structural Steel"]
MIN_BOLT_SIZE_MM = 10  # Example minimum bolt size in mm
VALID_ALIGNMENT = "Proper"

# Function to validate connections
def validate_connection(connection):
    """
    Validates a structural connection based on predefined rules.
    """
    # Extract connection parameters
    material = connection.LookupParameter("Material").AsString()
    bolt_size = connection.LookupParameter("Bolt Diameter").AsDouble() * 304.8  # Convert to mm
    alignment = connection.LookupParameter("Alignment").AsString()
    
    # Perform validation
    if material not in VALID_MATERIALS:
        return False, "Invalid Material: {}".format(material)
    
    if bolt_size < MIN_BOLT_SIZE_MM:
        return False, "Bolt size too small: {} mm".format(bolt_size)
    
    if alignment != VALID_ALIGNMENT:
        return False, "Improper alignment: {}".format(alignment)

    return True, "Connection Valid"

# Function to iterate over all structural connections
def validate_all_connections():
    """
    Validates all structural steel connections in the Revit model.
    """
    # Get all structural connection elements in the model
    connections = DB.FilteredElementCollector(doc) \
                    .OfCategory(DB.BuiltInCategory.OST_StructConnectionPlates) \
                    .WhereElementIsNotElementType() \
                    .ToElements()

    results = []
    
    # Iterate through each connection and validate
    for connection in connections:
        is_valid, message = validate_connection(connection)
        results.append((connection.Id, is_valid, message))
    
    return results

# Main execution
if __name__ == "__main__":
    validation_results = validate_all_connections()
    
    # Display results to user
    invalid_connections = ["Connection ID {}: {}".format(res[0], res[2]) for res in validation_results if not res[1]]
    
    if invalid_connections:
        forms.alert("Some connections failed validation:\n" + "\n".join(invalid_connections), exitscript=True)
    else:
        forms.alert("All connections are valid!", exitscript=True)
