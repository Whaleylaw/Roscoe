---
name: lien-negotiation
description: >
  Negotiate medical lien reductions to maximize client recovery. Use when
  settlement is pending and liens must be addressed, when calculating
  potential net ranges for client, or when requesting lien reductions
  from Medicare, Medicaid, ERISA plans, hospitals, or providers.
---

# Lien Negotiation Skill

## Skill Metadata

- **ID**: lien-negotiation
- **Category**: negotiation / settlement
- **Model Required**: claude-sonnet-4-20250514 or higher
- **Reference Material**: `references/reduction-strategies.md`
- **Tools Required**: None

---

## When to Use This Skill

Use this skill when:
- Settlement offer received and liens exist
- Calculating potential net recovery scenarios
- Preparing lien reduction requests
- Medicare/Medicaid conditional payments outstanding
- ERISA subrogation claim asserted
- Hospital or provider liens filed

**DO NOT use if:**
- No settlement pending
- Liens not yet identified
- Just tracking lien amounts (handle in case file)

---

## Workflow

### Step 1: Inventory All Liens

Create comprehensive lien list:

| Lien Holder | Type | Amount | Priority | Contact |
|-------------|------|--------|----------|---------|
| Medicare | Federal | $X | High | MSPRC |
| Medicaid | State | $X | High | State agency |
| ERISA Plan | Private | $X | Medium | Plan admin |
| Hospital | Statutory | $X | Medium | Hospital counsel |
| Providers | Contractual | $X | Lower | Each provider |

### Step 2: Prioritize Negotiation Order

1. **Medicare** - Must address first, federal priority
2. **Medicaid** - State law governs, often formula-based
3. **ERISA** - Federal law, "make whole" arguments
4. **Hospital Liens** - Statutory, often negotiable
5. **Provider Liens** - Most flexible, negotiate last

### Step 3: Calculate Reduction Potential

**Target reductions:**
- Medicare: 20-30% (procurement costs)
- Medicaid: Per state formula
- ERISA: 25-50% (common fund/make whole)
- Hospital: 30-50%
- Providers: 40-60%

### Step 4: Prepare Reduction Requests

For each lien holder:
1. Verify lien amount accuracy
2. Challenge improper charges
3. Request pro-rata reduction
4. Cite applicable law/doctrine

### Step 5: Document Agreements

Record all reductions:
```json
{
  "lien_holder": "Medicare",
  "original_amount": 15000,
  "reduction_type": "procurement_cost",
  "reduced_amount": 10500,
  "savings": 4500,
  "date_agreed": "2024-XX-XX"
}
```

---

## Key Arguments by Lien Type

### Medicare

- Procurement cost reduction (1/3 of fees + costs)
- Dispute unrelated charges
- Request final demand letter

### ERISA

- "Make whole" doctrine (if plan silent)
- Common fund doctrine
- Equitable defenses

### Hospital/Provider

- Reasonable settlement argument
- Client hardship
- Limited recovery available

**See:** `references/reduction-strategies.md` for detailed tactics.

---

## Output Format

```markdown
## Lien Reduction Analysis

### Current Liens
| Lien Holder | Original | Target Reduction | Estimated Reduced |
|-------------|----------|------------------|-------------------|
| Medicare | $15,000 | 30% | $10,500 |
| ERISA Plan | $8,000 | 40% | $4,800 |
| Hospital | $12,000 | 35% | $7,800 |
| **Total** | **$35,000** | - | **$23,100** |

### Potential Savings: $11,900

### Strategy
[Outline approach for each lien holder]

### Timeline
[Expected time to resolve each lien]
```

---

## Related Skills

- `offer-evaluation` - For overall settlement analysis
- `lien-classification` - For identifying lien types

---

## Reference Material

For detailed strategies, load:
- `references/reduction-strategies.md` - Specific tactics by lien type

