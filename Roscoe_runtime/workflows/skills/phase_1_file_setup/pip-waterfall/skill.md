---
name: pip-waterfall
description: >
  Kentucky PIP carrier determination toolkit for walking through statutory waterfall 
  questions, identifying the correct insurer, and detecting disqualification scenarios. 
  Asks structured questions about vehicle title, vehicle insurance, client insurance, 
  and household insurance. When Claude needs to determine which insurance company 
  provides PIP coverage, run PIP waterfall analysis, check if client qualifies for 
  PIP benefits, or identify Kentucky Assigned Claims scenarios. Use for all Kentucky 
  MVA cases before opening PIP claims. Not for non-MVA cases, out-of-state accidents, 
  or when PIP carrier is already determined.
---

# PIP Waterfall Skill

Determine the correct PIP carrier using Kentucky's statutory waterfall rules.

## Capabilities

- Guide user through waterfall questions
- Run `pip_waterfall.py` tool
- Determine PIP carrier or KAC assignment
- Identify disqualification scenarios
- Record determination for case file

**Keywords**: PIP, Personal Injury Protection, waterfall, Kentucky, KAC, Kentucky Assigned Claims, no-fault, medical payments, vehicle insurance, disqualified

## Waterfall Summary

```
Q1: Client on vehicle TITLE?
    ├── YES → Is vehicle INSURED?
    │         ├── YES → Vehicle's insurer = PIP
    │         └── NO → ⚠️ DISQUALIFIED
    └── NO → Q2

Q2: Was vehicle occupied INSURED?
    ├── YES → Vehicle's insurer = PIP
    └── NO → Q3

Q3: Does CLIENT have own auto insurance?
    ├── YES → Client's insurer = PIP
    └── NO → Q4

Q4: Does HOUSEHOLD MEMBER have auto insurance?
    ├── YES → Household insurer = PIP
    └── NO → Kentucky Assigned Claims (KAC)
```

## Quick Questions

| Step | Question | If Yes | If No |
|------|----------|--------|-------|
| 1 | Client on title of vehicle they were in? | Check if insured | Go to Q2 |
| 1a | (If Q1=Yes) Was that vehicle insured? | Vehicle's PIP | **DISQUALIFIED** |
| 2 | Was vehicle occupied insured? | Vehicle's PIP | Go to Q3 |
| 3 | Does client have own auto insurance? | Client's PIP | Go to Q4 |
| 4 | Does household member have insurance? | Household PIP | KAC |

## Tool

**Tool**: `tools/pip_waterfall.py`

```bash
python pip_waterfall.py --interactive
```

```python
from pip_waterfall import run_waterfall
result = run_waterfall(client_on_title=False, vehicle_insured=True, ...)
```

## Output Patterns

**Normal**: `✅ PIP CARRIER DETERMINED: [Insurer Name]`  
**KAC**: `📋 KENTUCKY ASSIGNED CLAIMS REQUIRED`  
**Disqualified**: `⚠️ CLIENT DISQUALIFIED FROM PIP BENEFITS`

## References

For detailed guidance, see:
- **Waterfall logic** → `references/waterfall-steps.md`
- **Disqualification rules** → `references/disqualification.md`
- **KAC process** → `references/kac-process.md`
- **Tool usage** → `references/tool-usage.md`

## Output

- PIP carrier determined
- Waterfall path documented
- Result saved to insurance.json
