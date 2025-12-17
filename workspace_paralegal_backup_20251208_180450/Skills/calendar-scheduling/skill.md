---
name: calendar-scheduling
description: Use when managing case deadlines, scheduling depositions, hearings, client meetings, or tracking important dates. Provides Google Calendar integration for statute of limitations, discovery deadlines, court dates, and appointments.
---

# Calendar Scheduling Skill

This skill provides guidance for managing case deadlines, appointments, and scheduling using Google Calendar tools.

## Available Tools

| Tool | Description |
|------|-------------|
| `list_events` | View upcoming calendar events |
| `create_event` | Create new events (deadlines, hearings, depositions) |
| `update_event` | Modify existing events |
| `delete_event` | Cancel/remove events |
| `find_free_time` | Find available time slots |
| `get_event` | Get full details of specific event |

## Event Types for Legal Practice

The `create_event` tool supports these event types (adds appropriate emoji tag):

| Type | Tag | Use Case |
|------|-----|----------|
| `deadline` | 🔴 DEADLINE: | SOL, discovery deadlines, filing dates |
| `hearing` | ⚖️ HEARING: | Court hearings, motions, trials |
| `deposition` | 📝 DEPOSITION: | Client, defendant, expert depositions |
| `meeting` | 👥 MEETING: | Client meetings, attorney conferences |
| `reminder` | 🔔 REMINDER: | Follow-ups, ticklers |
| `other` | (no tag) | General events |

## Critical Legal Deadlines

### Statute of Limitations

**ALWAYS calendar SOL deadlines immediately when case opens:**

```python
create_event(
    summary="Wilson MVA - Statute of Limitations EXPIRES",
    start_datetime="2025-07-30",  # SOL date
    event_type="deadline",
    description="Kentucky 1-year motor vehicle accident SOL expires. ACTION: File complaint before this date."
)
```

### Discovery Deadlines

Track discovery response deadlines (typically 30 days in Kentucky):

```python
create_event(
    summary="Wilson MVA - Discovery Responses Due",
    start_datetime="2025-02-15",
    event_type="deadline",
    description="Responses to Defendant's First Set of Interrogatories and RFPs due."
)
```

### Motion Deadlines

```python
create_event(
    summary="Wilson MVA - Response to MSJ Due",
    start_datetime="2025-01-20",
    event_type="deadline",
    description="Response to Defendant's Motion for Summary Judgment. 21 days from service."
)
```

## Scheduling Patterns

### Pattern 1: Deposition Scheduling

When scheduling a deposition:

```python
# 1. Check availability
find_free_time(duration_minutes=180, days_ahead=30)

# 2. Create deposition event
create_event(
    summary="Deposition - Dr. Smith (Treating Physician)",
    start_datetime="2025-01-15 14:00",
    duration_minutes=180,
    location="Court Reporter Office - 123 Main St",
    event_type="deposition",
    description="Wilson MVA - Expert deposition of Dr. Smith, orthopedic surgeon",
    attendees=["attorney@firm.com", "courtreporter@example.com"]
)
```

### Pattern 2: Client Meeting

```python
# 1. Find available slots
find_free_time(duration_minutes=60, days_ahead=7)

# 2. Schedule meeting
create_event(
    summary="Client Meeting - Wilson",
    start_datetime="2025-01-10 10:00",
    duration_minutes=60,
    location="Office - Conference Room A",
    event_type="meeting",
    description="Review settlement offer and discuss litigation options",
    attendees=["client@email.com"]
)
```

### Pattern 3: Court Hearing

```python
create_event(
    summary="Motion Hearing - Wilson MVA",
    start_datetime="2025-02-01 09:00",
    duration_minutes=60,
    location="Jefferson Circuit Court, Division 3",
    event_type="hearing",
    description="Hearing on Plaintiff's Motion to Compel Discovery",
    attendees=["attorney@firm.com"]
)
```

## Calendar Review Workflows

### Daily Review

```python
# View today's and tomorrow's events
list_events(days=2)
```

### Weekly Planning

```python
# View next week's schedule
list_events(days=7)
```

### Deadline Review

```python
# Find all upcoming deadlines
list_events(days=30, query="DEADLINE")
```

### Case-Specific View

```python
# View all events for a specific case
list_events(days=60, query="Wilson")
```

## Best Practices

### 1. Deadline Management

- **SOL dates**: Calendar 6 months before, 90 days before, 30 days before, and actual deadline
- **Discovery deadlines**: Calendar when received AND when due
- **Motion deadlines**: Calendar response deadlines immediately upon receipt

### 2. Buffer Time

- Add 30-minute buffers between appointments
- For court hearings, include travel time
- For depositions, include setup and wrap-up time

### 3. Reminders

Create reminder events for important follow-ups:

```python
create_event(
    summary="REMINDER: Follow up on Wilson demand letter",
    start_datetime="2025-01-20",
    event_type="reminder",
    description="30 days since demand sent. Check for response, send follow-up if needed."
)
```

### 4. Description Best Practices

Always include in event description:
- Case name and number
- Purpose of event
- Action items or topics to cover
- Relevant contacts or documents

## Kentucky-Specific Considerations

| Item | Deadline | Notes |
|------|----------|-------|
| Personal Injury SOL | 1 year | KRS 413.140 |
| MVA SOL | 2 years | KRS 413.125 |
| Discovery Responses | 30 days | CR 33.01, 34.02 |
| Motion Responses | 21 days | CR 6.04 |
| MSJ Response | 21 days | CR 56.03 |

## Integration with Case Management

When creating events for cases:
1. Reference case folder: `/projects/{case-name}/`
2. Include case contacts from `contacts.json`
3. Reference deadlines from `overview.json`
4. Link to relevant documents in description

## Error Handling

If Calendar tools fail:
1. Check Google OAuth configuration: `GOOGLE_CREDENTIALS_FILE`
2. First-time use requires browser authentication
3. Verify timezone settings: `DEFAULT_TIMEZONE` env variable (defaults to America/New_York)

