# Medical Provider Setup Checklist (Gap #8)

## Overview
Process for adding and setting up new medical providers in a case.

---

## Trigger: When to Add Provider

1. Client mentions new provider during check-in
2. Police report shows EMS/ER
3. Records show referral to specialist
4. Client provides new provider info

---

## Setup Process

### Step 1: Collect Provider Information
- [ ] Provider full name
- [ ] Provider type (ER, PCP, Chiropractor, PT, Specialist, etc.)
- [ ] Address
- [ ] Phone/Fax
- [ ] First visit date

### Step 2: Add to Case File
Add entry to medical_providers with:
```json
{
  "project_name": "{{case_name}}",
  "provider_full_name": "{{provider_name}}",
  "date_treatment_started": "{{first_visit_date}}",
  "date_treatment_completed": null,
  "medical_provider_notes": "Added {{today_date}}"
}
```

### Step 3: Send Letter of Representation
- [ ] Generate LOR from template
- [ ] Include HIPAA authorization
- [ ] Send via fax/mail
- [ ] Note in provider record

### Step 4: Add to Master Directory (if new)
If provider not in directory:
- [ ] Add to Database/directory.json
- [ ] Include contact info, fax, address

---

## Provider Types

| Type | Abbreviation | Notes |
|------|--------------|-------|
| Emergency Room | ER | Usually one-time visit |
| Primary Care | PCP | May be ongoing |
| Chiropractor | Chiro | Often extended treatment |
| Physical Therapy | PT | Usually prescribed course |
| Orthopedic | Ortho | Specialist referral |
| Pain Management | PM | Often injections |
| Neurologist | Neuro | For head/nerve injuries |
| Surgeon | Surg | If surgery needed |
| Imaging | MRI/CT | Diagnostic only |
| EMS/Ambulance | EMS | Transport only |

---

## Template: LOR to Provider

```markdown
RE: Letter of Representation
    Patient: {{client_name}}
    DOB: {{client_dob}}
    DOA: {{accident_date}}

Dear Provider:

Please be advised that this office represents {{client_name}}
regarding injuries sustained on {{accident_date}}.

Please direct all correspondence regarding this patient
to our office.

Enclosed: HIPAA Authorization

{{attorney_signature_block}}
```

---

## PIP Billing Setup

If client has PIP coverage:
- [ ] Provide PIP carrier info to provider
- [ ] Provider bills PIP directly
- [ ] Track PIP payments

---

## Follow-Up

### Initial Setup
- Confirm provider received LOR
- Verify they have correct billing info

### Ongoing
- Track treatment status via client check-ins
- Request records when treatment complete

