# Workflow: Medical Records Request

## Phase: treatment
## Goal: Request and track medical records and bills from all providers

---

## When to Trigger

- After HIPAA authorizations obtained
- When new provider is identified
- When follow-up needed on outstanding requests
- User asks about records status

---

## Inputs Required

- Signed HIPAA authorizations
- List of medical providers
- Client's full name and DOB
- Date of incident

---

## Step-by-Step Process

### Step 1: Compile Provider List
**Use skill: medical-record-request**

From intake and client communications:
1. Emergency room / hospital
2. Primary care physician
3. Specialists (orthopedic, neurologist, etc.)
4. Physical therapy
5. Chiropractor
6. Imaging centers
7. Ambulance service
8. Pharmacy (for prescription records)

### Step 2: Gather Provider Contact Info
For each provider:
1. Full facility name
2. Medical records department contact
3. Phone and fax numbers
4. Mailing address
5. Online portal (if available)
6. Preferred request method

### Step 3: Prepare Record Requests
For each provider, prepare request including:
1. Cover letter
2. HIPAA authorization
3. Specific date range (DOS to present)
4. Request for:
   - Complete medical records
   - Itemized billing statements
   - Radiology images (if applicable)

### Step 4: Send Requests
1. Send via provider's preferred method
2. Track delivery confirmation
3. Note date sent
4. Set follow-up reminder (2-3 weeks)

### Step 5: Update Tracking System
Create/update `medical_providers.json`:
```json
{
  "providers": [
    {
      "name": "",
      "type": "hospital|specialist|pt|chiro|pcp|imaging",
      "contact": {},
      "records": {
        "requested": "date",
        "received": null,
        "status": "pending|received|incomplete|follow_up"
      },
      "bills": {
        "requested": "date", 
        "received": null,
        "status": "pending|received|incomplete|follow_up",
        "amount": null
      },
      "notes": ""
    }
  ]
}
```

### Step 6: Follow Up on Outstanding
Weekly review:
1. Check status of all pending requests
2. Send follow-up for requests > 3 weeks old
3. Call records departments if needed
4. Document all follow-up attempts

### Step 7: Process Received Records
When records arrive:
1. Verify completeness (check date range)
2. Scan if received by mail
3. Organize in `Records/Medical/[Provider]/`
4. Update tracking status
5. Flag for chronology update

---

## Skills Used

- **medical-record-request**: Prepare and send requests
- **document-organization**: Organize received records
- **medical-record-extraction**: Process received records

---

## Completion Criteria

- [ ] All known providers identified
- [ ] Requests sent to all providers
- [ ] Tracking system updated
- [ ] Follow-ups scheduled
- [ ] Received records organized

---

## Outputs

- Updated `medical_providers.json`
- `Correspondence/records_requests/` - Sent requests
- `Records/Medical/` - Organized received records
- Records tracking report

---

## Phase Exit Contribution

This workflow contributes to:
- `all_records_requested`
- `all_records_received`
- `all_bills_received`

---

## Common Issues

### Records Delays
- Large hospital systems: 4-6 weeks typical
- Small practices: 1-2 weeks typical
- Follow up after 3 weeks with no response

### Incomplete Records
- Compare received dates to treatment dates
- Request specific missing records
- Note any gaps for client follow-up

### Excessive Charges
- Some providers charge per page
- Request fee schedule before authorizing
- Negotiate if charges excessive

