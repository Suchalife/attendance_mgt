"""
Employee Management Routes
Handles employee registration and retrieval
"""
from flask import Blueprint, request, jsonify
from services.csv_service import CSVService

employees_bp = Blueprint('employees', __name__)
csv_service = CSVService()

# CSV configuration
EMPLOYEES_FILE = 'employees.csv'
EMPLOYEE_FIELDS = ['EmployeeID', 'EmployeeName', 'Department', 'Shift']


@employees_bp.route('/api/employees', methods=['POST'])
def create_employee():
    """
    Create new employee
    Accepts JSON with either camelCase or PascalCase field names:
    {employeeId/EmployeeID, employeeName/EmployeeName, department/Department, shift/Shift}
    """
    try:
        data = request.get_json()
        
        # Accept both camelCase (frontend) and PascalCase (legacy) formats
        employee_id = data.get('employeeId') or data.get('EmployeeID')
        employee_name = data.get('employeeName') or data.get('EmployeeName')
        department = data.get('department') or data.get('Department')
        shift = data.get('shift') or data.get('Shift') or 'Day'
        
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
        
        # Check for duplicate EmployeeID
        existing_employees = csv_service.read_csv(EMPLOYEES_FILE)
        if any(emp['EmployeeID'] == employee_id for emp in existing_employees):
            return jsonify({
                'success': False,
                'error': f'Employee ID {employee_id} already exists'
            }), 400
        
        # Prepare employee data for CSV (using PascalCase for CSV storage)
        employee_data = {
            'EmployeeID': employee_id,
            'EmployeeName': employee_name,
            'Department': department,
            'Shift': shift
        }
        
        # Append to CSV
        success = csv_service.append_csv(EMPLOYEES_FILE, employee_data, EMPLOYEE_FIELDS)
        
        if success:
            # Return response in camelCase format for frontend
            return jsonify({
                'success': True,
                'message': 'Employee created successfully',
                'employee': {
                    'employeeId': employee_id,
                    'employeeName': employee_name,
                    'department': department,
                    'shift': shift
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save employee data'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@employees_bp.route('/api/employees', methods=['GET'])
def get_employees():
    """
    Get all employees
    Returns list of all employees from CSV in camelCase format
    """
    try:
        employees = csv_service.read_csv(EMPLOYEES_FILE)
        
        # Transform PascalCase CSV data to camelCase for frontend
        transformed_employees = []
        for emp in employees:
            transformed_employees.append({
                'employeeId': emp.get('EmployeeID'),
                'employeeName': emp.get('EmployeeName'),
                'department': emp.get('Department'),
                'shift': emp.get('Shift')
            })
        
        return jsonify({
            'success': True,
            'count': len(transformed_employees),
            'employees': transformed_employees
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@employees_bp.route('/api/employees/count', methods=['GET'])
def get_employee_count():
    """
    Get total employee count
    """
    try:
        employees = csv_service.read_csv(EMPLOYEES_FILE)
        
        return jsonify({
            'success': True,
            'count': len(employees)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500
