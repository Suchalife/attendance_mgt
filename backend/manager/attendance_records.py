# teacher/attendance_records.py - REFACTORED FOR INDUSTRIAL RECYCLER EMPLOYEE SYSTEM

import io
import base64
import numpy as np
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from datetime import datetime
from PIL import Image
from scipy.spatial.distance import cosine
from deepface import DeepFace
import logging
import time

logger = logging.getLogger(__name__)

# Attendance Blueprint with URL prefix
attendance_session_bp = Blueprint(
    "attendance_session",
    __name__,
    url_prefix="/api/attendance"
)

# ----------------- Optimized Helper Functions ----------------- #

def read_image_from_base64_optimized(image_b64: str, target_size=(640, 480)):
    """Convert base64 image to RGB numpy array with size optimization"""
    if image_b64.startswith("data:"):
        image_b64 = image_b64.split(",", 1)[1]

    image_bytes = base64.b64decode(image_b64)
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    if img.width > target_size[0] or img.height > target_size[1]:
        img.thumbnail(target_size, Image.Resampling.LANCZOS)

    return np.array(img)


def detect_faces_optimized(rgb_image, detector):
    """Detect faces using preloaded MTCNN detector"""
    if rgb_image.shape[0] < 50 or rgb_image.shape[1] < 50:
        return []

    detections = detector.detect_faces(rgb_image)
    faces = []

    for d in detections:
        if d["confidence"] > 0.85:
            x, y, w, h = d["box"]
            x, y = max(0, x), max(0, y)
            if w > 40 and h > 40:
                face_rgb = rgb_image[y:y+h, x:x+w]
                faces.append({
                    "box": (x, y, w, h),
                    "face": face_rgb,
                    "confidence": d["confidence"]
                })

    return faces


def extract_embedding_optimized(face_rgb):
    """Extract face embedding using preloaded DeepFace model"""
    try:
        if face_rgb.shape[0] < 40 or face_rgb.shape[1] < 40:
            return None

        face_pil = Image.fromarray(face_rgb.astype("uint8")).resize((160, 160))
        face_array = np.array(face_pil)

        rep = DeepFace.represent(
            face_array,
            model_name="Facenet512",
            detector_backend="skip",
            enforce_detection=False
        )
        return np.array(rep[0]["embedding"], dtype=np.float32)

    except Exception as e:
        logger.error(f"Embedding extraction error: {e}")
        return None


def get_attendance_collection():
    """Get the attendance collection from app config"""
    return current_app.config.get("ATTENDANCE_COLLECTION")


# Enhanced embedding cache for attendance sessions
class AttendanceEmbeddingCache:
    def __init__(self):
        self.cached_embeddings = {}
        self.last_update = {}
        self.cache_duration = 600  # 10 minutes for attendance sessions

    def get_session_embeddings(self, employees_col, session_filter):
        """Get cached embeddings for specific session filters"""
        cache_key = str(sorted(session_filter.items()))
        current_time = time.time()

        if (cache_key not in self.cached_embeddings or
                current_time - self.last_update.get(cache_key, 0) > self.cache_duration):

            logger.info(f"Refreshing attendance embedding cache for {session_filter}")

            employees = list(employees_col.find(session_filter))

            session_embeddings = []
            for employee in employees:
                embeddings = employee.get('embeddings') or employee.get('embedding')
                if embeddings:
                    if isinstance(embeddings, list) and len(embeddings) > 0:
                        if isinstance(embeddings[0], list):
                            avg_embedding = np.mean(embeddings, axis=0).astype(np.float32)
                        else:
                            avg_embedding = np.array(embeddings, dtype=np.float32)
                    else:
                        avg_embedding = np.array(embeddings, dtype=np.float32)

                    session_embeddings.append({
                        'embedding': avg_embedding,
                        'employeeId': employee.get('employeeId'),
                        'employeeName': employee.get('employeeName'),
                        'department': employee.get('department'),
                        'shift': employee.get('shift')
                    })

            self.cached_embeddings[cache_key] = session_embeddings
            self.last_update[cache_key] = current_time
            logger.info(f"Cached {len(session_embeddings)} employee embeddings for session")

        return self.cached_embeddings[cache_key]


# Global cache instance for attendance
attendance_cache = AttendanceEmbeddingCache()


def find_best_match_optimized_attendance(query_embedding, employees_col, session_doc, threshold=0.6):
    """Optimized employee matching for attendance with session-specific filtering"""
    employee_filter = {"embeddings": {"$exists": True, "$ne": None}}

    if session_doc.get("department"):
        employee_filter["department"] = session_doc.get("department")
    if session_doc.get("shift"):
        employee_filter["shift"] = session_doc.get("shift")

    cached_embeddings = attendance_cache.get_session_embeddings(employees_col, employee_filter)

    if not cached_embeddings:
        return None, float('inf')

    best_match = None
    min_distance = float('inf')

    for employee_data in cached_embeddings:
        stored_embedding = employee_data['embedding']
        distance = cosine(query_embedding, stored_embedding)

        if distance < min_distance:
            min_distance = distance
            best_match = employee_data

    return best_match if min_distance < threshold else None, min_distance


# ----------------- Routes ----------------- #

@attendance_session_bp.route("/create_session", methods=["POST"])
def create_session():
    """Create a new employee attendance session"""
    data = request.json
    db = current_app.config.get("DB")
    employees_col = db.employees

    session_doc = {
        "date": data.get("date") or datetime.now().strftime("%Y-%m-%d"),
        "department": data.get("department"),
        "shift": data.get("shift"),
        "created_at": datetime.now(),
        "finalized": False,
        "ended_at": None,
        "employees": []
    }

    # Pre-populate session with all employees in that department/shift
    employee_filter = {}
    if data.get("department"):
        employee_filter["department"] = data.get("department")
    if data.get("shift"):
        employee_filter["shift"] = data.get("shift")

    try:
        employees = list(employees_col.find(employee_filter)) if employee_filter else []
        for e in employees:
            eid = e.get("employeeId") or e.get("employee_id")
            ename = e.get("employeeName") or e.get("employee_name")
            session_doc["employees"].append({
                "employee_id": eid,
                "employee_name": ename,
                "department": e.get("department"),
                "shift": e.get("shift"),
                "present": False,
                "marked_at": None
            })

        logger.info(f"Created session with {len(employees)} employees preloaded")

    except Exception as e:
        logger.error(f"Error preloading employees: {e}")

    collection = get_attendance_collection()
    session_id = collection.insert_one(session_doc).inserted_id
    return jsonify({
        "success": True,
        "sessionId": str(session_id),
        "session_id": str(session_id),
        "employees_count": len(session_doc["employees"])
    })


@attendance_session_bp.route("/end_session", methods=["POST"])
def end_session():
    """Finalize an attendance session"""
    data = request.get_json()
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    try:
        collection = get_attendance_collection()
        db = current_app.config.get("DB")
        employees_col = db.employees

        session_doc = collection.find_one({"_id": ObjectId(session_id)})
        if not session_doc:
            return jsonify({"error": "Session not found"}), 404

        # Build set of present employee ids
        present_employees = set(
            e.get("employee_id") for e in session_doc.get("employees", [])
            if e.get("present")
        )

        # Get all employees in that department/shift
        employee_filter = {}
        if session_doc.get("department"):
            employee_filter["department"] = session_doc.get("department")
        if session_doc.get("shift"):
            employee_filter["shift"] = session_doc.get("shift")

        all_employees = list(employees_col.find(employee_filter)) if employee_filter else []

        # Mark absent employees
        absent_count = 0
        for e in all_employees:
            eid = e.get("employeeId") or e.get("employee_id")
            ename = e.get("employeeName") or e.get("employee_name")

            if eid not in present_employees:
                updated = collection.update_one(
                    {"_id": ObjectId(session_id), "employees.employee_id": eid},
                    {"$set": {"employees.$.present": False, "employees.$.marked_at": None}}
                )

                if updated.matched_count == 0:
                    collection.update_one(
                        {"_id": ObjectId(session_id)},
                        {"$push": {
                            "employees": {
                                "employee_id": eid,
                                "employee_name": ename,
                                "present": False,
                                "marked_at": None
                            }
                        }}
                    )
                absent_count += 1

        # Mark session as finalized
        collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"finalized": True, "ended_at": datetime.now()}}
        )

        logger.info(f"Session finalized: {len(present_employees)} present, {absent_count} absent")

        return jsonify({
            "success": True,
            "statistics": {
                "present_count": len(present_employees),
                "absent_count": absent_count,
                "total_employees": len(all_employees)
            }
        })

    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_session_bp.route("/real-mark", methods=["POST"])
def mark_attendance_with_duplicate_prevention():
    """Mark employee attendance with duplicate prevention"""
    start_time = time.time()

    model_manager = current_app.config.get("MODEL_MANAGER")
    if not model_manager or not model_manager.is_ready():
        return jsonify({"error": "Face recognition models not initialized"}), 503

    detector = model_manager.get_detector()

    data = request.get_json()
    session_id = data.get("sessionId") or data.get("session_id")
    image_b64 = data.get("image")

    if not session_id or not image_b64:
        return jsonify({"error": "Missing session_id or image"}), 400

    try:
        rgb = read_image_from_base64_optimized(image_b64)
        faces = detect_faces_optimized(rgb, detector)

        if len(faces) == 0:
            return jsonify({"message": "No faces detected", "faces": []})

        collection = get_attendance_collection()
        session_doc = collection.find_one({"_id": ObjectId(session_id)})
        if not session_doc:
            return jsonify({"error": "Session not found"}), 404
        if session_doc.get("finalized"):
            return jsonify({"error": "Session already finalized"}), 400

        # Get set of already-marked employees
        already_present_employees = set()
        for entry in session_doc.get("employees", []):
            if entry.get("present") == True:
                already_present_employees.add(entry.get("employee_id"))

        logger.info(f"Session {session_id} already has {len(already_present_employees)} employees marked present")

        db = current_app.config.get("DB")
        employees_col = db.employees
        threshold = float(current_app.config.get("THRESHOLD", 0.6))

        employees = list(employees_col.find({"embeddings": {"$exists": True, "$ne": None}}))
        results = []

        for f in faces:
            emb = extract_embedding_optimized(f["face"])
            if emb is None:
                results.append({
                    "match": None,
                    "distance": None,
                    "box": f["box"],
                    "error": "Failed to extract embedding"
                })
                continue

            best, min_d = None, float("inf")
            for employee in employees:
                stored_embeddings = employee.get("embeddings", [])
                if not stored_embeddings:
                    continue

                if isinstance(stored_embeddings, list) and len(stored_embeddings) > 0:
                    avg_embedding = np.mean(stored_embeddings, axis=0)
                else:
                    avg_embedding = np.array(stored_embeddings)

                d = cosine(emb, avg_embedding)
                if d < min_d:
                    min_d = d
                    best = employee

            if min_d < threshold and best:
                employee_id = best.get("employeeId")
                employee_name = best.get("employeeName")
                department = best.get("department")

                # Duplicate prevention check
                if employee_id in already_present_employees:
                    results.append({
                        "match": {
                            "employee_id": employee_id,
                            "employee_name": employee_name,
                            "department": department
                        },
                        "distance": round(float(min_d), 4),
                        "confidence": round((1 - min_d) * 100, 1),
                        "box": f["box"],
                        "already_marked": True,
                        "status": "duplicate",
                        "message": f"{employee_name} is already marked present in this session"
                    })
                    logger.info(f"Duplicate detection: {employee_name} ({employee_id}) already present")
                    continue

                # Mark attendance
                updated = collection.update_one(
                    {"_id": ObjectId(session_id), "employees.employee_id": employee_id,
                     "employees.present": False},
                    {"$set": {"employees.$.present": True, "employees.$.marked_at": datetime.now()}}
                )

                if updated.matched_count > 0 and updated.modified_count > 0:
                    already_present_employees.add(employee_id)
                    results.append({
                        "match": {
                            "employee_id": employee_id,
                            "employee_name": employee_name,
                            "department": department
                        },
                        "distance": round(float(min_d), 4),
                        "confidence": round((1 - min_d) * 100, 1),
                        "box": f["box"],
                        "already_marked": False,
                        "status": "marked_present",
                        "message": f"{employee_name} marked present successfully"
                    })
                    logger.info(f"✅ Marked {employee_name} ({employee_id}) as present")
                else:
                    # Employee not in session yet, add them
                    collection.update_one(
                        {"_id": ObjectId(session_id)},
                        {"$push": {
                            "employees": {
                                "employee_id": employee_id,
                                "employee_name": employee_name,
                                "department": department,
                                "present": True,
                                "marked_at": datetime.now()
                            }
                        }}
                    )
                    already_present_employees.add(employee_id)
                    results.append({
                        "match": {
                            "employee_id": employee_id,
                            "employee_name": employee_name,
                            "department": department
                        },
                        "distance": round(float(min_d), 4),
                        "confidence": round((1 - min_d) * 100, 1),
                        "box": f["box"],
                        "already_marked": False,
                        "status": "marked_present_new",
                        "message": f"{employee_name} added to session and marked present"
                    })
                    logger.info(f"✅ Added {employee_name} ({employee_id}) to session as present")
            else:
                results.append({
                    "match": None,
                    "distance": round(float(min_d), 4) if min_d != float('inf') else None,
                    "confidence": round((1 - min_d) * 100, 1) if min_d != float('inf') else None,
                    "box": f["box"],
                    "status": "no_match",
                    "message": "Face not recognized"
                })

        processing_time = time.time() - start_time

        # Build recognized list for frontend (newly marked employees only)
        recognized = [
            {
                "employeeId": r["match"]["employee_id"],
                "employeeName": r["match"]["employee_name"],
                "department": r["match"].get("department", ""),
                "confidence": r.get("confidence", 0) / 100,
                "status": r.get("status")
            }
            for r in results
            if r.get("match") and r.get("status") in ("marked_present", "marked_present_new")
        ]

        return jsonify({
            "success": True,
            "message": "Recognition processed",
            "faces": results,
            "recognized": recognized,
            "processing_time": round(processing_time, 3),
            "session_info": {
                "session_id": session_id,
                "total_present_now": len(already_present_employees),
                "faces_detected": len(faces),
                "duplicates_prevented": sum(1 for r in results if r.get("status") == "duplicate")
            }
        })

    except Exception as e:
        logger.error(f"Attendance error: {e}")
        return jsonify({"error": str(e)}), 500


# Health check for attendance models
@attendance_session_bp.route("/models/status", methods=["GET"])
def attendance_model_status():
    """Check model status for the attendance system"""
    model_manager = current_app.config.get("MODEL_MANAGER")

    if not model_manager:
        return jsonify({
            "success": False,
            "error": "Model manager not available"
        }), 500

    return jsonify({
        "success": True,
        "models_ready": model_manager.is_ready(),
        "health_check": model_manager.health_check(),
        "cache_info": {
            "embedding_cache_active": True,
            "cache_duration": "10 minutes"
        },
        "timestamp": time.time()
    })
