#!/usr/bin/env python3
"""
Path Parser for Document Generation

Extracts project name, context type, and context name from file paths.
The path structure provides all the information needed to know:
- Which case/project the document belongs to
- What type of entity it relates to (insurance, medical provider, etc.)
- Which specific entity (State Farm, UK Hospital, etc.)

Usage:
    from path_parser import parse_path_context
    
    context = parse_path_context("/John-Doe-MVA-01-01-2025/Insurance/State Farm/LOR.docx")
    # Returns: {
    #     "project": "John-Doe-MVA-01-01-2025",
    #     "context_type": "insurance",
    #     "context_name": "State Farm",
    #     "filename": "LOR.docx",
    #     "case_info_path": "/path/to/Case Information/"
    # }
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional, Any


# Base path for cases - can be overridden
CLAUDE_DOCS = Path(os.environ.get("CLAUDE_DOCS", os.environ.get("ROSCOE_ROOT", str(Path(__file__).resolve().parents[2]))))

# Path keywords that indicate context type
PATH_KEYWORDS = {
    "Insurance": "insurance",
    "Medical Providers": "medical_provider",
    "Medical Records": "medical_provider",
    "Litigation": "litigation",
    "Liens": "lien",
    "Documents/Demand": "demand",
    "Demand": "demand",
    "Discovery": "discovery",
    "Client": "client",
    "Correspondence": "correspondence",
}

# Project name pattern: Name-Name-CaseType-MM-DD-YYYY
PROJECT_PATTERN = re.compile(
    r'^[A-Za-z]+-[A-Za-z]+-(?:MVA|SF|S&F|WC)-\d{1,2}-\d{1,2}-\d{4}$'
)


def parse_path_context(file_path: str) -> Dict[str, Any]:
    """
    Extract context information from a file path.
    
    The path structure tells us:
    - Project name (case folder name)
    - Context type (Insurance, Medical Providers, Litigation, etc.)
    - Context name (specific entity like "State Farm" or "UK Hospital")
    
    Args:
        file_path: Full path to the document
                   e.g., "/John-Doe-MVA-01-01-2025/Insurance/State Farm/LOR.docx"
    
    Returns:
        Dict with:
            - project: str - The project/case name
            - context_type: str - Type of context (insurance, medical_provider, etc.)
            - context_name: str|None - Specific entity name if applicable
            - filename: str - The document filename
            - case_info_path: Path - Path to Case Information folder
            - relative_path: str - Path relative to project folder
    """
    path = Path(file_path).resolve()
    parts = path.parts
    
    result = {
        "project": None,
        "context_type": None,
        "context_name": None,
        "filename": path.name,
        "case_info_path": None,
        "relative_path": None,
        "full_path": str(path),
    }
    
    # Find project folder by looking for pattern match
    project_index = None
    for i, part in enumerate(parts):
        if PROJECT_PATTERN.match(part):
            result["project"] = part
            project_index = i
            break
    
    # If no pattern match, look for known project folders
    if project_index is None:
        # Check if path is under claude_docs and find first meaningful folder
        for i, part in enumerate(parts):
            # Skip root/system folders
            if part in ('/', 'Users', 'aaronwhaley', 'claude_docs', 'Roscoe_active'):
                continue
            # Check if this folder has a Case Information subfolder
            potential_project = Path(*parts[:i+1])
            if (potential_project / "Case Information").exists():
                result["project"] = part
                project_index = i
                break
    
    if project_index is None:
        # Last resort: try to find any folder that looks like a case
        for i, part in enumerate(parts):
            if '-' in part and any(ct in part.upper() for ct in ['MVA', 'SF', 'WC']):
                result["project"] = part
                project_index = i
                break
    
    if result["project"] and project_index is not None:
        # Build path to Case Information
        project_path = Path(*parts[:project_index + 1])
        result["case_info_path"] = project_path / "Case Information"
        
        # Get relative path within project
        if project_index + 1 < len(parts):
            result["relative_path"] = str(Path(*parts[project_index + 1:]))
        
        # Determine context type from path
        remaining_parts = parts[project_index + 1:-1]  # Exclude filename
        
        for keyword, context_type in PATH_KEYWORDS.items():
            keyword_parts = keyword.split('/')
            # Check if keyword appears in path
            for i in range(len(remaining_parts) - len(keyword_parts) + 1):
                if remaining_parts[i:i+len(keyword_parts)] == tuple(keyword_parts):
                    result["context_type"] = context_type
                    
                    # Context name is typically the folder after the keyword
                    context_name_index = i + len(keyword_parts)
                    if context_name_index < len(remaining_parts):
                        result["context_name"] = remaining_parts[context_name_index]
                    break
            
            if result["context_type"]:
                break
        
        # Special handling for single-word keywords
        if not result["context_type"]:
            for part in remaining_parts:
                if part in PATH_KEYWORDS:
                    result["context_type"] = PATH_KEYWORDS[part]
                    # Get the next folder as context name
                    part_index = remaining_parts.index(part)
                    if part_index + 1 < len(remaining_parts):
                        result["context_name"] = remaining_parts[part_index + 1]
                    break
    
    return result


def get_case_json_path(context: Dict[str, Any], json_name: str) -> Optional[Path]:
    """
    Get the path to a specific JSON file in Case Information.
    
    Args:
        context: Result from parse_path_context
        json_name: Name of JSON file (e.g., "insurance.json", "overview.json")
    
    Returns:
        Path to JSON file or None if not available
    """
    if not context.get("case_info_path"):
        return None
    
    json_path = Path(context["case_info_path"]) / json_name
    if json_path.exists():
        return json_path
    return None


def find_project_folder(project_name: str) -> Optional[Path]:
    """
    Find the folder for a given project name.
    
    Searches common locations:
    - /claude_docs/{project_name}
    - /claude_docs/Roscoe_active/{project_name}
    
    Args:
        project_name: The project/case name
    
    Returns:
        Path to project folder or None if not found
    """
    search_paths = [
        CLAUDE_DOCS / project_name,
        CLAUDE_DOCS / "Roscoe_active" / project_name,
        CLAUDE_DOCS / "projects" / project_name,
    ]
    
    for path in search_paths:
        if path.exists() and path.is_dir():
            return path
    
    return None


def get_context_entity_id(
    context: Dict[str, Any],
    json_data: Any,
    name_field: str = "insurance_company_name"
) -> Optional[int]:
    """
    Find the entity ID that matches the context_name.
    
    Args:
        context: Result from parse_path_context
        json_data: Loaded JSON data (dict or list)
        name_field: The field to match against context_name
    
    Returns:
        Entity ID or None if not found
    """
    context_name = context.get("context_name")
    if not context_name:
        return None
    
    context_name_lower = context_name.lower().strip()
    
    def search_for_match(data, depth=0):
        if depth > 3:  # Prevent infinite recursion
            return None
            
        if isinstance(data, dict):
            # Check if this dict has the name field
            name_value = data.get(name_field, "")
            if isinstance(name_value, str) and context_name_lower in name_value.lower():
                return data.get("id")
            
            # Search nested dicts
            for key, value in data.items():
                result = search_for_match(value, depth + 1)
                if result is not None:
                    return result
                    
        elif isinstance(data, list):
            for item in data:
                result = search_for_match(item, depth + 1)
                if result is not None:
                    return result
        
        return None
    
    return search_for_match(json_data)


# =============================================================================
# CLI for testing
# =============================================================================

def main():
    """Test the path parser with example paths."""
    import sys
    import json
    
    roscoe_root = os.environ.get("ROSCOE_ROOT", "/path/to/Roscoe_runtime")
    test_paths = [
        f"{roscoe_root}/John-Doe-MVA-01-01-2025/Insurance/State Farm/LOR to PIP.docx",
        f"{roscoe_root}/John-Doe-MVA-01-01-2025/Medical Providers/UK Hospital/records_request.docx",
        f"{roscoe_root}/John-Doe-MVA-01-01-2025/Litigation/Complaint.md",
        f"{roscoe_root}/John-Doe-MVA-01-01-2025/Documents/Demand/Demand to State Farm.md",
    ]
    
    # Use command line arg if provided
    if len(sys.argv) > 1:
        test_paths = [sys.argv[1]]
    
    for path in test_paths:
        print(f"\n{'='*60}")
        print(f"Path: {path}")
        print(f"{'='*60}")
        
        context = parse_path_context(path)
        print(json.dumps(context, indent=2, default=str))


if __name__ == "__main__":
    main()

