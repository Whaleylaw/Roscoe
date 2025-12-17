---
name: final-lien-request
description: >
  Request final lien amounts from outstanding lien holders after settlement.
  Use when settlement is complete and liens were held in trust, when needing
  Medicare final demand letter, or when requesting final statements from
  ERISA plans, Medicaid, hospitals, or providers.
---

# Final Lien Request Skill

## Skill Metadata

- **ID**: final-lien-request
- **Category**: lien_phase
- **Model Required**: claude-sonnet-4-20250514 or higher
- **Reference Material**: `references/lien-type-contacts.md`
- **Tools Required**: None

---

## When to Use This Skill

Use this skill when:
- Settlement complete with outstanding liens
- Need final (not conditional) lien amounts
- Medicare final demand required
- ERISA/health insurance final statement needed
- Preparing for final distribution

**DO NOT use if:**
- Still in negotiation phase
- Liens already resolved during settlement
- Just tracking lien amounts (no final needed)

---

## Workflow

### Step 1: Identify Outstanding Liens

List liens needing final amounts:

| Lien Holder | Type | Conditional | Status |
|-------------|------|-------------|--------|
| Medicare | Federal | $X | Need final |
| [ERISA Plan] | Private | $X | Need final |
| Medicaid | State | $X | Need final |
| [Hospital] | Statutory | $X | Need final |

### Step 2: Select Request Method by Type

| Type | Method | Timeline |
|------|--------|----------|
| Medicare | BCRC/MSPRP portal | 30-60 days |
| ERISA | Written request | 2-4 weeks |
| Medicaid | State DMS | 2-4 weeks |
| Hospital | Written request | 1-2 weeks |
| Provider | Written request | 1-2 weeks |

### Step 3: Submit Settlement Information

For all requests, include:
- Settlement amount
- Settlement date
- Attorney fee percentage
- Case costs
- Other liens being paid

### Step 4: Track Responses

Document for each lien:
- Request date
- Response date
- Final amount
- Payment deadline (if any)

**See:** `references/lien-type-contacts.md` for specific contacts.

---

## Medicare Final Demand Process

1. **Report Settlement**
   - Call BCRC: 1-855-798-2627
   - Or use MSPRP portal
   - Submit settlement details

2. **Request Final Demand**
   - Request in writing
   - Allow 30-60 days
   - Follow up if delayed

3. **Verify Procurement Reduction**
   - Should reflect 1/3 reduction
   - If not, request correction

---

## Output Format

```markdown
## Final Lien Status Report

### Requests Submitted

| Lien Holder | Request Date | Method | Status |
|-------------|--------------|--------|--------|
| Medicare | [date] | BCRC phone | Pending |
| [Plan] | [date] | Letter | Received |

### Final Amounts Received

| Lien Holder | Conditional | Final | Difference | Deadline |
|-------------|-------------|-------|------------|----------|
| [Name] | $X | $Y | -$Z | [date] |

### Pending

- [ ] Medicare final demand (expected [date])
- [ ] [Other pending items]
```

---

## Related Skills

- `lien-reduction` - For negotiating final amounts
- `supplemental-statement` - For final distribution calculation

---

## Reference Material

For detailed contacts, load:
- `references/lien-type-contacts.md` - Contact information by lien type

