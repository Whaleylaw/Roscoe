---
name: lien_negotiation
description: >
  Negotiate lien reductions to maximize client recovery at settlement.
  This workflow handles Medicare, Medicaid, ERISA, hospital, and provider
  lien negotiations to reduce amounts owed and increase client net.
phase: settlement
workflow_id: lien_negotiation
related_skills:
  - lien-resolution
  - lien-classification
related_tools: []
templates:
  - lien_reduction_letter.md
---

# Workflow: Lien Negotiation

## Phase: settlement
## Goal: Negotiate lien reductions to maximize client recovery

---

## When to Trigger

- Settlement reached
- Before disbursement
- Liens exceed reasonable portion of settlement
- User asks about lien reduction

---

## Inputs Required

- Settlement amount
- Complete lien inventory
- Plan documents (for ERISA)
- State law research
- Attorney fees and costs

---

## Step-by-Step Process

### Step 1: Prioritize Liens
**Use skill: lien-classification**

Rank liens by negotiability:
1. Provider LOPs (most negotiable)
2. Hospital liens (state law dependent)
3. Fully insured health plans (state law applies)
4. Self-funded ERISA (least negotiable)
5. Medicare (formula-based reduction)
6. Medicaid (state law dependent)

### Step 2: Calculate Available Funds
```
Settlement Amount:          $[amount]
Less Attorney Fees:        -$[fees]
Less Costs:                -$[costs]
Available for Liens/Client: $[available]
Total Liens:               $[liens]
Shortfall (if any):        $[shortfall]
```

### Step 3: Research Applicable Law
For each lien type:
- State subrogation laws
- Made whole doctrine applicability
- Common fund doctrine
- ERISA preemption issues
- Statutory reduction formulas

### Step 4: Medicare Lien Negotiation
**Use skill: medicare-lien-resolution**

1. Request final conditional payment letter
2. Dispute unrelated charges
3. Calculate procurement cost reduction
4. Request waiver if hardship applies
5. Submit compromise request if needed

### Step 5: Medicaid Lien Negotiation
**Use skill: medicaid-lien-resolution**

1. Request final lien amount
2. Apply state-specific formulas
3. Request reduction based on:
   - Attorney fees/costs
   - Disputed liability
   - Policy limits
4. Document state law basis

### Step 6: Health Insurance Negotiation
1. Determine if ERISA applies
2. If NOT ERISA:
   - Assert made whole doctrine
   - Assert common fund (fee share)
   - Negotiate percentage reduction
3. If ERISA:
   - Review plan language carefully
   - Look for equitable defenses
   - Negotiate based on recovery ratio

### Step 7: Provider Lien Negotiation
For LOPs and provider liens:
1. Calculate percentage of settlement
2. Propose reduction based on:
   - Limited recovery
   - Full payment immediate
   - Ongoing referral relationship
3. Get written agreement on reduced amount

### Step 8: Document Negotiations
For each lien:
- Initial amount claimed
- Reduction arguments made
- Counter-offers
- Final agreed amount
- Written confirmation

### Step 9: Obtain Releases
Get written documentation:
- Lien satisfaction letters
- Release of subrogation interest
- Final payment amounts
- Payment instructions

### Step 10: Update Disbursement
Revise settlement disbursement with:
- Final negotiated lien amounts
- Verified payment information
- Client net recovery

---

## Skills Used

| Skill | Location | Purpose |
|-------|----------|---------|
| `lien-resolution` | `skills/lien-resolution/skill.md` | Core lien negotiation strategies |
| `lien-classification` | `skills/lien-classification/skill.md` | Understand lien types and rights |

## Templates

| Template | Location | Purpose |
|----------|----------|---------|
| Lien Reduction Letter | `templates/lien_reduction_letter.md` | Request lien reductions |

---

## Completion Criteria

- [ ] All liens verified and final
- [ ] Negotiations attempted on all liens
- [ ] Reductions documented
- [ ] Written confirmations obtained
- [ ] Releases collected
- [ ] Disbursement updated

---

## Outputs

- `lien_resolutions/` - Negotiation documentation
- Lien satisfaction letters
- Updated disbursement sheet
- Final `liens.json`

---

## Phase Exit Contribution

This workflow directly satisfies:
- `liens_negotiated`

---

## Reduction Strategies by Lien Type

| Lien Type | Strategy |
|-----------|----------|
| Medicare | Procurement costs (usually ~1/3) |
| Medicaid | State formula, attorney fees |
| ERISA | Limited - plan language controls |
| Fully Insured | Made whole, common fund, equity |
| Hospital Statutory | Statutory limits, negotiate |
| Provider LOP | Percentage of recovery |

---

## Sample Negotiation Letter Points

1. Limited recovery available
2. Disputed liability reduced value
3. Attorney fees/costs incurred
4. Made whole doctrine (if applicable)
5. Common fund contribution
6. Immediate payment offered
7. Alternative is protracted dispute

