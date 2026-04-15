# Quick Start - Phase 4 Frontend Integration

## 🚀 Get Started in 3 Steps

### Step 1: Start Backend (Terminal 1)

```bash
cd backend
python app_simple.py
```

✅ Backend running on `http://localhost:5000`

### Step 2: Start Frontend Server (Terminal 2)

```bash
cd UI_Image
python -m http.server 8000
```

✅ Frontend running on `http://localhost:8000`

### Step 3: Add Scripts to HTML Files

Each HTML file needs script tags added before the closing `</body>` tag.

## 📝 Script Tags to Add

### For Operations Dashboard
**File**: `operations_dashboard/code.html`

Add before `</body>`:
```html
<script src="../js/api-client.js"></script>
<script src="../js/router.js"></script>
<script src="../js/utils.js"></script>
<script src="dashboard.js"></script>
```

### For Employee Registration
**File**: `employee_registration_updated/code.html`

Add before `</body>`:
```html
<script src="../js/api-client.js"></script>
<script src="../js/router.js"></script>
<script src="../js/utils.js"></script>
<script src="registration.js"></script>
```

### For Biometric Enrollment
**File**: `biometric_enrollment_expanded/code.html`

Add before `</body>`:
```html
<script src="../js/api-client.js"></script>
<script src="../js/router.js"></script>
<script src="../js/utils.js"></script>
<script src="enrollment.js"></script>
```

### For Live Attendance
**File**: `live_attendance/code.html`

Add before `</body>`:
```html
<script src="../js/api-client.js"></script>
<script src="../js/router.js"></script>
<script src="../js/utils.js"></script>
<script src="attendance.js"></script>
```

### For Attendance Reports
**File**: `attendance_reports_simplified/code.html`

Add before `</body>`:
```html
<script src="../js/api-client.js"></script>
<script src="../js/router.js"></script>
<script src="../js/utils.js"></script>
<script src="reports.js"></script>
```

## 🧪 Test the Integration

### 1. Test Employee Registration

```
http://localhost:8000/employee_registration_updated/code.html
```

1. Fill in the form
2. Click "Save Employee"
3. Check for success notification

### 2. Test Dashboard

```
http://localhost:8000/operations_dashboard/code.html
```

1. Verify employee count updates
2. Check attendance statistics
3. See recent activity feed

### 3. Test Live Attendance

```
http://localhost:8000/live_attendance/code.html
```

1. Click "Start Attendance"
2. Camera feed should appear
3. Face detection runs every 2 seconds
4. Employees appear in list when detected

### 4. Test Reports

```
http://localhost:8000/attendance_reports_simplified/code.html
```

1. View attendance records in table
2. Try filtering by department/date
3. Click export to download CSV

## ✅ What's Working

- ✅ Employee registration form → Backend API
- ✅ Dashboard displays live data
- ✅ Live attendance with face detection
- ✅ Reports with filtering and export
- ✅ Navigation between modules
- ✅ Real-time updates via polling

## ⚠️ Important Notes

### Placeholder Recognition
The system currently uses placeholder recognition (assigns first employee to any detected face). This is intentional for testing.

### Camera Feed
Camera feed URL: `http://localhost:5000/api/camera/stream`

### CORS
Backend has CORS enabled. Must use a web server (not `file://` protocol).

### Polling
- Dashboard: Updates every 3 seconds
- Live Attendance: Checks for faces every 2 seconds

## 🐛 Quick Troubleshooting

### Backend Not Responding
```bash
# Check if backend is running
curl http://localhost:5000/health
```

### Camera Not Working
```bash
# Test camera endpoint
curl -X POST http://localhost:5000/api/camera/start
curl http://localhost:5000/api/camera/status
```

### CORS Errors
- Ensure using web server (not opening HTML directly)
- Check backend is running on port 5000
- Verify `api-client.js` has correct base URL

### No Data Showing
```bash
# Create test employee
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{"employeeId":"EMP001","employeeName":"Test User","department":"Engineering","shift":"Morning","email":"test@example.com","phoneNumber":"1234567890"}'

# Check employees
curl http://localhost:5000/api/employees
```

## 📚 Full Documentation

See `README_PHASE4.md` for complete documentation including:
- Detailed API integration
- All features explained
- Advanced troubleshooting
- Security notes
- Performance tips

## 🎯 Next Steps

1. Add script tags to all HTML files
2. Test each module
3. Test navigation
4. Verify end-to-end flow
5. Proceed to Phase 5: Reports & Filtering

## 📞 Need Help?

- Check browser console for errors
- Verify backend logs
- Test API endpoints with curl
- Read full documentation in `README_PHASE4.md`

