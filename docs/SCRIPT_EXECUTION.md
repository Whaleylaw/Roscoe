# Script Execution with GCS Filesystem Access

## Overview

The Roscoe paralegal agent can execute Python scripts from `/Tools/` with direct read-write access to the GCS-mounted filesystem. Scripts run in isolated Docker containers, ensuring:

- **Direct filesystem access**: Scripts can read, write, and modify files on GCS
- **Persistence**: All changes are automatically synced to GCS via gcsfuse
- **Isolation**: Each execution runs in a fresh container
- **Security**: Non-root execution with resource limits
- **Browser automation**: Optional Playwright support for web scraping

## Quick Start

### Execute a Script

```python
# Run a file inventory script
result = execute_python_script(
    script_path="/Tools/create_file_inventory.py",
    case_name="Wilson-MVA-2024"
)

# Run with arguments
result = execute_python_script(
    script_path="/Tools/document_processing/read_pdf.py",
    case_name="Wilson-MVA-2024",
    script_args=["Medical Records/report.pdf", "--output-format", "markdown"]
)

# Web scraping with Playwright
result = execute_python_script_with_browser(
    script_path="/Tools/web_scraping/courtlistener_search.py",
    script_args=["personal injury", "Kentucky"]
)
```

## When To Use

### Use `execute_python_script()` when:
- ✅ Running `/Tools/` scripts that need filesystem access
- ✅ Data processing that modifies actual files
- ✅ Complex workflows requiring file operations
- ✅ Batch operations on case folders

### Use `execute_python_script_with_browser()` when:
- ✅ Web scraping and data extraction
- ✅ Browser automation tasks
- ✅ Screenshot capture
- ✅ Court record lookups

### Use native FilesystemBackend when:
- ✅ Simple file read/write operations
- ✅ Directory listing
- ✅ File search
- ✅ Moving or deleting files

## Architecture

```
┌─────────────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Roscoe Agent          │     │   Docker Container   │     │   GCS via       │
│   (LangGraph)           │────▶│   (Short-lived)      │────▶│   gcsfuse       │
│                         │     │                      │     │                 │
│ execute_python_script() │     │ /workspace mounted   │     │ /mnt/workspace/ │
│                         │     │ as read-write        │     │                 │
└─────────────────────────┘     └──────────────────────┘     └─────────────────┘
```

### Execution Flow

1. Agent calls `execute_python_script(script_path="/Tools/analyze.py", case_name="Wilson")`
2. Docker container spins up with `/mnt/workspace` mounted as `/workspace`
3. Container working directory set to `/workspace/projects/Wilson`
4. Script executes with direct filesystem access
5. Container captures stdout/stderr and exits
6. Changes persist to GCS automatically
7. Agent receives formatted results

## API Reference

### execute_python_script()

```python
def execute_python_script(
    script_path: str,          # Path to script, e.g., "/Tools/analyze.py"
    case_name: str = None,     # Case folder for working directory
    script_args: list = None,  # Command-line arguments
    working_dir: str = None,   # Explicit working directory
    timeout: int = 300,        # Max execution time (seconds)
) -> str:
```

### execute_python_script_with_browser()

```python
def execute_python_script_with_browser(
    script_path: str,          # Path to Playwright script
    case_name: str = None,     # Case folder
    script_args: list = None,  # Arguments
    timeout: int = 600,        # Longer timeout for browser ops
) -> str:
```

## Docker Images

### Base Image (`roscoe-python-runner:latest`)

Pre-installed packages:
- pandas, numpy (data analysis)
- pdfplumber, PyPDF2 (PDF processing)
- python-docx, openpyxl (Office docs)
- requests, httpx, beautifulsoup4 (HTTP/HTML)
- tavily-python (search API)
- biopython (medical research)
- markdown, python-dateutil, jsonschema
- loguru (logging)

### Playwright Image (`roscoe-python-runner:playwright`)

Everything in base image, plus:
- Chromium browser
- Playwright library and dependencies
- Fonts for proper rendering

## Security

- **Non-root execution**: Scripts run as `roscoe` user
- **Resource limits**: 2GB RAM, 1 CPU core
- **Timeout enforcement**: Default 5 minutes, max 30 minutes
- **Container isolation**: Each execution in fresh container
- **Audit logging**: All executions logged to `/Database/script_execution_logs/`

## Environment Variables

Scripts have access to these API keys (if set in host environment):
- `TAVILY_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `NCBI_EMAIL`, `NCBI_API_KEY`
- `COURTLISTENER_API_KEY`
- `AIRTABLE_API_KEY`
- `ASSEMBLYAI_API_KEY`

Scripts also receive execution context:
- `EXECUTION_ID`: Unique execution identifier
- `CASE_NAME`: Case name if provided
- `SCRIPT_PATH`: Path to the executing script
- `WORKSPACE_ROOT`: Always `/workspace`

## Monitoring

### Execution Logs

Each execution creates a JSON log at:
```
/mnt/workspace/Database/script_execution_logs/{execution_id}.json
```

Log contents:
```json
{
  "execution_id": "exec_20251127_143022_a1b2c3d4",
  "success": true,
  "exit_code": 0,
  "stdout": "...",
  "stderr": "",
  "duration_seconds": 2.34,
  "script_path": "/Tools/analyze.py",
  "case_name": "Wilson-MVA-2024",
  "timestamp": "2025-11-27T14:30:22.123456",
  "working_dir": "/workspace/projects/Wilson-MVA-2024"
}
```

### Statistics

Get execution stats with:
```python
from roscoe.agents.paralegal.tools import get_script_execution_stats

stats = get_script_execution_stats(hours=24)
```

## Troubleshooting

### Script not found

```
ScriptExecutionError: Script not found: /Tools/my_script.py
```

**Solution**: Verify the script exists at `/mnt/workspace/Tools/my_script.py`

### Docker unavailable

```
ScriptExecutionError: Docker is not available
```

**Solution**: Ensure Docker daemon is running:
```bash
sudo systemctl status docker
sudo systemctl start docker
```

### Image not found

```
Docker image not found: roscoe-python-runner:latest
```

**Solution**: Build the images:
```bash
cd docker/roscoe-python-runner
./build.sh
```

### Permission denied

**Solution**: Check gcsfuse mount:
```bash
mount | grep gcsfuse
ls -la /mnt/workspace
```

### Timeout errors

**Solution**: Increase timeout or optimize script:
```python
execute_python_script(
    script_path="/Tools/slow_script.py",
    timeout=1800  # 30 minutes max
)
```

## Adding New Dependencies

To add Python packages:

1. Edit `docker/roscoe-python-runner/Dockerfile`
2. Add package to pip install section
3. Rebuild: `./build.sh`
4. Test: `docker run --rm roscoe-python-runner:latest python -c "import new_package"`

## Testing

Run the test suite:
```bash
# Direct execution (without Docker)
python /mnt/workspace/Tools/tests/run_all_tests.py --direct

# Via Docker executor
python /mnt/workspace/Tools/tests/run_all_tests.py

# Skip Playwright tests
python /mnt/workspace/Tools/tests/run_all_tests.py --skip-playwright
```

Individual tests:
- `test_basic.py` - Basic execution
- `test_dependencies.py` - Package availability
- `test_file_persistence.py` - GCS write persistence
- `test_arguments.py` - Argument passing
- `test_internet.py` - Network access
- `test_error_handling.py` - Error capture
- `test_playwright.py` - Browser automation (requires playwright image)

