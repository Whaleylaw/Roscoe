#!/usr/bin/env python3
"""
List calendar events with optional filtering.

Usage:
    python list_events.py [OPTIONS]

Options:
    --days N            Show events for next N days (default: 7)
    --project NAME      Filter by project/case name
    --type TYPE         Filter by event type (deadline, task, hearing, deposition, meeting, reminder)
    --status STATUS     Filter by status (pending, completed, cancelled)
    --priority PRIORITY Filter by priority (high, normal, low)
    --all               Show all events regardless of date
    --pretty            Pretty-print JSON output

Examples:
    python list_events.py --days 14
    python list_events.py --project "McCay-MVA-2023" --status pending
    python list_events.py --type deadline --priority high
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Calendar file location
CALENDAR_PATH = Path("/mnt/workspace/Database/calendar.json")


def load_calendar() -> dict:
    """Load the calendar JSON file."""
    if not CALENDAR_PATH.exists():
        return {"events": []}
    
    try:
        with open(CALENDAR_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"events": []}


def filter_events(
    events: list,
    days: int = None,
    project: str = None,
    event_type: str = None,
    status: str = None,
    priority: str = None,
    show_all: bool = False
) -> list:
    """Filter events based on criteria."""
    filtered = events
    today = datetime.now().date()
    
    # Date filtering
    if not show_all and days is not None:
        end_date = today + timedelta(days=days)
        filtered = [
            e for e in filtered
            if e.get('date') and today <= datetime.strptime(e['date'], '%Y-%m-%d').date() <= end_date
        ]
    
    # Project filtering (case-insensitive partial match)
    if project:
        project_lower = project.lower()
        filtered = [
            e for e in filtered
            if e.get('project_name') and project_lower in e['project_name'].lower()
        ]
    
    # Type filtering
    if event_type:
        filtered = [e for e in filtered if e.get('type') == event_type]
    
    # Status filtering
    if status:
        filtered = [e for e in filtered if e.get('status') == status]
    
    # Priority filtering
    if priority:
        filtered = [e for e in filtered if e.get('priority') == priority]
    
    # Sort by date, then priority
    priority_order = {'high': 0, 'normal': 1, 'low': 2}
    filtered.sort(key=lambda e: (
        e.get('date', '9999-99-99'),
        e.get('time', '23:59'),
        priority_order.get(e.get('priority', 'normal'), 1)
    ))
    
    return filtered


def format_event_summary(event: dict) -> str:
    """Format a single event for display."""
    date = event.get('date', 'No date')
    time = event.get('time', '')
    title = event.get('title', 'Untitled')
    event_type = event.get('type', 'task')
    project = event.get('project_name', '')
    priority = event.get('priority', 'normal')
    status = event.get('status', 'pending')
    
    # Priority indicator
    priority_icons = {'high': '🔴', 'normal': '🟡', 'low': '🟢'}
    priority_icon = priority_icons.get(priority, '⚪')
    
    # Type indicator
    type_icons = {
        'deadline': '⏰',
        'task': '📋',
        'hearing': '⚖️',
        'deposition': '📝',
        'meeting': '👥',
        'reminder': '🔔'
    }
    type_icon = type_icons.get(event_type, '📌')
    
    # Status indicator
    status_icon = '✅' if status == 'completed' else ('❌' if status == 'cancelled' else '')
    
    time_str = f" at {time}" if time else ""
    project_str = f" [{project}]" if project else ""
    
    return f"{priority_icon} {type_icon} {date}{time_str}: {title}{project_str} {status_icon}".strip()


def main():
    parser = argparse.ArgumentParser(description="List calendar events with optional filtering.")
    parser.add_argument("--days", type=int, default=7, help="Show events for next N days (default: 7)")
    parser.add_argument("--project", type=str, help="Filter by project/case name")
    parser.add_argument("--type", type=str, choices=['deadline', 'task', 'hearing', 'deposition', 'meeting', 'reminder'],
                        help="Filter by event type")
    parser.add_argument("--status", type=str, choices=['pending', 'completed', 'cancelled'],
                        help="Filter by status")
    parser.add_argument("--priority", type=str, choices=['high', 'normal', 'low'],
                        help="Filter by priority")
    parser.add_argument("--all", action="store_true", help="Show all events regardless of date")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    calendar = load_calendar()
    events = calendar.get('events', [])
    
    filtered = filter_events(
        events,
        days=args.days,
        project=args.project,
        event_type=args.type,
        status=args.status,
        priority=args.priority,
        show_all=args.all
    )
    
    # Build output
    today = datetime.now()
    output = {
        "success": True,
        "query": {
            "days": args.days if not args.all else "all",
            "project": args.project,
            "type": args.type,
            "status": args.status,
            "priority": args.priority
        },
        "total_events": len(filtered),
        "as_of": today.strftime("%Y-%m-%d %H:%M:%S"),
        "events": filtered,
        "summary": [format_event_summary(e) for e in filtered]
    }
    
    print(json.dumps(output, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())

