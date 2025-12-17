# Kentucky Assigned Claims (KAC) Process

## When KAC Applies

Kentucky Assigned Claims provides PIP coverage when:
- No insurance coverage exists through normal waterfall
- Client was NOT an owner of an uninsured vehicle (that would disqualify them)

## Waterfall Path to KAC

```
Step 1: Client on title? → NO (or YES with insured vehicle)
Step 2: Vehicle occupied insured? → NO
Step 3: Client has own insurance? → NO
Step 4: Household member insurance? → NO
Result: → KAC
```

## KAC Contact Information

```
Kentucky Assigned Claims Plan
P.O. Box 517
Frankfort, KY 40602

Phone: (502) 875-4460
Fax: (502) 875-4463
```

## KAC Application Process

### Step 1: Complete KACP Application
- Same form used for all PIP claims
- Must be fully completed
- Client signature required

### Step 2: Submit to KAC
- Mail or fax to KAC address above
- Include all supporting documentation:
  - Police report (if available)
  - Medical records showing injury
  - Proof of accident details

### Step 3: KAC Assigns Insurer
- KAC will review and assign an insurer
- Assignment based on market share rotation
- **Timeline: May take up to 30 days**

### Step 4: Contact Assigned Insurer
- KAC will notify of assignment
- Contact assigned insurer directly
- Open PIP claim with assigned carrier
- Proceed as normal PIP claim

## User Notification

```
📋 KENTUCKY ASSIGNED CLAIMS (KAC) REQUIRED

No PIP coverage found through normal channels:
- Client does not own insured vehicle involved
- Vehicle occupied was not insured
- Client has no auto insurance
- No household member has auto insurance

Next Steps:
1. Complete KACP Application (same form for all PIP)
2. Submit to Kentucky Assigned Claims Plan:
   
   Kentucky Assigned Claims Plan
   P.O. Box 517
   Frankfort, KY 40602
   Phone: (502) 875-4460

3. KAC will assign an insurer (may take up to 30 days)
4. Contact assigned insurer to open PIP claim

Note: KAC claims may have longer processing times compared 
to direct insurer claims.

Shall I help prepare the KACP Application for KAC submission?
```

## Data Recording

```json
{
  "pip": {
    "pip_insurer": "Kentucky Assigned Claims",
    "pip_insurer_type": "kac",
    "is_kac": true,
    "is_disqualified": false,
    "kac_status": "pending_application",
    "assigned_insurer": null,
    "kac_application_date": null,
    "kac_assignment_date": null,
    "waterfall_date": "2024-12-06",
    "waterfall_path": [
      "Step 1: Client not on vehicle title",
      "Step 2: Vehicle occupied not insured",
      "Step 3: Client has no own insurance",
      "Step 4: No household member insurance",
      "Result: KAC"
    ]
  }
}
```

## Timeline Expectations

| Stage | Expected Timeline |
|-------|-------------------|
| Application submitted | Day 0 |
| KAC review | 1-2 weeks |
| Insurer assignment | 2-4 weeks |
| Contact with assigned insurer | 3-5 weeks |
| PIP claim opened | 4-6 weeks |

## Follow-Up Schedule

After KAC application submitted:
- **14 days**: Call KAC to check status
- **21 days**: If no assignment, escalate inquiry
- **30 days**: Should have assignment, contact assigned insurer
- **45 days**: If still no assignment, formal complaint

## Common Issues

| Issue | Resolution |
|-------|------------|
| Application incomplete | KAC returns for completion |
| Missing documentation | Submit additional docs |
| Assignment delayed | Follow up with KAC directly |
| Assigned insurer unresponsive | Contact KAC for assistance |

