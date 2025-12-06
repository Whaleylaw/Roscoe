# Workflow: Client Intake & Screening

## Phase: intake
## Goal: Complete initial client consultation, conflicts check, and case acceptance decision

---

## When to Trigger

- New potential client contacts office
- User says "new client", "intake", "consultation"
- Beginning work on a newly accepted case

---

## Inputs Required

- Client contact information
- Basic incident details
- Referral source (if any)

---

## Step-by-Step Process

### Step 1: Initial Contact Documentation
1. Record client's full legal name
2. Get contact information (phone, email, address)
3. Note date and time of initial contact
4. Record referral source

### Step 2: Conflicts Check
**Use skill: conflicts-check**

1. Search existing client database for:
   - Client name variations
   - Adverse parties mentioned
   - Related parties
2. Check against current opposing parties
3. Document conflicts check result

### Step 3: Preliminary Case Information
**Use skill: fact-investigation**

Gather essential facts:
- Date of incident
- Location of incident
- Type of incident (MVA, slip/fall, etc.)
- Brief description of what happened
- Injuries claimed
- Medical treatment to date
- Other parties involved
- Insurance information (if known)

### Step 4: Initial Case Evaluation
Assess case viability:
- Clear liability indicators?
- Significant injuries?
- Insurance coverage likely?
- Statute of limitations status?
- Venue considerations?

### Step 5: Decision Point
Based on evaluation:
- **Accept**: Proceed to document signing
- **Decline**: Send non-engagement letter
- **Further Review**: Schedule attorney consultation

### Step 6: Document Decision
1. Create intake record in case management
2. If accepted, create case folder
3. If declined, document reason and send letter

---

## Skills Used

- **conflicts-check**: Verify no conflicts of interest
- **fact-investigation**: Gather incident details
- **client-communication**: Professional intake communication

---

## Completion Criteria

- [ ] Client information recorded
- [ ] Conflicts check completed and cleared
- [ ] Basic incident facts gathered
- [ ] Case viability assessed
- [ ] Accept/decline decision made
- [ ] Appropriate follow-up initiated

---

## Outputs

- `intake_form.json` - Structured intake data
- `conflicts_check.json` - Conflicts check documentation
- Case folder (if accepted)
- Non-engagement letter (if declined)

---

## Phase Exit Contribution

This workflow contributes to:
- `client_documents_signed` (when paired with initial_documentation)

---

## Intake Form Structure

```json
{
  "client": {
    "name": "",
    "dob": "",
    "ssn_last4": "",
    "address": "",
    "phone": "",
    "email": ""
  },
  "incident": {
    "date": "",
    "location": "",
    "type": "",
    "description": ""
  },
  "injuries": [],
  "treatment_to_date": [],
  "other_parties": [],
  "insurance_known": {},
  "referral_source": "",
  "intake_date": "",
  "intake_by": ""
}
```

