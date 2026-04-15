#!/usr/bin/env python3
"""
Test script for Start Attendance button functionality
Tests the /api/attendance/start endpoint
"""

import requests
import json
import time

# API base URL
API_BASE_URL = 'http://localhost:5000'

def test_camera_endpoints():
    """Test camera-related endpoints"""
    print("=== Testing Camera Endpoints ===")
    
    # Test camera status
    try:
        response = requests.get(f'{API_BASE_URL}/api/camera/status')
        print(f"Camera Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Active: {data.get('active', False)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Connection Error: {e}")
    
    # Test start camera
    try:
        response = requests.post(f'{API_BASE_URL}/api/camera/start')
        print(f"Start Camera: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', False)}")
            print(f"  Message: {data.get('message', 'No message')}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Connection Error: {e}")

def test_attendance_start():
    """Test the attendance start endpoint"""
    print("\n=== Testing Attendance Start Endpoint ===")
    
    try:
        response = requests.post(f'{API_BASE_URL}/api/attendance/start')
        print(f"Attendance Start: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', False)}")
            print(f"  Session ID: {data.get('session_id', 'None')}")
            print(f"  Face Detected: {data.get('face_detected', False)}")
            print(f"  Employee Recognized: {data.get('employee_recognized', False)}")
            print(f"  Message: {data.get('message', 'No message')}")
            
            if data.get('employee'):
                emp = data['employee']
                print(f"  Employee: {emp.get('employeeName')} (ID: {emp.get('employeeId')})")
        else:
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"  Connection Error: {e}")

def test_attendance_stats():
    """Test attendance stats endpoint"""
    print("\n=== Testing Attendance Stats ===")
    
    try:
        response = requests.get(f'{API_BASE_URL}/api/attendance/stats')
        print(f"Attendance Stats: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', False)}")
            stats = data.get('stats', {})
            print(f"  Total Employees: {stats.get('total_employees', 0)}")
            print(f"  Present Today: {stats.get('present_today', 0)}")
            print(f"  Absent Today: {stats.get('absent_today', 0)}")
        else:
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"  Connection Error: {e}")

def test_employees_endpoint():
    """Test employees endpoint"""
    print("\n=== Testing Employees Endpoint ===")
    
    try:
        response = requests.get(f'{API_BASE_URL}/api/employees')
        print(f"Get Employees: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data.get('success', False)}")
            employees = data.get('employees', [])
            print(f"  Employee Count: {len(employees)}")
            
            if employees:
                print("  Sample Employee:")
                emp = employees[0]
                print(f"    ID: {emp.get('employeeId')}")
                print(f"    Name: {emp.get('employeeName')}")
                print(f"    Department: {emp.get('department')}")
        else:
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"  Connection Error: {e}")

if __name__ == '__main__':
    print("Testing Start Attendance Button Backend Functionality")
    print("=" * 60)
    
    # Test all endpoints
    test_employees_endpoint()
    test_camera_endpoints()
    test_attendance_start()
    test_attendance_stats()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("\nTo run the backend server:")
    print("  cd backend")
    print("  python app.py")
    print("\nThen open the frontend:")
    print("  Open UI_Image/live_attendance/code.html in browser")