---
name: negotiate_lien
description: >
  Negotiate lien reduction with lien holders. This workflow handles negotiation
  strategies, reduction requests, and documentation of negotiated amounts.
phase: lien_phase
workflow_id: negotiate_lien
related_skills:
  - lien-reduction
related_tools: []
templates:
  - lien_reduction_request.md
---

# Negotiate Lien Workflow

## Overview

This workflow handles negotiation of lien amounts when the full amount would be burdensome to the client. Different strategies apply based on lien type (Medicare, ERISA, etc.).

**Workflow ID:** `negotiate_lien`  
**Phase:** `lien_phase`  
**Owner:** Agent/User (mixed)  
**Repeatable:** Yes (per lien)

---

## Prerequisites

- Final lien amount received
- Negotiation warranted (based on case economics)

---

## Negotiation Strategies by Lien Type

### Medicare Liens

**Automatic Reductions:**
- Procurement cost reduction: 1/3 off for attorney involvement

**Compromise/Waiver Request:**
- Submit to BCRC if hardship exists
- Document that full payment would deprive beneficiary of reasonable benefit

**Waiver Criteria:**
- Low net to client
- Documented financial hardship
- Full payment would be inequitable

---

### ERISA Health Insurance Liens

**Review Plan Language:**
1. Obtain Summary Plan Description (SPD)
2. Check for reduction provisions
3. Look for "made whole" language
4. Identify common fund provisions

**Negotiation Arguments:**
| Argument | When Applicable |
|----------|-----------------|
| Common Fund | Plan should pay share of attorney fees |
| Made Whole | Client not fully compensated |
| Proportional Reduction | Settlement < case value |
| Hardship | Low net to client |

**Typical Result:** 20-50% reduction

---

### Medicaid Liens

**State-Specific Rules:**
- Kentucky DMS has specific reduction procedures
- May accept proportional reduction

---

### Hospital/Provider Liens

**Negotiation Points:**
- Settlement amount vs. damages
- Multiple liens sharing limited funds
- Provider relationship considerations

---

## Workflow Steps

### Step 1: Evaluate Negotiation Potential

**Step ID:** `evaluate_potential`  
**Owner:** Agent  
**Automatable:** Partial

**Action:**
Assess whether negotiation is warranted and likely successful.

**Consider:**
- Net to client after full lien payment
- Lien holder's typical flexibility
- Available reduction arguments
- Time constraints

---

### Step 2: Prepare Reduction Request

**Step ID:** `prepare_request`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Draft lien reduction request with supporting arguments.

**Request Should Include:**
- Settlement amount and breakdown
- Attorney fees and expenses
- Other liens being paid
- Net to client calculation
- Hardship explanation (if applicable)
- Specific reduction request

---

### Step 3: Submit and Track

**Step ID:** `submit_request`  
**Owner:** User  
**Automatable:** No

**Action:**
Submit reduction request and track response.

---

### Step 4: Document Result

**Step ID:** `document_result`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Record negotiation outcome.

**Updates:**
```json
{
  "negotiation": {
    "requested_amount": {{amount}},
    "negotiated_amount": {{result}},
    "reduction_percentage": {{percent}},
    "negotiation_notes": "{{notes}}"
  },
  "final_payment_amount": {{negotiated_amount}},
  "status": "negotiated"
}
```

---

## Outputs

### Per Lien
- Negotiated amount documented
- Reduction percentage recorded
- Ready for payment

---

## Completion Criteria

- Negotiation complete
- Final payment amount determined

---

## Related Workflows

- **Triggered By:** `get_final_lien` (when reduction needed)
- **Triggers:** Lien payment in `final_distribution`

---

## Skills Used

| Skill | Location | Purpose |
|-------|----------|---------|
| `lien-reduction` | `skills/lien-reduction/skill.md` | Lien negotiation strategies |

---

## Templates

| Template | Location | Purpose |
|----------|----------|---------|
| Lien Reduction Request | `templates/lien_reduction_request.md` | Request lien reductions |

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Lien holder won't negotiate | Document attempts, may need to pay full |
| ERISA plan denies reduction | Review plan documents, consider legal challenge |
| Medicare denies waiver | Pay amount, may appeal |

