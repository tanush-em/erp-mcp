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
        ),
        Resource(
            uri="erp://dashboard",
            name="Live Dashboard",
            description="Real-time ERP system overview: counts, pending actions, at-risk students, and key metrics",
            mimeType="application/json"
        ),
        Resource(
            uri="erp://student/{roll}",
            name="Student by Roll",
            description="Dynamic resource to fetch individual student by roll number. Use erp://student/1001 for roll 1001",
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
    
    elif uri == "erp://dashboard":
        return await _get_dashboard_data()
    
    elif uri.startswith("erp://student/"):
        try:
            roll = int(uri.split("/")[-1])
            student = await students_collection.find_one({"roll": roll, "isActive": True})
            if not student:
                raise ValueError(f"Student with roll {roll} not found")
            # Enrich with attendance and leave info
            att = await attendance_collection.find_one({"studentRoll": roll}, sort=[("year", -1), ("month", 1)])
            leaves = await leave_requests_collection.find({"studentRoll": roll}).to_list(length=5)
            enriched = {**student, "recentAttendance": att, "recentLeaves": leaves}
            return json.dumps(enriched, default=str)
        except ValueError as e:
            raise e
        except (IndexError, ValueError):
            raise ValueError(f"Invalid student URI. Use erp://student/{{roll_number}}")
    
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
        ),
        
        # Advanced Features (Project Showcase)
        Tool(
            name="search_faculty",
            description="Search faculty by name, email, designation, or subjects they teach",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Search by name (partial match)"},
                    "email": {"type": "string", "description": "Search by email"},
                    "designation": {"type": "string", "description": "Filter by designation"},
                    "subject": {"type": "string", "description": "Find faculty who teach this subject"},
                    "isActive": {"type": "boolean", "description": "Filter by active status"}
                }
            }
        ),
        Tool(
            name="get_students_at_risk",
            description="Get students with low attendance who may need intervention (default threshold 75%)",
            inputSchema={
                "type": "object",
                "properties": {
                    "threshold": {"type": "integer", "description": "Attendance percentage threshold (default 75)", "default": 75},
                    "month": {"type": "string", "description": "Filter by month"},
                    "year": {"type": "integer", "description": "Filter by year"},
                    "limit": {"type": "integer", "description": "Max results to return (default 20)", "default": 20}
                }
            }
        ),
        Tool(
            name="get_pending_actions",
            description="Get a summary of items requiring attention: pending leave requests, low attendance alerts",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_leave_details": {"type": "boolean", "description": "Include full leave request details", "default": True}
                }
            }
        ),
        Tool(
            name="bulk_create_students",
            description="Create multiple students in one operation (useful for batch enrollment)",
            inputSchema={
                "type": "object",
                "required": ["students"],
                "properties": {
                    "students": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["roll", "fullName", "email", "phone"],
                            "properties": {
                                "roll": {"type": "integer"},
                                "fullName": {"type": "string"},
                                "email": {"type": "string"},
                                "phone": {"type": "string"}
                            }
                        }
                    }
                }
            }
        ),
        Tool(
            name="export_collection",
            description="Export a collection as JSON or CSV format for reports and backup",
            inputSchema={
                "type": "object",
                "required": ["collection"],
                "properties": {
                    "collection": {"type": "string", "enum": ["students", "faculties", "courses", "attendances", "leaverequests", "timetables"]},
                    "format": {"type": "string", "enum": ["json", "csv"], "default": "json"},
                    "filters": {"type": "object", "description": "Optional filters (e.g. isActive: true)"}
                }
            }
        ),
        Tool(
            name="get_executive_summary",
            description="Generate a human-readable executive summary report of the ERP system",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_recommendations": {"type": "boolean", "description": "Include AI-style recommendations", "default": True}
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
        elif name == "search_faculty":
            return await search_faculty(arguments)
        elif name == "get_students_at_risk":
            return await get_students_at_risk(arguments)
        elif name == "get_pending_actions":
            return await get_pending_actions(arguments)
        elif name == "bulk_create_students":
            return await bulk_create_students(arguments)
        elif name == "export_collection":
            return await export_collection(arguments)
        elif name == "get_executive_summary":
            return await get_executive_summary(arguments)
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

# Dashboard helper (for erp://dashboard resource)
async def _get_dashboard_data() -> str:
    """Generate real-time dashboard data"""
    total_students = await students_collection.count_documents({"isActive": True})
    total_faculty = await faculty_collection.count_documents({"isActive": True})
    total_courses = await courses_collection.count_documents({"isActive": True})
    pending_leaves = await leave_requests_collection.count_documents({"status": "pending"})
    
    low_attendance_cursor = attendance_collection.find({"attendancePercentage": {"$lt": 75}})
    at_risk = await low_attendance_cursor.to_list(length=50)
    at_risk_students = []
    for r in at_risk[:10]:
        s = await students_collection.find_one({"roll": r["studentRoll"]})
        if s:
            at_risk_students.append({"roll": r["studentRoll"], "name": s["fullName"], "percentage": r["attendancePercentage"]})
    
    dashboard = {
        "generatedAt": datetime.now().isoformat(),
        "summary": {
            "students": total_students,
            "faculty": total_faculty,
            "courses": total_courses,
        },
        "alerts": {
            "pendingLeaveRequests": pending_leaves,
            "studentsAtRiskCount": len(at_risk),
            "studentsAtRisk": at_risk_students,
        },
    }
    return json.dumps(dashboard, indent=2, default=str)

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

# Advanced Feature Implementations
async def search_faculty(args: Dict[str, Any]) -> List[TextContent]:
    """Search faculty by various criteria"""
    query = {}
    if "name" in args:
        query["fullName"] = {"$regex": args["name"], "$options": "i"}
    if "email" in args:
        query["email"] = args["email"]
    if "designation" in args:
        query["designation"] = {"$regex": args["designation"], "$options": "i"}
    if "subject" in args:
        query["subjectsHandled"] = {"$regex": args["subject"], "$options": "i"}
    if "isActive" in args:
        query["isActive"] = args["isActive"]
    
    cursor = faculty_collection.find(query)
    results = await cursor.to_list(length=100)
    return [TextContent(type="text", text=json.dumps(results, default=str))]

async def get_students_at_risk(args: Dict[str, Any]) -> List[TextContent]:
    """Get students with low attendance"""
    threshold = args.get("threshold", 75)
    limit = args.get("limit", 20)
    query = {"attendancePercentage": {"$lt": threshold}}
    if "month" in args:
        query["month"] = args["month"]
    if "year" in args:
        query["year"] = args["year"]
    
    cursor = attendance_collection.find(query).limit(limit)
    records = await cursor.to_list(length=limit)
    result = []
    for r in records:
        student = await students_collection.find_one({"roll": r["studentRoll"]})
        if student:
            result.append({
                "roll": r["studentRoll"],
                "name": student["fullName"],
                "attendance_percentage": r["attendancePercentage"],
                "month": r.get("month"),
                "year": r.get("year"),
            })
    return [TextContent(type="text", text=json.dumps(result, default=str))]

async def get_pending_actions(args: Dict[str, Any]) -> List[TextContent]:
    """Get items requiring attention"""
    pending_leaves = await leave_requests_collection.find({"status": "pending"}).to_list(length=50)
    low_att = await attendance_collection.find({"attendancePercentage": {"$lt": 75}}).to_list(length=20)
    
    leave_details = []
    if args.get("include_leave_details", True):
        for lr in pending_leaves:
            student = await students_collection.find_one({"roll": lr["studentRoll"]})
            leave_details.append({
                "id": str(lr["_id"]),
                "student_roll": lr["studentRoll"],
                "student_name": student["fullName"] if student else "Unknown",
                "start_date": lr["startDate"],
                "end_date": lr["endDate"],
                "reason": lr.get("reason", ""),
            })
    
    at_risk = []
    for r in low_att[:10]:
        s = await students_collection.find_one({"roll": r["studentRoll"]})
        if s:
            at_risk.append({"roll": r["studentRoll"], "name": s["fullName"], "percentage": r["attendancePercentage"]})
    
    summary = {
        "pending_leave_requests": len(pending_leaves),
        "leave_details": leave_details,
        "students_at_risk_count": len(low_att),
        "students_at_risk_preview": at_risk,
    }
    return [TextContent(type="text", text=json.dumps(summary, default=str))]

async def bulk_create_students(args: Dict[str, Any]) -> List[TextContent]:
    """Create multiple students"""
    students = args["students"]
    created = 0
    errors = []
    for s in students:
        try:
            data = {
                "roll": s["roll"],
                "fullName": s["fullName"],
                "email": s["email"],
                "phone": s["phone"],
                "isActive": True,
                "createdAt": datetime.now(),
                "updatedAt": datetime.now(),
            }
            await students_collection.insert_one(data)
            created += 1
        except DuplicateKeyError:
            errors.append(f"Roll {s['roll']} or email already exists")
        except Exception as e:
            errors.append(f"Roll {s['roll']}: {str(e)}")
    
    result = {"created": created, "total": len(students), "errors": errors}
    return [TextContent(type="text", text=json.dumps(result, default=str))]

async def export_collection(args: Dict[str, Any]) -> List[TextContent]:
    """Export collection as JSON or CSV"""
    coll_name = args["collection"]
    fmt = args.get("format", "json")
    filters = args.get("filters", {})
    
    coll_map = {
        "students": students_collection,
        "faculties": faculty_collection,
        "courses": courses_collection,
        "attendances": attendance_collection,
        "leaverequests": leave_requests_collection,
        "timetables": timetables_collection,
    }
    coll = coll_map.get(coll_name)
    if not coll:
        return [TextContent(type="text", text=f"Unknown collection: {coll_name}")]
    
    cursor = coll.find(filters)
    docs = await cursor.to_list(length=5000)
    
    if fmt == "json":
        return [TextContent(type="text", text=json.dumps(docs, indent=2, default=str))]
    
    if fmt == "csv" and docs:
        import csv
        import io
        keys = list(docs[0].keys())
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        for d in docs:
            row = {k: str(v) if not isinstance(v, (str, int, float, bool)) else v for k, v in d.items()}
            writer.writerow(row)
        return [TextContent(type="text", text=output.getvalue())]
    
    return [TextContent(type="text", text="No data to export")]

async def get_executive_summary(args: Dict[str, Any]) -> List[TextContent]:
    """Generate executive summary report"""
    include_recs = args.get("include_recommendations", True)
    
    total_students = await students_collection.count_documents({"isActive": True})
    total_faculty = await faculty_collection.count_documents({"isActive": True})
    total_courses = await courses_collection.count_documents({"isActive": True})
    pending_leaves = await leave_requests_collection.count_documents({"status": "pending"})
    at_risk_count = await attendance_collection.count_documents({"attendancePercentage": {"$lt": 75}})
    
    summary = [
        f"# ERP Executive Summary",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Overview",
        f"- **Students**: {total_students} active",
        f"- **Faculty**: {total_faculty} active",
        f"- **Courses**: {total_courses} active",
        "",
        "## Action Items",
        f"- **Pending leave requests**: {pending_leaves}",
        f"- **Students at risk** (attendance < 75%): {at_risk_count}",
        "",
    ]
    
    if include_recs:
        summary.extend([
            "## Recommendations",
            "- Review and process pending leave requests promptly" if pending_leaves else "- No pending leave requests",
            "- Follow up with at-risk students for attendance improvement" if at_risk_count else "- Attendance levels are healthy",
            "- Use get_students_at_risk and get_pending_actions for detailed lists",
        ])
    
    return [TextContent(type="text", text="\n".join(summary))]

# Main server execution
async def main():
    """Main server execution"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="erp-mcp-server",
                server_version="1.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(resources_changed=True),
                    experimental_capabilities={}
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
