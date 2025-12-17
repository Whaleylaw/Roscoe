---
name: offer-evaluation
description: >
  Analyze settlement offers, calculate net to client, and prepare recommendations.
  Use when insurance company makes an offer, counter-offer is received, or need
  to advise client on settlement. Handles fee calculations, lien deductions,
  and comparison to case value.
---

# Offer Evaluation Skill

## Skill Metadata

- **ID**: offer-evaluation
- **Category**: negotiation
- **Model Required**: claude-sonnet-4-20250514 or higher
- **Reference Material**: `references/net-calculation.md`, `references/comparable-analysis.md`
- **Tools Required**: None (calculation-based)

---

## When to Use This Skill

Use this skill when:
- Insurance company makes a settlement offer
- Counter-offer received from adjuster
- Need to calculate net to client
- Client asks "how much would I get?"
- Attorney needs offer analysis for decision

**DO NOT use if:**
- No offer has been made
- Just tracking offers (use `offer-tracking` instead)
- Negotiating lien reductions (use `lien-negotiation` instead)

---

## Workflow

### Step 1: Gather Offer Information

Collect from user or case file:
- Offer amount
- Offer date
- Any conditions attached
- Response deadline (if any)

### Step 2: Calculate Net to Client

Use the formula:
```
Net = Gross Settlement - Attorney Fee - Case Costs - Liens
```

**Fee Determination:**
- Pre-litigation: 33.33% (standard)
- Post-litigation: 40% (standard)
- Check fee agreement for actual rate

**See:** `references/net-calculation.md` for detailed calculation steps.

### Step 3: Compare to Demand

| Metric | Value |
|--------|-------|
| Our Demand | $X |
| Their Offer | $Y |
| Gap | $X - Y |
| Offer as % of Demand | Y/X × 100 |

### Step 4: Evaluate Offer Quality

**Strong indicators:**
- Offer > 50% of demand
- Offer > 3× medical specials
- Offer near policy limits

**Weak indicators:**
- Offer < 25% of demand
- Offer < medical specials
- Large gap from demand

### Step 5: Prepare Recommendation

Options:
1. **Accept** - Offer is fair given case factors
2. **Counter** - Room for negotiation, suggest amount
3. **Reject** - Offer insultingly low, need movement
4. **Request Time** - Need more information

---

## Output Format

Provide structured analysis:

```markdown
## Offer Analysis

**Offer:** $[amount] from [adjuster/carrier]
**Date:** [date]

### Net Calculation
| Item | Amount |
|------|--------|
| Gross Settlement | $X |
| Attorney Fee (X%) | -$X |
| Case Costs | -$X |
| Medical Liens | -$X |
| **Net to Client** | **$X** |

### Comparison
- Demand: $X
- Gap: $X
- Offer as % of Demand: X%

### Recommendation
[Accept/Counter/Reject] because [reasoning]

### Suggested Counter (if applicable)
$[amount] based on [justification]
```

---

## Related Skills

- `lien-negotiation` - For analyzing lien reduction potential
- `negotiation-strategy` - For counter-offer tactics
- `offer-tracking` - For documenting offers

---

## Reference Material

For detailed information, load:
- `references/net-calculation.md` - Detailed calculation formulas
- `references/comparable-analysis.md` - Researching comparable verdicts

