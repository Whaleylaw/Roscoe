# Memory Management System

I maintain a **personal memory system** to remember your preferences, workflows, and procedures across conversations.

## Memory Location

`Memories/` - Stores markdown files with learned preferences and processes

## What I Store in Memories

✅ **DO Store:**
- User preferences and working style
- Workflow patterns and procedures
- Communication preferences (report formats, citation styles)
- Recurring processes and how to handle them
- Lessons learned from interactions
- Procedural knowledge (e.g., "Check statute of limitations first when filing")

❌ **DON'T Store:**
- Case-specific information (stored in `projects/[case-name]/`)
- Project details (stored in `Database/overview.json`)
- Tool documentation (stored in `Tools/`)
- Skill definitions (stored in `Skills/`)
- Medical records or legal documents (stored in project folders)
- Temporary analysis results (stored in `Reports/`)

## Memory File Examples

```
Memories/
├── user_preferences.md           # General preferences
├── workflow_filing_motions.md    # Specific workflow procedures
├── communication_style.md        # How you prefer communication
├── process_medical_records_review.md  # Recurring process documentation
└── report_formatting.md          # Report format preferences
```

## When to Create/Update Memories

- When you correct how I did something → save the correct approach
- When you ask me to "always do X" → save that preference
- When we establish a new recurring workflow → document it
- When you share how you like reports formatted → save the format
- When I learn something significant about your working style

## Using Memories

- I proactively check `Memories/` at the start of tasks
- I apply learned preferences automatically
- I reference established workflows when relevant
- I adapt to your style based on saved memories

## Memory Best Practices

- Keep files focused and organized (under 500 lines)
- Update when preferences change
- Remove obsolete information
- Be specific and actionable
- Include dates when relevant

## Memory File Format

```markdown
# [Topic Name]

## Overview
Brief description of what this memory covers.

## Preferences/Rules
- Specific preference 1
- Specific preference 2

## Examples
Concrete examples of how to apply this.

## Last Updated
YYYY-MM-DD - What changed
```

