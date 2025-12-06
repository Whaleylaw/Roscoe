#!/usr/bin/env python3
"""
Calendar List Events Tool

List and filter calendar events from /Database/calendar.json.

Usage:
    python calendar_list_events.py [options]

Options:
    --project NAME       Filter by project name
    --status STATUS      Filter by status (pending, completed)
    --event-type TYPE    Filter by type (meeting, deadline, task, reminder)
    --priority PRIORITY  Filter by priority (high, medium, low)
    --date-from DATE     Filter events from this date (YYYY-MM-DD)
    --date-to DATE       Filter events until this date (YYYY-MM-DD)
    --pretty             Pretty print JSON output

Examples:
    python calendar_list_events.py
    python calendar_list_events.py --project "Wilson-MVA-2024" --status pending
    python calendar_list_events.py --date-from 2025-12-01 --date-to 2025-12-31 --pretty
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_workspace_path() -> Path:
    """Get workspace path from environment or default."""
    return Path(os.environ.get("WORKSPACE_DIR", os.environ.get("WORKSPACE_ROOT", "/mnt/workspace")))


def load_calendar() -> Dict[str, Any]:
    """Load calendar data from JSON file."""
    calendar_path = get_workspace_path() / "Database" / "calendar.json"
    
    if not calendar_path.exists():
        return {"version": "1.0.0", "events": []}
    
    try:
        with open(calendar_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading calendar: {e}", file=sys.stderr)
        return {"version": "1.0.0", "events": []}


def filter_events(
    events: List[Dict[str, Any]],
    project: Optional[str] = None,
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    priority: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Filter events based on criteria."""
    filtered = events
    
    if project:
        filtered = [e for e in filtered if e.get("project_name", "").lower() == project.lower()]
    
    if status:
        filtered = [e for e in filtered if e.get("status", "").lower() == status.lower()]
    
    if event_type:
        filtered = [e for e in filtered if e.get("event_type", "").lower() == event_type.lower()]
    
    if priority:
        filtered = [e for e in filtered if e.get("priority", "").lower() == priority.lower()]
    
    if date_from:
        filtered = [e for e in filtered if e.get("date", "") >= date_from]
    
    if date_to:
        filtered = [e for e in filtered if e.get("date", "") <= date_to]
    
    # Sort by date, then priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    filtered.sort(key=lambda e: (e.get("date", "9999-99-99"), priority_order.get(e.get("priority", "low"), 2)))
    
    return filtered


def main():
    parser = argparse.ArgumentParser(description="List and filter calendar events")
    parser.add_argument("--project", help="Filter by project name")
    parser.add_argument("--status", choices=["pending", "completed"], help="Filter by status")
    parser.add_argument("--event-type", choices=["meeting", "deadline", "task", "reminder"], help="Filter by event type")
    parser.add_argument("--priority", choices=["high", "medium", "low"], help="Filter by priority")
    parser.add_argument("--date-from", help="Filter events from this date (YYYY-MM-DD)")
    parser.add_argument("--date-to", help="Filter events until this date (YYYY-MM-DD)")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    args = parser.parse_args()
    
    # Load calendar
    calendar_data = load_calendar()
    events = calendar_data.get("events", [])
    
    # Filter events
    filtered = filter_events(
        events,
        project=args.project,
        status=args.status,
        event_type=args.event_type,
        priority=args.priority,
        date_from=args.date_from,
        date_to=args.date_to,
    )
    
    # Output result
    result = {
        "success": True,
        "total_events": len(events),
        "filtered_count": len(filtered),
        "events": filtered,
    }
    
    print(json.dumps(result, indent=2 if args.pretty else None))
    sys.exit(0)


if __name__ == "__main__":
    main()

