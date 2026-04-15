# Manual Navigation Fix Instructions

## Automated Method (Recommended)

Run the Python script to automatically add nav-item class:

```bash
cd UI_Image
python fix_navigation.py
```

---

## Manual Method

If you prefer to add the `nav-item` class manually, follow these instructions for each HTML file.

### What to Change

Find all sidebar navigation `<a>` tags for these menu items:
- Dashboard
- Employee Registration
- Biometric Enrollment
- Attendance
- Reports

Add `nav-item` to the existing class attribute.

---

### 1. Operations Dashboard

**File**: `operations_dashboard/code.html`

**Find lines like**:
```html
<a class="bg-[#0058be] text-white rounded-md mx-2 flex items-center px-4 py-3..." href="#">
    <span class="material-symbols-outlined mr-3">dashboard</span>
    Dashboard
</a>
```

**Change to**:
```html
<a class="nav-item bg-[#0058be] text-white rounded-md mx-2 flex items-center px-4 py-3..." href="#">
    <span class="material-symbols-outlined mr-3">dashboard</span>
    Dashboard
</a>
```

**Apply to all 5 navigation items** (Dashboard, Employee Registration, Biometric Enrollment, Attendance, Reports)

---

### 2. Employee Registration

**File**: `employee_registration_updated/code.html`

**Find lines like**:
```html
<a class="flex items-center px-4 py-3 text-slate-400 hover:text-white..." href="#">
    <span class="material-symbols-outlined mr-3">dashboard</span>
    Dashboard
</a>
```

**Change to**:
```html
<a class="nav-item flex items-center px-4 py-3 text-slate-400 hover:text-white..." href="#">
    <span class="material-symbols-outlined mr-3">dashboard</span>
    Dashboard
</a>
```

**Apply to all 5 navigation items**

---

### 3. Biometric Enrollment

**File**: `biometric_enrollment_expanded/code.html`

Same pattern as above - add `nav-item` to the class attribute of all 5 navigation `<a>` tags.

---

### 4. Live Attendance

**File**: `live_attendance/code.html`

Same pattern as above - add `nav-item` to the class attribute of all 5 navigation `<a>` tags.

---

### 5. Attendance Reports

**File**: `attendance_reports_simplified/code.html`

Same pattern as above - add `nav-item` to the class attribute of all 5 navigation `<a>` tags.

---

## Example: Before and After

### Before:
```html
<a class="text-slate-400 hover:text-white mx-2 flex items-center px-4 py-3" href="#">
    <span class="material-symbols-outlined mr-3">dashboard</span>
    Dashboard
</a>
```

### After:
```html
<a class="nav-item text-slate-400 hover:text-white mx-2 flex items-center px-4 py-3" href="#">
    <span class="material-symbols-outlined mr-3">dashboard</span>
    Dashboard
</a>
```

**Key Change**: Added `nav-item` at the beginning of the class attribute.

---

## Important Notes

1. **Only add to navigation items** - Don't add to Settings or Support links
2. **Add to class attribute** - Just add `nav-item` to the existing classes
3. **Don't change anything else** - Keep all other classes and structure the same
4. **All 5 files** - Must update all HTML files for consistent navigation

---

## Verification

After making changes:

1. Open any HTML file in a text editor
2. Search for "Dashboard" in the sidebar
3. Confirm the `<a>` tag has `class="nav-item ..."`
4. Repeat for all 5 navigation items

---

## Testing

1. Start backend and frontend servers
2. Open any page in browser
3. Click sidebar navigation items
4. Should navigate to different pages
5. Check browser console (F12) for errors

---

## Troubleshooting

### Navigation still not working
- Check browser console for JavaScript errors
- Verify `nav-item` class is added to all 5 items in all 5 files
- Ensure router.js is loaded (check Network tab in DevTools)
- Clear browser cache and refresh

### Class not being added
- Make sure you're editing the correct `<a>` tags (in sidebar navigation)
- Don't add to Settings or Support links
- Keep existing classes, just add `nav-item` at the beginning

### Styling changed
- If styling looks different, you may have accidentally modified other classes
- Revert and try again, only adding `nav-item` to the class attribute

