# Phase 2: Camera Streaming (MJPEG)

## Overview

Phase 2 adds camera streaming capability using MJPEG (Motion JPEG) format. This allows live webcam video to be streamed directly to a browser.

## New Files Created

```
backend/
├── services/
│   └── camera_service.py    # Camera operations (start, stop, capture, stream)
└── routes/
    └── camera.py             # Camera API endpoints
```

## Updated Files

- `app_simple.py` - Registered camera routes
- `requirements_simple.txt` - Added opencv-python dependency

## Setup Instructions

### 1. Install New Dependencies

```bash
cd backend
pip install -r requirements_simple.txt
```

This will install:
- `opencv-python` - For camera access and frame processing

### 2. Verify Camera Access

Make sure your webcam is:
- Connected to your computer
- Not being used by another application
- Accessible (check permissions if needed)

### 3. Start Flask Server

```bash
python app_simple.py
```

## API Endpoints

### 1. GET /api/camera/stream
Stream live camera feed using MJPEG

**Usage:**
- Open in browser: `http://localhost:5000/api/camera/stream`
- Embed in HTML: `<img src="http://localhost:5000/api/camera/stream" />`

**Response:**
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
- Continuous stream of JPEG frames

**Features:**
- Automatic camera initialization
- 15 FPS frame rate
- 640x480 resolution
- JPEG quality: 85%
- Auto-restart on frame capture failure

### 2. POST /api/camera/start
Manually start camera

**Response (Success):**
```json
{
  "success": true,
  "message": "Camera started successfully"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Failed to start camera. Please check camera connection."
}
```

### 3. POST /api/camera/stop
Stop camera and release resources

**Response (Success):**
```json
{
  "success": true,
  "message": "Camera stopped successfully"
}
```

### 4. GET /api/camera/status
Check camera status

**Response:**
```json
{
  "success": true,
  "active": true,
  "message": "Camera is active"
}
```

## Testing

### Test 1: Browser Stream Test

1. Start Flask server: `python app_simple.py`
2. Open browser: `http://localhost:5000/api/camera/stream`
3. **Expected Result**: Live webcam feed appears in browser

### Test 2: HTML Embed Test

Create a test HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Camera Stream Test</title>
</head>
<body>
    <h1>Live Camera Feed</h1>
    <img src="http://localhost:5000/api/camera/stream" 
         style="width: 640px; height: 480px; border: 2px solid #333;" />
    
    <div style="margin-top: 20px;">
        <button onclick="startCamera()">Start Camera</button>
        <button onclick="stopCamera()">Stop Camera</button>
        <button onclick="checkStatus()">Check Status</button>
    </div>
    
    <div id="status" style="margin-top: 10px;"></div>
    
    <script>
        async function startCamera() {
            const response = await fetch('http://localhost:5000/api/camera/start', {
                method: 'POST'
            });
            const data = await response.json();
            document.getElementById('status').innerText = JSON.stringify(data, null, 2);
        }
        
        async function stopCamera() {
            const response = await fetch('http://localhost:5000/api/camera/stop', {
                method: 'POST'
            });
            const data = await response.json();
            document.getElementById('status').innerText = JSON.stringify(data, null, 2);
        }
        
        async function checkStatus() {
            const response = await fetch('http://localhost:5000/api/camera/status');
            const data = await response.json();
            document.getElementById('status').innerText = JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
```

Save as `test_camera.html` and open in browser.

### Test 3: cURL Tests

```bash
# Start camera
curl -X POST http://localhost:5000/api/camera/start

# Check status
curl http://localhost:5000/api/camera/status

# Stop camera
curl -X POST http://localhost:5000/api/camera/stop
```

### Test 4: Postman Tests

**Start Camera:**
- Method: POST
- URL: `http://localhost:5000/api/camera/start`

**Check Status:**
- Method: GET
- URL: `http://localhost:5000/api/camera/status`

**Stop Camera:**
- Method: POST
- URL: `http://localhost:5000/api/camera/stop`

## Camera Service Details

### CameraService Class

**Methods:**
- `start_camera(camera_id=0)` - Initialize camera with device ID
- `stop_camera()` - Release camera resources
- `get_frame()` - Capture single JPEG frame
- `generate_frames()` - Generator for MJPEG streaming
- `is_camera_active()` - Check if camera is active

**Features:**
- Singleton pattern (global instance)
- Automatic error recovery
- Frame rate limiting (15 FPS)
- JPEG compression (quality 85%)
- Resource cleanup

### Frame Processing

1. Capture frame using `cv2.VideoCapture.read()`
2. Encode as JPEG using `cv2.imencode('.jpg', frame)`
3. Convert to bytes
4. Wrap in multipart format for MJPEG

### MJPEG Format

Each frame is sent as:
```
--frame\r\n
Content-Type: image/jpeg\r\n\r\n
<JPEG_DATA>
\r\n
```

## Troubleshooting

### Camera Not Found

**Error:** "Failed to open camera 0"

**Solutions:**
1. Check if webcam is connected
2. Try different camera ID: `camera_service.start_camera(1)`
3. Close other applications using the camera
4. Check camera permissions (especially on macOS/Linux)

### Permission Denied (Linux)

```bash
# Add user to video group
sudo usermod -a -G video $USER

# Logout and login again
```

### Permission Denied (macOS)

1. System Preferences → Security & Privacy → Camera
2. Allow Terminal/Python to access camera

### Low Frame Rate

**Causes:**
- CPU overload
- Poor lighting
- Camera hardware limitations

**Solutions:**
- Reduce resolution in `camera_service.py`
- Increase frame delay (reduce FPS)
- Close other applications

### Stream Stops After Few Seconds

**Cause:** Camera resource not properly released

**Solution:**
```bash
# Stop camera before restarting server
curl -X POST http://localhost:5000/api/camera/stop

# Restart Flask server
python app_simple.py
```

## Technical Details

### Camera Settings

```python
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Width: 640px
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Height: 480px
camera.set(cv2.CAP_PROP_FPS, 15)            # Frame rate: 15 FPS
```

### JPEG Encoding

```python
cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
```
- Quality: 85% (balance between size and quality)
- Format: JPEG (widely supported)

### Frame Rate Limiting

```python
time.sleep(0.066)  # ~66ms delay = ~15 FPS
```

## Next Steps

After verifying Phase 2 works:

1. ✅ Test camera stream in browser
2. ✅ Verify start/stop functionality
3. ✅ Test with HTML embed
4. ✅ Check resource cleanup (stop camera properly)
5. → Proceed to Phase 3: Face Recognition Integration

## Notes

- Camera is automatically started when accessing `/api/camera/stream`
- Only one camera instance is active at a time (singleton pattern)
- Camera resources are released when calling `/api/camera/stop`
- Stream continues until client disconnects or camera is stopped
- No threading used (simple implementation)
- No face recognition yet (Phase 3)
