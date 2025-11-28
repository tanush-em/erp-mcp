#!/usr/bin/env python3
"""
ERP MCP Server - MongoDB-backed Model Context Protocol server
Provides intelligent access to ERP data with natural language capabilities
"""

import asyncio
import json
import logging
import os
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# MongoDB imports
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from bson.errors import InvalidId

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/erp")
client = AsyncIOMotorClient(MONGODB_URI)
db = client.erp

# Collections
students_collection = db.students
faculty_collection = db.faculties
courses_collection = db.courses
attendance_collection = db.attendances
leave_requests_collection = db.leaverequests
timetables_collection = db.timetables

# Load system instructions
SYSTEM_INSTRUCTIONS_PATH = os.path.join(os.path.dirname(__file__), "system_instructions.json")
system_instructions = {}
if os.path.exists(SYSTEM_INSTRUCTIONS_PATH):
    try:
        with open(SYSTEM_INSTRUCTIONS_PATH, 'r') as f:
            system_instructions = json.load(f)
    except Exception as e:
        logger.warning(f"Could not load system instructions: {e}")

# MCP Server instance
server = Server("erp-mcp-server")

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available ERP resources"""
    resources = [
        Resource(
            uri="erp://system-instructions",
            name="System Instructions",
            description="Interaction guidelines, tone, and conversation flow instructions for the ERP MCP server",
            mimeType="application/json"
        ),
        Resource(
            uri="erp://students",
            name="Students",
            description="All student records in the ERP system",
            mimeType="application/json"
        ),
        Resource(
            uri="erp://faculty", 
            name="Faculty",
            description="All faculty records in the ERP system",
            mimeType="application/json"
        ),
        Resource(
            uri="erp://courses",
            name="Courses", 
            description="All course records in the ERP system",
            mimeType="application/json"
        ),
        Resource(
            uri="erp://attendance",
            name="Attendance",
            description="All attendance records in the ERP system", 
            mimeType="application/json"
        ),
        Resource(
            uri="erp://leave-requests",
            name="Leave Requests",
            description="All leave request records in the ERP system",
            mimeType="application/json"
        ),
        Resource(
            uri="erp://timetables",
            name="Timetables",
            description="All timetable records in the ERP system",
            mimeType="application/json"
        )
    ]
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read ERP resource data"""
    if uri == "erp://system-instructions":
        # Return system instructions for interaction guidelines
        return json.dumps(system_instructions, indent=2, default=str)
    
    elif uri == "erp://students":
        cursor = students_collection.find({"isActive": True})
        students = await cursor.to_list(length=1000)
        return json.dumps(students, default=str)
    
    elif uri == "erp://faculty":
        cursor = faculty_collection.find({"isActive": True})
        faculty = await cursor.to_list(length=1000)
        return json.dumps(faculty, default=str)
    
    elif uri == "erp://courses":
        cursor = courses_collection.find({"isActive": True})
        courses = await cursor.to_list(length=1000)
        return json.dumps(courses, default=str)
    
    elif uri == "erp://attendance":
        cursor = attendance_collection.find()
        attendance = await cursor.to_list(length=1000)
        return json.dumps(attendance, default=str)
    
    elif uri == "erp://leave-requests":
        cursor = leave_requests_collection.find()
        leave_requests = await cursor.to_list(length=1000)
        return json.dumps(leave_requests, default=str)
    
    elif uri == "erp://timetables":
        cursor = timetables_collection.find({"isActive": True})
        timetables = await cursor.to_list(length=1000)
        return json.dumps(timetables, default=str)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

# Student Management Tools
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available ERP management tools"""
    return [
        # Student Management
        Tool(
            name="get_student",
            description="Get student information by roll number or ObjectId",
            inputSchema={
                "type": "object",
                "properties": {
                    "roll": {"type": "integer", "description": "Student roll number"},
                    "student_id": {"type": "string", "description": "Student ObjectId"}
                }
            }
        ),
        Tool(
            name="create_student", 
            description="Create a new student record",
            inputSchema={
                "type": "object",
                "required": ["roll", "fullName", "email", "phone"],
                "properties": {
                    "roll": {"type": "integer", "description": "Student roll number"},
                    "fullName": {"type": "string", "description": "Student full name"},
                    "email": {"type": "string", "description": "Student email"},
                    "phone": {"type": "string", "description": "Student phone number"},
                    "isActive": {"type": "boolean", "description": "Student active status", "default": True}
                }
            }
        ),
        Tool(
            name="update_student",
            description="Update student information",
            inputSchema={
                "type": "object", 
                "required": ["student_id"],
                "properties": {
                    "student_id": {"type": "string", "description": "Student ObjectId"},
                    "roll": {"type": "integer", "description": "Student roll number"},
                    "fullName": {"type": "string", "description": "Student full name"},
                    "email": {"type": "string", "description": "Student email"},
                    "phone": {"type": "string", "description": "Student phone number"},
                    "isActive": {"type": "boolean", "description": "Student active status"}
                }
            }
        ),
        Tool(
            name="delete_student",
            description="Delete student record (soft delete by setting isActive to false)",
            inputSchema={
                "type": "object",
                "required": ["student_id"],
                "properties": {
                    "student_id": {"type": "string", "description": "Student ObjectId"}
                }
            }
        ),
        Tool(
            name="search_students",
            description="Search students by various criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Search by name (partial match)"},
                    "email": {"type": "string", "description": "Search by email"},
                    "roll_range": {"type": "object", "properties": {
                        "min": {"type": "integer"},
                        "max": {"type": "integer"}
                    }, "description": "Search by roll number range"},
                    "isActive": {"type": "boolean", "description": "Filter by active status"}
                }
            }
        ),
        
        # Faculty Management
        Tool(
            name="get_faculty",
            description="Get faculty information by employee ID or ObjectId",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "Faculty employee ID"},
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId"}
                }
            }
        ),
        Tool(
            name="create_faculty",
            description="Create a new faculty record", 
            inputSchema={
                "type": "object",
                "required": ["employeeId", "fullName", "email", "designation"],
                "properties": {
                    "employeeId": {"type": "string", "description": "Faculty employee ID"},
                    "fullName": {"type": "string", "description": "Faculty full name"},
                    "email": {"type": "string", "description": "Faculty email"},
                    "designation": {"type": "string", "description": "Faculty designation"},
                    "subjectsHandled": {"type": "array", "items": {"type": "string"}, "description": "Subjects handled"},
                    "isActive": {"type": "boolean", "description": "Faculty active status", "default": True}
                }
            }
        ),
        Tool(
            name="update_faculty",
            description="Update faculty information",
            inputSchema={
                "type": "object",
                "required": ["faculty_id"],
                "properties": {
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId"},
                    "employeeId": {"type": "string", "description": "Faculty employee ID"},
                    "fullName": {"type": "string", "description": "Faculty full name"},
                    "email": {"type": "string", "description": "Faculty email"},
                    "designation": {"type": "string", "description": "Faculty designation"},
                    "subjectsHandled": {"type": "array", "items": {"type": "string"}, "description": "Subjects handled"},
                    "isActive": {"type": "boolean", "description": "Faculty active status"}
                }
            }
        ),
        Tool(
            name="delete_faculty",
            description="Delete faculty record (soft delete by setting isActive to false)",
            inputSchema={
                "type": "object",
                "required": ["faculty_id"],
                "properties": {
                    "faculty_id": {"type": "string", "description": "Faculty ObjectId"}
                }
            }
        ),
        
        # Course Management
        Tool(
            name="get_course",
            description="Get course information by code or ObjectId",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Course code"},
                    "course_id": {"type": "string", "description": "Course ObjectId"}
                }
            }
        ),
        Tool(
            name="create_course",
            description="Create a new course record",
            inputSchema={
                "type": "object",
                "required": ["code", "title", "credits", "semester"],
                "properties": {
                    "code": {"type": "string", "description": "Course code"},
                    "title": {"type": "string", "description": "Course title"},
                    "credits": {"type": "integer", "description": "Course credits"},
                    "semester": {"type": "integer", "description": "Course semester"},
                    "description": {"type": "string", "description": "Course description"},
                    "facultyInCharge": {"type": "string", "description": "Faculty ObjectId in charge"},
                    "isActive": {"type": "boolean", "description": "Course active status", "default": True}
                }
            }
        ),
        Tool(
            name="update_course",
            description="Update course information",
            inputSchema={
                "type": "object",
                "required": ["course_id"],
                "properties": {
                    "course_id": {"type": "string", "description": "Course ObjectId"},
                    "code": {"type": "string", "description": "Course code"},
                    "title": {"type": "string", "description": "Course title"},
                    "credits": {"type": "integer", "description": "Course credits"},
                    "semester": {"type": "integer", "description": "Course semester"},
                    "description": {"type": "string", "description": "Course description"},
                    "facultyInCharge": {"type": "string", "description": "Faculty ObjectId in charge"},
                    "isActive": {"type": "boolean", "description": "Course active status"}
                }
            }
        ),
        Tool(
            name="delete_course",
            description="Delete course record (soft delete by setting isActive to false)",
            inputSchema={
                "type": "object",
                "required": ["course_id"],
                "properties": {
                    "course_id": {"type": "string", "description": "Course ObjectId"}
                }
            }
        ),
        
        # Attendance Management
        Tool(
            name="record_attendance",
            description="Record attendance for a student",
            inputSchema={
                "type": "object",
                "required": ["student_roll", "month", "year", "attendance_data"],
                "properties": {
                    "student_roll": {"type": "integer", "description": "Student roll number"},
                    "month": {"type": "string", "description": "Month (e.g., 'January 2025')"},
                    "year": {"type": "integer", "description": "Year"},
                    "attendance_data": {"type": "array", "items": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "format": "date"},
                            "status": {"type": "string", "enum": ["P", "A", "DNM"]}
                        }
                    }, "description": "Array of attendance records"}
                }
            }
        ),
        Tool(
            name="get_attendance",
            description="Get attendance records for a student",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_roll": {"type": "integer", "description": "Student roll number"},
                    "month": {"type": "string", "description": "Month (e.g., 'January 2025')"},
                    "year": {"type": "integer", "description": "Year"}
                }
            }
        ),
        Tool(
            name="calculate_attendance_stats",
            description="Calculate attendance statistics for a student or all students",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_roll": {"type": "integer", "description": "Student roll number (optional)"},
                    "month": {"type": "string", "description": "Month (optional)"},
                    "year": {"type": "integer", "description": "Year (optional)"}
                }
            }
        ),
        
        # Leave Request Management
        Tool(
            name="create_leave_request",
            description="Create a new leave request",
            inputSchema={
                "type": "object",
                "required": ["student_roll", "start_date", "end_date", "reason"],
                "properties": {
                    "student_roll": {"type": "integer", "description": "Student roll number"},
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"},
                    "reason": {"type": "string", "description": "Reason for leave"},
                    "comments": {"type": "string", "description": "Additional comments"}
                }
            }
        ),
        Tool(
            name="update_leave_request",
            description="Update leave request status (approve/reject)",
            inputSchema={
                "type": "object",
                "required": ["leave_id", "status", "handled_by"],
                "properties": {
                    "leave_id": {"type": "string", "description": "Leave request ObjectId"},
                    "status": {"type": "string", "enum": ["approved", "rejected"]},
                    "handled_by": {"type": "string", "description": "Faculty ObjectId handling the request"},
                    "comments": {"type": "string", "description": "Additional comments"}
                }
            }
        ),
        Tool(
            name="get_leave_requests",
            description="Get leave requests with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_roll": {"type": "integer", "description": "Student roll number"},
                    "status": {"type": "string", "enum": ["pending", "approved", "rejected"]},
                    "date_range": {"type": "object", "properties": {
                        "start": {"type": "string", "format": "date"},
                        "end": {"type": "string", "format": "date"}
                    }}
                }
            }
        ),
        
        # Timetable Management
        Tool(
            name="create_timetable",
            description="Create timetable for a day and semester",
            inputSchema={
                "type": "object",
                "required": ["dayOfWeek", "semester", "slots"],
                "properties": {
                    "dayOfWeek": {"type": "string", "enum": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                    "semester": {"type": "integer", "description": "Semester number"},
                    "slots": {"type": "array", "items": {
                        "type": "object",
                        "properties": {
                            "period": {"type": "integer"},
                            "type": {"type": "string", "enum": ["lecture", "break", "lab", "tutorial"]},
                            "courseCode": {"type": "string"},
                            "course": {"type": "string", "description": "Course ObjectId reference"},
                            "faculty": {"type": "string", "description": "Faculty ObjectId reference"},
                            "room": {"type": "string"}
                        },
                        "required": ["period", "type", "courseCode"]
                    }, "description": "Time slots for the day"}
                }
            }
        ),
        Tool(
            name="get_timetable",
            description="Get timetable for a specific day and semester",
            inputSchema={
                "type": "object",
                "required": ["dayOfWeek", "semester"],
                "properties": {
                    "dayOfWeek": {"type": "string", "enum": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
                    "semester": {"type": "integer", "description": "Semester number"}
                }
            }
        ),
        Tool(
            name="get_weekly_timetable",
            description="Get complete weekly timetable for a semester",
            inputSchema={
                "type": "object",
                "required": ["semester"],
                "properties": {
                    "semester": {"type": "integer", "description": "Semester number"}
                }
            }
        ),
        
        # Analytics and Complex Queries
        Tool(
            name="get_erp_analytics",
            description="Get comprehensive ERP analytics and insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "semester": {"type": "integer", "description": "Filter by semester"},
                    "month": {"type": "string", "description": "Filter by month"},
                    "year": {"type": "integer", "description": "Filter by year"}
                }
            }
        ),
        Tool(
            name="complex_query",
            description="Execute complex queries across multiple collections",
            inputSchema={
                "type": "object",
                "required": ["query_type"],
                "properties": {
                    "query_type": {"type": "string", "enum": [
                        "students_with_low_attendance",
                        "faculty_workload",
                        "course_enrollment_stats",
                        "leave_request_trends",
                        "timetable_conflicts"
                    ]},
                    "parameters": {"type": "object", "description": "Query-specific parameters"}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for ERP management"""
    try:
        if name == "get_student":
            return await get_student(arguments)
        elif name == "create_student":
            return await create_student(arguments)
        elif name == "update_student":
            return await update_student(arguments)
        elif name == "delete_student":
            return await delete_student(arguments)
        elif name == "search_students":
            return await search_students(arguments)
        elif name == "get_faculty":
            return await get_faculty(arguments)
        elif name == "create_faculty":
            return await create_faculty(arguments)
        elif name == "update_faculty":
            return await update_faculty(arguments)
        elif name == "delete_faculty":
            return await delete_faculty(arguments)
        elif name == "get_course":
            return await get_course(arguments)
        elif name == "create_course":
            return await create_course(arguments)
        elif name == "update_course":
            return await update_course(arguments)
        elif name == "delete_course":
            return await delete_course(arguments)
        elif name == "record_attendance":
            return await record_attendance(arguments)
        elif name == "get_attendance":
            return await get_attendance(arguments)
        elif name == "calculate_attendance_stats":
            return await calculate_attendance_stats(arguments)
        elif name == "create_leave_request":
            return await create_leave_request(arguments)
        elif name == "update_leave_request":
            return await update_leave_request(arguments)
        elif name == "get_leave_requests":
            return await get_leave_requests(arguments)
        elif name == "create_timetable":
            return await create_timetable(arguments)
        elif name == "get_timetable":
            return await get_timetable(arguments)
        elif name == "get_weekly_timetable":
            return await get_weekly_timetable(arguments)
        elif name == "get_erp_analytics":
            return await get_erp_analytics(arguments)
        elif name == "complex_query":
            return await complex_query(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

# Student Management Functions
async def get_student(args: Dict[str, Any]) -> List[TextContent]:
    """Get student information"""
    if "roll" in args:
        student = await students_collection.find_one({"roll": args["roll"]})
    elif "student_id" in args:
        try:
            student = await students_collection.find_one({"_id": ObjectId(args["student_id"])})
        except InvalidId:
            return [TextContent(type="text", text="Invalid student ID format")]
    else:
        return [TextContent(type="text", text="Either roll or student_id is required")]
    
    if not student:
        return [TextContent(type="text", text="Student not found")]
    
    return [TextContent(type="text", text=json.dumps(student, default=str))]

async def create_student(args: Dict[str, Any]) -> List[TextContent]:
    """Create a new student"""
    try:
        student_data = {
            "roll": args["roll"],
            "fullName": args["fullName"],
            "email": args["email"],
            "phone": args["phone"],
            "isActive": args.get("isActive", True),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        result = await students_collection.insert_one(student_data)
        return [TextContent(type="text", text=f"Student created successfully with ID: {result.inserted_id}")]
    except DuplicateKeyError:
        return [TextContent(type="text", text="Student with this roll number or email already exists")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error creating student: {str(e)}")]

async def update_student(args: Dict[str, Any]) -> List[TextContent]:
    """Update student information"""
    try:
        student_id = ObjectId(args["student_id"])
        update_data = {"updatedAt": datetime.now()}
        
        for field in ["roll", "fullName", "email", "phone", "isActive"]:
            if field in args:
                update_data[field] = args[field]
        
        result = await students_collection.update_one(
            {"_id": student_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return [TextContent(type="text", text="Student not found")]
        
        return [TextContent(type="text", text="Student updated successfully")]
    except InvalidId:
        return [TextContent(type="text", text="Invalid student ID format")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error updating student: {str(e)}")]

async def delete_student(args: Dict[str, Any]) -> List[TextContent]:
    """Soft delete student"""
    try:
        student_id = ObjectId(args["student_id"])
        result = await students_collection.update_one(
            {"_id": student_id},
            {"$set": {"isActive": False, "updatedAt": datetime.now()}}
        )
        
        if result.matched_count == 0:
            return [TextContent(type="text", text="Student not found")]
        
        return [TextContent(type="text", text="Student deactivated successfully")]
    except InvalidId:
        return [TextContent(type="text", text="Invalid student ID format")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error deleting student: {str(e)}")]

async def search_students(args: Dict[str, Any]) -> List[TextContent]:
    """Search students with various criteria"""
    query = {}
    
    if "name" in args:
        query["fullName"] = {"$regex": args["name"], "$options": "i"}
    if "email" in args:
        query["email"] = args["email"]
    if "roll_range" in args:
        range_query = {}
        if "min" in args["roll_range"]:
            range_query["$gte"] = args["roll_range"]["min"]
        if "max" in args["roll_range"]:
            range_query["$lte"] = args["roll_range"]["max"]
        if range_query:
            query["roll"] = range_query
    if "isActive" in args:
        query["isActive"] = args["isActive"]
    
    cursor = students_collection.find(query)
    students = await cursor.to_list(length=1000)
    return [TextContent(type="text", text=json.dumps(students, default=str))]

# Faculty Management Functions
async def get_faculty(args: Dict[str, Any]) -> List[TextContent]:
    """Get faculty information"""
    if "employee_id" in args:
        faculty = await faculty_collection.find_one({"employeeId": args["employee_id"]})
    elif "faculty_id" in args:
        try:
            faculty = await faculty_collection.find_one({"_id": ObjectId(args["faculty_id"])})
        except InvalidId:
            return [TextContent(type="text", text="Invalid faculty ID format")]
    else:
        return [TextContent(type="text", text="Either employee_id or faculty_id is required")]
    
    if not faculty:
        return [TextContent(type="text", text="Faculty not found")]
    
    return [TextContent(type="text", text=json.dumps(faculty, default=str))]

async def create_faculty(args: Dict[str, Any]) -> List[TextContent]:
    """Create a new faculty member"""
    try:
        faculty_data = {
            "employeeId": args["employeeId"],
            "fullName": args["fullName"],
            "email": args["email"],
            "designation": args["designation"],
            "subjectsHandled": args.get("subjectsHandled", []),
            "isActive": args.get("isActive", True),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        result = await faculty_collection.insert_one(faculty_data)
        return [TextContent(type="text", text=f"Faculty created successfully with ID: {result.inserted_id}")]
    except DuplicateKeyError:
        return [TextContent(type="text", text="Faculty with this employee ID or email already exists")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error creating faculty: {str(e)}")]

async def update_faculty(args: Dict[str, Any]) -> List[TextContent]:
    """Update faculty information"""
    try:
        faculty_id = ObjectId(args["faculty_id"])
        update_data = {"updatedAt": datetime.now()}
        
        for field in ["employeeId", "fullName", "email", "designation", "subjectsHandled", "isActive"]:
            if field in args:
                update_data[field] = args[field]
        
        result = await faculty_collection.update_one(
            {"_id": faculty_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return [TextContent(type="text", text="Faculty not found")]
        
        return [TextContent(type="text", text="Faculty updated successfully")]
    except InvalidId:
        return [TextContent(type="text", text="Invalid faculty ID format")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error updating faculty: {str(e)}")]

async def delete_faculty(args: Dict[str, Any]) -> List[TextContent]:
    """Soft delete faculty"""
    try:
        faculty_id = ObjectId(args["faculty_id"])
        result = await faculty_collection.update_one(
            {"_id": faculty_id},
            {"$set": {"isActive": False, "updatedAt": datetime.now()}}
        )
        
        if result.matched_count == 0:
            return [TextContent(type="text", text="Faculty not found")]
        
        return [TextContent(type="text", text="Faculty deactivated successfully")]
    except InvalidId:
        return [TextContent(type="text", text="Invalid faculty ID format")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error deleting faculty: {str(e)}")]

# Course Management Functions
async def get_course(args: Dict[str, Any]) -> List[TextContent]:
    """Get course information"""
    if "code" in args:
        course = await courses_collection.find_one({"code": args["code"]})
    elif "course_id" in args:
        try:
            course = await courses_collection.find_one({"_id": ObjectId(args["course_id"])})
        except InvalidId:
            return [TextContent(type="text", text="Invalid course ID format")]
    else:
        return [TextContent(type="text", text="Either code or course_id is required")]
    
    if not course:
        return [TextContent(type="text", text="Course not found")]
    
    return [TextContent(type="text", text=json.dumps(course, default=str))]

async def create_course(args: Dict[str, Any]) -> List[TextContent]:
    """Create a new course"""
    try:
        # Validate facultyInCharge ObjectId if provided
        faculty_in_charge = None
        if args.get("facultyInCharge"):
            try:
                faculty_id = ObjectId(args["facultyInCharge"])
                # Verify faculty exists
                faculty = await faculty_collection.find_one({"_id": faculty_id})
                if not faculty:
                    return [TextContent(type="text", text=f"Faculty with ID {args['facultyInCharge']} not found")]
                faculty_in_charge = faculty_id
            except InvalidId:
                return [TextContent(type="text", text=f"Invalid faculty ID format: {args['facultyInCharge']}")]
        
        course_data = {
            "code": args["code"],
            "title": args["title"],
            "credits": args["credits"],
            "semester": args["semester"],
            "description": args.get("description", ""),
            "facultyInCharge": faculty_in_charge,
            "isActive": args.get("isActive", True),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        result = await courses_collection.insert_one(course_data)
        return [TextContent(type="text", text=f"Course created successfully with ID: {result.inserted_id}")]
    except DuplicateKeyError:
        return [TextContent(type="text", text="Course with this code already exists")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error creating course: {str(e)}")]

async def update_course(args: Dict[str, Any]) -> List[TextContent]:
    """Update course information"""
    try:
        course_id = ObjectId(args["course_id"])
        update_data = {"updatedAt": datetime.now()}
        
        for field in ["code", "title", "credits", "semester", "description", "isActive"]:
            if field in args:
                update_data[field] = args[field]
        
        if "facultyInCharge" in args:
            if args["facultyInCharge"]:
                try:
                    faculty_id = ObjectId(args["facultyInCharge"])
                    # Verify faculty exists
                    faculty = await faculty_collection.find_one({"_id": faculty_id})
                    if not faculty:
                        return [TextContent(type="text", text=f"Faculty with ID {args['facultyInCharge']} not found")]
                    update_data["facultyInCharge"] = faculty_id
                except InvalidId:
                    return [TextContent(type="text", text=f"Invalid faculty ID format: {args['facultyInCharge']}")]
            else:
                update_data["facultyInCharge"] = None
        
        result = await courses_collection.update_one(
            {"_id": course_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return [TextContent(type="text", text="Course not found")]
        
        return [TextContent(type="text", text="Course updated successfully")]
    except InvalidId:
        return [TextContent(type="text", text="Invalid course ID format")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error updating course: {str(e)}")]

async def delete_course(args: Dict[str, Any]) -> List[TextContent]:
    """Soft delete course"""
    try:
        course_id = ObjectId(args["course_id"])
        result = await courses_collection.update_one(
            {"_id": course_id},
            {"$set": {"isActive": False, "updatedAt": datetime.now()}}
        )
        
        if result.matched_count == 0:
            return [TextContent(type="text", text="Course not found")]
        
        return [TextContent(type="text", text="Course deactivated successfully")]
    except InvalidId:
        return [TextContent(type="text", text="Invalid course ID format")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error deleting course: {str(e)}")]

# Attendance Management Functions
async def record_attendance(args: Dict[str, Any]) -> List[TextContent]:
    """Record attendance for a student"""
    try:
        # Get student ID from roll number
        student = await students_collection.find_one({"roll": args["student_roll"]})
        if not student:
            return [TextContent(type="text", text="Student not found")]
        
        # Convert date strings to datetime objects
        attendance_records = []
        for record in args["attendance_data"]:
            date_obj = datetime.strptime(record["date"], "%Y-%m-%d") if isinstance(record["date"], str) else record["date"]
            attendance_records.append({
                "date": date_obj,
                "status": record["status"]
            })
        
        attendance_data = {
            "student": student["_id"],
            "studentRoll": args["student_roll"],
            "month": args["month"],
            "year": args["year"],
            "attendance": attendance_records,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        # Calculate statistics
        total_days = len(attendance_data["attendance"])
        present_days = sum(1 for record in attendance_data["attendance"] if record["status"] == "P")
        absent_days = sum(1 for record in attendance_data["attendance"] if record["status"] == "A")
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
        
        attendance_data.update({
            "totalDays": total_days,
            "presentDays": present_days,
            "absentDays": absent_days,
            "attendancePercentage": round(attendance_percentage, 2)
        })
        
        # Use upsert to handle existing records
        result = await attendance_collection.update_one(
            {"studentRoll": args["student_roll"], "month": args["month"], "year": args["year"]},
            {"$set": attendance_data},
            upsert=True
        )
        
        return [TextContent(type="text", text=f"Attendance recorded successfully. Percentage: {attendance_percentage:.2f}%")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error recording attendance: {str(e)}")]

async def get_attendance(args: Dict[str, Any]) -> List[TextContent]:
    """Get attendance records for a student"""
    try:
        query = {"studentRoll": args["student_roll"]}
        
        if "month" in args:
            query["month"] = args["month"]
        if "year" in args:
            query["year"] = args["year"]
        
        cursor = attendance_collection.find(query)
        attendance_records = await cursor.to_list(length=1000)
        return [TextContent(type="text", text=json.dumps(attendance_records, default=str))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting attendance: {str(e)}")]

async def calculate_attendance_stats(args: Dict[str, Any]) -> List[TextContent]:
    """Calculate attendance statistics"""
    try:
        query = {}
        
        if "student_roll" in args:
            query["studentRoll"] = args["student_roll"]
        if "month" in args:
            query["month"] = args["month"]
        if "year" in args:
            query["year"] = args["year"]
        
        cursor = attendance_collection.find(query)
        records = await cursor.to_list(length=1000)
        
        if not records:
            return [TextContent(type="text", text="No attendance records found")]
        
        # Calculate overall statistics
        total_students = len(set(record["studentRoll"] for record in records))
        total_days = sum(record["totalDays"] for record in records)
        total_present = sum(record["presentDays"] for record in records)
        overall_percentage = (total_present / total_days * 100) if total_days > 0 else 0
        
        # Find students with low attendance (< 75%)
        low_attendance_students = []
        for record in records:
            if record["attendancePercentage"] < 75:
                student = await students_collection.find_one({"roll": record["studentRoll"]})
                if student:
                    low_attendance_students.append({
                        "roll": record["studentRoll"],
                        "name": student["fullName"],
                        "percentage": record["attendancePercentage"]
                    })
        
        stats = {
            "total_students": total_students,
            "total_days": total_days,
            "total_present": total_present,
            "overall_percentage": round(overall_percentage, 2),
            "low_attendance_students": low_attendance_students
        }
        
        return [TextContent(type="text", text=json.dumps(stats, default=str))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error calculating attendance stats: {str(e)}")]

# Leave Request Management Functions
async def create_leave_request(args: Dict[str, Any]) -> List[TextContent]:
    """Create a new leave request"""
    try:
        # Get student ID from roll number
        student = await students_collection.find_one({"roll": args["student_roll"]})
        if not student:
            return [TextContent(type="text", text="Student not found")]
        
        start_date = datetime.strptime(args["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(args["end_date"], "%Y-%m-%d")
        total_days = (end_date - start_date).days + 1
        
        leave_data = {
            "student": student["_id"],
            "studentRoll": args["student_roll"],
            "startDate": start_date,
            "endDate": end_date,
            "reason": args["reason"],
            "comments": args.get("comments", ""),
            "totalDays": total_days,
            "status": "pending",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        result = await leave_requests_collection.insert_one(leave_data)
        return [TextContent(type="text", text=f"Leave request created successfully with ID: {result.inserted_id}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error creating leave request: {str(e)}")]

async def update_leave_request(args: Dict[str, Any]) -> List[TextContent]:
    """Update leave request status"""
    try:
        leave_id = ObjectId(args["leave_id"])
        update_data = {
            "status": args["status"],
            "handledBy": ObjectId(args["handled_by"]),
            "handledAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        if "comments" in args:
            update_data["comments"] = args["comments"]
        
        result = await leave_requests_collection.update_one(
            {"_id": leave_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return [TextContent(type="text", text="Leave request not found")]
        
        return [TextContent(type="text", text=f"Leave request {args['status']} successfully")]
    except InvalidId:
        return [TextContent(type="text", text="Invalid leave request ID format")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error updating leave request: {str(e)}")]

async def get_leave_requests(args: Dict[str, Any]) -> List[TextContent]:
    """Get leave requests with optional filtering"""
    try:
        query = {}
        
        if "student_roll" in args:
            query["studentRoll"] = args["student_roll"]
        if "status" in args:
            query["status"] = args["status"]
        if "date_range" in args:
            date_query = {}
            if "start" in args["date_range"]:
                date_query["$gte"] = datetime.strptime(args["date_range"]["start"], "%Y-%m-%d")
            if "end" in args["date_range"]:
                date_query["$lte"] = datetime.strptime(args["date_range"]["end"], "%Y-%m-%d")
            if date_query:
                query["startDate"] = date_query
        
        cursor = leave_requests_collection.find(query)
        leave_requests = await cursor.to_list(length=1000)
        return [TextContent(type="text", text=json.dumps(leave_requests, default=str))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting leave requests: {str(e)}")]

# Timetable Management Functions
async def create_timetable(args: Dict[str, Any]) -> List[TextContent]:
    """Create timetable for a day and semester"""
    try:
        # Process slots to convert course and faculty strings to ObjectIds if provided
        processed_slots = []
        for slot in args["slots"]:
            processed_slot = {
                "period": slot["period"],
                "type": slot["type"],
                "courseCode": slot["courseCode"],
                "room": slot.get("room")
            }
            
            # Convert course string to ObjectId if provided
            if "course" in slot and slot["course"]:
                try:
                    processed_slot["course"] = ObjectId(slot["course"])
                except InvalidId:
                    return [TextContent(type="text", text=f"Invalid course ObjectId: {slot['course']}")]
            
            # Convert faculty string to ObjectId if provided
            if "faculty" in slot and slot["faculty"]:
                try:
                    processed_slot["faculty"] = ObjectId(slot["faculty"])
                except InvalidId:
                    return [TextContent(type="text", text=f"Invalid faculty ObjectId: {slot['faculty']}")]
            
            processed_slots.append(processed_slot)
        
        timetable_data = {
            "dayOfWeek": args["dayOfWeek"],
            "semester": args["semester"],
            "slots": processed_slots,
            "isActive": True,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        result = await timetables_collection.insert_one(timetable_data)
        return [TextContent(type="text", text=f"Timetable created successfully with ID: {result.inserted_id}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error creating timetable: {str(e)}")]

async def get_timetable(args: Dict[str, Any]) -> List[TextContent]:
    """Get timetable for a specific day and semester"""
    try:
        timetable = await timetables_collection.find_one({
            "dayOfWeek": args["dayOfWeek"],
            "semester": args["semester"],
            "isActive": True
        })
        
        if not timetable:
            return [TextContent(type="text", text="Timetable not found")]
        
        return [TextContent(type="text", text=json.dumps(timetable, default=str))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting timetable: {str(e)}")]

async def get_weekly_timetable(args: Dict[str, Any]) -> List[TextContent]:
    """Get complete weekly timetable for a semester"""
    try:
        cursor = timetables_collection.find({
            "semester": args["semester"],
            "isActive": True
        })
        timetables = await cursor.to_list(length=1000)
        
        # Organize by day of week
        weekly_schedule = {}
        for timetable in timetables:
            weekly_schedule[timetable["dayOfWeek"]] = timetable
        
        return [TextContent(type="text", text=json.dumps(weekly_schedule, default=str))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting weekly timetable: {str(e)}")]

# Analytics and Complex Queries
async def get_erp_analytics(args: Dict[str, Any]) -> List[TextContent]:
    """Get comprehensive ERP analytics and insights"""
    try:
        analytics = {}
        
        # Student analytics
        total_students = await students_collection.count_documents({"isActive": True})
        analytics["students"] = {
            "total": total_students,
            "active": total_students,
            "inactive": await students_collection.count_documents({"isActive": False})
        }
        
        # Faculty analytics
        total_faculty = await faculty_collection.count_documents({"isActive": True})
        analytics["faculty"] = {
            "total": total_faculty,
            "active": total_faculty,
            "inactive": await faculty_collection.count_documents({"isActive": False})
        }
        
        # Course analytics
        total_courses = await courses_collection.count_documents({"isActive": True})
        analytics["courses"] = {
            "total": total_courses,
            "active": total_courses,
            "inactive": await courses_collection.count_documents({"isActive": False})
        }
        
        # Attendance analytics
        attendance_records = await attendance_collection.count_documents({})
        analytics["attendance"] = {
            "total_records": attendance_records
        }
        
        # Leave request analytics
        pending_requests = await leave_requests_collection.count_documents({"status": "pending"})
        approved_requests = await leave_requests_collection.count_documents({"status": "approved"})
        rejected_requests = await leave_requests_collection.count_documents({"status": "rejected"})
        
        analytics["leave_requests"] = {
            "pending": pending_requests,
            "approved": approved_requests,
            "rejected": rejected_requests,
            "total": pending_requests + approved_requests + rejected_requests
        }
        
        # Timetable analytics
        total_timetables = await timetables_collection.count_documents({"isActive": True})
        analytics["timetables"] = {
            "total": total_timetables
        }
        
        return [TextContent(type="text", text=json.dumps(analytics, default=str))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting analytics: {str(e)}")]

async def complex_query(args: Dict[str, Any]) -> List[TextContent]:
    """Execute complex queries across multiple collections"""
    try:
        query_type = args["query_type"]
        parameters = args.get("parameters", {})
        
        if query_type == "students_with_low_attendance":
            # Find students with attendance below threshold
            threshold = parameters.get("threshold", 75)
            cursor = attendance_collection.find({"attendancePercentage": {"$lt": threshold}})
            records = await cursor.to_list(length=1000)
            
            result = []
            for record in records:
                student = await students_collection.find_one({"roll": record["studentRoll"]})
                if student:
                    result.append({
                        "roll": record["studentRoll"],
                        "name": student["fullName"],
                        "attendance_percentage": record["attendancePercentage"],
                        "month": record["month"],
                        "year": record["year"]
                    })
            
            return [TextContent(type="text", text=json.dumps(result, default=str))]
        
        elif query_type == "faculty_workload":
            # Calculate faculty workload based on courses and timetables
            faculty_courses = {}
            cursor = courses_collection.find({"isActive": True})
            courses = await cursor.to_list(length=1000)
            
            for course in courses:
                if course.get("facultyInCharge"):
                    faculty_id = str(course["facultyInCharge"])
                    if faculty_id not in faculty_courses:
                        faculty_courses[faculty_id] = []
                    faculty_courses[faculty_id].append(course)
            
            result = []
            for faculty_id, courses_list in faculty_courses.items():
                faculty = await faculty_collection.find_one({"_id": ObjectId(faculty_id)})
                if faculty:
                    result.append({
                        "faculty_id": faculty_id,
                        "name": faculty["fullName"],
                        "courses_count": len(courses_list),
                        "courses": [{"code": c["code"], "title": c["title"]} for c in courses_list]
                    })
            
            return [TextContent(type="text", text=json.dumps(result, default=str))]
        
        elif query_type == "course_enrollment_stats":
            # Get course enrollment statistics
            cursor = courses_collection.find({"isActive": True})
            courses = await cursor.to_list(length=1000)
            
            result = []
            for course in courses:
                # Count students enrolled in this course (based on attendance records)
                student_count = await attendance_collection.distinct("studentRoll")
                result.append({
                    "course_code": course["code"],
                    "course_title": course["title"],
                    "semester": course["semester"],
                    "credits": course["credits"],
                    "faculty": course.get("facultyInCharge")
                })
            
            return [TextContent(type="text", text=json.dumps(result, default=str))]
        
        elif query_type == "leave_request_trends":
            # Analyze leave request trends
            cursor = leave_requests_collection.find()
            requests = await cursor.to_list(length=1000)
            
            # Group by month
            monthly_trends = {}
            for request in requests:
                year = request['startDate'].year
                month = request['startDate'].month
                month_key = f"{year}-{month:02d}"
                if month_key not in monthly_trends:
                    monthly_trends[month_key] = {"total": 0, "approved": 0, "rejected": 0, "pending": 0}
                
                monthly_trends[month_key]["total"] += 1
                monthly_trends[month_key][request["status"]] += 1
            
            return [TextContent(type="text", text=json.dumps(monthly_trends, default=str))]
        
        elif query_type == "timetable_conflicts":
            # Check for timetable conflicts
            cursor = timetables_collection.find({"isActive": True})
            timetables = await cursor.to_list(length=1000)
            
            conflicts = []
            for timetable in timetables:
                # Check for room-period conflicts within the same day
                room_period_map = {}
                for slot in timetable["slots"]:
                    if slot.get("room") and slot.get("period"):
                        room = slot["room"]
                        period = slot["period"]
                        key = f"{room}-{period}"
                        if key in room_period_map:
                            conflicts.append({
                                "day": timetable["dayOfWeek"],
                                "semester": timetable["semester"],
                                "room": room,
                                "period": period,
                                "conflict": f"Room {room} used in multiple slots at period {period}"
                            })
                        room_period_map[key] = slot
                
                # Check for faculty conflicts (same faculty teaching at same period)
                faculty_period_map = {}
                for slot in timetable["slots"]:
                    if slot.get("faculty") and slot.get("period"):
                        faculty = slot["faculty"]
                        period = slot["period"]
                        key = f"{faculty}-{period}"
                        if key in faculty_period_map:
                            conflicts.append({
                                "day": timetable["dayOfWeek"],
                                "semester": timetable["semester"],
                                "faculty": str(faculty),
                                "period": period,
                                "conflict": f"Faculty {faculty} assigned to multiple slots at period {period}"
                            })
                        faculty_period_map[key] = slot
            
            return [TextContent(type="text", text=json.dumps(conflicts, default=str))]
        
        else:
            return [TextContent(type="text", text=f"Unknown query type: {query_type}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing complex query: {str(e)}")]

# Main server execution
async def main():
    """Main server execution"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="erp-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
