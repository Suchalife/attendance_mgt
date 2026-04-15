# This file makes the student directory a Python package
# Note: Directory retains name 'student' for backwards compatibility
# All internal references have been updated to use employee terminology

from .registration import employee_registration_bp
from .updatedetails import employee_update_bp
from .demo_session import demo_session_bp
from .view_attendance import attendance_bp

__all__ = [
    'employee_registration_bp',
    'employee_update_bp',
    'demo_session_bp',
    'attendance_bp'
]
