# Calendar Management System

I maintain a **calendar system** for tracking deadlines, tasks, hearings, and events linked to cases.

## Calendar Location

`Database/calendar.json`

## Event Types

| Type | Use For |
|------|---------|
| `deadline` | Court deadlines, discovery due dates, filing deadlines |
| `task` | General to-do items, follow-ups, reviews |
| `hearing` | Court appearances, motion hearings |
| `deposition` | Scheduled depositions |
| `meeting` | Client meetings, attorney conferences |
| `reminder` | General reminders, check-ins |

## Priority Levels

- `high` - Urgent, time-sensitive
- `normal` - Standard priority
- `low` - When time permits

## Calendar Tools (in `Tools/calendar/`)

| Tool | Purpose | Example |
|------|---------|---------|
| `list_events.py` | List/filter events | `--days 7`, `--project "McCay"`, `--type deadline` |
| `add_event.py` | Create events | `--title "..." --date "YYYY-MM-DD" --project "..." --type deadline` |
| `update_event.py` | Modify events | `--id "evt-xxx" --status completed` |
| `delete_event.py` | Remove events | `--id "evt-xxx"` |

## Calendar UI (in `Tools/UI/`)

`calendar_view.py` - Display calendar: `--view week`, `--view list`, `--project "McCay"`

## When to Create Calendar Events

✅ **DO Create Events For:**
- User mentions a deadline or due date
- Discovery deadlines from litigation documents
- Deposition dates
- Court hearings
- User asks to "remind me" or "schedule" something
- Follow-up tasks from case work

## Responding to Calendar Queries

| User Says | Action |
|-----------|--------|
| "What's on the calendar?" | Run `list_events.py --days 7` and show CalendarView UI |
| "Show me deadlines" | Run `list_events.py --type deadline` |
| "What's coming up for McCay?" | Run `list_events.py --project "McCay"` |
| "Add a deadline..." | Use `add_event.py` with appropriate parameters |

## Auto-Creating Events

When you identify a deadline or important date during case work, proactively create a calendar event:

```python
execute_python_script(
    script_path="Tools/calendar/add_event.py",
    script_args=[
        "--title", "Discovery responses due",
        "--date", "2025-12-15",
        "--type", "deadline",
        "--project", "Case-Name",
        "--priority", "high"
    ]
)
```

## Event Format

```json
{
  "id": "evt-uuid",
  "title": "Event title",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "type": "deadline|task|hearing|deposition|meeting|reminder",
  "priority": "high|normal|low",
  "project_name": "Case-Name",
  "status": "pending|completed|cancelled",
  "notes": "Additional details"
}
```

