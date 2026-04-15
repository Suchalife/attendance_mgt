"""
Single-Server Flask Application for Employee Attendance System
Serves both backend APIs and frontend UI from the same server
"""
from flask import Flask, render_template
from flask_cors import CORS
from routes.employees import employees_bp
from routes.camera import camera_bp
from routes.attendance import attendance_bp

# Create Flask app with template and static folder configuration
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')

# Enable CORS for any remaining cross-origin requests
CORS(app)

# Register API blueprints
app.register_blueprint(employees_bp)
app.register_blueprint(camera_bp)
app.register_blueprint(attendance_bp)


# Frontend Routes
@app.route('/')
def home():
    """Home page - redirect to biometric enrollment"""
    return render_template("biometric_enrollment_expanded/code.html")


@app.route('/enrollment')
def enrollment_page():
    """Biometric enrollment page"""
    return render_template("biometric_enrollment_expanded/code.html")


@app.route('/attendance')
def attendance_page():
    """Live attendance page"""
    return render_template("live_attendance/code.html")


@app.route('/dashboard')
def dashboard_page():
    """Operations dashboard page"""
    return render_template("operations_dashboard/code.html")


@app.route('/registration')
def registration_page():
    """Employee registration page"""
    return render_template("employee_registration_updated/code.html")


@app.route('/reports')
def reports_page():
    """Attendance reports page"""
    return render_template("attendance_reports_simplified/code.html")


# API Health Check
@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'message': 'API is running'
    }


if __name__ == '__main__':
    print("=" * 60)
    print("Employee Attendance System - Single Server Application")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("\nFrontend Pages:")
    print("  GET  /                    - Home (Biometric Enrollment)")
    print("  GET  /enrollment          - Biometric Enrollment")
    print("  GET  /attendance          - Live Attendance")
    print("  GET  /dashboard           - Operations Dashboard")
    print("  GET  /registration        - Employee Registration")
    print("  GET  /reports             - Attendance Reports")
    print("\nAPI Endpoints:")
    print("  GET  /health              - Health check")
    print("\n  Employee Management:")
    print("  POST /api/employees       - Create employee")
    print("  GET  /api/employees       - Get all employees")
    print("  GET  /api/employees/count - Get employee count")
    print("\n  Camera Streaming:")
    print("  GET  /api/camera/stream   - MJPEG camera stream")
    print("  POST /api/camera/start    - Start camera")
    print("  POST /api/camera/stop     - Stop camera")
    print("  GET  /api/camera/status   - Camera status")
    print("  POST /api/camera/capture  - Capture images for training")
    print("  POST /api/camera/train    - Train face recognition model")
    print("\n  Attendance:")
    print("  POST /api/attendance/start - Start attendance (detect & mark)")
    print("  GET  /api/attendance       - Get attendance records")
    print("  GET  /api/attendance/stats - Get attendance statistics")
    print("  POST /api/attendance/mark  - Manually mark attendance")
    print("=" * 60)
    print("🚀 Single server mode: Frontend + Backend integrated!")
    print("📱 Open http://localhost:5000 in your browser")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
