# Requirements Document

## Introduction

This document specifies the requirements for integrating a Python backend (OpenCV + face recognition) with HTML/CSS/JS frontend UI modules for an Employee Face Recognition Attendance System. The system enables industrial recycling operations to manage employee registration, biometric enrollment, live attendance tracking, and attendance reporting through a unified web application.

## Glossary

- **Backend_System**: The Python-based server application using Flask/FastAPI that provides face recognition, employee management, and attendance tracking services
- **Frontend_UI**: The collection of five HTML/CSS/JS modules that provide the user interface for system operations
- **Face_Recognition_Engine**: The OpenCV and DeepFace-based subsystem that detects and recognizes employee faces
- **Camera_Feed**: Real-time video stream from webcam captured via OpenCV and displayed in the browser
- **Employee_Database**: MongoDB database storing employee details and face embeddings
- **Attendance_Record**: CSV or database entry containing employee check-in/check-out timestamps
- **API_Layer**: RESTful HTTP interface connecting Frontend_UI to Backend_System
- **Navigation_Router**: Client-side routing mechanism enabling transitions between UI modules
- **KPI_Card**: Dashboard widget displaying key performance indicators (Total Employees, Present Today, Absent Today)
- **Biometric_Enrollment**: Process of capturing face images and training recognition model for an employee
- **Live_Recognition**: Real-time face detection and identification during attendance sessions

## Requirements

### Requirement 1: Operations Dashboard Integration

**User Story:** As a manager, I want to view real-time attendance statistics on the operations dashboard, so that I can monitor workforce presence and make informed decisions.

#### Acceptance Criteria

1. WHEN the operations dashboard loads, THE Frontend_UI SHALL fetch current attendance data from Backend_System via API_Layer
2. THE Frontend_UI SHALL display Total Employees count by querying Employee_Database through API_Layer
3. THE Frontend_UI SHALL display Present Today count by querying today's Attendance_Records through API_Layer
4. THE Frontend_UI SHALL display Absent Today count by calculating Total Employees minus Present Today
5. THE Frontend_UI SHALL update KPI_Cards every 30 seconds without page refresh
6. THE Frontend_UI SHALL display recent activity feed by fetching latest 10 Attendance_Records through API_Layer
7. THE Frontend_UI SHALL render attendance trend chart using data from last 7 days of Attendance_Records

### Requirement 2: Employee Registration Integration

**User Story:** As an HR administrator, I want to register new employees through the web interface, so that their information is stored in the system for biometric enrollment.

#### Acceptance Criteria

1. WHEN the registration form is submitted, THE Frontend_UI SHALL send employee data (ID, name, department, role, branch, phone) to Backend_System via API_Layer
2. THE Backend_System SHALL validate all required fields (EmployeeID, EmployeeName, Department) before storage
3. THE Backend_System SHALL store employee details in Employee_Database
4. WHEN storage succeeds, THE Backend_System SHALL return success status to Frontend_UI
5. THE Frontend_UI SHALL display success message with green notification banner
6. IF storage fails, THEN THE Backend_System SHALL return error details to Frontend_UI
7. THE Frontend_UI SHALL display error message with red notification banner
8. THE Frontend_UI SHALL clear form fields after successful registration

### Requirement 3: Biometric Enrollment Integration

**User Story:** As an HR administrator, I want to capture employee face images and train the recognition model through the web interface, so that employees can be identified during attendance.

#### Acceptance Criteria

1. WHEN biometric enrollment page loads, THE Frontend_UI SHALL fetch list of registered employees from Backend_System via API_Layer
2. WHEN "Capture Images" button is clicked, THE Frontend_UI SHALL request Camera_Feed activation from Backend_System
3. THE Backend_System SHALL initialize Camera_Feed using OpenCV and stream frames to Frontend_UI
4. THE Frontend_UI SHALL display Camera_Feed in designated video element without freezing UI
5. THE Backend_System SHALL capture 50 face images when capture is triggered
6. THE Frontend_UI SHALL display capture progress (e.g., "15/50 images captured") in real-time
7. WHEN "Train Model" button is clicked, THE Frontend_UI SHALL trigger model training via API_Layer
8. THE Backend_System SHALL extract face embeddings and update Face_Recognition_Engine
9. THE Frontend_UI SHALL display training status (loading spinner during training, success message on completion)
10. THE Backend_System SHALL store face embeddings in Employee_Database linked to employee record

### Requirement 4: Live Attendance Integration

**User Story:** As a security officer, I want to start live attendance sessions and see recognized employees in real-time, so that I can monitor who enters the facility.

#### Acceptance Criteria

1. WHEN "Start Attendance" button is clicked, THE Frontend_UI SHALL initiate attendance session via API_Layer
2. THE Backend_System SHALL activate Camera_Feed and Face_Recognition_Engine
3. THE Backend_System SHALL stream Camera_Feed frames to Frontend_UI via WebSocket or HTTP streaming
4. THE Frontend_UI SHALL display Camera_Feed in video element without UI freezing
5. THE Backend_System SHALL perform face detection and recognition on each frame
6. WHEN a face is recognized, THE Backend_System SHALL send employee details (ID, name, department, timestamp) to Frontend_UI
7. THE Frontend_UI SHALL display recognized employee in real-time list with green "Present" badge
8. WHEN an unknown face is detected, THE Backend_System SHALL send unknown alert to Frontend_UI
9. THE Frontend_UI SHALL display unknown person entry with red "Unknown" badge
10. THE Backend_System SHALL record attendance timestamp in Attendance_Record for each recognized employee
11. THE Frontend_UI SHALL update attendance statistics (Shift Coverage, Total Checked-In) in real-time

### Requirement 5: Attendance Reports Integration

**User Story:** As a manager, I want to view and filter attendance reports, so that I can analyze employee attendance patterns and export data.

#### Acceptance Criteria

1. WHEN attendance reports page loads, THE Frontend_UI SHALL fetch attendance data for current month from Backend_System via API_Layer
2. THE Backend_System SHALL read Attendance_Records and calculate attendance percentage for each employee
3. THE Frontend_UI SHALL display employee attendance table with columns: EmployeeID, FullName, Department, DaysPresent, AttendancePercentage
4. WHEN department filter is changed, THE Frontend_UI SHALL request filtered data from Backend_System
5. THE Backend_System SHALL return Attendance_Records matching selected department
6. WHEN date range filter is applied, THE Frontend_UI SHALL request data for specified period from Backend_System
7. THE Backend_System SHALL return Attendance_Records within specified date range
8. WHEN "Export CSV" button is clicked, THE Frontend_UI SHALL request CSV export from Backend_System
9. THE Backend_System SHALL generate CSV file from Attendance_Records and return download link
10. THE Frontend_UI SHALL trigger browser download of CSV file

### Requirement 6: Navigation System

**User Story:** As a system user, I want to navigate between different modules using the sidebar, so that I can access all system features seamlessly.

#### Acceptance Criteria

1. THE Frontend_UI SHALL implement Navigation_Router for client-side routing between modules
2. WHEN a sidebar link is clicked, THE Navigation_Router SHALL load corresponding module without full page reload
3. THE Frontend_UI SHALL highlight active module in sidebar with blue background
4. THE Navigation_Router SHALL support five routes: /dashboard, /registration, /enrollment, /attendance, /reports
5. THE Frontend_UI SHALL maintain consistent sidebar and header across all routes
6. WHEN browser back button is pressed, THE Navigation_Router SHALL navigate to previous module

### Requirement 7: Camera Feed Management

**User Story:** As a system user, I want the camera feed to be embedded in the UI and not freeze the interface, so that I can interact with the system while camera is active.

#### Acceptance Criteria

1. THE Backend_System SHALL capture Camera_Feed frames using OpenCV VideoCapture
2. THE Backend_System SHALL encode frames as JPEG or base64 for transmission to Frontend_UI
3. THE Backend_System SHALL stream frames via HTTP multipart response or WebSocket connection
4. THE Frontend_UI SHALL decode and display frames in HTML video or img element
5. THE Frontend_UI SHALL maintain UI responsiveness during Camera_Feed streaming
6. WHEN camera is stopped, THE Backend_System SHALL release VideoCapture resources
7. THE Frontend_UI SHALL display "Camera Inactive" placeholder when Camera_Feed is not streaming

### Requirement 8: API Layer Implementation

**User Story:** As a developer, I want a RESTful API layer connecting frontend and backend, so that all UI actions trigger real backend functions.

#### Acceptance Criteria

1. THE Backend_System SHALL implement API_Layer using Flask or FastAPI framework
2. THE API_Layer SHALL expose endpoint POST /api/employees for employee registration
3. THE API_Layer SHALL expose endpoint GET /api/employees for fetching employee list
4. THE API_Layer SHALL expose endpoint POST /api/enrollment/capture for face image capture
5. THE API_Layer SHALL expose endpoint POST /api/enrollment/train for model training
6. THE API_Layer SHALL expose endpoint POST /api/attendance/start for starting attendance session
7. THE API_Layer SHALL expose endpoint GET /api/attendance/stream for Camera_Feed streaming
8. THE API_Layer SHALL expose endpoint GET /api/attendance/records for fetching attendance data
9. THE API_Layer SHALL expose endpoint GET /api/reports/attendance for attendance reports with filters
10. THE API_Layer SHALL return JSON responses with status codes (200 for success, 400 for validation errors, 500 for server errors)
11. THE API_Layer SHALL enable CORS to allow Frontend_UI requests from different origin

### Requirement 9: Real-Time Data Updates

**User Story:** As a system user, I want to see real-time updates during attendance sessions, so that I can monitor current activity without manual refresh.

#### Acceptance Criteria

1. THE Backend_System SHALL implement WebSocket connection or Server-Sent Events for real-time communication
2. WHEN an employee is recognized during attendance, THE Backend_System SHALL push recognition event to Frontend_UI immediately
3. THE Frontend_UI SHALL update recognized employee list within 1 second of recognition
4. THE Frontend_UI SHALL update attendance statistics (Present Today, Shift Coverage) within 2 seconds of new attendance record
5. THE Frontend_UI SHALL display real-time capture progress during biometric enrollment
6. WHEN training completes, THE Backend_System SHALL push completion event to Frontend_UI within 1 second

### Requirement 10: Error Handling and User Feedback

**User Story:** As a system user, I want clear error messages and feedback, so that I understand system status and can resolve issues.

#### Acceptance Criteria

1. WHEN Backend_System encounters an error, THE API_Layer SHALL return error response with descriptive message
2. THE Frontend_UI SHALL display error messages in notification banners or modal dialogs
3. WHEN camera initialization fails, THE Backend_System SHALL return error "Camera not accessible" to Frontend_UI
4. THE Frontend_UI SHALL display camera error with troubleshooting instructions
5. WHEN face detection fails during enrollment, THE Backend_System SHALL return error "No face detected" to Frontend_UI
6. THE Frontend_UI SHALL display face detection error with guidance to adjust position
7. WHEN network request fails, THE Frontend_UI SHALL display error "Connection lost - please check network"
8. THE Frontend_UI SHALL provide retry button for failed operations
