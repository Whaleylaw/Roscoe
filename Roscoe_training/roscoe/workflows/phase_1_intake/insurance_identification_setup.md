# Workflow: Insurance Identification & Setup

## Phase: intake
## Goal: Identify all insurance coverage and open necessary claims

---

## When to Trigger

- After initial documentation is complete
- User asks about insurance or coverage
- Need to open claims

---

## Inputs Required

- Accident report (if available)
- Client's insurance information
- At-fault party information
- Vehicle information (for MVA)

---

## Step-by-Step Process

### Step 1: Identify Client's Insurance
**Use skill: insurance-coverage-analysis**

For motor vehicle accidents:
1. Auto policy (liability, PIP, UM/UIM, MedPay)
2. Health insurance
3. Medicare/Medicaid status
4. Disability insurance
5. Umbrella policies

For premises liability:
1. Health insurance
2. Homeowner's/renter's insurance
3. Medicare/Medicaid status

### Step 2: Identify At-Fault Party Insurance
**Use skill: liable-party-identification**

1. Get at-fault party's insurance from:
   - Accident report
   - At-fault party directly
   - Insurance databases
2. Verify policy is active
3. Identify policy limits if possible

### Step 3: Identify Additional Coverage
Check for:
- Commercial policies (if commercial vehicle)
- Employer coverage (if during employment)
- Government entity coverage (sovereign immunity issues)
- Excess/umbrella policies

### Step 4: Open PIP Claim
**Use skill: pip-claim-setup**

1. Contact client's auto insurer
2. Report the claim
3. Request claim number
4. Identify adjuster
5. Note coverage limits
6. Document any PIP application requirements

### Step 5: Open BI Claim
1. Send Letter of Representation to at-fault insurer
2. Request claim number
3. Identify adjuster
4. Request policy limits disclosure
5. Request copy of declarations page

### Step 6: Send Letters of Representation
For each insurance company:
1. Prepare LOR with:
   - Client identification
   - Date of loss
   - Claim number (if known)
   - Request for acknowledgment
2. Send via certified mail or fax
3. Track for acknowledgment

### Step 7: Document All Coverage
Create comprehensive insurance record:
```json
{
  "client_coverage": {
    "auto": {
      "carrier": "",
      "policy_number": "",
      "claim_number": "",
      "adjuster": "",
      "pip_limit": "",
      "um_uim_limit": ""
    },
    "health": {
      "carrier": "",
      "type": "group|individual|medicare|medicaid",
      "policy_number": ""
    }
  },
  "adverse_coverage": {
    "liability": {
      "carrier": "",
      "policy_number": "",
      "claim_number": "",
      "adjuster": "",
      "known_limits": ""
    }
  }
}
```

---

## Skills Used

- **insurance-coverage-analysis**: Analyze all available coverage
- **liable-party-identification**: Identify at-fault parties and their insurance
- **pip-claim-setup**: Open PIP claims properly
- **um-uim-analysis**: Evaluate UM/UIM potential

---

## Completion Criteria

- [ ] Client's auto insurance identified
- [ ] Client's health insurance identified
- [ ] At-fault party insurance identified
- [ ] PIP claim opened (if applicable)
- [ ] BI claim opened with at-fault insurer
- [ ] Letters of representation sent
- [ ] LOR acknowledgments received
- [ ] All coverage documented in insurance.json

---

## Outputs

- `insurance.json` - Comprehensive coverage record
- `Correspondence/letters_of_rep/` - Sent LORs
- `Correspondence/lor_acknowledgments/` - Received acknowledgments
- Updated `medical_providers.json` with PIP info

---

## Phase Exit Contribution

This workflow directly satisfies:
- `insurance_companies_identified`
- `pip_claim_opened`
- `bi_claim_opened`
- `letters_of_rep_acknowledged`

---

## Important Deadlines

- **PIP Application**: Many states require application within specific timeframe
- **UM/UIM Notice**: May require timely notice to preserve rights
- **Policy Limits Demand**: Consider timing strategically

