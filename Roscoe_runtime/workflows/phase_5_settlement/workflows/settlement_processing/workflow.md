---
name: settlement_processing
description: >
  Finalize settlement and distribute funds. This workflow handles settlement
  statement preparation, authorization to settle, release processing, check
  receipt, lien payment, and final distribution to client.
phase: settlement
workflow_id: settlement_processing
related_skills:
  - settlement-statement
  - docusign-send
related_tools:
  - generate_document.py
templates:
  - templates/settlement_statement.md
  - templates/authorization_to_settle.md
---

# Settlement Processing Workflow

## Overview

This workflow manages the complete settlement process from acceptance to final distribution. It ensures proper documentation, client authorization, release execution, and compliant fund distribution.

**Workflow ID:** `settlement_processing`  
**Phase:** `settlement`  
**Owner:** Agent/User (mixed)  
**Repeatable:** No

---

## Prerequisites

- Settlement reached during negotiation
- Settlement amount agreed by all parties
- Client has verbally authorized settlement

---

## Workflow Steps

### Step 1: Prepare Settlement Statement

**Step ID:** `prepare_settlement_statement`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Create detailed settlement breakdown showing all deductions and net to client.

**Skill:** `Skills/document-xlsx/skill.md`

**Template:** `forms/settlement/settlement_statement_TEMPLATE.xlsx`

**Settlement Statement Contents:**

```
SETTLEMENT STATEMENT
Client: {{client.name}}
Date of Accident: {{accident.date}}
Date of Settlement: {{today}}

GROSS SETTLEMENT                           ${{gross_amount}}

LESS: Attorney Fee ({{fee_rate}}%)        -${{attorney_fee}}
LESS: Case Expenses                       -${{total_expenses}}
      - Filing fees                        ${{filing_fees}}
      - Medical records                    ${{records_fees}}
      - Postage                           ${{postage}}
      - [Other itemized expenses]
LESS: Liens                               -${{total_liens}}
      - {{lien_holder_1}}                  ${{lien_1_amount}}
      - {{lien_holder_2}}                  ${{lien_2_amount}}
────────────────────────────────────────────────────────
NET TO CLIENT                              ${{net_to_client}}
```

**Output:** Settlement statement document

**Saves To:** `Documents/Settlement/settlement_statement_{{client.name}}.xlsx`

---

### Step 2: Prepare Authorization to Settle

**Step ID:** `prepare_auth_to_settle`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Generate authorization form for client signature.

**Skill:** `Skills/document-docx/skill.md`

**Template:** `forms/settlement/authorization_to_settle_TEMPLATE.docx`

**Authorization Contents:**
- Settlement amount
- Summary of deductions
- Net to client
- Client acknowledgment of terms
- Signature line

**Output:** Authorization to settle document

**Saves To:** `Documents/Settlement/auth_to_settle_{{client.name}}.docx`

---

### Step 3: Client Signs Authorization

**Step ID:** `client_signs_auth`  
**Owner:** User  
**Automatable:** No

**Action:**
Get client signature on settlement authorization.

**Process:**
1. Send authorization and settlement statement to client
2. Explain all deductions
3. Answer any questions
4. Obtain signature (e-sign or in-person)

**Agent Prompt to User:**
> "Send Authorization to Settle to client for signature. Include the settlement statement showing their net amount."

**Updates:**
```json
{
  "documents.settlement_auth.status": "signed",
  "documents.settlement_auth.signed_date": "{{date}}"
}
```

---

### Step 4: Confirm Settlement with Adjuster

**Step ID:** `confirm_with_adjuster`  
**Owner:** User  
**Automatable:** No

**Action:**
Contact adjuster to confirm settlement acceptance and request release.

**Communication:**
> "We are accepting your settlement offer of ${{amount}}. 
> Please send the release for signature."

**Agent Prompt to User:**
> "Contact adjuster to confirm we're accepting the settlement. Request they send the release."

**Updates:**
```json
{
  "settlement.adjuster_notified_date": "{{today}}"
}
```

---

### Step 5: Receive Release

**Step ID:** `receive_release`  
**Owner:** User  
**Automatable:** No  
**Waiting On:** External (insurance)

**Expected Wait:** 5-10 business days

**Action:**
Receive release document from insurance company.

**Agent Prompt to User:**
> "Waiting for release from insurance. Update when received."

**Review Release For:**
- Correct settlement amount
- Proper party names
- Acceptable release language
- No problematic provisions

**If Issues Found:**
- Negotiate changes with adjuster
- Have attorney review problematic language

**Updates:**
```json
{
  "documents.release.received_date": "{{today}}"
}
```

---

### Step 6: Client Signs Release

**Step ID:** `client_signs_release`  
**Owner:** User  
**Automatable:** No

**Action:**
Get client signature on release document.

**Agent Prompt to User:**
> "Send release to client for signature via DocuSign."

**Updates:**
```json
{
  "documents.release.status": "signed",
  "documents.release.signed_date": "{{date}}"
}
```

---

### Step 7: Return Signed Release

**Step ID:** `return_release`  
**Owner:** User  
**Automatable:** No

**Action:**
Send signed release back to insurance company.

**Agent Prompt to User:**
> "Send signed release back to insurance company. Request they send the settlement check."

**Updates:**
```json
{
  "documents.release.returned_date": "{{today}}"
}
```

---

### Step 8: Receive Settlement Check

**Step ID:** `receive_check`  
**Owner:** User  
**Automatable:** No  
**Waiting On:** External (insurance)

**Expected Wait:** 10-21 business days

**Action:**
Receive settlement check and deposit to client trust account.

**Agent Prompt to User:**
> "Waiting for settlement check. When received, deposit to client trust account."

**Upon Receipt:**
1. Verify check amount matches settlement
2. Deposit to client trust account
3. Note deposit date

**Updates:**
```json
{
  "settlement.check_received_date": "{{today}}",
  "settlement.check_amount": {{amount}},
  "settlement.check_deposited_date": "{{today}}"
}
```

---

### Step 9: Pay Liens

**Step ID:** `pay_liens`  
**Owner:** User  
**Automatable:** No  
**Conditional:** `liens.length > 0`

**Action:**
Pay all outstanding liens from settlement proceeds.

**Agent Prompt to User:**
> "Pay all liens from settlement. Update each lien with payment date and amount."

**For Each Lien:**
1. Issue check for final negotiated amount
2. Send with cover letter
3. Request lien satisfaction letter
4. Update lien status

**Updates (per lien):**
```json
{
  "liens[].payment_date": "{{today}}",
  "liens[].payment_amount": {{amount}},
  "liens[].status": "paid"
}
```

**If Liens Cannot Be Resolved:**
→ Move to `lien_phase`

---

### Step 10: Distribute Funds

**Step ID:** `distribute_funds`  
**Owner:** User  
**Automatable:** No

**Action:**
Write distribution checks per settlement statement.

**Distribution Checks:**
| Payee | Amount | Purpose |
|-------|--------|---------|
| Law Firm | Attorney fee | Earned fee |
| Law Firm | Expenses | Reimbursement |
| Client | Net amount | Settlement proceeds |

**Agent Prompt to User:**
> "Write checks: attorney fee, case expenses, and client net. Get client to pick up or mail their check."

**Client Distribution:**
- Schedule pickup appointment OR
- Mail via certified mail OR
- Direct deposit (if set up)

**Updates:**
```json
{
  "settlement.client_check_issued_date": "{{today}}",
  "settlement.client_check_amount": {{net_amount}},
  "settlement.client_received_date": "{{date}}"
}
```

---

## Outputs

### Documents Created
| Document | Purpose |
|----------|---------|
| Settlement Statement | Financial breakdown |
| Authorization to Settle | Client consent |
| Distribution records | Trust account documentation |

### Financial Actions
- Trust account deposit
- Lien payments
- Final distribution

### Phase Transition
| Outcome | Next Phase |
|---------|------------|
| All liens paid, client paid | `closed` |
| Liens unresolved | `lien_phase` |

---

## Completion Criteria

### Required
- `documents.settlement_auth.status == "signed"`
- `documents.release.status == "signed"`
- `client_paid == true`

---

## State Updates

On completion, update `case_state.json`:
```json
{
  "workflows": {
    "settlement_processing": {
      "status": "complete",
      "completed_date": "{{today}}",
      "settlement_amount": {{amount}},
      "net_to_client": {{net}},
      "liens_paid": {{count}}
    }
  },
  "current_phase": "closed"
}
```

---

## Related Workflows

- **Triggered By:** Settlement reached in negotiation
- **Triggers:** `close_case` or `lien_phase`

---

## Skills Used

| Skill | Location | Purpose |
|-------|----------|---------|
| `settlement-statement` | `skills/settlement-statement/skill.md` | Create settlement breakdown |
| `docusign-send` | `skills/docusign-send/skill.md` | Send documents for signature |

---

## Tools

| Tool | Location | Purpose |
|------|----------|---------|
| `generate_document.py` | `tools/generate_document.py` | Generate settlement documents |

---

## Templates

| Template | Location | Purpose |
|----------|----------|---------|
| Settlement Statement | `templates/settlement_statement.md` | Financial breakdown template |
| Authorization to Settle | `templates/authorization_to_settle.md` | Client consent document |

---

## Trust Account Requirements

Kentucky Rules require:
- Settlement funds deposited to IOLTA trust account
- Hold until check clears (typically 5-10 days)
- Pay liens before client distribution
- Maintain detailed records

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Client won't sign auth | Review concerns, explain process |
| Release has bad language | Negotiate changes, attorney review |
| Check delayed | Follow up with claims department |
| Lien exceeds available funds | Negotiate reduction, may need lien phase |
| Client wants immediate funds | Explain trust requirements |

