"""
Test script for real face training and recognition
Tests the new training and recognition implementation
"""
import requests
import json
import os

BASE_URL = 'http://localhost:5000'

def test_real_training():
    """Test real face training endpoint"""
    print("\n" + "="*60)
    print("Testing REAL Face Training - POST /api/camera/train")
    print("="*60)
    
    # Check if we have any employee images
    images_dir = os.path.join(os.path.dirname(__file__), 'data', 'employee_images')
    images_dir = os.path.abspath(images_dir)
    print(f"Checking for employee images in: {images_dir}")
    if not os.path.exists(images_dir):
        print("❌ No employee images directory found")
        print("   Please capture images first using POST /api/camera/capture")
        return False
    
    # List available employees
    employees = [d for d in os.listdir(images_dir) if os.path.isdir(os.path.join(images_dir, d))]
    if not employees:
        print("❌ No employee directories found")
        print("   Please capture images first using POST /api/camera/capture")
        return False
    
    print(f"Found employee directories: {employees}")
    
    # Test training for all employees
    try:
        print("\n🔄 Starting training for all employees...")
        response = requests.post(
            f'{BASE_URL}/api/camera/train',
            json={},
            timeout=60  # Training can take time
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and result.get('success'):
            print("✅ Real training completed successfully!")
            
            # Check if encodings file was created
            encodings_file = result.get('encodings_file')
            if not encodings_file:
                encodings_file = os.path.join(os.path.dirname(__file__), 'data', 'face_encodings.pkl')
                encodings_file = os.path.abspath(encodings_file)
            
            print(f"Checking encodings file: {encodings_file}")
            if os.path.exists(encodings_file):
                print(f"✅ Encodings file created: {encodings_file}")
                
                # Check file size
                file_size = os.path.getsize(encodings_file)
                print(f"   File size: {file_size} bytes")
                
                return True
            else:
                print(f"❌ Encodings file not found: {encodings_file}")
                return False
        else:
            print("❌ Training failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_recognition_after_training():
    """Test face recognition after training"""
    print("\n" + "="*60)
    print("Testing Face Recognition - POST /api/attendance/start")
    print("="*60)
    
    try:
        print("🔄 Testing face recognition...")
        response = requests.post(
            f'{BASE_URL}/api/attendance/start',
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200:
            if result.get('face_detected'):
                if result.get('employee_recognized'):
                    employee = result.get('employee', {})
                    confidence = employee.get('confidence', 0)
                    print(f"✅ Employee recognized: {employee.get('employeeName')} (confidence: {confidence}%)")
                else:
                    print("⚠️  Face detected but no employee recognized")
            else:
                print("ℹ️  No face detected (normal if no one in front of camera)")
            return True
        else:
            print("❌ Recognition test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_encodings_file():
    """Test if encodings file exists and is valid"""
    print("\n" + "="*60)
    print("Testing Face Encodings File")
    print("="*60)
    
    encodings_file = os.path.join(os.path.dirname(__file__), 'data', 'face_encodings.pkl')
    encodings_file = os.path.abspath(encodings_file)
    print(f"Checking encodings file: {encodings_file}")
    
    if os.path.exists(encodings_file):
        print(f"✅ Encodings file exists: {encodings_file}")
        
        try:
            import pickle
            with open(encodings_file, 'rb') as f:
                encodings = pickle.load(f)
            
            print(f"✅ Encodings loaded successfully")
            print(f"   Number of employees: {len(encodings)}")
            
            for emp_id, data in encodings.items():
                embedding_len = len(data.get('embedding', []))
                num_images = data.get('num_images', 0)
                trained_at = data.get('trained_at', 'Unknown')
                print(f"   - {emp_id}: {embedding_len}D embedding from {num_images} images (trained: {trained_at})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading encodings: {e}")
            return False
    else:
        print(f"❌ Encodings file not found: {encodings_file}")
        return False


def test_health():
    """Test server health"""
    print("\n" + "="*60)
    print("Testing Server Health - GET /health")
    print("="*60)
    
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Server is healthy!")
            return True
        else:
            print("❌ Server health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n⚠️  Make sure the backend server is running:")
        print("   cd backend")
        print("   python app_simple.py")
        return False


if __name__ == '__main__':
    print("\n" + "="*60)
    print("REAL FACE TRAINING & RECOGNITION TESTS")
    print("="*60)
    print("\nMake sure backend server is running on http://localhost:5000")
    print("Run: cd backend && python app_simple.py")
    
    # Test sequence
    tests_passed = 0
    total_tests = 4
    
    # 1. Health check
    if test_health():
        tests_passed += 1
    
    # 2. Training test
    if test_real_training():
        tests_passed += 1
    
    # 3. Encodings file test
    if test_encodings_file():
        tests_passed += 1
    
    # 4. Recognition test
    if test_recognition_after_training():
        tests_passed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Real face training and recognition is working!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n" + "="*60)