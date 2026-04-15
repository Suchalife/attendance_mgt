from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
import time

employee_update_bp = Blueprint("employee_update", __name__)

DEPARTMENTS = [
    "Sorting", "Shredding", "Processing",
    "Packaging", "Logistics", "Quality Control", "Administration"
]
# Shift is always 'Day'
SHIFT = "Day"

# ============================================================================
# EMPLOYEE ROUTES (Employees can only update their own records)
# ============================================================================

@employee_update_bp.route('/api/employees', methods=['GET'])
def get_employees():
    """Get employees for the logged-in user (email-based authorization for employees only)"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    try:
        user_email = request.headers.get('X-User-Email') or request.args.get('user_email') or ''
        user_type = request.headers.get('X-User-Type', 'manager')

        department = request.args.get('department', '')
        search = request.args.get('search', '')

        # For employees: only show their own record
        if user_type == 'employee':
            query = {"email": user_email}
            if department:
                query['department'] = department
            if search:
                query['$or'] = [
                    {'employeeName': {'$regex': search, '$options': 'i'}},
                    {'employeeId': {'$regex': search, '$options': 'i'}}
                ]
        else:
            # For managers: show all employees
            query = {}
            if department:
                query['department'] = department
            if search:
                query['$or'] = [
                    {'employeeName': {'$regex': search, '$options': 'i'}},
                    {'employeeId': {'$regex': search, '$options': 'i'}},
                    {'email': {'$regex': search, '$options': 'i'}}
                ]

        employees = list(employees_col.find(query, {"embeddings": 0}).sort('employeeName', 1))
        for employee in employees:
            employee['_id'] = str(employee['_id'])

        return jsonify({
            "success": True,
            "employees": employees,
            "count": len(employees),
            "user_type": user_type
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@employee_update_bp.route('/api/employees/<employee_db_id>', methods=['GET'])
def get_employee(employee_db_id):
    """Get a specific employee record (email-based authorization)"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    try:
        user_email = request.headers.get('X-User-Email') or ''
        user_type = request.headers.get('X-User-Type', 'manager')

        # Look up by employeeId field first, fall back to MongoDB _id
        employee = employees_col.find_one({"employeeId": employee_db_id}, {"embeddings": 0})
        if not employee:
            try:
                employee = employees_col.find_one({"_id": ObjectId(employee_db_id)}, {"embeddings": 0})
            except Exception:
                pass
        if not employee:
            return jsonify({"success": False, "error": "Employee not found"}), 404

        if user_type == 'employee':
            if employee.get('email') != user_email:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized: You can only view your own employee record"
                }), 403
        elif user_type == 'manager':
            pass  # Managers can view any employee record
        else:
            return jsonify({"success": False, "error": "Invalid user type"}), 403

        employee['_id'] = str(employee['_id'])
        return jsonify({"success": True, "employee": employee})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@employee_update_bp.route('/api/employees/<employee_db_id>', methods=['PUT'])
def update_employee(employee_db_id):
    """Update employee record (employees can update own, managers can update any)"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    data = request.get_json()

    try:
        user_email = request.headers.get('X-User-Email') or data.get('user_email') or ''
        user_type = request.headers.get('X-User-Type', 'manager')

        # Look up by employeeId field first, fall back to MongoDB _id
        employee = employees_col.find_one({"employeeId": employee_db_id})
        if not employee:
            try:
                employee = employees_col.find_one({"_id": ObjectId(employee_db_id)})
            except Exception:
                pass
        if not employee:
            return jsonify({"success": False, "error": "Employee not found"}), 404

        if user_type == 'employee':
            if employee.get('email') != user_email:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized: You can only update your own employee record"
                }), 403
            if data.get('email') and data.get('email') != employee.get('email'):
                return jsonify({
                    "success": False,
                    "error": "Email cannot be changed for security reasons. Contact administrator."
                }), 400
        elif user_type == 'manager':
            if data.get('email') and data.get('email') != employee.get('email'):
                existing = employees_col.find_one({
                    'email': data.get('email'),
                    '_id': {'$ne': ObjectId(employee_db_id)}
                })
                if existing:
                    return jsonify({"success": False, "error": "Email already registered"}), 400
        else:
            return jsonify({"success": False, "error": "Invalid user type"}), 403

        if data.get('employeeId') and data.get('employeeId') != employee.get('employeeId'):
            existing = employees_col.find_one({
                'employeeId': data.get('employeeId'),
                '_id': {'$ne': employee['_id']}
            })
            if existing:
                return jsonify({"success": False, "error": "Employee ID already exists"}), 400

        # Accept both field name aliases from frontend
        update_data = {
            "employeeName": data.get("employeeName") or data.get("name") or employee.get("employeeName"),
            "employeeId": data.get("employeeId", employee.get("employeeId")),
            "department": data.get("department", employee.get("department")),
            "shift": SHIFT,
            "phoneNumber": data.get("phoneNumber") or data.get("phone") or employee.get("phoneNumber"),
            "role": data.get("role", employee.get("role", "")),
            "branch": data.get("branch", employee.get("branch", "")),
            "updated_at": time.time(),
            "updated_by": user_email,
            "updated_by_type": user_type
        }

        if user_type == 'manager':
            update_data["email"] = data.get("email", employee.get("email"))

        result = employees_col.update_one(
            {"_id": employee['_id']},
            {"$set": update_data}
        )

        if result.modified_count > 0:
            message = "Employee details updated successfully"
            if user_type == 'employee':
                message = "Your employee details updated successfully"
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": "No changes made"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@employee_update_bp.route('/api/employees/<employee_db_id>', methods=['DELETE'])
def delete_employee(employee_db_id):
    """Delete employee record"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    try:
        user_email = request.headers.get('X-User-Email') or ''
        user_type = request.headers.get('X-User-Type', 'manager')

        # Look up by employeeId field first, fall back to MongoDB _id
        employee = employees_col.find_one({"employeeId": employee_db_id})
        if not employee:
            try:
                employee = employees_col.find_one({"_id": ObjectId(employee_db_id)})
            except Exception:
                pass
        if not employee:
            return jsonify({"success": False, "error": "Employee not found"}), 404

        if user_type == 'employee':
            if employee.get('email') != user_email:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized: You can only delete your own employee record"
                }), 403
        elif user_type == 'manager':
            pass  # Managers can delete any employee record
        else:
            return jsonify({"success": False, "error": "Invalid user type"}), 403

        employees_col.delete_one({"_id": employee['_id']})

        message = f"Employee {employee.get('employeeName')} deleted successfully"
        if user_type == 'employee':
            message = f"Your employee record ({employee.get('employeeName')}) deleted successfully"

        return jsonify({"success": True, "message": message})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Alternative routes for frontend compatibility
@employee_update_bp.route('/api/update-employee/<employee_db_id>', methods=['PUT'])
def update_employee_alt(employee_db_id):
    """Alternative route for frontend compatibility"""
    return update_employee(employee_db_id)


@employee_update_bp.route('/api/delete-employee/<employee_db_id>', methods=['DELETE'])
def delete_employee_alt(employee_db_id):
    """Alternative route for frontend compatibility"""
    return delete_employee(employee_db_id)

# ============================================================================
# MANAGER/ADMIN ROUTES (Managers can access all employees)
# ============================================================================

@employee_update_bp.route('/api/admin/employees', methods=['GET'])
def get_all_employees_admin():
    """Admin/Manager route to view all employees with filtering"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    try:
        user_type = request.headers.get('X-User-Type')
        user_email = request.headers.get('X-User-Email')

        if user_type not in ['manager', 'admin']:
            return jsonify({
                "success": False,
                "error": "Unauthorized: Manager/Admin access required"
            }), 403

        department = request.args.get('department', '')
        shift = request.args.get('shift', '')
        employee_id = request.args.get('employeeId', '')
        search = request.args.get('search', '')

        query = {}
        if department:
            query['department'] = department
        if employee_id:
            query['employeeId'] = {'$regex': employee_id, '$options': 'i'}
        if search:
            query['$or'] = [
                {'employeeName': {'$regex': search, '$options': 'i'}},
                {'employeeId': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}}
            ]

        employees = list(employees_col.find(query, {"embedding": 0}).sort('employeeName', 1))
        for employee in employees:
            employee['_id'] = str(employee['_id'])

        return jsonify({
            "success": True,
            "employees": employees,
            "count": len(employees),
            "admin_view": True,
            "user_type": user_type
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@employee_update_bp.route('/api/manager/employees/search', methods=['GET'])
def search_employees_manager():
    """Advanced search for managers with multiple filters"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    try:
        user_type = request.headers.get('X-User-Type')
        if user_type != 'manager':
            return jsonify({
                "success": False,
                "error": "Unauthorized: Manager access required"
            }), 403

        employee_id = request.args.get('employeeId', '').strip()
        employee_name = request.args.get('employeeName', '').strip()
        department = request.args.get('department', '').strip()

        query = {}
        if employee_id:
            query['employeeId'] = {'$regex': employee_id, '$options': 'i'}
        if employee_name:
            query['employeeName'] = {'$regex': employee_name, '$options': 'i'}
        if department:
            query['department'] = department

        employees = list(employees_col.find(
            query,
            {"embedding": 0}
        ).limit(50).sort('employeeName', 1))

        for employee in employees:
            employee['_id'] = str(employee['_id'])

        return jsonify({
            "success": True,
            "employees": employees,
            "count": len(employees),
            "query": query
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@employee_update_bp.route('/api/manager/employee/<employee_id_or_db_id>', methods=['GET'])
def get_employee_by_id_manager(employee_id_or_db_id):
    """Manager route to get any employee by EmployeeID or database _id"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    try:
        user_type = request.headers.get('X-User-Type')
        if user_type != 'manager':
            return jsonify({
                "success": False,
                "error": "Unauthorized: Manager access required"
            }), 403

        employee = employees_col.find_one({"employeeId": employee_id_or_db_id}, {"embedding": 0})

        if not employee:
            try:
                employee = employees_col.find_one(
                    {"_id": ObjectId(employee_id_or_db_id)}, {"embedding": 0}
                )
            except Exception:
                pass

        if not employee:
            return jsonify({
                "success": False,
                "error": f"Employee with ID '{employee_id_or_db_id}' not found"
            }), 404

        employee['_id'] = str(employee['_id'])
        return jsonify({"success": True, "employee": employee})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@employee_update_bp.route('/api/manager/employee/<employee_db_id>', methods=['PUT'])
def update_employee_manager(employee_db_id):
    """Manager route to update any employee by database _id"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    data = request.get_json()

    try:
        user_type = request.headers.get('X-User-Type')
        user_email = request.headers.get('X-User-Email')

        if user_type != 'manager':
            return jsonify({
                "success": False,
                "error": "Unauthorized: Manager access required"
            }), 403

        employee = employees_col.find_one({"_id": ObjectId(employee_db_id)})
        if not employee:
            return jsonify({"success": False, "error": "Employee not found"}), 404

        if data.get('employeeId') and data.get('employeeId') != employee.get('employeeId'):
            existing = employees_col.find_one({
                'employeeId': data.get('employeeId'),
                '_id': {'$ne': ObjectId(employee_db_id)}
            })
            if existing:
                return jsonify({"success": False, "error": "Employee ID already exists"}), 400

        if data.get('email') and data.get('email') != employee.get('email'):
            existing = employees_col.find_one({
                'email': data.get('email'),
                '_id': {'$ne': ObjectId(employee_db_id)}
            })
            if existing:
                return jsonify({"success": False, "error": "Email already registered"}), 400

        update_data = {
            "employeeName": data.get("employeeName", employee.get("employeeName")),
            "employeeId": data.get("employeeId", employee.get("employeeId")),
            "department": data.get("department", employee.get("department")),
            "shift": SHIFT,  # Always Day
            "email": data.get("email", employee.get("email")),
            "phoneNumber": data.get("phoneNumber", employee.get("phoneNumber")),
            "updated_at": time.time(),
            "updated_by_manager": user_email or 'manager',
            "updated_by_type": "manager"
        }

        result = employees_col.update_one(
            {"_id": ObjectId(employee_db_id)},
            {"$set": update_data}
        )

        if result.modified_count > 0:
            return jsonify({
                "success": True,
                "message": f"Employee {data.get('employeeName', 'record')} updated successfully by manager"
            })
        else:
            return jsonify({"success": False, "error": "No changes made"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@employee_update_bp.route('/api/manager/employee/<employee_db_id>', methods=['DELETE'])
def delete_employee_manager(employee_db_id):
    """Manager route to delete any employee by database _id"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    try:
        user_type = request.headers.get('X-User-Type')
        if user_type != 'manager':
            return jsonify({
                "success": False,
                "error": "Unauthorized: Manager access required"
            }), 403

        employee = employees_col.find_one({"_id": ObjectId(employee_db_id)})
        if not employee:
            return jsonify({"success": False, "error": "Employee not found"}), 404

        employees_col.delete_one({"_id": ObjectId(employee_db_id)})

        return jsonify({
            "success": True,
            "message": f"Employee {employee.get('employeeName')} deleted successfully by manager"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# UTILITY ROUTES
# ============================================================================

@employee_update_bp.route('/api/employees/search', methods=['GET'])
def search_employees():
    """General search employees by various criteria"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    try:
        user_type = request.headers.get('X-User-Type', 'employee')
        user_email = request.headers.get('X-User-Email')

        if user_type not in ['employee', 'manager', 'admin']:
            return jsonify({"success": False, "error": "Unauthorized"}), 403

        search_term = request.args.get('q', '')
        department = request.args.get('department', '')
        shift = request.args.get('shift', '')
        limit = int(request.args.get('limit', 10))

        if not search_term and not department and not shift:
            return jsonify({"success": False, "error": "Search term or filters required"}), 400

        query = {}

        if user_type == 'employee':
            query['email'] = user_email

        if search_term:
            query['$or'] = [
                {'employeeName': {'$regex': search_term, '$options': 'i'}},
                {'employeeId': {'$regex': search_term, '$options': 'i'}},
                {'email': {'$regex': search_term, '$options': 'i'}}
            ]
        if department:
            query['department'] = department
        if shift:
            query['shift'] = shift

        employees = list(employees_col.find(
            query,
            {"embedding": 0}
        ).limit(limit).sort('employeeName', 1))

        for employee in employees:
            employee['_id'] = str(employee['_id'])

        return jsonify({
            "success": True,
            "employees": employees,
            "count": len(employees),
            "search_term": search_term,
            "user_type": user_type
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@employee_update_bp.route('/api/employees/stats', methods=['GET'])
def get_employee_stats():
    """Get employee statistics (admin/manager only)"""
    db = current_app.config.get("DB")
    employees_col = db.employees

    try:
        user_type = request.headers.get('X-User-Type')

        if user_type not in ['manager', 'admin']:
            return jsonify({
                "success": False,
                "error": "Unauthorized: Manager/Admin access required"
            }), 403

        total_employees = employees_col.count_documents({})

        # Employees by department
        dept_pipeline = [
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        dept_stats = list(employees_col.aggregate(dept_pipeline))

        # Employees with face data
        face_registered = employees_col.count_documents(
            {"embeddings": {"$exists": True, "$ne": None}}
        )

        return jsonify({
            "success": True,
            "stats": {
                "total_employees": total_employees,
                "face_registered": face_registered,
                "by_department": dept_stats,
                "shift": "Day (fixed)"
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
