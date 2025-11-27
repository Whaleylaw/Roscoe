# Sandbox Solution Analysis: Enabling Direct File Operations for AI Agents

## Executive Summary

This document analyzes the fundamental constraint preventing Roscoe agents from performing direct file operations on the persistent `/projects` workspace, and proposes three comprehensive solutions. Each solution addresses the core requirement: enabling agents to programmatically reorganize, transform, and modify case files stored in Google Cloud Storage while maintaining security, auditability, and safety.

**Current State**: RunLoop sandbox operates on an ephemeral copy-and-execute model—files are copied in, code runs in isolation, and changes are discarded. There is no mechanism to write changes back to the real filesystem.

**Goal**: Enable agents to:
1. Execute file transformations and modifications directly on the persistent `/projects` tree
2. Run code execution (Python scripts, shell commands)
3. Perform internet searches, browser automation (Playwright), and web scraping
4. Maintain full auditability and safety guardrails

---

## Current Architecture Analysis

### How RunLoop Works Today

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Roscoe Agent      │────▶│   RunLoop Sandbox    │     │   GCS Bucket    │
│   (LangGraph)       │     │   (Ephemeral)        │     │   (Persistent)  │
│                     │     │                      │     │                 │
│ • execute_code()    │     │ • Fresh container    │     │ • /projects/    │
│ • input_files=[]    │     │ • Copies of files    │◀───▶│ • /Tools/       │
└─────────────────────┘     │ • No write-back      │     │ • /Database/    │
                            └──────────────────────┘     └─────────────────┘
                                     ▲
                                     │
                              Changes are LOST
                              when container exits
```

From `src/roscoe/agents/paralegal/tools.py`:

```python
def execute_code(
    command: str,
    working_dir: str = "/workspace",
    timeout: int = 60,
    input_files: Optional[list[str]] = None,
) -> str:
    """Execute shell commands or Python code in an isolated Runloop sandbox."""
    
    # Problem 1: Creates ephemeral container
    devbox = runloop_client.devboxes.create_and_await_running(...)
    
    # Problem 2: Files must be uploaded as copies
    if input_files:
        for file_path in input_files:
            runloop_client.devboxes.upload_file(devbox.id, path=remote_path, file=f)
    
    # Problem 3: Results stay in sandbox, no write-back
    result = runloop_client.devboxes.execute_and_await_completion(devbox.id, command=command)
    
    # Container shutdown - all changes lost
    runloop_client.devboxes.shutdown(devbox.id)
```

### Key Limitations

| Capability | RunLoop Status | Required |
|------------|----------------|----------|
| Read files from workspace | ✅ Via upload | ✅ |
| Execute Python/shell | ✅ In sandbox | ✅ |
| Write files back to workspace | ❌ Not supported | ✅ |
| Move/rename files in workspace | ❌ Not supported | ✅ |
| Internet access | ✅ Supported | ✅ |
| Browser/Playwright | ⚠️ Requires setup | ✅ |
| Persistent state | ❌ Ephemeral only | ✅ |

---

## Solution 1: Workspace Mutation Service (Plan & Apply API)

**Architecture**: Deploy a lightweight FastAPI service on the GCE VM that exposes curated file operation endpoints. The LLM generates operation plans (JSON), which the service validates and executes with full audit logging.

**Best For**: Fastest path to production, strong safety guarantees, no per-operation container overhead.

### Architecture Diagram

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Roscoe Agent      │     │  Mutation Service    │     │   GCS FUSE      │
│   (LangGraph)       │────▶│  (FastAPI on GCE)    │────▶│   Mount         │
│                     │     │                      │     │                 │
│ • submit_plan()     │     │ POST /plans          │     │ /mnt/workspace/ │
│ • validate_plan()   │     │ POST /plans/{id}/val │     │ ├── projects/   │
│ • apply_plan()      │     │ POST /plans/{id}/app │     │ ├── Tools/      │
│                     │     │ POST /plans/{id}/roll│     │ └── Database/   │
└─────────────────────┘     └──────────────────────┘     └─────────────────┘
                                     │
                                     ▼
                            ┌──────────────────────┐
                            │   Audit Log          │
                            │   (JSON + GCS)       │
                            │                      │
                            │ • Operation history  │
                            │ • Rollback scripts   │
                            │ • Actor attribution  │
                            └──────────────────────┘
```

### Implementation

#### 1. Mutation Service (FastAPI)

```python
# services/mutation_service/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime
import shutil
import json
import uuid
import os

app = FastAPI(title="Roscoe Workspace Mutation Service")

# Configuration
WORKSPACE_ROOT = Path("/mnt/workspace")
PROJECTS_DIR = WORKSPACE_ROOT / "projects"
AUDIT_DIR = WORKSPACE_ROOT / "Database" / "reorg_audit"
MAX_OPERATIONS_PER_PLAN = 500
ALLOWED_ROOTS = ["/mnt/workspace/projects", "/mnt/workspace/Reports"]

# --- Models ---

class FileOperation(BaseModel):
    """Single file operation"""
    operation: str = Field(..., pattern="^(move|copy|delete|create_dir|rename)$")
    source: str
    destination: str | None = None
    reason: str | None = None

class ReorganizationPlan(BaseModel):
    """Complete reorganization plan"""
    case_name: str
    operations: list[FileOperation]
    actor: str = "roscoe-agent"
    dry_run: bool = True

class PlanResult(BaseModel):
    """Result of plan validation or execution"""
    plan_id: str
    status: str
    executed_operations: list[dict] = []
    errors: list[str] = []
    rollback_script: str | None = None

# --- Safety Checks ---

def validate_path(path: str) -> Path:
    """Ensure path is within allowed roots and doesn't escape."""
    resolved = Path(path).resolve()
    
    # Check it's under allowed roots
    allowed = any(str(resolved).startswith(root) for root in ALLOWED_ROOTS)
    if not allowed:
        raise HTTPException(400, f"Path not in allowed roots: {path}")
    
    # Check for path traversal attacks
    if ".." in path:
        raise HTTPException(400, f"Path traversal detected: {path}")
    
    return resolved

def validate_operation(op: FileOperation, case_name: str) -> tuple[bool, str]:
    """Validate a single operation for safety."""
    try:
        source = validate_path(op.source)
        
        # For operations that need destination
        if op.operation in ["move", "copy", "rename"]:
            if not op.destination:
                return False, f"Operation {op.operation} requires destination"
            dest = validate_path(op.destination)
            
            # Ensure destination is within same case
            if case_name not in str(dest):
                return False, f"Cross-case operations not allowed"
        
        # Check source exists for read operations
        if op.operation in ["move", "copy", "delete"]:
            if not source.exists():
                return False, f"Source does not exist: {source}"
        
        # Check destination doesn't exist for create operations
        if op.operation == "create_dir":
            dest = validate_path(op.destination or op.source)
            if dest.exists():
                return False, f"Directory already exists: {dest}"
        
        return True, "OK"
        
    except HTTPException as e:
        return False, e.detail

# --- Plan Storage ---

plans_db: dict[str, dict] = {}

def store_plan(plan: ReorganizationPlan) -> str:
    """Store plan and return ID."""
    plan_id = f"plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    plans_db[plan_id] = {
        "plan": plan.model_dump(),
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "validation_result": None,
        "execution_result": None
    }
    return plan_id

# --- Endpoints ---

@app.post("/plans", response_model=dict)
async def create_plan(plan: ReorganizationPlan):
    """Submit a new reorganization plan."""
    
    # Enforce operation limits
    if len(plan.operations) > MAX_OPERATIONS_PER_PLAN:
        raise HTTPException(400, f"Plan exceeds max operations ({MAX_OPERATIONS_PER_PLAN})")
    
    plan_id = store_plan(plan)
    
    return {
        "plan_id": plan_id,
        "status": "pending",
        "message": f"Plan created with {len(plan.operations)} operations. Call /plans/{plan_id}/validate next."
    }

@app.post("/plans/{plan_id}/validate", response_model=PlanResult)
async def validate_plan(plan_id: str):
    """Validate a plan (dry run)."""
    
    if plan_id not in plans_db:
        raise HTTPException(404, "Plan not found")
    
    plan_data = plans_db[plan_id]["plan"]
    plan = ReorganizationPlan(**plan_data)
    
    errors = []
    validated_ops = []
    
    for i, op in enumerate(plan.operations):
        valid, msg = validate_operation(op, plan.case_name)
        if not valid:
            errors.append(f"Operation {i}: {msg}")
        else:
            validated_ops.append({
                "index": i,
                "operation": op.operation,
                "source": op.source,
                "destination": op.destination,
                "status": "valid"
            })
    
    status = "validated" if not errors else "validation_failed"
    plans_db[plan_id]["status"] = status
    plans_db[plan_id]["validation_result"] = {
        "valid_operations": len(validated_ops),
        "errors": errors
    }
    
    return PlanResult(
        plan_id=plan_id,
        status=status,
        executed_operations=validated_ops,
        errors=errors
    )

@app.post("/plans/{plan_id}/apply", response_model=PlanResult)
async def apply_plan(plan_id: str, background_tasks: BackgroundTasks):
    """Execute a validated plan."""
    
    if plan_id not in plans_db:
        raise HTTPException(404, "Plan not found")
    
    if plans_db[plan_id]["status"] != "validated":
        raise HTTPException(400, "Plan must be validated before applying")
    
    plan_data = plans_db[plan_id]["plan"]
    plan = ReorganizationPlan(**plan_data)
    
    executed = []
    errors = []
    rollback_commands = []
    
    for i, op in enumerate(plan.operations):
        try:
            source = Path(op.source)
            dest = Path(op.destination) if op.destination else None
            
            if op.operation == "move":
                # Create rollback command
                rollback_commands.append(f"mv '{dest}' '{source}'")
                # Execute
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(dest))
                
            elif op.operation == "copy":
                rollback_commands.append(f"rm -rf '{dest}'")
                dest.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    shutil.copytree(str(source), str(dest))
                else:
                    shutil.copy2(str(source), str(dest))
                    
            elif op.operation == "delete":
                # Backup before delete (safety)
                backup_path = AUDIT_DIR / plan_id / "backups" / source.name
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                if source.is_dir():
                    shutil.copytree(str(source), str(backup_path))
                else:
                    shutil.copy2(str(source), str(backup_path))
                rollback_commands.append(f"cp -r '{backup_path}' '{source}'")
                
                # Now delete
                if source.is_dir():
                    shutil.rmtree(str(source))
                else:
                    source.unlink()
                    
            elif op.operation == "create_dir":
                target = dest or source
                Path(target).mkdir(parents=True, exist_ok=True)
                rollback_commands.append(f"rmdir '{target}'")
                
            elif op.operation == "rename":
                rollback_commands.append(f"mv '{dest}' '{source}'")
                source.rename(dest)
            
            executed.append({
                "index": i,
                "operation": op.operation,
                "source": str(source),
                "destination": str(dest) if dest else None,
                "status": "completed"
            })
            
        except Exception as e:
            errors.append(f"Operation {i} failed: {str(e)}")
            # Stop on first error to allow partial rollback
            break
    
    # Generate rollback script
    rollback_script = "#!/bin/bash\n# Rollback script for " + plan_id + "\n"
    rollback_script += "\n".join(reversed(rollback_commands))
    
    # Save rollback script
    rollback_path = AUDIT_DIR / plan_id / "rollback.sh"
    rollback_path.parent.mkdir(parents=True, exist_ok=True)
    rollback_path.write_text(rollback_script)
    
    # Save audit log
    audit_entry = {
        "plan_id": plan_id,
        "case_name": plan.case_name,
        "actor": plan.actor,
        "timestamp": datetime.utcnow().isoformat(),
        "operations_attempted": len(plan.operations),
        "operations_completed": len(executed),
        "errors": errors,
        "rollback_script": str(rollback_path)
    }
    
    audit_log_path = AUDIT_DIR / f"{plan_id}_audit.json"
    audit_log_path.write_text(json.dumps(audit_entry, indent=2))
    
    status = "completed" if not errors else "partial_failure"
    plans_db[plan_id]["status"] = status
    plans_db[plan_id]["execution_result"] = audit_entry
    
    return PlanResult(
        plan_id=plan_id,
        status=status,
        executed_operations=executed,
        errors=errors,
        rollback_script=str(rollback_path)
    )

@app.post("/plans/{plan_id}/rollback")
async def rollback_plan(plan_id: str):
    """Execute rollback script for a plan."""
    
    rollback_path = AUDIT_DIR / plan_id / "rollback.sh"
    if not rollback_path.exists():
        raise HTTPException(404, "Rollback script not found")
    
    import subprocess
    result = subprocess.run(
        ["bash", str(rollback_path)],
        capture_output=True,
        text=True
    )
    
    return {
        "plan_id": plan_id,
        "rollback_status": "completed" if result.returncode == 0 else "failed",
        "stdout": result.stdout,
        "stderr": result.stderr
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "workspace_mounted": PROJECTS_DIR.exists()}
```

#### 2. Agent Tool Integration

```python
# src/roscoe/agents/paralegal/tools.py (additions)
import httpx
from typing import Optional

MUTATION_SERVICE_URL = os.environ.get("MUTATION_SERVICE_URL", "http://localhost:8500")

def submit_reorganization_plan(
    case_name: str,
    operations: list[dict],
    auto_apply: bool = False,
) -> str:
    """
    Submit a file reorganization plan to the Mutation Service.
    
    This tool enables direct file operations (move, copy, delete, rename) on the
    persistent /projects filesystem. Plans are validated before execution.
    
    Args:
        case_name: Name of the case folder (e.g., "Caryn-McCay-MVA-7-30-2023")
        operations: List of operation dicts, each with:
            - operation: "move", "copy", "delete", "create_dir", or "rename"
            - source: Source path (full path starting with /mnt/workspace/)
            - destination: Destination path (required for move/copy/rename)
            - reason: Optional explanation for the operation
        auto_apply: If True, automatically apply after validation (default: False)
    
    Returns:
        Status message with plan ID and validation/execution results.
    
    Example:
        submit_reorganization_plan(
            case_name="Wilson-MVA",
            operations=[
                {
                    "operation": "move",
                    "source": "/mnt/workspace/projects/Wilson-MVA/misc/medical_records.pdf",
                    "destination": "/mnt/workspace/projects/Wilson-MVA/Medical Records/medical_records.pdf",
                    "reason": "Organize into standard bucket structure"
                },
                {
                    "operation": "create_dir",
                    "source": "/mnt/workspace/projects/Wilson-MVA/Insurance",
                    "reason": "Create missing Insurance bucket"
                }
            ],
            auto_apply=True
        )
    """
    try:
        # Step 1: Submit plan
        response = httpx.post(
            f"{MUTATION_SERVICE_URL}/plans",
            json={
                "case_name": case_name,
                "operations": operations,
                "actor": "roscoe-agent",
                "dry_run": not auto_apply
            },
            timeout=30
        )
        response.raise_for_status()
        plan_result = response.json()
        plan_id = plan_result["plan_id"]
        
        # Step 2: Validate
        val_response = httpx.post(
            f"{MUTATION_SERVICE_URL}/plans/{plan_id}/validate",
            timeout=60
        )
        val_response.raise_for_status()
        validation = val_response.json()
        
        if validation["status"] != "validated":
            return f"Plan validation failed:\n" + "\n".join(validation["errors"])
        
        # Step 3: Apply (if auto_apply)
        if auto_apply:
            apply_response = httpx.post(
                f"{MUTATION_SERVICE_URL}/plans/{plan_id}/apply",
                timeout=120
            )
            apply_response.raise_for_status()
            result = apply_response.json()
            
            summary = f"**Plan {plan_id} executed**\n"
            summary += f"- Status: {result['status']}\n"
            summary += f"- Operations completed: {len(result['executed_operations'])}\n"
            
            if result["errors"]:
                summary += f"- Errors:\n" + "\n".join(result["errors"])
            
            if result.get("rollback_script"):
                summary += f"\n- Rollback available: {result['rollback_script']}"
            
            return summary
        else:
            return f"Plan {plan_id} validated with {len(operations)} operations. Call apply_plan('{plan_id}') to execute."
    
    except httpx.HTTPError as e:
        return f"Mutation service error: {str(e)}"

def apply_plan(plan_id: str) -> str:
    """
    Apply a previously validated reorganization plan.
    
    Use this after submit_reorganization_plan() when auto_apply=False.
    """
    try:
        response = httpx.post(
            f"{MUTATION_SERVICE_URL}/plans/{plan_id}/apply",
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        
        summary = f"**Plan {plan_id} executed**\n"
        summary += f"- Status: {result['status']}\n"
        summary += f"- Operations completed: {len(result['executed_operations'])}\n"
        
        if result["errors"]:
            summary += f"- Errors:\n" + "\n".join(result["errors"])
        
        return summary
        
    except httpx.HTTPError as e:
        return f"Apply error: {str(e)}"

def rollback_plan(plan_id: str) -> str:
    """
    Rollback a previously executed plan.
    
    This will undo the file operations using the auto-generated rollback script.
    """
    try:
        response = httpx.post(
            f"{MUTATION_SERVICE_URL}/plans/{plan_id}/rollback",
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        return f"Rollback {result['rollback_status']}: {result.get('stdout', '')}"
        
    except httpx.HTTPError as e:
        return f"Rollback error: {str(e)}"
```

#### 3. Deployment (systemd on GCE VM)

```bash
# /etc/systemd/system/roscoe-mutation.service
[Unit]
Description=Roscoe Workspace Mutation Service
After=network.target gcsfuse.service

[Service]
Type=simple
User=roscoe
Group=roscoe
WorkingDirectory=/opt/roscoe/services/mutation_service
ExecStart=/opt/roscoe/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8500
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/roscoe

[Install]
WantedBy=multi-user.target
```

### Advantages

| Benefit | Description |
|---------|-------------|
| **Speed** | No container spin-up per operation; direct filesystem access |
| **Safety** | Centralized validation, path sanitization, and audit logging |
| **Rollback** | Auto-generated rollback scripts for every plan |
| **Simplicity** | Single service to deploy and maintain |
| **Works with GCS** | Uses existing gcsfuse mount—no new infrastructure |

### Challenges & Mitigations

| Challenge | Mitigation |
|-----------|------------|
| New API surface to maintain | Keep scope minimal; focus on file ops only |
| Risk of mass deletions | Operation limits, path whitelisting, mandatory backups |
| Service availability | systemd auto-restart, health checks, monitoring |

---

## Solution 2: Scoped Mutable Containers (Docker on GCE VM)

**Architecture**: When a mutation is requested, spin up a short-lived Docker container on the GCE VM with the specific case folder mounted read-write. The container executes the operation directly on the real filesystem, then exits.

**Best For**: Preserving the "sandbox feel" while enabling real mutations; reuses existing Python scripts.

### Architecture Diagram

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Roscoe Agent      │     │   Mutation Executor  │     │   GCS FUSE      │
│   (LangGraph)       │────▶│   (Docker SDK)       │     │   Mount         │
│                     │     │                      │     │                 │
│ execute_mutation()  │     │ docker run --rm \    │     │ /mnt/workspace/ │
│                     │     │   -v /projects/Case  │────▶│ └── projects/   │
│                     │     │   :/case:rw          │     │     └── Case/   │
│                     │     │   roscoe-mutator     │     │                 │
└─────────────────────┘     │   python /script.py  │     │                 │
                            └──────────────────────┘     └─────────────────┘
                                     │
                                     ▼
                            Container exits,
                            changes persist on GCS
```

### Implementation

#### 1. Mutator Docker Image

```dockerfile
# Dockerfile.mutator
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages needed for file operations and tools
RUN pip install --no-cache-dir \
    pathlib \
    shutil \
    pandas \
    openpyxl \
    PyPDF2 \
    playwright \
    tavily-python \
    httpx

# Install Playwright browsers
RUN playwright install chromium --with-deps

# Create non-root user
RUN useradd -m -s /bin/bash mutator
USER mutator

# Working directory
WORKDIR /workspace

# Default command
CMD ["python", "-c", "print('Mutator ready')"]
```

#### 2. Executor Module

```python
# src/roscoe/agents/paralegal/mutation_executor.py
import docker
import os
import uuid
import json
from pathlib import Path
from datetime import datetime

# Docker client
docker_client = docker.from_env()

# Configuration
WORKSPACE_ROOT = "/mnt/workspace"
MUTATOR_IMAGE = "roscoe-mutator:latest"
AUDIT_DIR = Path(WORKSPACE_ROOT) / "Database" / "mutation_logs"

def execute_mutation_command(
    case_name: str,
    command: str,
    additional_mounts: list[str] | None = None,
    env_vars: dict | None = None,
    timeout: int = 300,
) -> dict:
    """
    Execute a command in a Docker container with write access to the case folder.
    
    Args:
        case_name: Name of case folder to mount read-write
        command: Shell command or Python script to execute
        additional_mounts: Additional paths to mount (read-only)
        env_vars: Environment variables to pass
        timeout: Maximum execution time in seconds
    
    Returns:
        Dict with exit_code, stdout, stderr, and execution metadata
    """
    execution_id = f"mut_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Build volume mounts
    volumes = {
        f"{WORKSPACE_ROOT}/projects/{case_name}": {
            "bind": "/case",
            "mode": "rw"  # Read-write access to case folder
        },
        f"{WORKSPACE_ROOT}/Tools": {
            "bind": "/tools",
            "mode": "ro"  # Read-only access to tools
        }
    }
    
    # Add additional mounts (read-only)
    if additional_mounts:
        for mount_path in additional_mounts:
            mount_name = Path(mount_path).name
            volumes[mount_path] = {
                "bind": f"/mnt/{mount_name}",
                "mode": "ro"
            }
    
    # Build environment
    environment = env_vars or {}
    environment.update({
        "CASE_NAME": case_name,
        "EXECUTION_ID": execution_id,
        "WORKSPACE": "/case"
    })
    
    # Pass through API keys if needed
    for key in ["TAVILY_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
        if val := os.environ.get(key):
            environment[key] = val
    
    try:
        # Run container
        container = docker_client.containers.run(
            MUTATOR_IMAGE,
            command=f"bash -c '{command}'",
            volumes=volumes,
            environment=environment,
            working_dir="/case",
            remove=True,  # Auto-remove after exit
            detach=False,  # Wait for completion
            stdout=True,
            stderr=True,
            user="mutator",
            network_mode="bridge",  # Allow internet access
            mem_limit="2g",
            cpu_period=100000,
            cpu_quota=100000,  # 1 CPU max
        )
        
        # Container.run with detach=False returns bytes directly
        stdout = container.decode('utf-8') if isinstance(container, bytes) else str(container)
        stderr = ""
        exit_code = 0
        
    except docker.errors.ContainerError as e:
        stdout = e.container.logs(stdout=True, stderr=False).decode('utf-8')
        stderr = e.container.logs(stdout=False, stderr=True).decode('utf-8')
        exit_code = e.exit_status
        
    except Exception as e:
        stdout = ""
        stderr = str(e)
        exit_code = 1
    
    # Log execution
    audit_entry = {
        "execution_id": execution_id,
        "case_name": case_name,
        "command": command,
        "exit_code": exit_code,
        "timestamp": datetime.utcnow().isoformat(),
        "stdout_length": len(stdout),
        "stderr_length": len(stderr)
    }
    
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit_path = AUDIT_DIR / f"{execution_id}.json"
    audit_path.write_text(json.dumps(audit_entry, indent=2))
    
    return {
        "execution_id": execution_id,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "audit_log": str(audit_path)
    }


def run_python_script(
    case_name: str,
    script_path: str,
    script_args: list[str] | None = None,
) -> dict:
    """
    Run a Python script from /Tools against a case folder.
    
    Args:
        case_name: Target case folder
        script_path: Path to script (relative to /Tools/)
        script_args: Arguments to pass to script
    
    Returns:
        Execution result dict
    """
    args_str = " ".join(script_args or [])
    command = f"python /tools/{script_path} {args_str}"
    
    return execute_mutation_command(case_name, command)


def run_file_reorganization(
    case_name: str,
    reorganization_map: dict,
) -> dict:
    """
    Execute file reorganization based on a mapping.
    
    Args:
        case_name: Target case folder
        reorganization_map: Dict mapping source paths to destination paths
            Example: {
                "misc/medical.pdf": "Medical Records/medical.pdf",
                "docs/insurance_claim.pdf": "Insurance/claim.pdf"
            }
    
    Returns:
        Execution result dict
    """
    # Generate inline Python script for reorganization
    script = """
import shutil
import json
from pathlib import Path

reorg_map = json.loads('''""" + json.dumps(reorganization_map) + """''')

results = []
for source, dest in reorg_map.items():
    src_path = Path('/case') / source
    dst_path = Path('/case') / dest
    
    try:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))
        results.append(f"✓ {source} -> {dest}")
    except Exception as e:
        results.append(f"✗ {source}: {e}")

print("\\n".join(results))
print(f"\\nCompleted: {len([r for r in results if r.startswith('✓')])} / {len(reorg_map)}")
"""
    
    return execute_mutation_command(
        case_name,
        f"python -c '{script}'"
    )
```

#### 3. Agent Tool Integration

```python
# src/roscoe/agents/paralegal/tools.py (additions)

from roscoe.agents.paralegal.mutation_executor import (
    execute_mutation_command,
    run_python_script,
    run_file_reorganization
)

def execute_case_mutation(
    case_name: str,
    command: str,
    timeout: int = 300,
) -> str:
    """
    Execute a shell command with direct write access to a case folder.
    
    This runs in an isolated Docker container with the case folder mounted.
    Changes are persisted directly to the /projects filesystem.
    
    Args:
        case_name: The case folder name (e.g., "Wilson-MVA-2024")
        command: Shell command to execute (runs in /case working directory)
        timeout: Maximum execution time in seconds
    
    Returns:
        Command output and execution status
    
    Examples:
        # Create the standard 8-bucket structure
        execute_case_mutation("Wilson-MVA", "mkdir -p Insurance Lien Expenses 'Negotiation Settlement' Litigation")
        
        # Move files to correct buckets
        execute_case_mutation("Wilson-MVA", "mv misc/*.pdf 'Medical Records/'")
        
        # Run a Tool script
        execute_case_mutation("Wilson-MVA", "python /tools/create_file_inventory.py --root /case")
    """
    result = execute_mutation_command(case_name, command, timeout=timeout)
    
    output = f"**Execution {result['execution_id']}**\n"
    output += f"Exit code: {result['exit_code']}\n\n"
    
    if result['stdout']:
        output += f"**Output:**\n```\n{result['stdout']}\n```\n"
    
    if result['stderr']:
        output += f"**Errors:**\n```\n{result['stderr']}\n```\n"
    
    return output

def reorganize_case_files(
    case_name: str,
    file_mapping: dict[str, str],
) -> str:
    """
    Reorganize files within a case folder using a source->destination mapping.
    
    This is the primary tool for case file organization tasks.
    
    Args:
        case_name: The case folder name
        file_mapping: Dict mapping current paths to new paths (relative to case folder)
            Example: {
                "unsorted/medical_bill_1.pdf": "Medical Records/Bills/medical_bill_1.pdf",
                "docs/complaint.pdf": "Litigation/Pleadings/complaint.pdf"
            }
    
    Returns:
        Summary of move operations with success/failure status
    
    Example:
        reorganize_case_files(
            case_name="Caryn-McCay-MVA",
            file_mapping={
                "Police Report.pdf": "Investigation/Police Report.pdf",
                "ER Visit 2023-07-30.pdf": "Medical Records/Emergency/ER Visit 2023-07-30.pdf",
                "Photos/damage_1.jpg": "case_information/Photos/damage_1.jpg"
            }
        )
    """
    result = run_file_reorganization(case_name, file_mapping)
    
    output = f"**File Reorganization: {case_name}**\n"
    output += f"Operations: {len(file_mapping)}\n\n"
    output += result['stdout']
    
    if result['stderr']:
        output += f"\n\n**Warnings:**\n{result['stderr']}"
    
    return output
```

### Advantages

| Benefit | Description |
|---------|-------------|
| **Isolated Execution** | Each operation runs in fresh container |
| **Reuses Existing Scripts** | Run `/Tools/create_file_inventory.py` directly |
| **Full Capabilities** | Python, bash, Playwright all available |
| **Internet Access** | Container can make HTTP requests |
| **Resource Limits** | CPU/memory limits prevent runaway processes |

### Challenges & Mitigations

| Challenge | Mitigation |
|-----------|------------|
| Container spin-up overhead | Pre-pull image; use small base image |
| Docker privileges on VM | Run Docker rootless or with scoped permissions |
| No built-in approval workflow | Combine with Plan & Apply for human review |
| Audit trail complexity | Log all executions with full context |

---

## Solution 3: GKE Agent Sandbox with Persistent Volumes

**Architecture**: Deploy a GKE cluster with Agent Sandbox (gVisor) enabled, using Persistent Volume Claims backed by GCS or Filestore. Agents execute in sandboxed pods with direct read-write access to the workspace.

**Best For**: Enterprise-grade security, multi-agent scalability, full Kubernetes ecosystem integration.

### Architecture Diagram

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Roscoe Agent      │     │   GKE Agent Sandbox  │     │   Filestore     │
│   (LangGraph)       │────▶│   (gVisor Runtime)   │     │   (NFS)         │
│                     │     │                      │     │                 │
│ execute_sandboxed() │     │ ┌──────────────────┐ │     │ /mnt/workspace/ │
│                     │     │ │  Pod             │ │     │ ├── projects/   │
│                     │     │ │  securityContext │─┼────▶│ ├── Tools/      │
│                     │     │ │  gvisor runtime  │ │     │ └── Database/   │
│                     │     │ └──────────────────┘ │     │                 │
└─────────────────────┘     └──────────────────────┘     └─────────────────┘
                                     │
                                     │ Network Policy
                                     ▼
                            ┌──────────────────────┐
                            │   External APIs      │
                            │   (Tavily, OpenAI)   │
                            └──────────────────────┘
```

### Implementation

#### 1. GKE Cluster with Agent Sandbox

```yaml
# k8s/cluster-config.yaml
# Create cluster with gVisor sandbox enabled
apiVersion: container.v1
kind: Cluster
metadata:
  name: roscoe-agents-cluster
spec:
  location: us-central1
  autopilot:
    enabled: true
  workloadIdentityConfig:
    workloadPool: YOUR_PROJECT.svc.id.goog
  addonsConfig:
    gceSandboxConfig:
      enabled: true  # Enable gVisor sandbox
```

#### 2. Persistent Volume with Filestore

```yaml
# k8s/storage/filestore-pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: roscoe-workspace-pv
spec:
  capacity:
    storage: 1Ti
  accessModes:
    - ReadWriteMany
  nfs:
    server: FILESTORE_IP  # Replace with your Filestore IP
    path: /workspace
  persistentVolumeReclaimPolicy: Retain
  storageClassName: filestore
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: roscoe-workspace-pvc
  namespace: roscoe
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Ti
  storageClassName: filestore
```

#### 3. Sandbox Pod Template

```yaml
# k8s/sandbox-job-template.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: roscoe-sandbox-{{EXECUTION_ID}}
  namespace: roscoe
  labels:
    app: roscoe-sandbox
    execution-id: "{{EXECUTION_ID}}"
spec:
  ttlSecondsAfterFinished: 3600  # Cleanup after 1 hour
  backoffLimit: 0  # No retries
  template:
    metadata:
      labels:
        app: roscoe-sandbox
    spec:
      runtimeClassName: gvisor  # Use gVisor sandbox
      serviceAccountName: roscoe-sandbox-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: executor
        image: gcr.io/YOUR_PROJECT/roscoe-sandbox:latest
        command: ["bash", "-c", "{{COMMAND}}"]
        workingDir: /workspace/projects/{{CASE_NAME}}
        env:
        - name: EXECUTION_ID
          value: "{{EXECUTION_ID}}"
        - name: CASE_NAME
          value: "{{CASE_NAME}}"
        - name: TAVILY_API_KEY
          valueFrom:
            secretKeyRef:
              name: roscoe-api-keys
              key: tavily-api-key
        volumeMounts:
        - name: workspace
          mountPath: /workspace
        resources:
          limits:
            cpu: "2"
            memory: 4Gi
          requests:
            cpu: "500m"
            memory: 1Gi
      volumes:
      - name: workspace
        persistentVolumeClaim:
          claimName: roscoe-workspace-pvc
      restartPolicy: Never
```

#### 4. Network Policy (Security)

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: roscoe-sandbox-network
  namespace: roscoe
spec:
  podSelector:
    matchLabels:
      app: roscoe-sandbox
  policyTypes:
  - Ingress
  - Egress
  egress:
  # Allow DNS
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53
  # Allow HTTPS to external APIs
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 10.0.0.0/8      # Block internal networks
        - 172.16.0.0/12
        - 192.168.0.0/16
    ports:
    - protocol: TCP
      port: 443
  ingress: []  # No inbound connections allowed
```

#### 5. Python Client for K8s Jobs

```python
# src/roscoe/agents/paralegal/k8s_executor.py
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time
import uuid
import yaml
from datetime import datetime

# Load kube config (in-cluster or local)
try:
    config.load_incluster_config()
except:
    config.load_kube_config()

batch_v1 = client.BatchV1Api()
core_v1 = client.CoreV1Api()

NAMESPACE = "roscoe"
JOB_TEMPLATE_PATH = "/app/k8s/sandbox-job-template.yaml"

def execute_in_sandbox(
    case_name: str,
    command: str,
    timeout: int = 300,
) -> dict:
    """
    Execute a command in a GKE Agent Sandbox pod.
    
    Args:
        case_name: Case folder to work with
        command: Shell command to execute
        timeout: Maximum execution time in seconds
    
    Returns:
        Dict with execution results
    """
    execution_id = f"exec-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    
    # Load and customize job template
    with open(JOB_TEMPLATE_PATH) as f:
        job_template = f.read()
    
    job_yaml = job_template.replace("{{EXECUTION_ID}}", execution_id)
    job_yaml = job_yaml.replace("{{CASE_NAME}}", case_name)
    job_yaml = job_yaml.replace("{{COMMAND}}", command.replace('"', '\\"'))
    
    job_manifest = yaml.safe_load(job_yaml)
    
    try:
        # Create job
        job = batch_v1.create_namespaced_job(NAMESPACE, job_manifest)
        job_name = job.metadata.name
        
        # Wait for completion
        start_time = time.time()
        while time.time() - start_time < timeout:
            job_status = batch_v1.read_namespaced_job_status(job_name, NAMESPACE)
            
            if job_status.status.succeeded:
                break
            if job_status.status.failed:
                break
            
            time.sleep(2)
        
        # Get logs
        pods = core_v1.list_namespaced_pod(
            NAMESPACE,
            label_selector=f"job-name={job_name}"
        )
        
        logs = ""
        if pods.items:
            pod_name = pods.items[0].metadata.name
            logs = core_v1.read_namespaced_pod_log(pod_name, NAMESPACE)
        
        # Determine status
        final_status = batch_v1.read_namespaced_job_status(job_name, NAMESPACE)
        success = final_status.status.succeeded is not None and final_status.status.succeeded > 0
        
        return {
            "execution_id": execution_id,
            "job_name": job_name,
            "success": success,
            "exit_code": 0 if success else 1,
            "stdout": logs,
            "stderr": "" if success else "Job failed or timed out",
            "duration_seconds": time.time() - start_time
        }
        
    except ApiException as e:
        return {
            "execution_id": execution_id,
            "success": False,
            "exit_code": 1,
            "stdout": "",
            "stderr": f"Kubernetes API error: {e.reason}",
        }
```

#### 6. Agent Tool Integration

```python
# src/roscoe/agents/paralegal/tools.py (additions)

def execute_sandboxed(
    case_name: str,
    command: str,
    timeout: int = 300,
) -> str:
    """
    Execute a command in a secure GKE sandbox with direct workspace access.
    
    This provides enterprise-grade isolation using gVisor while allowing
    direct read-write access to the persistent /workspace filesystem.
    
    Args:
        case_name: The case folder to operate on
        command: Shell command to execute
        timeout: Maximum execution time (default: 5 minutes)
    
    Returns:
        Execution results including stdout and status
    
    Examples:
        # Run file organization script
        execute_sandboxed("Wilson-MVA", "python /workspace/Tools/create_file_inventory.py")
        
        # Create directory structure
        execute_sandboxed("Wilson-MVA", "mkdir -p 'Medical Records/Bills' Insurance Lien")
        
        # Move files
        execute_sandboxed("Wilson-MVA", "mv unsorted/*.pdf 'Medical Records/'")
    """
    from roscoe.agents.paralegal.k8s_executor import execute_in_sandbox
    
    result = execute_in_sandbox(case_name, command, timeout)
    
    output = f"**Sandbox Execution: {result['execution_id']}**\n"
    output += f"Job: {result.get('job_name', 'N/A')}\n"
    output += f"Status: {'✓ Success' if result['success'] else '✗ Failed'}\n"
    output += f"Duration: {result.get('duration_seconds', 0):.1f}s\n\n"
    
    if result['stdout']:
        output += f"**Output:**\n```\n{result['stdout']}\n```\n"
    
    if result['stderr']:
        output += f"**Errors:**\n```\n{result['stderr']}\n```"
    
    return output
```

### Advantages

| Benefit | Description |
|---------|-------------|
| **Enterprise Security** | gVisor kernel-level isolation, RBAC, network policies |
| **Scalability** | Kubernetes auto-scaling for multiple concurrent agents |
| **Full Filesystem Access** | PVC mounts enable direct read-write |
| **Internet Access** | Controlled egress via network policies |
| **Audit Trail** | Kubernetes events, pod logs, custom logging |
| **Multi-tenancy** | Namespace isolation for different workloads |

### Challenges & Mitigations

| Challenge | Mitigation |
|-----------|------------|
| Kubernetes complexity | Use GKE Autopilot for managed infrastructure |
| Higher operational cost | Right-size resources, use preemptible nodes |
| Setup time | Use Terraform/Pulumi for infrastructure as code |
| Learning curve | Leverage existing GCP expertise |

---

## Solution Comparison Matrix

| Criteria | Solution 1: Mutation Service | Solution 2: Docker Containers | Solution 3: GKE Sandbox |
|----------|------------------------------|-------------------------------|-------------------------|
| **Implementation Time** | 1-2 weeks | 2-3 weeks | 4-6 weeks |
| **Operational Complexity** | Low | Medium | High |
| **Security Level** | Medium-High | Medium | Very High |
| **Scalability** | Medium | Medium | Very High |
| **Cost** | Low ($50-100/mo) | Low-Medium ($100-200/mo) | Medium-High ($300-500/mo) |
| **File Operation Performance** | Fast (direct) | Fast (mounted) | Fast (PVC) |
| **Internet/Browser Access** | ❌ (separate tool) | ✅ Full | ✅ Full |
| **Existing Script Reuse** | ⚠️ API calls only | ✅ Direct execution | ✅ Direct execution |
| **Rollback Capability** | ✅ Auto-generated | ⚠️ Manual | ⚠️ Via snapshots |
| **Human Approval Workflow** | ✅ Built-in | ⚠️ Add-on needed | ⚠️ Add-on needed |

---

## Recommendation

### For Immediate Implementation (Next 2-4 Weeks)

**Start with Solution 1 (Mutation Service)** combined with your existing RunLoop sandbox:

1. **Mutation Service** handles file operations (move, copy, delete, rename)
2. **RunLoop Sandbox** handles code execution, analysis, and internet operations

This gives you:
- Fastest path to production
- Strong safety guarantees with validation + rollback
- No new major infrastructure
- Clear separation of concerns

### For Full Capability (2-3 Months)

**Transition to Solution 2 (Docker Containers)** which provides:
- Direct execution of existing `/Tools` scripts
- Browser automation with Playwright
- Internet access for searches and API calls
- All file operations in one unified tool

### For Enterprise Scale (6+ Months)

**Migrate to Solution 3 (GKE Sandbox)** when you need:
- Multi-agent concurrent execution
- Enterprise security compliance
- High availability and auto-scaling
- Multi-tenant law firm support

---

## Implementation Roadmap

### Phase 1: Mutation Service (Weeks 1-2)

```bash
# Week 1: Build and deploy mutation service
1. Create FastAPI service with /plans endpoints
2. Deploy as systemd service on GCE VM
3. Add agent tools: submit_reorganization_plan(), apply_plan()

# Week 2: Testing and integration
4. Test with sample case reorganizations
5. Add monitoring and alerting
6. Document usage patterns
```

### Phase 2: Docker Mutator (Weeks 3-4)

```bash
# Week 3: Container setup
1. Build roscoe-mutator Docker image
2. Install Playwright and dependencies
3. Test with mounted GCS volumes

# Week 4: Integration
4. Add execute_case_mutation() tool
5. Add reorganize_case_files() tool  
6. Test full workflows
```

### Phase 3: GKE Migration (Month 2-3)

```bash
# If scaling requires it:
1. Create GKE cluster with Agent Sandbox
2. Set up Filestore PVC
3. Deploy job templates
4. Migrate agent tools to K8s executor
```

---

## Appendix: Environment Variables

```bash
# Add to .env for Mutation Service
MUTATION_SERVICE_URL=http://localhost:8500

# Add to .env for Docker execution
DOCKER_HOST=unix:///var/run/docker.sock

# Add to .env for GKE (if using)
KUBECONFIG=/path/to/kubeconfig
GKE_NAMESPACE=roscoe
```

## Appendix: Safety Checklist

Before deploying any solution:

- [ ] Path validation prevents traversal attacks
- [ ] Operation limits prevent mass deletions
- [ ] Audit logging captures all mutations
- [ ] Rollback scripts generated for every plan
- [ ] Backups taken before destructive operations
- [ ] API keys not exposed in logs
- [ ] Network access controlled and monitored
- [ ] Resource limits prevent runaway processes

