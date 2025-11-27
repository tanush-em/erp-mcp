# ERP MCP Server Usage Guide

## Quick Start

1. **Install dependencies**:
   ```bash
   ./install.sh
   ```

2. **Start the server**:
   ```bash
   python3 server.py
   ```

3. **Test the server**:
   ```bash
   python3 test_client.py
   ```

## Available Tools

### Student Management
```json
{
  "name": "create_student",
  "arguments": {
    "roll": 1001,
    "fullName": "John Doe",
    "email": "john.doe@university.edu",
    "phone": "+1234567890"
  }
}
```

```json
{
  "name": "get_student",
  "arguments": {
    "roll": 1001
  }
}
```

```json
{
  "name": "search_students",
  "arguments": {
    "name": "John",
    "isActive": true
  }
}
```

### Faculty Management
```json
{
  "name": "create_faculty",
  "arguments": {
    "employeeId": "EMP001",
    "fullName": "Dr. Jane Smith",
    "email": "jane.smith@university.edu",
    "designation": "Professor",
    "subjectsHandled": ["Mathematics", "Statistics"]
  }
}
```

### Course Management
```json
{
  "name": "create_course",
  "arguments": {
    "code": "MATH101",
    "title": "Introduction to Mathematics",
    "credits": 3,
    "semester": 1,
    "description": "Basic mathematics course",
    "facultyInCharge": "faculty_object_id"
  }
}
```

### Attendance Management
```json
{
  "name": "record_attendance",
  "arguments": {
    "student_roll": 1001,
    "month": "January 2025",
    "year": 2025,
    "attendance_data": [
      {"date": "2025-01-01", "status": "P"},
      {"date": "2025-01-02", "status": "A"},
      {"date": "2025-01-03", "status": "P"}
    ]
  }
}
```

```json
{
  "name": "calculate_attendance_stats",
  "arguments": {
    "student_roll": 1001,
    "month": "January 2025"
  }
}
```

### Leave Request Management
```json
{
  "name": "create_leave_request",
  "arguments": {
    "student_roll": 1001,
    "start_date": "2025-01-15",
    "end_date": "2025-01-17",
    "reason": "Medical emergency",
    "comments": "Family emergency"
  }
}
```

```json
{
  "name": "update_leave_request",
  "arguments": {
    "leave_id": "leave_request_object_id",
    "status": "approved",
    "handled_by": "faculty_object_id",
    "comments": "Approved for medical reasons"
  }
}
```

### Timetable Management
```json
{
  "name": "create_timetable",
  "arguments": {
    "dayOfWeek": "Monday",
    "semester": 1,
    "slots": [
      {
        "period": 1,
        "type": "lecture",
        "courseCode": "MATH101",
        "room": "A101"
      },
      {
        "period": 2,
        "type": "break",
        "courseCode": "",
        "room": ""
      }
    ]
  }
}
```

### Analytics and Complex Queries
```json
{
  "name": "get_erp_analytics",
  "arguments": {}
}
```

```json
{
  "name": "complex_query",
  "arguments": {
    "query_type": "students_with_low_attendance",
    "parameters": {
      "threshold": 75
    }
  }
}
```

```json
{
  "name": "complex_query",
  "arguments": {
    "query_type": "faculty_workload"
  }
}
```

```json
{
  "name": "complex_query",
  "arguments": {
    "query_type": "leave_request_trends"
  }
}
```

## Context-Aware Features

The server provides intelligent context-aware capabilities:

1. **Cross-Collection Analysis**: Understand relationships between students, faculty, courses, and attendance
2. **Trend Analysis**: Track patterns in attendance, leave requests, and academic performance
3. **Conflict Detection**: Identify scheduling conflicts and data inconsistencies
4. **Intelligent Queries**: Natural language processing for complex database operations

## Error Handling

The server includes comprehensive error handling:
- Input validation
- Database connection errors
- Duplicate key prevention
- Invalid ID format handling
- Graceful error responses

## Database Schema

The server works with these MongoDB collections:
- `students` - Student records
- `faculty` - Faculty records  
- `courses` - Course information
- `attendances` - Attendance records
- `leaverequests` - Leave request workflow
- `timetables` - Class schedules

## Integration with Next.js App

Your Next.js app can continue to display the data while the MCP server handles:
- Data manipulation
- Complex queries
- Analytics
- Context-aware operations

The MCP server operates independently and provides intelligent access to your MongoDB database.
