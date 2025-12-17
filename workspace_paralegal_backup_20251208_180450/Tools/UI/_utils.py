"""
Shared utilities for UI scripts.

This module provides common functions used across all UI components:
- Path handling
- JSON file reading with database export format handling
- File URL generation
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote


def get_workspace_path() -> Path:
    """Get workspace path from environment or default."""
    return Path(os.environ.get("WORKSPACE_DIR", "/workspace"))


def get_project_path(project_name: str) -> Path:
    """Get the full path to a project folder."""
    return get_workspace_path() / "projects" / project_name


def read_json_file(file_path: Path) -> Any:
    """
    Read a JSON file, handling nested database export format.
    
    Handles the [{"jsonb_agg": [...]}] format from Supabase exports.
    
    Returns:
        Parsed JSON data, or None if file doesn't exist or can't be parsed
    """
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r') as f:
            raw = json.load(f)
        
        # Handle nested format: [{"jsonb_agg": [{...actual data...}]}]
        if isinstance(raw, list) and len(raw) > 0:
            first_item = raw[0]
            if isinstance(first_item, dict) and "jsonb_agg" in first_item:
                jsonb_data = first_item["jsonb_agg"]
                return jsonb_data if isinstance(jsonb_data, list) else [jsonb_data]
            return raw
        return raw
    except Exception as e:
        print(f"Warning: Failed to read {file_path}: {e}", file=sys.stderr)
        return None


def read_overview(project_path: Path) -> Dict[str, Any]:
    """
    Read overview.json and return the first item as a dict.
    """
    overview_raw = read_json_file(project_path / "Case Information" / "overview.json")
    if isinstance(overview_raw, list) and overview_raw:
        return overview_raw[0] if isinstance(overview_raw[0], dict) else {}
    return overview_raw if isinstance(overview_raw, dict) else {}


def get_client_name(overview_data: Dict[str, Any], project_name: str) -> str:
    """Extract client name from overview or derive from project name."""
    client_name = overview_data.get("client_name", "") if overview_data else ""
    if not client_name:
        parts = project_name.split("-")
        if len(parts) >= 2:
            client_name = f"{parts[0]} {parts[1]}"
    return client_name


def get_accident_date(overview_data: Dict[str, Any]) -> Optional[str]:
    """Extract accident date from overview data."""
    if not overview_data:
        return None
    return overview_data.get("date_of_loss") or overview_data.get("accident_date")


def generate_file_url(file_path: Path, workspace_path: Path, disposition: str = "inline") -> str:
    """Generate a local API URL for file access."""
    relative_path = file_path.relative_to(workspace_path)
    encoded_path = quote(str(relative_path), safe='')
    return f"/api/files?path={encoded_path}&disposition={disposition}"


def output_result(result: Dict[str, Any], success: bool = True) -> None:
    """Output result as JSON and exit with appropriate code."""
    result["success"] = success
    print(json.dumps(result))
    sys.exit(0 if success else 1)


def output_error(error_message: str) -> None:
    """Output an error and exit."""
    output_result({"error": error_message}, success=False)

