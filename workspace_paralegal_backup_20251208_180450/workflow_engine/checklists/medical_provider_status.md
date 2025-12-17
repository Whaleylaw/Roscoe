# Medical Provider Status Tracking (Gap #10)

## Overview
Track treatment status across all providers to determine readiness for demand.

---

## Existing Data Fields (medical_providers.json)
- `date_treatment_started` - First visit date
- `date_treatment_completed` - Last visit date (null = still treating)
- `number_of_visits` - Total visits
- `medical_provider_notes` - Status notes

---

## Provider Status Definitions

| Status | Condition | Next Action |
|--------|-----------|-------------|
| **Active** | `date_treatment_completed` is null | Monitor via check-ins |
| **Complete** | `date_treatment_completed` is set | Request final records/bills |
| **Pending Setup** | No dates set | Send LOR, get started |
| **Unknown** | No recent check-in | Follow up with client |

---

## Status Review Process

### Weekly Status Check
For each case in treatment phase:

1. **List all providers** from medical_providers.json
2. **Check each provider:**
   - Treatment status (active/complete)
   - Records status (requested/received)
   - Bills status (requested/received)
3. **Flag issues:**
   - Active > 90 days without check-in
   - Complete but records not requested
   - Records requested > 30 days ago without receipt

---

## Status Derivation Logic

```python
def get_provider_status(provider):
    if provider.date_treatment_completed:
        if provider.date_medical_records_received:
            return "COMPLETE_WITH_RECORDS"
        elif provider.date_medical_records_requested:
            return "COMPLETE_AWAITING_RECORDS"
        else:
            return "COMPLETE_NEEDS_RECORDS"
    elif provider.date_treatment_started:
        return "ACTIVE"
    else:
        return "PENDING_SETUP"
```

---

## Treatment Complete Detection

### Signals Treatment May Be Complete
1. Client reports "done" or "discharged"
2. No visits in 30+ days
3. Provider note says "discharged" or "MMI"
4. Client referred elsewhere

### Verification Steps
1. Confirm with client during check-in
2. Check for final visit note in records
3. Verify no future appointments scheduled

---

## Gap Detection

### Treatment Gap (Potential Problem)
- No provider visits for 30+ days
- Client still has symptoms
- Could hurt case value

### Action for Gap
1. Document reason for gap
2. Encourage client to return to treatment if needed
3. Note in case file for demand narrative

---

## Readiness for Demand

### All Providers Must Be:
- [ ] Treatment status = complete
- [ ] Records received
- [ ] Bills received

### Case Ready for Demand When:
- All providers complete
- All records/bills received
- Client confirms no planned treatment
- Waiting period (2-3 weeks) after last treatment

