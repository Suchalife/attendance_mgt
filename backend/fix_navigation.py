#!/usr/bin/env python3
"""
Fix navigation links in Flask templates to use Flask routes
"""
import os
import re

def fix_navigation_links(file_path):
    """Fix navigation links in a template file"""
    print(f"Fixing navigation in: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace # links with Flask routes
    replacements = [
        # Navigation links
        (r'href="#"([^>]*>[\s\n]*<span[^>]*data-icon="dashboard")', r'href="/dashboard"\1'),
        (r'href="#"([^>]*>[\s\n]*<span[^>]*data-icon="person_add")', r'href="/registration"\1'),
        (r'href="#"([^>]*>[\s\n]*<span[^>]*data-icon="fingerprint")', r'href="/enrollment"\1'),
        (r'href="#"([^>]*>[\s\n]*<span[^>]*data-icon="event_available")', r'href="/attendance"\1'),
        (r'href="#"([^>]*>[\s\n]*<span[^>]*data-icon="analytics")', r'href="/reports"\1'),
    ]
    
    # Apply replacements
    original_content = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Check if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Updated navigation links")
        return True
    else:
        print(f"  ℹ️  No navigation changes needed")
        return False

def main():
    """Fix navigation in all template files"""
    print("Fixing Flask template navigation links...")
    print("=" * 50)
    
    # Template directories to fix
    template_dirs = [
        'templates/live_attendance',
        'templates/biometric_enrollment_expanded',
        'templates/operations_dashboard',
        'templates/employee_registration_updated',
        'templates/attendance_reports_simplified'
    ]
    
    total_fixed = 0
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            html_file = os.path.join(template_dir, 'code.html')
            if os.path.exists(html_file):
                if fix_navigation_links(html_file):
                    total_fixed += 1
            else:
                print(f"❌ File not found: {html_file}")
        else:
            print(f"❌ Directory not found: {template_dir}")
    
    print("=" * 50)
    print(f"Fixed navigation in {total_fixed} template files")

if __name__ == '__main__':
    main()