---
name: serve_defendant
description: >
  Serve complaint and summons on all defendants. Coordinates service of process,
  tracks attempts, files proof of service, and calendars answer deadlines.
  Use after complaint filed and summons issued.
phase: 7.1_complaint
workflow_id: serve_defendant
related_skills:
  - service-of-process
templates:
  - service_tracking.md
---

# Serve Defendant Workflow

## Overview

Manage service of process on all defendants, tracking attempts and filing proof of service.

## Entry Criteria

- Complaint filed with court
- Summons issued for each defendant
- Defendant addresses available

## Steps

### 1. Select Service Method

**Owner:** User  
**Skill:** `service-of-process`  
**Action:** Determine appropriate service method per defendant.

### 2. Arrange Service

**Owner:** User  
**Action:** Contact sheriff or process server.

### 3. Track Attempts

**Owner:** Agent  
**Action:** Document each service attempt with date, method, result.

### 3.5. Evaluate Service Failures (If Applicable)

**Owner:** User/Agent  
**Action:** If 2+ service attempts have failed, consider alternative methods:

```
┌─────────────────────────────────┐
│  Service failed 2+ times?       │
└──────────────┬──────────────────┘
               │
        ┌──────┴───────┐
        │              │
        ▼              ▼
  ┌─────────────┐ ┌─────────────┐
  │ Defendant   │ │ Defendant   │
  │ evading?    │ │ location    │
  │             │ │ unknown?    │
  └─────┬───────┘ └──────┬──────┘
        │                │
        ▼                ▼
  Special Bailiff   Warning Order
  (Jefferson Co.)   (CR 4.05)
```

**Special Bailiff Option (Jefferson County):**
1. Prepare `special_bailiff_affidavit.md` documenting failed attempts
2. Prepare `special_bailiff_order.md` for judge signature
3. File motion with court
4. Once signed, coordinate with appointed Special Bailiff

**Warning Order Option (Unknown Location):**
1. Document all search efforts
2. File motion for warning order
3. Follow publication requirements

See `service-of-process/references/service-methods.md` for detailed guidance.

### 4. File Proof of Service

**Owner:** User  
**Action:** File proof of service with court for each served defendant.

### 5. Calendar Answer Deadline

**Owner:** Agent  
**Action:** Calculate 20-day answer deadline and create calendar event.

## Exit Criteria (Per Defendant)

For each defendant:
- [ ] Defendant served
- [ ] Proof of service filed
- [ ] Answer deadline calendared (20 days from service)

**Effect:** Once a defendant is served, their track advances to `process_answer`. Other defendants may still be pending service.

**Workflow remains active** until all defendants are served.

## Templates

| Template | Purpose |
|----------|---------|
| `service_tracking.md` | Track service attempts by defendant |
| `special_bailiff_affidavit.md` | Affidavit of good cause for Special Bailiff |
| `special_bailiff_order.md` | Proposed order appointing Special Bailiff |

## Related Workflows

- **Triggered By:** `draft_file_complaint`
- **Triggers:** `process_answer`

