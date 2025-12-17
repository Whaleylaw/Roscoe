---
name: offer_evaluation
description: >
  Evaluate settlement offers and prepare recommendation for client. This workflow
  handles calculating net to client, analyzing offer merits, researching comparable
  verdicts, and coordinating client decision-making.
phase: negotiation
workflow_id: offer_evaluation
related_skills:
  - offer-evaluation
  - lien-negotiation
related_tools: []
templates:
  - offer_analysis_template.md
---

# Workflow: Offer Evaluation

## Phase: negotiation
## Goal: Evaluate settlement offers and prepare recommendation for client

---

## When to Trigger

- Insurance company makes settlement offer
- Counter-offer received
- User asks about offer evaluation
- Need to advise client on offer

---

## Inputs Required

- Settlement offer amount
- Current medical specials
- Projected future expenses
- Lien amounts
- Fee agreement terms
- Policy limits (if known)

---

## Step-by-Step Process

### Step 1: Document the Offer
Record offer details:
```json
{
  "offer_date": "",
  "offer_amount": "",
  "from": "adjuster name/company",
  "conditions": [],
  "expiration": "",
  "in_response_to": "demand|counter"
}
```

### Step 2: Calculate Net to Client
**Use skill: offer-evaluation**

Calculate breakdown:
1. **Gross Settlement**: Offer amount
2. **Attorney Fees**: Per fee agreement (typically 33.3% or 40%)
3. **Case Costs**: Actual costs incurred
4. **Medical Liens**: Total lien obligations
5. **Net to Client**: Gross - Fees - Costs - Liens

### Step 3: Compare to Demand
1. What was our demand?
2. What is the gap?
3. Is counter-offer reasonable?
4. Room for negotiation?

### Step 4: Evaluate Case Factors
Consider:
- Liability strength (clear vs. disputed)
- Injury severity
- Jury appeal
- Venue considerations
- Time to trial
- Client's financial situation
- Litigation costs if rejected

### Step 5: Research Comparable Verdicts
**Use legal research tools**

Search for:
- Similar injury verdicts
- Same venue verdicts
- Settlement ranges for injury type
- Document findings

### Step 6: Lien Impact Analysis
**Use skill: lien-negotiation**

Calculate lien scenarios:
1. Full lien payment
2. Negotiated reduction (estimate)
3. Impact on client's net recovery

### Step 7: Prepare Recommendation
Draft analysis including:
1. Offer summary
2. Net calculation
3. Comparison to case value
4. Pros of accepting
5. Cons of accepting
6. Recommendation
7. Suggested counter (if applicable)

### Step 8: Present to Attorney
Review with supervising attorney:
1. Offer details
2. Analysis
3. Recommendation
4. Get guidance on client communication

### Step 9: Client Communication
**Use skill: client-communication**

Communicate to client:
1. Explain the offer
2. Show net calculation
3. Present recommendation
4. Explain alternatives
5. Answer questions
6. Get decision

### Step 10: Document Decision
Record:
- Client's response to offer
- Authority to accept/counter
- Counter amount (if applicable)
- Follow-up needed

---

## Skills Used

| Skill | Location | Purpose |
|-------|----------|---------|
| `offer-evaluation` | `skills/offer-evaluation/skill.md` | Analyze offer merits, calculate net |
| `lien-negotiation` | `skills/lien-negotiation/skill.md` | Factor in lien reductions |

## Templates

| Template | Location | Purpose |
|----------|----------|---------|
| Offer Analysis | `templates/offer_analysis_template.md` | Document offer evaluation |

---

## Completion Criteria

- [ ] Offer documented
- [ ] Net to client calculated
- [ ] Case factors evaluated
- [ ] Comparable verdicts researched
- [ ] Recommendation prepared
- [ ] Attorney reviewed
- [ ] Client informed
- [ ] Client decision recorded

---

## Outputs

- `offer_analysis.json` - Detailed offer analysis
- Client communication record
- Decision documentation

---

## Phase Exit Contribution

This workflow contributes to:
- `offers_evaluated`
- `client_advised`

---

## Net Calculation Template

```
Gross Settlement:           $[amount]
Less:
  Attorney Fee ([%]):      -$[fee]
  Case Costs:              -$[costs]
  Medical Liens:           -$[liens]
                          ─────────
Net to Client:             $[net]
```

---

## Offer Response Options

| Option | When Appropriate |
|--------|------------------|
| Accept | Offer is fair, client agrees |
| Counter | Room for negotiation exists |
| Reject | Offer is insultingly low |
| Request time | Need more information |

