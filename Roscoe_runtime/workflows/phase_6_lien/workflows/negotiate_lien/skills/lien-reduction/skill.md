---
name: lien-reduction
description: >
  Negotiate lien reductions in the Lien Phase when full payment would be
  burdensome. Use when final lien amounts exceed available funds, when
  client net would be unreasonably low, or when ERISA, Medicare, or other
  liens can potentially be reduced through legal arguments or compromise.
---

# Lien Reduction Skill

## Skill Metadata

- **ID**: lien-reduction
- **Category**: lien_phase
- **Model Required**: claude-sonnet-4-20250514 or higher
- **Reference Material**: `references/erisa-negotiation.md`, `references/compromise-waiver.md`
- **Tools Required**: None

---

## When to Use This Skill

Use this skill when:
- Final lien amount received exceeds expectations
- Full payment would leave client with inadequate recovery
- ERISA plan may have reduction provisions
- Medicare compromise/waiver may be available
- Multiple liens competing for limited funds

**DO NOT use if:**
- Lien already at acceptable amount
- Lien holder won't negotiate (documented)
- No legal basis for reduction

---

## Workflow

### Step 1: Assess Reduction Potential

| Factor | Analysis |
|--------|----------|
| Net to client after full payment | $X |
| Legal basis for reduction | [Identify] |
| Lien holder's flexibility | [Assess] |
| Time available | [Deadline] |

### Step 2: Identify Reduction Strategy

| Lien Type | Primary Strategy |
|-----------|------------------|
| Medicare | Procurement cost (auto) + Compromise |
| ERISA | Plan language + Common fund |
| Medicaid | Statutory formula |
| Hospital | Pro-rata + Hardship |
| Provider | Recovery percentage |

### Step 3: Prepare Reduction Request

Include:
- Settlement breakdown
- Net to client calculation
- Legal basis for reduction
- Specific amount requested
- Hardship factors (if applicable)

### Step 4: Submit and Track

Document:
- Request date
- Response received
- Counter-offers
- Final agreement

---

## Key Strategies

### ERISA Plans

1. **Review Plan Language**
   - Check for reduction provisions
   - Look for "make whole" clauses
   - Identify common fund language

2. **Assert Legal Arguments**
   - Common fund doctrine
   - Equitable principles
   - Made whole (if applicable)

**See:** `references/erisa-negotiation.md`

### Medicare Compromise

If procurement cost isn't enough:
1. Document hardship
2. Calculate net to beneficiary
3. Submit compromise request
4. Await determination

**See:** `references/compromise-waiver.md`

---

## Output Format

```markdown
## Lien Reduction Summary

### Lien: [Lien Holder Name]

| Item | Amount |
|------|--------|
| Original Lien | $[original] |
| Reduction Requested | $[requested] |
| Final Negotiated | $[final] |
| **Savings** | **$[savings]** |

### Negotiation Notes
[Summary of negotiation process]

### Documentation
- [ ] Reduction request submitted [date]
- [ ] Response received [date]
- [ ] Written agreement obtained [date]
```

---

## Related Skills

- `final-lien-request` - For getting final amounts first
- `supplemental-statement` - For calculating distribution after reduction

---

## Reference Material

For detailed strategies, load:
- `references/erisa-negotiation.md` - ERISA plan negotiation tactics
- `references/compromise-waiver.md` - Medicare compromise/waiver process

