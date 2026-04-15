#!/usr/bin/env python3
"""
Fix biometric enrollment navigation specifically
"""
import os

def fix_biometric_navigation():
    """Fix the biometric enrollment navigation"""
    file_path = 'templates/biometric_enrollment_expanded/code.html'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"Fixing biometric enrollment navigation...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace div navigation elements with anchor elements
    replacements = [
        # Dashboard
        ('<div class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-3 cursor-pointer transition-colors duration-200 font-medium tracking-tight text-sm scale-95 active:scale-90">\n<span class="material-symbols-outlined mr-3">dashboard</span>\n                Dashboard\n            </div>',
         '<a href="/dashboard" class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-3 cursor-pointer transition-colors duration-200 font-medium tracking-tight text-sm scale-95 active:scale-90">\n<span class="material-symbols-outlined mr-3">dashboard</span>\n                Dashboard\n            </a>'),
        
        # Employee Registration
        ('<div class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-3 cursor-pointer transition-colors duration-200 font-medium tracking-tight text-sm scale-95 active:scale-90">\n<span class="material-symbols-outlined mr-3">person_add</span>\n                Employee Registration\n            </div>',
         '<a href="/registration" class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-3 cursor-pointer transition-colors duration-200 font-medium tracking-tight text-sm scale-95 active:scale-90">\n<span class="material-symbols-outlined mr-3">person_add</span>\n                Employee Registration\n            </a>'),
        
        # Biometric Enrollment (active)
        ('<div class="nav-item bg-[#0058be] text-white rounded-md mx-2 flex items-center px-4 py-3 cursor-pointer transition-colors duration-200 font-medium tracking-tight text-sm scale-95 active:scale-90">\n<span class="material-symbols-outlined mr-3" style="font-variation-settings: \'FILL\' 1;">fingerprint</span>\n                Biometric Enrollment\n            </div>',
         '<a href="/enrollment" class="nav-item bg-[#0058be] text-white rounded-md mx-2 flex items-center px-4 py-3 cursor-pointer transition-colors duration-200 font-medium tracking-tight text-sm scale-95 active:scale-90">\n<span class="material-symbols-outlined mr-3" style="font-variation-settings: \'FILL\' 1;">fingerprint</span>\n                Biometric Enrollment\n            </a>'),
        
        # Attendance
        ('<div class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-3 cursor-pointer transition-colors duration-200 font-medium tracking-tight text-sm scale-95 active:scale-90">\n<span class="material-symbols-outlined mr-3">event_available</span>\n                Attendance\n            </div>',
         '<a href="/attendance" class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-3 cursor-pointer transition-colors duration-200 font-medium tracking-tight text-sm scale-95 active:scale-90">\n<span class="material-symbols-outlined mr-3">event_available</span>\n                Attendance\n            </a>'),
        
        # Reports
        ('<div class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-3 cursor-pointer transition-colors duration-200 font-medium tracking-tight text-sm scale-95 active:scale-90">\n<span class="material-symbols-outlined mr-3">analytics</span>\n                Reports\n            </div>',
         '<a href="/reports" class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-3 cursor-pointer transition-colors duration-200 font-medium tracking-tight text-sm scale-95 active:scale-90">\n<span class="material-symbols-outlined mr-3">analytics</span>\n                Reports\n            </a>')
    ]
    
    original_content = content
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed biometric enrollment navigation")
        return True
    else:
        print("ℹ️  No changes needed")
        return False

def main():
    """Main function"""
    print("Fixing Biometric Enrollment Navigation")
    print("=" * 40)
    
    if fix_biometric_navigation():
        print("\n✅ Navigation fixed successfully!")
        print("\nNavigation routes:")
        print("  Dashboard → /dashboard")
        print("  Employee Registration → /registration")
        print("  Biometric Enrollment → /enrollment")
        print("  Attendance → /attendance")
        print("  Reports → /reports")
    else:
        print("\n❌ No changes made")
    
    print("\nTest by running: python app_simple.py")

if __name__ == '__main__':
    main()