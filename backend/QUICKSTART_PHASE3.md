# Quick Start Guide - Phase 3

## What's New in Phase 3?

✅ **Face Detection** - Detect faces using OpenCV Haar Cascade  
✅ **Attendance Marking** - Automatically mark attendance when face detected  
✅ **Session Management** - Group attendance by session ID  
✅ **Duplicate Prevention** - Prevent marking same employee twice in session  
✅ **Statistics** - Get attendance stats (present, absent, total)  

## Quick Test (5 minutes)

### Step 1: Start Server

```bash
cd backend
python app_simple.py
```

### Step 2: Create Test Employee

```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "employeeId": "EMP001",
    "employeeName": "John Doe",
    "department": "Engineering",
    "shift": "Morning",
    "email": "john@example.com",
    "phoneNumber": "1234567890"
  }'
```

### Step 3: Start Camera

```bash
curl -X POST http://localhost:5000/api/camera/start
```

### Step 4: Mark Attendance (Face Detection)

```bash
curl -X POST http://localhost:5000/api/attendance/start
```

**Expected Response**:
```json
{
  "success": true,
  "session_id": "...",
  "face_detected": true,
  "employee_recognized": true,
  "employee": {
    "employeeId": "EMP001",
    "employeeName": "John Doe",
    "department": "Engineering"
  },
  "attendance": {
    "success": true,
    "message": "Attendance marked for John Doe"
  }
}
```

### Step 5: View Attendance Records

```bash
curl http://localhost:5000/api/attendance
```

### Step 6: Get Statistics

```bash
curl http://localhost:5000/api/attendance/stats
```

## Run Automated Tests

```bash
cd backend
python test_phase3.py
```

This will run 12 automated tests covering all Phase 3 functionality.

## Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/attendance/start` | Detect face & mark attendance |
| GET | `/api/attendance` | Get all attendance records |
| GET | `/api/attendance/stats` | Get attendance statistics |
| POST | `/api/attendance/mark` | Manually mark attendance |

## Important Notes

### Placeholder Recognition

⚠️ **Current Implementation**: The system uses a **placeholder** recognition that assigns the first employee to any detected face.

**Why?**
- Allows testing full attendance flow
- No training data required
- Easy to replace with real recognition later

**How to Replace?**
1. Add face recognition model (LBPH, DeepFace, FaceNet)
2. Update `recognize_employee()` in `recognition_service.py`
3. Add training/enrollment endpoints
4. Store face embeddings or trained models

### Face Detection

✅ **Works**: Frontal faces with good lighting  
❌ **Struggles**: Side profiles, poor lighting, multiple faces  

**Tips for Best Results**:
- Face camera directly
- Ensure good lighting
- Position face in center of frame
- Stay 1-2 feet from camera

## Troubleshooting

### No Face Detected

**Problem**: Response shows `"face_detected": false`

**Solutions**:
1. Check camera is working: `http://localhost:5000/api/camera/stream`
2. Improve lighting
3. Position face in center of frame
4. Move closer to camera

### Camera Not Available

**Problem**: Error "Camera not available"

**Solutions**:
1. Start camera first: `curl -X POST http://localhost:5000/api/camera/start`
2. Check camera is connected
3. Close other apps using camera
4. Restart Flask server

### Duplicate Attendance

**Problem**: "Attendance already marked" error

**Expected Behavior**: System prevents duplicates in same session

**Solution**: This is correct! Use different session ID for new session.

## File Structure

```
backend/
├── services/
│   ├── recognition_service.py    # Face detection
│   ├── attendance_service.py     # Attendance management
│   ├── camera_service.py         # Camera operations
│   └── csv_service.py            # CSV utilities
├── routes/
│   ├── attendance.py             # Attendance endpoints
│   ├── camera.py                 # Camera endpoints
│   └── employees.py              # Employee endpoints
├── data/
│   ├── employees.csv             # Employee records
│   └── attendance.csv            # Attendance records
├── app_simple.py                 # Flask application
├── test_phase3.py                # Automated tests
└── README_PHASE3.md              # Full documentation
```

## Next Steps

After verifying Phase 3 works:

1. ✅ Test face detection
2. ✅ Test attendance marking
3. ✅ Verify duplicate prevention
4. → **Add real face recognition** (replace placeholder)
5. → **Proceed to Phase 4**: Frontend Integration

## Need Help?

- **Full Documentation**: See `README_PHASE3.md`
- **API Details**: See endpoint descriptions in README
- **Testing**: Run `python test_phase3.py`
- **Issues**: Check troubleshooting section

