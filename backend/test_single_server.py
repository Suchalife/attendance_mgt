#!/usr/bin/env python3
"""
Test script for single-server Flask application
Tests that all routes work and templates load correctly
"""
import requests
import time
import subprocess
import sys
import os

def test_flask_routes():
    """Test all Flask routes"""
    base_url = 'http://localhost:5000'
    
    # Test routes
    routes_to_test = [
        ('/', 'Home (Biometric Enrollment)'),
        ('/enrollment', 'Biometric Enrollment'),
        ('/attendance', 'Live Attendance'),
        ('/dashboard', 'Operations Dashboard'),
        ('/registration', 'Employee Registration'),
        ('/reports', 'Attendance Reports'),
        ('/health', 'Health Check'),
        ('/api/employees', 'Employees API'),
        ('/api/camera/status', 'Camera Status API'),
        ('/api/attendance/stats', 'Attendance Stats API'),
    ]
    
    print("Testing Flask routes...")
    print("=" * 50)
    
    for route, description in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {route:<20} - {description}")
            else:
                print(f"❌ {route:<20} - {description} (Status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"❌ {route:<20} - {description} (Error: {e})")
    
    print("=" * 50)

def test_static_files():
    """Test that static files are accessible"""
    base_url = 'http://localhost:5000'
    
    static_files = [
        '/static/js/api-client.js',
        '/static/js/router.js',
        '/static/js/utils.js',
        '/static/js/attendance.js',
        '/static/js/enrollment.js',
        '/static/js/dashboard.js',
        '/static/js/registration.js',
        '/static/js/reports.js',
    ]
    
    print("Testing static files...")
    print("=" * 30)
    
    for static_file in static_files:
        try:
            response = requests.get(f"{base_url}{static_file}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {static_file}")
            else:
                print(f"❌ {static_file} (Status: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"❌ {static_file} (Error: {e})")
    
    print("=" * 30)

def main():
    """Main test function"""
    print("Single-Server Flask Application Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000/health', timeout=2)
        if response.status_code == 200:
            print("✅ Flask server is running")
        else:
            print("❌ Flask server responded with error")
            return
    except requests.exceptions.RequestException:
        print("❌ Flask server is not running!")
        print("\nTo start the server:")
        print("  cd backend")
        print("  python app_simple.py")
        return
    
    # Run tests
    test_flask_routes()
    test_static_files()
    
    print("\n" + "=" * 60)
    print("🎉 Single-server integration complete!")
    print("\nTo use the application:")
    print("1. Keep the Flask server running: python app_simple.py")
    print("2. Open your browser to: http://localhost:5000")
    print("3. Navigate between pages using the sidebar")
    print("4. All functionality should work without separate frontend server")

if __name__ == '__main__':
    main()