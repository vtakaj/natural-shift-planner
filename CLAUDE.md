# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Shift Scheduler API built with FastAPI and Timefold Solver (AI optimization engine). The application optimizes employee shift assignments based on skills, work hours constraints, and fairness.

## Key Commands

### Development Setup
```bash
# Complete setup - installs all Python dependencies including FastMCP and Bun dependencies (run this first!)
make setup

# Initialize Pulumi for infrastructure (if working with infrastructure)
make pulumi-setup

# Test Azure Storage integration (requires Azure credentials)
python scripts/test_azure_storage.py
```

### Running the Application
```bash
# Start FastAPI server only
make run

# Start with extended solver timeout (5 minutes)
SOLVER_TIMEOUT_SECONDS=300 make run

# Start with verbose solver logging
SOLVER_LOG_LEVEL=DEBUG make run

# Start with all optimizations
SOLVER_TIMEOUT_SECONDS=300 SOLVER_LOG_LEVEL=DEBUG make run

# Start both API and MCP servers together
make run-mcp

# Start in debug mode with verbose logging
make debug

# Start Streamlit web UI (requires API to be running)
make streamlit
```

### Testing
```bash
# Run all tests
make test

# Test API endpoints (server must be running)
make test-api
```

### Code Quality
```bash
# Format code with ruff
make format

# Run linters (ruff, mypy)
make lint
```

### Troubleshooting
```bash
# Check environment
make check

# Full troubleshooting info
make troubleshoot

# Clean cache and Python artifacts
make clean
```

## Architecture

### Folder Structure

```
src/natural_shift_planner/
├── api/              # FastAPI application layer
│   ├── app.py        # FastAPI instance and configuration
│   ├── routes.py     # API endpoints
│   ├── schemas.py    # Pydantic request/response models
│   ├── solver.py     # Timefold solver configuration
│   ├── jobs.py       # Async job management
│   ├── job_store.py  # Job persistence abstraction
│   ├── azure_job_store.py # Azure Blob Storage implementation
│   ├── converters.py # Domain <-> API model converters
│   └── analysis.py   # Weekly hours analysis logic
├── config/           # Configuration management
│   └── storage_config.py # Storage configuration utilities
├── core/             # Domain logic
│   ├── models/       # Domain models with Timefold annotations
│   │   ├── employee.py   # Employee entity
│   │   ├── shift.py      # Shift planning entity
│   │   └── schedule.py   # ShiftSchedule planning solution
│   └── constraints/  # Optimization constraints
│       └── shift_constraints.py
├── mcp/              # MCP server for AI assistants
│   ├── server.py     # FastMCP server setup
│   └── tools.py      # MCP tool functions
└── utils/            # Utilities
    └── demo_data.py  # Demo data generation
```

### Core Components

1. **main.py**: Entry point that imports and runs the FastAPI app
   - Adds src directory to Python path
   - Starts the API server on port 8081

2. **api/routes.py**: API endpoints for shift optimization
   - Defines all REST endpoints
   - Manages async job processing
   - Handles request/response conversion

3. **core/models/**: Domain models using Timefold annotations
   - `Employee`: Has skills, assigned to shifts
   - `Shift`: Planning entity with time, location, required skills
   - `ShiftSchedule`: Planning solution containing employees and shifts

4. **core/constraints/shift_constraints.py**: Optimization rules
   - Hard constraints: skill matching, no overlapping shifts, max weekly hours
   - Medium constraints: minimum rest time, minimum weekly hours
   - Soft constraints: minimize unassigned shifts, fair workload distribution

5. **mcp_server.py**: Entry point for MCP server
   - Exposes shift scheduler functionality to AI assistants
   - Uses FastMCP for protocol implementation

### Constraint System

The solver optimizes using HardMediumSoftScore:
- Hard constraints must be satisfied (skill requirements, no double-booking)
- Medium constraints are important but can be violated (8-hour rest periods)
- Soft constraints are optimization goals (fairness, target hours)

### Date Format Specification

**Employee Unavailable Dates**:
- **Format**: ISO 8601 (`YYYY-MM-DDTHH:MM:SS` or `YYYY-MM-DD`)
- **Examples**: 
  - `"2024-01-15T00:00:00"` (with time)
  - `"2024-01-15"` (date only)
  - `"2024-12-25T09:30:00"` (specific time)
- **Behavior**: Time component is optional and normalized to date-only for comparison
- **Use Cases**: Employee vacation days, sick leave, personal unavailability

**Shift Times**:
- **Format**: ISO 8601 with time (`YYYY-MM-DDTHH:MM:SS`)
- **Examples**: 
  - `"2024-01-15T09:00:00"` (9:00 AM start)
  - `"2024-01-15T17:30:00"` (5:30 PM end)

### API Endpoints

#### Basic Operations
- `GET /health`: Health check
- `GET /api/shifts/demo`: Demo data with sample schedule
- `POST /api/shifts/solve-sync`: Synchronous optimization (blocks until complete)
- `POST /api/shifts/solve`: Async optimization (returns job ID)
- `GET /api/shifts/solve/{job_id}`: Get optimization results
- `POST /api/shifts/analyze-weekly`: Analyze weekly work hours
- `GET /api/shifts/test-weekly`: Test weekly constraint calculations

#### Employee Management (New Feature)
- `POST /api/shifts/{job_id}/add-employee`: Add single employee to completed job
- `PATCH /api/shifts/{job_id}/employee/{employee_id}/skills`: Update employee skills and re-optimize
- `POST /api/shifts/{job_id}/reassign`: Reassign shift to specific employee or unassign

#### Job Management
- `GET /api/jobs`: List all jobs with status
- `DELETE /api/jobs/{job_id}`: Delete specific job
- `POST /api/jobs/cleanup`: Clean up old jobs


## Development Notes

### Dependencies
- Python 3.11+ required (3.13+ not supported by Timefold)
- Java 17 required (for Timefold Solver)
- Uses `uv` for Python dependency management
- Uses `bun` for Node.js dependency management (Husky, commitlint)
- FastAPI for web framework
- Timefold Solver for constraint optimization

### Testing
Tests use pytest and are located in `test_models.py`. Run a single test with:
```bash
uv run pytest test_models.py::test_name -v
```

### Common Issues
1. If `uv sync` fails, delete `uv.lock` and run `make setup`
2. Java environment must be properly configured (JAVA_HOME)
3. Port 8081 must be available for the server
4. If `bun install` fails, ensure bun is installed: `curl -fsSL https://bun.sh/install | bash`

### API Testing
The `api-test.http` file contains REST Client requests for testing endpoints. Use with VS Code REST Client extension or similar tools.

### Storage Configuration

The application supports multiple storage backends for job data persistence:

#### File System Storage (Default)
```bash
export JOB_STORAGE_TYPE=filesystem
export JOB_STORAGE_DIR=./job_storage
```

#### Azure Blob Storage
```bash
export JOB_STORAGE_TYPE=azure
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
# OR use managed identity
export AZURE_STORAGE_ACCOUNT_NAME="mystorageaccount"
export AZURE_STORAGE_CONTAINER_NAME="job-data"  # Optional, defaults to "job-data"
```

#### Azure Storage Features
- **Automatic lifecycle management**: Job data deleted after 30 days, logs archived and cleaned up
- **SAS token support**: Secure access with time-limited tokens
- **High availability**: Azure-managed redundancy and backup
- **Managed identity support**: Secure authentication without connection strings

#### Testing Azure Storage
```bash
# Test Azure Storage integration
python scripts/test_azure_storage.py

# Run tests with Azure storage backend
JOB_STORAGE_TYPE=azure make test
```

## MCP Server

The project includes a Python-based MCP (Model Context Protocol) server using FastMCP that exposes the Shift Scheduler API as MCP tools.

### MCP Server Setup
The MCP server uses FastMCP and is automatically set up when you run `make setup`. To run both servers together:
```bash
make run-mcp
```

Or run the MCP server separately:
```bash
make mcp
```

### Available MCP Tools

#### Basic Operations
- `health_check`: Check API health
- `get_demo_schedule`: Get demo shift schedule
- `solve_schedule_sync`: Synchronous shift optimization
- `solve_schedule_async`: Asynchronous shift optimization
- `get_solve_status`: Check async job status
- `analyze_weekly_hours`: Analyze weekly work hours
- `test_weekly_constraints`: Test weekly constraints with demo data

#### Employee Management (Available Now)
- `add_employee_to_job`: Add single employee to completed job with minimal re-optimization
- `update_employee_skills`: Update employee skills and re-optimize affected assignments
- `reassign_shift`: Reassign shift to specific employee or unassign it

#### Schedule Inspection
- `get_schedule_shifts`: Get all shifts from a completed schedule for inspection

#### Report Generation
- `get_demo_schedule_html`: Get demo schedule as formatted HTML report
- `get_schedule_html_report`: Get completed schedule as HTML report
- `solve_schedule_sync_html`: Solve and return HTML report in one step

See `MCP_SERVER.md` for detailed usage and Claude Desktop integration instructions.