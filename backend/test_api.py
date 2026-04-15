"""
Simple test script to verify Phase 1 API endpoints
Run this after starting the Flask server
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("\n1. Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.status_code == 200

def test_create_employee():
    """Test creating an employee"""
    print("\n2. Testing Create Employee...")
    employee_data = {
        "EmployeeID": "EMP-TEST-001",
        "EmployeeName": "Test Employee",
        "Department": "Sorting",
        "Shift": "Day"
    }
    response = requests.post(
        f"{BASE_URL}/api/employees",
        json=employee_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201

def test_create_duplicate():
    """Test creating duplicate employee (should fail)"""
    print("\n3. Testing Duplicate Employee (should fail)...")
    employee_data = {
        "EmployeeID": "EMP-TEST-001",
        "EmployeeName": "Duplicate Employee",
        "Department": "Logistics"
    }
    response = requests.post(
        f"{BASE_URL}/api/employees",
        json=employee_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 400

def test_missing_fields():
    """Test creating employee with missing fields (should fail)"""
    print("\n4. Testing Missing Required Fields (should fail)...")
    employee_data = {
        "EmployeeID": "EMP-TEST-002"
        # Missing EmployeeName and Department
    }
    response = requests.post(
        f"{BASE_URL}/api/employees",
        json=employee_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 400

def test_get_employees():
    """Test getting all employees"""
    print("\n5. Testing Get All Employees...")
    response = requests.get(f"{BASE_URL}/api/employees")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Count: {data.get('count')}")
    print(f"   Employees: {json.dumps(data.get('employees'), indent=2)}")
    return response.status_code == 200

def test_get_count():
    """Test getting employee count"""
    print("\n6. Testing Get Employee Count...")
    response = requests.get(f"{BASE_URL}/api/employees/count")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 1 API Test Suite")
    print("=" * 60)
    print("\nMake sure Flask server is running on http://localhost:5000")
    print("Run: python app_simple.py")
    
    input("\nPress Enter to start tests...")
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Create Employee", test_create_employee()))
    results.append(("Duplicate Check", test_create_duplicate()))
    results.append(("Missing Fields Check", test_missing_fields()))
    results.append(("Get All Employees", test_get_employees()))
    results.append(("Get Employee Count", test_get_count()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    print("=" * 60)
