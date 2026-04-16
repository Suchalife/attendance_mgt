"""
Single-Server Flask Application for Employee Attendance System
Serves both backend APIs and frontend UI from the same server
"""
import os
import io
import csv
from flask import Flask, render_template, send_file, Response
from flask_cors import CORS
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
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
    return render_template("biometric_enrollment_expanded/code.html", active_page="enrollment")


@app.route('/enrollment')
def enrollment_page():
    """Biometric enrollment page"""
    return render_template("biometric_enrollment_expanded/code.html", active_page="enrollment")


@app.route('/attendance')
def attendance_page():
    """Live attendance page"""
    return render_template("live_attendance/code.html", active_page="attendance")


@app.route('/dashboard')
def dashboard_page():
    """Operations dashboard page"""
    return render_template("operations_dashboard/code.html", active_page="dashboard")


@app.route('/registration')
def registration_page():
    """Employee registration page"""
    return render_template("employee_registration_updated/code.html", active_page="registration")


@app.route('/reports')
def reports_page():
    """Attendance reports page"""
    return render_template("attendance_reports_simplified/code.html", active_page="reports")


# Download Routes
ATTENDANCE_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'attendance.csv')


@app.route('/download/csv')
def download_csv():
    """Download attendance data as CSV"""
    if not os.path.exists(ATTENDANCE_CSV_PATH):
        return {'error': 'No attendance data found'}, 404
    return send_file(
        ATTENDANCE_CSV_PATH,
        mimetype='text/csv',
        as_attachment=True,
        download_name='attendance.csv'
    )


@app.route('/download/pdf')
def download_pdf():
    """Download attendance data as PDF"""
    if not os.path.exists(ATTENDANCE_CSV_PATH):
        return {'error': 'No attendance data found'}, 404

    # Read CSV data
    rows = []
    with open(ATTENDANCE_CSV_PATH, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        return {'error': 'Attendance file is empty'}, 404

    # Build PDF in memory
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(letter),
                            leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Attendance Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Wrap long cell text in Paragraphs for word-wrap
    cell_style = styles['Normal']
    cell_style.fontSize = 8
    cell_style.leading = 10
    table_data = []
    for row in rows:
        table_data.append([Paragraph(cell, cell_style) for cell in row])

    num_cols = len(rows[0]) if rows else 1
    col_width = (doc.width) / num_cols
    col_widths = [col_width] * num_cols

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0058be')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)

    doc.build(elements)
    buf.seek(0)

    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='attendance.pdf'
    )


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
    print("Single server mode: Frontend + Backend integrated!")
    print("Open http://localhost:5000 in your browser")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
