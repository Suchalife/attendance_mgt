"""
Attendance Service for managing attendance records
Simple service using CSV storage
"""
from datetime import datetime, timedelta
from services.csv_service import CSVService


class AttendanceService:
    """Service for attendance operations"""
    
    def __init__(self):
        self.csv_service = CSVService()
        self.attendance_file = 'attendance.csv'
        self.attendance_fields = [
            'employeeId',
            'employeeName',
            'department',
            'timestamp',
            'status',
            'sessionId'
        ]
        
        # Create attendance file if it doesn't exist
        if not self.csv_service.file_exists(self.attendance_file):
            self.csv_service.write_csv(self.attendance_file, [], self.attendance_fields)
            print(f"Created {self.attendance_file}")
    
    def mark_attendance(self, employee_id, employee_name, department, status='Present', session_id=None):
        """
        Mark attendance for an employee
        
        Args:
            employee_id: Employee ID
            employee_name: Employee name
            department: Department name
            status: Attendance status (default: 'Present')
            session_id: Optional session ID for grouping attendance records
        
        Returns:
            dict: Result with success status and message
        """
        try:
            # Get current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Check for duplicate entry (within last 5 minutes)
            if self._is_duplicate_entry(employee_id, session_id):
                return {
                    'success': False,
                    'message': f'Attendance already marked for {employee_name} in this session',
                    'duplicate': True
                }
            
            # Create attendance record
            attendance_record = {
                'employeeId': employee_id,
                'employeeName': employee_name,
                'department': department,
                'timestamp': timestamp,
                'status': status,
                'sessionId': session_id or 'default'
            }
            
            # Append to CSV
            success = self.csv_service.append_csv(
                self.attendance_file,
                attendance_record,
                self.attendance_fields
            )
            
            if success:
                return {
                    'success': True,
                    'message': f'Attendance marked for {employee_name}',
                    'duplicate': False,
                    'record': attendance_record
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to save attendance record',
                    'duplicate': False
                }
                
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'duplicate': False
            }
    
    def _is_duplicate_entry(self, employee_id, session_id):
        """
        Check if employee already has attendance marked in current session
        
        Args:
            employee_id: Employee ID to check
            session_id: Session ID to check
        
        Returns:
            bool: True if duplicate found
        """
        try:
            # Read all attendance records
            records = self.csv_service.read_csv(self.attendance_file)
            
            # Check for existing entry with same employee and session
            for record in records:
                if (record.get('employeeId') == employee_id and 
                    record.get('sessionId') == (session_id or 'default')):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return False
    
    def get_all_attendance(self):
        """
        Get all attendance records
        
        Returns:
            list: List of attendance records
        """
        try:
            records = self.csv_service.read_csv(self.attendance_file)
            return records
        except Exception as e:
            print(f"Error reading attendance: {e}")
            return []
    
    def get_attendance_by_session(self, session_id):
        """
        Get attendance records for a specific session
        
        Args:
            session_id: Session ID to filter by
        
        Returns:
            list: Filtered attendance records
        """
        try:
            all_records = self.get_all_attendance()
            return [r for r in all_records if r.get('sessionId') == session_id]
        except Exception as e:
            print(f"Error filtering attendance: {e}")
            return []
    
    def get_attendance_by_date(self, date_str):
        """
        Get attendance records for a specific date
        
        Args:
            date_str: Date string in format 'YYYY-MM-DD'
        
        Returns:
            list: Filtered attendance records
        """
        try:
            all_records = self.get_all_attendance()
            return [r for r in all_records if r.get('timestamp', '').startswith(date_str)]
        except Exception as e:
            print(f"Error filtering by date: {e}")
            return []
    
    def get_attendance_stats(self):
        """
        Get attendance statistics for today

        Returns:
            dict: Statistics with present_today (unique employees), total_records
        """
        try:
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')

            # Get today's attendance
            today_records = self.get_attendance_by_date(today)

            # Count unique present employees (not duplicate records)
            unique_present = set()
            for record in today_records:
                emp_id = record.get('employeeId')
                if emp_id:
                    unique_present.add(emp_id)

            return {
                'present_today': len(unique_present),
                'total_records': len(self.get_all_attendance())
            }

        except Exception as e:
            print(f"Error calculating stats: {e}")
            return {
                'present_today': 0,
                'total_records': 0
            }

    def get_weekly_trend(self):
        """
        Get attendance counts for the last 7 days

        Returns:
            list: List of dicts with date, day_name, and count of unique present employees
        """
        try:
            all_records = self.get_all_attendance()
            today = datetime.now().date()
            trend = []

            for i in range(6, -1, -1):
                day = today - timedelta(days=i)
                date_str = day.strftime('%Y-%m-%d')
                day_name = day.strftime('%a')

                # Count unique employees for this day
                unique_present = set()
                for record in all_records:
                    if record.get('timestamp', '').startswith(date_str):
                        emp_id = record.get('employeeId')
                        if emp_id:
                            unique_present.add(emp_id)

                trend.append({
                    'date': date_str,
                    'day': day_name,
                    'count': len(unique_present)
                })

            return trend
        except Exception as e:
            print(f"Error calculating weekly trend: {e}")
            return []

    def get_recent_activity(self, limit=6):
        """
        Get most recent attendance records

        Args:
            limit: Maximum number of records to return

        Returns:
            list: Most recent attendance records sorted by timestamp descending
        """
        try:
            all_records = self.get_all_attendance()

            # Sort by timestamp descending
            sorted_records = sorted(
                all_records,
                key=lambda r: r.get('timestamp', ''),
                reverse=True
            )

            return sorted_records[:limit]
        except Exception as e:
            print(f"Error getting recent activity: {e}")
            return []

    def get_avg_attendance_pct(self, total_employees):
        """
        Calculate average attendance percentage over the last 7 days

        Args:
            total_employees: Total number of registered employees

        Returns:
            float: Average attendance percentage
        """
        try:
            if total_employees == 0:
                return 0.0

            trend = self.get_weekly_trend()
            # Only count days that have passed (with any data or today/past)
            days_with_data = [d for d in trend if d['count'] > 0]

            if not days_with_data:
                return 0.0

            total_pct = sum(
                (d['count'] / total_employees) * 100
                for d in days_with_data
            )

            return round(total_pct / len(days_with_data), 1)
        except Exception as e:
            print(f"Error calculating avg attendance: {e}")
            return 0.0


# Global attendance service instance
attendance_service = AttendanceService()
