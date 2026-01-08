"""
Script Executor - Run Python scripts with GCS filesystem access

This module provides script execution for the Roscoe paralegal agent.
Scripts can run in isolated Docker containers (preferred) or natively via
subprocess when Docker is unavailable.

Key features:
- Direct GCS filesystem access (read-write)
- Docker execution with resource limits (when available)
- Native subprocess fallback (when Docker unavailable)
- Comprehensive audit logging
- Optional Playwright browser support (Docker only)
"""

import os
import sys
import uuid
import json
import shlex
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# Try to import docker, but don't fail if unavailable
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    docker = None
    DOCKER_AVAILABLE = False
    logger.info("Docker SDK not installed, will use native execution")

# Configuration - can be overridden via environment variables
# WORKSPACE_ROOT: GCS Fuse mount (for binary files, persistent storage)
# LOCAL_WORKSPACE: Fast local disk (for text files)
WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", "/mnt/workspace"))
LOCAL_WORKSPACE = Path(os.environ.get("LOCAL_WORKSPACE", "/home/aaronwhaley/workspace_local"))
DOCKER_IMAGE = os.environ.get("DOCKER_IMAGE", "roscoe-python-runner:latest")
DOCKER_IMAGE_PLAYWRIGHT = os.environ.get("DOCKER_IMAGE_PLAYWRIGHT", "roscoe-python-runner:playwright")
EXECUTION_LOGS_DIR = WORKSPACE_ROOT / "Database" / "script_execution_logs"

# Execution mode: "docker", "native", or "auto" (try docker, fallback to native)
EXECUTION_MODE = os.environ.get("SCRIPT_EXECUTION_MODE", "auto")

# Timeouts
DEFAULT_TIMEOUT = int(os.environ.get("DEFAULT_TIMEOUT", "300"))  # 5 minutes
MAX_TIMEOUT = int(os.environ.get("MAX_TIMEOUT", "1800"))  # 30 minutes

# Resource limits (Docker only)
MEMORY_LIMIT = os.environ.get("MEMORY_LIMIT", "2g")  # 2GB
CPU_PERIOD = 100000
CPU_QUOTA = 100000  # 1 CPU core

# Initialize Docker client
docker_client: Optional["docker.DockerClient"] = None


def _init_docker_client() -> Optional["docker.DockerClient"]:
    """Initialize Docker client with error handling."""
    global docker_client
    
    if not DOCKER_AVAILABLE:
        return None
    
    if docker_client is not None:
        return docker_client
    
    try:
        docker_client = docker.from_env()
        # Test connection
        docker_client.ping()
        logger.info("Docker client initialized successfully")
        return docker_client
    except docker.errors.DockerException as e:
        logger.warning(f"Failed to connect to Docker daemon: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error initializing Docker client: {e}")
        return None


def _check_docker_image_exists(image: str) -> bool:
    """Check if a Docker image exists locally."""
    client = _init_docker_client()
    if not client:
        return False
    
    try:
        client.images.get(image)
        return True
    except Exception:
        return False


class ScriptExecutionError(Exception):
    """Raised when script execution fails."""
    pass


def _execute_native(
    script_path: str,
    case_name: Optional[str] = None,
    script_args: Optional[List[str]] = None,
    working_dir: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Execute a Python script natively using subprocess.
    
    This is the fallback execution method when Docker is unavailable.
    Scripts run directly on the host with the current Python interpreter.
    """
    execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    start_time = datetime.utcnow()
    
    # Normalize script path
    if script_path.startswith('/'):
        script_path_clean = script_path[1:]
    else:
        script_path_clean = script_path
    
    # Verify script exists
    script_full_path = WORKSPACE_ROOT / script_path_clean
    if not script_full_path.exists():
        raise ScriptExecutionError(f"Script not found: {script_path} (checked: {script_full_path})")
    
    # Determine working directory
    if working_dir:
        cwd = Path(working_dir.replace("/workspace", str(WORKSPACE_ROOT)))
    elif case_name:
        cwd = WORKSPACE_ROOT / "projects" / case_name
    else:
        cwd = WORKSPACE_ROOT
    
    # Ensure working directory exists
    if not cwd.exists():
        cwd = WORKSPACE_ROOT
    
    # Build environment
    environment = os.environ.copy()
    if env_vars:
        environment.update(env_vars)
    
    # Add execution context
    environment.update({
        "EXECUTION_ID": execution_id,
        "CASE_NAME": case_name or "",
        "SCRIPT_PATH": script_path,
        "WORKSPACE_ROOT": str(WORKSPACE_ROOT),
        "WORKSPACE_DIR": str(WORKSPACE_ROOT),  # Alternative name used by some scripts
        "LOCAL_WORKSPACE": str(LOCAL_WORKSPACE),  # Fast local disk for text files
    })
    
    # Build command
    cmd = [sys.executable, str(script_full_path)]
    if script_args:
        cmd.extend(script_args)
    
    logger.info(f"Starting native script execution {execution_id}")
    logger.info(f"  Script: {script_path}")
    logger.info(f"  Case: {case_name or 'N/A'}")
    logger.info(f"  Working dir: {cwd}")
    logger.info(f"  Command: {' '.join(cmd)}")
    
    stdout = ""
    stderr = ""
    exit_code = 0
    success = True
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=environment,
            cwd=str(cwd),
        )
        
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
        success = (exit_code == 0)
        
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode('utf-8', errors='replace') if e.stdout else ""
        stderr = f"Script timed out after {timeout} seconds"
        exit_code = 124  # Standard timeout exit code
        success = False
        logger.warning(f"Script timed out: {script_path}")
        
    except Exception as e:
        stdout = ""
        stderr = f"Native execution error: {str(e)}"
        exit_code = 1
        success = False
        logger.error(f"Native script execution error: {e}")
    
    # Calculate duration
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    return {
        "execution_id": execution_id,
        "success": success,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "duration_seconds": duration,
        "script_path": script_path,
        "case_name": case_name,
        "timestamp": start_time.isoformat(),
        "log_file": None,
        "execution_mode": "native",
    }


def execute_python_script(
    script_path: str,
    case_name: Optional[str] = None,
    script_args: Optional[List[str]] = None,
    working_dir: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    enable_playwright: bool = False,
    enable_internet: bool = True,
) -> Dict[str, Any]:
    """
    Execute a Python script with direct filesystem access.
    
    Scripts can run in isolated Docker containers (preferred) or natively via
    subprocess when Docker is unavailable. The execution mode is determined by:
    1. SCRIPT_EXECUTION_MODE env var: "docker", "native", or "auto" (default)
    2. Docker/image availability when mode is "auto"
    
    Args:
        script_path: Path to Python script relative to workspace root.
                    Example: "/Tools/create_file_inventory.py" or "Tools/analyze.py"
        case_name: Optional case folder name to use as working directory.
                  Example: "Wilson-MVA-2024" -> working dir becomes /workspace/projects/Wilson-MVA-2024
        script_args: Optional list of command-line arguments for the script.
                    Example: ["--format", "json", "--output", "Reports/result.json"]
        working_dir: Optional explicit working directory (overrides case_name).
                    Example: "/workspace/projects/Wilson-MVA-2024"
        env_vars: Optional environment variables to pass to the script.
                 Example: {"DEBUG": "true", "CASE_ID": "12345"}
        timeout: Maximum execution time in seconds (default: 300, max: 1800).
        enable_playwright: Use Playwright-enabled image with Chromium (default: False).
                          Note: Playwright requires Docker; native mode will warn if requested.
        enable_internet: Allow network access for API calls (default: True).
    
    Returns:
        Dict with execution results:
        {
            "execution_id": str,      # Unique execution identifier
            "success": bool,          # True if exit code == 0
            "exit_code": int,         # Process exit code
            "stdout": str,            # Standard output
            "stderr": str,            # Standard error
            "duration_seconds": float, # Execution time
            "script_path": str,       # Original script path
            "case_name": str | None,  # Case name if provided
            "timestamp": str,         # ISO format timestamp
            "log_file": str | None,   # Path to execution log file
            "execution_mode": str,    # "docker" or "native"
        }
    
    Raises:
        ScriptExecutionError: If execution fails critically and no fallback available.
    
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
            script_args=["--output", "Reports/analysis.md", "--verbose"]
        )
        
        # Browser automation script (requires Docker)
        result = execute_python_script(
            script_path="/Tools/web_scraping/courtlistener_search.py",
            script_args=["personal injury", "Kentucky"],
            enable_playwright=True,
            timeout=600
        )
    """
    # Determine execution mode
    mode = EXECUTION_MODE.lower()
    
    # Select Docker image
    image = DOCKER_IMAGE_PLAYWRIGHT if enable_playwright else DOCKER_IMAGE
    
    # Check if we should/can use Docker
    use_docker = False
    if mode == "docker":
        use_docker = True
    elif mode == "native":
        use_docker = False
    else:  # "auto" mode
        client = _init_docker_client()
        if client is not None and _check_docker_image_exists(image):
            use_docker = True
        else:
            logger.info(f"Docker/image unavailable, using native execution for: {script_path}")
            if enable_playwright:
                logger.warning("Playwright requested but Docker unavailable - browser automation may not work")
    
    # Use native execution if Docker not available/configured
    if not use_docker:
        result = _execute_native(
            script_path=script_path,
            case_name=case_name,
            script_args=script_args,
            working_dir=working_dir,
            env_vars=env_vars,
            timeout=timeout,
        )
        # Log the execution
        _log_execution(result, image, enable_playwright, enable_internet)
        return result
    
    # Docker execution path
    client = _init_docker_client()
    if client is None:
        raise ScriptExecutionError(
            "Docker is not available. Set SCRIPT_EXECUTION_MODE=native or ensure Docker daemon is running."
        )
    
    # Validate timeout
    if timeout > MAX_TIMEOUT:
        logger.warning(f"Timeout {timeout}s exceeds maximum {MAX_TIMEOUT}s, capping")
        timeout = MAX_TIMEOUT
    
    # Generate execution ID
    execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    start_time = datetime.utcnow()
    
    # Normalize script path (remove leading slash if present)
    if script_path.startswith('/'):
        script_path_clean = script_path[1:]
    else:
        script_path_clean = script_path
    
    # Verify script exists
    script_full_path = WORKSPACE_ROOT / script_path_clean
    if not script_full_path.exists():
        raise ScriptExecutionError(f"Script not found: {script_path} (checked: {script_full_path})")
    
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
            "mode": "rw"  # Read-write access to GCS filesystem
        }
    }
    
    # Build environment variables
    environment = env_vars.copy() if env_vars else {}
    
    # Pass through API keys from host environment
    api_keys_to_pass = [
        "TAVILY_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "NCBI_EMAIL",
        "NCBI_API_KEY",
        "COURTLISTENER_API_KEY",
        "AIRTABLE_API_KEY",
        "ASSEMBLYAI_API_KEY",
        # KYeCourts credentials for browser automation
        "KYECOURTS_USERNAME",
        "KYECOURTS_PASSWORD",
    ]
    
    for key in api_keys_to_pass:
        if val := os.environ.get(key):
            environment[key] = val
    
    # Add execution context
    environment.update({
        "EXECUTION_ID": execution_id,
        "CASE_NAME": case_name or "",
        "SCRIPT_PATH": script_path,
        "WORKSPACE_ROOT": "/workspace",
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
    logger.info(f"  Playwright: {enable_playwright}")
    
    stdout = ""
    stderr = ""
    exit_code = 0
    success = True
    
    try:
        # Run container and capture combined output
        # Note: demux=True is not supported in containers.run(), stdout/stderr are combined
        output = client.containers.run(
            image,
            command=["bash", "-c", command],
            volumes=volumes,
            working_dir=container_workdir,
            environment=environment,
            remove=True,  # Auto-remove after exit
            detach=False,  # Wait for completion
            stdout=True,
            stderr=True,
            user="root",  # Run as root for GCS filesystem write access
            network_mode="bridge" if enable_internet else "none",
            mem_limit=MEMORY_LIMIT,
            cpu_period=CPU_PERIOD,
            cpu_quota=CPU_QUOTA,
            read_only=False,  # Allow writes to mounted workspace
        )
        
        # Output is bytes containing combined stdout/stderr
        if isinstance(output, bytes):
            stdout = output.decode('utf-8', errors='replace')
        else:
            stdout = str(output) if output else ""
        stderr = ""  # Combined with stdout when using containers.run()
        exit_code = 0
        success = True
        
    except docker.errors.ContainerError as e:
        # Container ran but exited with non-zero code
        try:
            stdout = e.container.logs(stdout=True, stderr=False).decode('utf-8', errors='replace')
            stderr = e.container.logs(stdout=False, stderr=True).decode('utf-8', errors='replace')
        except Exception:
            stdout = ""
            stderr = str(e)
        exit_code = e.exit_status
        success = False
        logger.warning(f"Script exited with code {exit_code}: {stderr[:200]}")
        
    except docker.errors.ImageNotFound as e:
        stdout = ""
        stderr = f"Docker image not found: {image}. Run build.sh to create images."
        exit_code = 1
        success = False
        logger.error(f"Image not found: {e}")
        
    except docker.errors.APIError as e:
        stdout = ""
        stderr = f"Docker API error: {str(e)}"
        exit_code = 1
        success = False
        logger.error(f"Docker API error: {e}")
        
    except Exception as e:
        stdout = ""
        stderr = f"Execution error: {str(e)}"
        exit_code = 1
        success = False
        logger.error(f"Script execution error: {e}")
    
    # Calculate duration
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    # Build result
    result: Dict[str, Any] = {
        "execution_id": execution_id,
        "success": success,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "duration_seconds": duration,
        "script_path": script_path,
        "case_name": case_name,
        "timestamp": start_time.isoformat(),
        "log_file": None,
        "execution_mode": "docker",
    }
    
    # Log execution
    _log_execution(result, image, enable_playwright, enable_internet, container_workdir, script_args, timeout)
    
    logger.info(f"Script execution {execution_id} completed: success={success}, duration={duration:.2f}s")
    
    return result


def _log_execution(
    result: Dict[str, Any],
    image: str = "",
    enable_playwright: bool = False,
    enable_internet: bool = True,
    working_dir: str = "",
    script_args: Optional[List[str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> None:
    """Log execution details to file."""
    try:
        EXECUTION_LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = EXECUTION_LOGS_DIR / f"{result['execution_id']}.json"
        
        log_entry = {
            **result,
            "working_dir": working_dir,
            "script_args": script_args,
            "timeout": timeout,
            "image": image,
            "enable_playwright": enable_playwright,
            "enable_internet": enable_internet,
        }
        
        log_file.write_text(json.dumps(log_entry, indent=2, default=str))
        result["log_file"] = str(log_file)
        
    except Exception as e:
        logger.error(f"Failed to write execution log: {e}")


def format_execution_result(result: Dict[str, Any], max_output_length: int = 4000) -> str:
    """
    Format execution result for display to agent/user.
    
    Args:
        result: Dict returned from execute_python_script
        max_output_length: Maximum length for stdout/stderr (truncates if exceeded)
    
    Returns:
        Formatted string with execution details
    """
    
    status_emoji = "✅" if result['success'] else "❌"
    execution_mode = result.get('execution_mode', 'unknown')
    mode_indicator = "🐳" if execution_mode == "docker" else "🐍"
    
    lines = [
        f"**Script Execution: {result['execution_id']}**",
        f"Script: `{result['script_path']}`",
        f"Status: {status_emoji} {'Success' if result['success'] else 'Failed'}",
        f"Mode: {mode_indicator} {execution_mode}",
        f"Exit Code: {result['exit_code']}",
        f"Duration: {result['duration_seconds']:.2f}s",
    ]
    
    if result.get('case_name'):
        lines.append(f"Case: {result['case_name']}")
    
    # Add stdout
    if result['stdout']:
        stdout_display = result['stdout'].strip()
        if len(stdout_display) > max_output_length:
            stdout_display = stdout_display[:max_output_length] + "\n... (truncated)"
        lines.append("")
        lines.append("**Output:**")
        lines.append("```")
        lines.append(stdout_display)
        lines.append("```")
    
    # Add stderr
    if result['stderr']:
        stderr_display = result['stderr'].strip()
        if len(stderr_display) > max_output_length // 2:
            stderr_display = stderr_display[:max_output_length // 2] + "\n... (truncated)"
        lines.append("")
        lines.append("**Errors:**")
        lines.append("```")
        lines.append(stderr_display)
        lines.append("```")
    
    # Add log file reference
    if result.get('log_file'):
        lines.append("")
        lines.append(f"Log: `{result['log_file']}`")
    
    return "\n".join(lines)


def get_execution_stats(hours: int = 24) -> Dict[str, Any]:
    """
    Get execution statistics from recent logs.
    
    Args:
        hours: Number of hours to look back
    
    Returns:
        Dict with execution statistics
    """
    from datetime import timedelta
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    recent_logs = []
    
    if not EXECUTION_LOGS_DIR.exists():
        return {
            "total_executions": 0,
            "success_count": 0,
            "failure_count": 0,
            "success_rate": 0.0,
            "average_duration": 0.0,
            "most_used_scripts": {},
            "period_hours": hours,
        }
    
    for log_file in EXECUTION_LOGS_DIR.glob("exec_*.json"):
        try:
            log_data = json.loads(log_file.read_text())
            log_time = datetime.fromisoformat(log_data['timestamp'])
            
            if log_time > cutoff_time:
                recent_logs.append(log_data)
        except Exception as e:
            logger.error(f"Failed to read log {log_file}: {e}")
    
    if not recent_logs:
        return {
            "total_executions": 0,
            "success_count": 0,
            "failure_count": 0,
            "success_rate": 0.0,
            "average_duration": 0.0,
            "most_used_scripts": {},
            "period_hours": hours,
        }
    
    success_count = sum(1 for e in recent_logs if e['success'])
    failure_count = len(recent_logs) - success_count
    
    durations = [e['duration_seconds'] for e in recent_logs]
    avg_duration = sum(durations) / len(durations)
    
    # Count script usage
    script_counts: Dict[str, int] = {}
    for e in recent_logs:
        script = e['script_path']
        script_counts[script] = script_counts.get(script, 0) + 1
    
    # Sort by usage
    most_used = dict(sorted(script_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    return {
        "total_executions": len(recent_logs),
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate": success_count / len(recent_logs),
        "average_duration": avg_duration,
        "most_used_scripts": most_used,
        "period_hours": hours,
    }


def check_docker_available() -> bool:
    """Check if Docker daemon is available and accessible."""
    client = _init_docker_client()
    return client is not None


def get_execution_mode_info() -> Dict[str, Any]:
    """
    Get information about the current execution mode and capabilities.
    
    Returns:
        Dict with execution mode details
    """
    client = _init_docker_client()
    docker_available = client is not None
    
    base_image_available = _check_docker_image_exists(DOCKER_IMAGE) if docker_available else False
    playwright_image_available = _check_docker_image_exists(DOCKER_IMAGE_PLAYWRIGHT) if docker_available else False
    
    # Determine effective mode
    mode = EXECUTION_MODE.lower()
    if mode == "auto":
        effective_mode = "docker" if (docker_available and base_image_available) else "native"
    else:
        effective_mode = mode
    
    return {
        "configured_mode": EXECUTION_MODE,
        "effective_mode": effective_mode,
        "docker_sdk_installed": DOCKER_AVAILABLE,
        "docker_daemon_available": docker_available,
        "base_image_available": base_image_available,
        "playwright_image_available": playwright_image_available,
        "base_image": DOCKER_IMAGE,
        "playwright_image": DOCKER_IMAGE_PLAYWRIGHT,
        "workspace_root": str(WORKSPACE_ROOT),
        "native_python": sys.executable,
    }

