#!/usr/bin/env python3
"""
Test script for the ERP MCP Server
"""

import asyncio
import json
from server import (
    get_student, create_student, search_students,
    get_faculty, create_faculty,
    get_course, create_course,
    get_erp_analytics, complex_query
)

async def test_basic_functionality():
    """Test basic MCP server functionality"""
    print("Testing ERP MCP Server...")
    
    # Test student creation
    print("\n1. Testing student creation...")
    try:
        result = await create_student({
            "roll": 1001,
            "fullName": "John Doe",
            "email": "john.doe@test.com",
            "phone": "+1234567890"
        })
        print(f"Student creation result: {result[0].text}")
    except Exception as e:
        print(f"Student creation error: {e}")
    
    # Test faculty creation
    print("\n2. Testing faculty creation...")
    try:
        result = await create_faculty({
            "employeeId": "EMP001",
            "fullName": "Dr. Jane Smith",
            "email": "jane.smith@test.com",
            "designation": "Professor",
            "subjectsHandled": ["Mathematics", "Statistics"]
        })
        print(f"Faculty creation result: {result[0].text}")
    except Exception as e:
        print(f"Faculty creation error: {e}")
    
    # Test course creation
    print("\n3. Testing course creation...")
    try:
        result = await create_course({
            "code": "MATH101",
            "title": "Introduction to Mathematics",
            "credits": 3,
            "semester": 1,
            "description": "Basic mathematics course"
        })
        print(f"Course creation result: {result[0].text}")
    except Exception as e:
        print(f"Course creation error: {e}")
    
    # Test analytics
    print("\n4. Testing analytics...")
    try:
        result = await get_erp_analytics({})
        print(f"Analytics result: {result[0].text}")
    except Exception as e:
        print(f"Analytics error: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
