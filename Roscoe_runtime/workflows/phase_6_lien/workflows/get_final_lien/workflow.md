---
name: get_final_lien
description: >
  Obtain final lien amounts from all outstanding lien holders. This workflow
  requests final demands from Medicare, health insurance, and other lien holders
  after settlement is reached.
phase: lien_phase
workflow_id: get_final_lien
related_skills:
  - final-lien-request
related_tools:
  - generate_document.py
templates:
  - templates/final_lien_request.md
---

# Get Final Lien Amount Workflow

## Overview

This workflow obtains final (not conditional) lien amounts from all outstanding lien holders. It is executed for each lien requiring resolution before final distribution.

**Workflow ID:** `get_final_lien`  
**Phase:** `lien_phase`  
**Owner:** Agent/User (mixed)  
**Repeatable:** Yes (per lien)

---

## Prerequisites

- Settlement complete
- Liens identified with conditional amounts
- Lien still outstanding (not resolved during settlement)

---

## Workflow Steps

### Step 1: Identify Outstanding Liens

**Step ID:** `identify_outstanding`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
List all liens requiring final amounts.

**Query:**
```python
outstanding = [lien for lien in liens if lien.status == "outstanding"]
```

**Output:**
| Lien Holder | Type | Conditional Amount | Status |
|-------------|------|-------------------|--------|
| Medicare | Federal | $15,000 | Need final demand |
| Blue Cross | ERISA | $8,500 | Need final amount |

---

### Step 2: Request Final Amount (Per Lien Type)

The process varies by lien type:

#### Medicare Liens

**Request Final Demand Letter:**
1. Report settlement to BCRC (Benefits Coordination & Recovery Center)
2. Submit settlement information:
   - Settlement amount
   - Date of settlement
   - Attorney fee percentage
3. Request Final Demand Letter

**Medicare Contact:**
- BCRC: 1-855-798-2627
- Portal: MSPRP (Medicare Secondary Payer Recovery Portal)

**Expected Timeline:** 30-60 days for final demand

#### Health Insurance (ERISA) Liens

**Request Final Statement:**
1. Send settlement notification letter
2. Request final itemized statement
3. Request plan documents (if negotiating)

**Include in Request:**
- Settlement amount
- Client name and ID
- Date of accident
- Request for reduction (if applicable)

#### Medicaid Liens

**Contact DMS (Department for Medicaid Services):**
1. Report settlement
2. Request final lien amount
3. Follow state-specific procedures

#### Hospital/Provider Liens

**Request Final Statement:**
1. Confirm statutory lien filed
2. Request final balance
3. Verify against bills received

---

### Step 3: Document Final Amounts

**Step ID:** `document_amounts`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Record final amounts received.

**Updates to `liens.json`:**
```json
{
  "id": "lien_001",
  "holder": "Medicare",
  "conditional_amount": 15000,
  "final_amount": 12500,
  "final_amount_date": "{{today}}",
  "reduction_applied": "Procurement cost reduction (1/3)",
  "payment_deadline": "{{date + 60 days}}",
  "status": "final_received"
}
```

---

## Outputs

### Per Lien
- Final amount documented
- Payment deadline noted
- Status updated

### Summary
- Total final lien amounts
- Remaining funds available for distribution

---

## Completion Criteria

### Per Lien
- Final amount received and documented
- OR documented reason for delay

---

## Related Workflows

- **Triggered By:** Entry to lien phase
- **Triggers:** `negotiate_lien` (if amounts need reduction)

---

## Skills Used

| Skill | Location | Purpose |
|-------|----------|---------|
| `final-lien-request` | `skills/final-lien-request/skill.md` | Lien-specific request procedures |

---

## Templates

| Template | Location | Purpose |
|----------|----------|---------|
| Final Lien Request | `templates/final_lien_request.md` | Request final lien amounts |

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Medicare won't issue final | Verify all info submitted, follow up |
| ERISA plan unresponsive | Escalate, may need attorney involvement |
| Final amount exceeds available funds | Proceed to `negotiate_lien` |

