#!/usr/bin/env python3
"""
Test script to verify navigation fix was applied correctly.
Checks that all HTML files have nav-item classes on the correct elements.
"""

import re
from pathlib import Path

# HTML files to check
HTML_FILES = [
    "operations_dashboard/code.html",
    "employee_registration_updated/code.html",
    "biometric_enrollment_expanded/code.html",
    "live_attendance/code.html",
    "attendance_reports_simplified/code.html"
]

# Expected navigation items (should have nav-item class)
EXPECTED_NAV_ITEMS = [
    "dashboard",
    "person_add",
    "fingerprint",
    "event_available",
    "analytics"
]

def check_nav_items(html_content, filename):
    """Check if all navigation items have nav-item class."""
    results = []
    
    for icon in EXPECTED_NAV_ITEMS:
        # Pattern to find elements with this icon
        pattern = rf'<(?:a|div)\s+class="([^"]*)"[^>]*>\s*<span[^>]*>{icon}</span>'
        matches = re.findall(pattern, html_content, re.DOTALL)
        
        if matches:
            for match in matches:
                has_nav_item = 'nav-item' in match
                results.append({
                    'icon': icon,
                    'has_nav_item': has_nav_item,
                    'classes': match
                })
        else:
            results.append({
                'icon': icon,
                'has_nav_item': False,
                'classes': 'NOT FOUND'
            })
    
    return results

def main():
    """Run tests on all HTML files."""
    base_dir = Path(__file__).parent
    all_passed = True
    
    print("=" * 70)
    print("NAVIGATION FIX VERIFICATION")
    print("=" * 70)
    print()
    
    for html_file in HTML_FILES:
        file_path = base_dir / html_file
        
        if not file_path.exists():
            print(f"❌ File not found: {html_file}")
            all_passed = False
            continue
        
        print(f"📄 {html_file}")
        print("-" * 70)
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check nav items
        results = check_nav_items(content, html_file)
        
        file_passed = True
        for result in results:
            icon = result['icon']
            has_nav_item = result['has_nav_item']
            
            if has_nav_item:
                print(f"  ✅ {icon:20s} - has nav-item class")
            else:
                print(f"  ❌ {icon:20s} - MISSING nav-item class")
                file_passed = False
        
        if file_passed:
            print(f"  ✅ All navigation items have nav-item class")
        else:
            print(f"  ❌ Some navigation items missing nav-item class")
            all_passed = False
        
        print()
    
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print()
        print("Next steps:")
        print("1. Start backend: cd backend && python app_simple.py")
        print("2. Open UI_Image/operations_dashboard/code.html in browser")
        print("3. Test navigation by clicking sidebar links")
        print("4. Verify dashboard shows real employee count")
    else:
        print("❌ SOME TESTS FAILED!")
        print()
        print("Run: python UI_Image/add_nav_item_class.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
