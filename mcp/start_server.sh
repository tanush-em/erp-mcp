#!/bin/bash

# ERP MCP Server Startup Script with Virtual Environment

echo "Starting ERP MCP Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if MongoDB is running
echo "Checking MongoDB connection..."
if ! command -v mongod &> /dev/null; then
    echo "Warning: MongoDB not found. Please install MongoDB and ensure it's running on localhost:27017"
else
    echo "MongoDB found. Starting server..."
fi

# Start the server
echo "Starting MCP server..."
python server.py
