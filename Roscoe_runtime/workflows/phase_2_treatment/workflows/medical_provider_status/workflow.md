---
name: medical_provider_status
description: >
  Monitor and update treatment status for medical providers. Track whether
  client is still treating, has been discharged, or needs follow-up with
  each provider. This workflow helps identify when treatment is complete.
phase: treatment
workflow_id: medical_provider_status
related_skills: []
related_tools: []
templates:
  - templates/provider_status_summary.md
---

# Medical Provider Status Workflow

## Overview

This workflow monitors the treatment status of all medical providers and ensures the case file accurately reflects where the client stands with each provider. It helps identify when treatment is complete and the case is ready to move toward demand.

**Workflow ID:** `medical_provider_status`  
**Phase:** `treatment`  
**Owner:** Agent  
**Repeatable:** Yes (runs as needed)

---

## Prerequisites

- At least one provider in `medical_providers.json`
- Client available for status updates (via check-in or direct contact)

---

## When to Run

This workflow runs:
- During client check-ins
- When updating case status
- When evaluating for demand phase entry
- When records are received (may indicate discharge)

---

## Workflow Steps

### Step 1: Review Current Provider List

**Step ID:** `review_providers`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Review all providers in `medical_providers.json` and their current status.

**Provider Status Summary:**
```
| Provider | Type | First Visit | Last Visit | Status |
|----------|------|-------------|------------|--------|
| Norton ER | emergency | 01/15/24 | 01/15/24 | discharged |
| Dr. Smith | orthopedic | 01/20/24 | 03/15/24 | active |
| ABC PT | physical_therapy | 02/01/24 | ongoing | active |
```

---

### Step 2: Update Individual Provider Status

**Step ID:** `update_status`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
For each provider, determine and update current treatment status.

**Status Determination:**

| Indicator | Status | Action |
|-----------|--------|--------|
| Single visit (ER) | `discharged` | Mark complete |
| Client says "still going" | `active` | Update last_visit if known |
| Client says "done there" | `discharged` | Set discharge date |
| Referred to another provider | `referred_out` | Note referral, add new provider |
| Waiting for surgery | `on_hold` | Note pending procedure |
| Scheduled but not seen | `pending_first_visit` | Track appointment date |

**Updates to `medical_providers.json`:**
```json
{
  "treatment": {
    "status": "{{new_status}}",
    "last_visit": "{{date}}",
    "status_updated": "{{today}}",
    "notes": "{{status_notes}}"
  }
}
```

---

### Step 3: Identify Treatment Completion

**Step ID:** `check_completion`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Evaluate whether overall treatment is complete.

**Treatment Complete Indicators:**
- All providers have status `discharged` or `referred_out`
- Client reports "done treating"
- Client has reached MMI (Maximum Medical Improvement)
- Doctor has released client from care

**Treatment Complete Calculation:**
```python
active_providers = count where status == 'active'
if active_providers == 0:
    treatment_may_be_complete = True
```

**If Treatment May Be Complete:**
1. Confirm with client
2. Verify all records requested
3. Flag for demand phase evaluation

---

### Step 4: Flag Providers Needing Follow-Up

**Step ID:** `flag_followup`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Identify providers that need follow-up actions.

**Follow-Up Flags:**

| Condition | Flag | Action |
|-----------|------|--------|
| Status `active` but no update in 30+ days | Stale status | Confirm current status |
| Status `active` but records not requested | Missing records | Trigger records request |
| Status `discharged` but no records | Discharged no records | Trigger records request |
| Client stopped going but not discharged | Unclear status | Clarify with client |

---

## Status Types Reference

| Status | Description | Next Steps |
|--------|-------------|------------|
| `active` | Currently receiving treatment | Monitor, update visits |
| `discharged` | Treatment complete, released | Request records if not done |
| `referred_out` | Referred to another provider | Add new provider |
| `on_hold` | Treatment paused (awaiting procedure, etc.) | Monitor, check timing |
| `pending_first_visit` | Scheduled but not seen yet | Confirm appointment |
| `unknown` | Status needs clarification | Follow up with client |

---

## Outputs

### Status Updates
- Each provider's treatment status updated
- `status_updated` date refreshed

### Flags Generated
- Providers needing records requests
- Stale statuses needing confirmation
- Treatment complete indication

---

## Completion Criteria

### For Each Provider
- Status is current (updated within 30 days if active)
- Status is not `unknown`

### For Overall Treatment
- All providers have definitive status
- Treatment complete determination made

---

## State Updates

After status review, update `case_state.json`:
```json
{
  "provider_statuses": {
    "active": {{count}},
    "discharged": {{count}},
    "referred_out": {{count}},
    "pending": {{count}}
  },
  "treatment_complete": {{true/false}},
  "last_status_review": "{{today}}"
}
```

---

## Related Workflows

- **Triggered By:** `client_check_in`, manual review
- **Triggers:** `request_records_bills` (for discharged providers)
- **Contributes to:** Phase exit evaluation

---

## Skills Used

None - this workflow updates provider status data.

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Client unsure about provider status | Contact provider directly, check for recent appointments |
| Provider merged or closed | Research new location, update contact info |
| Client stopped treating against advice | Document, note for attorney, may affect case value |
| Multiple providers with same type | Ensure each has unique entry, track separately |
| Status keeps changing | Note pattern, may indicate ongoing treatment needs |

