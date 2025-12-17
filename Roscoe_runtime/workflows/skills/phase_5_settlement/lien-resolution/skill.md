---
name: lien-resolution
description: >
  Resolve and negotiate lien reductions at settlement to maximize client
  recovery. Use when settlement is reached and liens must be paid, when
  calculating lien reduction scenarios, or when preparing lien reduction
  requests to Medicare, Medicaid, ERISA, hospitals, or providers.
---

# Lien Resolution Skill

## Skill Metadata

- **ID**: lien-resolution
- **Category**: settlement
- **Model Required**: claude-sonnet-4-20250514 or higher
- **Reference Material**: `references/medicare-process.md`, `references/medicaid-process.md`
- **Tools Required**: None

---

## When to Use This Skill

Use this skill when:
- Settlement has been reached
- Liens must be paid before distribution
- Calculating lien payment scenarios
- Preparing lien reduction requests
- Need to resolve Medicare, Medicaid, or ERISA liens

**DO NOT use if:**
- Still in negotiation phase (use `lien-negotiation` from Phase 4)
- Just identifying liens (use `lien-classification`)
- No settlement yet reached

---

## Workflow

### Step 1: Compile Final Lien Inventory

List all liens with current amounts:

| Lien Holder | Type | Original | Negotiated | Status |
|-------------|------|----------|------------|--------|
| Medicare | Federal | $X | $Y | Pending |
| Medicaid | State | $X | $Y | Pending |
| ERISA Plan | Private | $X | $Y | Pending |
| Hospital | Statutory | $X | $Y | Pending |
| Providers | LOP | $X | $Y | Pending |

### Step 2: Calculate Distribution Impact

```
Settlement Amount:        $[gross]
Less Attorney Fee:       -$[fee]
Less Case Costs:         -$[costs]
Available for Liens:      $[available]
Total Liens:             -$[liens]
Net to Client:            $[net]
```

### Step 3: Prioritize Resolution Order

1. **Medicare** - Federal priority, must resolve first
2. **Medicaid** - State statutory requirements
3. **ERISA** - Review plan language
4. **Hospital Liens** - Statutory, often negotiable
5. **Provider Liens** - Most flexible

### Step 4: Prepare Final Demands

For each lien holder:
1. Request final lien amount in writing
2. Challenge any unrelated charges
3. Submit settlement details
4. Request reduction based on applicable law

### Step 5: Obtain Satisfaction Letters

Before distributing funds:
- Get written confirmation of final amounts
- Obtain lien satisfaction/release letters
- Verify payment instructions
- Document all agreements

---

## Key Processes

### Medicare Resolution
1. Contact MSPRC for final demand
2. Submit settlement information
3. Request procurement cost reduction
4. Pay agreed amount
5. Obtain satisfaction letter

**See:** `references/medicare-process.md`

### Medicaid Resolution
1. Request final lien from state agency
2. Apply Kentucky statutory formula
3. Submit reduction request
4. Pay agreed amount
5. Obtain release

**See:** `references/medicaid-process.md`

### Provider Resolution
1. Compile all provider liens/LOPs
2. Calculate percentage of settlement
3. Propose reduced amounts
4. Negotiate final figures
5. Get written agreements

---

## Output Format

```markdown
## Lien Resolution Summary

### Final Lien Amounts

| Lien Holder | Original | Final | Savings |
|-------------|----------|-------|---------|
| [Name] | $X | $Y | $Z |
| **Total** | **$X** | **$Y** | **$Z** |

### Distribution

| Line Item | Amount |
|-----------|--------|
| Gross Settlement | $[gross] |
| Attorney Fee | -$[fee] |
| Case Costs | -$[costs] |
| Total Liens | -$[liens] |
| **Net to Client** | **$[net]** |

### Satisfaction Letters
- [ ] Medicare - Received [date]
- [ ] Medicaid - Received [date]
- [ ] [Other] - Received [date]
```

---

## Related Skills

- `lien-classification` - For identifying lien types
- `settlement-statement` - For final distribution calculation

---

## Reference Material

For detailed processes, load:
- `references/medicare-process.md` - Medicare lien resolution
- `references/medicaid-process.md` - Medicaid lien resolution

