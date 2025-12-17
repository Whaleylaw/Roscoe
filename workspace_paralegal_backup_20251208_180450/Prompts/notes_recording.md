# Notes Recording Rules

## CRITICAL: Recording Notes and Activity

When recording ANY activity, work done, or notes about a case:

### Step 1: Write to Project-Specific notes.json FIRST

- Path: `projects/{case-name}/notes.json`
- Example: `projects/Abby-Sitgraves-MVA-07-13-2024/notes.json`

### Step 2: Update Master notes.json

- Path: `Database/master_lists/notes.json`
- This keeps both files in sync

### Note Format

```json
{
  "note": "Description of activity or work done",
  "time": "HH:MM:SS",
  "note_type": "File Organization|Research|Communication|Medical Records|Litigation|etc.",
  "author_name": "Roscoe (AI Paralegal)",
  "note_summary": "Brief one-line summary",
  "project_name": "Case-Name-Here",
  "last_activity": "YYYY-MM-DD",
  "applies_to_projects": ["Case-Name-Here"]
}
```

### Note Types

- `File Organization` - Organizing, moving, renaming files
- `Research` - Legal research, case law, internet searches
- `Communication` - Client/attorney/adjuster communications
- `Medical Records` - Medical records review, analysis, requests
- `Litigation` - Court filings, pleadings, discovery
- `Settlement` - Negotiations, demands, offers
- `Administrative` - General case management tasks

### Sync Rule

When updating ANY project-specific JSON, also update the corresponding master JSON in `Database/master_lists/`, and vice versa. Both should always reflect the same data for the case.

### Database Maintenance

When case information changes, update:
- `overview.json` - Update last_update timestamp, last_activity, current_status fields
- `case_information/` folder - Save updated case summaries and timelines when generated

