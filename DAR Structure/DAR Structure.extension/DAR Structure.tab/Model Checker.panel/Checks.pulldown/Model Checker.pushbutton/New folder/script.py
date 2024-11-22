# -*- coding: utf-8 -*-
"""
Model Checker Automation Script with XML Template Logic
"""

__title__ = "Model Checker with XML"
__author__ = "Your Name"

# Imports
from pyrevit import forms, script
import os
import xml.etree.ElementTree as ET  # For parsing XML templates

# Step 1: Prompt user to select between Structural Concrete or Structural Steel
structure_type = forms.alert(
    "Select Structure Type", 
    title="Choose Structure", 
    options=["Structural Concrete", "Structural Steel"]
)

# Step 2: After selecting structure, prompt for template type (General 1, General 2, iLOD)
if structure_type:
    template_type = forms.alert(
        "Select Template Type", 
        title="Choose Template", 
        options=["General 1", "General 2", "iLOD"]
    )

# Step 3: Define paths for XML templates based on structure type
xml_paths_concrete = {
    "General 1": r"C:\Users\pyadav\Desktop\BIM_Work\06 Automation\pySTR\DAR Structure\DAR Structure.extension\DAR Structure.tab\Model Checker.panel\Model Checker.stack\Model Checker.pushbutton\Templates\0-GN\DAR_GN_Revit Model Quality Checks.xml",
    "General 2": r"K:\\BIM\\Interoperability\\Concrete\\General_02_Template.xml",
    "iLOD": r"K:\\BIM\\Interoperability\\Concrete\\iLOD_Template.xml"
}

xml_paths_steel = {
    "General 1": r"K:\\BIM\\Interoperability\\Steel\\General_01_Template.xml",
    "General 2": r"K:\\BIM\\Interoperability\\Steel\\General_02_Template.xml",
    "iLOD": r"K:\\BIM\\Interoperability\\Steel\\iLOD_Template.xml"
}

# Step 4: Function to get the appropriate XML path based on structure type
def get_xml_path(structure, template):
    if structure == "Structural Concrete":
        return xml_paths_concrete.get(template)
    elif structure == "Structural Steel":
        return xml_paths_steel.get(template)
    return None

# Step 5: Function to parse XML and extract checks
def parse_xml_for_checks(xml_file):
    """Parse the XML file to extract model check rules."""
    checks = []
    try:
        # Print the first few lines of the file for debugging
        with open(xml_file, 'r') as f:
            print("File contents (first 100 characters):", f.read(100))
        
        # Check if file is readable and contains valid XML structure
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Assume XML contains 'Check' elements with a 'Name' attribute and 'Condition' elements
        for check in root.findall('Check'):
            check_name = check.get('Name')
            condition = check.find('Condition').text
            checks.append((check_name, condition))
    
    except ET.ParseError as e:
        forms.alert("Error parsing XML file: {0}".format(e), title="XML Error", warn_icon=True)
    except IOError as e:
        forms.alert("File error: {0}".format(e), title="File Error", warn_icon=True)
    except Exception as e:
        forms.alert("Unexpected error: {0}".format(e), title="Unexpected Error", warn_icon=True)
    
    return checks


def run_model_checks_from_xml(xml_file_path):
    """Run model checks based on an XML template."""
    if not os.path.exists(xml_file_path):
        forms.alert("The specified XML file does not exist: {0}".format(xml_file_path), 
                    title="File Not Found", warn_icon=True)
        return

    # Parse the XML file for checks
    checks = parse_xml_for_checks(xml_file_path)
    
    if not checks:
        forms.alert("No checks found in the XML file.", title="No Checks", warn_icon=True)
        return

    # Run checks and output the result
    for check_name, condition in checks:
        # Placeholder for running the actual check - logic will depend on Revit API specifics
        print("Running check: {0} with condition: {1}".format(check_name, condition))
        # Simulate running the check (this would be integrated with Revit API in a real scenario)
        # result = run_check_in_revit(check_name, condition)
        # print("Check result for {0}: {1}".format(check_name, result))


# Example of setting an XML file path, modify as needed
xml_template_path = os.path.join(os.path.dirname(__file__), 
                                 "Templates", 
                                 "0-GN", 
                                 "DAR_GN_Revit Model Quality Checks.xml")

print("XML Path:", xml_template_path)

# Run the checks using the XML file
run_model_checks_from_xml(xml_template_path)# Step 6: Function to run checks based on XML template
def run_model_checks_from_xml(structure, template):
    """Run compliance checks based on structure and XML template selection."""
    xml_path = get_xml_path(structure, template)
    
    # Debugging: Print XML Path for reference
    print("XML Path:", xml_path)
    
    # Check if file exists, otherwise prompt user to select the file manually
    if not os.path.exists(xml_path):
        forms.alert("File not found at {0}. Please select the XML file manually.".format(xml_path), title="File Not Found")
        xml_path = forms.pick_file(file_ext='xml', title="Select the XML Template")
    
    if not xml_path:
        return "XML template path not found or not selected. Exiting."

    # Parse the XML template to get checks
    checks = parse_xml_for_checks(xml_path)
    
    if not checks:
        return "No checks found in the XML template."

    # Placeholder logic for applying the checks (to be customized)
    check_results = []
    for check_name, condition in checks:
        # Example: Check could be applied using Revit API logic here
        # Assuming all checks are passing for demonstration
        check_result = "Pass" if condition == "True" else "Fail"  # Example evaluation, replace with real logic
        check_results.append((check_name, check_result))
    
    return check_results

# Step 7: Run the selected model checks
check_results = []
if structure_type and template_type:
    check_results = run_model_checks_from_xml(structure_type, template_type)

# Step 8: Prompt user to select a folder to save the HTML report
save_folder = forms.pick_folder(title="Select Folder to Save HTML Report")

# Step 9: Save the results to an HTML file in the selected folder
if save_folder:
    report_file = os.path.join(save_folder, "Model_Check_Report_{0}_{1}.html".format(structure_type, template_type))
    
    # Generate HTML content with dynamic check results
    html_content = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        "    <meta charset=\"UTF-8\">\n"
        "    <title>Model Checker Report - {0} - {1}</title>\n"
        "    <style>\n"
        "        body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; }}\n"
        "        h1 {{ color: #00539C; }}\n"
        "        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}\n"
        "        table, th, td {{ border: 1px solid #ccc; padding: 8px; }}\n"
        "        th {{ background-color: #f4f4f4; color: #00539C; }}\n"
        "        td {{ text-align: left; }}\n"
        "    </style>\n"
        "</head>\n"
        "<body>\n"
        "    <h1>Model Checker Report</h1>\n"
        "    <p>Structure Type: {0}</p>\n"
        "    <p>Template Type: {1}</p>\n"
        "    <p>XML Path: {2}</p>\n"
        "    <h2>Check Results</h2>\n"
        "    <table>\n"
        "        <tr><th>Check Name</th><th>Result</th></tr>\n"
    ).format(structure_type, template_type, get_xml_path(structure_type, template_type))
    
    # Add check results to HTML table
    for check_name, check_result in check_results:
        html_content += "<tr><td>{0}</td><td>{1}</td></tr>\n".format(check_name, check_result)
    
    html_content += (
        "    </table>\n"
        "    <p>Generated by Model Checker Automation Script</p>\n"
        "</body>\n"
        "</html>\n"
    )
    
    # Write the HTML content to the file
    with open(report_file, 'w') as f:
        f.write(html_content)
    
    forms.alert("HTML Report saved at {0}".format(report_file), title="Report Generated")
else:
    forms.alert("No folder selected. Exiting the script.", title="Report Not Saved", warn_icon=True)
