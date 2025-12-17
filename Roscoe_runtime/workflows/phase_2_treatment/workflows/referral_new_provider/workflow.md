---
name: referral_new_provider
description: >
  Facilitate referral of client to a new medical provider, either from
  another provider's referral or based on case needs. This workflow
  handles provider selection, appointment coordination, and case file updates.
phase: treatment
workflow_id: referral_new_provider
related_skills:
  - calendar-scheduling (for scheduling appointments)
related_tools: []
templates:
  - templates/referral_note.md
---

# Referral to New Provider Workflow

## Overview

This workflow handles the process when a client needs to see a new medical provider. This can be triggered by a referral from an existing provider, identified need for specialist evaluation, or attorney/case strategy requirements.

**Workflow ID:** `referral_new_provider`  
**Phase:** `treatment`  
**Owner:** Agent/User (mixed)  
**Repeatable:** Yes

---

## Prerequisites

- Client in active treatment phase
- Need for additional provider identified
- Client consents to additional treatment

---

## Referral Sources

| Source | Example |
|--------|---------|
| Provider referral | PCP refers to orthopedic specialist |
| Case need | Need life care planner for catastrophic case |
| Client request | Client wants second opinion |
| Attorney strategy | Need specific type of documentation |

---

## Workflow Steps

### Step 1: Identify Referral Need

**Step ID:** `identify_need`  
**Owner:** Agent  
**Automatable:** Partial

**Action:**
Document why the new provider is needed.

**Collect:**
| Field | Description |
|-------|-------------|
| `referral_source` | Who/what identified the need |
| `referral_reason` | Why this provider type is needed |
| `specialty_needed` | Type of provider needed |
| `urgency` | How urgent is the referral |

**Common Referral Reasons:**
| Reason | Example |
|--------|---------|
| Specialist evaluation | Need orthopedic for suspected fracture |
| Second opinion | Client wants alternative treatment option |
| Specific treatment | Need physical therapy prescription |
| Documentation | Need IME or FCE for demand |
| Ongoing care | PCP referral to specialist |

---

### Step 2: Select Provider

**Step ID:** `select_provider`  
**Owner:** User  
**Automatable:** No

**Action:**
Select appropriate provider based on specialty, location, and case needs.

**Selection Criteria:**
| Factor | Consideration |
|--------|---------------|
| Specialty | Matches identified need |
| Location | Convenient for client |
| Insurance | Accepts client's health insurance (if applicable) |
| Reputation | Quality of care and documentation |
| Availability | Can see client in reasonable timeframe |
| Lien acceptance | Will treat on lien if needed |

**Agent Prompt to User:**
> "Client needs a {{specialty}} provider. Please select a provider and provide their contact information."

**Collect:**
- Provider name
- Contact information
- Specialty confirmation

---

### Step 3: Coordinate Appointment

**Step ID:** `coordinate_appointment`  
**Owner:** User/Client  
**Automatable:** No

**Action:**
Schedule appointment with the new provider.

**Options:**
| Method | Who Does It |
|--------|-------------|
| Client calls directly | Client |
| Office calls for client | Staff |
| Transfer referral | From referring provider |

**Agent Prompt to User:**
> "Please coordinate appointment with {{provider.name}} for {{client.name}}. Update with appointment date when scheduled."

**Track:**
- Appointment date
- Appointment time
- Any pre-appointment requirements

---

### Step 4: Add Provider to Case File

**Step ID:** `add_provider`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Add new provider to `medical_providers.json` using the `medical_provider_setup` workflow.

**Triggers:** `medical_provider_setup` workflow

**Initial Entry:**
```json
{
  "id": "provider_new",
  "name": "{{provider.name}}",
  "type": "{{specialty}}",
  "referral_source": "{{source}}",
  "referral_date": "{{today}}",
  "treatment": {
    "first_visit": null,
    "status": "pending_first_visit",
    "scheduled_date": "{{appointment_date}}"
  }
}
```

---

### Step 5: Follow Up on Appointment

**Step ID:** `follow_up`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
After scheduled appointment date, follow up to confirm visit occurred.

**Follow-Up Questions:**
- Did client attend the appointment?
- What was the provider's assessment?
- Is follow-up treatment recommended?
- Was additional referral made?

**Update Provider Status:**
- If attended: Update `first_visit` and `status` to `active`
- If not attended: Note reason, reschedule if needed

---

## Lien Treatment

For providers treating on a lien (no insurance):

### Letter of Protection
A Letter of Protection (LOP) may be needed:
1. Provider agrees to wait for payment from settlement
2. Firm sends LOP guaranteeing payment
3. Provider bills are tracked as liens

**LOP Template:** `forms/medical_records/letter_of_protection_TEMPLATE.md`

### Lien Considerations
| Factor | Impact |
|--------|--------|
| Total liens | May exceed settlement value |
| Provider requirements | Some require minimum settlement |
| Negotiability | Most providers will negotiate |

---

## Outputs

### Provider Entry Created
- New entry in `medical_providers.json`
- Status set to `pending_first_visit`

### Calendar Events
| Event | When |
|-------|------|
| Appointment reminder | Day before appointment |
| Post-appointment follow-up | Day after appointment |

---

## Completion Criteria

### Required
- Provider added to case file
- Appointment scheduled (or documented if client declined)

### Follow-Up Required
- Confirm appointment attended
- Update provider status

---

## State Updates

After referral complete, update `case_state.json`:
```json
{
  "provider_count": {{current + 1}},
  "pending_appointments": ["{{provider_id}}"],
  "last_referral_date": "{{today}}"
}
```

---

## Related Workflows

- **Triggered By:** Client check-in, provider recommendation, case evaluation
- **Triggers:** `medical_provider_setup`

---

## Skills Used

| Skill | Purpose |
|-------|---------|
| `calendar-scheduling` | Track appointment and follow-up |

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Client doesn't want to see specialist | Document refusal, note in file, consider impact on case |
| No providers in area | Expand search radius, consider telemedicine |
| Insurance won't cover | Discuss lien options, out-of-pocket, or case strategy |
| Long wait for appointment | Document wait time, consider alternatives |
| Provider won't accept lien | Try other providers or discuss case strength |

