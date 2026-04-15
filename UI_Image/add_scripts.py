#!/usr/bin/env python3
"""
Script to add JavaScript tags to all frontend HTML files
Adds script tags before the closing </body> tag
"""

import os
import re

# Define the files and their corresponding script tags
files_to_update = {
    'operations_dashboard/code.html': [
        '<script src="../js/api-client.js"></script>',
        '<script src="../js/router.js"></script>',
        '<script src="../js/utils.js"></script>',
        '<script src="dashboard.js"></script>'
    ],
    'employee_registration_updated/code.html': [
        '<script src="../js/api-client.js"></script>',
        '<script src="../js/router.js"></script>',
        '<script src="../js/utils.js"></script>',
        '<script src="registration.js"></script>'
    ],
    'biometric_enrollment_expanded/code.html': [
        '<script src="../js/api-client.js"></script>',
        '<script src="../js/router.js"></script>',
        '<script src="../js/utils.js"></script>',
        '<script src="enrollment.js"></script>'
    ],
    'live_attendance/code.html': [
        '<script src="../js/api-client.js"></script>',
        '<script src="../js/router.js"></script>',
        '<script src="../js/utils.js"></script>',
        '<script src="attendance.js"></script>'
    ],
    'attendance_reports_simplified/code.html': [
        '<script src="../js/api-client.js"></script>',
        '<script src="../js/router.js"></script>',
        '<script src="../js/utils.js"></script>',
        '<script src="reports.js"></script>'
    ]
}

def add_scripts_to_file(filepath, scripts):
    """Add script tags before closing </body> tag"""
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if scripts already added
    if 'api-client.js' in content:
        print(f"✓ Scripts already present in {filepath}")
        return False
    
    # Create script block
    script_block = '\n<!-- API Integration Scripts -->\n'
    script_block += '\n'.join(scripts)
    script_block += '\n'
    
    # Find </body> tag and insert before it
    if '</body>' in content:
        content = content.replace('</body>', f'{script_block}</body>')
    else:
        print(f"✗ Could not find </body> tag in {filepath}")
        return False
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Added scripts to {filepath}")
    return True

def main():
    """Main function"""
    print("Adding JavaScript script tags to HTML files...\n")
    
    updated_count = 0
    
    for filepath, scripts in files_to_update.items():
        if os.path.exists(filepath):
            if add_scripts_to_file(filepath, scripts):
                updated_count += 1
        else:
            print(f"✗ File not found: {filepath}")
    
    print(f"\n{'='*50}")
    print(f"Updated {updated_count} file(s)")
    print(f"{'='*50}")
    
    if updated_count > 0:
        print("\n✓ All script tags added successfully!")
        print("\nNext steps:")
        print("1. Start backend: cd backend && python app_simple.py")
        print("2. Start frontend: python -m http.server 8000")
        print("3. Open: http://localhost:8000/operations_dashboard/code.html")
    else:
        print("\n✓ No files needed updating (scripts already present)")

if __name__ == '__main__':
    main()
