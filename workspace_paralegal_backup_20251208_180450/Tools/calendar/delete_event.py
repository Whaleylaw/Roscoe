#!/usr/bin/env python3
"""
Delete an event from the calendar.

Usage:
    python delete_event.py --id EVENT_ID [OPTIONS]

Required:
    --id TEXT           Event ID to delete

Options:
    --confirm           Skip confirmation (for automated use)
    --pretty            Pretty-print JSON output

Examples:
    python delete_event.py --id "evt-abc123"
    python delete_event.py --id "evt-abc123" --confirm
"""

import argparse
import json
import sys
from pathlib import Path

# Calendar file location
CALENDAR_PATH = Path("/mnt/workspace/Database/calendar.json")


def load_calendar() -> dict:
    """Load the calendar JSON file."""
    if not CALENDAR_PATH.exists():
        return {"version": "1.0.0", "events": []}
    
    try:
        with open(CALENDAR_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"version": "1.0.0", "events": []}


def save_calendar(calendar: dict) -> None:
    """Save the calendar JSON file."""
    CALENDAR_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CALENDAR_PATH, 'w') as f:
        json.dump(calendar, f, indent=2)


def find_event(events: list, event_id: str) -> tuple:
    """Find event by ID, return (index, event) or (None, None)."""
    for i, event in enumerate(events):
        if event.get('id') == event_id:
            return i, event
    return None, None


def main():
    parser = argparse.ArgumentParser(description="Delete an event from the calendar.")
    parser.add_argument("--id", required=True, help="Event ID to delete")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    # Load calendar
    calendar = load_calendar()
    events = calendar.get('events', [])
    
    # Find event
    idx, event = find_event(events, args.id)
    
    if event is None:
        print(json.dumps({
            "success": False,
            "error": f"Event not found: {args.id}"
        }))
        return 1
    
    # Store event info before deletion
    deleted_event = event.copy()
    
    # Remove event
    calendar['events'].pop(idx)
    
    # Save calendar
    save_calendar(calendar)
    
    # Output result
    output = {
        "success": True,
        "message": f"Event '{deleted_event.get('title')}' deleted",
        "deleted_event": deleted_event
    }
    
    print(json.dumps(output, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())

