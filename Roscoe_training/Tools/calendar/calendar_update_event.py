#!/usr/bin/env python3
"""
Calendar Update Event Tool

Update an existing event in /Database/calendar.json.

Usage:
    python calendar_update_event.py --id EVENT_ID [options]

Required:
    --id ID              Event ID to update (e.g., evt-001)

Optional:
    --title TITLE        New event title
    --date DATE          New event date (YYYY-MM-DD)
    --time TIME          New event time (HH:MM)
    --event-type TYPE    New type: meeting, deadline, task, reminder
    --project NAME       New associated project name
    --priority PRIORITY  New priority: high, medium, low
    --status STATUS      New status: pending, completed
    --notes NOTES        New notes (replaces existing)
    --depends-on IDS     Comma-separated event IDs this depends on
    --mark-complete      Shortcut to set status=completed and add completed_at timestamp
    --pretty             Pretty print JSON output

Examples:
    python calendar_update_event.py --id evt-001 --mark-complete
    python calendar_update_event.py --id evt-002 --date 2025-12-20 --priority high
    python calendar_update_event.py --id evt-003 --notes "Updated: client rescheduled"
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


def save_calendar(calendar_data: Dict[str, Any]) -> bool:
    """Save calendar data to JSON file."""
    calendar_path = get_workspace_path() / "Database" / "calendar.json"
    
    try:
        with open(calendar_path, 'w') as f:
            json.dump(calendar_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving calendar: {e}", file=sys.stderr)
        return False


def find_event(events: List[Dict[str, Any]], event_id: str) -> Optional[Dict[str, Any]]:
    """Find an event by ID."""
    for event in events:
        if event.get("id") == event_id:
            return event
    return None


def main():
    parser = argparse.ArgumentParser(description="Update a calendar event")
    parser.add_argument("--id", required=True, help="Event ID to update")
    parser.add_argument("--title", help="New event title")
    parser.add_argument("--date", help="New event date (YYYY-MM-DD)")
    parser.add_argument("--time", help="New event time (HH:MM)")
    parser.add_argument("--event-type", choices=["meeting", "deadline", "task", "reminder"], help="New event type")
    parser.add_argument("--project", help="New associated project name")
    parser.add_argument("--priority", choices=["high", "medium", "low"], help="New priority level")
    parser.add_argument("--status", choices=["pending", "completed"], help="New status")
    parser.add_argument("--notes", help="New notes (replaces existing)")
    parser.add_argument("--depends-on", help="Comma-separated event IDs this depends on")
    parser.add_argument("--mark-complete", action="store_true", help="Mark event as completed with timestamp")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    args = parser.parse_args()
    
    # Validate date format if provided
    if args.date:
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
    
    # Find event
    event = find_event(events, args.id)
    if not event:
        print(json.dumps({"success": False, "error": f"Event not found: {args.id}"}))
        sys.exit(1)
    
    # Track changes
    changes = []
    
    # Apply updates
    if args.title:
        event["title"] = args.title
        changes.append(f"title → '{args.title}'")
    
    if args.date:
        event["date"] = args.date
        changes.append(f"date → {args.date}")
    
    if args.time:
        event["time"] = args.time
        changes.append(f"time → {args.time}")
    
    if args.event_type:
        event["event_type"] = args.event_type
        changes.append(f"event_type → {args.event_type}")
    
    if args.project:
        event["project_name"] = args.project
        changes.append(f"project → {args.project}")
    
    if args.priority:
        event["priority"] = args.priority
        changes.append(f"priority → {args.priority}")
    
    if args.status:
        event["status"] = args.status
        changes.append(f"status → {args.status}")
        if args.status == "completed" and "completed_at" not in event:
            event["completed_at"] = datetime.utcnow().isoformat() + "Z"
    
    if args.notes:
        event["notes"] = args.notes
        changes.append("notes updated")
    
    if args.depends_on:
        event["depends_on"] = [d.strip() for d in args.depends_on.split(",")]
        changes.append(f"depends_on → {args.depends_on}")
    
    if args.mark_complete:
        event["status"] = "completed"
        event["completed_at"] = datetime.utcnow().isoformat() + "Z"
        changes.append("marked as completed")
    
    # Add updated_at timestamp
    event["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    # Save calendar
    if save_calendar(calendar_data):
        result = {
            "success": True,
            "message": f"Event {args.id} updated: {', '.join(changes)}" if changes else f"No changes made to event {args.id}",
            "event": event
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

