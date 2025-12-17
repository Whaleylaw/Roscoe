---
name: send_demand
description: >
  Send the approved demand letter and package to insurance adjuster(s).
  This workflow identifies recipients, coordinates sending, notifies the
  client, and sets up follow-up tracking.
phase: demand_in_progress
workflow_id: send_demand
related_skills:
  - skills/calendar-scheduling/skill.md
related_tools:
  - calendar_add (Google Calendar integration)
templates:
  - templates/demand_tracking.md
---

# Send Demand Workflow

## Overview

This workflow handles sending the approved demand package to all appropriate recipients, notifying the client, and establishing follow-up tracking. Completion of this workflow triggers the phase transition to Negotiation.

**Workflow ID:** `send_demand`  
**Phase:** `demand_in_progress`  
**Owner:** Agent/User (mixed)  
**Repeatable:** No

---

## Prerequisites

- `draft_demand` workflow complete
- Demand letter approved by attorney
- Complete demand package ready

---

## Workflow Steps

### Step 1: Identify Recipients

**Step ID:** `identify_recipients`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Determine who should receive the demand.

**Logic:**
```
For each BI claim in insurance.json:
    If defense_attorney exists:
        Primary recipient = defense_attorney
        CC = adjuster
    Else:
        Primary recipient = adjuster
```

**Recipients List:**

| Recipient Type | When | Method |
|----------------|------|--------|
| BI Adjuster | No attorney | Direct to adjuster |
| Defense Attorney | Attorney involved | To attorney, cc adjuster |
| UM Carrier | UM claim | Same as BI |

**Agent Action:**
> "Identifying demand recipients. Demand will be sent to all BI adjusters."

**Output:**
```json
{
  "demand_recipients": [
    {
      "claim_id": "bi_001",
      "recipient": "{{adjuster_name}}",
      "company": "{{carrier}}",
      "email": "{{email}}",
      "address": "{{address}}"
    }
  ]
}
```

---

### Step 2: Send Demand Package

**Step ID:** `send_demand`  
**Owner:** User  
**Automatable:** No

**Action:**
Send the demand package via appropriate method.

**Sending Methods:**

| Method | Best For | Notes |
|--------|----------|-------|
| Certified Mail | Primary method | Proof of delivery |
| Email | Quick delivery | Follow up with hard copy |
| Fax | Immediate delivery | Less common now |
| eFile/Portal | Defense attorney | If they have portal |

**Recommended:** Send via certified mail AND email for confirmation.

**Agent Prompt to User:**
> "Please send the demand package to {{adjuster.name}} at {{adjuster.email}} or via certified mail. Track the certified mail number."

**For Each Recipient:**
1. Send demand letter
2. Include all exhibits
3. Record tracking information

**Updates:**
```json
{
  "insurance_claims[].demand_sent_date": "{{today}}",
  "insurance_claims[].demand_amount": {{amount}},
  "insurance_claims[].demand_sent_method": "certified_mail",
  "insurance_claims[].demand_tracking": "{{tracking_number}}"
}
```

---

### Step 3: Notify Client

**Step ID:** `notify_client`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Inform client that the demand has been sent.

**Message Template:**
> "Good news - we've sent the demand letter to {{insurance_company}} on {{date}}. 
> We demanded {{demand_amount}} based on your medical treatment and injuries.
> Insurance companies typically respond within 30 days. 
> I'll keep you updated on any offers or responses."

**Contact Method:** Use `client.preferred_contact`

**Agent Action:**
> "Notifying client that demand was sent to {{carrier}}."

**Updates:**
```json
{
  "demand_client_notification_date": "{{today}}"
}
```

---

### Step 4: Set Follow-Up Calendar

**Step ID:** `set_follow_up`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Schedule follow-up if no response received.

**Skill:** `Skills/calendar-scheduling/SKILL.md`  
**Tool:** `calendar_add`  
**Tool Available:** ✅ Yes

**Follow-Up Schedule:**

| Event | Days After | Purpose |
|-------|------------|---------|
| One-week check | +7 days | Confirm receipt |
| 30-day follow-up | +30 days | If no response |

**Calendar Events:**
```json
[
  {
    "title": "Demand Follow-Up: {{client.name}} - Confirm Receipt",
    "date": "{{demand_sent_date + 7 days}}",
    "type": "demand_followup",
    "description": "Confirm {{carrier}} received demand. Contact adjuster if no acknowledgment."
  },
  {
    "title": "Demand Follow-Up: {{client.name}} - 30 Day",
    "date": "{{demand_sent_date + 30 days}}",
    "type": "demand_followup",
    "description": "30 days since demand sent to {{carrier}}. Follow up if no response."
  }
]
```

**Agent Action:**
> "Follow-up scheduled for {{date}} if no response received."

---

## Demand Package Contents

When sending, include:

| Item | Required | Notes |
|------|----------|-------|
| Demand letter | Yes | Final approved version |
| Medical records | Yes | All providers |
| Medical bills | Yes | Itemized |
| Medical chronology | Yes | Summary document |
| Accident report | If available | Police/crash report |
| Photos | If available | Vehicle, injuries, scene |
| Wage loss docs | If applicable | Supporting lost wages |

---

## Outputs

### Actions Completed
- Demand sent to all BI adjusters
- Client notified
- Follow-up events scheduled

### Data Updates
- `insurance_claims[].demand_sent_date` updated
- `insurance_claims[].demand_amount` recorded

### Phase Transition
**→ Triggers entry to `negotiation` phase**

---

## Completion Criteria

### Required
- `demand_sent_to_all_bi_adjusters == true`

### Recommended
- Client notified
- Follow-up scheduled

---

## State Updates

On completion, update `case_state.json`:
```json
{
  "workflows": {
    "send_demand": {
      "status": "complete",
      "completed_date": "{{today}}",
      "recipients": ["{{carrier_1}}", "{{carrier_2}}"],
      "client_notified": true,
      "followup_scheduled": true
    }
  },
  "current_phase": "negotiation"
}
```

---

## Related Workflows

- **Triggered By:** `draft_demand` (approval)
- **Triggers:** Phase transition to `negotiation`

---

## Skills & Tools

| Resource | Purpose | Location |
|----------|---------|----------|
| `calendar-scheduling` | Schedule follow-up events | `skills/calendar-scheduling/skill.md` |
| `demand_tracking` | Track demand status | `templates/demand_tracking.md` |

---

## Multiple BI Claims

If case has multiple BI claims (multiple at-fault parties):
- Send separate demand to each adjuster
- May have different demand amounts per claim
- Track responses separately
- May negotiate in parallel

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Adjuster contact info changed | Call claims department to verify |
| Email bounces | Use certified mail, call to verify |
| File too large for email | Use file sharing service or send CD |
| Defense attorney involved | Send to attorney, cc adjuster |
| No acknowledgment | Follow up at 7 days, document attempts |

