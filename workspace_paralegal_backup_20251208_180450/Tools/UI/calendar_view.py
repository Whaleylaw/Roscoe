#!/usr/bin/env python3
"""
Calendar UI module - generates structured JSON for the CalendarView React component.

Uses Python's built-in calendar module for proper day names and month layouts.

Usage:
    python calendar_view.py [OPTIONS]

Options:
    --time RANGE        Time range: today, week, 30days, month, all (default: today)
    --project NAME      Filter by project/case name (optional)
    --month YYYY-MM     Show specific month (e.g., 2025-12)
    --include-completed Include completed events

Examples:
    python calendar_view.py --time today
    python calendar_view.py --time week --project "Robinson"
    python calendar_view.py --month 2025-12
    python calendar_view.py --time all --project "McCay"
"""

import argparse
import calendar
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import os

# Calendar file location
WORKSPACE = os.environ.get("WORKSPACE_DIR", "/mnt/workspace")
CALENDAR_PATH = Path(WORKSPACE) / "Database" / "calendar.json"


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
    start_date: datetime,
    end_date: datetime = None,
    project: str = None,
    include_completed: bool = False
) -> list:
    """Filter events based on criteria."""
    filtered = []
    
    for event in events:
        event_date_str = event.get('date')
        if not event_date_str:
            continue
        
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d')
        except ValueError:
            continue
        
        if event_date < start_date:
            continue
        if end_date and event_date > end_date:
            continue
        
        event_status = event.get('status', 'pending')
        if not include_completed and event_status == 'completed':
            continue
        
        if project:
            event_project = event.get('project_name', '')
            if project.lower() not in event_project.lower():
                continue
        
        filtered.append(event)
    
    # Sort by date and priority
    priority_order = {'high': 0, 'medium': 1, 'normal': 2, 'low': 3}
    filtered.sort(key=lambda e: (
        e.get('date', ''),
        priority_order.get(e.get('priority', 'normal'), 2),
        e.get('time', '00:00')
    ))
    
    return filtered


def get_event_type_icon(event_type: str) -> str:
    """Get icon for event type."""
    icons = {
        'meeting': '👥',
        'deadline': '⏰',
        'task': '📋',
        'hearing': '⚖️',
        'deposition': '📝',
        'reminder': '🔔',
        'call': '📞',
        'filing': '📁'
    }
    return icons.get(event_type, '📌')


def get_day_info(date_str: str) -> dict:
    """Get day information using Python's calendar module."""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now().date()
        date_obj = dt.date()
        diff = (date_obj - today).days
        
        # Day of week (0=Monday in calendar module)
        dow = calendar.weekday(dt.year, dt.month, dt.day)
        
        # Relative description
        if diff == 0:
            relative = "Today"
        elif diff == 1:
            relative = "Tomorrow"
        elif diff == -1:
            relative = "Yesterday"
        elif 0 < diff <= 7:
            relative = calendar.day_name[dow]  # Just the day name
        else:
            relative = dt.strftime("%b %d")  # "Dec 03"
        
        return {
            "day_name": calendar.day_name[dow],      # "Monday", "Tuesday", etc.
            "day_abbr": calendar.day_abbr[dow],      # "Mon", "Tue", etc.
            "day_number": dt.day,                     # 1-31
            "month_name": calendar.month_name[dt.month],  # "December"
            "month_abbr": calendar.month_abbr[dt.month],  # "Dec"
            "year": dt.year,
            "relative": relative,
            "is_today": diff == 0,
            "is_past": diff < 0,
            "is_weekend": dow >= 5,  # Saturday=5, Sunday=6
            "week_number": dt.isocalendar()[1]
        }
    except ValueError:
        return {}


def build_month_grid(year: int, month: int, events_by_date: dict) -> list:
    """Build a month calendar grid with events."""
    # Get the calendar for the month (list of weeks, each week is list of days)
    # 0 means day doesn't exist in that week position
    month_cal = calendar.monthcalendar(year, month)
    
    weeks = []
    for week in month_cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)  # Empty cell
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                day_events = events_by_date.get(date_str, [])
                week_data.append({
                    "day": day,
                    "date": date_str,
                    "day_info": get_day_info(date_str),
                    "events": day_events,
                    "event_count": len(day_events),
                    "has_high_priority": any(e.get('priority') == 'high' for e in day_events)
                })
        weeks.append(week_data)
    
    return weeks


def format_event(event: dict) -> dict:
    """Format an event for display."""
    return {
        "id": event.get('id'),
        "title": event.get('title'),
        "time": event.get('time'),
        "type": event.get('event_type', 'task'),
        "type_icon": get_event_type_icon(event.get('event_type', 'task')),
        "project_name": event.get('project_name'),
        "project_short": '-'.join(event.get('project_name', '').split('-')[0:2]) if event.get('project_name') else None,
        "priority": event.get('priority', 'normal'),
        "status": event.get('status', 'pending'),
        "notes": event.get('notes'),
        "depends_on": event.get('depends_on'),
        "prerequisite_for": event.get('prerequisite_for')
    }


def build_list_view(events: list, time_range: str, project: str = None) -> dict:
    """Build a list view grouped by date."""
    by_date = defaultdict(list)
    for event in events:
        date = event.get('date', 'Unknown')
        by_date[date].append(format_event(event))
    
    days = []
    for date in sorted(by_date.keys()):
        days.append({
            "date": date,
            "day_info": get_day_info(date),
            "events": by_date[date]
        })
    
    # Summary stats
    total = len(events)
    by_type = defaultdict(int)
    by_project = defaultdict(int)
    high_priority = sum(1 for e in events if e.get('priority') == 'high')
    
    for event in events:
        by_type[event.get('event_type', 'task')] += 1
        if event.get('project_name'):
            proj_short = '-'.join(event['project_name'].split('-')[0:2])
            by_project[proj_short] += 1
    
    return {
        "view_type": "list",
        "time_range": time_range,
        "project_filter": project,
        "total_events": total,
        "high_priority_count": high_priority,
        "days": days,
        "summary": {
            "by_type": dict(by_type),
            "by_project": dict(by_project)
        }
    }


def build_month_view(year: int, month: int, events: list, project: str = None) -> dict:
    """Build a full month calendar view."""
    # Group events by date
    events_by_date = defaultdict(list)
    for event in events:
        date = event.get('date')
        if date and date.startswith(f"{year}-{month:02d}"):
            events_by_date[date].append(format_event(event))
    
    # Build the month grid
    weeks = build_month_grid(year, month, events_by_date)
    
    # Summary
    total = len(events)
    high_priority = sum(1 for e in events if e.get('priority') == 'high')
    
    return {
        "view_type": "month",
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "project_filter": project,
        "total_events": total,
        "high_priority_count": high_priority,
        "day_headers": list(calendar.day_abbr),  # ["Mon", "Tue", "Wed", ...]
        "weeks": weeks
    }


def main():
    parser = argparse.ArgumentParser(description="Generate calendar UI data.")
    parser.add_argument("--time", default="today", 
                        choices=['today', 'week', '30days', 'month', 'all'],
                        help="Time range (default: today)")
    parser.add_argument("--project", help="Filter by project/case name")
    parser.add_argument("--month", help="Specific month YYYY-MM (e.g., 2025-12)")
    parser.add_argument("--include-completed", action="store_true",
                        help="Include completed events")
    
    args = parser.parse_args()
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Handle month view specially
    if args.month:
        try:
            year, month = map(int, args.month.split('-'))
        except ValueError:
            print(json.dumps({"error": f"Invalid month format: {args.month}. Use YYYY-MM"}))
            return 1
        
        # Get first and last day of month
        _, last_day = calendar.monthrange(year, month)
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, last_day, 23, 59, 59)
        view_type = "month"
    else:
        # Standard time ranges
        if args.time == 'today':
            start_date = today
            end_date = today + timedelta(days=1) - timedelta(seconds=1)
        elif args.time == 'week':
            start_date = today
            end_date = today + timedelta(days=7)
        elif args.time == '30days':
            start_date = today
            end_date = today + timedelta(days=30)
        elif args.time == 'month':
            # Current month
            _, last_day = calendar.monthrange(today.year, today.month)
            start_date = datetime(today.year, today.month, 1)
            end_date = datetime(today.year, today.month, last_day, 23, 59, 59)
        else:  # all
            start_date = datetime(2020, 1, 1)
            end_date = None
        view_type = args.time
    
    # Load and filter events
    cal_data = load_calendar()
    events = cal_data.get('events', [])
    
    filtered = filter_events(
        events,
        start_date,
        end_date,
        project=args.project,
        include_completed=args.include_completed
    )
    
    # Build appropriate view
    if args.month or args.time == 'month':
        if args.month:
            year, month = map(int, args.month.split('-'))
        else:
            year, month = today.year, today.month
        view_data = build_month_view(year, month, filtered, args.project)
    else:
        view_data = build_list_view(filtered, args.time, args.project)
    
    output = {
        "component": "CalendarView",
        "data": view_data
    }
    
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
