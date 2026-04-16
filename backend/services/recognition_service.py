"""
Recognition Service for face detection and recognition
Real implementation using MTCNN for face detection and DeepFace for recognition
"""
import cv2
import numpy as np
import os
import pickle
from deepface import DeepFace
from mtcnn import MTCNN
from scipy.spatial.distance import cosine


class RecognitionService:
    """Service for face detection and recognition"""
    
    def __init__(self):
        # Load Haar Cascade classifier for face detection (fallback)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Initialize MTCNN detector for better face detection
        try:
            self.mtcnn_detector = MTCNN()
            self.use_mtcnn = True
            print("MTCNN detector loaded successfully")
        except Exception as e:
            print(f"Error loading MTCNN: {e}, falling back to Haar Cascade")
            self.mtcnn_detector = None
            self.use_mtcnn = False
        
        if self.face_cascade.empty():
            print("Error: Could not load Haar Cascade classifier")
        else:
            print("Haar Cascade classifier loaded successfully")
        
        # Load face encodings
        self.face_encodings = self.load_face_encodings()
        print(f"Loaded face encodings for {len(self.face_encodings)} employees")
    
    def load_face_encodings(self):
        """Load face encodings from pickle file"""
        encodings_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'face_encodings.pkl')
        encodings_file = os.path.abspath(encodings_file)
        print(f"Loading face encodings from: {encodings_file}")
        
        if os.path.exists(encodings_file):
            try:
                with open(encodings_file, 'rb') as f:
                    encodings = pickle.load(f)
                print(f"Loaded face encodings from {encodings_file}")
                return encodings
            except Exception as e:
                print(f"Error loading face encodings: {e}")
                return {}
        else:
            print("No face encodings file found. Train the model first.")
            return {}
    
    def reload_face_encodings(self):
        """Reload face encodings (call after training)"""
        self.face_encodings = self.load_face_encodings()
        print(f"Reloaded face encodings for {len(self.face_encodings)} employees")
    
    def detect_faces(self, image):
        """
        Detect faces in an image using MTCNN (preferred) or Haar Cascade (fallback)
        
        Args:
            image: numpy array (BGR format from OpenCV)
        
        Returns:
            list: List of face bounding boxes [(x, y, w, h), ...]
        """
        if image is None:
            return []
        
        try:
            if self.use_mtcnn and self.mtcnn_detector:
                # Use MTCNN for better face detection
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                faces = self.mtcnn_detector.detect_faces(rgb_image)
                
                # Convert MTCNN format to (x, y, w, h) format
                face_boxes = []
                for face in faces:
                    if face['confidence'] > 0.9:  # High confidence only
                        x, y, w, h = face['box']
                        face_boxes.append((x, y, w, h))
                
                return face_boxes
            else:
                # Fallback to Haar Cascade
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                return faces.tolist() if len(faces) > 0 else []
                
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def extract_face_embedding(self, face_image):
        """
        Extract face embedding using DeepFace
        
        Args:
            face_image: numpy array (RGB format) of cropped face
        
        Returns:
            numpy array: 512-dimensional face embedding or None if failed
        """
        try:
            if face_image.shape[0] < 50 or face_image.shape[1] < 50:
                return None
            
            # Extract embedding using DeepFace Facenet512
            embedding = DeepFace.represent(
                face_image,
                model_name='Facenet512',
                detector_backend='skip',  # Skip detection since face is already cropped
                enforce_detection=False
            )
            
            if embedding and len(embedding) > 0:
                return np.array(embedding[0]['embedding'])
            else:
                return None
                
        except Exception as e:
            print(f"Error extracting face embedding: {e}")
            return None
    
    def find_best_match(self, query_embedding, threshold=0.3):
        """
        Find the best matching employee for a query embedding
        
        Args:
            query_embedding: numpy array of face embedding
            threshold: similarity threshold (lower = more similar)
        
        Returns:
            tuple: (employee_id, distance) or (None, float('inf')) if no match
        """
        if len(self.face_encodings) == 0:
            return None, float('inf')
        
        best_match = None
        min_distance = float('inf')
        
        for employee_id, employee_data in self.face_encodings.items():
            stored_embedding = np.array(employee_data['embedding'])
            
            # Calculate cosine distance
            distance = cosine(query_embedding, stored_embedding)
            
            if distance < min_distance:
                min_distance = distance
                best_match = employee_id
        
        # Return match only if distance is below threshold
        if min_distance < threshold:
            return best_match, min_distance
        else:
            return None, min_distance
    
    def detect_face_from_frame(self, frame_bytes):
        """
        Detect face from JPEG frame bytes
        
        Args:
            frame_bytes: JPEG encoded frame as bytes
        
        Returns:
            tuple: (success, face_count, faces)
                - success: bool indicating if detection was successful
                - face_count: number of faces detected
                - faces: list of face bounding boxes
        """
        if frame_bytes is None:
            return False, 0, []
        
        try:
            # Decode JPEG bytes to image
            nparr = np.frombuffer(frame_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return False, 0, []
            
            # Detect faces
            faces = self.detect_faces(image)
            
            return True, len(faces), faces
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return False, 0, []
    
    def recognize_employee(self, frame_bytes, employees):
        """
        Recognize employee from frame using real face recognition
        
        Args:
            frame_bytes: JPEG encoded frame as bytes
            employees: list of employee dictionaries (camelCase format)
        
        Returns:
            dict: Recognition result with keys:
                - success: bool
                - face_detected: bool
                - employee_id: str or None
                - employee_name: str or None
                - department: str or None
                - confidence: float (0-100)
                - message: str
        """
        # Detect face
        success, face_count, faces = self.detect_face_from_frame(frame_bytes)
        
        if not success:
            return {
                'success': False,
                'face_detected': False,
                'employee_id': None,
                'employee_name': None,
                'department': None,
                'confidence': 0.0,
                'message': 'Failed to process frame'
            }
        
        if face_count == 0:
            return {
                'success': True,
                'face_detected': False,
                'employee_id': None,
                'employee_name': None,
                'department': None,
                'confidence': 0.0,
                'message': 'No face detected'
            }
        
        # Check if we have trained encodings
        if len(self.face_encodings) == 0:
            return {
                'success': True,
                'face_detected': True,
                'employee_id': None,
                'employee_name': None,
                'department': None,
                'confidence': 0.0,
                'message': 'No trained face encodings found. Please train the model first.'
            }
        
        try:
            # Decode frame to image
            nparr = np.frombuffer(frame_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process the first detected face
            x, y, w, h = faces[0]  # Use first face
            face_img = rgb_image[y:y+h, x:x+w]
            
            # Extract embedding from detected face
            query_embedding = self.extract_face_embedding(face_img)
            
            if query_embedding is None:
                return {
                    'success': True,
                    'face_detected': True,
                    'employee_id': None,
                    'employee_name': None,
                    'department': None,
                    'confidence': 0.0,
                    'message': 'Failed to extract face embedding'
                }
            
            # Find best match
            best_employee_id, distance = self.find_best_match(query_embedding)
            
            if best_employee_id is None:
                return {
                    'success': True,
                    'face_detected': True,
                    'employee_id': None,
                    'employee_name': None,
                    'department': None,
                    'confidence': 0.0,
                    'message': 'Face detected but no matching employee found'
                }
            
            # Find employee details from the employees list
            employee_details = None
            for emp in employees:
                emp_id = emp.get('employeeId') or emp.get('EmployeeID')
                if emp_id == best_employee_id:
                    employee_details = emp
                    break
            
            if employee_details is None:
                return {
                    'success': True,
                    'face_detected': True,
                    'employee_id': best_employee_id,
                    'employee_name': 'Unknown',
                    'department': 'Unknown',
                    'confidence': round((1 - distance) * 100, 1),
                    'message': f'Recognized employee {best_employee_id} but details not found in employee list'
                }
            
            # Extract employee details (accept both camelCase and PascalCase)
            employee_name = employee_details.get('employeeName') or employee_details.get('EmployeeName')
            department = employee_details.get('department') or employee_details.get('Department')
            
            confidence = round((1 - distance) * 100, 1)
            
            return {
                'success': True,
                'face_detected': True,
                'employee_id': best_employee_id,
                'employee_name': employee_name,
                'department': department,
                'confidence': confidence,
                'message': f'Employee recognized: {employee_name} (confidence: {confidence}%)'
            }
            
        except Exception as e:
            print(f"Error in face recognition: {e}")
            return {
                'success': False,
                'face_detected': True,
                'employee_id': None,
                'employee_name': None,
                'department': None,
                'confidence': 0.0,
                'message': f'Error during recognition: {str(e)}'
            }
    
    def draw_faces(self, image, faces):
        """
        Draw rectangles around detected faces (utility for testing)
        
        Args:
            image: numpy array (BGR format)
            faces: list of face bounding boxes [(x, y, w, h), ...]
        
        Returns:
            numpy array: image with rectangles drawn
        """
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        return image


# Global recognition service instance
recognition_service = RecognitionService()


def reload_recognition_encodings():
    """
    Reload face encodings in the global recognition service
    Call this after training to update the recognition system
    """
    global recognition_service
    recognition_service.reload_face_encodings()
