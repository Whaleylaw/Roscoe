#!/usr/bin/env python3
"""
Add a new event to the calendar.

Usage:
    python add_event.py --title "Event Title" --date "2025-12-15" [OPTIONS]

Required:
    --title TEXT        Event title/description
    --date YYYY-MM-DD   Event date

Options:
    --time HH:MM        Event time (24-hour format)
    --end-time HH:MM    Event end time
    --type TYPE         Event type: deadline, task, hearing, deposition, meeting, reminder (default: task)
    --project NAME      Associated project/case name
    --priority PRIORITY Priority: high, normal, low (default: normal)
    --description TEXT  Additional details
    --pretty            Pretty-print JSON output

Examples:
    python add_event.py --title "McCay Discovery Due" --date "2025-12-15" --type deadline --project "Caryn-McCay-MVA-7-30-2023" --priority high
    python add_event.py --title "Review Wilson Records" --date "2025-12-03" --type task --project "Wilson-MVA-2024"
    python add_event.py --title "Smith Deposition" --date "2025-12-10" --time "09:00" --end-time "12:00" --type deposition --project "Smith-Slip-Fall-2024"
"""

import argparse
import json
import sys
import uuid
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


def create_event(
    title: str,
    date: str,
    time: str = None,
    end_time: str = None,
    event_type: str = "task",
    project: str = None,
    priority: str = "normal",
    description: str = None
) -> dict:
    """Create a new event dictionary."""
    event = {
        "id": f"evt-{uuid.uuid4().hex[:8]}",
        "title": title,
        "date": date,
        "type": event_type,
        "priority": priority,
        "status": "pending",
        "created_by": "Roscoe",
        "created_at": datetime.now().isoformat()
    }
    
    if time:
        event["time"] = time
    if end_time:
        event["end_time"] = end_time
    if project:
        event["project_name"] = project
    if description:
        event["description"] = description
    
    return event


def main():
    parser = argparse.ArgumentParser(description="Add a new event to the calendar.")
    parser.add_argument("--title", required=True, help="Event title/description")
    parser.add_argument("--date", required=True, help="Event date (YYYY-MM-DD)")
    parser.add_argument("--time", help="Event time (HH:MM, 24-hour format)")
    parser.add_argument("--end-time", help="Event end time (HH:MM)")
    parser.add_argument("--type", default="task",
                        choices=['deadline', 'task', 'hearing', 'deposition', 'meeting', 'reminder'],
                        help="Event type (default: task)")
    parser.add_argument("--project", help="Associated project/case name")
    parser.add_argument("--priority", default="normal",
                        choices=['high', 'normal', 'low'],
                        help="Priority level (default: normal)")
    parser.add_argument("--description", help="Additional details")
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
    
    # Create event
    event = create_event(
        title=args.title,
        date=args.date,
        time=args.time,
        end_time=args.end_time,
        event_type=args.type,
        project=args.project,
        priority=args.priority,
        description=args.description
    )
    
    # Add to calendar
    calendar['events'].append(event)
    
    # Save calendar
    save_calendar(calendar)
    
    # Output result
    output = {
        "success": True,
        "message": f"Event '{args.title}' added to calendar",
        "event": event
    }
    
    print(json.dumps(output, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())

