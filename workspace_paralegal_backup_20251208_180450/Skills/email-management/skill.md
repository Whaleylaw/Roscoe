---
name: email-management
description: Use when managing case-related email communications - searching inbox, reading emails, sending messages, creating drafts for attorney review, and tracking email threads with clients, adjusters, and opposing counsel.
---

# Email Management Skill

This skill provides guidance for managing case-related email communications using Gmail tools.

## Available Tools

| Tool | Description |
|------|-------------|
| `search_emails` | Search inbox using Gmail syntax |
| `get_email` | Read full email content |
| `send_email` | Send an email |
| `create_draft` | Create draft for attorney review |
| `get_thread` | Get entire email conversation |
| `list_labels` | List available Gmail labels/folders |

## Gmail Search Syntax

Use Gmail's powerful search operators:

```
from:sender@email.com      # Emails from specific sender
to:recipient@email.com     # Emails to specific recipient
subject:keyword            # Keyword in subject line
has:attachment             # Emails with attachments
after:2024/01/01          # Emails after date
before:2024/12/31         # Emails before date
is:unread                 # Unread emails only
label:important           # Emails with specific label
"exact phrase"            # Exact phrase match
```

**Combine operators:**
```
from:adjuster@insurance.com subject:Wilson after:2024/06/01
```

## Best Practices for Legal Email Management

### 1. Case Correspondence Search

When asked about case communications:
1. Search by case name: `subject:"Wilson MVA" OR subject:"Wilson case"`
2. Search by key contacts: `from:adjuster@statefarm.com`
3. Search by date range: `after:2024/06/01 before:2024/12/31`

### 2. Client Communications

ALWAYS exercise caution with client emails:
- **Before sending**: Confirm attorney approval for sensitive communications
- **Settlement discussions**: Create drafts for attorney review first
- **Demand letters**: ALWAYS create draft, never send directly

### 3. Insurance Adjuster Communications

Track correspondence with adjusters:
```
# Find all communications with State Farm adjuster
from:adjuster@statefarm.com OR to:adjuster@statefarm.com

# Find settlement-related emails
subject:settlement OR subject:offer OR subject:demand
```

### 4. Medical Records Requests

Track medical records correspondence:
```
# Hospital records communications
from:medicalrecords@hospital.com OR subject:"medical records"

# Track outstanding requests
subject:"records request" is:unread
```

## Email Workflow Patterns

### Pattern 1: Case Status Review

When reviewing case communications:
```
1. search_emails("subject:'{client_name}' after:{settlement_start_date}")
2. Review snippets for relevant threads
3. get_thread(thread_id) for important conversations
```

### Pattern 2: Demand Letter Follow-up

Track demand letter responses:
```
1. search_emails("subject:demand to:adjuster@insurance.com after:{demand_date}")
2. Check for responses within 30-day window
3. Create follow-up draft if no response
```

### Pattern 3: Client Update

Send case status update:
```
1. create_draft(to="client@email.com", subject="Case Update - {case_name}", body="...")
2. Notify attorney draft is ready for review
3. Once approved, send_email(...) or send from Gmail directly
```

## Email Categories for Personal Injury Cases

| Category | Search Query | Purpose |
|----------|--------------|---------|
| Insurance | `from:@statefarm.com OR from:@geico.com` | Adjuster communications |
| Medical | `from:@hospital.com OR subject:"medical records"` | Records requests/responses |
| Client | `from:{client_email}` | Client correspondence |
| Lien Holders | `from:@medicare.gov OR subject:lien` | Lien notices |
| Attorney | `from:{attorney_email}` | Firm communications |

## Security Notes

- **Privileged Communications**: Do not forward attorney-client communications without approval
- **HIPAA**: Be cautious with medical information in emails
- **Settlement Offers**: All settlement communications should go through attorney
- **Opposing Counsel**: Never communicate directly with opposing counsel without attorney approval

## Error Handling

If Gmail tools fail:
1. Check if Google OAuth is configured: `GOOGLE_CREDENTIALS_FILE` environment variable
2. First-time use requires browser authentication
3. Token may need refresh after 7 days of inactivity

