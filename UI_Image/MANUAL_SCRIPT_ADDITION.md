# Manual Script Tag Addition Instructions

## Automated Method (Recommended)

Run the Python script to automatically add all script tags:

```bash
cd UI_Image
python add_scripts.py
```

This will add the required script tags to all HTML files.

---

## Manual Method

If you prefer to add the script tags manually, follow these instructions:

### 1. Operations Dashboard

**File**: `operations_dashboard/code.html`

**Find**: `</body></html>` at the end of the file

**Replace with**:
```html
<!-- API Integration Scripts -->
<script src="../js/api-client.js"></script>
<script src="../js/router.js"></script>
<script src="../js/utils.js"></script>
<script src="dashboard.js"></script>
</body></html>
```

---

### 2. Employee Registration

**File**: `employee_registration_updated/code.html`

**Find**: `</body></html>` at the end of the file

**Replace with**:
```html
<!-- API Integration Scripts -->
<script src="../js/api-client.js"></script>
<script src="../js/router.js"></script>
<script src="../js/utils.js"></script>
<script src="registration.js"></script>
</body></html>
```

---

### 3. Biometric Enrollment

**File**: `biometric_enrollment_expanded/code.html`

**Find**: `</body></html>` at the end of the file

**Replace with**:
```html
<!-- API Integration Scripts -->
<script src="../js/api-client.js"></script>
<script src="../js/router.js"></script>
<script src="../js/utils.js"></script>
<script src="enrollment.js"></script>
</body></html>
```

---

### 4. Live Attendance

**File**: `live_attendance/code.html`

**Find**: The line before `</body></html>` (usually after a comment about FAB)

**Add before `</body>`**:
```html
<!-- API Integration Scripts -->
<script src="../js/api-client.js"></script>
<script src="../js/router.js"></script>
<script src="../js/utils.js"></script>
<script src="attendance.js"></script>
```

---

### 5. Attendance Reports

**File**: `attendance_reports_simplified/code.html`

**Find**: `</body></html>` at the end of the file

**Replace with**:
```html
<!-- API Integration Scripts -->
<script src="../js/api-client.js"></script>
<script src="../js/router.js"></script>
<script src="../js/utils.js"></script>
<script src="reports.js"></script>
</body></html>
```

---

## Verification

After adding the script tags, verify by:

1. Opening the HTML file in a text editor
2. Scrolling to the bottom
3. Confirming you see the 4 script tags before `</body>`

## Testing

After adding script tags to all files:

1. Start backend:
```bash
cd backend
python app_simple.py
```

2. Start frontend server:
```bash
cd UI_Image
python -m http.server 8000
```

3. Open in browser:
```
http://localhost:8000/operations_dashboard/code.html
```

4. Check browser console (F12) for any errors

## Expected Result

When you open any page:
- No JavaScript errors in console
- Navigation works (sidebar links)
- Data loads from backend
- Forms submit successfully

## Troubleshooting

### Scripts not loading
- Check file paths are correct
- Ensure web server is running (not opening file:// directly)
- Check browser console for 404 errors

### CORS errors
- Ensure backend is running on port 5000
- Check backend has CORS enabled
- Use web server (not file:// protocol)

### No data showing
- Check backend is running
- Test API endpoints with curl
- Check browser console for API errors

