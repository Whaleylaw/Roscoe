# Implementation Plan: Scoped Docker Task Runner

This plan implements the **"Task Runner"** architecture (Solution 2). It enables your agents to execute complex Python scripts (e.g., `create_file_inventory.py`, Playwright automations) against your GCS data by spinning up short-lived, scoped Docker containers on your GCE VM.

## 1. Architecture Overview

The system consists of three components:
1.  **Task Runner Image**: A Docker image pre-loaded with your required libraries (Pandas, Playwright, etc.).
2.  **Execution Service**: A lightweight FastAPI service running on the host VM. It accepts requests from the agent and manages the Docker containers.
3.  **Agent Tool**: A function exposed to the LLM that calls the Execution Service.

**Data Flow:**
1.  Agent calls `run_case_script(script="inventory.py", case="Case-123")`.
2.  Execution Service verifies paths and launches a Docker container.
3.  Service mounts the specific case folder from the host's `gcsfuse` mount (`/mnt/workspace/projects/Case-123`) into the container (`/data`).
4.  Script runs locally within the container, modifying `/data` (which updates GCS).
5.  Container exits; Service returns stdout/stderr to Agent.

---

## 2. The Task Runner Docker Image

This image provides the runtime environment for your scripts.

**File:** `docker/Dockerfile.task-runner`

```dockerfile
# Use a slim Python base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies (needed for Playwright/Pandas/etc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
# Add any other libs your scripts use here
RUN pip install \
    pandas \
    numpy \
    openpyxl \
    python-docx \
    reportlab \
    playwright \
    beautifulsoup4 \
    requests \
    google-cloud-storage

# Install Playwright browsers (if needed for browser tools)
RUN playwright install --with-deps chromium

# Create a non-root user for safety
RUN useradd -m taskrunner
USER taskrunner

WORKDIR /app

# Default entrypoint (can be overridden)
CMD ["python", "--version"]
```

---

## 3. The Execution Service (Host VM)

This service runs on your GCE VM. It acts as the bridge between the Agent and the Docker daemon, ensuring containers are launched with the correct security constraints.

**File:** `services/task_runner/main.py`

```python
import docker
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from pathlib import Path
import os
import logging

# Configuration
HOST_WORKSPACE_ROOT = Path("/mnt/workspace")  # Where gcsfuse is mounted on HOST
HOST_TOOLS_DIR = HOST_WORKSPACE_ROOT / "Tools"
HOST_PROJECTS_DIR = HOST_WORKSPACE_ROOT / "projects"
DOCKER_IMAGE_NAME = "roscoe-task-runner:latest"

# Initialize
app = FastAPI(title="Roscoe Task Runner")
client = docker.from_env()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task-runner")

class ScriptRequest(BaseModel):
    case_name: str
    script_name: str
    args: list[str] = []
    timeout: int = 300  # 5 minutes default

@app.post("/run")
def run_script(req: ScriptRequest):
    """
    Executes a script from /Tools against a specific Case folder.
    """
    # 1. Validation
    # Ensure case exists
    host_case_path = HOST_PROJECTS_DIR / req.case_name
    if not host_case_path.exists():
        raise HTTPException(404, detail=f"Case folder not found: {req.case_name}")

    # Ensure script exists
    host_script_path = HOST_TOOLS_DIR / req.script_name
    if not host_script_path.exists():
        raise HTTPException(404, detail=f"Script not found: {req.script_name}")
    
    # 2. Prepare Docker config
    # We mount the specific case to /data (Read-Write)
    # We mount Tools to /tools (Read-Only)
    volumes = {
        str(host_case_path): {'bind': '/data', 'mode': 'rw'},
        str(HOST_TOOLS_DIR): {'bind': '/tools', 'mode': 'ro'}
    }
    
    # Construct command: python /tools/script.py [args]
    # Note: Scripts should be written to accept input paths via args or default to CWD
    # We set CWD to /data so scripts running "./" work on the case files.
    cmd = ["python", f"/tools/{req.script_name}"] + req.args

    try:
        logger.info(f"Launching container for {req.case_name} with {req.script_name}")
        
        # 3. Run Container
        container = client.containers.run(
            image=DOCKER_IMAGE_NAME,
            command=cmd,
            volumes=volumes,
            working_dir="/data",  # Critical: CWD is the case root
            user="taskrunner",
            remove=True,         # Auto-cleanup
            detach=False,        # Wait for completion
            stdout=True,
            stderr=True,
            mem_limit="2g",      # Resource Cap
            network_mode="host"  # Or 'bridge' if you need internet but want isolation
        )
        
        # Docker client returns bytes if detach=False
        output = container.decode('utf-8')
        
        return {
            "status": "success",
            "output": output
        }

    except docker.errors.ContainerError as e:
        # Script ran but failed (non-zero exit)
        return {
            "status": "script_error",
            "exit_code": e.exit_status,
            "output": e.stderr.decode('utf-8') if e.stderr else e.stdout.decode('utf-8')
        }
    except Exception as e:
        logger.error(f"System error: {e}")
        raise HTTPException(500, detail=str(e))
```

---

## 4. Agent Tool Integration

Add this tool to your LangGraph/Agent definition. This is what the LLM "sees".

**File:** `src/roscoe/agents/paralegal/tools.py` (Update)

```python
import requests
import os

TASK_RUNNER_URL = os.getenv("TASK_RUNNER_URL", "http://localhost:8000")

def run_case_script(case_name: str, script_name: str, arguments: str = "") -> str:
    """
    Runs a Python script from the /Tools directory against a specific case folder.
    
    Use this for:
    - Complex file inventory or analysis (create_file_inventory.py)
    - Bulk reorganization logic defined in scripts
    - Generating PDF/Docx reports using python libraries
    
    The script runs in a container where the Case folder is mounted at /data (current working directory).
    
    Args:
        case_name: The exact name of the case folder (e.g., "Caryn-McCay-MVA")
        script_name: Filename of the script in /Tools (e.g., "create_file_inventory.py")
        arguments: Optional command line arguments string (e.g., "--format json --verbose")
    """
    payload = {
        "case_name": case_name,
        "script_name": script_name,
        "args": arguments.split() if arguments else []
    }
    
    try:
        resp = requests.post(f"{TASK_RUNNER_URL}/run", json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        
        if data["status"] == "success":
            return f"SUCCESS:\n{data['output']}"
        else:
            return f"SCRIPT FAILED (Exit {data.get('exit_code')}):\n{data['output']}"
            
    except requests.exceptions.RequestException as e:
        return f"SYSTEM ERROR: Could not contact Task Runner service. {e}"
```

---

## 5. Deployment Guide

### A. On the Host VM (One-time setup)

1.  **Install Docker** (if not present):
    ```bash
    sudo apt-get update && sudo apt-get install -y docker.io
    sudo usermod -aG docker $USER
    # Log out and back in
    ```

2.  **Build the Image**:
    ```bash
    cd /opt/roscoe/docker
    # (Place Dockerfile.task-runner here)
    docker build -t roscoe-task-runner:latest -f Dockerfile.task-runner .
    ```

3.  **Setup Python Service**:
    ```bash
    cd /opt/roscoe/services/task_runner
    # (Place main.py here)
    python3 -m venv venv
    source venv/bin/activate
    pip install fastapi uvicorn docker pydantic
    ```

4.  **Create Systemd Service**:
    **File:** `/etc/systemd/system/roscoe-task-runner.service`
    ```ini
    [Unit]
    Description=Roscoe Task Runner API
    After=docker.service network.target

    [Service]
    User=root
    # Root needed to talk to docker socket usually, or add user to docker group
    WorkingDirectory=/opt/roscoe/services/task_runner
    ExecStart=/opt/roscoe/services/task_runner/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
    
    ```bash
    sudo systemctl enable roscoe-task-runner
    sudo systemctl start roscoe-task-runner
    ```

### B. Updating Scripts

To make your existing scripts compatible, ensure they:
1.  Do **not** hardcode absolute paths like `/projects/...`.
2.  Instead, default to using the current working directory (which will be the case root) OR accept a `--root` argument.
3.  Example `create_file_inventory.py` tweak:
    ```python
    import argparse
    import os
    
    parser = argparse.ArgumentParser()
    # Default to '.' because we mount the case to CWD
    parser.add_argument("--root", default=".") 
    args = parser.parse_args()
    
    # Use args.root ...
    ```

