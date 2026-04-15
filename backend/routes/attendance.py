"""
Attendance Routes
Handles attendance marking and retrieval
"""
from flask import Blueprint, request, jsonify
from services.camera_service import camera_service
from services.recognition_service import recognition_service
from services.attendance_service import attendance_service
from services.csv_service import CSVService
import uuid

attendance_bp = Blueprint('attendance', __name__)
csv_service = CSVService()


@attendance_bp.route('/api/attendance/start', methods=['POST'])
def start_attendance():
    """
    Start attendance session and mark attendance for detected face
    
    Process:
    1. Get frame from camera
    2. Detect face
    3. Recognize employee (placeholder)
    4. Mark attendance
    
    Returns:
        JSON response with recognition result and attendance status (camelCase format)
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Check if camera is active
        if not camera_service.is_camera_active():
            # Try to start camera
            if not camera_service.start_camera():
                return jsonify({
                    'success': False,
                    'error': 'Camera not available. Please start camera first.'
                }), 500
        
        # Get frame from camera
        frame_bytes = camera_service.get_frame()
        
        if frame_bytes is None:
            return jsonify({
                'success': False,
                'error': 'Failed to capture frame from camera'
            }), 500
        
        # Get all employees for recognition
        employees_raw = csv_service.read_csv('employees.csv')
        
        # Transform to camelCase for recognition service
        employees = []
        for emp in employees_raw:
            employees.append({
                'employeeId': emp.get('EmployeeID'),
                'employeeName': emp.get('EmployeeName'),
                'department': emp.get('Department'),
                'shift': emp.get('Shift')
            })
        
        # Recognize employee from frame
        recognition_result = recognition_service.recognize_employee(frame_bytes, employees)
        
        # If face detected and employee recognized, mark attendance
        if recognition_result['face_detected'] and recognition_result['employee_id']:
            attendance_result = attendance_service.mark_attendance(
                employee_id=recognition_result['employee_id'],
                employee_name=recognition_result['employee_name'],
                department=recognition_result['department'],
                status='Present',
                session_id=session_id
            )
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'face_detected': True,
                'employee_recognized': True,
                'employee': {
                    'employeeId': recognition_result['employee_id'],
                    'employeeName': recognition_result['employee_name'],
                    'department': recognition_result['department']
                },
                'attendance': attendance_result,
                'message': recognition_result['message']
            }), 200
        
        # Face detected but no employee recognized
        elif recognition_result['face_detected']:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'face_detected': True,
                'employee_recognized': False,
                'message': recognition_result['message']
            }), 200
        
        # No face detected
        else:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'face_detected': False,
                'employee_recognized': False,
                'message': recognition_result['message']
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error processing attendance: {str(e)}'
        }), 500


@attendance_bp.route('/api/attendance', methods=['GET'])
def get_attendance():
    """
    Get all attendance records
    
    Query parameters:
        - session_id: Filter by session ID (optional)
        - date: Filter by date in format YYYY-MM-DD (optional)
    
    Returns:
        JSON response with attendance records
    """
    try:
        session_id = request.args.get('session_id')
        date = request.args.get('date')
        
        if session_id:
            records = attendance_service.get_attendance_by_session(session_id)
        elif date:
            records = attendance_service.get_attendance_by_date(date)
        else:
            records = attendance_service.get_all_attendance()
        
        return jsonify({
            'success': True,
            'count': len(records),
            'records': records
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error retrieving attendance: {str(e)}'
        }), 500


@attendance_bp.route('/api/attendance/stats', methods=['GET'])
def get_attendance_stats():
    """
    Get attendance statistics
    
    Returns:
        JSON response with attendance stats
    """
    try:
        stats = attendance_service.get_attendance_stats()
        
        # Get total employees count
        employees = csv_service.read_csv('employees.csv')
        total_employees = len(employees)
        
        # Calculate absent
        present_today = stats.get('present_today', 0)
        absent_today = max(0, total_employees - present_today)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_employees': total_employees,
                'present_today': present_today,
                'absent_today': absent_today,
                'total_records': stats.get('total_records', 0)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error calculating stats: {str(e)}'
        }), 500


@attendance_bp.route('/api/attendance/mark', methods=['POST'])
def mark_attendance_manual():
    """
    Manually mark attendance (for testing or manual entry)
    Accepts both camelCase and PascalCase field names
    
    Request body:
        {
            "employeeId"/"EmployeeID": "string",
            "employeeName"/"EmployeeName": "string",
            "department"/"Department": "string",
            "status": "Present" (optional),
            "sessionId": "string" (optional)
        }
    
    Returns:
        JSON response with attendance result
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Accept both camelCase and PascalCase formats
        employee_id = data.get('employeeId') or data.get('EmployeeID')
        employee_name = data.get('employeeName') or data.get('EmployeeName')
        department = data.get('department') or data.get('Department')
        status = data.get('status') or 'Present'
        session_id = data.get('sessionId') or data.get('SessionID')
        
        # Validate required fields
        if not employee_id:
            return jsonify({
                'success': False,
                'error': 'Missing required field: employeeId'
            }), 400
        
        if not employee_name:
            return jsonify({
                'success': False,
                'error': 'Missing required field: employeeName'
            }), 400
        
        if not department:
            return jsonify({
                'success': False,
                'error': 'Missing required field: department'
            }), 400
        
        # Mark attendance
        result = attendance_service.mark_attendance(
            employee_id=employee_id,
            employee_name=employee_name,
            department=department,
            status=status,
            session_id=session_id
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error marking attendance: {str(e)}'
        }), 500
