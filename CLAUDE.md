# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a ShiftAgent API built with FastAPI and Timefold Solver (AI optimization engine). The application optimizes employee shift assignments based on skills, work hours constraints, and fairness.

## Key Commands

### Development Setup
```bash
# Complete setup - installs all Python dependencies including FastMCP and pre-commit hooks (run this first!)
make setup

# Initialize Terraform for infrastructure
cd infrastructure && terraform init

# Test Azure Storage integration (requires Azure credentials)
python scripts/test_azure_storage_manual.py
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

# Start MCP server with HTTP transport (for web clients)
make mcp-http

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

### Git Hooks (pre-commit)
```bash
# Install pre-commit hooks (automatically runs during make setup)
make hooks-install

# Test all pre-commit hooks manually
make hooks-test

# Run pre-commit hooks on all files
uv run pre-commit run --all-files

# Skip pre-commit hooks for emergency commits
git commit --no-verify -m "emergency: fix critical issue"
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

### Infrastructure Management

```bash
# Navigate to infrastructure directory
cd infrastructure

# Initialize Terraform
terraform init

# Validate configuration
./scripts/validate.sh

# Deploy development environment
./scripts/deploy-dev.sh

# Deploy production environment
./scripts/deploy-prod.sh

# Plan specific environment
terraform plan -var-file="environments/dev.tfvars"
terraform plan -var-file="environments/prod.tfvars"

# Apply specific environment
terraform apply -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/prod.tfvars"

# Destroy environment (use with caution)
./scripts/destroy.sh dev
./scripts/destroy.sh prod

# View outputs
terraform output
```


## Architecture

### Folder Structure

```
src/
├── shiftagent/          # Main application package
│   ├── api/              # FastAPI application layer
│   │   ├── app.py        # FastAPI instance and configuration
│   │   ├── server.py     # Server entry point
│   │   ├── routes.py     # API endpoints
│   │   ├── schemas.py    # Pydantic request/response models
│   │   ├── solver.py     # Timefold solver configuration
│   │   ├── jobs.py       # Async job management
│   │   ├── job_store.py  # Job persistence abstraction
│   │   ├── azure_job_store.py # Azure Blob Storage implementation
│   │   ├── converters.py # Domain <-> API model converters
│   │   ├── analysis.py   # Weekly hours analysis logic
│   │   ├── problem_fact_changes.py # Dynamic problem updates
│   │   └── shift-schedule-template.html # HTML template
│   ├── config/           # Configuration management
│   │   └── storage_config.py # Storage configuration utilities
│   ├── core/             # Domain logic
│   │   ├── models/       # Domain models with Timefold annotations
│   │   │   ├── employee.py   # Employee entity
│   │   │   ├── shift.py      # Shift planning entity
│   │   │   └── schedule.py   # ShiftSchedule planning solution
│   │   └── constraints/  # Optimization constraints
│   │       └── shift_constraints.py
│   ├── templates/        # HTML template rendering
│   │   ├── renderer.py   # Template renderer utilities
│   │   └── schedule_report.html # Schedule report template
│   ├── utils/            # Utilities
│   │   └── demo_data.py  # Demo data generation
│   └── streamlit_app.py  # Streamlit web UI
└── shiftagent_mcp/      # MCP server package (separate)
    ├── server.py         # FastMCP server setup and tool registration
    └── tools.py          # MCP tool functions for shift scheduling

docker/                   # Docker configuration
├── dockerfiles/          # Container definitions
│   ├── Dockerfile.api    # Main API service
│   ├── Dockerfile.mcp    # MCP server (stdio)
│   ├── Dockerfile.mcp.http # MCP server (HTTP)
│   └── Dockerfile.mcp.sse  # MCP server (SSE)
└── compose/              # Docker Compose configurations
    ├── docker-compose.yml     # Development environment
    ├── docker-compose.prod.yml # Production environment
    ├── docker-compose.mcp.yml  # MCP server management
    └── docker-compose.n8n.yml  # n8n integration

scripts/                  # Utility scripts
├── run-mcp-server.sh     # MCP server launcher
├── docker_mcp.sh         # Docker MCP management
├── test_mcp_connection.sh # MCP connection testing
├── mock_mcp_server.py    # MCP protocol mock server
├── run_mcp_http.py       # HTTP MCP server runner
├── run_mcp_sse.py        # SSE MCP server runner
└── test_azure_storage_manual.py # Azure storage testing

Dockerfile                # Default Dockerfile for CI/CD (references API service)
```

### Core Components

1. **shiftagent/api/server.py**: API server entry point
   - Entry point for `shiftagent-api` command (defined in pyproject.toml)
   - Can be run directly with `python -m shiftagent.api.server`
   - Used by Docker containers
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

5. **shiftagent_mcp** (separate package): MCP server for AI assistants
   - `src/shiftagent_mcp/server.py`: FastMCP server setup and tool registration
   - `src/shiftagent_mcp/tools.py`: MCP tool functions for shift scheduling
   - Entry point: `python -m shiftagent_mcp.server`

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

#### Employee Management
- `POST /api/shifts/{job_id}/add-employee`: Add single employee to completed job
- `PATCH /api/shifts/{job_id}/employee/{employee_id}/skills`: Update employee skills and re-optimize

#### Job Management
- `GET /api/jobs`: List all jobs with status
- `DELETE /api/jobs/{job_id}`: Delete specific job
- `POST /api/jobs/cleanup`: Clean up old jobs

#### Report Generation
- `GET /api/shifts/demo/html`: Demo schedule as HTML report
- `GET /api/shifts/solve/{job_id}/html`: Optimization result as HTML report
- `POST /api/shifts/solve-sync/html`: Synchronous solve with HTML report


## Development Notes

### Dependencies
- Python 3.11+ required (3.13+ not supported by Timefold)
- Java 17 required (for Timefold Solver)
- Uses `uv` for Python dependency management
- Uses `pre-commit` for git hooks and code quality
- FastAPI for web framework
- Timefold Solver for constraint optimization

### Testing
Tests use pytest and are located in `tests/` directory. Run a single test with:
```bash
uv run pytest tests/test_models.py::test_name -v
```

### Common Issues
1. If `uv sync` fails, delete `uv.lock` and run `make setup`
2. Java environment must be properly configured (JAVA_HOME)
3. Port 8081 must be available for the server
4. If pre-commit hooks fail, run `make hooks-install` to reinstall them

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
- **SAS token support**: Secure access with time-limited tokens
- **High availability**: Azure-managed redundancy and backup
- **Managed identity support**: Secure authentication without connection strings

#### Testing Azure Storage
```bash
# Test Azure Storage integration
python scripts/test_azure_storage_manual.py

# Run tests with Azure storage backend
JOB_STORAGE_TYPE=azure make test
```

## MCP Server

The project includes a Python-based MCP (Model Context Protocol) server using FastMCP that exposes the ShiftAgent API as MCP tools. The MCP server is implemented as a separate package `shiftagent_mcp` to maintain clean separation of concerns.

### MCP Server Architecture
- **Package**: `src/shiftagent_mcp/` (separate from main shiftagent package)
- **Entry point**: `python -m shiftagent_mcp.server`
- **Protocol**: FastMCP for Model Context Protocol implementation

### MCP Server Setup
The MCP server uses FastMCP and is automatically set up when you run `make setup`.

**Default (stdio transport for Claude Desktop):**
```bash
make run-mcp  # Run both API and MCP servers
make mcp      # Run MCP server only (uses python -m shiftagent_mcp.server)
```

**HTTP Transport (for web clients):**
```bash
make mcp-http  # Run with HTTP transport on port 8083

# With custom configuration
MCP_HTTP_PORT=8084 MCP_HTTP_HOST=0.0.0.0 make mcp-http
```

**SSE Transport (deprecated, for legacy clients):**
```bash
make mcp-sse  # Run with SSE transport on port 8084

# With custom configuration
MCP_SSE_PORT=8085 MCP_SSE_HOST=0.0.0.0 make mcp-sse
```

The HTTP transport enables web-based deployments and supports multiple concurrent clients. SSE transport is deprecated but available for backward compatibility.

### Available MCP Tools

#### Basic Operations
- `health_check`: Check API health
- `get_demo_schedule`: Get demo shift schedule
- `solve_schedule_sync`: Synchronous shift optimization
- `solve_schedule_async`: Asynchronous shift optimization
- `get_solve_status`: Check async job status
- `analyze_weekly_hours`: Analyze weekly work hours
- `test_weekly_constraints`: Test weekly constraints with demo data

#### Employee Management
- `add_employee_to_job`: Add single employee to completed job with minimal re-optimization
- `update_employee_skills`: Update employee skills and re-optimize affected assignments

#### Schedule Inspection
- `get_schedule_shifts`: Get all shifts from a completed schedule for inspection

#### Report Generation
- `get_demo_schedule_html`: Get demo schedule as formatted HTML report
- `get_schedule_html_report`: Get completed schedule as HTML report
- `solve_schedule_sync_html`: Solve and return HTML report in one step

See `MCP_SERVER.md` for detailed usage and Claude Desktop integration instructions.
See `DOCKER_MCP.md` for running MCP servers in Docker containers with HTTP/SSE transport.

## Git Workflow Rules

**CRITICAL: Always use Pull Request workflow. NEVER push directly to main branch.**

### Required Workflow
1. **Create feature branch** for all changes:
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/your-fix-name
   ```

2. **Make changes and commit** to feature branch:
   ```bash
   git add .
   git commit -m "descriptive commit message"
   git push -u origin feat/your-feature-name
   ```

3. **Create Pull Request** for review:
   ```bash
   gh pr create --title "..." --body "..."
   ```

4. **Wait for review and merge** - never merge your own PRs immediately

### Prohibited Actions
- ❌ `git push origin main` (direct push to main)
- ❌ Working directly on main branch
- ❌ Force pushing to shared branches
- ❌ Merging without review (except in emergencies)

### Branch Naming Convention
- `feat/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `chore/` - Maintenance tasks

### Emergency Exception
Only in critical production issues:
```bash
git commit --no-verify -m "emergency: fix critical issue"
# Still create PR immediately after
```

**Remember: This protects main branch stability and enables proper code review.**
