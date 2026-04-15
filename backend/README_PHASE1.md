# Phase 1: Basic Flask API with CSV Storage

## Project Structure

```
backend/
├── app_simple.py           # Main Flask application
├── routes/
│   └── employees.py        # Employee API endpoints
├── services/
│   └── csv_service.py      # CSV file operations
├── data/
│   └── employees.csv       # Employee data storage
└── requirements_simple.txt # Python dependencies
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements_simple.txt
```

### 2. Run the Flask Server

```bash
python app_simple.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### 1. POST /api/employees
Create a new employee

**Request:**
```json
{
  "EmployeeID": "EMP-001",
  "EmployeeName": "John Doe",
  "Department": "Sorting",
  "Shift": "Day"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Employee created successfully",
  "employee": {
    "EmployeeID": "EMP-001",
    "EmployeeName": "John Doe",
    "Department": "Sorting",
    "Shift": "Day"
  }
}
```

**Response (Error - Missing Fields):**
```json
{
  "success": false,
  "error": "Missing required fields: EmployeeName"
}
```

**Response (Error - Duplicate ID):**
```json
{
  "success": false,
  "error": "Employee ID EMP-001 already exists"
}
```

### 2. GET /api/employees
Get all employees

**Response:**
```json
{
  "success": true,
  "count": 2,
  "employees": [
    {
      "EmployeeID": "EMP-001",
      "EmployeeName": "John Doe",
      "Department": "Sorting",
      "Shift": "Day"
    },
    {
      "EmployeeID": "EMP-002",
      "EmployeeName": "Jane Smith",
      "Department": "Logistics",
      "Shift": "Day"
    }
  ]
}
```

### 3. GET /api/employees/count
Get total employee count

**Response:**
```json
{
  "success": true,
  "count": 2
}
```

## Testing with Postman

### Create Employee (POST)
1. Method: POST
2. URL: `http://localhost:5000/api/employees`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "EmployeeID": "EMP-001",
  "EmployeeName": "John Doe",
  "Department": "Sorting",
  "Shift": "Day"
}
```

### Get All Employees (GET)
1. Method: GET
2. URL: `http://localhost:5000/api/employees`

### Get Employee Count (GET)
1. Method: GET
2. URL: `http://localhost:5000/api/employees/count`

## Testing with cURL

### Create Employee
```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "EmployeeID": "EMP-001",
    "EmployeeName": "John Doe",
    "Department": "Sorting",
    "Shift": "Day"
  }'
```

### Get All Employees
```bash
curl http://localhost:5000/api/employees
```

### Get Employee Count
```bash
curl http://localhost:5000/api/employees/count
```

## CSV File Format

The `backend/data/employees.csv` file stores employee data:

```csv
EmployeeID,EmployeeName,Department,Shift
EMP-001,John Doe,Sorting,Day
EMP-002,Jane Smith,Logistics,Day
```

## Validation Rules

1. **Required Fields**: EmployeeID, EmployeeName, Department
2. **Optional Fields**: Shift (defaults to "Day")
3. **Unique Constraint**: EmployeeID must be unique
4. **No Authentication**: Single-user system (simplified)

## Error Handling

All endpoints return JSON responses with:
- `success`: boolean indicating success/failure
- `error`: error message (if failed)
- `data`: response data (if successful)

HTTP Status Codes:
- `200`: Success (GET)
- `201`: Created (POST)
- `400`: Bad Request (validation error)
- `500`: Server Error

## Next Steps

After verifying Phase 1 works:
1. Test all endpoints with Postman
2. Verify CSV file is created and populated
3. Test error scenarios (missing fields, duplicate IDs)
4. Proceed to Phase 2: Camera Streaming
