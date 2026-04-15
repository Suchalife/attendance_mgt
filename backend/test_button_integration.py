"""
Test script for button integration endpoints
Tests the new capture and train endpoints
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_camera_capture():
    """Test image capture endpoint"""
    print("\n" + "="*50)
    print("Testing POST /api/camera/capture")
    print("="*50)
    
    # Test data
    data = {
        'employeeId': 'EMP-001',
        'numImages': 5
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/camera/capture',
            json=data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Capture endpoint working!")
        else:
            print("❌ Capture endpoint failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_camera_train():
    """Test model training endpoint"""
    print("\n" + "="*50)
    print("Testing POST /api/camera/train")
    print("="*50)
    
    # Test data (optional employeeId)
    data = {
        'employeeId': 'EMP-001'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/camera/train',
            json=data,
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Train endpoint working!")
        else:
            print("❌ Train endpoint failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_camera_train_all():
    """Test model training for all employees"""
    print("\n" + "="*50)
    print("Testing POST /api/camera/train (all employees)")
    print("="*50)
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/camera/train',
            json={},
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Train all endpoint working!")
        else:
            print("❌ Train all endpoint failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_health():
    """Test health endpoint"""
    print("\n" + "="*50)
    print("Testing GET /health")
    print("="*50)
    
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Server is healthy!")
        else:
            print("❌ Server health check failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n⚠️  Make sure the backend server is running:")
        print("   cd backend")
        print("   python app_simple.py")


if __name__ == '__main__':
    print("\n" + "="*50)
    print("BUTTON INTEGRATION ENDPOINT TESTS")
    print("="*50)
    print("\nMake sure backend server is running on http://localhost:5000")
    print("Run: cd backend && python app_simple.py")
    
    # Run tests
    test_health()
    
    print("\n\n⚠️  NOTE: The following tests require a camera to be connected")
    print("If no camera is available, they will fail gracefully\n")
    
    input("Press Enter to continue with camera tests...")
    
    test_camera_capture()
    test_camera_train()
    test_camera_train_all()
    
    print("\n" + "="*50)
    print("TESTS COMPLETE")
    print("="*50)
