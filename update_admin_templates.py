import os
import glob

# Directory containing admin templates
templates_dir = r'c:\Users\pinja\OneDrive\Desktop\BharatMoovers\BharatMovers\templates\accounts\admin'

# Find all HTML files except admin_base.html and base_admin.html
template_files = glob.glob(os.path.join(templates_dir, '*.html'))
template_files = [f for f in template_files if os.path.basename(f) not in ['admin_base.html', 'base_admin.html']]

# Update each file
for file_path in template_files:
    print(f"Processing {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace the extends statement
    updated_content = content.replace(
        '{% extends "accounts/admin/base_admin.html" %}',
        '{% extends "accounts/admin/admin_base.html" %}'
    )
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"Updated {file_path}")

print(f"Updated {len(template_files)} template files to use admin_base.html")
