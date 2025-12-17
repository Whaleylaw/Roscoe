# Medical Bills Request Checklist (Gap #12)

## Overview
Process for requesting itemized medical bills from providers.

---

## Existing Data Fields (medical_providers.json)
- `date_medical_bills_requested` - When request was sent
- `medical_bills_received_date` - When bills arrived
- `medical_bills_follow_up_date` - Follow-up tracking
- `billed_amount` - Total billed
- `settlement_payment` - Amount paid at settlement

---

## When to Request Bills

### Trigger Conditions
1. Treatment completed at provider
2. Records received (often request bills with records)
3. Approaching demand preparation
4. PIP submitting bills for payment

---

## Request Process

### Step 1: Prepare Request
**Required Information:**
- [ ] Provider name and address
- [ ] Client full name and DOB
- [ ] Date of accident
- [ ] Treatment date range
- [ ] Request "itemized statement" specifically

### Step 2: Send Request

**Key Points:**
- Request **itemized** bill (not summary/statement)
- Should show: date, CPT code, description, charge
- Include any payments already made (PIP, health insurance)

**Track in Case File:**
- Update `date_medical_bills_requested` = today's date

### Step 3: Follow-Up Schedule

| Days After Request | Action |
|-------------------|--------|
| 14 days | First follow-up call |
| 21 days | Second follow-up + written reminder |
| 30 days | Escalate |

### Step 4: Receipt & Verification

When bills arrive:
- [ ] Update `medical_bills_received_date` = today's date
- [ ] Update `billed_amount` = total from bill
- [ ] Verify matches treatment dates
- [ ] Check for payments/adjustments shown
- [ ] File in case folder: `/[case]/medical_bills/`

---

## Bill Review Checklist

- [ ] All dates of service included
- [ ] CPT codes present and reasonable
- [ ] No duplicate charges
- [ ] Payments/adjustments shown
- [ ] Balance matches expected

---

## Integration with Workflows

### For PIP Submission
- Submit bills to PIP as received
- Track PIP payments in insurance record

### For Demand Preparation
- Compile all bills for demand package
- Calculate total medical specials
- Note any reductions/write-offs

### For Settlement
- Final bills needed before settlement statement
- Track negotiated reductions

