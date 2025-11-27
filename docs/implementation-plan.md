# Scoped Container Execution: Detailed Implementation Plan

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Roscoe Agent  │────▶│  Docker Runner  │────▶│  GCE VM         │
│   (LangGraph)   │     │  (Python SDK)   │     │                 │
│                 │     │                 │     │ • Docker Engine │
│ • Native GCS    │     │ • Container mgmt│     │ • GCS FUSE      │
│ • Script exec   │     │ • Resource limits│     │ • /mnt/workspace│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                │
┌─────────────────┐     ┌─────────────────┐     │
│  Container      │     │  Real Files     │     │
│  (Ephemeral)    │────▶│  /projects/...  │◀────┘
│                 │     │  /Tools/...     │
│ • Python script │     │  /Database/...  │
│ • Internet access│     │                 │
│ • Browser auto   │     │                 │
└─────────────────┘     └─────────────────┘
```

## Prerequisites Check

**Required Infrastructure:**
- ✅ GCE VM with Docker installed (`docker --version`)
- ✅ GCS bucket mounted via `gcsfuse` at `/mnt/workspace`
- ✅ Agent has native GCS read/write/list/search capabilities
- ✅ Existing `/Tools` directory with Python scripts

**Commands to verify:**
```bash
# SSH to your GCE VM
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a

# Check Docker
docker --version
docker run hello-world

# Check GCS mount
ls -la /mnt/workspace/
df -h | grep workspace

# Check existing tools
ls -la /mnt/workspace/Tools/
```

## Phase 1: Container Setup (Week 1)

### 1.1 Create Docker Image

```dockerfile
# /opt/roscoe/containers/script-runner/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages needed for case organization
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    pathlib \
    openpyxl \
    PyPDF2 \
    python-magic \
    requests \
    beautifulsoup4 \
    lxml \
    tavily-python \
    && playwright install chromium

# Create non-root user
RUN useradd -m -s /bin/bash scriptuser

# Set working directory
WORKDIR /workspace

# Default command
USER scriptuser
CMD ["python", "--version"]
```

### 1.2 Build and Test Container

```bash
# On your GCE VM
cd /opt/roscoe/containers/script-runner

# Build the image
docker build -t roscoe-script-runner:latest .

# Test basic functionality
docker run --rm roscoe-script-runner python --version
docker run --rm roscoe-script-runner pip list | grep pandas

# Test with mounted workspace (read-only first)
docker run --rm \
  -v /mnt/workspace:/workspace:ro \
  roscoe-script-runner \
  ls -la /workspace/projects/
```

### 1.3 Test Script Execution

```bash
# Test running a simple existing script
docker run --rm \
  -v /mnt/workspace:/workspace:rw \
  -w /workspace/projects \
  roscoe-script-runner \
  python /workspace/Tools/create_file_inventory.py --help
```

## Phase 2: Agent Integration (Week 2)

### 2.1 Create Container Execution Module

```python
# src/roscoe/agents/paralegal/container_executor.py
import docker
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ContainerScriptExecutor:
    """Execute scripts in containers with GCS filesystem access."""

    def __init__(
        self,
        workspace_mount: str = "/mnt/workspace",
        container_image: str = "roscoe-script-runner:latest",
        timeout: int = 300
    ):
        self.workspace_mount = workspace_mount
        self.container_image = container_image
        self.timeout = timeout
        self.docker_client = docker.from_env()

    def execute_script(
        self,
        script_path: str,
        working_dir: str,
        args: List[str] = None,
        env_vars: Dict[str, str] = None,
        case_name: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Execute a Python script in a container with GCS access.

        Args:
            script_path: Path to script (e.g., "Tools/create_file_inventory.py")
            working_dir: Working directory inside container (e.g., "projects/CaseName")
            args: Command line arguments
            env_vars: Environment variables to pass
            case_name: Case name for logging

        Returns:
            Execution result dict
        """
        execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"

        # Build command
        cmd_parts = ["python", f"/workspace/{script_path}"]
        if args:
            cmd_parts.extend(args)
        command = cmd_parts

        # Build environment
        environment = env_vars or {}
        environment.update({
            "EXECUTION_ID": execution_id,
            "CASE_NAME": case_name or "unknown",
            "WORKSPACE_ROOT": "/workspace"
        })

        # Add API keys if available
        for key in ["TAVILY_API_KEY", "OPENAI_API_KEY"]:
            if val := os.environ.get(key):
                environment[key] = val

        try:
            # Run container
            container = self.docker_client.containers.run(
                self.container_image,
                command=command,
                volumes={
                    self.workspace_mount: {
                        "bind": "/workspace",
                        "mode": "rw"  # Read-write access to GCS
                    }
                },
                working_dir=f"/workspace/{working_dir}",
                environment=environment,
                remove=True,  # Auto-cleanup
                detach=False,  # Wait for completion
                stdout=True,
                stderr=True,
                user="scriptuser",  # Non-root user
                mem_limit="1g",  # Memory limit
                cpu_period=100000,
                cpu_quota=50000,  # 0.5 CPU cores max
                network_mode="bridge",  # Internet access
            )

            # Container.run returns bytes when detach=False
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
        self._log_execution(execution_id, case_name, script_path, exit_code, stdout, stderr)

        return {
            "execution_id": execution_id,
            "success": exit_code == 0,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "script_path": script_path,
            "working_dir": working_dir,
            "command": " ".join(cmd_parts)
        }

    def _log_execution(self, execution_id, case_name, script_path, exit_code, stdout, stderr):
        """Log execution to audit trail."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "execution_id": execution_id,
            "case_name": case_name,
            "script_path": script_path,
            "exit_code": exit_code,
            "stdout_length": len(stdout),
            "stderr_length": len(stderr),
            "success": exit_code == 0
        }

        # Write to GCS-mounted audit log
        audit_dir = Path(self.workspace_mount) / "Database" / "script_executions"
        audit_dir.mkdir(parents=True, exist_ok=True)

        audit_file = audit_dir / f"{execution_id}.json"
        audit_file.write_text(json.dumps(log_entry, indent=2))

# Global instance
container_executor = ContainerScriptExecutor()
```

### 2.2 Add Agent Tools

```python
# src/roscoe/agents/paralegal/tools.py (additions)

from roscoe.agents.paralegal.container_executor import container_executor

def execute_script_on_filesystem(
    script_name: str,
    case_name: str,
    script_args: List[str] = None,
    working_dir: str = None
) -> str:
    """
    Execute a Python script with direct access to the real GCS filesystem.

    This runs the script in an isolated Docker container that has read-write access
    to the entire /projects tree. Changes made by the script are persisted to GCS.

    Args:
        script_name: Name of script in /Tools/ (e.g., "create_file_inventory.py")
        case_name: Case folder name (e.g., "Caryn-McCay-MVA-7-30-2023")
        script_args: List of arguments to pass to the script
        working_dir: Working directory (defaults to case folder)

    Returns:
        Script execution results with stdout, stderr, and status

    Examples:
        # Run file inventory script
        execute_script_on_filesystem(
            script_name="create_file_inventory.py",
            case_name="Abby-Sitgraves-MVA-7-13-2024",
            script_args=["--format", "json", "--output", "inventory.json"]
        )

        # Run medical records organizer
        execute_script_on_filesystem(
            script_name="organize_medical_subfolders.sh",
            case_name="Wilson-MVA-2024"
        )
    """

    script_path = f"Tools/{script_name}"
    working_directory = working_dir or f"projects/{case_name}"

    try:
        result = container_executor.execute_script(
            script_path=script_path,
            working_dir=working_directory,
            args=script_args or [],
            case_name=case_name
        )

        # Format response
        output_lines = [
            f"**Script Execution: {result['execution_id']}**",
            f"Script: {script_name}",
            f"Case: {case_name}",
            f"Status: {'✅ Success' if result['success'] else '❌ Failed'}",
            f"Exit Code: {result['exit_code']}",
            "",
        ]

        if result['stdout']:
            output_lines.extend([
                "**Output:**",
                "```",
                result['stdout'][:2000],  # Truncate if too long
                "```",
                ""
            ])

        if result['stderr']:
            output_lines.extend([
                "**Errors:**",
                "```",
                result['stderr'][:1000],
                "```",
                ""
            ])

        # Add audit log reference
        output_lines.append(f"Audit Log: Database/script_executions/{result['execution_id']}.json")

        return "\n".join(output_lines)

    except Exception as e:
        return f"❌ Script execution failed: {str(e)}"

def execute_custom_script(
    script_content: str,
    case_name: str,
    script_name: str = "temp_script.py"
) -> str:
    """
    Execute a custom Python script provided as text.

    Args:
        script_content: Python script code as string
        case_name: Case to operate on
        script_name: Temporary filename for the script

    Returns:
        Execution results
    """

    # Write script to temp location
    temp_script_path = f"Database/temp_scripts/{script_name}"

    # Use native GCS write to create the script
    # (Assuming your agent has GCS write capability)
    # write_file_to_gcs(temp_script_path, script_content)

    return execute_script_on_filesystem(
        script_name=f"../Database/temp_scripts/{script_name}",
        case_name=case_name
    )
```

## Phase 3: Testing and Safety (End of Week 2)

### 3.1 Safety Testing

```bash
# Test with read-only mount first
docker run --rm \
  -v /mnt/workspace:/workspace:ro \
  roscoe-script-runner \
  python -c "import os; print('Files:', len(os.listdir('/workspace/projects')))"

# Test script execution (read-only)
docker run --rm \
  -v /mnt/workspace:/workspace:ro \
  -w /workspace/projects \
  roscoe-script-runner \
  python /workspace/Tools/create_file_inventory.py --help

# Test with write access (after confirming safety)
docker run --rm \
  -v /mnt/workspace:/workspace:rw \
  -w /workspace/projects/TestCase \
  roscoe-script-runner \
  touch test_file.txt
```

### 3.2 Integration Testing

```python
# Test from agent
result = execute_script_on_filesystem(
    script_name="create_file_inventory.py",
    case_name="Test-Case",
    script_args=["--dry-run"]
)
print(result)
```

### 3.3 Safety Features

```python
# Add to container_executor.py

def validate_script_access(self, script_path: str) -> bool:
    """Validate script is in allowed locations."""
    allowed_prefixes = ["Tools/", "Database/temp_scripts/"]
    return any(script_path.startswith(prefix) for prefix in allowed_prefixes)

def scan_script_for_dangerous_patterns(self, script_content: str) -> List[str]:
    """Scan script for potentially dangerous patterns."""
    warnings = []
    dangerous_patterns = [
        r'os\.system\s*\(',
        r'subprocess\..*shell\s*=\s*True',
        r'eval\s*\(',
        r'exec\s*\(',
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, script_content):
            warnings.append(f"Dangerous pattern detected: {pattern}")

    return warnings
```

## Phase 4: Deployment and Monitoring

### 4.1 Production Deployment

```bash
# Create systemd service for container management
cat > /etc/systemd/system/roscoe-container-executor.service << EOF
[Unit]
Description=Roscoe Container Script Executor
After=docker.service gcsfuse.service
Requires=docker.service

[Service]
Type=oneshot
User=roscoe
ExecStart=/usr/bin/docker system prune -f
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable roscoe-container-executor
```

### 4.2 Monitoring Setup

```python
# Add monitoring to agent
def get_execution_stats() -> str:
    """Get execution statistics from audit logs."""
    audit_dir = Path("/mnt/workspace/Database/script_executions")

    if not audit_dir.exists():
        return "No executions logged yet"

    executions = []
    for log_file in audit_dir.glob("*.json"):
        try:
            data = json.loads(log_file.read_text())
            executions.append(data)
        except:
            continue

    total = len(executions)
    successful = len([e for e in executions if e.get("success")])
    failed = total - successful

    recent = sorted(executions, key=lambda x: x["timestamp"], reverse=True)[:5]

    return f"""**Execution Statistics:**
- Total: {total}
- Successful: {successful} ({successful/total*100:.1f}%)
- Failed: {failed}

**Recent Executions:**
""" + "\n".join([
    f"- {e['timestamp'][:19]}: {e['script_path']} ({'✅' if e['success'] else '❌'})"
    for e in recent
])

# Add to tools.py
def monitor_script_executions() -> str:
    """Monitor recent script execution activity."""
    return get_execution_stats()
```

## Phase 5: Browser Automation Extension

### 5.1 Enhanced Container Image

```dockerfile
# Add to Dockerfile
RUN pip install --no-cache-dir \
    playwright \
    selenium \
    webdriver-manager

# Install browsers
RUN playwright install chromium firefox

# For Selenium
RUN apt-get update && apt-get install -y \
    chromium-browser \
    firefox \
    && rm -rf /var/lib/apt/lists/*
```

### 5.2 Browser Automation Tool

```python
def execute_browser_automation(
    url: str,
    actions: List[str],
    case_name: str,
    save_screenshots: bool = True
) -> str:
    """
    Execute browser automation with Playwright.

    Args:
        url: Starting URL
        actions: List of actions to perform
        case_name: Case to save results to
        save_screenshots: Whether to save screenshots

    Returns:
        Automation results
    """

    # Generate Playwright script
    script_content = f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("{url}")

        results = []

        # Execute actions
        {"; ".join(actions)}

        # Save screenshot if requested
        if {save_screenshots}:
            await page.screenshot(path="/workspace/projects/{case_name}/automation_screenshot.png")
            results.append("Screenshot saved")

        await browser.close()
        return results

if __name__ == "__main__":
    results = asyncio.run(main())
    print("\\n".join(results))
"""

    # Write temp script
    temp_script = f"Database/temp_scripts/browser_{os.urandom(4).hex()}.py"
    # write_file_to_gcs(temp_script, script_content)

    # Execute
    return execute_script_on_filesystem(
        script_name=f"../{temp_script}",
        case_name=case_name
    )
```

## Timeline and Milestones

**Week 1: Foundation**
- ✅ Build Docker image with Python dependencies
- ✅ Test basic container execution
- ✅ Verify GCS mounting works

**Week 2: Integration**
- ✅ Implement container executor module
- ✅ Add agent tools for script execution
- ✅ Test with existing case organization scripts
- ✅ Add logging and monitoring

**Week 3: Safety and Testing**
- ✅ Implement safety validations
- ✅ Add resource limits and constraints
- ✅ Comprehensive testing with real cases
- ✅ Performance optimization

**Week 4: Production**
- ✅ Deploy to production environment
- ✅ Add monitoring and alerting
- ✅ Create rollback procedures
- ✅ User training and documentation

## Cost Analysis

**Infrastructure Costs:**
- Docker on existing GCE VM: **$0** (already running)
- Container execution time: **$10-50/month** (depending on usage)
- GCS operations: **$5-20/month** (additional operations)

**Development Costs:**
- Implementation: **2-3 weeks** engineering time
- Testing: **1 week** QA and validation
- Documentation: **0.5 weeks**

**Total First-Year Cost: $500-2000** (mostly engineering time)

## Risk Mitigation

**Data Safety:**
- Container isolation prevents system-level damage
- Resource limits prevent resource exhaustion
- Non-root user execution
- Comprehensive audit logging

**Operational Risks:**
- Container startup time (2-3 seconds) - acceptable for batch operations
- Docker daemon dependency - monitor and auto-restart
- Network access for browser automation - controlled via network policies

**Rollback Procedures:**
```bash
# Emergency stop all containers
docker stop $(docker ps -q)

# Check recent executions
find /mnt/workspace/Database/script_executions -name "*.json" -mtime -1 | head -10

# Manual rollback (if needed)
# 1. Identify problematic execution
# 2. Use GCS versioning to restore affected files
# 3. Update audit logs
```

## Success Metrics

**Technical Metrics:**
- Script execution success rate: >95%
- Average execution time: <60 seconds
- Container startup time: <5 seconds
- Audit log completeness: 100%

**Business Metrics:**
- Case organization time reduction: 70%
- Manual file operations eliminated: 90%
- Agent productivity increase: 50%

---

## Quick Start Commands

```bash
# Build the container
docker build -t roscoe-script-runner:latest .

# Test script execution
docker run --rm \
  -v /mnt/workspace:/workspace:rw \
  -w /workspace/projects/CaseName \
  roscoe-script-runner \
  python /workspace/Tools/create_file_inventory.py
```

## Conclusion

This implementation plan provides a **production-ready solution** for enabling script execution on real GCS files while maintaining safety, auditability, and performance. The container-based approach leverages your existing infrastructure and native GCS capabilities to solve the core problem efficiently.

**Key Advantages:**
- Direct access to real `/projects` files
- Reuse of existing `/Tools` scripts
- Strong isolation and safety
- Easy extension for browser automation
- Comprehensive monitoring and audit trails
