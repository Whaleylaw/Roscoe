#!/usr/bin/env python3
"""
Calendar Add Event Tool

Add a new event to /Database/calendar.json.

Usage:
    python calendar_add_event.py --title TITLE --date DATE --event-type TYPE [options]

Required:
    --title TITLE        Event title
    --date DATE          Event date (YYYY-MM-DD)
    --event-type TYPE    Type: meeting, deadline, task, reminder

Optional:
    --project NAME       Associated project name
    --priority PRIORITY  Priority: high, medium, low (default: medium)
    --time TIME          Event time (HH:MM)
    --notes NOTES        Additional notes
    --depends-on IDS     Comma-separated event IDs this depends on
    --pretty             Pretty print JSON output

Examples:
    python calendar_add_event.py --title "Client meeting" --date 2025-12-10 --event-type meeting --project "Wilson-MVA-2024" --priority high
    python calendar_add_event.py --title "File motion" --date 2025-12-15 --event-type deadline --notes "Discovery deadline"
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
        return {
            "version": "1.0.0",
            "description": "Agent calendar for tracking deadlines, tasks, and events linked to cases",
            "events": []
        }
    
    try:
        with open(calendar_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading calendar: {e}", file=sys.stderr)
        return {"version": "1.0.0", "events": []}


def save_calendar(calendar_data: Dict[str, Any]) -> bool:
    """Save calendar data to JSON file."""
    calendar_path = get_workspace_path() / "Database" / "calendar.json"
    
    try:
        # Ensure directory exists
        calendar_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(calendar_path, 'w') as f:
            json.dump(calendar_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving calendar: {e}", file=sys.stderr)
        return False


def generate_event_id(events: List[Dict[str, Any]]) -> str:
    """Generate a new unique event ID."""
    existing_ids = {e.get("id", "") for e in events}
    
    # Find the highest existing ID number
    max_num = 0
    for event_id in existing_ids:
        if event_id.startswith("evt-"):
            try:
                num = int(event_id.split("-")[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                pass
    
    # Generate new ID
    new_num = max_num + 1
    return f"evt-{new_num:03d}"


def main():
    parser = argparse.ArgumentParser(description="Add a new calendar event")
    parser.add_argument("--title", required=True, help="Event title")
    parser.add_argument("--date", required=True, help="Event date (YYYY-MM-DD)")
    parser.add_argument("--event-type", required=True, choices=["meeting", "deadline", "task", "reminder"], help="Event type")
    parser.add_argument("--project", help="Associated project name")
    parser.add_argument("--priority", choices=["high", "medium", "low"], default="medium", help="Priority level")
    parser.add_argument("--time", help="Event time (HH:MM)")
    parser.add_argument("--notes", help="Additional notes")
    parser.add_argument("--depends-on", help="Comma-separated event IDs this depends on")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    args = parser.parse_args()
    
    # Validate date format
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print(json.dumps({"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}))
        sys.exit(1)
    
    # Validate time format if provided
    if args.time:
        try:
            datetime.strptime(args.time, "%H:%M")
        except ValueError:
            print(json.dumps({"success": False, "error": "Invalid time format. Use HH:MM"}))
            sys.exit(1)
    
    # Load calendar
    calendar_data = load_calendar()
    events = calendar_data.get("events", [])
    
    # Generate new event ID
    event_id = generate_event_id(events)
    
    # Parse depends_on
    depends_on = None
    if args.depends_on:
        depends_on = [d.strip() for d in args.depends_on.split(",")]
    
    # Create new event
    new_event = {
        "id": event_id,
        "title": args.title,
        "date": args.date,
        "time": args.time,
        "event_type": args.event_type,
        "project_name": args.project,
        "priority": args.priority,
        "status": "pending",
        "notes": args.notes,
        "prerequisite_for": None,
        "depends_on": depends_on,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "created_by": "agent"
    }
    
    # Add event
    events.append(new_event)
    calendar_data["events"] = events
    
    # Save calendar
    if save_calendar(calendar_data):
        result = {
            "success": True,
            "message": f"Event '{args.title}' added successfully",
            "event": new_event
        }
    else:
        result = {
            "success": False,
            "error": "Failed to save calendar"
        }
    
    print(json.dumps(result, indent=2 if args.pretty else None))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

