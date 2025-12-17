---
name: supplemental-statement
description: >
  Prepare supplemental settlement statement for final distribution after liens
  resolved. Use when lien holdback amounts differ from actual payments, when
  preparing additional distribution to client, or when closing trust account
  after lien phase completion.
---

# Supplemental Statement Skill

## Skill Metadata

- **ID**: supplemental-statement
- **Category**: lien_phase
- **Model Required**: claude-sonnet-4-20250514 or higher
- **Reference Material**: `references/calculation-guide.md`
- **Tools Required**: `generate_document.py`

---

## When to Use This Skill

Use this skill when:
- All liens resolved (paid or negotiated)
- Trust account has remaining funds
- Ready to distribute remaining funds to client
- Need to close out lien phase

**DO NOT use if:**
- Liens still outstanding
- Waiting for final amounts
- Settlement statement not yet issued

---

## Workflow

### Step 1: Gather Information

Collect from case file:
- Original settlement statement
- All lien payments made
- Trust account balance
- Original holdback amount

### Step 2: Calculate Distribution

| Item | Amount |
|------|--------|
| Amount Held for Liens | $[holdback] |
| Less: Lien Payments | -$[total_paid] |
| **Additional to Client** | **$[additional]** |

### Step 3: Prepare Statement

Use template:

```
SUPPLEMENTAL SETTLEMENT STATEMENT

Client: [Name]
Case: [Number]
Date: [Date]

═══════════════════════════════════════════════════
ORIGINAL SETTLEMENT (Reference)
═══════════════════════════════════════════════════
Gross Settlement:           $[gross]
Attorney Fee:              -$[fee]
Expenses:                  -$[expenses]
Liens (Held in Trust):     -$[held]
                           ─────────
Initial Net to Client:      $[initial_net]

═══════════════════════════════════════════════════
LIEN RESOLUTION
═══════════════════════════════════════════════════
Amount Held in Trust:       $[held]

Liens Paid:
  Medicare:                -$[medicare_paid]
  [Other Lien]:            -$[other_paid]
                           ─────────
Total Liens Paid:          -$[total_paid]

═══════════════════════════════════════════════════
ADDITIONAL DISTRIBUTION
═══════════════════════════════════════════════════
Remaining from Trust:       $[remaining]

ADDITIONAL TO CLIENT:       $[additional]

═══════════════════════════════════════════════════
TOTAL NET TO CLIENT
═══════════════════════════════════════════════════
Initial Distribution:       $[initial_net]
Additional Distribution:   +$[additional]
                           ─────────
TOTAL NET TO CLIENT:        $[total_net]
```

### Step 4: Verify Trust Balance

After distribution:
- Trust balance should be $0.00
- All liens marked paid
- Case ready to close

**See:** `references/calculation-guide.md` for detailed calculations.

---

## Tool Usage

Copy template to output location, then use `generate_document.py`:

```python
import shutil
from pathlib import Path

# Copy template to destination
project = "Client-Name-MVA-01-01-2025"
dest_folder = Path(f"${ROSCOE_ROOT}/{project}/Documents/Settlement")
dest_folder.mkdir(parents=True, exist_ok=True)

shutil.copy(
    "${ROSCOE_ROOT}/templates/supplemental_settlement_statement_template.md",
    dest_folder / "Supplemental_Settlement_Statement.md"
)
```

```bash
python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
  "${ROSCOE_ROOT}/Client-Name-MVA-01-01-2025/Documents/Settlement/Supplemental_Settlement_Statement.md"
```

---

## Output Format

```markdown
## Supplemental Statement Summary

### Distribution Calculation

| Item | Amount |
|------|--------|
| Original Holdback | $[amount] |
| Liens Actually Paid | $[paid] |
| **Additional to Client** | **$[add]** |

### Trust Account Status

- Opening Balance: $[held]
- Lien Payments: -$[paid]
- Distribution: -$[additional]
- **Closing Balance: $0.00**

### Documents Generated
- [ ] Supplemental Settlement Statement
- [ ] Trust Account Reconciliation
```

---

## Related Skills

- `final-lien-request` - Obtaining final lien amounts
- `lien-reduction` - Negotiating lien reductions
- `settlement-statement` - Original settlement statement

---

## Reference Material

For detailed calculations, load:
- `references/calculation-guide.md` - Step-by-step calculation examples

