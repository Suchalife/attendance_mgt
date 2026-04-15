#!/usr/bin/env python3
"""
Test script to verify Step 1: Field Name Mismatch Fix
Tests that backend accepts both camelCase and PascalCase formats
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_employee_registration_camelcase():
    """Test employee registration with camelCase (frontend format)"""
    print("\n" + "="*60)
    print("TEST 1: Employee Registration (camelCase)")
    print("="*60)
    
    data = {
        "employeeId": "EMP-TEST-001",
        "employeeName": "John Doe",
        "department": "IT",
        "shift": "Morning"
    }
    
    print(f"Request: POST {BASE_URL}/api/employees")
    print(f"Payload: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(f'{BASE_URL}/api/employees', json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Employee created with camelCase format")
            return True
        else:
            print("❌ FAILED: Unexpected status code")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_employee_registration_pascalcase():
    """Test employee registration with PascalCase (backward compatibility)"""
    print("\n" + "="*60)
    print("TEST 2: Employee Registration (PascalCase - Backward Compatibility)")
    print("="*60)
    
    data = {
        "EmployeeID": "EMP-TEST-002",
        "EmployeeName": "Jane Smith",
        "Department": "HR",
        "Shift": "Evening"
    }
    
    print(f"Request: POST {BASE_URL}/api/employees")
    print(f"Payload: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(f'{BASE_URL}/api/employees', json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ SUCCESS: Employee created with PascalCase format")
            return True
        else:
            print("❌ FAILED: Unexpected status code")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_get_employees():
    """Test getting all employees (should return camelCase)"""
    print("\n" + "="*60)
    print("TEST 3: Get All Employees (Should Return camelCase)")
    print("="*60)
    
    print(f"Request: GET {BASE_URL}/api/employees")
    
    try:
        response = requests.get(f'{BASE_URL}/api/employees')
        print(f"\nStatus Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            # Check if employees are in camelCase format
            if data.get('employees') and len(data['employees']) > 0:
                first_emp = data['employees'][0]
                has_camelcase = 'employeeId' in first_emp and 'employeeName' in first_emp
                
                if has_camelcase:
                    print("✅ SUCCESS: Employees returned in camelCase format")
                    return True
                else:
                    print("❌ FAILED: Employees not in camelCase format")
                    print(f"   Keys found: {list(first_emp.keys())}")
                    return False
            else:
                print("⚠️  WARNING: No employees found (might be expected)")
                return True
        else:
            print("❌ FAILED: Unexpected status code")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_attendance_mark_camelcase():
    """Test manual attendance marking with camelCase"""
    print("\n" + "="*60)
    print("TEST 4: Mark Attendance (camelCase)")
    print("="*60)
    
    data = {
        "employeeId": "EMP-TEST-001",
        "employeeName": "John Doe",
        "department": "IT",
        "status": "Present"
    }
    
    print(f"Request: POST {BASE_URL}/api/attendance/mark")
    print(f"Payload: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(f'{BASE_URL}/api/attendance/mark', json=data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Attendance marked with camelCase format")
            return True
        else:
            print("❌ FAILED: Unexpected status code")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("STEP 1: FIELD NAME MISMATCH FIX - VERIFICATION TESTS")
    print("="*60)
    print("\nMake sure Flask backend is running on http://localhost:5000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    results = []
    
    # Run tests
    results.append(("Employee Registration (camelCase)", test_employee_registration_camelcase()))
    results.append(("Employee Registration (PascalCase)", test_employee_registration_pascalcase()))
    results.append(("Get Employees (camelCase response)", test_get_employees()))
    results.append(("Mark Attendance (camelCase)", test_attendance_mark_camelcase()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Step 1 is complete.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")


if __name__ == '__main__':
    main()
