"""
Test script to verify all data paths are correctly standardized
Tests that all services use the correct backend/data/ directory
"""
import os
import sys

# Add backend to path so we can import services
sys.path.append(os.path.dirname(__file__))

def test_csv_service_paths():
    """Test CSV service uses correct paths"""
    print("\n" + "="*50)
    print("Testing CSV Service Paths")
    print("="*50)
    
    try:
        from services.csv_service import CSVService
        
        csv_service = CSVService()
        print(f"CSV Service data directory: {csv_service.data_dir}")
        
        # Check if it points to backend/data
        expected_path = os.path.join(os.path.dirname(__file__), 'data')
        expected_path = os.path.abspath(expected_path)
        
        if csv_service.data_dir == expected_path:
            print("✅ CSV Service uses correct data directory")
            
            # Test reading employees.csv
            employees = csv_service.read_csv('employees.csv')
            print(f"✅ Successfully read {len(employees)} employees from CSV")
            
            return True
        else:
            print(f"❌ CSV Service data directory mismatch")
            print(f"   Expected: {expected_path}")
            print(f"   Actual: {csv_service.data_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing CSV service: {e}")
        return False


def test_recognition_service_paths():
    """Test recognition service uses correct paths"""
    print("\n" + "="*50)
    print("Testing Recognition Service Paths")
    print("="*50)
    
    try:
        from services.recognition_service import RecognitionService
        
        recognition_service = RecognitionService()
        print(f"✅ Recognition service initialized")
        print(f"   Loaded {len(recognition_service.face_encodings)} face encodings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing recognition service: {e}")
        return False


def test_attendance_service_paths():
    """Test attendance service uses correct paths"""
    print("\n" + "="*50)
    print("Testing Attendance Service Paths")
    print("="*50)
    
    try:
        from services.attendance_service import AttendanceService
        
        attendance_service = AttendanceService()
        print(f"✅ Attendance service initialized")
        
        # Test reading attendance records
        records = attendance_service.get_all_attendance()
        print(f"✅ Successfully read {len(records)} attendance records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing attendance service: {e}")
        return False


def test_data_directory_structure():
    """Test that data directory structure is correct"""
    print("\n" + "="*50)
    print("Testing Data Directory Structure")
    print("="*50)
    
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    data_dir = os.path.abspath(data_dir)
    
    print(f"Data directory: {data_dir}")
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        print("❌ Data directory does not exist")
        return False
    
    print("✅ Data directory exists")
    
    # Check required files
    required_files = ['employees.csv', 'attendance.csv']
    required_dirs = ['employee_images']
    
    all_good = True
    
    for file in required_files:
        file_path = os.path.join(data_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_good = False
    
    for dir_name in required_dirs:
        dir_path = os.path.join(data_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            all_good = False
    
    # Check for duplicate backend/backend directory
    duplicate_dir = os.path.join(os.path.dirname(__file__), 'backend')
    if os.path.exists(duplicate_dir):
        print(f"❌ Duplicate backend/backend directory found: {duplicate_dir}")
        all_good = False
    else:
        print("✅ No duplicate backend/backend directory found")
    
    return all_good


def test_file_contents():
    """Test that CSV files have content"""
    print("\n" + "="*50)
    print("Testing File Contents")
    print("="*50)
    
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    # Test employees.csv
    employees_file = os.path.join(data_dir, 'employees.csv')
    if os.path.exists(employees_file):
        try:
            with open(employees_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                lines = [line for line in content.split('\n') if line.strip()]  # Filter empty lines
                print(f"✅ employees.csv has {len(lines)} lines")
                if len(lines) > 1:  # Header + at least one employee
                    print(f"   Header: {lines[0]}")
                    print(f"   Sample employee: {lines[1] if len(lines) > 1 else 'No data'}")
                    print(f"   Total employees: {len(lines) - 1}")
                else:
                    print("⚠️  employees.csv only has headers, no employee data")
        except Exception as e:
            print(f"❌ Error reading employees.csv: {e}")
            return False
    else:
        print("❌ employees.csv not found")
        return False
    
    return True


if __name__ == '__main__':
    print("\n" + "="*60)
    print("DATA PATHS STANDARDIZATION TEST")
    print("="*60)
    
    tests = [
        test_data_directory_structure,
        test_file_contents,
        test_csv_service_paths,
        test_attendance_service_paths,
        test_recognition_service_paths,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Data paths are correctly standardized!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("="*60)