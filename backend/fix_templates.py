#!/usr/bin/env python3
"""
Fix Flask templates to use correct static file paths
"""
import os
import re

def fix_template_file(file_path):
    """Fix script src paths in a template file"""
    print(f"Fixing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace relative JS paths with Flask url_for
    replacements = [
        # Common JS files
        (r'<script src="../js/api-client\.js"></script>', 
         '<script src="{{ url_for(\'static\', filename=\'js/api-client.js\') }}"></script>'),
        (r'<script src="../js/router\.js"></script>', 
         '<script src="{{ url_for(\'static\', filename=\'js/router.js\') }}"></script>'),
        (r'<script src="../js/utils\.js"></script>', 
         '<script src="{{ url_for(\'static\', filename=\'js/utils.js\') }}"></script>'),
        
        # Page-specific JS files
        (r'<script src="attendance\.js"></script>', 
         '<script src="{{ url_for(\'static\', filename=\'js/attendance.js\') }}"></script>'),
        (r'<script src="enrollment\.js"></script>', 
         '<script src="{{ url_for(\'static\', filename=\'js/enrollment.js\') }}"></script>'),
        (r'<script src="dashboard\.js"></script>', 
         '<script src="{{ url_for(\'static\', filename=\'js/dashboard.js\') }}"></script>'),
        (r'<script src="registration\.js"></script>', 
         '<script src="{{ url_for(\'static\', filename=\'js/registration.js\') }}"></script>'),
        (r'<script src="reports\.js"></script>', 
         '<script src="{{ url_for(\'static\', filename=\'js/reports.js\') }}"></script>'),
    ]
    
    # Apply replacements
    original_content = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Check if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Updated script paths")
        return True
    else:
        print(f"  ℹ️  No changes needed")
        return False

def main():
    """Fix all template files"""
    print("Fixing Flask template script paths...")
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
                if fix_template_file(html_file):
                    total_fixed += 1
            else:
                print(f"❌ File not found: {html_file}")
        else:
            print(f"❌ Directory not found: {template_dir}")
    
    print("=" * 50)
    print(f"Fixed {total_fixed} template files")
    print("\nNext steps:")
    print("1. Run: cd backend && python app_simple.py")
    print("2. Open: http://localhost:5000")
    print("3. Test all pages work correctly")

if __name__ == '__main__':
    main()