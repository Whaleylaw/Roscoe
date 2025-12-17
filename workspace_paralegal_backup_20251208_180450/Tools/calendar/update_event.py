#!/usr/bin/env python3
"""
Update an existing calendar event.

Usage:
    python update_event.py --id EVENT_ID [OPTIONS]

Required:
    --id TEXT           Event ID to update

Options:
    --title TEXT        New title
    --date YYYY-MM-DD   New date
    --time HH:MM        New time
    --end-time HH:MM    New end time
    --type TYPE         New type: deadline, task, hearing, deposition, meeting, reminder
    --project NAME      New project/case name
    --priority PRIORITY New priority: high, normal, low
    --status STATUS     New status: pending, completed, cancelled
    --description TEXT  New description
    --pretty            Pretty-print JSON output

Examples:
    python update_event.py --id "evt-abc123" --status completed
    python update_event.py --id "evt-abc123" --date "2025-12-20" --priority high
    python update_event.py --id "evt-abc123" --title "Updated Title" --description "New details"
"""

import argparse
import json
import sys
from datetime import datetime
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


def validate_date(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD."""
    if not date_str:
        return True
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_time(time_str: str) -> bool:
    """Validate time format HH:MM."""
    if not time_str:
        return True
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


def find_event(events: list, event_id: str) -> tuple:
    """Find event by ID, return (index, event) or (None, None)."""
    for i, event in enumerate(events):
        if event.get('id') == event_id:
            return i, event
    return None, None


def main():
    parser = argparse.ArgumentParser(description="Update an existing calendar event.")
    parser.add_argument("--id", required=True, help="Event ID to update")
    parser.add_argument("--title", help="New title")
    parser.add_argument("--date", help="New date (YYYY-MM-DD)")
    parser.add_argument("--time", help="New time (HH:MM)")
    parser.add_argument("--end-time", help="New end time (HH:MM)")
    parser.add_argument("--type", choices=['deadline', 'task', 'hearing', 'deposition', 'meeting', 'reminder'],
                        help="New event type")
    parser.add_argument("--project", help="New project/case name")
    parser.add_argument("--priority", choices=['high', 'normal', 'low'], help="New priority")
    parser.add_argument("--status", choices=['pending', 'completed', 'cancelled'], help="New status")
    parser.add_argument("--description", help="New description")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not validate_date(args.date):
        print(json.dumps({
            "success": False,
            "error": f"Invalid date format: {args.date}. Use YYYY-MM-DD."
        }))
        return 1
    
    if not validate_time(args.time):
        print(json.dumps({
            "success": False,
            "error": f"Invalid time format: {args.time}. Use HH:MM (24-hour)."
        }))
        return 1
    
    if not validate_time(args.end_time):
        print(json.dumps({
            "success": False,
            "error": f"Invalid end time format: {args.end_time}. Use HH:MM (24-hour)."
        }))
        return 1
    
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
    
    # Track changes
    changes = {}
    
    # Apply updates
    if args.title:
        changes['title'] = {'old': event.get('title'), 'new': args.title}
        event['title'] = args.title
    
    if args.date:
        changes['date'] = {'old': event.get('date'), 'new': args.date}
        event['date'] = args.date
    
    if args.time:
        changes['time'] = {'old': event.get('time'), 'new': args.time}
        event['time'] = args.time
    
    if args.end_time:
        changes['end_time'] = {'old': event.get('end_time'), 'new': args.end_time}
        event['end_time'] = args.end_time
    
    if args.type:
        changes['type'] = {'old': event.get('type'), 'new': args.type}
        event['type'] = args.type
    
    if args.project:
        changes['project_name'] = {'old': event.get('project_name'), 'new': args.project}
        event['project_name'] = args.project
    
    if args.priority:
        changes['priority'] = {'old': event.get('priority'), 'new': args.priority}
        event['priority'] = args.priority
    
    if args.status:
        changes['status'] = {'old': event.get('status'), 'new': args.status}
        event['status'] = args.status
        # Add completed_at timestamp if marking as completed
        if args.status == 'completed':
            event['completed_at'] = datetime.now().isoformat()
    
    if args.description:
        changes['description'] = {'old': event.get('description'), 'new': args.description}
        event['description'] = args.description
    
    # Add updated_at timestamp
    event['updated_at'] = datetime.now().isoformat()
    
    # Save calendar
    calendar['events'][idx] = event
    save_calendar(calendar)
    
    # Output result
    output = {
        "success": True,
        "message": f"Event '{event.get('title')}' updated",
        "changes": changes,
        "event": event
    }
    
    print(json.dumps(output, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())

