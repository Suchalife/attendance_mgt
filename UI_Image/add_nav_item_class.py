#!/usr/bin/env python3
"""
Script to add 'nav-item' class to navigation links in HTML files.
This enables the router.js to properly handle navigation clicks.
"""

import re
from pathlib import Path

# HTML files to update
HTML_FILES = [
    "operations_dashboard/code.html",
    "employee_registration_updated/code.html",
    "biometric_enrollment_expanded/code.html",
    "live_attendance/code.html",
    "attendance_reports_simplified/code.html"
]

# Navigation items that need the nav-item class (NOT Settings or Support)
NAV_PATTERNS = [
    (r'(<(?:a|div)\s+class="(?!.*nav-item)([^"]*)"[^>]*>\s*<span[^>]*>dashboard</span>)', r'\1 nav-item'),
    (r'(<(?:a|div)\s+class="(?!.*nav-item)([^"]*)"[^>]*>\s*<span[^>]*>person_add</span>)', r'\1 nav-item'),
    (r'(<(?:a|div)\s+class="(?!.*nav-item)([^"]*)"[^>]*>\s*<span[^>]*>fingerprint</span>)', r'\1 nav-item'),
    (r'(<(?:a|div)\s+class="(?!.*nav-item)([^"]*)"[^>]*>\s*<span[^>]*>event_available</span>)', r'\1 nav-item'),
    (r'(<(?:a|div)\s+class="(?!.*nav-item)([^"]*)"[^>]*>\s*<span[^>]*>analytics</span>)', r'\1 nav-item'),
]

def add_nav_item_class(html_content):
    """Add nav-item class to navigation links."""
    modified = html_content
    
    # Find all navigation links and add nav-item class
    # Pattern: class="..." where the element contains Dashboard, Employee Registration, etc.
    patterns = [
        # Dashboard
        (r'(<(?:a|div)\s+class=")([^"]*?)("(?:[^>]*?)>\s*<span[^>]*>dashboard</span>)',
         lambda m: f'{m.group(1)}nav-item {m.group(2)}{m.group(3)}' if 'nav-item' not in m.group(2) else m.group(0)),
        # Employee Registration
        (r'(<(?:a|div)\s+class=")([^"]*?)("(?:[^>]*?)>\s*<span[^>]*>person_add</span>)',
         lambda m: f'{m.group(1)}nav-item {m.group(2)}{m.group(3)}' if 'nav-item' not in m.group(2) else m.group(0)),
        # Biometric Enrollment
        (r'(<(?:a|div)\s+class=")([^"]*?)("(?:[^>]*?)>\s*<span[^>]*>fingerprint</span>)',
         lambda m: f'{m.group(1)}nav-item {m.group(2)}{m.group(3)}' if 'nav-item' not in m.group(2) else m.group(0)),
        # Attendance
        (r'(<(?:a|div)\s+class=")([^"]*?)("(?:[^>]*?)>\s*<span[^>]*>event_available</span>)',
         lambda m: f'{m.group(1)}nav-item {m.group(2)}{m.group(3)}' if 'nav-item' not in m.group(2) else m.group(0)),
        # Reports
        (r'(<(?:a|div)\s+class=")([^"]*?)("(?:[^>]*?)>\s*<span[^>]*>analytics</span>)',
         lambda m: f'{m.group(1)}nav-item {m.group(2)}{m.group(3)}' if 'nav-item' not in m.group(2) else m.group(0)),
    ]
    
    for pattern, replacement in patterns:
        modified = re.sub(pattern, replacement, modified, flags=re.DOTALL)
    
    return modified

def main():
    """Process all HTML files."""
    base_dir = Path(__file__).parent
    
    for html_file in HTML_FILES:
        file_path = base_dir / html_file
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
        
        print(f"Processing: {html_file}")
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add nav-item class
        modified_content = add_nav_item_class(content)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"✅ Updated: {html_file}")
    
    print("\n✅ All files updated successfully!")
    print("\nNext steps:")
    print("1. Open any HTML file in browser")
    print("2. Click navigation links")
    print("3. Verify navigation works correctly")

if __name__ == "__main__":
    main()
