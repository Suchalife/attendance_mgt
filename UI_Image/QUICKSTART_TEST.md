# Quick Start - Test Navigation & Dashboard Fixes

## 🚀 Quick Test (5 minutes)

### Step 1: Start Backend (Terminal 1)
```bash
cd backend
python app_simple.py
```

Wait for: `* Running on http://127.0.0.1:5000`

### Step 2: Add Test Data (Terminal 2)
```bash
# Add 3 test employees
curl -X POST http://localhost:5000/api/employees -H "Content-Type: application/json" -d "{\"EmployeeID\":\"EMP-001\",\"EmployeeName\":\"John Doe\",\"Department\":\"Sorting\",\"Shift\":\"Morning\"}"

curl -X POST http://localhost:5000/api/employees -H "Content-Type: application/json" -d "{\"EmployeeID\":\"EMP-002\",\"EmployeeName\":\"Jane Smith\",\"Department\":\"Logistics\",\"Shift\":\"Evening\"}"

curl -X POST http://localhost:5000/api/employees -H "Content-Type: application/json" -d "{\"EmployeeID\":\"EMP-003\",\"EmployeeName\":\"Bob Johnson\",\"Department\":\"Processing\",\"Shift\":\"Night\"}"

# Verify count
curl http://localhost:5000/api/employees/count
```

Expected: `{"count":3,"success":true}`

### Step 3: Open Dashboard
1. Open `UI_Image/operations_dashboard/code.html` in browser
2. Press F12 to open console

### Step 4: Verify Dashboard
**Expected**:
- ✅ "Total Employees" shows **3** (not 1,284)
- ✅ Console shows: "Dashboard initialized successfully"
- ✅ Console shows: "Dashboard data updated: {count: 3}"

### Step 5: Test Navigation
Click each link in sidebar:
1. **Employee Registration** → Should navigate to registration page
2. **Dashboard** → Should return to dashboard
3. **Biometric Enrollment** → Should navigate to enrollment page
4. **Attendance** → Should navigate to attendance page
5. **Reports** → Should navigate to reports page

**Expected**: Each click navigates to correct page (no page refresh)

---

## ✅ Success Criteria

### Navigation Working
- [x] All 5 navigation links clickable
- [x] Pages switch without refresh
- [x] Active state updates correctly
- [x] No console errors

### Dashboard Working
- [x] Shows real employee count (3)
- [x] Count updates every 3 seconds
- [x] Console shows successful data fetch
- [x] No CORS errors

---

## 🐛 Troubleshooting

### Dashboard Still Shows 1,284
**Fix**: Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

### Navigation Not Working
**Fix**: 
1. Check console for errors
2. Verify router.js loaded: Type `router` in console
3. Clear cache and reload

### CORS Errors
**Fix**: Restart backend server

### Backend Not Starting
**Fix**: 
```bash
cd backend
pip install -r requirements_simple.txt
python app_simple.py
```

---

## 📊 What Changed

### Before
- Navigation: ❌ Clicks do nothing
- Dashboard: ❌ Shows hardcoded 1,284

### After
- Navigation: ✅ Works perfectly
- Dashboard: ✅ Shows real count from backend

---

## 🎯 Next Steps

After verifying fixes work:
1. Continue to Phase 5: Full module integration
2. Connect registration form to backend
3. Implement camera streaming in enrollment
4. Add real-time attendance updates

---

**Need Help?** See `NAVIGATION_AND_DASHBOARD_FIX.md` for detailed documentation.
