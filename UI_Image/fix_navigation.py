#!/usr/bin/env python3
"""
Script to add nav-item class to sidebar navigation links
Adds class="nav-item" to clickable menu items without modifying structure
"""

import os
import re

# Define the files to update
html_files = [
    'operations_dashboard/code.html',
    'employee_registration_updated/code.html',
    'biometric_enrollment_expanded/code.html',
    'live_attendance/code.html',
    'attendance_reports_simplified/code.html'
]

# Navigation items to target (text content)
nav_items = [
    'Dashboard',
    'Employee Registration',
    'Biometric Enrollment',
    'Attendance',
    'Reports'
]

def add_nav_item_class(filepath):
    """Add nav-item class to navigation links"""
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated
    if 'class="nav-item' in content or 'class=\'nav-item' in content:
        print(f"✓ nav-item class already present in {filepath}")
        return False
    
    original_content = content
    modified = False
    
    # Pattern to match <a> tags in sidebar navigation
    # Look for <a> tags that contain navigation text
    patterns = [
        # Pattern 1: <a class="..." href="#">
        (r'(<a\s+class="[^"]*")(\s+href="#"[^>]*>[\s\S]*?(?:Dashboard|Employee Registration|Biometric Enrollment|Attendance|Reports))',
         r'\1 nav-item\2'),
        
        # Pattern 2: <a href="#" class="...">
        (r'(<a\s+href="#"\s+class="[^"]*")([^>]*>[\s\S]*?(?:Dashboard|Employee Registration|Biometric Enrollment|Attendance|Reports))',
         r'\1 nav-item\2'),
        
        # Pattern 3: <a class="..."> (no href yet)
        (r'(<a\s+class="[^"]*")(>[\s\S]*?(?:Dashboard|Employee Registration|Biometric Enrollment|Attendance|Reports))',
         r'\1 nav-item\2'),
    ]
    
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True
    
    # If patterns didn't work, try a more direct approach
    # Find <a> tags in the sidebar navigation section
    if not modified:
        # Look for navigation links in <aside> or <nav> sections
        lines = content.split('\n')
        new_lines = []
        in_nav = False
        
        for line in lines:
            # Detect if we're in navigation section
            if '<aside' in line or '<nav' in line:
                in_nav = True
            elif '</aside>' in line or '</nav>' in line:
                in_nav = False
            
            # If in navigation and line has <a> tag with navigation text
            if in_nav and '<a' in line:
                has_nav_text = any(item in line for item in nav_items)
                if has_nav_text and 'nav-item' not in line:
                    # Add nav-item class
                    if 'class="' in line:
                        line = line.replace('class="', 'class="nav-item ')
                    elif "class='" in line:
                        line = line.replace("class='", "class='nav-item ")
                    else:
                        # Add class attribute after <a
                        line = line.replace('<a ', '<a class="nav-item" ')
                    modified = True
            
            new_lines.append(line)
        
        if modified:
            content = '\n'.join(new_lines)
    
    # Write back if modified
    if modified and content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Added nav-item class to {filepath}")
        return True
    else:
        print(f"✗ Could not update {filepath} (no changes made)")
        return False

def main():
    """Main function"""
    print("Adding nav-item class to sidebar navigation links...\n")
    
    updated_count = 0
    
    for filepath in html_files:
        if os.path.exists(filepath):
            if add_nav_item_class(filepath):
                updated_count += 1
        else:
            print(f"✗ File not found: {filepath}")
    
    print(f"\n{'='*50}")
    print(f"Updated {updated_count} file(s)")
    print(f"{'='*50}")
    
    if updated_count > 0:
        print("\n✓ Navigation classes added successfully!")
        print("\nNext steps:")
        print("1. Refresh your browser")
        print("2. Click sidebar navigation items")
        print("3. Navigation should work without page reload")
    else:
        print("\n✓ No files needed updating (nav-item already present)")

if __name__ == '__main__':
    main()
