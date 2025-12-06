#!/usr/bin/env python3
"""
Calendar Delete Event Tool

Delete an event from /Database/calendar.json.

Usage:
    python calendar_delete_event.py --id EVENT_ID [options]

Required:
    --id ID              Event ID to delete (e.g., evt-001)

Optional:
    --force              Delete without confirmation (for automation)
    --pretty             Pretty print JSON output

Examples:
    python calendar_delete_event.py --id evt-001
    python calendar_delete_event.py --id evt-002 --force --pretty
"""

import argparse
import json
import os
import sys
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


def find_event_index(events: List[Dict[str, Any]], event_id: str) -> int:
    """Find an event's index by ID. Returns -1 if not found."""
    for i, event in enumerate(events):
        if event.get("id") == event_id:
            return i
    return -1


def find_dependent_events(events: List[Dict[str, Any]], event_id: str) -> List[str]:
    """Find events that depend on the given event ID."""
    dependents = []
    for event in events:
        depends_on = event.get("depends_on", [])
        if depends_on and event_id in depends_on:
            dependents.append(event.get("id", "unknown"))
    return dependents


def main():
    parser = argparse.ArgumentParser(description="Delete a calendar event")
    parser.add_argument("--id", required=True, help="Event ID to delete")
    parser.add_argument("--force", action="store_true", help="Delete without warning about dependents")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    args = parser.parse_args()
    
    # Load calendar
    calendar_data = load_calendar()
    events = calendar_data.get("events", [])
    
    # Find event
    event_index = find_event_index(events, args.id)
    if event_index == -1:
        print(json.dumps({"success": False, "error": f"Event not found: {args.id}"}))
        sys.exit(1)
    
    deleted_event = events[event_index]
    
    # Check for dependent events
    dependents = find_dependent_events(events, args.id)
    if dependents and not args.force:
        result = {
            "success": False,
            "error": f"Event {args.id} has dependent events: {', '.join(dependents)}. Use --force to delete anyway.",
            "dependent_events": dependents
        }
        print(json.dumps(result, indent=2 if args.pretty else None))
        sys.exit(1)
    
    # Remove event
    events.pop(event_index)
    calendar_data["events"] = events
    
    # Clear references in dependent events if forcing deletion
    if dependents and args.force:
        for event in events:
            depends_on = event.get("depends_on", [])
            if depends_on and args.id in depends_on:
                event["depends_on"] = [d for d in depends_on if d != args.id]
                if not event["depends_on"]:
                    event["depends_on"] = None
    
    # Save calendar
    if save_calendar(calendar_data):
        result = {
            "success": True,
            "message": f"Event {args.id} deleted successfully",
            "deleted_event": deleted_event,
            "cleared_from_dependents": dependents if dependents else None
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

