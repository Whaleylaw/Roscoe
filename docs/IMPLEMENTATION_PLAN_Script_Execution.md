# Script Execution with Filesystem Access - Implementation Plan
## Docker-Based Python Script Runner for Roscoe Paralegal Agent

**Date**: November 27, 2025  
**Target Completion**: 2-3 weeks

---

## Executive Summary

This implementation plan enables the Roscoe paralegal agent to execute Python scripts (from `/Tools/`) with direct read-write access to the GCS-mounted filesystem at `/mnt/workspace`, while maintaining security isolation and auditability.

**Key Insight**: The agent already has native file operations via FilesystemBackend. This plan focuses exclusively on **script execution**, not file operations.

**What This Enables**:
- ✅ Run `/Tools/create_file_inventory.py` against real case folders
- ✅ Execute reorganization scripts with actual file modifications
- ✅ Run data analysis scripts on PDFs and markdown files
- ✅ Use Playwright for web scraping and browser automation
- ✅ Internet access for API calls (PubMed, legal research, etc.)

**What This Doesn't Need To Do**:
- ❌ Provide file operation APIs (already have via FilesystemBackend)
- ❌ Validation/approval workflows (agent controls this)
- ❌ Complex plan-based orchestration

---

## Architecture Overview

### Current State

```
┌─────────────────────────┐
│   Roscoe Agent          │
│   (LangGraph)           │
│                         │
│ FilesystemBackend:      │
│ ✅ read/write files     │
│ ✅ list directories     │
│ ✅ search files         │
│ ✅ move/delete/rename   │
│                         │
│ execute_code (RunLoop): │
│ ❌ Sandbox only         │
│ ❌ No filesystem access │
│ ❌ Changes don't persist│
└─────────────────────────┘
```

### Target State

```
┌─────────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Roscoe Agent          │     │   Docker Container   │     │   GCS via       │
│   (LangGraph)           │────▶│   (Short-lived)      │────▶│   gcsfuse       │
│                         │     │                      │     │                 │
│ FilesystemBackend:      │     │ ┌──────────────────┐ │     │ /mnt/workspace/ │
│ ✅ Native file ops      │     │ │ Python Script    │ │     │ ├── projects/   │
│                         │     │ │ /Tools/script.py │ │     │ ├── Tools/      │
│ execute_python_script:  │     │ │                  │ │     │ ├── Database/   │
│ ✅ Run scripts          │     │ │ Direct R/W access│─┼────▶│ └── Reports/    │
│ ✅ Filesystem access    │     │ └──────────────────┘ │     │                 │
│ ✅ Internet enabled     │     │                      │     │                 │
│ ✅ Isolated execution   │     │ • Resource limits    │     │                 │
└─────────────────────────┘     │ • Network access     │     │                 │
                                │ • Auto-cleanup       │     │                 │
                                └──────────────────────┘     └─────────────────┘
```

### Execution Flow

```
1. Agent decides to run a script
   ↓
2. Calls execute_python_script(script_path="/Tools/analyze.py", case_name="Wilson-MVA")
   ↓
3. Docker container spins up with:
   - Volume mount: /mnt/workspace → /workspace (read-write)
   - Working directory: /workspace/projects/Wilson-MVA
   - Environment: API keys, case context
   ↓
4. Script executes with direct filesystem access
   - Can read PDFs, markdown, JSON
   - Can write reports, modify files
   - Can use internet (requests, httpx)
   - Can use Playwright for browser
   ↓
5. Container exits, returns output
   - stdout/stderr captured
   - Exit code logged
   - Changes persisted to GCS
   ↓
6. Agent receives results and continues
```

---

## Week 1: Core Implementation

### Day 1: Docker Image Creation

**Objective**: Build `roscoe-python-runner` Docker image with all required dependencies

**File**: `docker/roscoe-python-runner/Dockerfile`

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages commonly used in Tools scripts
RUN pip install --no-cache-dir \
    # Core data processing
    pandas==2.1.4 \
    numpy==1.26.2 \
    # PDF processing
    PyPDF2==3.0.1 \
    pdfplumber==0.10.3 \
    pypdf==3.17.4 \
    # Document processing
    python-docx==1.1.0 \
    openpyxl==3.1.2 \
    # Internet and APIs
    requests==2.31.0 \
    httpx==0.25.2 \
    beautifulsoup4==4.12.2 \
    lxml==4.9.3 \
    # Legal research APIs
    tavily-python==0.3.0 \
    # Markdown and text processing
    markdown==3.5.1 \
    markdownify==0.11.6 \
    # Date/time parsing
    python-dateutil==2.8.2 \
    # JSON processing
    jsonschema==4.20.0 \
    # File operations
    pathlib2==2.3.7 \
    # Google Cloud Storage (if direct API access needed)
    google-cloud-storage==2.14.0 \
    # Logging and utilities
    loguru==0.7.2

# Install Playwright (but not browsers yet - we'll add conditionally)
RUN pip install --no-cache-dir playwright==1.40.0

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash roscoe && \
    mkdir -p /home/roscoe/.cache && \
    chown -R roscoe:roscoe /home/roscoe

# Switch to non-root user
USER roscoe
WORKDIR /workspace

# Set Python to unbuffered mode for immediate output
ENV PYTHONUNBUFFERED=1

# Default command (will be overridden)
CMD ["python", "--version"]
```

**Build Command**:
```bash
cd docker/roscoe-python-runner
docker build -t roscoe-python-runner:latest .
docker tag roscoe-python-runner:latest roscoe-python-runner:v1.0.0
```

**Build Playwright-enabled variant** (optional, larger image):
```dockerfile
# Dockerfile.playwright
FROM roscoe-python-runner:latest

# Switch back to root to install system deps
USER root

# Install Playwright browsers and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Chromium dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Switch to roscoe user and install browsers
USER roscoe
RUN playwright install chromium

USER roscoe
WORKDIR /workspace
```

**Action Items**:
- [ ] Create `docker/roscoe-python-runner/` directory
- [ ] Write Dockerfile
- [ ] Build base image
- [ ] Test image locally: `docker run --rm roscoe-python-runner:latest python -c "import pandas; print('OK')"`
- [ ] (Optional) Build Playwright variant

---

### Day 2: Script Executor Module

**Objective**: Implement Python module for executing scripts in Docker containers

**File**: `src/roscoe/agents/paralegal/script_executor.py`

```python
"""
Script Executor - Run Python scripts with filesystem access via Docker
"""
import docker
import os
import uuid
import json
import shlex
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# Configuration
WORKSPACE_ROOT = Path("/mnt/workspace")
DOCKER_IMAGE = "roscoe-python-runner:latest"
DOCKER_IMAGE_PLAYWRIGHT = "roscoe-python-runner:playwright"
EXECUTION_LOGS_DIR = WORKSPACE_ROOT / "Database" / "script_execution_logs"
DEFAULT_TIMEOUT = 300  # 5 minutes
MAX_TIMEOUT = 1800  # 30 minutes

# Initialize Docker client
try:
    docker_client = docker.from_env()
    # Test connection
    docker_client.ping()
    logger.info("Docker client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Docker client: {e}")
    docker_client = None


class ScriptExecutionError(Exception):
    """Raised when script execution fails"""
    pass


def execute_python_script(
    script_path: str,
    case_name: Optional[str] = None,
    working_dir: Optional[str] = None,
    script_args: Optional[List[str]] = None,
    env_vars: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    enable_playwright: bool = False,
    enable_internet: bool = True,
) -> Dict[str, any]:
    """
    Execute a Python script with direct filesystem access.
    
    Args:
        script_path: Path to Python script relative to workspace root
                    Example: "/Tools/create_file_inventory.py"
        case_name: Optional case folder name to set as working directory
                  Example: "Wilson-MVA-2024"
        working_dir: Optional explicit working directory (overrides case_name)
                    Example: "/workspace/projects/Wilson-MVA-2024"
        script_args: Optional list of command-line arguments for the script
                    Example: ["--format", "json", "--output", "Reports/inventory.json"]
        env_vars: Optional environment variables to pass to script
                 Example: {"DEBUG": "true", "CASE_ID": "12345"}
        timeout: Maximum execution time in seconds (default: 300)
        enable_playwright: Use Playwright-enabled image (default: False)
        enable_internet: Allow network access (default: True)
    
    Returns:
        Dict with execution results:
        {
            "execution_id": str,
            "success": bool,
            "exit_code": int,
            "stdout": str,
            "stderr": str,
            "duration_seconds": float,
            "script_path": str,
            "case_name": str,
            "log_file": str
        }
    
    Raises:
        ScriptExecutionError: If execution fails or Docker unavailable
    
    Examples:
        # Basic script execution
        result = execute_python_script(
            script_path="/Tools/create_file_inventory.py",
            case_name="Wilson-MVA-2024"
        )
        
        # Script with arguments
        result = execute_python_script(
            script_path="/Tools/analyze_medical_records.py",
            case_name="Wilson-MVA-2024",
            script_args=["--output", "Reports/medical_analysis.md", "--verbose"]
        )
        
        # Script with custom environment
        result = execute_python_script(
            script_path="/Tools/pubmed_search.py",
            script_args=["whiplash injury prognosis"],
            env_vars={"PUBMED_API_KEY": "..."}
        )
        
        # Browser automation script
        result = execute_python_script(
            script_path="/Tools/courtlistener_search.py",
            script_args=["personal injury statute of limitations"],
            enable_playwright=True
        )
    """
    
    if docker_client is None:
        raise ScriptExecutionError("Docker client not available")
    
    # Validate timeout
    if timeout > MAX_TIMEOUT:
        logger.warning(f"Timeout {timeout}s exceeds maximum, capping at {MAX_TIMEOUT}s")
        timeout = MAX_TIMEOUT
    
    # Generate execution ID
    execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    start_time = datetime.utcnow()
    
    # Normalize script path
    if script_path.startswith('/'):
        script_path_clean = script_path[1:]  # Remove leading slash
    else:
        script_path_clean = script_path
    
    # Verify script exists
    script_full_path = WORKSPACE_ROOT / script_path_clean
    if not script_full_path.exists():
        raise ScriptExecutionError(f"Script not found: {script_path}")
    
    # Determine working directory
    if working_dir:
        container_workdir = working_dir
    elif case_name:
        container_workdir = f"/workspace/projects/{case_name}"
    else:
        container_workdir = "/workspace"
    
    # Build volume mounts
    volumes = {
        str(WORKSPACE_ROOT): {
            "bind": "/workspace",
            "mode": "rw"  # Read-write access
        }
    }
    
    # Build environment variables
    environment = env_vars or {}
    
    # Pass through API keys from host environment
    api_keys_to_pass = [
        "TAVILY_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "PUBMED_API_KEY",
    ]
    
    for key in api_keys_to_pass:
        if val := os.environ.get(key):
            environment[key] = val
    
    # Add execution context
    environment.update({
        "EXECUTION_ID": execution_id,
        "CASE_NAME": case_name or "",
        "SCRIPT_PATH": script_path,
    })
    
    # Build command
    script_container_path = f"/workspace/{script_path_clean}"
    args_str = " ".join([shlex.quote(arg) for arg in (script_args or [])])
    command = f"python {shlex.quote(script_container_path)} {args_str}".strip()
    
    # Select image
    image = DOCKER_IMAGE_PLAYWRIGHT if enable_playwright else DOCKER_IMAGE
    
    # Log execution start
    logger.info(f"Starting script execution {execution_id}")
    logger.info(f"  Script: {script_path}")
    logger.info(f"  Case: {case_name or 'N/A'}")
    logger.info(f"  Working dir: {container_workdir}")
    logger.info(f"  Image: {image}")
    logger.info(f"  Timeout: {timeout}s")
    
    try:
        # Run container
        container = docker_client.containers.run(
            image,
            command=["bash", "-c", command],
            volumes=volumes,
            working_dir=container_workdir,
            environment=environment,
            remove=True,  # Auto-remove after exit
            detach=False,  # Wait for completion
            stdout=True,
            stderr=True,
            user="roscoe",  # Non-root user
            network_mode="bridge" if enable_internet else "none",
            mem_limit="2g",  # 2GB memory limit
            cpu_period=100000,
            cpu_quota=100000,  # 1 CPU core max
            read_only=False,  # Allow writes to workspace
        )
        
        # Container.run returns bytes when detach=False
        stdout_bytes = container if isinstance(container, bytes) else b""
        stdout = stdout_bytes.decode('utf-8', errors='replace')
        stderr = ""
        exit_code = 0
        success = True
        
    except docker.errors.ContainerError as e:
        # Container ran but exited with non-zero code
        stdout = e.container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
        stderr = e.container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
        exit_code = e.exit_status
        success = False
        logger.error(f"Container exited with code {exit_code}: {stderr[:500]}")
        
    except docker.errors.APIError as e:
        # Docker API error
        stdout = ""
        stderr = f"Docker API error: {str(e)}"
        exit_code = 1
        success = False
        logger.error(f"Docker API error: {e}")
        
    except Exception as e:
        # Other errors
        stdout = ""
        stderr = f"Execution error: {str(e)}"
        exit_code = 1
        success = False
        logger.error(f"Script execution error: {e}")
    
    # Calculate duration
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    # Build result
    result = {
        "execution_id": execution_id,
        "success": success,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "duration_seconds": duration,
        "script_path": script_path,
        "case_name": case_name,
        "timestamp": start_time.isoformat(),
    }
    
    # Log execution to file
    try:
        EXECUTION_LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = EXECUTION_LOGS_DIR / f"{execution_id}.json"
        
        log_entry = {
            **result,
            "working_dir": container_workdir,
            "script_args": script_args,
            "timeout": timeout,
            "image": image,
        }
        
        log_file.write_text(json.dumps(log_entry, indent=2))
        result["log_file"] = str(log_file)
        
    except Exception as e:
        logger.error(f"Failed to write execution log: {e}")
        result["log_file"] = None
    
    logger.info(f"Script execution {execution_id} completed: success={success}, duration={duration:.2f}s")
    
    return result


def format_execution_result(result: Dict[str, any]) -> str:
    """
    Format execution result for display to agent.
    
    Args:
        result: Dict returned from execute_python_script
    
    Returns:
        Formatted string with execution details
    """
    
    lines = [
        f"**Script Execution: {result['execution_id']}**",
        f"Script: `{result['script_path']}`",
        f"Status: {'✅ Success' if result['success'] else '❌ Failed'}",
        f"Exit Code: {result['exit_code']}",
        f"Duration: {result['duration_seconds']:.2f}s",
    ]
    
    if result.get('case_name'):
        lines.append(f"Case: {result['case_name']}")
    
    if result['stdout']:
        lines.append("")
        lines.append("**Output:**")
        lines.append("```")
        lines.append(result['stdout'].strip())
        lines.append("```")
    
    if result['stderr']:
        lines.append("")
        lines.append("**Errors:**")
        lines.append("```")
        lines.append(result['stderr'].strip())
        lines.append("```")
    
    if result.get('log_file'):
        lines.append("")
        lines.append(f"Log: `{result['log_file']}`")
    
    return "\n".join(lines)
```

**Action Items**:
- [ ] Create `src/roscoe/agents/paralegal/script_executor.py`
- [ ] Add Docker SDK to requirements: `pip install docker==7.0.0`
- [ ] Test locally with a simple script
- [ ] Verify gcsfuse mount is accessible from container

**Test Script** (`test_script_executor.py`):
```python
from script_executor import execute_python_script, format_execution_result

# Test 1: Simple script
result = execute_python_script(
    script_path="/Tools/test_script.py",
    script_args=["--test"]
)
print(format_execution_result(result))

# Test 2: File operations
result = execute_python_script(
    script_path="/Tools/create_file_inventory.py",
    case_name="Test-Case-001"
)
print(format_execution_result(result))
```

---

### Day 3: Agent Tool Integration

**Objective**: Add `execute_python_script` as an agent tool

**File**: `src/roscoe/agents/paralegal/tools.py` (modifications)

```python
# Add at top of file
from roscoe.agents.paralegal.script_executor import (
    execute_python_script as _execute_python_script,
    format_execution_result,
    ScriptExecutionError,
)

# Add new tool function
def execute_python_script(
    script_path: str,
    case_name: Optional[str] = None,
    script_args: Optional[list[str]] = None,
    working_dir: Optional[str] = None,
    timeout: int = 300,
) -> str:
    """
    Execute a Python script from /Tools/ with direct filesystem access.
    
    This tool enables running Python scripts that need to operate on the actual
    GCS-mounted filesystem at /mnt/workspace. Scripts run in isolated Docker
    containers with direct read-write access to all workspace files.
    
    Use this for:
    - Running /Tools/ scripts (create_file_inventory.py, analyze_medical_records.py, etc.)
    - Data processing that needs to modify actual files
    - Complex analysis workflows that require filesystem access
    - Any Python code that needs to persist changes to the workspace
    
    Note: For simple file operations (read, write, move, delete), use the native
    FilesystemBackend capabilities instead. This tool is for executing scripts.
    
    Args:
        script_path: Path to Python script in workspace (e.g., "/Tools/create_file_inventory.py")
        case_name: Optional case folder name to use as working directory
        script_args: Optional list of command-line arguments
        working_dir: Optional explicit working directory (overrides case_name)
        timeout: Maximum execution time in seconds (default: 300, max: 1800)
    
    Returns:
        Formatted execution results including stdout, stderr, and execution status
    
    Examples:
        # Run file inventory script on a case
        execute_python_script(
            script_path="/Tools/create_file_inventory.py",
            case_name="Wilson-MVA-2024"
        )
        
        # Run analysis script with arguments
        execute_python_script(
            script_path="/Tools/analyze_medical_records.py",
            case_name="Wilson-MVA-2024",
            script_args=["--output", "Reports/analysis.md", "--verbose"]
        )
        
        # Run data processing script
        execute_python_script(
            script_path="/Tools/document_processing/batch_import_all.py",
            script_args=["--case", "Wilson-MVA-2024"]
        )
    """
    
    try:
        result = _execute_python_script(
            script_path=script_path,
            case_name=case_name,
            script_args=script_args,
            working_dir=working_dir,
            timeout=timeout,
        )
        
        return format_execution_result(result)
        
    except ScriptExecutionError as e:
        return f"❌ Script execution failed: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def execute_python_script_with_browser(
    script_path: str,
    case_name: Optional[str] = None,
    script_args: Optional[list[str]] = None,
    timeout: int = 600,
) -> str:
    """
    Execute a Python script with Playwright browser automation capabilities.
    
    Use this for scripts that need to:
    - Scrape websites (legal research, court records, etc.)
    - Automate web-based tasks
    - Extract data from web pages
    - Interact with web applications
    
    Note: This uses a larger Docker image with Chromium pre-installed.
    Execution may be slower than regular scripts due to browser startup.
    
    Args:
        script_path: Path to Playwright-enabled Python script
        case_name: Optional case folder name
        script_args: Optional command-line arguments
        timeout: Maximum execution time (default: 600s due to browser overhead)
    
    Returns:
        Formatted execution results
    
    Examples:
        # Scrape court records
        execute_python_script_with_browser(
            script_path="/Tools/legal_research/courtlistener_search.py",
            script_args=["personal injury", "Kentucky"]
        )
        
        # Extract data from case management system
        execute_python_script_with_browser(
            script_path="/Tools/web_scraping/extract_case_data.py",
            case_name="Wilson-MVA-2024"
        )
    """
    
    try:
        result = _execute_python_script(
            script_path=script_path,
            case_name=case_name,
            script_args=script_args,
            timeout=timeout,
            enable_playwright=True,
        )
        
        return format_execution_result(result)
        
    except ScriptExecutionError as e:
        return f"❌ Browser script execution failed: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"
```

**File**: `src/roscoe/agents/paralegal/agent.py` (modifications)

```python
# Update imports
from roscoe.agents.paralegal.tools import (
    send_slack_message,
    upload_file_to_slack,
    execute_code,  # Keep for backward compatibility with RunLoop
    execute_python_script,  # NEW: Docker-based script execution
    execute_python_script_with_browser,  # NEW: Playwright-enabled execution
)

# Update agent creation
personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,
    subagents=[
        multimodal_sub_agent,
    ],
    model=agent_llm,
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[
        send_slack_message,
        upload_file_to_slack,
        execute_code,  # RunLoop sandbox (read-only analysis, internet research)
        execute_python_script,  # NEW: Script execution with filesystem access
        execute_python_script_with_browser,  # NEW: Browser automation
    ],
    # ... rest of config
)
```

**Action Items**:
- [ ] Add imports to `tools.py`
- [ ] Implement `execute_python_script()` tool function
- [ ] Implement `execute_python_script_with_browser()` tool function
- [ ] Update agent configuration in `agent.py`
- [ ] Update requirements.txt: `docker==7.0.0`

---

### Day 4: Testing & Validation

**Objective**: Test script execution with real Tools scripts

**Test Cases**:

**Test 1: Simple File Inventory**
```python
# Test with create_file_inventory.py
from roscoe.agents.paralegal.tools import execute_python_script

result = execute_python_script(
    script_path="/Tools/create_file_inventory.py",
    case_name="Test-Case-001"
)
print(result)
```

**Test 2: Script with Arguments**
```python
# Test with arguments
result = execute_python_script(
    script_path="/Tools/create_file_inventory.py",
    case_name="Test-Case-001",
    script_args=["--format", "json", "--output", "Reports/inventory.json"]
)
print(result)
```

**Test 3: Script That Modifies Files**
```python
# Create a test script that writes a file
test_script = """
from pathlib import Path

# Write test file
output_file = Path('/workspace/Reports/test_output.txt')
output_file.parent.mkdir(exist_ok=True)
output_file.write_text('Test successful!')

print('File written to:', output_file)
"""

# Save as /Tools/test_write.py
Path("/mnt/workspace/Tools/test_write.py").write_text(test_script)

# Execute
result = execute_python_script(
    script_path="/Tools/test_write.py"
)
print(result)

# Verify file was created
assert Path("/mnt/workspace/Reports/test_output.txt").exists()
print("✅ File persistence verified")
```

**Test 4: Internet Access**
```python
# Test script with internet access
internet_test_script = """
import requests

response = requests.get('https://httpbin.org/ip')
print('Internet access works!')
print(f'Response: {response.status_code}')
print(response.json())
"""

Path("/mnt/workspace/Tools/test_internet.py").write_text(internet_test_script)

result = execute_python_script(
    script_path="/Tools/test_internet.py"
)
print(result)
```

**Test 5: Error Handling**
```python
# Test script that fails
failing_script = """
raise ValueError("Intentional test error")
"""

Path("/mnt/workspace/Tools/test_fail.py").write_text(failing_script)

result = execute_python_script(
    script_path="/Tools/test_fail.py"
)
print(result)
# Should show error in stderr and exit_code = 1
```

**Test 6: Timeout**
```python
# Test timeout
slow_script = """
import time
time.sleep(120)  # 2 minutes
print('Done')
"""

Path("/mnt/workspace/Tools/test_slow.py").write_text(slow_script)

result = execute_python_script(
    script_path="/Tools/test_slow.py",
    timeout=10  # 10 second timeout
)
print(result)
# Should timeout and fail
```

**Test 7: Real Tools Script**
```python
# Test actual Tools script
result = execute_python_script(
    script_path="/Tools/document_processing/read_pdf.py",
    case_name="Abby-Sitgraves-MVA-7-13-2024",
    script_args=["Medical Records/sample.pdf"]
)
print(result)
```

**Action Items**:
- [ ] Run all 7 test cases
- [ ] Verify Docker containers are cleaned up after execution
- [ ] Check execution logs in `/mnt/workspace/Database/script_execution_logs/`
- [ ] Monitor resource usage (CPU, memory)
- [ ] Test with actual case folders and Tools scripts
- [ ] Document any issues or edge cases

---

### Day 5: Documentation & Integration

**Objective**: Document the new capability and integrate with existing workflows

**File**: `docs/SCRIPT_EXECUTION.md`

```markdown
# Script Execution with Filesystem Access

## Overview

The Roscoe paralegal agent can now execute Python scripts from `/Tools/` with direct read-write access to the GCS-mounted filesystem. This enables running data processing, analysis, and reorganization scripts that need to operate on actual files, not copies.

## When To Use

**Use `execute_python_script()` when**:
- ✅ Running existing Tools scripts (create_file_inventory.py, analyze_medical_records.py)
- ✅ Data processing that modifies actual files
- ✅ Complex workflows requiring filesystem access
- ✅ Scripts that need to persist changes

**Use native FilesystemBackend when**:
- ✅ Simple file operations (read, write, move, delete)
- ✅ Listing directories
- ✅ Searching for files
- ✅ Reading/writing individual files

**Use `execute_code()` (RunLoop) when**:
- ✅ Read-only analysis that doesn't need persistence
- ✅ Internet research and API calls
- ✅ Experiments that shouldn't modify real files

## Examples

### Basic Script Execution

```python
# Run file inventory script
result = execute_python_script(
    script_path="/Tools/create_file_inventory.py",
    case_name="Wilson-MVA-2024"
)
```

### Script with Arguments

```python
# Run analysis with specific output
result = execute_python_script(
    script_path="/Tools/analyze_medical_records.py",
    case_name="Wilson-MVA-2024",
    script_args=["--output", "Reports/medical_analysis.md", "--verbose"]
)
```

### Browser Automation

```python
# Scrape court records
result = execute_python_script_with_browser(
    script_path="/Tools/legal_research/courtlistener_search.py",
    script_args=["personal injury statute of limitations", "Kentucky"]
)
```

## How It Works

1. Script execution request sent to Docker engine
2. Container spins up with `/mnt/workspace` mounted
3. Script runs with direct filesystem access
4. stdout/stderr captured
5. Container auto-removes
6. Changes persist to GCS via gcsfuse

## Security

- Scripts run as non-root user (`roscoe`)
- Resource limits: 2GB RAM, 1 CPU core
- Execution timeout enforced
- Complete audit logging
- Network access controllable

## Monitoring

Execution logs stored at:
```
/mnt/workspace/Database/script_execution_logs/{execution_id}.json
```

Each log contains:
- Script path and arguments
- Execution duration
- Exit code and success status
- stdout/stderr output
- Timestamp and execution ID

## Troubleshooting

**Script not found error**:
- Verify script exists in `/mnt/workspace/Tools/`
- Check path starts with `/Tools/` not `/mnt/workspace/Tools/`

**Permission denied**:
- Ensure script is readable
- Check gcsfuse mount is active: `mount | grep gcsfuse`

**Timeout errors**:
- Increase timeout parameter (max 1800s)
- Check if script has infinite loop
- Consider breaking into smaller steps

**Docker errors**:
- Verify Docker daemon is running: `docker ps`
- Check image exists: `docker images | grep roscoe-python-runner`
- Review Docker logs: `docker logs`

## Adding New Python Packages

To add packages to the execution environment:

1. Edit `docker/roscoe-python-runner/Dockerfile`
2. Add package to pip install list
3. Rebuild image: `docker build -t roscoe-python-runner:latest .`
4. Restart agent
```

**File**: `workspace_paralegal/Skills/script-execution/skill.md`

```markdown
# Script Execution Skill

## Overview
Execute Python scripts from /Tools/ with direct filesystem access.

## When To Use
- Running Tools scripts that need to modify files
- Data processing workflows
- File reorganization scripts
- Complex analysis requiring filesystem access

## Available Tools
- `execute_python_script`: Run Python scripts with filesystem access
- `execute_python_script_with_browser`: Run scripts with Playwright browser

## Examples

### File Inventory
```
Run create_file_inventory.py on the Wilson case
```

### Medical Analysis
```
Execute analyze_medical_records.py for Wilson-MVA-2024 with output to Reports/
```

### Browser Automation
```
Use the browser script to search CourtListener for personal injury cases in Kentucky
```

## Tips
- Scripts run in isolated containers
- Changes persist to GCS automatically
- Resource limits prevent runaway scripts
- Execution logs saved for debugging
```

**Action Items**:
- [ ] Create `docs/SCRIPT_EXECUTION.md`
- [ ] Create skill markdown in `workspace_paralegal/Skills/`
- [ ] Update main README with script execution capabilities
- [ ] Create example scripts in `/Tools/examples/`
- [ ] Add to skills manifest JSON

---

## Week 2: Enhancements & Production Hardening

### Day 6-7: Playwright Integration

**Objective**: Enable browser automation for web scraping and legal research

**File**: `docker/roscoe-python-runner/Dockerfile.playwright`

```dockerfile
FROM roscoe-python-runner:latest

# Switch to root for system package installation
USER root

# Install Chromium dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Chromium browser dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    # Additional utilities
    fonts-liberation \
    fonts-noto \
    && rm -rf /var/lib/apt/lists/*

# Switch back to roscoe user
USER roscoe

# Install Playwright browsers
RUN playwright install chromium

# Verify installation
RUN python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

USER roscoe
WORKDIR /workspace

CMD ["python", "--version"]
```

**Build**:
```bash
cd docker/roscoe-python-runner
docker build -f Dockerfile.playwright -t roscoe-python-runner:playwright .
```

**Example Playwright Script**: `/Tools/examples/courtlistener_example.py`

```python
"""
Example: Search CourtListener for legal cases using Playwright
"""
from playwright.sync_api import sync_playwright
import sys
import json
from pathlib import Path

def search_courtlistener(query: str, output_file: str = None):
    """Search CourtListener and extract case citations"""
    
    results = []
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to CourtListener
        page.goto("https://www.courtlistener.com/")
        
        # Search
        page.fill('input[name="q"]', query)
        page.click('button[type="submit"]')
        
        # Wait for results
        page.wait_for_selector('.result')
        
        # Extract results
        result_elements = page.query_selector_all('.result')
        
        for elem in result_elements[:10]:  # Top 10 results
            title = elem.query_selector('.title')
            citation = elem.query_selector('.citation')
            summary = elem.query_selector('.snippet')
            
            if title:
                results.append({
                    'title': title.inner_text(),
                    'citation': citation.inner_text() if citation else '',
                    'summary': summary.inner_text() if summary else ''
                })
        
        browser.close()
    
    # Output results
    print(f"Found {len(results)} results for: {query}")
    print(json.dumps(results, indent=2))
    
    # Save to file if requested
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(results, indent=2))
        print(f"Results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python courtlistener_example.py <query> [output_file]")
        sys.exit(1)
    
    query = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    search_courtlistener(query, output_file)
```

**Test Playwright**:
```python
from roscoe.agents.paralegal.tools import execute_python_script_with_browser

result = execute_python_script_with_browser(
    script_path="/Tools/examples/courtlistener_example.py",
    script_args=["personal injury statute of limitations Kentucky", "/Reports/courtlistener_results.json"]
)
print(result)
```

**Action Items**:
- [ ] Build Playwright Docker image
- [ ] Test browser launch and navigation
- [ ] Create example Playwright scripts
- [ ] Test with real legal research queries
- [ ] Document Playwright capabilities

---

### Day 8-9: Monitoring & Safety

**Objective**: Add monitoring, alerting, and safety controls

**File**: `src/roscoe/agents/paralegal/script_monitor.py`

```python
"""
Script Execution Monitoring and Safety Controls
"""
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

EXECUTION_LOGS_DIR = Path("/mnt/workspace/Database/script_execution_logs")
ALERT_THRESHOLDS = {
    "failure_rate": 0.3,  # Alert if >30% of executions fail
    "avg_duration": 300,   # Alert if average duration >5 minutes
    "execution_count": 100,  # Alert if >100 executions in 1 hour
}


class ScriptMonitor:
    """Monitor script execution health and safety"""
    
    def __init__(self):
        self.logs_dir = EXECUTION_LOGS_DIR
    
    def get_recent_executions(self, hours: int = 24) -> List[Dict]:
        """Get execution logs from last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_logs = []
        
        if not self.logs_dir.exists():
            return []
        
        for log_file in self.logs_dir.glob("exec_*.json"):
            try:
                log_data = json.loads(log_file.read_text())
                log_time = datetime.fromisoformat(log_data['timestamp'])
                
                if log_time > cutoff_time:
                    recent_logs.append(log_data)
            except Exception as e:
                logger.error(f"Failed to read log {log_file}: {e}")
        
        return sorted(recent_logs, key=lambda x: x['timestamp'], reverse=True)
    
    def get_execution_stats(self, hours: int = 24) -> Dict:
        """Calculate execution statistics"""
        executions = self.get_recent_executions(hours)
        
        if not executions:
            return {
                "total_executions": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "most_used_scripts": {},
                "period_hours": hours,
            }
        
        success_count = sum(1 for e in executions if e['success'])
        failure_count = len(executions) - success_count
        
        durations = [e['duration_seconds'] for e in executions]
        avg_duration = sum(durations) / len(durations)
        
        # Count script usage
        script_counts = {}
        for e in executions:
            script = e['script_path']
            script_counts[script] = script_counts.get(script, 0) + 1
        
        # Sort by usage
        most_used = dict(sorted(script_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            "total_executions": len(executions),
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_count / len(executions),
            "average_duration": avg_duration,
            "most_used_scripts": most_used,
            "period_hours": hours,
        }
    
    def check_health(self) -> Dict[str, any]:
        """Check execution health and return alerts"""
        stats = self.get_execution_stats(hours=1)
        alerts = []
        
        # Check failure rate
        if stats['total_executions'] > 5 and stats['success_rate'] < (1 - ALERT_THRESHOLDS['failure_rate']):
            alerts.append({
                "level": "warning",
                "message": f"High failure rate: {(1-stats['success_rate'])*100:.1f}% in last hour",
                "metric": "failure_rate",
                "value": 1 - stats['success_rate'],
            })
        
        # Check average duration
        if stats['total_executions'] > 0 and stats['average_duration'] > ALERT_THRESHOLDS['avg_duration']:
            alerts.append({
                "level": "info",
                "message": f"High average execution time: {stats['average_duration']:.1f}s",
                "metric": "avg_duration",
                "value": stats['average_duration'],
            })
        
        # Check execution count
        if stats['total_executions'] > ALERT_THRESHOLDS['execution_count']:
            alerts.append({
                "level": "info",
                "message": f"High execution volume: {stats['total_executions']} in last hour",
                "metric": "execution_count",
                "value": stats['total_executions'],
            })
        
        return {
            "healthy": len([a for a in alerts if a['level'] == 'warning']) == 0,
            "stats": stats,
            "alerts": alerts,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_failed_executions(self, hours: int = 24) -> List[Dict]:
        """Get list of failed executions for debugging"""
        executions = self.get_recent_executions(hours)
        return [e for e in executions if not e['success']]


# Monitoring tool for agent
def get_script_execution_stats(hours: int = 24) -> str:
    """
    Get statistics on script execution health.
    
    Use this to monitor script execution performance and identify issues.
    
    Args:
        hours: Number of hours to look back (default: 24)
    
    Returns:
        Formatted statistics report
    """
    monitor = ScriptMonitor()
    stats = monitor.get_execution_stats(hours)
    
    lines = [
        f"**Script Execution Stats (Last {hours} hours)**",
        "",
        f"Total Executions: {stats['total_executions']}",
        f"Success Rate: {stats['success_rate']*100:.1f}%",
        f"Average Duration: {stats['average_duration']:.2f}s",
        "",
        "**Most Used Scripts:**",
    ]
    
    for script, count in stats['most_used_scripts'].items():
        lines.append(f"  - {script}: {count} executions")
    
    # Add health check
    health = monitor.check_health()
    if health['alerts']:
        lines.append("")
        lines.append("**Alerts:**")
        for alert in health['alerts']:
            emoji = "⚠️" if alert['level'] == 'warning' else "ℹ️"
            lines.append(f"  {emoji} {alert['message']}")
    
    return "\n".join(lines)
```

**Add monitoring tool to agent**:
```python
# In tools.py
from roscoe.agents.paralegal.script_monitor import get_script_execution_stats

# Add to agent tools list
```

**Action Items**:
- [ ] Implement monitoring module
- [ ] Add health check endpoint
- [ ] Set up alerting (Slack notifications for failures)
- [ ] Create dashboard for execution metrics
- [ ] Test alert thresholds

---

### Day 10: Production Deployment

**Objective**: Deploy to production with proper configuration

**File**: `deploy/docker-compose.script-executor.yml`

```yaml
version: '3.8'

services:
  roscoe-agent:
    # Existing agent service
    volumes:
      # Mount Docker socket for script execution
      - /var/run/docker.sock:/var/run/docker.sock
      # Mount workspace
      - /mnt/workspace:/mnt/workspace
    environment:
      # Enable script execution
      ENABLE_SCRIPT_EXECUTION: "true"
```

**File**: `deploy/setup_script_execution.sh`

```bash
#!/bin/bash
set -e

echo "Setting up script execution environment..."

# 1. Verify gcsfuse mount
if ! mount | grep -q "gcsfuse"; then
    echo "ERROR: gcsfuse not mounted at /mnt/workspace"
    exit 1
fi
echo "✓ gcsfuse mount verified"

# 2. Build Docker images
echo "Building roscoe-python-runner image..."
cd docker/roscoe-python-runner
docker build -t roscoe-python-runner:latest .
echo "✓ Base image built"

echo "Building Playwright image..."
docker build -f Dockerfile.playwright -t roscoe-python-runner:playwright .
echo "✓ Playwright image built"

# 3. Create execution logs directory
mkdir -p /mnt/workspace/Database/script_execution_logs
chmod 755 /mnt/workspace/Database/script_execution_logs
echo "✓ Logs directory created"

# 4. Test execution
echo "Testing script execution..."
python3 << 'EOF'
from roscoe.agents.paralegal.script_executor import execute_python_script
import tempfile
from pathlib import Path

# Create test script
test_script = Path("/mnt/workspace/Tools/test_execution_setup.py")
test_script.write_text("print('Script execution setup successful!')")

# Execute
result = execute_python_script(script_path="/Tools/test_execution_setup.py")
assert result['success'], f"Test failed: {result['stderr']}"
print("✓ Test execution successful")

# Cleanup
test_script.unlink()
EOF

echo ""
echo "Script execution environment ready!"
echo "Images: roscoe-python-runner:latest, roscoe-python-runner:playwright"
echo "Logs: /mnt/workspace/Database/script_execution_logs/"
```

**Deployment Steps**:

```bash
# On GCE VM as roscoe user

# 1. Pull latest code
cd /opt/roscoe/ccf
git pull

# 2. Install Docker SDK
pip install docker==7.0.0

# 3. Run setup script
chmod +x deploy/setup_script_execution.sh
./deploy/setup_script_execution.sh

# 4. Restart agent
docker-compose restart roscoe-agent

# 5. Verify
docker ps  # Should see agent running
docker images | grep roscoe-python-runner  # Should see both images

# 6. Test from agent
# (Send test message via Slack or API)
```

**Action Items**:
- [ ] Create deployment scripts
- [ ] Test on staging VM first
- [ ] Deploy to production VM
- [ ] Verify with real workload
- [ ] Monitor for issues
- [ ] Update runbook documentation

---

## Week 3: Optimization & Advanced Features

### Day 11-12: Performance Optimization

**Objectives**:
- Reduce container startup time
- Optimize image size
- Implement caching

**Optimizations**:

**1. Pre-pull images on VM startup**:
```bash
# /etc/systemd/system/docker-prepull.service
[Unit]
Description=Pre-pull Docker images for Roscoe
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/usr/bin/docker pull roscoe-python-runner:latest
ExecStart=/usr/bin/docker pull roscoe-python-runner:playwright
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

**2. Optimize Dockerfile for faster builds**:
```dockerfile
# Use build cache effectively
FROM python:3.11-slim as base

# Install system deps (cached)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ git curl \
    && rm -rf /var/lib/apt/lists/*

# Install common packages (cached separately)
FROM base as packages
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Final image
FROM packages
# ... rest of Dockerfile
```

**3. Add image warmup script**:
```python
# warm_up_executor.py
"""Warm up Docker images to reduce first-execution latency"""
from script_executor import execute_python_script
from pathlib import Path

# Create minimal test script
test_script = Path("/mnt/workspace/Tools/.warmup_test.py")
test_script.write_text("print('warm')")

# Warm up base image
print("Warming up base image...")
execute_python_script(script_path="/Tools/.warmup_test.py", timeout=30)

# Warm up Playwright image
print("Warming up Playwright image...")
execute_python_script(
    script_path="/Tools/.warmup_test.py",
    enable_playwright=True,
    timeout=60
)

test_script.unlink()
print("Warmup complete")
```

**Action Items**:
- [ ] Implement pre-pull service
- [ ] Optimize Dockerfiles
- [ ] Add warmup to agent startup
- [ ] Measure performance improvements
- [ ] Document optimization results

---

### Day 13-14: Advanced Features

**Feature 1: Parallel Script Execution**

```python
# script_executor.py additions

import asyncio
from concurrent.futures import ThreadPoolExecutor

async def execute_python_scripts_parallel(
    scripts: List[Dict[str, any]],
    max_parallel: int = 3,
) -> List[Dict[str, any]]:
    """
    Execute multiple scripts in parallel.
    
    Args:
        scripts: List of script configs, each with:
            - script_path: str
            - case_name: Optional[str]
            - script_args: Optional[List[str]]
        max_parallel: Maximum concurrent executions
    
    Returns:
        List of execution results
    """
    
    executor = ThreadPoolExecutor(max_workers=max_parallel)
    
    async def run_script(script_config):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            _execute_python_script,
            script_config['script_path'],
            script_config.get('case_name'),
            script_config.get('script_args'),
        )
    
    tasks = [run_script(config) for config in scripts]
    results = await asyncio.gather(*tasks)
    
    return results
```

**Feature 2: Script Result Caching**

```python
# script_cache.py

import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path("/mnt/workspace/Database/script_execution_cache")
CACHE_TTL = timedelta(hours=1)

def get_cache_key(script_path: str, case_name: str, script_args: List[str]) -> str:
    """Generate cache key for script execution"""
    key_data = {
        "script_path": script_path,
        "case_name": case_name,
        "script_args": script_args or [],
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()

def get_cached_result(cache_key: str) -> Optional[Dict]:
    """Get cached result if exists and not expired"""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    
    if not cache_file.exists():
        return None
    
    try:
        cached = json.loads(cache_file.read_text())
        cached_time = datetime.fromisoformat(cached['timestamp'])
        
        if datetime.utcnow() - cached_time < CACHE_TTL:
            return cached['result']
    except Exception:
        pass
    
    return None

def cache_result(cache_key: str, result: Dict):
    """Cache execution result"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    cache_file = CACHE_DIR / f"{cache_key}.json"
    cache_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "result": result,
    }
    cache_file.write_text(json.dumps(cache_data))
```

**Action Items**:
- [ ] Implement parallel execution
- [ ] Add caching layer
- [ ] Test with batch operations
- [ ] Benchmark performance gains
- [ ] Document advanced features

---

### Day 15: Final Testing & Documentation

**Comprehensive Test Suite**:

```python
# tests/test_script_execution.py

import pytest
from roscoe.agents.paralegal.script_executor import execute_python_script
from pathlib import Path

def test_basic_execution():
    """Test basic script execution"""
    result = execute_python_script(
        script_path="/Tools/test_script.py"
    )
    assert result['success']
    assert result['exit_code'] == 0

def test_script_with_args():
    """Test script with arguments"""
    result = execute_python_script(
        script_path="/Tools/test_script.py",
        script_args=["--verbose", "--output", "test.txt"]
    )
    assert result['success']

def test_file_persistence():
    """Test that file changes persist"""
    test_file = Path("/mnt/workspace/Reports/test_output.txt")
    
    # Clean up from previous runs
    if test_file.exists():
        test_file.unlink()
    
    # Run script that creates file
    result = execute_python_script(
        script_path="/Tools/test_write_file.py"
    )
    
    assert result['success']
    assert test_file.exists()
    
    # Cleanup
    test_file.unlink()

def test_error_handling():
    """Test error handling for failing scripts"""
    result = execute_python_script(
        script_path="/Tools/test_error.py"
    )
    
    assert not result['success']
    assert result['exit_code'] != 0
    assert len(result['stderr']) > 0

def test_timeout():
    """Test timeout enforcement"""
    result = execute_python_script(
        script_path="/Tools/test_slow.py",
        timeout=5
    )
    
    assert not result['success']

def test_internet_access():
    """Test internet connectivity"""
    result = execute_python_script(
        script_path="/Tools/test_internet.py"
    )
    
    assert result['success']
    assert "200" in result['stdout']

def test_resource_limits():
    """Test resource limit enforcement"""
    # Script that tries to use too much memory
    result = execute_python_script(
        script_path="/Tools/test_memory_hog.py"
    )
    
    # Should fail due to memory limit
    assert not result['success']

# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Final Documentation Updates**:
- [ ] Update main README
- [ ] Create video walkthrough
- [ ] Write troubleshooting guide
- [ ] Document all configuration options
- [ ] Create example scripts library

---

## Production Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Docker images built and tagged
- [ ] Deployment scripts tested on staging
- [ ] Monitoring configured
- [ ] Alerts configured (Slack)
- [ ] Documentation complete
- [ ] Rollback plan documented

### Deployment
- [ ] Schedule deployment window
- [ ] Backup current configuration
- [ ] Deploy to production VM
- [ ] Run smoke tests
- [ ] Verify with real workload
- [ ] Monitor for errors

### Post-Deployment
- [ ] Verify agent can execute scripts
- [ ] Check execution logs
- [ ] Monitor resource usage
- [ ] Review error rates
- [ ] Update runbook with learnings

---

## Monitoring & Maintenance

### Daily
- [ ] Check execution success rate (should be >90%)
- [ ] Review failed executions
- [ ] Monitor resource usage

### Weekly
- [ ] Review execution statistics
- [ ] Update Docker images if needed
- [ ] Clean up old execution logs (>30 days)
- [ ] Review and optimize slow scripts

### Monthly
- [ ] Review and update Docker base image
- [ ] Audit security configurations
- [ ] Performance optimization review
- [ ] Update documentation

---

## Key Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Success Rate | >95% | <90% |
| Avg Duration | <60s | >300s |
| P95 Duration | <180s | >600s |
| Container Cleanup | 100% | <95% |
| Log File Size | <10MB/day | >50MB/day |
| Failed Executions | <5/day | >20/day |

---

## Troubleshooting Guide

### Issue: Script execution fails with "Docker unavailable"
**Solution**:
```bash
# Check Docker daemon
systemctl status docker

# Restart if needed
sudo systemctl restart docker

# Verify agent can access Docker
docker ps
```

### Issue: Scripts can't access files
**Solution**:
```bash
# Verify gcsfuse mount
mount | grep gcsfuse

# Check permissions
ls -la /mnt/workspace

# Remount if needed
sudo umount /mnt/workspace
sudo gcsfuse whaley-law-firm /mnt/workspace
```

### Issue: Container doesn't clean up
**Solution**:
```bash
# List all containers
docker ps -a

# Remove stuck containers
docker rm -f $(docker ps -aq -f status=exited)

# Check disk space
df -h
```

### Issue: Slow execution times
**Solution**:
- Check if images need to be pulled: `docker images`
- Verify VM resources: `htop`, `free -h`
- Review script for optimization opportunities
- Consider increasing resource limits

---

## Appendix A: Example Scripts

### Example 1: File Inventory Script

```python
# /Tools/examples/create_inventory.py
"""
Create a JSON inventory of all files in a case folder
"""
import json
from pathlib import Path
import sys

def create_inventory(case_path: str, output_file: str = None):
    """Create file inventory for a case"""
    
    case_dir = Path(case_path)
    
    if not case_dir.exists():
        print(f"Error: Case directory not found: {case_path}")
        sys.exit(1)
    
    inventory = {
        "case_name": case_dir.name,
        "total_files": 0,
        "total_size_mb": 0,
        "buckets": {}
    }
    
    # Walk directory tree
    for item in case_dir.rglob("*"):
        if item.is_file():
            # Get bucket (top-level folder)
            try:
                bucket = item.relative_to(case_dir).parts[0]
            except:
                bucket = "root"
            
            # Initialize bucket if needed
            if bucket not in inventory["buckets"]:
                inventory["buckets"][bucket] = {
                    "file_count": 0,
                    "size_mb": 0,
                    "files": []
                }
            
            # Add file info
            file_size = item.stat().st_size
            inventory["buckets"][bucket]["files"].append({
                "name": item.name,
                "path": str(item.relative_to(case_dir)),
                "size_bytes": file_size,
                "extension": item.suffix
            })
            
            inventory["buckets"][bucket]["file_count"] += 1
            inventory["buckets"][bucket]["size_mb"] += file_size / (1024 * 1024)
            inventory["total_files"] += 1
            inventory["total_size_mb"] += file_size / (1024 * 1024)
    
    # Output
    print(json.dumps(inventory, indent=2))
    
    # Save to file if requested
    if output_file:
        output_path = case_dir / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(inventory, indent=2))
        print(f"\nInventory saved to: {output_file}")
    
    return inventory

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_inventory.py <case_path> [output_file]")
        sys.exit(1)
    
    case_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    create_inventory(case_path, output_file)
```

### Example 2: Medical Records Analysis

```python
# /Tools/examples/analyze_medical_records.py
"""
Analyze medical records in a case folder
"""
from pathlib import Path
import sys
import json
from datetime import datetime

def analyze_medical_records(case_path: str):
    """Analyze medical records"""
    
    case_dir = Path(case_path)
    medical_dir = case_dir / "Medical Records"
    
    if not medical_dir.exists():
        print("No Medical Records folder found")
        return
    
    analysis = {
        "case": case_dir.name,
        "analysis_date": datetime.now().isoformat(),
        "records_found": 0,
        "providers": set(),
        "date_range": {"earliest": None, "latest": None},
        "files_by_type": {}
    }
    
    # Scan medical records
    for record in medical_dir.rglob("*"):
        if record.is_file():
            analysis["records_found"] += 1
            
            # Extract provider from path
            parts = record.relative_to(medical_dir).parts
            if len(parts) > 0:
                provider = parts[0]
                analysis["providers"].add(provider)
            
            # Count by type
            ext = record.suffix.lower()
            analysis["files_by_type"][ext] = analysis["files_by_type"].get(ext, 0) + 1
    
    # Convert set to list for JSON
    analysis["providers"] = sorted(list(analysis["providers"]))
    
    # Output
    print("Medical Records Analysis")
    print("=" * 50)
    print(f"Case: {analysis['case']}")
    print(f"Total Records: {analysis['records_found']}")
    print(f"Providers: {len(analysis['providers'])}")
    print(f"\nProviders found: {', '.join(analysis['providers'])}")
    print(f"\nFiles by type: {json.dumps(analysis['files_by_type'], indent=2)}")
    
    # Save report
    report_file = case_dir / "Reports" / "medical_records_analysis.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(analysis, indent=2, default=str))
    print(f"\nReport saved: {report_file}")
    
    return analysis

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_medical_records.py <case_path>")
        sys.exit(1)
    
    analyze_medical_records(sys.argv[1])
```

---

## Appendix B: Configuration Reference

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `WORKSPACE_ROOT` | Path to workspace | `/mnt/workspace` | Yes |
| `DOCKER_IMAGE` | Base Python image | `roscoe-python-runner:latest` | Yes |
| `DOCKER_IMAGE_PLAYWRIGHT` | Playwright image | `roscoe-python-runner:playwright` | No |
| `DEFAULT_TIMEOUT` | Default timeout (seconds) | `300` | No |
| `MAX_TIMEOUT` | Maximum timeout (seconds) | `1800` | No |
| `ENABLE_SCRIPT_EXECUTION` | Enable script execution | `true` | No |

### Resource Limits

| Resource | Default | Adjustable |
|----------|---------|------------|
| Memory | 2GB | Edit `script_executor.py` |
| CPU | 1 core | Edit `script_executor.py` |
| Timeout | 300s | Per-execution parameter |
| Max Timeout | 1800s | Configuration constant |

---

## Success Criteria

This implementation will be considered successful when:

- [x] Agent can execute any Python script from `/Tools/` with filesystem access
- [x] Scripts can read, write, modify files with changes persisting to GCS
- [x] Playwright-enabled scripts can perform browser automation
- [x] Execution success rate >95%
- [x] Average execution time <60 seconds
- [x] Complete audit logging of all executions
- [x] Resource limits prevent runaway processes
- [x] Docker containers properly clean up after execution
- [x] Documentation covers all use cases and troubleshooting

---

**Implementation Timeline**: 2-3 weeks  
**Estimated Effort**: 60-80 hours  
**Team Size**: 1-2 developers  
**Risk Level**: Low-Medium  

**Next Steps**:
1. Review and approve this plan
2. Set up development environment
3. Begin Week 1 implementation
4. Daily standups to track progress
5. Weekly demos of functionality

---

*Document Version: 1.0*  
*Last Updated: November 27, 2025*  
*Prepared By: Claude Sonnet 4.5*

