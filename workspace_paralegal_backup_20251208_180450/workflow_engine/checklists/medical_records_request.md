# Medical Records Request Checklist (Gap #11)

## Overview
Process for requesting and tracking medical records from providers.

---

## Existing Data Fields (medical_providers.json)
- `date_medical_records_requested` - When request was sent
- `date_medical_records_received` - When records arrived
- `medical_provider_notes` - Notes about requests/follow-ups

---

## When to Request Records

### Trigger Conditions
1. Provider added to case file
2. Client check-in shows provider discharged
3. Approaching demand preparation
4. 30+ days since treatment completed with no records

---

## Request Process

### Step 1: Prepare Request
```bash
# Generate medical records request letter
# Template: /forms/medical_requests/medical_records_request_TEMPLATE.md
```

**Required Information:**
- [ ] Provider name and address
- [ ] Client full name and DOB
- [ ] Date of accident
- [ ] Treatment date range
- [ ] HIPAA authorization attached

### Step 2: Send Request

**Preferred Methods (in order):**
1. **Provider Portal** - If available, use electronic request
2. **Fax** - Most common for medical offices
3. **Email** - If provider accepts
4. **Mail** - Last resort, use certified mail

**Track in Case File:**
- Update `date_medical_records_requested` = today's date
- Add note: "Records requested via [method]"

### Step 3: Follow-Up Schedule

| Days After Request | Action |
|-------------------|--------|
| 14 days | First follow-up call |
| 21 days | Second follow-up + written reminder |
| 30 days | Escalate - request supervisor/manager |
| 45 days | Consider subpoena if in litigation |

### Step 4: Receipt & Verification

When records arrive:
- [ ] Update `date_medical_records_received` = today's date
- [ ] Verify date range is complete
- [ ] Check for missing pages/visits
- [ ] File in case folder: `/[case]/medical_records/`
- [ ] Add note with page count and date range

---

## Template Usage

```markdown
# Medical Records Request Letter

**TO:** {{provider_name}}
       {{provider_address}}
       {{provider_fax}}

**RE:** Medical Records Request
        Patient: {{client_name}}
        DOB: {{client_dob}}
        DOA: {{accident_date}}

Please provide complete medical records for the above patient
for dates of service from {{accident_date}} to present.

Enclosed: HIPAA Authorization

{{attorney_signature_block}}
```

---

## Common Issues

### Missing Records
- Request specific missing dates
- Ask for "all records including but not limited to..."

### Provider Merged/Closed
- Check for successor organization
- Try state medical records repository

### Records Fee
- Many providers charge $0.50-1.00/page
- Hospitals may charge flat fee
- PIP may cover records fees

---

## Integration with Workflows

### After Records Received
1. → Medical chronology skill for analysis
2. → Check for additional referrals (new providers)
3. → Update demand materials checklist

### If Treatment Complete + Records Received
- Mark provider status: complete
- Proceed to demand preparation if all providers done

