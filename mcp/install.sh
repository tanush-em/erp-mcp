#!/bin/bash

# ERP MCP Server Installation Script with Virtual Environment

echo "Installing ERP MCP Server with Virtual Environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if MongoDB is running
echo "Checking MongoDB connection..."
if ! command -v mongod &> /dev/null; then
    echo "Warning: MongoDB not found. Please install MongoDB and ensure it's running on localhost:27017"
else
    echo "MongoDB found. Please ensure it's running on localhost:27017"
fi

# Make server executable
chmod +x server.py

echo "Installation completed!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the server:"
echo "  source venv/bin/activate && python server.py"
echo ""
echo "To test the server:"
echo "  source venv/bin/activate && python test_client.py"
echo ""
echo "To deactivate the virtual environment:"
echo "  deactivate"
echo ""
echo "Make sure MongoDB is running before starting the server."
