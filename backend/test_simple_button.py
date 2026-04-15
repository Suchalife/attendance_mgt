#!/usr/bin/env python3
"""
Simple test for Start Attendance button
Tests the exact endpoint the button will call
"""

import requests
import json

def test_attendance_start():
    """Test the attendance start endpoint exactly as the button will call it"""
    print("Testing POST http://127.0.0.1:5000/api/attendance/start")
    print("=" * 50)
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/attendance/start",
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("\n🎉 Button should show: 'Attendance started successfully'")
            else:
                print(f"\n❌ Button should show error: {data.get('error', 'Unknown error')}")
        else:
            print("❌ FAILED")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR")
        print("Backend server is not running!")
        print("\nTo start backend:")
        print("  cd backend")
        print("  python app.py")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == '__main__':
    test_attendance_start()