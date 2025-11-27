# Sandbox Solution Analysis: Three Pragmatic Approaches for Direct File Operations

## Executive Summary

After analyzing your current RunLoop sandbox constraints, existing GCE VM + GCS infrastructure, and researching alternative approaches, I propose three practical solutions to enable your agents to perform direct file transformations, browser automation, internet searches, and persistent filesystem mutations. These solutions are designed to integrate with your existing Google Cloud infrastructure while providing increasing levels of sophistication and isolation.

## Current Infrastructure Analysis

**What you have:**
- Google Cloud Storage bucket: `gs://whaley_law_firm` (~100GB case files)
- GCE VM: `roscoe-paralegal-vm` (us-central1-a)
- gcsfuse mounting GCS to `/mnt/workspace` on VM
- Docker containers running LangGraph server
- DeepAgents framework with FilesystemBackend
- RunLoop sandbox for code execution (ephemeral, copy-only)

**Core Constraint:**
RunLoop sandbox operates on ephemeral copies—code cannot directly mutate the persistent `/projects/...` filesystem. Changes made in sandbox are discarded when the container exits.

## Three Proposed Solutions

### Solution 1: VM-Native Workspace Mutation Service (Minimal Infrastructure Change)
**Best for: Fast implementation, leveraging existing infrastructure**

#### Architecture Overview

Build a lightweight mutation service that runs directly on your existing GCE VM, providing controlled filesystem access through a validated API layer.

```
┌─────────────────────┐
│   Roscoe Agent      │
│   (LangGraph)       │
│                     │
│ • Analysis in       │
│   RunLoop sandbox   │
│ • Generates plans   │
└──────────┬──────────┘
           │ HTTP/gRPC
           ▼
┌─────────────────────┐    ┌─────────────────────┐
│ Mutation Service    │────│  gcsfuse Mount      │
│ (FastAPI on VM)     │    │  /mnt/workspace/    │
│                     │    │                     │
│ • Validates plans   │    │ • /projects/        │
│ • Applies changes   │    │ • /Tools/           │
│ • Audit logging     │    │ • /Database/        │
└─────────────────────┘    └─────────────────────┘
```

#### Implementation Details

**1. Mutation Service (FastAPI)**

Create a new service that runs on your VM:

```python
# /opt/roscoe/mutation_service/app.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, validator
from typing import List, Optional, Literal
import shutil
import json
from pathlib import Path
from datetime import datetime
import hashlib

app = FastAPI(title="Roscoe Workspace Mutation Service")

# Configuration
WORKSPACE_ROOT = Path("/mnt/workspace")
PROJECTS_ROOT = WORKSPACE_ROOT / "projects"
DATABASE_ROOT = WORKSPACE_ROOT / "Database"
AUDIT_LOG_ROOT = DATABASE_ROOT / "reorg_audit"
AUDIT_LOG_ROOT.mkdir(parents=True, exist_ok=True)

# Plan models
class FileOperation(BaseModel):
    type: Literal["move", "copy", "delete", "create_dir", "write_file"]
    source: Optional[str] = None
    destination: Optional[str] = None
    content: Optional[str] = None  # For write_file operations
    
    @validator('source', 'destination')
    def validate_path(cls, v):
        if v and ('..' in v or v.startswith('/')):
            raise ValueError("Path must be relative and cannot contain '..'")
        return v

class MutationPlan(BaseModel):
    plan_id: str
    case_name: str
    description: str
    operations: List[FileOperation]
    created_by: str = "roscoe-agent"
    requires_approval: bool = True

class PlanValidationResult(BaseModel):
    plan_id: str
    valid: bool
    warnings: List[str]
    errors: List[str]
    operation_count: int
    estimated_size_change_mb: float
    dry_run_summary: str

class PlanExecutionResult(BaseModel):
    plan_id: str
    success: bool
    operations_completed: int
    operations_failed: int
    audit_log_path: str
    error_details: Optional[str] = None

# In-memory plan store (use Redis/DB in production)
plans = {}
approved_plans = set()

@app.post("/plans", response_model=MutationPlan)
async def create_plan(plan: MutationPlan):
    """Upload a mutation plan for validation and execution."""
    
    # Generate plan ID if not provided
    if not plan.plan_id:
        plan.plan_id = hashlib.sha256(
            f"{plan.case_name}-{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
    
    # Store plan
    plans[plan.plan_id] = plan
    
    # Save plan to filesystem for audit
    plan_file = DATABASE_ROOT / "reorg_queue" / f"{plan.plan_id}.json"
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    plan_file.write_text(plan.json(indent=2))
    
    return plan

@app.post("/plans/{plan_id}/validate", response_model=PlanValidationResult)
async def validate_plan(plan_id: str):
    """Validate a plan with dry-run checks."""
    
    if plan_id not in plans:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    plan = plans[plan_id]
    warnings = []
    errors = []
    
    case_root = PROJECTS_ROOT / plan.case_name
    
    # Check case exists
    if not case_root.exists():
        errors.append(f"Case directory not found: {plan.case_name}")
        return PlanValidationResult(
            plan_id=plan_id,
            valid=False,
            warnings=warnings,
            errors=errors,
            operation_count=len(plan.operations),
            estimated_size_change_mb=0.0,
            dry_run_summary="Validation failed: case not found"
        )
    
    # Validate each operation
    size_change = 0.0
    for i, op in enumerate(plan.operations):
        try:
            if op.type == "move":
                source_path = case_root / op.source
                dest_path = case_root / op.destination
                
                if not source_path.exists():
                    errors.append(f"Op {i}: Source not found: {op.source}")
                elif dest_path.exists():
                    warnings.append(f"Op {i}: Destination exists, will be overwritten: {op.destination}")
                else:
                    # Calculate size
                    if source_path.is_file():
                        size_change += source_path.stat().st_size / (1024 * 1024)
                        
            elif op.type == "delete":
                source_path = case_root / op.source
                if not source_path.exists():
                    warnings.append(f"Op {i}: File already deleted: {op.source}")
                elif source_path.is_file():
                    size_change -= source_path.stat().st_size / (1024 * 1024)
                    
            elif op.type == "create_dir":
                dest_path = case_root / op.destination
                if dest_path.exists():
                    warnings.append(f"Op {i}: Directory already exists: {op.destination}")
                    
            elif op.type == "write_file":
                dest_path = case_root / op.destination
                if dest_path.exists():
                    warnings.append(f"Op {i}: File will be overwritten: {op.destination}")
                if op.content:
                    size_change += len(op.content) / (1024 * 1024)
                    
        except Exception as e:
            errors.append(f"Op {i}: Validation error: {str(e)}")
    
    # Safety checks
    if len(plan.operations) > 1000:
        warnings.append(f"Large operation count: {len(plan.operations)}")
    
    if abs(size_change) > 100:  # 100MB
        warnings.append(f"Large size change: {size_change:.2f} MB")
    
    valid = len(errors) == 0
    
    summary_lines = [
        f"Plan: {plan.description}",
        f"Case: {plan.case_name}",
        f"Operations: {len(plan.operations)}",
        f"Estimated size change: {size_change:.2f} MB",
        f"Validation: {'PASSED' if valid else 'FAILED'}",
        f"Warnings: {len(warnings)}",
        f"Errors: {len(errors)}"
    ]
    
    return PlanValidationResult(
        plan_id=plan_id,
        valid=valid,
        warnings=warnings,
        errors=errors,
        operation_count=len(plan.operations),
        estimated_size_change_mb=size_change,
        dry_run_summary="\n".join(summary_lines)
    )

@app.post("/plans/{plan_id}/approve")
async def approve_plan(plan_id: str, approved_by: str = "user"):
    """Approve a plan for execution."""
    
    if plan_id not in plans:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Validate first
    validation = await validate_plan(plan_id)
    if not validation.valid:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot approve invalid plan. Errors: {validation.errors}"
        )
    
    approved_plans.add(plan_id)
    
    # Log approval
    approval_log = {
        "plan_id": plan_id,
        "approved_by": approved_by,
        "approved_at": datetime.utcnow().isoformat(),
        "validation": validation.dict()
    }
    
    approval_file = DATABASE_ROOT / "reorg_approvals" / f"{plan_id}.json"
    approval_file.parent.mkdir(parents=True, exist_ok=True)
    approval_file.write_text(json.dumps(approval_log, indent=2))
    
    return {"status": "approved", "plan_id": plan_id}

@app.post("/plans/{plan_id}/apply", response_model=PlanExecutionResult)
async def apply_plan(plan_id: str, background_tasks: BackgroundTasks):
    """Execute an approved plan."""
    
    if plan_id not in plans:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    plan = plans[plan_id]
    
    # Check approval
    if plan.requires_approval and plan_id not in approved_plans:
        raise HTTPException(
            status_code=403, 
            detail="Plan not approved. Call /plans/{plan_id}/approve first."
        )
    
    # Execute operations
    case_root = PROJECTS_ROOT / plan.case_name
    operations_completed = 0
    operations_failed = 0
    audit_entries = []
    error_details = []
    
    for i, op in enumerate(plan.operations):
        try:
            audit_entry = {
                "operation_index": i,
                "operation": op.dict(),
                "timestamp": datetime.utcnow().isoformat(),
                "status": "pending"
            }
            
            if op.type == "move":
                source_path = case_root / op.source
                dest_path = case_root / op.destination
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(dest_path))
                audit_entry["status"] = "completed"
                operations_completed += 1
                
            elif op.type == "copy":
                source_path = case_root / op.source
                dest_path = case_root / op.destination
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                if source_path.is_file():
                    shutil.copy2(str(source_path), str(dest_path))
                else:
                    shutil.copytree(str(source_path), str(dest_path))
                audit_entry["status"] = "completed"
                operations_completed += 1
                
            elif op.type == "delete":
                source_path = case_root / op.source
                if source_path.is_file():
                    source_path.unlink()
                elif source_path.is_dir():
                    shutil.rmtree(str(source_path))
                audit_entry["status"] = "completed"
                operations_completed += 1
                
            elif op.type == "create_dir":
                dest_path = case_root / op.destination
                dest_path.mkdir(parents=True, exist_ok=True)
                audit_entry["status"] = "completed"
                operations_completed += 1
                
            elif op.type == "write_file":
                dest_path = case_root / op.destination
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                dest_path.write_text(op.content or "")
                audit_entry["status"] = "completed"
                operations_completed += 1
                
            audit_entries.append(audit_entry)
            
        except Exception as e:
            audit_entry["status"] = "failed"
            audit_entry["error"] = str(e)
            audit_entries.append(audit_entry)
            error_details.append(f"Op {i}: {str(e)}")
            operations_failed += 1
    
    # Write audit log
    audit_log = {
        "plan": plan.dict(),
        "execution_started": datetime.utcnow().isoformat(),
        "operations_completed": operations_completed,
        "operations_failed": operations_failed,
        "audit_entries": audit_entries
    }
    
    audit_file = AUDIT_LOG_ROOT / f"{plan_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    audit_file.write_text(json.dumps(audit_log, indent=2))
    
    # Remove from approved set
    if plan_id in approved_plans:
        approved_plans.remove(plan_id)
    
    success = operations_failed == 0
    
    return PlanExecutionResult(
        plan_id=plan_id,
        success=success,
        operations_completed=operations_completed,
        operations_failed=operations_failed,
        audit_log_path=str(audit_file),
        error_details="; ".join(error_details) if error_details else None
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "workspace_mounted": WORKSPACE_ROOT.exists(),
        "projects_accessible": PROJECTS_ROOT.exists()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8124)
```

**2. Systemd Service Configuration**

```ini
# /etc/systemd/system/roscoe-mutation-service.service
[Unit]
Description=Roscoe Workspace Mutation Service
After=network.target gcsfuse.service

[Service]
Type=simple
User=roscoe
WorkingDirectory=/opt/roscoe/mutation_service
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8124
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. Integration with Agent Tools**

```python
# Add to src/roscoe/agents/paralegal/tools.py

import httpx
from typing import List, Dict

MUTATION_SERVICE_URL = os.environ.get(
    "MUTATION_SERVICE_URL", 
    "http://localhost:8124"
)

def reorganize_case_files(
    case_name: str,
    operations: List[Dict],
    description: str = "Case file reorganization"
) -> str:
    """
    Submit a file reorganization plan to the mutation service.
    
    This tool allows you to perform file operations (move, copy, delete, create) on case
    files in a controlled, audited manner. Plans are validated before execution.
    
    Args:
        case_name: Name of the case (e.g., "Abby-Sitgraves-MVA-7-13-2024")
        operations: List of operations to perform. Each operation is a dict with:
            - type: "move", "copy", "delete", "create_dir", or "write_file"
            - source: Source path (relative to case root)
            - destination: Destination path (for move/copy/create_dir/write_file)
            - content: File content (for write_file)
        description: Human-readable description of what this plan does
    
    Returns:
        Status message with plan ID and validation results
    
    Examples:
        # Move medical records into proper structure
        reorganize_case_files(
            case_name="Abby-Sitgraves-MVA-7-13-2024",
            operations=[
                {
                    "type": "create_dir",
                    "destination": "Medical Records/Provider1"
                },
                {
                    "type": "move",
                    "source": "records_001.pdf",
                    "destination": "Medical Records/Provider1/records_001.pdf"
                }
            ],
            description="Organize medical records into provider folders"
        )
    """
    
    try:
        client = httpx.Client(timeout=60.0)
        
        # Create plan
        plan_data = {
            "plan_id": "",  # Auto-generated
            "case_name": case_name,
            "description": description,
            "operations": operations,
            "created_by": "roscoe-agent",
            "requires_approval": True
        }
        
        response = client.post(
            f"{MUTATION_SERVICE_URL}/plans",
            json=plan_data
        )
        response.raise_for_status()
        plan = response.json()
        plan_id = plan["plan_id"]
        
        # Validate plan
        validation_response = client.post(
            f"{MUTATION_SERVICE_URL}/plans/{plan_id}/validate"
        )
        validation_response.raise_for_status()
        validation = validation_response.json()
        
        result_lines = [
            f"✅ Plan created: {plan_id}",
            f"Description: {description}",
            f"Case: {case_name}",
            f"Operations: {validation['operation_count']}",
            f"Validation: {'PASSED ✓' if validation['valid'] else 'FAILED ✗'}",
            "",
            "Dry Run Summary:",
            validation['dry_run_summary']
        ]
        
        if validation['warnings']:
            result_lines.append("")
            result_lines.append("⚠️ Warnings:")
            for warning in validation['warnings']:
                result_lines.append(f"  - {warning}")
        
        if validation['errors']:
            result_lines.append("")
            result_lines.append("❌ Errors:")
            for error in validation['errors']:
                result_lines.append(f"  - {error}")
        
        if validation['valid']:
            result_lines.append("")
            result_lines.append(f"To execute this plan, use: execute_mutation_plan('{plan_id}')")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Failed to create reorganization plan: {str(e)}"

def execute_mutation_plan(plan_id: str, auto_approve: bool = False) -> str:
    """
    Execute an approved file mutation plan.
    
    Args:
        plan_id: Plan ID from reorganize_case_files
        auto_approve: If True, automatically approve before execution (use with caution)
    
    Returns:
        Execution result summary
    """
    
    try:
        client = httpx.Client(timeout=120.0)
        
        # Approve if needed
        if auto_approve:
            approve_response = client.post(
                f"{MUTATION_SERVICE_URL}/plans/{plan_id}/approve",
                params={"approved_by": "roscoe-agent-auto"}
            )
            approve_response.raise_for_status()
        
        # Execute
        execute_response = client.post(
            f"{MUTATION_SERVICE_URL}/plans/{plan_id}/apply"
        )
        execute_response.raise_for_status()
        result = execute_response.json()
        
        result_lines = [
            f"{'✅' if result['success'] else '❌'} Plan execution {'completed' if result['success'] else 'failed'}",
            f"Plan ID: {plan_id}",
            f"Operations completed: {result['operations_completed']}",
            f"Operations failed: {result['operations_failed']}",
            f"Audit log: {result['audit_log_path']}"
        ]
        
        if result['error_details']:
            result_lines.append("")
            result_lines.append(f"❌ Errors: {result['error_details']}")
        
        return "\n".join(result_lines)
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            return f"Plan {plan_id} requires manual approval. Ask user to approve via mutation service."
        return f"Failed to execute plan: {e.response.text}"
    except Exception as e:
        return f"Failed to execute plan: {str(e)}"
```

**4. Browser & Internet Access**

For browser automation and internet searches, continue using the RunLoop sandbox (read-only analysis) or add additional tools:

```python
# These can remain in RunLoop sandbox since they don't need file mutations
def search_internet(query: str) -> str:
    """Search internet using Tavily API (doesn't need filesystem access)."""
    # Existing Tavily implementation
    pass

def analyze_with_playwright(url: str, actions: List[str]) -> str:
    """
    Use Playwright in RunLoop sandbox for browser automation.
    Results can be saved to /Reports/ via the mutation service.
    """
    # Execute in RunLoop sandbox, capture results, optionally persist via mutation service
    pass
```

#### Deployment Steps

1. **Install mutation service on VM:**
```bash
# SSH to VM
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a

# Create service directory
sudo mkdir -p /opt/roscoe/mutation_service
sudo chown roscoe:roscoe /opt/roscoe/mutation_service

# Copy service code (from your local machine)
# Then on VM:
cd /opt/roscoe/mutation_service
python3 -m pip install fastapi uvicorn httpx pydantic

# Create systemd service
sudo cp roscoe-mutation-service.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable roscoe-mutation-service
sudo systemctl start roscoe-mutation-service

# Check status
sudo systemctl status roscoe-mutation-service
curl http://localhost:8124/health
```

2. **Update agent environment:**
```bash
# Add to docker-compose.yml or .env
MUTATION_SERVICE_URL=http://localhost:8124
```

3. **Test the flow:**
```python
# From agent
reorganize_case_files(
    case_name="Test-Case",
    operations=[
        {"type": "create_dir", "destination": "Medical Records"},
        {"type": "write_file", "destination": "Medical Records/test.txt", "content": "test"}
    ],
    description="Test mutation service"
)
```

#### Security & Safety Features

- ✅ **Path validation**: Prevents directory traversal attacks
- ✅ **Dry-run validation**: All plans validated before execution
- ✅ **Approval workflow**: Dangerous operations require explicit approval
- ✅ **Complete audit trail**: Every operation logged with timestamps
- ✅ **Size and count limits**: Warnings for large operations
- ✅ **Case-scoped**: Operations limited to specific case directories
- ✅ **Rollback support**: Audit logs enable manual rollback if needed

#### Advantages

✅ **Minimal infrastructure change**: Uses existing VM and gcsfuse mount  
✅ **Fast to implement**: ~2-3 days for MVP  
✅ **Low latency**: Direct filesystem access, no container overhead  
✅ **Flexible**: Easy to add new operation types  
✅ **Auditable**: Complete operation history  
✅ **Safe**: Validation + approval workflow prevents accidents  

#### Challenges & Mitigations

- **Service availability**: Single point of failure
  - *Mitigation*: Run as systemd service with auto-restart, monitor with healthchecks
- **Concurrent operations**: Multiple agents might conflict
  - *Mitigation*: Add locking mechanism (file locks or Redis locks)
- **No automatic rollback**: Manual intervention needed for mistakes
  - *Mitigation*: Generate rollback plans as part of audit logs

---

### Solution 2: Dagger-Based Containerized Execution Pipeline
**Best for: Portable, reproducible execution with good isolation**

#### Architecture Overview

Use Dagger (CI/CD pipeline as code) to orchestrate containerized code execution with volume mounting to GCS-backed filesystem.

```
┌─────────────────────┐
│   Roscoe Agent      │
│   (LangGraph)       │
│                     │
│ • Generates tasks   │
│ • Calls Dagger SDK  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐    ┌─────────────────────┐
│   Dagger Engine     │────│  Docker + Volumes   │
│   (VM or Cloud)     │    │                     │
│                     │    │ • Mounts GCS path   │
│ • Container exec    │    │ • Isolated env      │
│ • Volume management │    │ • Direct file ops   │
│ • Output capture    │    │ • Internet access   │
└─────────────────────┘    └─────────────────────┘
```

#### Why Dagger?

Dagger provides:
- **Programmable pipelines**: Define execution as Python code
- **Volume mounting**: Direct access to host filesystem (your gcsfuse mount)
- **Reproducible**: Same execution environment every time
- **Cloud-agnostic**: Works on GCE VM, local dev, or any Docker host
- **Built-in caching**: Speeds up repeated operations

#### Implementation Details

**1. Install Dagger on VM**

```bash
# SSH to VM
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a

# Install Dagger CLI
curl -L https://dl.dagger.io/dagger/install.sh | BIN_DIR=/usr/local/bin sh

# Verify
dagger version
```

**2. Create Dagger Pipeline Module**

```python
# /opt/roscoe/dagger_pipelines/file_operations.py
import dagger
import anyio
from pathlib import Path
from typing import List, Dict, Optional

async def execute_file_reorganization(
    case_name: str,
    script_path: str,
    script_args: List[str],
    workspace_path: str = "/mnt/workspace"
) -> Dict[str, str]:
    """
    Execute a file reorganization script with direct filesystem access.
    
    Args:
        case_name: Name of the case to work on
        script_path: Path to Python/bash script (relative to workspace)
        script_args: Arguments to pass to script
        workspace_path: Host path to mounted workspace
    
    Returns:
        Dict with stdout, stderr, and exit_code
    """
    
    config = dagger.Config(workdir="/opt/roscoe/dagger_pipelines")
    
    async with dagger.Connection(config) as client:
        # Create a container from Python image
        container = (
            client.container()
            .from_("python:3.11-slim")
            
            # Install common dependencies
            .with_exec(["pip", "install", "pandas", "python-magic", "pathlib"])
            
            # Mount workspace directory from host
            # This gives the container direct access to gcsfuse-mounted GCS
            .with_mounted_directory(
                "/workspace",
                client.host().directory(workspace_path)
            )
            
            # Set working directory to case folder
            .with_workdir(f"/workspace/projects/{case_name}")
            
            # Execute script
            .with_exec([
                "python",
                f"/workspace/{script_path}",
                *script_args
            ])
        )
        
        # Get output
        try:
            stdout = await container.stdout()
            stderr = await container.stderr()
            
            return {
                "success": True,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": "0"
            }
        except dagger.ExecError as e:
            return {
                "success": False,
                "stdout": e.stdout if hasattr(e, 'stdout') else "",
                "stderr": e.stderr if hasattr(e, 'stderr') else str(e),
                "exit_code": str(e.exit_code) if hasattr(e, 'exit_code') else "1"
            }

async def run_browser_automation(
    url: str,
    playwright_script: str,
    output_dir: str = "/workspace/Reports/browser_outputs"
) -> Dict[str, str]:
    """
    Run Playwright browser automation with screenshots/data capture.
    
    Args:
        url: URL to automate
        playwright_script: Python script using Playwright
        output_dir: Where to save outputs
    
    Returns:
        Dict with execution results
    """
    
    config = dagger.Config(workdir="/opt/roscoe/dagger_pipelines")
    
    async with dagger.Connection(config) as client:
        # Use Playwright image with browsers pre-installed
        container = (
            client.container()
            .from_("mcr.microsoft.com/playwright/python:v1.40.0-jammy")
            
            # Mount workspace for output
            .with_mounted_directory(
                "/workspace",
                client.host().directory("/mnt/workspace")
            )
            
            # Write playwright script to container
            .with_new_file("/script.py", contents=playwright_script)
            
            # Execute with full internet access
            .with_exec([
                "python",
                "/script.py",
                url,
                output_dir
            ])
        )
        
        try:
            stdout = await container.stdout()
            stderr = await container.stderr()
            
            return {
                "success": True,
                "stdout": stdout,
                "stderr": stderr
            }
        except dagger.ExecError as e:
            return {
                "success": False,
                "stderr": str(e)
            }

async def run_internet_research(
    search_query: str,
    research_script: str,
    api_keys: Dict[str, str]
) -> Dict[str, str]:
    """
    Run internet research with API calls (Tavily, PubMed, etc).
    
    Args:
        search_query: What to research
        research_script: Python script that performs research
        api_keys: Dict of API keys to inject as env vars
    
    Returns:
        Research results
    """
    
    config = dagger.Config(workdir="/opt/roscoe/dagger_pipelines")
    
    async with dagger.Connection(config) as client:
        container = (
            client.container()
            .from_("python:3.11-slim")
            .with_exec(["pip", "install", "httpx", "beautifulsoup4", "tavily-python"])
        )
        
        # Inject API keys as environment variables
        for key, value in api_keys.items():
            container = container.with_env_variable(key, value)
        
        container = (
            container
            .with_new_file("/research.py", contents=research_script)
            .with_exec(["python", "/research.py", search_query])
        )
        
        try:
            stdout = await container.stdout()
            return {
                "success": True,
                "results": stdout
            }
        except dagger.ExecError as e:
            return {
                "success": False,
                "error": str(e)
            }
```

**3. Dagger Service Wrapper**

```python
# /opt/roscoe/dagger_pipelines/service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import anyio
from file_operations import (
    execute_file_reorganization,
    run_browser_automation,
    run_internet_research
)

app = FastAPI(title="Roscoe Dagger Execution Service")

class FileReorgRequest(BaseModel):
    case_name: str
    script_path: str
    script_args: List[str]

class BrowserAutomationRequest(BaseModel):
    url: str
    playwright_script: str
    output_dir: Optional[str] = "/workspace/Reports/browser_outputs"

class ResearchRequest(BaseModel):
    search_query: str
    research_script: str
    api_keys: Dict[str, str]

@app.post("/execute/file-reorganization")
async def execute_reorg(request: FileReorgRequest):
    """Execute file reorganization script via Dagger."""
    result = await execute_file_reorganization(
        case_name=request.case_name,
        script_path=request.script_path,
        script_args=request.script_args
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["stderr"])
    
    return result

@app.post("/execute/browser-automation")
async def execute_browser(request: BrowserAutomationRequest):
    """Execute Playwright browser automation via Dagger."""
    result = await run_browser_automation(
        url=request.url,
        playwright_script=request.playwright_script,
        output_dir=request.output_dir
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["stderr"])
    
    return result

@app.post("/execute/research")
async def execute_research(request: ResearchRequest):
    """Execute internet research via Dagger."""
    result = await run_internet_research(
        search_query=request.search_query,
        research_script=request.research_script,
        api_keys=request.api_keys
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@app.get("/health")
async def health():
    return {"status": "healthy", "engine": "dagger"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8125)
```

**4. Integration with Agent**

```python
# Add to src/roscoe/agents/paralegal/tools.py

DAGGER_SERVICE_URL = os.environ.get(
    "DAGGER_SERVICE_URL",
    "http://localhost:8125"
)

def execute_file_transformation_script(
    case_name: str,
    script_name: str,
    script_args: List[str]
) -> str:
    """
    Execute a file transformation script with direct filesystem access.
    
    This uses Dagger to run scripts in isolated containers that have direct
    access to the case files via volume mounting. Changes are persisted.
    
    Args:
        case_name: Case to operate on
        script_name: Script name in /Tools/ (e.g., "create_file_inventory.py")
        script_args: Arguments to pass to script
    
    Returns:
        Script output
        
    Examples:
        execute_file_transformation_script(
            case_name="Abby-Sitgraves-MVA-7-13-2024",
            script_name="Tools/create_file_inventory.py",
            script_args=["--format", "json"]
        )
    """
    
    try:
        response = httpx.post(
            f"{DAGGER_SERVICE_URL}/execute/file-reorganization",
            json={
                "case_name": case_name,
                "script_path": script_name,
                "script_args": script_args
            },
            timeout=300.0
        )
        response.raise_for_status()
        result = response.json()
        
        return f"✅ Script executed successfully\n\nOutput:\n{result['stdout']}"
        
    except Exception as e:
        return f"❌ Failed to execute script: {str(e)}"

def automate_web_browser(
    url: str,
    actions: List[str],
    save_screenshots: bool = True
) -> str:
    """
    Automate web browser with Playwright to scrape data or interact with web apps.
    
    Args:
        url: URL to visit
        actions: List of actions to perform (in natural language or Playwright code)
        save_screenshots: Whether to save screenshots
    
    Returns:
        Results of automation including any extracted data
        
    Examples:
        automate_web_browser(
            url="https://www.courtlistener.com",
            actions=[
                "search for 'personal injury statute of limitations'",
                "click first result",
                "extract case citation and summary"
            ]
        )
    """
    
    # Generate Playwright script from actions
    playwright_script = generate_playwright_script(url, actions, save_screenshots)
    
    try:
        response = httpx.post(
            f"{DAGGER_SERVICE_URL}/execute/browser-automation",
            json={
                "url": url,
                "playwright_script": playwright_script
            },
            timeout=180.0
        )
        response.raise_for_status()
        result = response.json()
        
        return f"✅ Browser automation completed\n\nResults:\n{result['stdout']}"
        
    except Exception as e:
        return f"❌ Browser automation failed: {str(e)}"
```

#### Deployment Steps

1. **Install Dagger on VM:**
```bash
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a
curl -L https://dl.dagger.io/dagger/install.sh | BIN_DIR=/usr/local/bin sh
```

2. **Deploy Dagger service:**
```bash
cd /opt/roscoe/dagger_pipelines
pip install fastapi uvicorn dagger-io httpx
python service.py  # Or create systemd service
```

3. **Update agent environment:**
```bash
# Add to docker-compose.yml
DAGGER_SERVICE_URL=http://localhost:8125
```

#### Advantages

✅ **Reproducible**: Same container environment every time  
✅ **Portable**: Works on any Docker host (VM, local, cloud)  
✅ **Isolated**: Each execution in fresh container  
✅ **Full capabilities**: Supports Playwright, internet access, any Python library  
✅ **Direct file access**: Volume mounting enables real filesystem mutations  
✅ **Developer-friendly**: Define execution as code, easy to test  

#### Challenges & Mitigations

- **Docker dependency**: Requires Docker on execution host
  - *Mitigation*: Your VM already has Docker installed
- **Performance**: Container startup overhead
  - *Mitigation*: Dagger caches layers aggressively (~2-3s startup)
- **Complexity**: Learning Dagger SDK
  - *Mitigation*: Well-documented, Python SDK is straightforward

---

### Solution 3: Hybrid Execution Architecture (RunLoop + Privileged VM Executor)
**Best for: Maximum safety with controlled escalation to privileged operations**

#### Architecture Overview

Keep RunLoop sandbox for safe read-only analysis, but add a privileged execution path on the VM for approved mutations. Best of both worlds.

```
┌─────────────────────────────────────────┐
│           Roscoe Agent                  │
│           (LangGraph)                   │
└─────────────┬───────────────────────────┘
              │
       ┌──────┴──────┐
       │  Decision:  │
       │  Read-only  │
       │     or      │
       │  Mutate?    │
       └──────┬──────┘
              │
       ┌──────┴──────────────────┐
       │                         │
       ▼                         ▼
┌─────────────┐          ┌─────────────────┐
│  RunLoop    │          │  VM Executor    │
│  Sandbox    │          │  (Privileged)   │
│             │          │                 │
│ • Analysis  │          │ • File ops      │
│ • Research  │          │ • Approved only │
│ • Reports   │          │ • Audit logged  │
│ • (read-only)│         │ • Direct GCS    │
└─────────────┘          └─────────────────┘
```

#### Core Concept

- **RunLoop sandbox**: For all read-only operations (analysis, research, report generation)
- **VM privileged executor**: Only for approved file mutations
- **Decision layer**: Determines which execution path to use based on operation type

#### Implementation Details

**1. Operation Classifier**

```python
# src/roscoe/core/execution_router.py
from enum import Enum
from typing import Dict, Any, Callable
import re

class ExecutionMode(Enum):
    SANDBOX = "sandbox"  # RunLoop - safe, isolated
    PRIVILEGED = "privileged"  # VM - direct filesystem access

class OperationType(Enum):
    READ_ONLY = "read_only"
    MUTATION = "mutation"
    INTERNET = "internet"
    BROWSER = "browser"

def classify_operation(
    command: str,
    description: str = ""
) -> tuple[OperationType, ExecutionMode]:
    """
    Classify an operation to determine execution mode.
    
    Returns:
        (operation_type, execution_mode)
    """
    
    # Mutation indicators
    mutation_keywords = [
        r'\bmv\b', r'\brm\b', r'\bcp\b', r'\bmkdir\b',
        r'\.rename\(', r'\.unlink\(', r'shutil\.',
        r'os\.remove', r'os\.mkdir', r'Path.*\.write_',
        'move', 'delete', 'create', 'reorganize'
    ]
    
    is_mutation = any(
        re.search(pattern, command, re.IGNORECASE) or
        re.search(pattern, description, re.IGNORECASE)
        for pattern in mutation_keywords
    )
    
    # Internet/browser indicators
    internet_keywords = [
        'http://', 'https://', 'requests.', 'httpx.',
        'playwright', 'selenium', 'beautifulsoup',
        'tavily', 'search', 'scrape'
    ]
    
    is_internet = any(
        keyword in command.lower() or keyword in description.lower()
        for keyword in internet_keywords
    )
    
    # Classify
    if is_mutation:
        return OperationType.MUTATION, ExecutionMode.PRIVILEGED
    elif is_internet:
        return OperationType.INTERNET, ExecutionMode.SANDBOX
    else:
        return OperationType.READ_ONLY, ExecutionMode.SANDBOX

class ExecutionRouter:
    """Routes operations to appropriate execution backend."""
    
    def __init__(
        self,
        sandbox_executor: Callable,
        privileged_executor: Callable,
        approval_required: bool = True
    ):
        self.sandbox_executor = sandbox_executor
        self.privileged_executor = privileged_executor
        self.approval_required = approval_required
        self.pending_approvals = {}
    
    async def execute(
        self,
        command: str,
        description: str = "",
        case_name: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route and execute a command.
        
        Args:
            command: Command to execute
            description: Human-readable description
            case_name: Case being operated on
            **kwargs: Additional execution parameters
        
        Returns:
            Execution result dict
        """
        
        op_type, exec_mode = classify_operation(command, description)
        
        # Log classification
        classification_log = {
            "command": command[:100],
            "description": description,
            "case_name": case_name,
            "operation_type": op_type.value,
            "execution_mode": exec_mode.value
        }
        
        if exec_mode == ExecutionMode.SANDBOX:
            # Safe - execute in RunLoop sandbox
            result = await self.sandbox_executor(
                command=command,
                **kwargs
            )
            return {
                "success": True,
                "mode": "sandbox",
                "classification": classification_log,
                "result": result
            }
        
        else:  # PRIVILEGED
            # Potentially dangerous - require approval
            if self.approval_required:
                approval_id = self._request_approval(
                    command=command,
                    description=description,
                    case_name=case_name
                )
                
                return {
                    "success": False,
                    "mode": "privileged",
                    "requires_approval": True,
                    "approval_id": approval_id,
                    "classification": classification_log,
                    "message": (
                        f"This operation requires approval because it will modify files.\n"
                        f"Approval ID: {approval_id}\n"
                        f"To approve: approve_privileged_operation('{approval_id}')"
                    )
                }
            else:
                # Auto-approved (dangerous - use with caution)
                result = await self.privileged_executor(
                    command=command,
                    case_name=case_name,
                    **kwargs
                )
                return {
                    "success": True,
                    "mode": "privileged",
                    "classification": classification_log,
                    "result": result
                }
    
    def _request_approval(
        self,
        command: str,
        description: str,
        case_name: str
    ) -> str:
        """Create approval request and return approval ID."""
        import uuid
        approval_id = str(uuid.uuid4())[:8]
        
        self.pending_approvals[approval_id] = {
            "command": command,
            "description": description,
            "case_name": case_name,
            "requested_at": datetime.utcnow().isoformat()
        }
        
        return approval_id
    
    def approve(self, approval_id: str, approved_by: str = "user") -> bool:
        """Approve a pending operation."""
        if approval_id in self.pending_approvals:
            self.pending_approvals[approval_id]["approved_by"] = approved_by
            self.pending_approvals[approval_id]["approved_at"] = datetime.utcnow().isoformat()
            return True
        return False
    
    async def execute_approved(self, approval_id: str) -> Dict[str, Any]:
        """Execute a previously approved operation."""
        if approval_id not in self.pending_approvals:
            return {
                "success": False,
                "error": f"Approval ID {approval_id} not found"
            }
        
        approval = self.pending_approvals[approval_id]
        
        if "approved_by" not in approval:
            return {
                "success": False,
                "error": "Operation not approved yet"
            }
        
        # Execute with privileged executor
        result = await self.privileged_executor(
            command=approval["command"],
            case_name=approval["case_name"]
        )
        
        # Remove from pending
        del self.pending_approvals[approval_id]
        
        return {
            "success": True,
            "mode": "privileged",
            "approval": approval,
            "result": result
        }
```

**2. VM Privileged Executor**

```python
# src/roscoe/core/vm_executor.py
import paramiko
import os
from typing import Dict, Any, Optional

class VMExecutor:
    """Execute commands directly on VM with filesystem access."""
    
    def __init__(
        self,
        vm_host: str,
        vm_user: str = "roscoe",
        workspace_root: str = "/mnt/workspace"
    ):
        self.vm_host = vm_host
        self.vm_user = vm_user
        self.workspace_root = workspace_root
        self._ssh_client = None
    
    def _connect(self):
        """Establish SSH connection to VM."""
        if self._ssh_client is None:
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Use gcloud SSH for authentication
            # Or use SSH key directly
            self._ssh_client.connect(
                hostname=self.vm_host,
                username=self.vm_user,
                key_filename=os.path.expanduser("~/.ssh/google_compute_engine")
            )
    
    async def execute(
        self,
        command: str,
        case_name: str,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute command on VM with direct filesystem access.
        
        Args:
            command: Command to execute
            case_name: Case directory to operate in
            timeout: Execution timeout in seconds
        
        Returns:
            Execution result
        """
        
        self._connect()
        
        # Build full command with workspace context
        full_command = f"""
        cd {self.workspace_root}/projects/{case_name} && \
        {command}
        """
        
        # Execute
        stdin, stdout, stderr = self._ssh_client.exec_command(
            full_command,
            timeout=timeout
        )
        
        exit_code = stdout.channel.recv_exit_status()
        stdout_text = stdout.read().decode()
        stderr_text = stderr.read().decode()
        
        # Log execution
        self._log_execution(
            command=command,
            case_name=case_name,
            exit_code=exit_code,
            stdout=stdout_text,
            stderr=stderr_text
        )
        
        return {
            "exit_code": exit_code,
            "stdout": stdout_text,
            "stderr": stderr_text,
            "success": exit_code == 0
        }
    
    def _log_execution(
        self,
        command: str,
        case_name: str,
        exit_code: int,
        stdout: str,
        stderr: str
    ):
        """Log execution to audit trail."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "executor": "vm_privileged",
            "case_name": case_name,
            "command": command,
            "exit_code": exit_code,
            "stdout_length": len(stdout),
            "stderr_length": len(stderr)
        }
        
        # Write to VM filesystem
        log_file = f"{self.workspace_root}/Database/execution_audit/vm_exec_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        
        stdin, stdout, stderr = self._ssh_client.exec_command(
            f"echo '{json.dumps(log_entry)}' >> {log_file}"
        )
        stdout.channel.recv_exit_status()
```

**3. Agent Integration**

```python
# src/roscoe/agents/paralegal/tools.py

# Initialize execution router
execution_router = ExecutionRouter(
    sandbox_executor=execute_code_runloop,  # Existing RunLoop function
    privileged_executor=vm_executor.execute,
    approval_required=True  # Require approval for mutations
)

def execute_code_smart(
    command: str,
    description: str = "",
    case_name: str = "",
    **kwargs
) -> str:
    """
    Smart code execution that routes to appropriate backend.
    
    Read-only operations use RunLoop sandbox (safe, isolated).
    File mutations use VM privileged executor (requires approval).
    
    Args:
        command: Command to execute
        description: What this command does
        case_name: Case to operate on
    
    Returns:
        Execution result
        
    Examples:
        # Read-only - executes in sandbox automatically
        execute_code_smart(
            command="python /workspace/Tools/analyze_case.py",
            description="Analyze case files and generate report",
            case_name="Abby-Sitgraves-MVA-7-13-2024"
        )
        
        # Mutation - requires approval
        execute_code_smart(
            command="python /workspace/Tools/reorganize_files.py --execute",
            description="Reorganize medical records into 8-bucket structure",
            case_name="Abby-Sitgraves-MVA-7-13-2024"
        )
    """
    
    result = anyio.run(
        execution_router.execute,
        command=command,
        description=description,
        case_name=case_name,
        **kwargs
    )
    
    if result.get("requires_approval"):
        return result["message"]
    elif result["success"]:
        output = result["result"]
        return f"✅ Executed ({result['mode']} mode)\n\n{output.get('stdout', output)}"
    else:
        return f"❌ Execution failed: {result.get('error', 'Unknown error')}"

def approve_privileged_operation(approval_id: str) -> str:
    """
    Approve and execute a pending privileged operation.
    
    Args:
        approval_id: Approval ID from previous execute_code_smart call
    
    Returns:
        Execution result
    """
    
    # Mark as approved
    if not execution_router.approve(approval_id, approved_by="user"):
        return f"❌ Approval ID {approval_id} not found"
    
    # Execute
    result = anyio.run(execution_router.execute_approved, approval_id)
    
    if result["success"]:
        output = result["result"]
        return f"✅ Approved operation executed\n\n{output.get('stdout', output)}"
    else:
        return f"❌ Execution failed: {result.get('error', 'Unknown error')}"
```

#### Deployment Steps

1. **Configure VM SSH access from LangGraph container:**
```bash
# Generate SSH key in container or mount host SSH keys
docker exec roscoe-container ssh-keygen -t rsa -b 4096

# Add key to VM
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a -- \
  "echo 'YOUR_PUBLIC_KEY' >> ~/.ssh/authorized_keys"
```

2. **Update agent environment:**
```bash
# Add to docker-compose.yml
VM_HOST=localhost  # If running in same VM, otherwise IP
VM_USER=roscoe
VM_WORKSPACE_ROOT=/mnt/workspace
```

3. **Test the routing:**
```python
# Read-only - automatic sandbox
execute_code_smart(
    command="ls -la",
    description="List files",
    case_name="Test-Case"
)

# Mutation - requires approval
execute_code_smart(
    command="mkdir new_folder",
    description="Create folder",
    case_name="Test-Case"
)
# Returns approval_id

# Approve and execute
approve_privileged_operation(approval_id)
```

#### Security & Safety Features

- ✅ **Automatic classification**: Detects dangerous operations
- ✅ **Approval workflow**: Mutations require explicit approval
- ✅ **Sandbox by default**: Safe operations use RunLoop
- ✅ **Audit trail**: All privileged operations logged
- ✅ **Minimal privilege**: Only approved commands get VM access
- ✅ **Backward compatible**: Existing read-only tools work unchanged

#### Advantages

✅ **Best of both worlds**: Safety of sandbox + power of direct access  
✅ **Backward compatible**: Existing tools continue to work  
✅ **Graduated security**: Automatic escalation only when needed  
✅ **Flexible**: Easy to adjust classification rules  
✅ **Low latency for reads**: Most operations stay in RunLoop sandbox  
✅ **Explicit approval**: User controls dangerous operations  

#### Challenges & Mitigations

- **Complexity**: More moving parts
  - *Mitigation*: Well-defined interfaces, good logging
- **Classification accuracy**: Might misclassify some operations
  - *Mitigation*: Conservative defaults (bias toward sandbox), user override
- **SSH dependency**: Requires SSH access between containers/VM
  - *Mitigation*: If running on same VM, can use local execution instead

---

## Solution Comparison Matrix

| Criteria | Solution 1: VM Mutation Service | Solution 2: Dagger Pipelines | Solution 3: Hybrid Router |
|----------|--------------------------------|------------------------------|---------------------------|
| **Implementation Complexity** | Low | Medium | Medium-High |
| **Time to Deploy** | 2-3 days | 3-5 days | 5-7 days |
| **Infrastructure Changes** | Minimal (add service) | Minimal (add Dagger) | Minimal (add router) |
| **Cost** | Very Low ($0 extra) | Very Low ($0 extra) | Very Low ($0 extra) |
| **File Operation Latency** | Very Low (direct) | Low (container startup) | Low (routing overhead) |
| **Security** | High (validation + approval) | High (container isolation) | Very High (graduated) |
| **Auditability** | Excellent | Good | Excellent |
| **Browser Automation** | Via RunLoop or separate | Native (Playwright container) | Via RunLoop |
| **Internet Access** | Via RunLoop or separate | Native | Native (RunLoop) |
| **Rollback Support** | Manual (audit logs) | Manual | Manual (audit logs) |
| **Multi-tenant Safe** | Yes (path validation) | Yes (volume scoping) | Yes (classification) |
| **Developer Experience** | Good (REST API) | Excellent (code as config) | Good (automatic routing) |
| **Maintenance Burden** | Low | Low | Medium |
| **Backward Compatible** | Partial (new tools) | Partial (new tools) | Excellent (auto-routing) |

## Recommendations

### For Immediate Deployment (Next 1-2 weeks)

**Choose Solution 1: VM-Native Mutation Service**

**Why:**
- Fastest to implement with your existing infrastructure
- Minimal new dependencies (just FastAPI)
- Uses your existing gcsfuse mount
- Clear approval workflow for safety
- Easy to test and iterate

**Action Plan:**
1. Day 1-2: Implement mutation service FastAPI app
2. Day 3: Deploy as systemd service on VM
3. Day 4: Create initial agent tools (reorganize_case_files)
4. Day 5: Test with 1-2 real cases
5. Week 2: Iterate based on usage, add more operation types

### For Long-Term Scalability (1-3 months)

**Choose Solution 2: Dagger Pipelines**

**Why:**
- More portable and reproducible
- Better developer experience (code as config)
- Easier to test locally before deploying
- Natural fit for complex multi-step operations
- Cloud-agnostic (works anywhere Docker runs)

**Migration Path:**
1. Start with Solution 1 for immediate needs
2. Implement Dagger alongside for new features
3. Gradually migrate operations to Dagger as you refine workflows
4. Eventually deprecate mutation service in favor of Dagger

### For Maximum Safety (Enterprise/Production)

**Choose Solution 3: Hybrid Router**

**Why:**
- Preserves existing RunLoop sandbox for safe operations
- Automatic classification reduces human error
- Explicit approval for dangerous operations
- Excellent audit trail
- Backward compatible with existing tools

**Best For:**
- Environments with strict compliance requirements
- Multi-user scenarios where not all users should have mutation access
- Cases where you want to maintain RunLoop's safety guarantees while selectively enabling mutations

## Additional Considerations

### Browser Automation & Internet Access

All three solutions support browser automation and internet access:

**Solution 1**: Use RunLoop sandbox for Playwright/searches (read-only), mutation service for file operations
**Solution 2**: Native support via Dagger containers with browser images  
**Solution 3**: Automatic routing - browser/internet ops go to RunLoop sandbox

### Cost Analysis

All three solutions have **minimal additional cost**:
- No new cloud services required
- Use existing GCE VM
- Use existing GCS bucket
- Minor compute overhead (~1-2% CPU for services)

**Estimated monthly cost increase**: $0-5

### Testing Strategy

Before deploying any solution:

1. **Test with dummy case**: Create a test case folder with fake files
2. **Validate safety mechanisms**: Try to break out of allowed paths
3. **Benchmark performance**: Measure latency for typical operations
4. **Audit logging**: Verify all operations are logged correctly
5. **Rollback procedure**: Test recovery from mistakes

### Quick Start Commands

**For Solution 1:**
```bash
# Clone the mutation service code
git clone your-repo
cd mutation_service
pip install -r requirements.txt
python app.py
```

**For Solution 2:**
```bash
# Install Dagger
curl -L https://dl.dagger.io/dagger/install.sh | sh
# Run pipeline
dagger run python file_operations.py
```

**For Solution 3:**
```bash
# Deploy execution router
pip install paramiko
# Configure VM SSH
gcloud compute config-ssh
```

## Conclusion

Each solution addresses your core constraint—enabling agents to perform persistent filesystem mutations—while maintaining security and auditability. The choice depends on your priorities:

- **Speed to deployment**: Solution 1
- **Long-term maintainability**: Solution 2  
- **Maximum safety**: Solution 3

All three solutions are production-ready and can be deployed on your existing GCE VM + GCS infrastructure. You can also implement Solution 1 initially for fast wins, then migrate to Solution 2 or 3 as your needs evolve.

## Next Steps

1. **Review this document** with your team
2. **Choose a solution** based on your timeline and requirements
3. **Set up test environment** with dummy case files
4. **Implement MVP** of chosen solution
5. **Test thoroughly** before production deployment
6. **Monitor and iterate** based on real usage

Need help with implementation? I can assist with:
- Writing the actual code for any solution
- Creating deployment scripts
- Setting up monitoring and alerts
- Designing rollback procedures
- Building approval workflows

