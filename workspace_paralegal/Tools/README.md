# Tools Directory

## Overview

This directory contains Python scripts that can be executed via the `execute_python_script` tool. Scripts run in isolated Docker containers with direct access to the GCS-mounted filesystem at `/workspace`.

## How to Execute Tools

Use the `execute_python_script` function to run any tool:

```python
# Basic execution
execute_python_script(
    script_path="/Tools/create_file_inventory.py",
    script_args=["/workspace/projects/Case-Name-MVA-Date"]
)

# With case_name for automatic working directory
execute_python_script(
    script_path="/Tools/create_file_inventory.py",
    case_name="Case-Name-MVA-Date"
)

# For web scraping tasks (uses Playwright-enabled container)
execute_python_script_with_browser(
    script_path="/Tools/legal_research/search_case_law.py",
    script_args=["negligence standard of care", "--courts", "ky,kyctapp"]
)
```

## Path Conventions

**Inside Scripts (Container Environment):**
- Workspace root: `/workspace/`
- Projects: `/workspace/projects/{case_name}/`
- Tools: `/workspace/Tools/`
- Database: `/workspace/Database/`

**Script Arguments:**
- Always use `/workspace/...` paths when passing paths as arguments
- Example: `script_args=["/workspace/projects/Case-Name/Reports/file.md"]`

**FilesystemBackend (Agent Operations):**
- Use virtual paths: `/projects/...`, `/Tools/...`
- These are translated automatically

## Available Tools

### File Organization Tools

| Tool | Description |
|------|-------------|
| `create_file_inventory.py` | Create inventory of case files with scrambled naming |
| `file_reorganize.py` | Execute file reorganization from JSON plan |
| `split_inventory.py` | Split large inventories for parallel processing |
| `merge_reorg_chunks.py` | Merge partial reorganization maps |
| `count_plan_rows.py` | Count rows in reorganization plan |
| `get_error_rate.py` | Extract error rate from quality review |
| `line_count.py` | Count lines in a file |

### Document Processing

| Tool | Description |
|------|-------------|
| `document_processing/batch_import_all.py` | Batch import documents to a case |
| `document_processing/pdf_to_md.py` | Convert PDF to Markdown |
| `document_processing/extract_text.py` | Extract text from various formats |

### Legal Research

| Tool | Description |
|------|-------------|
| `legal_research/search_case_law.py` | Search CourtListener for case law |
| `legal_research/search_statutes.py` | Search for statutes and regulations |

### Reporting

| Tool | Description |
|------|-------------|
| `reporting/active_negotiations_report.py` | Generate active negotiations report |
| `reporting/case_summary.py` | Generate case summary report |

### Video/Audio Analysis

| Tool | Description |
|------|-------------|
| `analyze_videos.py` | Analyze video evidence |
| `analyze_video_script.py` | Generate video analysis script |

## Creating New Tools

### Basic Template

```python
#!/usr/bin/env python3
"""
Tool Name - Brief description

Usage:
    python tool_name.py <required_arg> [--optional-flag]

Arguments:
    required_arg: Description of the argument
    --optional-flag: What this flag does
"""

import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python tool_name.py <required_arg>")
        sys.exit(1)
    
    # Parse arguments
    arg = sys.argv[1]
    
    # Determine workspace root
    workspace = Path("/workspace")
    if not workspace.exists():
        workspace = Path("/mnt/workspace")
    
    # Your tool logic here
    print(f"Processing: {arg}")
    
    # Always print clear output
    print("✅ Complete!")

if __name__ == "__main__":
    main()
```

### Best Practices

1. **Use `/workspace` as root** - Scripts run in Docker containers where the GCS mount is at `/workspace`

2. **Handle both paths** - Fall back to `/mnt/workspace` for direct VM access:
   ```python
   workspace = Path("/workspace")
   if not workspace.exists():
       workspace = Path("/mnt/workspace")
   ```

3. **Clear output** - Print progress and results so the agent knows what happened

4. **Exit codes** - Use `sys.exit(1)` for errors, let success exit naturally

5. **JSON output** - For structured data, print JSON that can be parsed:
   ```python
   import json
   result = {"status": "success", "files_processed": 42}
   print(json.dumps(result, indent=2))
   ```

## Environment

Scripts run in Docker containers with:
- Python 3.11
- Common libraries: pandas, numpy, pdfplumber, PyPDF2, requests, beautifulsoup4, etc.
- Playwright (for browser-enabled scripts)
- Full read/write access to `/workspace` (GCS-mounted)

## Execution Logging

All script executions are logged to:
`/workspace/Database/script_execution_logs/exec_{timestamp}_{id}.json`

Logs include:
- Script path and arguments
- Exit code
- Duration
- stdout/stderr output
- Container details

## Troubleshooting

**Script not found:**
- Verify the path starts with `/Tools/`
- Check the file exists in the workspace

**Permission denied:**
- Scripts run as root in containers
- GCS filesystem should be accessible

**Import errors:**
- Check if the library is in the Docker image
- Request additions via the development team

**Timeout:**
- Default timeout is 300 seconds (5 minutes)
- For long-running scripts, pass `timeout=1800` (30 minutes max)
