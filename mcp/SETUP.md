# ERP MCP Server Setup Guide

## Virtual Environment Setup

This project uses a Python virtual environment for dependency isolation and management.

## Quick Start

### 1. Install and Setup
```bash
# Run the installation script
./install.sh
```

### 2. Start the Server
```bash
# Use the startup script (recommended)
./start_server.sh

# Or manually activate and run
source venv/bin/activate
python server.py
```

### 3. Test the Server
```bash
# Use the test script
./test_with_venv.sh

# Or manually
source venv/bin/activate
python test_client.py
```

## Manual Setup

### 1. Create Virtual Environment
```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Server
```bash
python server.py
```

## Virtual Environment Management

### Activate Virtual Environment
```bash
source venv/bin/activate
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Check Installed Packages
```bash
source venv/bin/activate
pip list
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

## Project Structure

```
mcp/
├── venv/                    # Virtual environment (created by install.sh)
├── server.py               # Main MCP server
├── requirements.txt        # Python dependencies
├── config.json            # Server configuration
├── install.sh             # Installation script
├── start_server.sh        # Server startup script
├── test_with_venv.sh      # Test script with venv
├── test_client.py         # Test client
├── .gitignore             # Git ignore file
├── README.md              # Documentation
├── USAGE.md               # Usage guide
└── SETUP.md               # This file
```

## Troubleshooting

### Virtual Environment Not Found
```bash
# Recreate virtual environment
rm -rf venv/
./install.sh
```

### Dependencies Issues
```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
brew services list | grep mongodb
# or
sudo systemctl status mongod
```

### Permission Issues
```bash
# Make scripts executable
chmod +x *.sh
```

## Development

### Adding New Dependencies
1. Activate virtual environment: `source venv/bin/activate`
2. Install new package: `pip install package_name`
3. Update requirements: `pip freeze > requirements.txt`

### Updating Dependencies
```bash
source venv/bin/activate
pip install --upgrade package_name
pip freeze > requirements.txt
```

## Production Deployment

### 1. Create Production Virtual Environment
```bash
python3 -m venv venv_prod
source venv_prod/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
export MONGODB_URI="mongodb://your-mongodb-host:27017/erp"
```

### 3. Run in Production
```bash
source venv_prod/bin/activate
python server.py
```

## Benefits of Virtual Environment

1. **Dependency Isolation**: Prevents conflicts with system Python packages
2. **Reproducible Environment**: Same dependencies across different machines
3. **Easy Cleanup**: Remove entire environment with `rm -rf venv/`
4. **Version Control**: requirements.txt tracks exact package versions
5. **Development Safety**: No risk of breaking system Python installation

## Scripts Overview

- **`install.sh`**: Creates virtual environment and installs dependencies
- **`start_server.sh`**: Activates venv and starts the MCP server
- **`test_with_venv.sh`**: Activates venv and runs tests
- **`.gitignore`**: Excludes virtual environment from version control
