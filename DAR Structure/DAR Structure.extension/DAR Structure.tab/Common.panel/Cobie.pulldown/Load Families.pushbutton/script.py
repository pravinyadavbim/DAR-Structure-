from pyrevit import forms, revit, DB
import json
import os

TEMPLATE_FILE = "view_range_templates.json"

# Load templates from file
def load_templates():
    if not os.path.exists(TEMPLATE_FILE):
        return {}
    with open(TEMPLATE_FILE, 'r') as f:
        return json.load(f)

# Save templates to file
def save_templates(templates):
    with open(TEMPLATE_FILE, 'w') as f:
        json.dump(templates, f, indent=4)

# Apply view range settings
def apply_view_range(view, top, bottom, depth):
    if isinstance(view, DB.ViewPlan):  # Ensure the view is a floor plan
        view.get_Parameter(DB.BuiltInParameter.VIEW_RANGE).Set(top)
        view.get_Parameter(DB.BuiltInParameter.BOTTOM_CLIP).Set(bottom)
        view.get_Parameter(DB.BuiltInParameter.VIEW_DEPTH).Set(depth)
        print("Updated {} - Top: {}, Bottom: {}, Depth: {}".format(view.Name, top, bottom, depth))

# Main function
def main():
    # Load existing templates
    templates = load_templates()
    
    # Select operation
    operation = forms.alert("Choose an operation:", yes="Create Template", no="Apply Template", cancel="Cancel")
    
    if operation == 'Cancel':
        return
    
    # Create a new template
    if operation == 'Create Template':
        name = forms.ask_for_string("Enter Template Name:")
        top = forms.ask_for_number("Enter Top Offset:")
        bottom = forms.ask_for_number("Enter Bottom Offset:")
        depth = forms.ask_for_number("Enter View Depth:")
        
        templates[name] = {'top': top, 'bottom': bottom, 'depth': depth}
        save_templates(templates)
        forms.alert("Template '{}' created successfully!".format(name))
    
    # Apply an existing template
    elif operation == 'Apply Template':
        if not templates:
            forms.alert("No templates available!")
            return
        
        template_name = forms.SelectFromList("Choose a Template:", list(templates.keys()))
        selected_views = forms.select_views(multi=True)  # Select views to apply the template
        
        if template_name and selected_views:
            template = templates[template_name]
            for view in selected_views:
                apply_view_range(view, template['top'], template['bottom'], template['depth'])
            forms.alert("Applied template '{}' to selected views.".format(template_name))

# Run the script
main()
