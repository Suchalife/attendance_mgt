#!/usr/bin/env python3
"""
Comprehensive fix for all navigation links in Flask templates
"""
import os
import re

def fix_navigation_comprehensive(file_path):
    """Comprehensively fix all navigation links"""
    print(f"Fixing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Method 1: Replace any href="#" or href="anything" that contains navigation text
    
    # Dashboard navigation
    content = re.sub(
        r'(<a[^>]+)href="[^"]*"([^>]*>[^<]*<span[^>]*data-icon="dashboard"[^>]*>[^<]*</span>[^<]*Dashboard[^<]*</a>)',
        r'\1href="/dashboard"\2',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Employee Registration navigation
    content = re.sub(
        r'(<a[^>]+)href="[^"]*"([^>]*>[^<]*<span[^>]*data-icon="person_add"[^>]*>[^<]*</span>[^<]*Employee Registration[^<]*</a>)',
        r'\1href="/registration"\2',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Biometric Enrollment navigation
    content = re.sub(
        r'(<a[^>]+)href="[^"]*"([^>]*>[^<]*<span[^>]*data-icon="fingerprint"[^>]*>[^<]*</span>[^<]*Biometric Enrollment[^<]*</a>)',
        r'\1href="/enrollment"\2',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Attendance navigation
    content = re.sub(
        r'(<a[^>]+)href="[^"]*"([^>]*>[^<]*<span[^>]*data-icon="event_available"[^>]*>[^<]*</span>[^<]*Attendance[^<]*</a>)',
        r'\1href="/attendance"\2',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Reports navigation
    content = re.sub(
        r'(<a[^>]+)href="[^"]*"([^>]*>[^<]*<span[^>]*data-icon="analytics"[^>]*>[^<]*</span>[^<]*Reports[^<]*</a>)',
        r'\1href="/reports"\2',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Method 2: Line-by-line replacement for simpler patterns
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Dashboard
        if 'data-icon="dashboard"' in line and 'Dashboard' in line:
            lines[i] = re.sub(r'href="[^"]*"', 'href="/dashboard"', line)
        
        # Employee Registration
        elif 'data-icon="person_add"' in line and 'Employee Registration' in line:
            lines[i] = re.sub(r'href="[^"]*"', 'href="/registration"', line)
        
        # Biometric Enrollment
        elif 'data-icon="fingerprint"' in line and 'Biometric Enrollment' in line:
            lines[i] = re.sub(r'href="[^"]*"', 'href="/enrollment"', line)
        
        # Attendance
        elif 'data-icon="event_available"' in line and 'Attendance' in line:
            lines[i] = re.sub(r'href="[^"]*"', 'href="/attendance"', line)
        
        # Reports
        elif 'data-icon="analytics"' in line and 'Reports' in line:
            lines[i] = re.sub(r'href="[^"]*"', 'href="/reports"', line)
    
    content = '\n'.join(lines)
    
    # Check if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Updated navigation links")
        return True
    else:
        print(f"  ℹ️  No changes needed")
        return False

def verify_navigation_links(file_path):
    """Verify that navigation links are correct"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for correct links
    checks = [
        ('Dashboard', '/dashboard'),
        ('Employee Registration', '/registration'),
        ('Biometric Enrollment', '/enrollment'),
        ('Attendance', '/attendance'),
        ('Reports', '/reports')
    ]
    
    print(f"  Verifying {file_path}:")
    for text, expected_href in checks:
        if text in content:
            if f'href="{expected_href}"' in content:
                print(f"    ✅ {text} → {expected_href}")
            else:
                print(f"    ❌ {text} → NOT FIXED")

def main():
    """Fix and verify navigation in all template files"""
    print("Comprehensive Navigation Link Fix")
    print("=" * 60)
    
    template_dirs = [
        'templates/live_attendance',
        'templates/biometric_enrollment_expanded',
        'templates/operations_dashboard',
        'templates/employee_registration_updated',
        'templates/attendance_reports_simplified'
    ]
    
    # Fix navigation
    total_fixed = 0
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            html_file = os.path.join(template_dir, 'code.html')
            if os.path.exists(html_file):
                if fix_navigation_comprehensive(html_file):
                    total_fixed += 1
    
    print("=" * 60)
    print(f"Fixed navigation in {total_fixed} files")
    
    # Verify navigation
    print("\nVerification:")
    print("-" * 30)
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            html_file = os.path.join(template_dir, 'code.html')
            if os.path.exists(html_file):
                verify_navigation_links(html_file)
    
    print("\n" + "=" * 60)
    print("Navigation update complete!")
    print("Test by running: python app_simple.py")

if __name__ == '__main__':
    main()