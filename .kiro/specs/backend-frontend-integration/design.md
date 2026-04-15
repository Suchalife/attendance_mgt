# Design Document: Backend-Frontend Integration

## Overview

This design document specifies the architecture and implementation strategy for integrating the Python-based face recognition backend with the HTML/CSS/JS frontend modules for the Employee Face Recognition Attendance System. The integration creates a unified web application enabling industrial recycling operations to manage employee registration, biometric enrollment, live attendance tracking, and reporting through a seamless user interface.

### System Context

The system consists of:
- **Backend**: Flask-based Python application with OpenCV, MTCNN face detection, and DeepFace Facenet512 embeddings
- **Frontend**: Five HTML/CSS/JS modules with Tailwind CSS styling
- **Database**: MongoDB storing employee records and attendance data
- **Integration Layer**: RESTful API with real-time communication capabilities

### Design Goals

1. **Seamless Integration**: Connect existing backend services with frontend UI modules without major refactoring
2. **Real-Time Experience**: Provide live camera feeds and instant recognition feedback
3. **Non-Blocking Operations**: Ensure camera operations don't freeze the UI
4. **Maintainability**: Keep clear separation between frontend, API, and backend logic
5. **Scalability**: Support multiple concurrent users and camera sessions

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (Client)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboard   │  │ Registration │  │  Enrollment  │          │
│  │    Module    │  │    Module    │  │    Module    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  Attendance  │  │   Reports    │                            │
│  │    Module    │  │    Module    │                            │
│  └──────────────┘  └──────────────┘                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Client-Side Router (Vanilla JS)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Flask API Layer (Python)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    RESTful Endpoints                      │  │
│  │  /api/employees  /api/enrollment  /api/attendance        │  │
│  │  /api/reports    /api/camera                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              WebSocket/SSE Handler                        │  │
│  │  (Real-time recognition events, camera frames)            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Services (Python)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Employee   │  │  Attendance  │  │   Camera     │          │
│  │  Management  │  │   Service    │  │   Service    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │     Face     │  │   Report     │                            │
│  │ Recognition  │  │  Generator   │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MongoDB Database                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  employees   │  │  attendance  │  │    auth      │          │
│  │ collection   │  │   _records   │  │ collections  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User Action → Frontend Module → Client Router → API Request → 
Flask Endpoint → Backend Service → MongoDB → Response → 
Frontend Update → UI Render
```

## Components and Interfaces

### 1. Client-Side Router

**Purpose**: Enable navigation between UI modules without full page reloads

**Implementation**:
- Vanilla JavaScript router using History API
- Route definitions for five modules
- Dynamic content loading
- State preservation across navigation

**Interface**:
```javascript
class Router {
  constructor(routes);
  navigate(path);
  init();
  handlePopState();
}

// Route Configuration
const routes = {
  '/dashboard': { module: 'dashboard', title: 'Operations Dashboard' },
  '/registration': { module: 'registration', title: 'Employee Registration' },
  '/enrollment': { module: 'enrollment', title: 'Biometric Enrollment' },
  '/attendance': { module: 'attendance', title: 'Live Attendance' },
  '/reports': { module: 'reports', title: 'Attendance Reports' }
};
```

**Key Methods**:
- `navigate(path)`: Load module content and update URL
- `loadModule(moduleName)`: Fetch and render module HTML
- `updateActiveNav(path)`: Highlight active sidebar link

### 2. API Client Service

**Purpose**: Centralized HTTP communication with backend

**Implementation**:
```javascript
class APIClient {
  constructor(baseURL);
  
  // Employee Management
  async registerEmployee(employeeData);
  async getEmployees(filters);
  async getEmployeeCount();
  
  // Biometric Enrollment
  async captureImages(employeeId, imageData);
  async trainModel(employeeId);
  async getEnrollmentStatus(employeeId);
  
  // Attendance
  async startAttendanceSession(sessionConfig);
  async markAttendance(sessionId, imageData);
  async endAttendanceSession(sessionId);
  async getAttendanceRecords(filters);
  
  // Reports
  async getAttendanceReport(filters);
  async exportCSV(filters);
  
  // Camera
  async getCameraStream();
  async stopCamera();
  
  // Utility
  async handleResponse(response);
  async handleError(error);
}
```

### 3. Camera Service

**Purpose**: Manage camera feed streaming and frame capture

**Backend Implementation** (Python):
```python
class CameraService:
    def __init__(self):
        self.camera = None
        self.is_streaming = False
        self.frame_queue = queue.Queue(maxsize=10)
    
    def start_camera(self, camera_id=0):
        """Initialize OpenCV VideoCapture"""
        self.camera = cv2.VideoCapture(camera_id)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.is_streaming = True
    
    def get_frame(self):
        """Capture single frame"""
        ret, frame = self.camera.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            return buffer.tobytes()
        return None
    
    def generate_frames(self):
        """Generator for MJPEG streaming"""
        while self.is_streaming:
            frame_bytes = self.get_frame()
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    def stop_camera(self):
        """Release camera resources"""
        self.is_streaming = False
        if self.camera:
            self.camera.release()
            self.camera = None
```

**Frontend Implementation** (JavaScript):
```javascript
class CameraManager {
  constructor(videoElement);
  
  async startStream(streamURL);
  stopStream();
  captureFrame();
  displayFrame(frameData);
  
  // Event handlers
  onFrameReceived(callback);
  onError(callback);
}
```

**Streaming Strategy**: MJPEG over HTTP
- Simple implementation
- Wide browser support
- Acceptable latency for attendance use case
- Fallback to base64 image polling if needed

### 4. Real-Time Communication Service

**Purpose**: Push recognition events and updates to frontend

**Implementation Options**:

**Option A: Server-Sent Events (SSE)** - Recommended
```python
@app.route('/api/attendance/events/<session_id>')
def attendance_events(session_id):
    def event_stream():
        while session_active(session_id):
            event_data = get_latest_recognition(session_id)
            if event_data:
                yield f"data: {json.dumps(event_data)}\n\n"
            time.sleep(0.5)
    
    return Response(event_stream(), mimetype='text/event-stream')
```

```javascript
// Frontend
const eventSource = new EventSource(`/api/attendance/events/${sessionId}`);
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateAttendanceUI(data);
};
```

**Option B: WebSocket** - Alternative
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('start_recognition')
def handle_recognition(data):
    session_id = data['session_id']
    # Process recognition
    emit('recognition_result', result_data, room=session_id)
```

**Decision**: Use SSE for simplicity and unidirectional data flow (server → client)

### 5. State Management

**Purpose**: Manage application state across modules

**Implementation**:
```javascript
class StateManager {
  constructor() {
    this.state = {
      currentUser: null,
      activeSession: null,
      attendanceStats: {},
      cameraActive: false
    };
    this.listeners = [];
  }
  
  setState(updates) {
    this.state = { ...this.state, ...updates };
    this.notifyListeners();
  }
  
  getState() {
    return { ...this.state };
  }
  
  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }
  
  notifyListeners() {
    this.listeners.forEach(listener => listener(this.state));
  }
}
```

## Data Models

### API Request/Response Models

#### Employee Registration

**Request**:
```json
{
  "employeeId": "EMP-2024-001",
  "employeeName": "John Doe",
  "department": "Sorting",
  "shift": "Day",
  "email": "john.doe@company.com",
  "phoneNumber": "+1-555-0100",
  "images": ["base64_image_1", "base64_image_2", "...", "base64_image_5"]
}
```

**Response**:
```json
{
  "success": true,
  "employeeId": "EMP-2024-001",
  "record_id": "507f1f77bcf86cd799439011",
  "message": "Employee registered successfully"
}
```

#### Biometric Enrollment

**Capture Request**:
```json
{
  "employeeId": "EMP-2024-001",
  "image": "base64_encoded_image_data"
}
```

**Capture Response**:
```json
{
  "success": true,
  "captureCount": 15,
  "totalRequired": 50,
  "faceDetected": true,
  "quality": "good"
}
```

**Train Request**:
```json
{
  "employeeId": "EMP-2024-001"
}
```

**Train Response**:
```json
{
  "success": true,
  "embeddingsGenerated": 50,
  "trainingTime": 12.5,
  "message": "Model trained successfully"
}
```

#### Attendance Session

**Start Session Request**:
```json
{
  "date": "2024-01-15",
  "department": "Sorting",
  "shift": "Day"
}
```

**Start Session Response**:
```json
{
  "success": true,
  "session_id": "507f1f77bcf86cd799439011",
  "employees_count": 45,
  "streamURL": "/api/camera/stream/507f1f77bcf86cd799439011"
}
```

**Recognition Event** (SSE):
```json
{
  "type": "recognition",
  "timestamp": 1705334400,
  "employee": {
    "employee_id": "EMP-2024-001",
    "employee_name": "John Doe",
    "department": "Sorting"
  },
  "confidence": 95.8,
  "status": "marked_present",
  "already_marked": false
}
```

#### Attendance Reports

**Request**:
```json
{
  "startDate": "2024-01-01",
  "endDate": "2024-01-31",
  "department": "Sorting",
  "employeeId": null
}
```

**Response**:
```json
{
  "success": true,
  "records": [
    {
      "employeeId": "EMP-2024-001",
      "employeeName": "John Doe",
      "department": "Sorting",
      "daysPresent": 22,
      "daysAbsent": 2,
      "attendancePercentage": 91.7,
      "records": [
        {
          "date": "2024-01-15",
          "status": "present",
          "checkIn": "08:05:23",
          "checkOut": "17:02:15"
        }
      ]
    }
  ],
  "summary": {
    "totalEmployees": 45,
    "averageAttendance": 89.3
  }
}
```

### Database Schema Extensions

#### Attendance Records Collection

```javascript
{
  "_id": ObjectId,
  "session_id": String,
  "date": ISODate,
  "department": String,
  "shift": String,
  "created_at": ISODate,
  "ended_at": ISODate,
  "finalized": Boolean,
  "employees": [
    {
      "employee_id": String,
      "employee_name": String,
      "department": String,
      "shift": String,
      "present": Boolean,
      "marked_at": ISODate,
      "confidence": Number
    }
  ]
}
```

#### Camera Sessions Collection

```javascript
{
  "_id": ObjectId,
  "session_id": String,
  "camera_id": Number,
  "started_at": ISODate,
  "stopped_at": ISODate,
  "status": String, // "active", "stopped", "error"
  "frame_count": Number,
  "recognition_count": Number
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Before defining correctness properties, I need to analyze the acceptance criteria to determine which are suitable for property-based testing.


### Property Reflection

After analyzing all acceptance criteria, I've identified the following properties that are suitable for property-based testing. Let me review for redundancy:

**Data Display Properties (1.2, 1.3, 1.4)**:
- 1.2 tests employee count display matches database
- 1.3 tests present count display matches database
- 1.4 tests absent count calculation
These are distinct properties testing different data points, no redundancy.

**Data Filtering Properties (5.5, 5.7)**:
- 5.5 tests department filtering
- 5.7 tests date range filtering
These test different filter types, no redundancy.

**Validation Properties (2.2, 2.6)**:
- 2.2 tests validation failure for missing fields
- 2.6 tests error response format for failures
These are related but distinct - one tests validation logic, the other tests error response format. Keep both.

**Storage Properties (2.3, 3.10)**:
- 2.3 tests employee data storage and retrieval
- 3.10 tests embedding storage and linking
These test different types of data storage, no redundancy.

**Recognition Properties (4.6, 4.8)**:
- 4.6 tests recognized face response
- 4.8 tests unknown face response
These are complementary (success vs failure cases), no redundancy.

**API Properties (8.2-8.9, 8.10)**:
- 8.2-8.9 test endpoint existence
- 8.10 tests response format
These can be combined into a single property about API endpoint behavior.

**Conclusion**: Most properties are distinct. I'll combine the endpoint properties (8.2-8.9) into a single comprehensive property.

### Property 1: Data Display Consistency

*For any* database state, the displayed employee count in the dashboard SHALL equal the actual count of employees in the Employee_Database.

**Validates: Requirements 1.2**

### Property 2: Present Count Accuracy

*For any* set of attendance records for the current date, the displayed "Present Today" count SHALL equal the count of employees marked as present in the Attendance_Records.

**Validates: Requirements 1.3**

### Property 3: Absent Count Calculation

*For any* total employee count and present employee count, the displayed "Absent Today" count SHALL equal the total employee count minus the present employee count.

**Validates: Requirements 1.4**

### Property 4: Recent Activity Ordering

*For any* set of attendance records, the displayed activity feed SHALL contain exactly the 10 most recent records ordered by timestamp in descending order.

**Validates: Requirements 1.6**

### Property 5: Trend Chart Date Filtering

*For any* set of attendance records with timestamps, the attendance trend chart data SHALL only include records with dates within the last 7 days from the current date.

**Validates: Requirements 1.7**

### Property 6: Required Field Validation

*For any* employee registration data missing one or more required fields (employeeId, employeeName, department), the validation SHALL fail and return an error response.

**Validates: Requirements 2.2**

### Property 7: Storage Persistence

*For any* valid employee data, after successful storage in the Employee_Database, querying the database with the employeeId SHALL return the same employee data.

**Validates: Requirements 2.3**

### Property 8: Success Response Format

*For any* successful storage operation, the API response SHALL have success=true and include the employeeId and record_id.

**Validates: Requirements 2.4**

### Property 9: Error Response Format

*For any* storage operation that fails, the API response SHALL have success=false and include descriptive error details.

**Validates: Requirements 2.6**

### Property 10: Image Capture Count

*For any* biometric enrollment capture operation, the total number of captured face images SHALL equal exactly 50 when the capture process completes.

**Validates: Requirements 3.5**

### Property 11: Embedding Storage and Linking

*For any* employee and generated face embeddings, after storage, querying the employee record from Employee_Database SHALL return the employee data with the embeddings linked to that employee.

**Validates: Requirements 3.10**

### Property 12: Face Detection Execution

*For any* video frame containing at least one face, the face detection system SHALL detect the face and return detection results with bounding box coordinates.

**Validates: Requirements 4.5**

### Property 13: Recognition Result Completeness

*For any* successfully recognized face, the recognition response SHALL contain all required employee details: employee_id, employee_name, department, and timestamp.

**Validates: Requirements 4.6**

### Property 14: Unknown Face Handling

*For any* face that does not match any employee in the Employee_Database (distance above threshold), the system SHALL return an unknown alert response.

**Validates: Requirements 4.8**

### Property 15: Attendance Record Creation

*For any* recognized employee during an active attendance session, an attendance record SHALL be created in the Attendance_Records collection with the employee_id and recognition timestamp.

**Validates: Requirements 4.10**

### Property 16: Attendance Percentage Calculation

*For any* employee with attendance records over a period, the calculated attendance percentage SHALL equal (days_present / total_working_days) * 100, rounded to one decimal place.

**Validates: Requirements 5.2**

### Property 17: Department Filter Accuracy

*For any* department filter value, all returned attendance records SHALL have the department field matching the filter value.

**Validates: Requirements 5.5**

### Property 18: Date Range Filter Accuracy

*For any* date range filter (startDate, endDate), all returned attendance records SHALL have date values within the range [startDate, endDate] inclusive.

**Validates: Requirements 5.7**

### Property 19: CSV Generation Completeness

*For any* set of attendance records, the generated CSV file SHALL contain all records with all required columns (employeeId, employeeName, department, date, status) in valid CSV format.

**Validates: Requirements 5.9**

### Property 20: Route Navigation Correctness

*For any* of the five defined routes (/dashboard, /registration, /enrollment, /attendance, /reports), navigating to that route SHALL load the corresponding module content.

**Validates: Requirements 6.4**

### Property 21: UI Consistency Across Routes

*For any* route navigation, the sidebar and header elements SHALL remain visible and maintain consistent structure and styling.

**Validates: Requirements 6.5**

### Property 22: Frame Encoding Validity

*For any* captured camera frame, the encoded output SHALL be valid JPEG format or valid base64-encoded image data.

**Validates: Requirements 7.2**

### Property 23: Resource Cleanup on Camera Stop

*For any* camera stop operation, after execution, the VideoCapture resources SHALL be released and subsequent camera access attempts SHALL fail until reinitialized.

**Validates: Requirements 7.6**

### Property 24: API Endpoint Availability

*For any* defined API endpoint in the specification (POST /api/employees, GET /api/employees, POST /api/enrollment/capture, POST /api/enrollment/train, POST /api/attendance/start, GET /api/attendance/stream, GET /api/attendance/records, GET /api/reports/attendance), making a request to that endpoint SHALL return a response with status code other than 404.

**Validates: Requirements 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9**

### Property 25: JSON Response Format

*For any* API request to any endpoint, the response SHALL be valid JSON format with an appropriate HTTP status code (200 for success, 400 for client errors, 500 for server errors).

**Validates: Requirements 8.10**

### Property 26: Real-Time Event Delivery

*For any* recognition event during an active attendance session, the event SHALL be pushed to the Frontend_UI through the real-time communication channel (SSE or WebSocket).

**Validates: Requirements 9.2**

### Property 27: Error Response Descriptiveness

*For any* error condition encountered by the Backend_System, the API response SHALL have success=false and include a descriptive error message explaining the error.

**Validates: Requirements 10.1**

## Error Handling

### Error Categories

#### 1. Camera Errors

**Scenarios**:
- Camera not accessible (hardware not found)
- Camera already in use by another process
- Camera initialization timeout
- Frame capture failure

**Handling Strategy**:
```python
class CameraError(Exception):
    pass

def initialize_camera(camera_id=0, timeout=5):
    try:
        camera = cv2.VideoCapture(camera_id)
        if not camera.isOpened():
            raise CameraError("Camera not accessible. Please check hardware connection.")
        
        # Test frame capture
        ret, frame = camera.read()
        if not ret:
            raise CameraError("Failed to capture frame from camera.")
        
        return camera
    except Exception as e:
        logger.error(f"Camera initialization failed: {e}")
        raise CameraError(f"Camera initialization failed: {str(e)}")
```

**API Response**:
```json
{
  "success": false,
  "error": "Camera not accessible. Please check hardware connection.",
  "error_code": "CAMERA_NOT_ACCESSIBLE",
  "troubleshooting": [
    "Ensure camera is connected",
    "Check if another application is using the camera",
    "Verify camera permissions"
  ]
}
```

#### 2. Face Detection Errors

**Scenarios**:
- No face detected in frame
- Multiple faces detected (when single face required)
- Face too small or low quality
- Face partially occluded

**Handling Strategy**:
```python
def detect_and_validate_face(frame, require_single=True):
    faces = detector.detect_faces(frame)
    
    if len(faces) == 0:
        raise FaceDetectionError(
            "No face detected. Please position your face in the camera view.",
            error_code="NO_FACE_DETECTED"
        )
    
    if require_single and len(faces) > 1:
        raise FaceDetectionError(
            f"{len(faces)} faces detected. Please ensure only one person is in view.",
            error_code="MULTIPLE_FACES_DETECTED"
        )
    
    face = faces[0]
    if face['confidence'] < 0.85:
        raise FaceDetectionError(
            "Face detection confidence too low. Please improve lighting.",
            error_code="LOW_CONFIDENCE"
        )
    
    return face
```

**API Response**:
```json
{
  "success": false,
  "error": "No face detected. Please position your face in the camera view.",
  "error_code": "NO_FACE_DETECTED",
  "guidance": [
    "Move closer to the camera",
    "Ensure adequate lighting",
    "Face the camera directly"
  ]
}
```

#### 3. Recognition Errors

**Scenarios**:
- Embedding extraction failure
- No matching employee found
- Database query failure
- Model not initialized

**Handling Strategy**:
```python
def recognize_face(face_image):
    # Check model status
    if not model_manager.is_ready():
        raise RecognitionError(
            "Face recognition models not initialized.",
            error_code="MODELS_NOT_READY"
        )
    
    # Extract embedding
    try:
        embedding = extract_embedding(face_image)
        if embedding is None:
            raise RecognitionError(
                "Failed to extract face features. Please try again.",
                error_code="EMBEDDING_EXTRACTION_FAILED"
            )
    except Exception as e:
        logger.error(f"Embedding extraction error: {e}")
        raise RecognitionError(
            "Face feature extraction failed.",
            error_code="EMBEDDING_ERROR"
        )
    
    # Search database
    try:
        best_match, distance = find_best_match(embedding)
        if distance > threshold:
            return {
                "recognized": False,
                "message": "Face not recognized. Please register first."
            }
        return {
            "recognized": True,
            "employee": best_match
        }
    except Exception as e:
        logger.error(f"Database search error: {e}")
        raise RecognitionError(
            "Database search failed.",
            error_code="DATABASE_ERROR"
        )
```

#### 4. Validation Errors

**Scenarios**:
- Missing required fields
- Invalid data format
- Duplicate employee ID
- Invalid department/shift values

**Handling Strategy**:
```python
def validate_employee_data(data):
    errors = []
    
    required_fields = ['employeeId', 'employeeName', 'department', 'email', 'phoneNumber']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"{field} is required")
    
    if data.get('department') not in DEPARTMENTS:
        errors.append(f"Invalid department. Must be one of: {', '.join(DEPARTMENTS)}")
    
    # Check for duplicates
    if employees_col.find_one({'employeeId': data.get('employeeId')}):
        errors.append("Employee ID already exists")
    
    if employees_col.find_one({'email': data.get('email')}):
        errors.append("Email already registered")
    
    if errors:
        raise ValidationError(errors)
    
    return True
```

**API Response**:
```json
{
  "success": false,
  "error": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "validation_errors": [
    "employeeName is required",
    "Invalid department. Must be one of: Sorting, Shredding, Processing, Packaging, Logistics, Quality Control, Administration"
  ]
}
```

#### 5. Network Errors

**Frontend Handling**:
```javascript
class APIClient {
  async handleRequest(url, options) {
    try {
      const response = await fetch(url, {
        ...options,
        timeout: 30000 // 30 second timeout
      });
      
      if (!response.ok) {
        throw new APIError(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      if (error.name === 'TypeError' || error.name === 'NetworkError') {
        throw new NetworkError(
          "Connection lost. Please check your network connection.",
          { retryable: true }
        );
      }
      if (error.name === 'AbortError') {
        throw new NetworkError(
          "Request timeout. Please try again.",
          { retryable: true }
        );
      }
      throw error;
    }
  }
}
```

### Error Recovery Strategies

#### Automatic Retry
- Network errors: Retry up to 3 times with exponential backoff
- Camera frame capture: Retry immediately up to 5 times
- Database queries: Retry once after 1 second delay

#### User-Initiated Retry
- Face detection failures: Provide "Try Again" button
- Recognition failures: Provide "Retry Recognition" button
- Form submission failures: Provide "Resubmit" button

#### Graceful Degradation
- If real-time updates fail, fall back to polling every 5 seconds
- If camera streaming fails, fall back to snapshot mode (capture on demand)
- If CSV export fails, provide JSON download as alternative

## Testing Strategy

### Testing Approach

This feature requires a **dual testing approach** combining property-based tests for universal properties and integration tests for infrastructure and UI behavior.

#### Property-Based Testing

**Applicability**: This feature has significant portions suitable for property-based testing, particularly:
- Data transformation and filtering logic
- Calculation and validation logic
- API response format consistency
- Data persistence and retrieval

**Not Suitable for PBT**:
- UI rendering and interaction (use integration tests)
- Camera hardware initialization (use integration tests)
- Network streaming infrastructure (use integration tests)
- Real-time communication setup (use integration tests)

**Property Test Configuration**:
- Library: `hypothesis` for Python backend tests
- Minimum iterations: 100 per property test
- Each test must reference its design property using the tag format

**Example Property Test**:
```python
from hypothesis import given, strategies as st
import pytest

# Feature: backend-frontend-integration, Property 16: Attendance Percentage Calculation
@given(
    days_present=st.integers(min_value=0, max_value=30),
    total_days=st.integers(min_value=1, max_value=30)
)
def test_attendance_percentage_calculation(days_present, total_days):
    """
    For any employee with attendance records over a period, 
    the calculated attendance percentage should equal 
    (days_present / total_working_days) * 100, rounded to one decimal place.
    """
    # Ensure days_present doesn't exceed total_days
    days_present = min(days_present, total_days)
    
    expected_percentage = round((days_present / total_days) * 100, 1)
    actual_percentage = calculate_attendance_percentage(days_present, total_days)
    
    assert actual_percentage == expected_percentage
    assert 0 <= actual_percentage <= 100
```

#### Integration Testing

**Scope**: Integration tests verify:
- Frontend-to-API communication
- API-to-backend service integration
- Backend-to-database operations
- Camera hardware interaction
- Real-time communication channels
- UI rendering and user interactions

**Test Categories**:

1. **API Integration Tests**
   - Test each API endpoint with valid and invalid inputs
   - Verify request/response formats
   - Test error handling and status codes
   - Test CORS configuration

2. **Camera Integration Tests**
   - Test camera initialization and release
   - Test frame capture and encoding
   - Test streaming functionality
   - Test concurrent camera access handling

3. **Recognition Pipeline Tests**
   - Test end-to-end recognition flow
   - Test face detection with various image qualities
   - Test embedding extraction and matching
   - Test duplicate prevention logic

4. **UI Integration Tests**
   - Test navigation between modules
   - Test form submissions and validations
   - Test real-time UI updates
   - Test error message displays

**Example Integration Test**:
```python
def test_employee_registration_integration(client, db):
    """Integration test for employee registration flow"""
    employee_data = {
        "employeeId": "EMP-TEST-001",
        "employeeName": "Test Employee",
        "department": "Sorting",
        "shift": "Day",
        "email": "test@example.com",
        "phoneNumber": "+1-555-0100",
        "images": [generate_test_face_image() for _ in range(5)]
    }
    
    response = client.post('/api/register-employee', json=employee_data)
    
    assert response.status_code == 200
    assert response.json['success'] == True
    assert 'employeeId' in response.json
    
    # Verify database storage
    employee = db.employees.find_one({'employeeId': 'EMP-TEST-001'})
    assert employee is not None
    assert employee['employeeName'] == 'Test Employee'
    assert len(employee['embeddings']) == 5
```

#### Unit Testing

**Scope**: Unit tests for individual functions and utilities:
- Data validation functions
- Calculation functions
- Encoding/decoding functions
- Utility functions

**Example Unit Test**:
```python
def test_validate_required_fields():
    """Unit test for field validation"""
    valid_data = {
        'employeeId': 'EMP-001',
        'employeeName': 'John Doe',
        'department': 'Sorting',
        'email': 'john@example.com',
        'phoneNumber': '+1-555-0100'
    }
    
    assert validate_employee_data(valid_data) == True
    
    invalid_data = {
        'employeeId': 'EMP-001',
        # missing employeeName
        'department': 'Sorting'
    }
    
    with pytest.raises(ValidationError) as exc_info:
        validate_employee_data(invalid_data)
    
    assert 'employeeName is required' in str(exc_info.value)
```

### Test Coverage Goals

- **Property Tests**: Cover all 27 identified properties
- **Integration Tests**: Cover all API endpoints and major user flows
- **Unit Tests**: Cover all utility functions and calculations
- **Overall Code Coverage**: Minimum 80% for backend services

### Testing Tools and Frameworks

**Backend (Python)**:
- `pytest`: Test framework
- `hypothesis`: Property-based testing
- `pytest-flask`: Flask application testing
- `pytest-cov`: Coverage reporting
- `mongomock`: MongoDB mocking for tests

**Frontend (JavaScript)**:
- `Jest`: Test framework
- `@testing-library/dom`: DOM testing utilities
- `MSW` (Mock Service Worker): API mocking
- `fast-check`: Property-based testing for JavaScript

### Continuous Integration

**Test Execution Strategy**:
1. Run unit tests on every commit
2. Run property tests (100 iterations) on every pull request
3. Run integration tests on pull request and before deployment
4. Generate coverage reports and enforce minimum thresholds

**CI Pipeline**:
```yaml
test:
  stages:
    - unit-tests
    - property-tests
    - integration-tests
  
  unit-tests:
    script:
      - pytest tests/unit --cov=backend --cov-report=xml
    coverage: 80%
  
  property-tests:
    script:
      - pytest tests/properties -v --hypothesis-show-statistics
    iterations: 100
  
  integration-tests:
    script:
      - pytest tests/integration -v
    services:
      - mongodb
      - camera-simulator
```

## Implementation Notes

### Technology Stack Decisions

#### Backend Framework: Flask
**Rationale**: 
- Already in use in existing codebase
- Lightweight and flexible
- Good support for streaming responses
- Easy integration with OpenCV and DeepFace

**Alternative Considered**: FastAPI
- Pros: Better async support, automatic API documentation
- Cons: Would require refactoring existing code

#### Real-Time Communication: Server-Sent Events (SSE)
**Rationale**:
- Simpler than WebSocket for unidirectional communication
- Built-in browser support
- Automatic reconnection handling
- Sufficient for attendance updates

**Alternative Considered**: WebSocket
- Pros: Bidirectional communication, lower latency
- Cons: More complex implementation, overkill for this use case

#### Camera Streaming: MJPEG over HTTP
**Rationale**:
- Simple implementation with Flask
- Wide browser compatibility
- Acceptable latency for attendance use case
- Easy to debug

**Alternative Considered**: WebRTC
- Pros: Lower latency, better quality
- Cons: Complex implementation, requires signaling server

#### Client-Side Router: Vanilla JavaScript
**Rationale**:
- No additional dependencies
- Lightweight
- Sufficient for 5 routes
- Maintains consistency with existing frontend

**Alternative Considered**: React Router or Vue Router
- Pros: More features, better state management
- Cons: Would require framework adoption, increased complexity

### Performance Considerations

#### Backend Optimizations

1. **Model Preloading**: Load MTCNN and DeepFace models once at startup using ModelManager singleton
2. **Embedding Caching**: Cache employee embeddings in memory to avoid repeated database queries
3. **Frame Rate Limiting**: Limit camera stream to 15 FPS to reduce bandwidth and processing load
4. **Batch Processing**: Process multiple faces in a single frame concurrently
5. **Connection Pooling**: Use MongoDB connection pooling for efficient database access

#### Frontend Optimizations

1. **Debouncing**: Debounce filter inputs to reduce API calls
2. **Lazy Loading**: Load module content on-demand rather than upfront
3. **Image Compression**: Compress captured images before sending to backend
4. **Virtual Scrolling**: Use virtual scrolling for large attendance lists
5. **Caching**: Cache static data (employee list, departments) in localStorage

### Security Considerations

1. **Authentication**: Implement JWT-based authentication for API endpoints
2. **Authorization**: Role-based access control (manager vs employee)
3. **Input Validation**: Validate and sanitize all user inputs
4. **Rate Limiting**: Implement rate limiting on API endpoints
5. **HTTPS**: Enforce HTTPS for all communications
6. **CORS**: Configure CORS to allow only trusted origins
7. **Data Privacy**: Encrypt face embeddings at rest in database
8. **Session Management**: Implement secure session handling with timeouts

### Deployment Considerations

1. **Camera Access**: Ensure server has access to camera hardware
2. **Resource Requirements**: Minimum 4GB RAM for face recognition models
3. **Concurrent Users**: Support up to 10 concurrent camera sessions
4. **Database Indexing**: Create indexes on employeeId, email, date fields
5. **Logging**: Implement comprehensive logging for debugging and auditing
6. **Monitoring**: Set up monitoring for API response times and error rates
7. **Backup**: Regular backups of MongoDB database

## Conclusion

This design provides a comprehensive architecture for integrating the Python backend with the HTML/CSS/JS frontend, creating a unified Employee Face Recognition Attendance System. The design emphasizes:

- **Seamless Integration**: Clear API layer connecting frontend and backend
- **Real-Time Experience**: SSE for live updates, MJPEG for camera streaming
- **Robust Error Handling**: Comprehensive error handling with user-friendly messages
- **Testability**: Property-based tests for logic, integration tests for infrastructure
- **Maintainability**: Clear separation of concerns, modular architecture
- **Performance**: Optimizations for model loading, caching, and streaming

The implementation will follow this design to ensure all requirements are met while maintaining code quality and system reliability.
