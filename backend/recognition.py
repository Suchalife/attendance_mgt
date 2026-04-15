import os
import cv2
from mtcnn import MTCNN
from deepface import DeepFace
from pymongo import MongoClient
from scipy.spatial.distance import cosine
import numpy as np
import time
from dotenv import load_dotenv

load_dotenv()

# ----------------- MongoDB Setup -----------------
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGODB_URI)
db = client['ecorecycle_ams_db']
collection = db['employees']

DEPARTMENTS = [
    "Sorting", "Shredding", "Processing",
    "Packaging", "Logistics", "Quality Control", "Administration"
]

# ----------------- Face Detector -----------------
detector = MTCNN()


# ----------------- Detect Faces -----------------
def detect_faces(image):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    faces = detector.detect_faces(rgb_image)
    face_data = []
    for face in faces:
        x, y, w, h = face['box']
        x, y = max(0, x), max(0, y)
        face_img = rgb_image[y:y+h, x:x+w]
        face_data.append({'box': (x, y, w, h), 'face': face_img})
    return face_data


# ----------------- Extract Embedding -----------------
def extract_embedding(face_img):
    try:
        embedding = DeepFace.represent(face_img, model_name='Facenet512', detector_backend='skip')
        return embedding[0]['embedding']
    except Exception as e:
        print("Error extracting embedding:", e)
        return None


# ----------------- Register Employee -----------------
def register_employee(employee_id, employee_name, department, shift="Morning", wait_time=5):
    """
    Automatically captures a face from webcam and registers the employee.
    wait_time: Seconds to wait before registering (to stabilize face).
    """
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print(f"Looking for {employee_name}'s face. Please look at the camera for {wait_time} seconds...")

    start_time = time.time()
    registered = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        faces = detect_faces(frame)
        if len(faces) == 1:
            x, y, w, h = faces[0]['box']
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Face detected", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            if time.time() - start_time > wait_time:
                embedding = extract_embedding(faces[0]['face'])
                if embedding is not None:
                    employee_data = {
                        'employee_id': employee_id,
                        'employee_name': employee_name,
                        'department': department,
                        'shift': shift,
                        'embedding': embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
                    }
                    collection.insert_one(employee_data)
                    print(f"Employee {employee_name} registered successfully in {department} department.")
                    registered = True
                    break
        else:
            cv2.putText(frame, f"{len(faces)} faces detected. Show only one face.", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            start_time = time.time()  # Reset timer if face not stable

        cv2.imshow("EcoRecycle - Employee Registration", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if not registered:
        print("Registration failed. Please try again.")


# ----------------- Live Recognition -----------------
def live_recognition():
    employees = list(collection.find())
    if not employees:
        print("No employees registered.")
        return

    threshold = 0.7  # Cosine similarity threshold

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("Starting live recognition. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        faces = detect_faces(frame)

        for face_data in faces:
            x, y, w, h = face_data['box']
            face_img = face_data['face']
            embedding = extract_embedding(face_img)
            if embedding is None:
                continue

            best_match = None
            min_distance = float('inf')

            for employee in employees:
                stored_embedding = employee['embedding']
                distance = cosine(embedding, stored_embedding)
                if distance < min_distance:
                    min_distance = distance
                    best_match = employee

            if min_distance < threshold:
                emp_name = best_match.get('employee_name', 'Unknown')
                emp_dept = best_match.get('department', '')
                display_text = f"{emp_name} | {emp_dept} ({min_distance:.2f})"
                color = (0, 255, 0)  # Green for recognized
            else:
                display_text = "Unknown Employee"
                color = (0, 0, 255)  # Red for unrecognized

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, display_text, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("EcoRecycle - Live Employee Recognition", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# ----------------- Main Menu -----------------
def main():
    while True:
        print("\n=== EcoRecycle Employee Face Recognition System ===")
        print("1. Register Employee")
        print("2. Start Live Recognition")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            employee_id = input("Enter Employee ID: ")
            employee_name = input("Enter Employee Name: ")
            print("Available Departments:", ", ".join(DEPARTMENTS))
            department = input("Enter Department: ")
            shift = input("Enter Shift (Morning/Evening/Night): ")
            register_employee(employee_id, employee_name, department, shift)
        elif choice == '2':
            live_recognition()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
