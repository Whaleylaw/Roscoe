---
name: client_check_in
description: >
  Bi-weekly check-in with client during treatment to monitor their medical progress,
  identify new providers, gather updates on treatment status, and maintain the
  attorney-client relationship. This is a recurring workflow until demand is sent.
phase: treatment
workflow_id: client_check_in
related_skills:
  - skills/calendar-scheduling/skill.md
related_tools:
  - calendar_add (Google Calendar integration)
templates:
  - templates/check_in_note.md
recurring: true
frequency_days: 14
until_condition: demand_sent
---

# Client Check-In Workflow

## Overview

The Client Check-In workflow maintains regular contact with the client during the treatment phase. These bi-weekly check-ins ensure we stay informed about their medical progress, identify any new providers or treatment changes, and maintain a strong attorney-client relationship.

**Workflow ID:** `client_check_in`  
**Phase:** `treatment`  
**Owner:** Agent  
**Repeatable:** Yes (recurring every 14 days)  
**Frequency:** Every 14 days  
**Continues Until:** Demand sent

---

## Prerequisites

- Case in Treatment phase
- Client contact information available
- Last check-in was 14+ days ago (or first check-in)

---

## Recurring Schedule

```
Treatment Start → Check-in → 14 days → Check-in → 14 days → ... → Demand Sent
```

---

## Workflow Steps

### Step 1: Contact Client

**Step ID:** `contact_client`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Reach out to client for status update using their preferred contact method.

**Contact Method:** Use `client.preferred_contact` from overview.json
- Phone call
- Text message  
- Email

**Standard Check-In Questions:**
1. "Are you still treating with your medical providers?"
2. "Have you seen any new doctors or specialists?"
3. "Any new symptoms or changes in your condition?"
4. "Have you been able to return to work?"
5. "Any updates on [outstanding items from File Setup]?"

**Additional Questions (situational):**
- "How are you feeling overall?"
- "Any concerns about your treatment?"
- "Have you received any correspondence from insurance?"
- "Any changes to your contact information?"

**Agent Prompt:**
> "Time for bi-weekly client check-in. I'll prepare questions based on their current treatment status."

---

### Step 2: Document Responses

**Step ID:** `document_responses`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Record client's responses and update case file.

**Updates:**
- `last_client_contact` → Today's date
- `notes` → Add check-in summary

**Check-In Note Format:**
```
## Client Check-In - {{date}}

**Treatment Status:**
- Currently treating at: [providers]
- New providers since last check-in: [if any]

**Condition Update:**
- Client reports: [summary of how they're feeling]
- New symptoms: [if any]
- Symptom improvements: [if any]

**Work Status:**
- Currently working: Yes/No/Modified
- Missed work since last check-in: [days/hours]

**Outstanding Items:**
- [Status of any pending items]

**Next Steps:**
- [Any actions identified]

**Next Check-In:** {{date + 14 days}}
```

**Data Targets:**
- `Case Information/overview.json` → `last_client_contact`
- `Case Information/notes.json` → Add new note entry

---

### Step 3: Trigger New Provider Workflow (Conditional)

**Step ID:** `trigger_new_provider`  
**Owner:** Agent  
**Automatable:** Yes  
**Conditional:** If client mentions new provider

**Condition:**
```
client_mentioned_new_provider == true
```

**Action:**
If client mentions seeing a new provider, trigger the medical provider setup workflow.

**Triggers:** `medical_provider_setup` workflow

**Agent Action:**
> "Client mentioned a new provider. I'll add them to the case file."

---

### Step 4: Schedule Next Check-In

**Step ID:** `schedule_next`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Add next check-in to calendar (14 days from today).

**Tool:** `calendar_add`  
**Tool Available:** ✅ Yes

**Calendar Event:**
```json
{
  "title": "Client Check-In: {{client.name}}",
  "date": "{{today + 14 days}}",
  "type": "client_check_in",
  "case_id": "{{case_id}}",
  "description": "Bi-weekly check-in with {{client.name}} re: {{accident.date}} accident"
}
```

**Agent Action:**
> "Next check-in scheduled for {{date + 14 days}}."

---

## Treatment Status Detection

During check-in, listen for indicators of treatment completion:

### Treatment Continuing
- "I'm still going to physical therapy"
- "I have another appointment next week"
- "The doctor wants to see me again"

### Treatment Complete Indicators
- "I've been discharged"
- "The doctor said I'm done"
- "I'm not going back"
- "I've reached MMI" (Maximum Medical Improvement)

**If treatment appears complete:**
1. Confirm with client
2. Update provider statuses
3. Notify that case may be ready for demand phase

---

## Outstanding Items Follow-Up

Check-ins should follow up on:

| Item | Question |
|------|----------|
| Unsigned documents | "Have you had a chance to sign the documents we sent?" |
| Missing insurance info | "Were you able to find your insurance card?" |
| Wage loss docs | "Have you gotten the wage verification from your employer?" |
| Police report | "Did you receive the police report?" |

---

## Outputs

### Case Updates
- `last_client_contact` updated
- Check-in note added to case file

### Workflows Triggered
| Condition | Workflow |
|-----------|----------|
| New provider mentioned | `medical_provider_setup` |
| Treatment complete | Evaluation for `demand_in_progress` entry |

### Calendar Events
| Event | Description |
|-------|-------------|
| Next check-in | +14 days from today |

---

## Completion Criteria

### Required
- `last_client_contact` updated to today

### Documentation
- Check-in note recorded in notes.json

---

## State Updates

After each check-in, update `case_state.json`:
```json
{
  "last_client_contact": "{{today}}",
  "check_in_count": {{current + 1}},
  "next_check_in_due": "{{today + 14 days}}",
  "treatment_status": "{{active/complete/unknown}}"
}
```

---

## Related Workflows

- **Triggers:** `medical_provider_setup` (if new provider)
- **Contributes to:** Phase exit evaluation (treatment complete detection)

---

## Skills & Resources

| Resource | Purpose | Location |
|----------|---------|----------|
| `calendar-scheduling` | Schedule next check-in | `skills/calendar-scheduling/skill.md` |
| `check_in_note` | Document check-in results | `templates/check_in_note.md` |

---

## Client Contact Guidelines

### Contact Frequency
| Days Since Last Contact | Status |
|-------------------------|--------|
| 0-14 days | On schedule |
| 15-30 days | Overdue - prioritize contact |
| 31-60 days | Warning - document attempts |
| 60+ days | Critical - attorney notification |

### Best Practices
- Use client's preferred contact method
- Leave voicemail with callback number
- Follow up voicemail with text/email
- Document all contact attempts
- Be genuinely interested in their wellbeing

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Client not responding | Try all contact methods. Send certified letter if 30+ days. |
| Client frustrated with timeline | Explain process, set expectations, involve attorney if needed |
| Client treating with unauthorized provider | Gather info, note for attorney review |
| Client wants to settle immediately | Explain value of completing treatment, involve attorney |
| Client moved/changed number | Update contact info, note in file |

