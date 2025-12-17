---
name: close_case
description: >
  Final case closure and archiving. This workflow verifies all obligations
  are complete, sends final letter to client, requests review if appropriate,
  and archives the case file.
phase: closed
workflow_id: close_case
related_skills:
  - document-docx
related_tools: []
templates:
  - forms/closing/case_closing_letter_TEMPLATE.md
---

# Close Case Workflow

## Overview

This workflow handles the final closure of the case, including verification of completion, client communication, and file archival. This is the terminal workflow for successful cases.

**Workflow ID:** `close_case`  
**Phase:** `closed`  
**Owner:** Agent/User (mixed)  
**Repeatable:** No

---

## Prerequisites

- All settlement/verdict funds distributed
- All liens paid
- Client received their funds
- No outstanding obligations

---

## Workflow Steps

### Step 1: Verify All Complete

**Step ID:** `verify_complete`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Confirm all case obligations have been fulfilled.

**Verification Checklist:**
- [ ] Settlement/verdict amount received
- [ ] All liens paid
- [ ] Client received net distribution
- [ ] Trust account balance is zero
- [ ] All releases signed (if applicable)
- [ ] All court requirements satisfied (if litigation)

**Agent Action:**
> "Verifying case completion. Checking: funds distributed, liens paid, trust account zeroed."

**If Issues Found:**
- Flag incomplete items
- Route for resolution before proceeding

---

### Step 2: Send Final Letter

**Step ID:** `send_final_letter`  
**Owner:** User  
**Automatable:** No

**Action:**
Send closing letter to client.

**Template:** `forms/closing/case_closing_letter_TEMPLATE.md`

**Letter Contents:**
- Thank client for choosing the firm
- Summarize case outcome
- Advise files are available if needed
- Mention file retention period (5 years)
- Encourage future contact if needed
- Request review (if appropriate)

**Agent Prompt to User:**
> "Send final letter to client thanking them and confirming case is closed."

**Updates:**
```json
{
  "closure.final_letter_sent_date": "{{today}}"
}
```

---

### Step 3: Request Review (Conditional)

**Step ID:** `request_review`  
**Owner:** User  
**Automatable:** No  
**Conditional:** Good outcome AND good relationship

**Action:**
Request Google review from satisfied client.

**Criteria for Requesting:**
- ✅ Good case outcome
- ✅ Good client relationship throughout
- ✅ Client expressed satisfaction
- ✅ No significant issues during representation

**Do NOT Request If:**
- ❌ Poor outcome
- ❌ Client expressed dissatisfaction
- ❌ Contentious relationship
- ❌ Case declined (no representation provided)

**Agent Prompt to User:**
> "If appropriate, request a Google review from the client."

**Updates:**
```json
{
  "closure.review_requested": true,
  "closure.review_requested_date": "{{today}}"
}
```

---

### Step 4: Archive File

**Step ID:** `archive_file`  
**Owner:** User  
**Automatable:** No

**Action:**
Archive both physical and digital files.

**Physical File Archive:**
1. Compile all original documents
2. Remove duplicates and non-essential copies
3. Organize in archive folders
4. Label with: case name, number, closure date
5. Store in archive location
6. Log in archive database

**Digital File Archive:**
1. Ensure all documents saved to case folder
2. Export from case management if needed
3. Backup to archive storage
4. Verify backup integrity
5. Mark case as archived in system

**Retention Period:** 5 years minimum (longer for minors)

**Agent Prompt to User:**
> "Archive the physical and digital file. Retain for minimum 5 years."

**Updates:**
```json
{
  "closure.archived_date": "{{today}}",
  "closure.archive_location": "{{location}}",
  "closure.retention_until": "{{today + 5 years}}",
  "case_state.status": "closed"
}
```

---

## Outputs

### Actions Completed
- Completion verified
- Final letter sent
- Review requested (if appropriate)
- File archived

### Case Status
- `case_state.status = "closed"`

---

## Completion Criteria

### Required
- `file_archived == true`

### Full Closure
- All verification items complete
- Final letter sent
- Archive complete

---

## State Updates

On completion, update `case_state.json`:
```json
{
  "current_phase": "closed",
  "status": "closed",
  "closure": {
    "completed_date": "{{today}}",
    "final_letter_sent": true,
    "review_requested": {{true/false}},
    "archived": true,
    "archive_location": "{{location}}",
    "retention_until": "{{date}}"
  }
}
```

---

## Related Workflows

- **Triggered By:** Settlement complete OR verdict rendered
- **Triggers:** None (terminal workflow)

---

## Skills Used

| Skill | Purpose |
|-------|---------|
| `document-docx` | Generate closing letter |

---

## Reopening Cases

### Can Reopen If:
- Client returns with new related matter
- Additional insurance coverage discovered
- Appeal or post-judgment matter

### Cannot Reopen If:
- Settlement fully completed
- Judgment satisfied

### To Reopen:
1. Create new case linked to original
2. Reference original case number
3. Import relevant documents from archive

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Outstanding item found | Resolve before archiving |
| Client unresponsive for final letter | Send via mail, document |
| Archive space issue | Follow firm archive procedures |
| Client requests documents after close | Retrieve from archive, charge if allowed |

