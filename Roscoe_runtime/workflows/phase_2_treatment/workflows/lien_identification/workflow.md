---
name: lien_identification
description: >
  Identify and classify all potential liens that may affect case recovery during
  treatment phase. Includes Medicare, Medicaid, ERISA health plans, hospital liens,
  and letters of protection.
phase: treatment
workflow_id: lien_identification
related_skills:
  - skills/lien-classification/skill.md
related_tools: []
templates:
  - templates/lien_inventory.md
---

# Workflow: Lien Identification

## Phase: treatment
## Goal: Identify all potential liens that may affect case recovery

---

## When to Trigger

- During treatment phase of any case
- When health insurance pays medical bills
- Client mentions Medicare, Medicaid, or ERISA plan
- Hospital or provider mentions lien

---

## Inputs Required

- Client's health insurance information
- Medicare/Medicaid status
- List of medical providers
- Medical bills received

---

## Step-by-Step Process

### Step 1: Categorize Health Coverage
**Use skill: lien-classification**

Determine type of coverage:
- [ ] Private health insurance (fully insured)
- [ ] Self-funded ERISA plan
- [ ] Medicare
- [ ] Medicaid
- [ ] TRICARE/VA
- [ ] Workers' compensation
- [ ] No health insurance

### Step 2: Identify Medicare Interest
If client is Medicare eligible:
1. Verify Medicare status (Parts A, B, D, Advantage)
2. Register case with MSPRC
3. Request conditional payment information
4. Note Section 111 reporting obligations

### Step 3: Identify Medicaid Interest
If Medicaid involved:
1. Identify state Medicaid agency
2. Send notice of representation
3. Request lien amount
4. Note state-specific lien rules

### Step 4: Identify Health Insurance Liens
**Use skill: lien-identification**

For each health plan:
1. Determine if plan has subrogation rights
2. Check if ERISA applies (self-funded?)
3. Review plan language for:
   - Subrogation clause
   - Reimbursement clause
   - Made whole doctrine applicability
4. Send subrogation notice

### Step 5: Identify Provider Liens
Check for:
- Hospital statutory liens
- Provider letters of protection
- Ambulance liens
- Unpaid providers with lien rights

### Step 6: Create Lien Inventory
Document all identified liens:
```json
{
  "liens": [
    {
      "type": "health_insurance|medicare|medicaid|hospital|provider",
      "holder": "",
      "contact": "",
      "claimed_amount": null,
      "basis": "subrogation|statutory|contract",
      "erisa": true|false,
      "reduction_strategy": "",
      "status": "identified|notice_sent|amount_confirmed|negotiating|resolved"
    }
  ]
}
```

### Step 7: Send Appropriate Notices
For each lien holder:
1. Prepare notice of representation
2. Request itemized lien amount
3. Request plan documents (for ERISA)
4. Document all communications

---

## Skills Used

- **lien-classification**: Categorize liens by type and applicable law
- **lien-identification**: Identify all potential lien holders
- **medicare-lien-resolution**: Handle Medicare-specific requirements
- **medicaid-lien-resolution**: Handle Medicaid-specific requirements
- **erisa-lien-analysis**: Analyze ERISA plan rights

---

## Completion Criteria

- [ ] All health coverage types identified
- [ ] Medicare status confirmed
- [ ] Medicaid status confirmed
- [ ] Health insurance subrogation notices sent
- [ ] Provider liens identified
- [ ] Lien inventory created
- [ ] All lien holders notified

---

## Outputs

- `liens.json` - Complete lien inventory
- `Correspondence/lien_notices/` - Sent notices
- Updated case notes with lien information

---

## Phase Exit Contribution

This workflow directly satisfies:
- `liens_identified`

---

## Lien Priority Reference

| Lien Type | Strength | Reduction Potential |
|-----------|----------|---------------------|
| Medicare | Federal law - strong | Limited (procurement costs) |
| Medicaid | State law - varies | State dependent |
| ERISA self-funded | Federal law - strong | Plan language dependent |
| Fully insured | State law applies | Made whole, common fund |
| Hospital statutory | State law | Varies by state |
| Provider LOP | Contract | Negotiable |

---

## Red Flags

- Client unsure of health insurance type
- Large hospital bills without health insurance
- Client receiving disability benefits (Medicare?)
- Workers' comp involvement
- Prior attorneys involved (may have created LOPs)

