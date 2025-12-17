# Client Check-in Checklist

## Overview
Bi-weekly client check-ins during treatment phase to track progress, identify new providers, and determine readiness for demand.

---

## Check-in Schedule

### Standard Frequency
- **Every 14 days** during active treatment
- Adjust based on case complexity or client preference

### Schedule Commands
```bash
# Schedule next check-in
python /Tools/client/checkin_tracker.py --case "{{case_name}}" --schedule --days 14

# Check if overdue
python /Tools/client/checkin_tracker.py --case "{{case_name}}" --status --pretty
```

---

## Standard Questions

Ask the client:

1. **Treatment Status**: "Are you still treating for your injuries?"
2. **Current Providers**: "Which providers are you currently seeing?"
3. **New Providers**: "Have you started with any new providers since we last spoke?"
4. **Discharged**: "Have you been discharged from any providers?"
5. **Pain Level**: "On a scale of 1-10, how would you rate your pain today?"
6. **Work Status**: "Are you currently working?"
7. **Upcoming Appointments**: "Do you have any upcoming appointments scheduled?"
8. **Other Updates**: "Is there anything else you'd like me to know about your treatment?"

---

## Recording Check-ins

### Basic Check-in (Still Treating)
```bash
python /Tools/client/checkin_tracker.py --case "{{case_name}}" \
  --checkin \
  --still-treating \
  --providers "Dr. Smith, PT Plus, Chiropractor" \
  --pain 6 \
  --notes "Continuing treatment, improving slowly" \
  --pretty
```

### New Provider Added
```bash
python /Tools/client/checkin_tracker.py --case "{{case_name}}" \
  --checkin \
  --still-treating \
  --providers "Dr. Smith, PT Plus" \
  --new-provider "Pain Management Associates" \
  --notes "Referred to pain management for injections" \
  --pretty
```

### Provider Discharged
```bash
python /Tools/client/checkin_tracker.py --case "{{case_name}}" \
  --checkin \
  --still-treating \
  --providers "Dr. Smith" \
  --discharged "PT Plus" \
  --notes "Completed PT course, continuing with PCP only" \
  --pretty
```

### Treatment Complete
```bash
python /Tools/client/checkin_tracker.py --case "{{case_name}}" \
  --checkin \
  --treatment-complete \
  --discharged "All providers" \
  --notes "Client reports full recovery, no further treatment planned" \
  --pretty
```

---

## Automatic Flags

The tool automatically detects these conditions:

| Flag | Meaning | Action Required |
|------|---------|-----------------|
| `NEW_PROVIDER` | Client started with new provider | Run provider setup workflow |
| `DISCHARGED` | Client finished with a provider | Request final records/bills |
| `TREATMENT_COMPLETE` | All treatment ended | Begin demand preparation |
| `HIGH_PAIN` | Pain level 8-10 | Document, consider additional treatment |
| `NOT_WORKING` | Client still out of work | Ensure wage loss documentation |
| `TREATMENT_GAP` | >30 days since check-in | Follow up immediately |

---

## Downstream Workflows

### When NEW_PROVIDER flagged:
1. Add provider to case file
2. Send Letter of Representation to provider
3. Add to records/bills request list

### When DISCHARGED flagged:
1. Request final records from provider
2. Request final itemized bill
3. Mark provider as "treatment complete" in case file

### When TREATMENT_COMPLETE flagged:
1. Verify all records/bills received
2. Request any missing records
3. Transition to demand preparation phase

### When NOT_WORKING flagged:
1. Verify wage loss documentation:
   - Off-work notes from doctor
   - Employer verification
   - Pay stubs (before and after accident)
2. Calculate lost wages

---

## Calendar Integration

### Create Recurring Check-in Reminders
```bash
python /Tools/calendar/calendar_add_event.py \
  --title "Client Check-in: {{client_name}}" \
  --date "{{next_checkin_date}}" \
  --case "{{case_name}}" \
  --category "check-in" \
  --notes "Bi-weekly treatment check-in"
```

---

## Review History

```bash
# View all check-ins for a case
python /Tools/client/checkin_tracker.py --case "{{case_name}}" --history --pretty
```

---

## Best Practices

1. **Be Consistent**: Check in every 2 weeks without fail
2. **Document Everything**: Record all provider changes and client statements
3. **Act on Flags**: When a flag is raised, complete the associated workflow
4. **Track Pain Trends**: Note if pain is improving, stable, or worsening over time
5. **Anticipate Discharge**: When client mentions "almost done" with a provider, prepare records request
6. **Coordinate Records**: When treatment ends, wait 2-3 weeks for final notes before requesting

---

## Phase Transition

When `TREATMENT_COMPLETE` flag is raised for 30+ days with no new treatment:

1. Confirm with client treatment is truly complete
2. Ensure all records/bills are received
3. Request any outstanding records with 14-day deadline
4. Transition case to `demand_in_progress` phase

