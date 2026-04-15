from flask import Blueprint, request, jsonify, current_app
import time
import base64
import numpy as np
from PIL import Image
import io
from deepface import DeepFace
import logging

employee_registration_bp = Blueprint("employee_registration", __name__)
logger = logging.getLogger(__name__)

DEPARTMENTS = [
    "Sorting", "Shredding", "Processing",
    "Packaging", "Logistics", "Quality Control", "Administration"
]
SHIFT = "Day"


def read_image_from_bytes(b):
    img = Image.open(io.BytesIO(b)).convert('RGB')
    return np.array(img)


def detect_faces_rgb(rgb_image, detector):
    detections = detector.detect_faces(rgb_image)
    faces = []
    for d in detections:
        if d['confidence'] > 0.9:
            x, y, w, h = d['box']
            x, y = max(0, x), max(0, y)
            if w > 50 and h > 50:
                face_rgb = rgb_image[y:y+h, x:x+w]
                faces.append({'box': (x, y, w, h), 'face': face_rgb, 'confidence': d['confidence']})
    return faces


def extract_embedding(face_rgb):
    try:
        face_pil = Image.fromarray(face_rgb.astype('uint8')).resize((160, 160))
        face_array = np.array(face_pil)
        rep = DeepFace.represent(face_array, model_name='Facenet512', detector_backend='skip')
        return np.array(rep[0]['embedding'], dtype=float)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None


def process_images(images, detector):
    """Process face images and return embeddings list."""
    embeddings = []
    for idx, img_b64 in enumerate(images):
        try:
            if img_b64.startswith("data:"):
                img_b64 = img_b64.split(",", 1)[1]
            rgb = read_image_from_bytes(base64.b64decode(img_b64))
        except Exception:
            return None, f"Invalid image data at index {idx}"

        faces = detect_faces_rgb(rgb, detector)
        if len(faces) != 1:
            return None, f"Ensure exactly one face per image (failed at image {idx+1})"

        emb = extract_embedding(faces[0]['face'])
        if emb is None:
            return None, f"Failed to extract face features for image {idx+1}"
        embeddings.append(emb.tolist())
    return embeddings, None


@employee_registration_bp.route('/api/register-employee', methods=['POST'])
def register_employee():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON data"}), 400

    db = current_app.config.get("DB")
    detector = current_app.config.get("MTCNN_DETECTOR")
    employees_col = db.employees

    # Accept both camelCase aliases for field names
    employee_name = data.get('employeeName') or data.get('name')
    employee_id = data.get('employeeId') or data.get('id')
    phone = data.get('phoneNumber') or data.get('phone')
    email = data.get('email')
    department = data.get('department')
    phase = data.get('phase', 'details')  # 'details' (step 1) or 'biometric' (step 2)
    images = data.get('images', [])

    # ── Phase 2: Add biometric embeddings to an existing employee ──
    if phase == 'biometric':
        if not employee_id:
            return jsonify({"success": False, "error": "employeeId is required"}), 400
        if not images or len(images) != 5:
            return jsonify({"success": False, "error": "Exactly 5 face images are required"}), 400

        existing = employees_col.find_one({'employeeId': employee_id})
        if not existing:
            return jsonify({"success": False, "error": "Employee not found. Complete step 1 first."}), 404

        embeddings, err = process_images(images, detector)
        if err:
            return jsonify({"success": False, "error": err}), 400

        employees_col.update_one(
            {'employeeId': employee_id},
            {'$set': {'embeddings': embeddings, 'face_registered': True, 'updated_at': time.time()}}
        )
        return jsonify({"success": True, "employeeId": employee_id, "message": "Biometric enrollment complete"})

    # ── Phase 1: Save employee details (images optional) ──
    if not employee_name:
        return jsonify({"success": False, "error": "employeeName is required"}), 400
    if not employee_id:
        return jsonify({"success": False, "error": "employeeId is required"}), 400
    if not email:
        return jsonify({"success": False, "error": "email is required"}), 400

    if department and department not in DEPARTMENTS:
        return jsonify({"success": False, "error": f"Invalid department. Must be one of: {', '.join(DEPARTMENTS)}"}), 400

    if employees_col.find_one({'employeeId': employee_id}):
        return jsonify({"success": False, "error": "Employee ID already exists"}), 400
    if employees_col.find_one({'email': email}):
        return jsonify({"success": False, "error": "Email already registered"}), 400

    employee_data = {
        "employeeId": employee_id,
        "employeeName": employee_name,
        "department": department,
        "shift": SHIFT,
        "email": email,
        "phoneNumber": phone,
        "role": data.get("role", ""),
        "branch": data.get("branch", ""),
        "status": "active",
        "embeddings": [],
        "face_registered": False,
        "created_at": time.time(),
        "updated_at": time.time()
    }

    # If all 5 images provided upfront, process them now
    if images:
        if len(images) != 5:
            return jsonify({"success": False, "error": "Exactly 5 face images are required"}), 400
        embeddings, err = process_images(images, detector)
        if err:
            return jsonify({"success": False, "error": err}), 400
        employee_data["embeddings"] = embeddings
        employee_data["face_registered"] = True

    result = employees_col.insert_one(employee_data)
    return jsonify({
        "success": True,
        "employeeId": employee_id,
        "record_id": str(result.inserted_id)
    })


@employee_registration_bp.route('/api/employees/count', methods=['GET'])
def get_employee_count():
    db = current_app.config.get("DB")
    return jsonify({"success": True, "count": db.employees.count_documents({})})


@employee_registration_bp.route('/api/employees/departments', methods=['GET'])
def get_departments():
    db = current_app.config.get("DB")
    departments = db.employees.distinct("department")
    return jsonify({"success": True, "departments": departments, "count": len(departments)})
