# ERP MCP Server

A context-aware Model Context Protocol (MCP) server for managing ERP data in MongoDB. This server provides intelligent access to student, faculty, course, attendance, leave request, and timetable data with natural language capabilities.

## Features

### Core Functionality
- **Student Management**: Create, read, update, delete, and search students
- **Faculty Management**: Complete faculty lifecycle management
- **Course Management**: Course creation, updates, and assignment to faculty
- **Attendance Tracking**: Record and analyze student attendance
- **Leave Request Management**: Handle student leave requests with approval workflow
- **Timetable Management**: Create and manage class schedules
- **Analytics**: Comprehensive reporting and insights

### Context-Aware Features
- **Intelligent Queries**: Natural language processing for complex database queries
- **Cross-Collection Analysis**: Analyze relationships between different data entities
- **Trend Analysis**: Track patterns in attendance, leave requests, and academic performance
- **Conflict Detection**: Identify scheduling conflicts and data inconsistencies

## Installation

### Quick Start (Recommended)
1. Run the installation script:
```bash
./install.sh
```

2. Start the server:
```bash
./start_server.sh
```

### Manual Installation
1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure MongoDB is running on `localhost:27017`

4. Run the server:
```bash
python server.py
```

## Virtual Environment Management

The project uses a Python virtual environment for dependency isolation:

### Activate Virtual Environment
```bash
source venv/bin/activate
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Update Dependencies
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Remove Virtual Environment
```bash
rm -rf venv/
```

## Available Tools

### Student Management
- `get_student`: Retrieve student information by roll number or ID
- `create_student`: Add new student records
- `update_student`: Modify existing student information
- `delete_student`: Soft delete students (set isActive to false)
- `search_students`: Advanced search with multiple criteria

### Faculty Management
- `get_faculty`: Retrieve faculty information
- `create_faculty`: Add new faculty members
- `update_faculty`: Modify faculty information
- `delete_faculty`: Soft delete faculty members

### Course Management
- `get_course`: Retrieve course information
- `create_course`: Add new courses
- `update_course`: Modify course details
- `delete_course`: Soft delete courses

### Attendance Management
- `record_attendance`: Record daily attendance
- `get_attendance`: Retrieve attendance records
- `calculate_attendance_stats`: Generate attendance analytics

### Leave Request Management
- `create_leave_request`: Submit new leave requests
- `update_leave_request`: Approve/reject leave requests
- `get_leave_requests`: Retrieve leave requests with filtering

### Timetable Management
- `create_timetable`: Create daily schedules
- `get_timetable`: Retrieve specific day schedules
- `get_weekly_timetable`: Get complete weekly schedules

### Analytics & Reporting
- `get_erp_analytics`: Comprehensive system analytics
- `complex_query`: Advanced cross-collection queries

## Complex Query Types

The server supports several intelligent query types:

1. **students_with_low_attendance**: Find students with attendance below threshold
2. **faculty_workload**: Analyze faculty teaching load
3. **course_enrollment_stats**: Course enrollment analytics
4. **leave_request_trends**: Analyze leave request patterns
5. **timetable_conflicts**: Detect scheduling conflicts

## Database Schema

The server works with the following MongoDB collections:

- **students**: Student records with roll numbers, contact info, and status
- **faculty**: Faculty records with employee IDs, designations, and subjects
- **courses**: Course information with codes, credits, and faculty assignments
- **attendances**: Attendance records with daily status and statistics
- **leaverequests**: Leave request workflow with approval status
- **timetables**: Class schedules organized by day and semester

## Usage Examples

### Create a Student
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

### Record Attendance
```json
{
  "name": "record_attendance",
  "arguments": {
    "student_roll": 1001,
    "month": "January 2025",
    "year": 2025,
    "attendance_data": [
      {"date": "2025-01-01", "status": "P"},
      {"date": "2025-01-02", "status": "A"}
    ]
  }
}
```

### Get Analytics
```json
{
  "name": "get_erp_analytics",
  "arguments": {}
}
```

## Configuration

The server can be configured via `config.json`:

- MongoDB connection settings
- Collection mappings
- Feature toggles
- Server metadata

## Error Handling

The server includes comprehensive error handling:
- Input validation
- Database connection errors
- Duplicate key prevention
- Invalid ID format handling
- Graceful error responses

## Security Features

- Soft delete functionality (no permanent data loss)
- Input sanitization
- Duplicate key prevention
- Transaction safety

## Development

The server is built using:
- **MCP Framework**: For protocol compliance
- **Motor**: Async MongoDB driver
- **PyMongo**: MongoDB operations
- **Asyncio**: Async/await support

### Development Setup
```bash
# Clone and setup
git clone <repository>
cd mcp
./install.sh

# Activate virtual environment
source venv/bin/activate

# Make changes to server.py
# Test changes
./test_with_venv.sh
```

## Scripts

- **`./install.sh`**: Setup virtual environment and install dependencies
- **`./start_server.sh`**: Start the MCP server with virtual environment
- **`./test_with_venv.sh`**: Run tests with virtual environment
- **`./test_client.py`**: Test client for server functionality

## License

This MCP server is part of the ERP system and follows the same licensing terms.
