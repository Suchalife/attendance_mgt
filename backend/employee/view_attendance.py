from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date as date_obj
import time
from collections import defaultdict

attendance_bp = Blueprint("attendance", __name__)

# ------------------------- GET ATTENDANCE -------------------------
@attendance_bp.route('/api/attendance', methods=['GET'])
def get_attendance():
    db = current_app.config.get("DB")
    attendance_col = db.attendance_records
    employees_col = db.employees

    date = request.args.get('date')
    department = request.args.get('department')
    shift = request.args.get('shift')
    employee_id = request.args.get('employee_id')

    try:
        # Query attendance collection
        query = {}
        if date:
            query["date"] = date
        if department:
            query["department"] = department
        if shift:
            query["shift"] = shift

        attendance_doc = attendance_col.find_one(query)

        # Build roster from employees collection for given department/shift filters
        roster_filter = {}
        if department:
            roster_filter["department"] = department
        if shift:
            roster_filter["shift"] = shift

        roster = list(employees_col.find(roster_filter)) if roster_filter else []

        # Map session employees by id for quick lookup
        session_map = {}
        if attendance_doc:
            for e in attendance_doc.get("employees", []):
                eid = e.get("employee_id")
                session_map[eid] = e

        attendance_list = []
        seen_employees = set()

        # Merge roster and session employees: show present and absent
        for employee in roster:
            eid = employee.get("employeeId") or employee.get("employee_id")
            if not eid or eid in seen_employees:
                continue
            seen_employees.add(eid)

            if employee_id and eid != employee_id:
                continue

            sess = session_map.get(eid, None)
            if sess:
                present = bool(sess.get("present"))
                marked_at = sess.get("marked_at")
                if marked_at is not None:
                    try:
                        marked_at = marked_at.isoformat()
                    except Exception:
                        marked_at = str(marked_at)
            else:
                present = False
                marked_at = None

            attendance_list.append({
                "employeeId": str(eid) if eid is not None else "",
                "employeeName": employee.get("employeeName") or employee.get("employee_name"),
                "department": str(attendance_doc.get("department")) if attendance_doc else str(department),
                "shift": str(attendance_doc.get("shift")) if attendance_doc else str(shift),
                "date": str(attendance_doc.get("date")) if attendance_doc else str(date),
                "status": "Present" if present else "Absent",
                "markedAt": marked_at
            })

        # Also include any session-only employees not in roster (fallback)
        if attendance_doc:
            for e in attendance_doc.get("employees", []):
                eid = e.get("employee_id")
                if eid in seen_employees:
                    continue
                if employee_id and eid != employee_id:
                    continue
                seen_employees.add(eid)

                marked = e.get("marked_at")
                if marked is not None:
                    try:
                        marked = marked.isoformat()
                    except Exception:
                        marked = str(marked)

                attendance_list.append({
                    "employeeId": str(eid) if eid is not None else "",
                    "employeeName": e.get("employee_name"),
                    "department": str(attendance_doc.get("department")),
                    "shift": str(attendance_doc.get("shift", "")),
                    "date": str(attendance_doc.get("date")),
                    "status": "Present" if e.get("present") else "Absent",
                    "markedAt": marked
                })

        # Stats computed against roster size
        total_employees = employees_col.count_documents(roster_filter) if roster_filter else 0
        present_count = sum(1 for r in attendance_list if r.get("status") == "Present")
        absent_count = max(total_employees - present_count, 0)
        attendance_rate = round((present_count / total_employees * 100) if total_employees > 0 else 0, 1)

        return jsonify({
            "success": True,
            "attendance": attendance_list,
            "stats": {
                "totalEmployees": total_employees,
                "presentToday": present_count,
                "absentToday": absent_count,
                "attendanceRate": attendance_rate
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ------------------------- EXPORT TO CSV/EXCEL -------------------------
@attendance_bp.route('/api/attendance/export', methods=['GET'])
def export_attendance():
    db = current_app.config.get("DB")
    attendance_col = db.attendance_records
    employees_col = db.employees

    date = request.args.get('date')
    department = request.args.get('department')
    shift = request.args.get('shift')

    try:
        query = {}
        if date:
            query["date"] = date
        if department:
            query["department"] = department
        if shift:
            query["shift"] = shift

        attendance_doc = attendance_col.find_one(query)
        present_employees = set()

        if attendance_doc:
            for employee in attendance_doc.get("employees", []):
                present_employees.add(employee.get("employee_id"))

        # Get all employees in that department/shift
        employee_filter = {}
        if department:
            employee_filter["department"] = department
        if shift:
            employee_filter["shift"] = shift

        employees = list(employees_col.find(employee_filter))
        export_data = []

        for employee in employees:
            eid = employee.get("employeeId") or employee.get("employee_id")
            name = employee.get("employeeName") or employee.get("employee_name")
            status = "Present" if eid in present_employees else "Absent"
            export_data.append({
                "employeeId": str(eid) if eid is not None else "",
                "employeeName": name,
                "department": str(department) if department else employee.get("department", "N/A"),
                "shift": str(shift) if shift else employee.get("shift", "N/A"),
                "date": str(date) if date else "N/A",
                "status": status
            })

        return jsonify({"success": True, "data": export_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ------------------------- ATTENDANCE SUMMARY (per employee) -------------------------
@attendance_bp.route('/api/attendance/summary', methods=['GET'])
def get_attendance_summary():
    """Return per-employee attendance summary across all sessions."""
    db = current_app.config.get("DB")
    attendance_col = db.attendance_records
    employees_col = db.employees

    user_email = request.headers.get('X-User-Email')
    user_type = request.headers.get('X-User-Type', 'employee')

    try:
        # Fetch all finalized sessions
        all_sessions = list(attendance_col.find({}))
        total_sessions = len(all_sessions)
        working_days = max(total_sessions, 1)

        # Aggregate presence counts per employeeId
        presence_count = defaultdict(int)
        for session in all_sessions:
            for entry in session.get("employees", []):
                if entry.get("present"):
                    eid = entry.get("employee_id")
                    if eid:
                        presence_count[eid] += 1

        # Build employee list
        query = {}
        if user_type == 'employee' and user_email:
            query = {"email": user_email}

        employees = list(employees_col.find(query, {"embeddings": 0}))
        summary = []
        for emp in employees:
            eid = emp.get("employeeId") or emp.get("employee_id")
            days_present = presence_count.get(eid, 0)
            attendance_rate = round(days_present / working_days * 100, 1) if working_days > 0 else 0
            summary.append({
                "employeeId": str(eid) if eid else "",
                "employeeName": emp.get("employeeName") or emp.get("employee_name", ""),
                "department": emp.get("department", ""),
                "daysPresent": days_present,
                "workingDays": working_days,
                "attendanceRate": attendance_rate,
            })

        return jsonify({"success": True, "summary": summary})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500