# employee/demo_session.py - OPTIMIZED VERSION
from flask import Blueprint, request, jsonify, current_app
import time
import base64
import numpy as np
from PIL import Image
import io
from deepface import DeepFace
from scipy.spatial.distance import cosine
import logging
import threading

logger = logging.getLogger(__name__)

demo_session_bp = Blueprint("demo_session", __name__)


def read_image_from_bytes_optimized(b, target_size=(640, 480)):
    """Optimized image reading with size constraints"""
    img = Image.open(io.BytesIO(b)).convert("RGB")
    if img.width > target_size[0] or img.height > target_size[1]:
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
    return np.array(img)


def detect_faces_rgb_optimized(rgb_image, detector):
    """Optimized face detection using preloaded MTCNN detector"""
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
    """Optimized embedding extraction using preloaded model"""
    try:
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


# In-memory cache for employee embeddings
class EmbeddingCache:
    def __init__(self):
        self.employee_embeddings = None
        self.last_update = 0
        self.cache_duration = 300  # 5 minutes
        self.lock = threading.Lock()

    def get_embeddings(self, employees_col):
        current_time = time.time()

        with self.lock:
            if (self.employee_embeddings is None or
                    current_time - self.last_update > self.cache_duration):

                logger.info("Refreshing employee embedding cache...")

                employees = list(employees_col.find(
                    {"embeddings": {"$exists": True, "$ne": None}},
                    {"employeeId": 1, "employeeName": 1, "department": 1, "shift": 1, "embeddings": 1}
                ))

                self.employee_embeddings = []
                for employee in employees:
                    embeddings = employee.get('embeddings', [])
                    if embeddings:
                        avg_embedding = np.mean(embeddings, axis=0).astype(np.float32)
                        self.employee_embeddings.append({
                            'embedding': avg_embedding,
                            'employeeId': employee.get('employeeId'),
                            'employeeName': employee.get('employeeName'),
                            'department': employee.get('department'),
                            'shift': employee.get('shift')
                        })

                self.last_update = current_time
                logger.info(f"Cache refreshed with {len(self.employee_embeddings)} employees")

        return self.employee_embeddings


# Global embedding cache instance
embedding_cache = EmbeddingCache()


def find_best_match_optimized(query_embedding, employees_col, threshold=0.6):
    """Optimized database search with caching"""
    cached_embeddings = embedding_cache.get_embeddings(employees_col)

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


@demo_session_bp.route("/api/demo/recognize", methods=["POST"])
def demo_recognize_optimized():
    """OPTIMIZED face recognition endpoint for employee identification"""
    start_time = time.time()

    model_manager = current_app.config.get("MODEL_MANAGER")
    if not model_manager or not model_manager.is_ready():
        logger.error("Models not ready")
        return jsonify({
            "success": False,
            "error": "Face recognition models not initialized"
        }), 503

    detector = model_manager.get_detector()

    data = request.get_json()
    db = current_app.config.get("DB")
    employees_col = db.employees
    threshold = float(current_app.config.get("THRESHOLD", "0.6"))

    image_b64 = data.get("image", "")
    if image_b64.startswith("data:"):
        image_b64 = image_b64.split(",", 1)[1]

    try:
        rgb = read_image_from_bytes_optimized(base64.b64decode(image_b64))
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        return jsonify({"success": False, "error": "Invalid base64 image"}), 400

    detection_start = time.time()
    faces = detect_faces_rgb_optimized(rgb, detector)
    detection_time = time.time() - detection_start

    if len(faces) == 0:
        return jsonify({
            "success": True,
            "faces": [],
            "processing_time": round(time.time() - start_time, 3),
            "detection_time": round(detection_time, 3)
        })

    results = []

    for f in faces:
        embedding_start = time.time()
        emb = extract_embedding_optimized(f["face"])
        embedding_time = time.time() - embedding_start

        if emb is None:
            results.append({
                "match": None,
                "distance": None,
                "box": f["box"],
                "error": "Failed to extract embedding"
            })
            continue

        search_start = time.time()
        best_match, min_distance = find_best_match_optimized(emb, employees_col, threshold)
        search_time = time.time() - search_start

        if best_match:
            results.append({
                "match": {
                    "employee_id": best_match["employeeId"],
                    "employee_name": best_match["employeeName"],
                    "department": best_match["department"],
                    "shift": best_match.get("shift", "")
                },
                "distance": round(float(min_distance), 4),
                "confidence": round((1 - min_distance) * 100, 1),
                "box": f["box"],
                "timing": {
                    "embedding": round(embedding_time, 3),
                    "search": round(search_time, 3)
                }
            })
        else:
            results.append({
                "match": None,
                "distance": round(float(min_distance), 4),
                "box": f["box"],
                "timing": {
                    "embedding": round(embedding_time, 3),
                    "search": round(search_time, 3)
                }
            })

    total_time = time.time() - start_time

    return jsonify({
        "success": True,
        "faces": results,
        "processing_time": round(total_time, 3),
        "detailed_timing": {
            "detection": round(detection_time, 3),
            "total": round(total_time, 3)
        },
        "performance_info": {
            "models_preloaded": True,
            "cache_enabled": True
        }
    })


@demo_session_bp.route('/api/demo/session', methods=['POST'])
def create_demo_session():
    """Create a new demo attendance session"""
    db = current_app.config.get("DB")
    demo_sessions_col = db.demo_sessions

    session_data = {
        "session_id": f"demo_{int(time.time())}",
        "started_at": time.time(),
        "status": "active",
        "recognitions": []
    }

    result = demo_sessions_col.insert_one(session_data)
    session_data['_id'] = str(result.inserted_id)

    return jsonify({
        "success": True,
        "session": session_data
    })


@demo_session_bp.route('/api/demo/session/<session_id>/log', methods=['POST'])
def log_recognition(session_id):
    """Log recognition result to session"""
    db = current_app.config.get("DB")
    demo_sessions_col = db.demo_sessions

    data = request.get_json()
    recognition_log = {
        "timestamp": time.time(),
        "result": data.get('result'),
        "confidence": data.get('confidence'),
        "processing_time": data.get('processing_time')
    }

    demo_sessions_col.update_one(
        {"session_id": session_id},
        {"$push": {"recognitions": recognition_log}}
    )

    return jsonify({"success": True, "message": "Recognition logged"})


@demo_session_bp.route('/api/demo/models/status', methods=['GET'])
def model_status():
    """Check face recognition model status"""
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
        "timestamp": time.time()
    })