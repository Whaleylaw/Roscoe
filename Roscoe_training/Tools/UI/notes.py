#!/usr/bin/env python3
"""
Notes listing UI component.

Displays case notes with optional time filtering.

Usage:
    python notes.py --project-name "Case-Name" [--days N] [--note-type TYPE]

Arguments:
    --project-name: Case folder name (required)
    --days: Number of days to look back (optional, default: all)
    --note-type: Filter by note type (optional)

Output:
    JSON with component="NotesView" for frontend rendering
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import shared utilities
from _utils import (
    get_workspace_path,
    get_project_path,
    read_json_file,
    output_result,
    output_error,
)


def get_notes_data(
    project_name: str,
    days: Optional[int] = None,
    note_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get notes for a case with optional filtering.
    
    Args:
        project_name: Case folder name
        days: Number of days to look back (None = all)
        note_type: Filter by note type (None = all types)
    
    Returns:
        Dictionary with notes data for UI rendering
    """
    workspace_path = get_workspace_path()
    project_path = get_project_path(project_name)
    
    # Try project-specific notes first, then fall back to master list
    notes_path = project_path / "notes.json"
    if not notes_path.exists():
        notes_path = workspace_path / "Database" / "master_lists" / "notes.json"
    
    if not notes_path.exists():
        return {
            "error": f"No notes found for {project_name}",
            "project_name": project_name,
        }
    
    # Read notes
    all_notes = read_json_file(notes_path)
    if not isinstance(all_notes, list):
        all_notes = [all_notes] if all_notes else []
    
    # Filter by project name
    project_notes = [
        n for n in all_notes
        if n.get("project_name") == project_name
        or project_name in (n.get("applies_to_projects") or [])
    ]
    
    # Calculate cutoff date if days specified
    cutoff_date = None
    if days is not None:
        cutoff_date = datetime.now() - timedelta(days=days)
    
    # Filter and format notes
    filtered_notes = []
    for note in project_notes:
        # Parse date
        last_activity = note.get("last_activity")
        if last_activity:
            try:
                note_date = datetime.strptime(last_activity, "%Y-%m-%d")
            except ValueError:
                note_date = None
        else:
            note_date = None
        
        # Apply date filter
        if cutoff_date and note_date and note_date < cutoff_date:
            continue
        
        # Apply note type filter
        if note_type and note.get("note_type") != note_type:
            continue
        
        # Format note for display
        filtered_notes.append({
            "date": last_activity or "Unknown",
            "time": note.get("time", ""),
            "author": note.get("author_name", "Unknown"),
            "type": note.get("note_type") or "General",
            "summary": note.get("note_summary") or "",
            "content": note.get("note") or "",
            "id": note.get("id"),
        })
    
    # Sort by date (newest first)
    filtered_notes.sort(key=lambda x: x["date"], reverse=True)
    
    # Get unique note types for filtering UI
    note_types = list(set(
        n.get("note_type") or "General"
        for n in project_notes
        if n.get("note_type")
    ))
    note_types.sort()
    
    # Calculate summary stats
    total_notes = len(project_notes)
    filtered_count = len(filtered_notes)
    
    # Get date range
    if filtered_notes:
        oldest_date = filtered_notes[-1]["date"]
        newest_date = filtered_notes[0]["date"]
    else:
        oldest_date = newest_date = None
    
    return {
        "project_name": project_name,
        "total_notes": total_notes,
        "filtered_count": filtered_count,
        "days_filter": days,
        "type_filter": note_type,
        "date_range": {
            "oldest": oldest_date,
            "newest": newest_date,
        },
        "available_types": note_types,
        "notes": filtered_notes,
    }


def main():
    parser = argparse.ArgumentParser(description="List case notes")
    parser.add_argument("--project-name", required=True, help="Case folder name")
    parser.add_argument("--days", type=int, help="Number of days to look back")
    parser.add_argument("--note-type", help="Filter by note type")
    args = parser.parse_args()
    
    data = get_notes_data(
        project_name=args.project_name,
        days=args.days,
        note_type=args.note_type,
    )
    
    if "error" in data:
        output_error(data["error"])
    else:
        output_result({
            "component": "NotesView",
            "data": data,
        })


if __name__ == "__main__":
    main()

