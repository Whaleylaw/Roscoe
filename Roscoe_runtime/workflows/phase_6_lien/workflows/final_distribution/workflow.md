---
name: final_distribution
description: >
  Distribute remaining funds to client after all liens resolved. This workflow
  prepares supplemental settlement statement and issues final payment.
phase: lien_phase
workflow_id: final_distribution
related_skills:
  - supplemental-statement
related_tools:
  - generate_document.py
templates:
  - supplemental_settlement_statement.md
---

# Final Distribution Workflow

## Overview

This workflow handles the final distribution of remaining settlement funds to the client after all liens have been resolved.

**Workflow ID:** `final_distribution`  
**Phase:** `lien_phase`  
**Owner:** Agent/User (mixed)  
**Repeatable:** No

---

## Prerequisites

- All liens resolved (paid or negotiated)
- Funds remaining in trust account
- Original settlement statement distributed

---

## Workflow Steps

### Step 1: Prepare Supplemental Settlement Statement

**Step ID:** `prepare_supplemental`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Create supplemental statement showing lien resolution and additional distribution.

**Template:** `forms/settlement/supplemental_settlement_statement_TEMPLATE.xlsx`

**Contents:**
```
SUPPLEMENTAL SETTLEMENT STATEMENT
Client: {{client.name}}

ORIGINAL SETTLEMENT
Gross Settlement:                   ${{original_gross}}
Less: Attorney Fee:                -${{fee}}
Less: Expenses:                    -${{expenses}}
Less: Liens (held):                -${{held_for_liens}}
────────────────────────────────────
Initial Net to Client:              ${{initial_net}}

LIEN RESOLUTION
Amount Held for Liens:              ${{held_amount}}
Liens Actually Paid:
  - {{lien_1}}:                    -${{paid_1}}
  - {{lien_2}}:                    -${{paid_2}}
────────────────────────────────────
Remaining After Liens:              ${{remaining}}

ADDITIONAL DISTRIBUTION TO CLIENT:  ${{additional_distribution}}

TOTAL NET TO CLIENT:                ${{total_net}}
(Initial: ${{initial}} + Additional: ${{additional}})
```

---

### Step 2: Issue Additional Distribution

**Step ID:** `issue_distribution`  
**Owner:** User  
**Automatable:** No

**Action:**
Issue check for additional funds to client.

**Process:**
1. Prepare check from trust account
2. Include supplemental settlement statement
3. Schedule pickup or mail certified
4. Update trust account records

---

### Step 3: Confirm Receipt

**Step ID:** `confirm_receipt`  
**Owner:** User  
**Automatable:** No

**Action:**
Confirm client received additional funds.

---

### Step 4: Zero Trust Account

**Step ID:** `zero_account`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Verify trust account balance is zero for this client.

**Updates:**
```json
{
  "settlement.final_distribution_date": "{{today}}",
  "settlement.final_distribution_amount": {{amount}},
  "settlement.trust_account_balance": 0
}
```

---

## Outputs

### Documents Created
- Supplemental settlement statement

### Financial Actions
- Additional distribution to client
- Trust account zeroed

### Phase Transition
→ `closed` phase

---

## Completion Criteria

- Trust account balance zero
- Client received additional funds
- All liens paid

---

## Related Workflows

- **Triggered By:** All liens resolved
- **Triggers:** `close_case`

---

## Skills Used

| Skill | Location | Purpose |
|-------|----------|---------|
| `supplemental-statement` | `skills/supplemental-statement/skill.md` | Create supplemental settlement statement |

---

## Tools

| Tool | Location | Purpose |
|------|----------|---------|
| `generate_document.py` | `tools/generate_document.py` | Generate settlement documents |

---

## Templates

| Template | Location | Purpose |
|----------|----------|---------|
| Supplemental Statement | `templates/supplemental_settlement_statement.md` | Final distribution breakdown |

