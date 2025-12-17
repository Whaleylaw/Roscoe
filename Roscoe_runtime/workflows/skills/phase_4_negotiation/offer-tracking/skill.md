---
name: offer-tracking
description: >
  Document and track all settlement offers and counteroffers throughout
  negotiation. Use when recording new offers, updating offer status,
  generating negotiation summaries, or reviewing negotiation history.
  Maintains comprehensive audit trail of all negotiation activity.
---

# Offer Tracking Skill

## Skill Metadata

- **ID**: offer-tracking
- **Category**: negotiation / documentation
- **Model Required**: claude-sonnet-4-20250514 or higher
- **Reference Material**: `references/tracking-fields.md`
- **Tools Required**: None (JSON data management)

---

## When to Use This Skill

Use this skill when:
- New offer received from insurance
- Counter-offer sent to insurance
- Need to review negotiation history
- Generating negotiation summary report
- Preparing for client communication about offers
- Updating offer status (accepted, rejected, expired)

**DO NOT use if:**
- Evaluating offer merits (use `offer-evaluation`)
- Planning counter strategy (use `negotiation-strategy`)
- No offers yet (case not in negotiation phase)

---

## Workflow

### Step 1: Identify Entry Type

| Entry Type | When Used |
|------------|-----------|
| `initial_offer` | Insurance's first offer |
| `revised_offer` | Subsequent insurance offers |
| `counter` | Our counter-offer |
| `final_offer` | Stated as final |
| `acceptance` | Offer accepted |
| `rejection` | Offer rejected |

### Step 2: Collect Required Fields

For each entry, collect:
- Date
- Round number
- Entry type
- From (insurance/plaintiff)
- Amount
- Status

**See:** `references/tracking-fields.md` for complete field list.

### Step 3: Update Insurance JSON

Add entry to `insurance.json`:

```json
{
  "claims": [{
    "id": "bi_001",
    "offers": [
      {
        "date": "2024-06-01",
        "round": 1,
        "type": "initial_offer",
        "from": "insurance",
        "amount": 25000,
        "adjuster_notes": "Initial evaluation",
        "status": "countered"
      }
    ]
  }]
}
```

### Step 4: Calculate Metrics

Track key metrics:
- Gap (our position - their position)
- Movement (change from previous)
- Days in negotiation
- Offer as % of demand/limits

### Step 5: Generate Summary

Create negotiation summary showing:
- Timeline of all offers
- Movement patterns
- Current status
- Next steps

---

## Entry Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Awaiting response |
| `under_review` | Being evaluated |
| `countered` | Counter was sent |
| `responded` | Response received |
| `accepted` | Offer accepted |
| `rejected` | Offer rejected |
| `expired` | Deadline passed |

---

## Output Format

### Single Entry Record

```json
{
  "date": "2024-06-15",
  "round": 2,
  "type": "revised_offer",
  "from": "insurance",
  "amount": 35000,
  "conditions": "Release all parties",
  "adjuster_notes": "Reviewed medical records",
  "deadline": "2024-07-15",
  "status": "pending"
}
```

### Summary Report

```markdown
## Negotiation Summary

**Claim:** State Farm (BI) - Claim #12345
**Demand:** $100,000 (sent 05/01/2024)
**Policy Limits:** $100,000

### Offer History

| Date | Round | From | Amount | Status |
|------|-------|------|--------|--------|
| 06/01 | 1 | Insurance | $25,000 | Countered |
| 06/05 | 1 | Plaintiff | $85,000 | Responded |
| 06/15 | 2 | Insurance | $35,000 | Pending |

### Metrics
- Current Gap: $50,000
- Days in Negotiation: 45
- Rounds Completed: 2
- Insurance Movement: +$10,000
- Our Movement: -$15,000

### Current Status
Awaiting client decision on $35,000 offer.
```

---

## Best Practices

### Document Everything

- Record every communication
- Note adjuster's reasoning
- Document our justification
- Include deadlines

### Track Timing

- Response times
- Deadline compliance
- Negotiation velocity

### Identify Patterns

- Adjuster negotiation style
- Movement patterns
- Sticking points

---

## Related Skills

- `offer-evaluation` - For analyzing offer merits
- `negotiation-strategy` - For planning responses
- `calendar-scheduling` - For deadline tracking

---

## Reference Material

For detailed field specifications, load:
- `references/tracking-fields.md` - All fields and valid values

