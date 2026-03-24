# Enhancing ERP with Model Context Protocol (MCP) Servers

A modern Enterprise Resource Planning (ERP) system enhanced with Model Context Protocol (MCP) servers for intelligent, context-aware business process automation. Built for educational institutions with student, faculty, course, attendance, leave, and timetable management.

## Overview

This project integrates MCP servers with traditional ERP functionality to create a more intelligent and responsive business management system. The integration enables:

- **Natural language access** to ERP data via AI assistants (Cursor, Claude Desktop, etc.)
- **Predictive analytics** and at-risk student identification
- **Bulk operations** and export capabilities for administrative workflows
- **Live dashboard** and executive reporting
- **Dynamic resources** with parameterized URIs

## Key Features for Evaluators

### 🔧 **28+ MCP Tools**
Full CRUD for students, faculty, courses, attendance, leave requests, and timetables—all accessible via natural language.

### 📊 **Advanced Analytics**
- `get_erp_analytics` – System-wide statistics
- `get_students_at_risk` – Students below attendance threshold (configurable)
- `get_pending_actions` – Leave requests + at-risk students requiring attention
- `get_executive_summary` – Human-readable report with recommendations
- `complex_query` – Faculty workload, leave trends, timetable conflicts

### 📦 **Bulk & Export Operations**
- `bulk_create_students` – Batch enrollment
- `export_collection` – JSON or CSV export for reports/backup

### 🔍 **Enhanced Search**
- `search_students` – By name, email, roll range
- `search_faculty` – By name, email, designation, **or subjects taught**

### 📁 **Dynamic MCP Resources**
| Resource | Description |
|----------|-------------|
| `erp://dashboard` | Real-time overview: counts, pending actions, at-risk students |
| `erp://student/{roll}` | Individual student with attendance & leave history |
| `erp://students`, `erp://faculty`, etc. | Full collection exports |

### 🧠 **Context-Aware Design**
System instructions define tone, response formatting, and domain-specific behaviors (e.g., highlight low attendance, prioritize pending leaves).

## Setup

1. **Prerequisites**: Python 3.10+, MongoDB
2. **Install**: `./mcp/install.sh` (creates venv, installs deps)
3. **Start MongoDB**: `brew services start mongodb-community` or `mongod`
4. **Run MCP Server**: `./mcp/start_server.sh`

## Cursor Integration

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "erp": {
      "command": "path/to/erp-mcp/mcp/start_server.sh",
      "env": {
        "MONGODB_URI": "mongodb://localhost:27017/erp"
      }
    }
  }
}
```

## Example Prompts (Try in Cursor/Claude)

- *"Show me students with attendance below 75%"*
- *"What leave requests are pending?"*
- *"Generate an executive summary of the ERP system"*
- *"Search for faculty who teach Mathematics"*
- *"Export the students collection as CSV"*
- *"Create 3 new students: Roll 2001 John Doe, 2002 Jane Smith, 2003 Bob Wilson"*

## Architecture

```
erp-mcp/
├── mcp/
│   ├── server.py          # MCP server (resources, tools, handlers)
│   ├── system_instructions.json
│   └── config.json
├── erp/                   # Next.js ERP frontend
└── README.md
```

## Contact

For questions or support, please open an issue in the repository or contact the maintainers.
