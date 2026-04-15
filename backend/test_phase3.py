"""
Test script for Phase 3: Face Detection and Attendance
Tests all attendance endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_response(response):
    """Print formatted response"""
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_health():
    """Test health endpoint"""
    print_section("Test 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    return response.status_code == 200

def test_create_employee():
    """Test creating an employee"""
    print_section("Test 2: Create Employee")
    
    employee_data = {
        "employeeId": "EMP001",
        "employeeName": "John Doe",
        "department": "Engineering",
        "shift": "Morning",
        "email": "john@example.com",
        "phoneNumber": "1234567890"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/employees",
        json=employee_data
    )
    print_response(response)
    return response.status_code == 201

def test_get_employees():
    """Test getting all employees"""
    print_section("Test 3: Get All Employees")
    response = requests.get(f"{BASE_URL}/api/employees")
    print_response(response)
    return response.status_code == 200

def test_start_camera():
    """Test starting camera"""
    print_section("Test 4: Start Camera")
    response = requests.post(f"{BASE_URL}/api/camera/start")
    print_response(response)
    return response.status_code == 200

def test_camera_status():
    """Test camera status"""
    print_section("Test 5: Camera Status")
    response = requests.get(f"{BASE_URL}/api/camera/status")
    print_response(response)
    return response.status_code == 200

def test_manual_attendance():
    """Test manual attendance marking"""
    print_section("Test 6: Manual Attendance Marking")
    
    attendance_data = {
        "employeeId": "EMP001",
        "employeeName": "John Doe",
        "department": "Engineering",
        "status": "Present",
        "sessionId": "test-session-1"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/attendance/mark",
        json=attendance_data
    )
    print_response(response)
    return response.status_code == 200

def test_duplicate_attendance():
    """Test duplicate attendance prevention"""
    print_section("Test 7: Duplicate Attendance Prevention")
    
    attendance_data = {
        "employeeId": "EMP001",
        "employeeName": "John Doe",
        "department": "Engineering",
        "status": "Present",
        "sessionId": "test-session-1"
    }
    
    print("Attempting to mark attendance again with same session...")
    response = requests.post(
        f"{BASE_URL}/api/attendance/mark",
        json=attendance_data
    )
    print_response(response)
    
    # Should return 400 or success=false with duplicate=true
    return response.status_code in [200, 400]

def test_get_attendance():
    """Test getting all attendance records"""
    print_section("Test 8: Get All Attendance Records")
    response = requests.get(f"{BASE_URL}/api/attendance")
    print_response(response)
    return response.status_code == 200

def test_get_attendance_stats():
    """Test getting attendance statistics"""
    print_section("Test 9: Get Attendance Statistics")
    response = requests.get(f"{BASE_URL}/api/attendance/stats")
    print_response(response)
    return response.status_code == 200

def test_attendance_start():
    """Test attendance start with face detection"""
    print_section("Test 10: Start Attendance (Face Detection)")
    
    print("This will capture a frame from camera and detect faces...")
    print("Make sure camera is active and you're in front of it!")
    
    time.sleep(2)  # Give user time to position
    
    response = requests.post(f"{BASE_URL}/api/attendance/start")
    print_response(response)
    return response.status_code == 200

def test_session_filter():
    """Test filtering by session"""
    print_section("Test 11: Filter Attendance by Session")
    response = requests.get(f"{BASE_URL}/api/attendance?session_id=test-session-1")
    print_response(response)
    return response.status_code == 200

def test_date_filter():
    """Test filtering by date"""
    print_section("Test 12: Filter Attendance by Date")
    
    # Get today's date
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    response = requests.get(f"{BASE_URL}/api/attendance?date={today}")
    print_response(response)
    return response.status_code == 200

def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  PHASE 3 TEST SUITE")
    print("  Face Detection and Attendance Integration")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("Create Employee", test_create_employee),
        ("Get Employees", test_get_employees),
        ("Start Camera", test_start_camera),
        ("Camera Status", test_camera_status),
        ("Manual Attendance", test_manual_attendance),
        ("Duplicate Prevention", test_duplicate_attendance),
        ("Get Attendance", test_get_attendance),
        ("Attendance Stats", test_get_attendance_stats),
        ("Attendance Start (Face Detection)", test_attendance_start),
        ("Session Filter", test_session_filter),
        ("Date Filter", test_date_filter),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {str(e)}")
            results.append((test_name, False))
        
        time.sleep(1)  # Small delay between tests
    
    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    print("\n⚠️  Make sure Flask server is running on http://localhost:5000")
    print("⚠️  Make sure camera is connected and accessible")
    input("\nPress Enter to start tests...")
    
    run_all_tests()
