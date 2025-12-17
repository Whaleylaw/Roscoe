---
name: settlement-statement
description: >
  Prepare comprehensive settlement statements showing gross settlement,
  deductions, and net to client. Use when settlement is reached and
  distribution must be calculated, when preparing authorization to settle,
  or when explaining distribution to client.
---

# Settlement Statement Skill

## Skill Metadata

- **ID**: settlement-statement
- **Category**: settlement
- **Model Required**: claude-sonnet-4-20250514 or higher
- **Reference Material**: `references/fee-calculation.md`, `references/trust-requirements.md`
- **Tools Required**: `generate_document.py`

---

## When to Use This Skill

Use this skill when:
- Settlement has been reached
- Need to calculate net to client
- Preparing authorization to settle document
- Explaining distribution breakdown to client
- Creating final settlement accounting

**DO NOT use if:**
- Settlement not yet reached (estimating during negotiation)
- Just evaluating offers (use `offer-evaluation`)
- No actual settlement amount confirmed

---

## Workflow

### Step 1: Gather Settlement Information

Collect:
- Gross settlement amount
- Settlement date
- Fee agreement terms
- All case costs/expenses
- All liens (final amounts)

### Step 2: Determine Fee Rate

**Pre-Litigation (Standard):** 33.33%
**Post-Litigation (Standard):** 40%

Always verify against actual fee agreement.

**See:** `references/fee-calculation.md`

### Step 3: Itemize Case Costs

| Cost Category | Common Items |
|---------------|--------------|
| Filing fees | Complaint, motions |
| Service | Process server |
| Records | Medical records fees |
| Postage | Certified mail |
| Expert fees | If applicable |
| Deposition | Court reporter |
| Other | Case-specific |

### Step 4: List All Liens

| Lien Type | Include |
|-----------|---------|
| Medicare | Final negotiated amount |
| Medicaid | Final negotiated amount |
| ERISA/Health | Final negotiated amount |
| Hospital | Final negotiated amount |
| Provider | Final negotiated amount |

### Step 5: Calculate Distribution

```
SETTLEMENT STATEMENT

Gross Settlement:                    $[gross]

DEDUCTIONS:
Attorney Fee ([rate]%):             -$[fee]
Case Costs (itemized):              -$[costs]
  - Medical records                  $[amount]
  - Filing fees                      $[amount]
  - [Other costs]                    $[amount]
Liens (itemized):                   -$[liens]
  - [Lien holder 1]                  $[amount]
  - [Lien holder 2]                  $[amount]
                                    ─────────
NET TO CLIENT:                       $[net]
```

### Step 6: Generate Document

```python
import shutil
from pathlib import Path

# Copy template to output location
templates_dir = Path("${ROSCOE_ROOT}/templates")
project = "John-Doe-MVA-01-01-2025"

dest_folder = Path(f"${ROSCOE_ROOT}/{project}/Documents/Settlement")
dest_folder.mkdir(parents=True, exist_ok=True)

shutil.copy(
    templates_dir / "settlement_statement_template.md",
    dest_folder / "Settlement_Statement.md"
)

# Generate document
import sys
sys.path.insert(0, "${ROSCOE_ROOT}/Tools/document_generation")
from generate_document import generate_document

result = generate_document(
    f"${ROSCOE_ROOT}/{project}/Documents/Settlement/Settlement_Statement.md"
)
```

---

## Fee Calculation

### Pre-Litigation
```
Attorney Fee = Gross × 0.3333
```

### Post-Litigation
```
Attorney Fee = Gross × 0.40
```

### Hybrid (if applicable)
Some fee agreements have staged rates:
- 33.33% if settled before litigation
- 40% if settled after filing
- 45% if settled after trial begins

**See:** `references/fee-calculation.md` for complex scenarios.

---

## Trust Account Requirements

Kentucky KRPC 1.15 requires:
- Settlement funds to trust account
- Hold until check clears
- Pay liens before distribution
- Maintain detailed records

**See:** `references/trust-requirements.md`

---

## Output Format

```markdown
## Settlement Statement

**Client:** [Name]
**Date of Accident:** [Date]
**Date of Settlement:** [Date]
**Claim Type:** [BI/UM/etc.]

### Distribution

| Item | Amount |
|------|--------|
| Gross Settlement | $[gross] |
| Attorney Fee ([%]) | -$[fee] |
| Case Costs | -$[costs] |
| Liens | -$[liens] |
| **Net to Client** | **$[net]** |

### Costs Detail
[Itemized list]

### Liens Detail
[Itemized list]

### Signatures
_________________________
Client Signature     Date

_________________________
Attorney Signature   Date
```

---

## Related Skills

- `lien-resolution` - For finalizing lien amounts
- `docusign-send` - For getting client signature

---

## Reference Material

For detailed information, load:
- `references/fee-calculation.md` - Fee calculation scenarios
- `references/trust-requirements.md` - Kentucky trust account rules

