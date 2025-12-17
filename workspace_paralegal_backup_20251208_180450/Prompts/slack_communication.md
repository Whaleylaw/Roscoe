# Slack Communication Guidelines

When a message includes `[SLACK CONVERSATION]` context, the user is communicating via Slack.

## Key Principles

- Your initial response automatically goes to Slack (handled by the system)
- For **long-running tasks** (file organization, analysis, research), use `send_slack_message` to provide progress updates
- When tasks complete or encounter issues, use `send_slack_message` to notify the user
- The default channel is #legal-updates unless the conversation context specifies otherwise

## Urgency Levels

| Level | Use For |
|-------|---------|
| `normal` | Progress updates, routine notifications |
| `high` | Concerns, issues needing attention |
| `urgent` | Critical issues, immediate action needed |

## When to Use send_slack_message

- Progress updates during multi-step workflows (e.g., "Starting Phase 2 of file organization...")
- Task completion notifications (e.g., "Medical records analysis complete")
- Red flags or issues discovered during work
- Results summaries after lengthy operations
- Any time the user should be notified asynchronously

## Examples

```python
# Progress update during long task
send_slack_message(
    "📂 Phase 1 complete: Created directory structure for McCay case",
    urgency="normal"
)

# Issue discovered
send_slack_message(
    "⚠️ Found 5 files with unclear categorization - will need your review",
    urgency="high"
)

# Task completion
send_slack_message(
    "✅ File reorganization complete! 177 files processed.",
    urgency="normal"
)

# Critical issue
send_slack_message(
    "🚨 Statute of limitations expires in 3 days for Wilson case!",
    urgency="urgent"
)
```

## Message Formatting

- Use emojis sparingly for visual clarity
- Keep messages concise but informative
- Include case name when relevant
- Provide actionable information
- For long results, summarize key points rather than dumping raw data

