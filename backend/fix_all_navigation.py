#!/usr/bin/env python3
"""
Fix all navigation links in Flask templates to use correct Flask routes
"""
import os
import re

def fix_navigation_in_file(file_path):
    """Fix navigation links in a template file"""
    print(f"Fixing navigation in: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace all navigation links with Flask routes
    # Pattern: href="#" or href="any_path" followed by navigation items
    
    # Dashboard links
    content = re.sub(
        r'href="[^"]*"(\s+[^>]*>\s*<span[^>]*data-icon="dashboard"[^>]*>[^<]*</span>\s*Dashboard)',
        r'href="/dashboard"\1',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Employee Registration links
    content = re.sub(
        r'href="[^"]*"(\s+[^>]*>\s*<span[^>]*data-icon="person_add"[^>]*>[^<]*</span>\s*Employee Registration)',
        r'href="/registration"\1',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Biometric Enrollment links
    content = re.sub(
        r'href="[^"]*"(\s+[^>]*>\s*<span[^>]*data-icon="fingerprint"[^>]*>[^<]*</span>\s*Biometric Enrollment)',
        r'href="/enrollment"\1',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Attendance links
    content = re.sub(
        r'href="[^"]*"(\s+[^>]*>\s*<span[^>]*data-icon="event_available"[^>]*>[^<]*</span>\s*Attendance)',
        r'href="/attendance"\1',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Reports links
    content = re.sub(
        r'href="[^"]*"(\s+[^>]*>\s*<span[^>]*data-icon="analytics"[^>]*>[^<]*</span>\s*Reports)',
        r'href="/reports"\1',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Alternative patterns for different HTML structures
    # Simple text-based matching for navigation items
    
    # Dashboard
    content = re.sub(
        r'<a\s+class="[^"]*nav-item[^"]*"\s+href="[^"]*"([^>]*>\s*<span[^>]*>[^<]*</span>\s*Dashboard)',
        r'<a class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-2 text-sm font-medium transition-colors duration-200 rounded-md" href="/dashboard"\1',
        content
    )
    
    # Employee Registration
    content = re.sub(
        r'<a\s+class="[^"]*nav-item[^"]*"\s+href="[^"]*"([^>]*>\s*<span[^>]*>[^<]*</span>\s*Employee Registration)',
        r'<a class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-2 text-sm font-medium transition-colors duration-200 rounded-md" href="/registration"\1',
        content
    )
    
    # Biometric Enrollment
    content = re.sub(
        r'<a\s+class="[^"]*nav-item[^"]*"\s+href="[^"]*"([^>]*>\s*<span[^>]*>[^<]*</span>\s*Biometric Enrollment)',
        r'<a class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-2 text-sm font-medium transition-colors duration-200 rounded-md" href="/enrollment"\1',
        content
    )
    
    # Attendance
    content = re.sub(
        r'<a\s+class="[^"]*nav-item[^"]*"\s+href="[^"]*"([^>]*>\s*<span[^>]*>[^<]*</span>\s*Attendance)',
        r'<a class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-2 text-sm font-medium transition-colors duration-200 rounded-md" href="/attendance"\1',
        content
    )
    
    # Reports
    content = re.sub(
        r'<a\s+class="[^"]*nav-item[^"]*"\s+href="[^"]*"([^>]*>\s*<span[^>]*>[^<]*</span>\s*Reports)',
        r'<a class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-2 text-sm font-medium transition-colors duration-200 rounded-md" href="/reports"\1',
        content
    )
    
    # Check if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Updated navigation links")
        return True
    else:
        print(f"  ℹ️  No changes needed")
        return False

def main():
    """Fix navigation in all template files"""
    print("Fixing ALL navigation links in Flask templates...")
    print("=" * 60)
    
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
                if fix_navigation_in_file(html_file):
                    total_fixed += 1
            else:
                print(f"❌ File not found: {html_file}")
        else:
            print(f"❌ Directory not found: {template_dir}")
    
    print("=" * 60)
    print(f"Fixed navigation in {total_fixed} template files")
    print("\nNavigation routes updated:")
    print("  Dashboard → /dashboard")
    print("  Employee Registration → /registration")
    print("  Biometric Enrollment → /enrollment")
    print("  Attendance → /attendance")
    print("  Reports → /reports")
    print("\nTest by running: python app_simple.py")

if __name__ == '__main__':
    main()