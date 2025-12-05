"""
Google Calendar Tools for Roscoe Paralegal Agent

Provides calendar functionality for case management:
- List upcoming events
- Create calendar events (deadlines, depositions, hearings)
- Update existing events
- Delete events
- Find free time slots

All tools use lazy initialization to avoid pickle issues with LangGraph checkpointing.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, List, Literal
from zoneinfo import ZoneInfo


def _get_calendar_service():
    """Lazily get Google Calendar API service."""
    from roscoe.core.google_auth import get_calendar_service
    return get_calendar_service()


def _get_default_timezone() -> str:
    """Get default timezone from environment or use America/New_York (Eastern)."""
    return os.environ.get("DEFAULT_TIMEZONE", "America/New_York")


def _parse_datetime(dt_str: str, timezone: str = None) -> datetime:
    """
    Parse datetime string into datetime object.
    Supports various formats.
    """
    tz = ZoneInfo(timezone or _get_default_timezone())
    
    formats = [
        "%Y-%m-%dT%H:%M:%S",      # ISO format without timezone
        "%Y-%m-%d %H:%M:%S",      # Common format
        "%Y-%m-%d %H:%M",         # Without seconds
        "%Y-%m-%d",               # Date only (will use 9:00 AM)
        "%m/%d/%Y %H:%M",         # US format
        "%m/%d/%Y",               # US date only
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            return dt.replace(tzinfo=tz)
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse datetime: {dt_str}")


def _format_event(event: dict) -> dict:
    """Format calendar event into a clean summary dict."""
    start = event.get('start', {})
    end = event.get('end', {})
    
    # Handle all-day events vs timed events
    start_str = start.get('dateTime', start.get('date', ''))
    end_str = end.get('dateTime', end.get('date', ''))
    is_all_day = 'date' in start and 'dateTime' not in start
    
    return {
        "id": event.get('id'),
        "summary": event.get('summary', '(No title)'),
        "description": event.get('description', ''),
        "location": event.get('location', ''),
        "start": start_str,
        "end": end_str,
        "is_all_day": is_all_day,
        "status": event.get('status', 'confirmed'),
        "html_link": event.get('htmlLink', ''),
        "attendees": [a.get('email') for a in event.get('attendees', [])],
        "creator": event.get('creator', {}).get('email', ''),
    }


def list_events(
    days: int = 7,
    max_results: int = 20,
    calendar_id: str = "primary",
    query: Optional[str] = None,
) -> str:
    """
    List upcoming calendar events.
    
    Args:
        days: Number of days to look ahead (default: 7)
        max_results: Maximum events to return (default: 20, max: 100)
        calendar_id: Calendar ID (default: "primary" for main calendar)
        query: Optional search query to filter events
    
    Returns:
        List of upcoming events with details
    
    Examples:
        list_events()  # Next 7 days
        list_events(days=30)  # Next month
        list_events(query="Wilson")  # Events mentioning Wilson
        list_events(days=14, query="deposition")  # Depositions in next 2 weeks
    """
    service = _get_calendar_service()
    if not service:
        return "Error: Google Calendar not configured. Set up Google OAuth credentials first."
    
    try:
        max_results = min(max_results, 100)
        
        now = datetime.utcnow().isoformat() + 'Z'
        time_max = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'
        
        # Build request
        request_params = {
            'calendarId': calendar_id,
            'timeMin': now,
            'timeMax': time_max,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime',
        }
        
        if query:
            request_params['q'] = query
        
        events_result = service.events().list(**request_params).execute()
        events = events_result.get('items', [])
        
        if not events:
            return f"No events found in the next {days} days."
        
        output_lines = [f"**Upcoming Events** (Next {days} days)", ""]
        
        current_date = None
        for event in events:
            formatted = _format_event(event)
            
            # Parse date for grouping
            start_str = formatted['start']
            if 'T' in start_str:
                event_date = start_str.split('T')[0]
                event_time = start_str.split('T')[1][:5]
            else:
                event_date = start_str
                event_time = "All Day"
            
            # Add date header if new date
            if event_date != current_date:
                current_date = event_date
                output_lines.append(f"\n📅 **{event_date}**")
            
            # Format event line
            summary = formatted['summary']
            location = f" @ {formatted['location']}" if formatted['location'] else ""
            
            output_lines.append(f"  • {event_time}: {summary}{location}")
            
            if formatted['description']:
                desc_preview = formatted['description'][:80]
                output_lines.append(f"    _{desc_preview}..._" if len(formatted['description']) > 80 else f"    _{desc_preview}_")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error listing events: {str(e)}"


def create_event(
    summary: str,
    start_datetime: str,
    end_datetime: Optional[str] = None,
    duration_minutes: int = 60,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    send_notifications: bool = True,
    calendar_id: str = "primary",
    timezone: Optional[str] = None,
    event_type: Literal["meeting", "deadline", "hearing", "deposition", "reminder", "other"] = "other",
) -> str:
    """
    Create a new calendar event.
    
    For legal events, include relevant case information in the description
    for easy reference.
    
    Args:
        summary: Event title (e.g., "Wilson MVA - Deposition of Defendant")
        start_datetime: Start time (e.g., "2024-12-15 10:00" or "2024-12-15T10:00:00")
        end_datetime: End time (optional, uses duration_minutes if not provided)
        duration_minutes: Duration in minutes if end_datetime not provided (default: 60)
        description: Event description with case details
        location: Event location (address or "Virtual/Zoom")
        attendees: List of email addresses to invite
        send_notifications: Send email invites to attendees (default: True)
        calendar_id: Calendar to add event to (default: "primary")
        timezone: Timezone (default: America/New_York)
        event_type: Type of legal event for organization
    
    Returns:
        Confirmation with event details and calendar link
    
    Examples:
        create_event("Wilson MVA - SOL Deadline", "2025-07-30", event_type="deadline")
        create_event("Deposition - Dr. Smith", "2024-12-20 14:00", duration_minutes=180, 
                    location="Court Reporter Office", event_type="deposition")
        create_event("Client Meeting - McCay", "2024-12-18 09:00", 
                    attendees=["client@email.com"], event_type="meeting")
    """
    service = _get_calendar_service()
    if not service:
        return "Error: Google Calendar not configured. Set up Google OAuth credentials first."
    
    try:
        tz = timezone or _get_default_timezone()
        
        # Parse start time
        start = _parse_datetime(start_datetime, tz)
        
        # Calculate end time
        if end_datetime:
            end = _parse_datetime(end_datetime, tz)
        else:
            end = start + timedelta(minutes=duration_minutes)
        
        # Add event type tag to summary if not already present
        type_tags = {
            "deadline": "🔴 DEADLINE:",
            "hearing": "⚖️ HEARING:",
            "deposition": "📝 DEPOSITION:",
            "meeting": "👥 MEETING:",
            "reminder": "🔔 REMINDER:",
        }
        
        if event_type in type_tags and not any(tag in summary for tag in type_tags.values()):
            summary = f"{type_tags[event_type]} {summary}"
        
        # Build event body
        event = {
            'summary': summary,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': tz,
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': tz,
            },
        }
        
        if description:
            event['description'] = description
        if location:
            event['location'] = location
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        # Create event
        created = service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates='all' if send_notifications and attendees else 'none'
        ).execute()
        
        output_lines = [
            "✅ Event created successfully!",
            "",
            f"**{created.get('summary')}**",
            f"📅 {start.strftime('%B %d, %Y')}",
            f"🕐 {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}",
        ]
        
        if location:
            output_lines.append(f"📍 {location}")
        if attendees:
            output_lines.append(f"👥 Attendees: {', '.join(attendees)}")
        
        output_lines.extend([
            "",
            f"🔗 [Open in Calendar]({created.get('htmlLink')})",
            f"Event ID: {created.get('id')}"
        ])
        
        return "\n".join(output_lines)
        
    except ValueError as e:
        return f"Error parsing date/time: {str(e)}\nUse format: YYYY-MM-DD HH:MM or YYYY-MM-DD"
    except Exception as e:
        return f"Error creating event: {str(e)}"


def update_event(
    event_id: str,
    summary: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    calendar_id: str = "primary",
    timezone: Optional[str] = None,
) -> str:
    """
    Update an existing calendar event.
    
    Only provide the fields you want to change; other fields remain unchanged.
    
    Args:
        event_id: Event ID to update (from list_events)
        summary: New event title (optional)
        start_datetime: New start time (optional)
        end_datetime: New end time (optional)
        description: New description (optional)
        location: New location (optional)
        calendar_id: Calendar containing the event
        timezone: Timezone for new times
    
    Returns:
        Confirmation with updated event details
    
    Examples:
        update_event("abc123", start_datetime="2024-12-22 15:00")  # Reschedule
        update_event("abc123", location="Zoom Meeting")  # Update location
        update_event("abc123", summary="Rescheduled: Wilson Deposition")
    """
    service = _get_calendar_service()
    if not service:
        return "Error: Google Calendar not configured. Set up Google OAuth credentials first."
    
    try:
        tz = timezone or _get_default_timezone()
        
        # Get existing event
        event = service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        # Update fields
        if summary:
            event['summary'] = summary
        if description is not None:
            event['description'] = description
        if location is not None:
            event['location'] = location
        if start_datetime:
            start = _parse_datetime(start_datetime, tz)
            event['start'] = {'dateTime': start.isoformat(), 'timeZone': tz}
        if end_datetime:
            end = _parse_datetime(end_datetime, tz)
            event['end'] = {'dateTime': end.isoformat(), 'timeZone': tz}
        
        # Update event
        updated = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event
        ).execute()
        
        formatted = _format_event(updated)
        
        return f"✅ Event updated successfully!\n\n**{formatted['summary']}**\nStart: {formatted['start']}\nEnd: {formatted['end']}\n\n🔗 [Open in Calendar]({formatted['html_link']})"
        
    except Exception as e:
        return f"Error updating event: {str(e)}"


def delete_event(
    event_id: str,
    calendar_id: str = "primary",
    send_notifications: bool = True,
) -> str:
    """
    Delete/cancel a calendar event.
    
    Args:
        event_id: Event ID to delete
        calendar_id: Calendar containing the event
        send_notifications: Notify attendees of cancellation
    
    Returns:
        Confirmation of deletion
    
    Examples:
        delete_event("abc123")
        delete_event("abc123", send_notifications=False)
    """
    service = _get_calendar_service()
    if not service:
        return "Error: Google Calendar not configured. Set up Google OAuth credentials first."
    
    try:
        # Get event first to confirm
        event = service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        event_summary = event.get('summary', 'Untitled Event')
        
        # Delete event
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendUpdates='all' if send_notifications else 'none'
        ).execute()
        
        return f"✅ Event deleted: **{event_summary}**\n\nEvent ID: {event_id}"
        
    except Exception as e:
        return f"Error deleting event: {str(e)}"


def find_free_time(
    duration_minutes: int = 60,
    days_ahead: int = 7,
    start_hour: int = 9,
    end_hour: int = 17,
    calendar_id: str = "primary",
    timezone: Optional[str] = None,
) -> str:
    """
    Find available time slots for scheduling.
    
    Searches for gaps in the calendar within business hours.
    
    Args:
        duration_minutes: Required meeting length (default: 60)
        days_ahead: Days to search (default: 7)
        start_hour: Business hours start (default: 9 AM)
        end_hour: Business hours end (default: 5 PM)
        calendar_id: Calendar to check
        timezone: Timezone for results
    
    Returns:
        List of available time slots
    
    Examples:
        find_free_time(duration_minutes=30)  # 30-minute slots this week
        find_free_time(duration_minutes=120, days_ahead=14)  # 2-hour slots, 2 weeks
    """
    service = _get_calendar_service()
    if not service:
        return "Error: Google Calendar not configured. Set up Google OAuth credentials first."
    
    try:
        tz = ZoneInfo(timezone or _get_default_timezone())
        now = datetime.now(tz)
        
        # Get all events in the range
        time_min = now.isoformat()
        time_max = (now + timedelta(days=days_ahead)).isoformat()
        
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Build list of busy times
        busy_times = []
        for event in events:
            start = event.get('start', {})
            end = event.get('end', {})
            
            if 'dateTime' in start:
                start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00')).astimezone(tz)
                end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00')).astimezone(tz)
                busy_times.append((start_dt, end_dt))
        
        # Find free slots
        free_slots = []
        current_date = now.date()
        
        for day_offset in range(days_ahead):
            check_date = current_date + timedelta(days=day_offset)
            
            # Skip weekends
            if check_date.weekday() >= 5:
                continue
            
            day_start = datetime(check_date.year, check_date.month, check_date.day, 
                               start_hour, 0, tzinfo=tz)
            day_end = datetime(check_date.year, check_date.month, check_date.day,
                             end_hour, 0, tzinfo=tz)
            
            # Skip if in the past
            if day_start < now:
                day_start = now + timedelta(minutes=30 - now.minute % 30)  # Round up to next 30 min
            
            current_time = day_start
            
            while current_time + timedelta(minutes=duration_minutes) <= day_end:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                
                # Check if slot conflicts with any busy time
                is_free = True
                for busy_start, busy_end in busy_times:
                    if not (slot_end <= busy_start or current_time >= busy_end):
                        is_free = False
                        # Jump to end of this busy period
                        current_time = busy_end
                        break
                
                if is_free:
                    free_slots.append((current_time, slot_end))
                    current_time = slot_end
                
                # Limit results
                if len(free_slots) >= 10:
                    break
            
            if len(free_slots) >= 10:
                break
        
        if not free_slots:
            return f"No available {duration_minutes}-minute slots found in the next {days_ahead} days."
        
        output_lines = [
            f"**Available {duration_minutes}-minute Time Slots**",
            f"(Next {days_ahead} weekdays, {start_hour}:00 - {end_hour}:00)",
            ""
        ]
        
        current_date = None
        for start, end in free_slots:
            if start.date() != current_date:
                current_date = start.date()
                output_lines.append(f"\n📅 **{start.strftime('%A, %B %d')}**")
            
            output_lines.append(f"  • {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error finding free time: {str(e)}"


def get_event(
    event_id: str,
    calendar_id: str = "primary",
) -> str:
    """
    Get details of a specific calendar event.
    
    Args:
        event_id: Event ID to retrieve
        calendar_id: Calendar containing the event
    
    Returns:
        Full event details
    """
    service = _get_calendar_service()
    if not service:
        return "Error: Google Calendar not configured. Set up Google OAuth credentials first."
    
    try:
        event = service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        formatted = _format_event(event)
        
        output_lines = [
            f"**{formatted['summary']}**",
            "",
            f"📅 Start: {formatted['start']}",
            f"📅 End: {formatted['end']}",
        ]
        
        if formatted['location']:
            output_lines.append(f"📍 Location: {formatted['location']}")
        
        if formatted['description']:
            output_lines.extend(["", "**Description:**", formatted['description']])
        
        if formatted['attendees']:
            output_lines.extend(["", "**Attendees:**"])
            for attendee in formatted['attendees']:
                output_lines.append(f"  • {attendee}")
        
        output_lines.extend([
            "",
            f"Status: {formatted['status']}",
            f"Creator: {formatted['creator']}",
            f"🔗 [Open in Calendar]({formatted['html_link']})",
            f"Event ID: {formatted['id']}"
        ])
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error getting event: {str(e)}"

