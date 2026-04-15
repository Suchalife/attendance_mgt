"""
Camera Routes
Handles camera streaming and control
"""
from flask import Blueprint, Response, jsonify, request
from services.camera_service import camera_service
from services.csv_service import CSVService
from services.recognition_service import reload_recognition_encodings
import os
import cv2
import numpy as np
import pickle
from datetime import datetime
from deepface import DeepFace
from mtcnn import MTCNN

camera_bp = Blueprint('camera', __name__)
csv_service = CSVService()

# Initialize MTCNN detector for face detection
mtcnn_detector = MTCNN()


@camera_bp.route('/api/camera/stream', methods=['GET'])
def stream_camera():
    """
    Stream camera feed using MJPEG
    Returns multipart response with JPEG frames
    """
    try:
        # Check if camera is available
        if not camera_service.is_camera_active():
            if not camera_service.start_camera():
                return jsonify({
                    'success': False,
                    'error': 'Camera not accessible. Please check camera connection.'
                }), 500
        
        return Response(
            camera_service.generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Camera streaming error: {str(e)}'
        }), 500


@camera_bp.route('/api/camera/start', methods=['POST'])
def start_camera():
    """
    Start camera
    Returns success/error response
    """
    try:
        success = camera_service.start_camera()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Camera started successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start camera. Please check camera connection.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error starting camera: {str(e)}'
        }), 500


@camera_bp.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    """
    Stop camera and release resources
    Returns success/error response
    """
    try:
        success = camera_service.stop_camera()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Camera stopped successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to stop camera'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error stopping camera: {str(e)}'
        }), 500


@camera_bp.route('/api/camera/status', methods=['GET'])
def camera_status():
    """
    Get camera status
    Returns camera active status
    """
    try:
        is_active = camera_service.is_camera_active()
        
        return jsonify({
            'success': True,
            'active': is_active,
            'message': 'Camera is active' if is_active else 'Camera is inactive'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error checking camera status: {str(e)}'
        }), 500



@camera_bp.route('/api/camera/capture', methods=['POST'])
def capture_images():
    """
    Capture images for employee enrollment
    
    Request body:
        {
            "employeeId": "string",
            "numImages": number (optional, default 10)
        }
    
    Returns:
        JSON response with capture result
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Get employee ID
        employee_id = data.get('employeeId') or data.get('EmployeeID')
        num_images = data.get('numImages', 10)
        
        if not employee_id:
            return jsonify({
                'success': False,
                'error': 'Missing required field: employeeId'
            }), 400
        
        # Check if camera is active
        if not camera_service.is_camera_active():
            if not camera_service.start_camera():
                return jsonify({
                    'success': False,
                    'error': 'Camera not available'
                }), 500
        
        # Create directory for employee images
        images_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'employee_images', employee_id)
        images_dir = os.path.abspath(images_dir)
        print(f"Creating employee images directory: {images_dir}")
        os.makedirs(images_dir, exist_ok=True)
        
        # Capture images
        captured_count = 0
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for i in range(num_images):
            frame_bytes = camera_service.get_frame()
            
            if frame_bytes is None:
                continue
            
            # Decode frame
            nparr = np.frombuffer(frame_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is not None:
                # Save image
                filename = f"{employee_id}_{timestamp}_{i+1}.jpg"
                filepath = os.path.join(images_dir, filename)
                cv2.imwrite(filepath, image)
                captured_count += 1
        
        if captured_count > 0:
            return jsonify({
                'success': True,
                'message': f'Captured {captured_count} images for employee {employee_id}',
                'captured': captured_count,
                'directory': images_dir
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to capture any images'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error capturing images: {str(e)}'
        }), 500


@camera_bp.route('/api/camera/train', methods=['POST'])
def train_model():
    """
    Train face recognition model with captured images
    
    Real implementation that:
    1. Loads images from data/employee_images/{employeeId}/
    2. Detects faces using MTCNN
    3. Extracts embeddings using DeepFace Facenet512
    4. Stores embeddings in data/face_encodings.pkl
    
    Request body:
        {
            "employeeId": "string" (optional - if provided, train only for this employee)
        }
    
    Returns:
        JSON response with training result
    """
    try:
        data = request.get_json() or {}
        employee_id = data.get('employeeId') or data.get('EmployeeID')
        
        # Check if employee images directory exists
        images_base_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'employee_images')
        images_base_dir = os.path.abspath(images_base_dir)
        print(f"Looking for employee images in: {images_base_dir}")
        
        if not os.path.exists(images_base_dir):
            return jsonify({
                'success': False,
                'error': 'No employee images found. Please capture images first.'
            }), 400
        
        # Load existing encodings or create new dict
        encodings_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'face_encodings.pkl')
        encodings_file = os.path.abspath(encodings_file)
        print(f"Encodings file path: {encodings_file}")
        if os.path.exists(encodings_file):
            with open(encodings_file, 'rb') as f:
                face_encodings = pickle.load(f)
        else:
            face_encodings = {}
        
        employees_trained = 0
        total_images_processed = 0
        total_faces_detected = 0
        
        # Determine which employees to train
        if employee_id:
            # Train specific employee
            employee_dirs = [employee_id] if os.path.exists(os.path.join(images_base_dir, employee_id)) else []
        else:
            # Train all employees
            employee_dirs = [d for d in os.listdir(images_base_dir) 
                           if os.path.isdir(os.path.join(images_base_dir, d))]
        
        if not employee_dirs:
            return jsonify({
                'success': False,
                'error': f'No images found for employee {employee_id}' if employee_id else 'No employee directories found'
            }), 400
        
        # Process each employee
        for emp_id in employee_dirs:
            employee_dir = os.path.join(images_base_dir, emp_id)
            image_files = [f for f in os.listdir(employee_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if len(image_files) == 0:
                continue
            
            print(f"Training employee {emp_id} with {len(image_files)} images...")
            
            employee_embeddings = []
            images_processed = 0
            faces_detected = 0
            
            for image_file in image_files:
                image_path = os.path.join(employee_dir, image_file)
                
                try:
                    # Load image
                    image = cv2.imread(image_path)
                    if image is None:
                        continue
                    
                    # Convert BGR to RGB for MTCNN
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    # Detect faces using MTCNN
                    faces = mtcnn_detector.detect_faces(rgb_image)
                    
                    images_processed += 1
                    
                    # Process each detected face
                    for face in faces:
                        if face['confidence'] > 0.9:  # High confidence faces only
                            # Extract face region
                            x, y, w, h = face['box']
                            x, y = max(0, x), max(0, y)
                            face_img = rgb_image[y:y+h, x:x+w]
                            
                            # Skip very small faces
                            if face_img.shape[0] < 50 or face_img.shape[1] < 50:
                                continue
                            
                            try:
                                # Extract embedding using DeepFace
                                embedding = DeepFace.represent(
                                    face_img,
                                    model_name='Facenet512',
                                    detector_backend='skip',  # Skip detection since we already detected
                                    enforce_detection=False
                                )
                                
                                if embedding and len(embedding) > 0:
                                    employee_embeddings.append(embedding[0]['embedding'])
                                    faces_detected += 1
                                    
                            except Exception as e:
                                print(f"Error extracting embedding from {image_file}: {e}")
                                continue
                
                except Exception as e:
                    print(f"Error processing image {image_file}: {e}")
                    continue
            
            # Store embeddings for this employee if we got any
            if len(employee_embeddings) > 0:
                # Average the embeddings for better representation
                avg_embedding = np.mean(employee_embeddings, axis=0).tolist()
                face_encodings[emp_id] = {
                    'embedding': avg_embedding,
                    'num_images': len(employee_embeddings),
                    'trained_at': datetime.now().isoformat()
                }
                employees_trained += 1
                print(f"✅ Trained {emp_id}: {len(employee_embeddings)} face embeddings averaged")
            else:
                print(f"❌ No valid faces found for {emp_id}")
            
            total_images_processed += images_processed
            total_faces_detected += faces_detected
        
        if employees_trained == 0:
            return jsonify({
                'success': False,
                'error': 'No valid face embeddings could be extracted from the images'
            }), 400
        
        # Save updated encodings to file
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        data_dir = os.path.abspath(data_dir)
        os.makedirs(data_dir, exist_ok=True)
        print(f"Saving encodings to: {encodings_file}")
        with open(encodings_file, 'wb') as f:
            pickle.dump(face_encodings, f)
        
        # Reload encodings in recognition service
        reload_recognition_encodings()
        
        return jsonify({
            'success': True,
            'message': f'Training completed successfully for {employees_trained} employee(s)',
            'employees_trained': employees_trained,
            'total_images_processed': total_images_processed,
            'total_faces_detected': total_faces_detected,
            'encodings_file': encodings_file,
            'trained_employees': list(face_encodings.keys()) if not employee_id else [employee_id]
        }), 200
        
    except Exception as e:
        print(f"Training error: {e}")
        return jsonify({
            'success': False,
            'error': f'Error during training: {str(e)}'
        }), 500
