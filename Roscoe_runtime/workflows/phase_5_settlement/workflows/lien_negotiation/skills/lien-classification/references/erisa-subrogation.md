# ERISA Subrogation Reference

## Overview

ERISA (Employee Retirement Income Security Act) governs employer-sponsored health plans. ERISA preempts state law, which significantly impacts lien negotiation strategies.

## Self-Funded vs Fully Insured

### Self-Funded Plans (ERISA Applies)
- Employer bears financial risk for claims
- Third-party administrator (TPA) processes claims
- Federal ERISA law controls exclusively
- Plan language governs recovery rights
- State law defenses (made-whole) generally unavailable

### Fully Insured Plans (State Law May Apply)
- Insurance company bears financial risk
- Insurer both administers and pays claims
- State insurance regulations apply
- Made-whole and common fund doctrines available
- More negotiable

## Identification Questions

1. **Employer size?** Large employers (500+) often self-funded
2. **Who pays claims?** If TPA, likely self-funded
3. **Plan documents state?** Look for "self-funded" or "self-insured"
4. **ERISA statement?** SPD will state if ERISA applies

## Key Plan Language to Review

### Subrogation vs Reimbursement
- **Subrogation**: Plan steps into client's shoes (limits to net recovery)
- **Reimbursement**: Plan has direct claim on proceeds (first-dollar recovery)

### Made-Whole Provision
- Does plan require client to be "made whole" before recovery?
- If silent, US Airways v. McCutchen says plan language controls

### Attorney Fee Provision
- Does plan pay share of attorney fees?
- Common fund doctrine may apply if plan silent

### First-Dollar Language
- "First dollar" = Plan recovers before client gets anything
- Montanile v. Board of Trustees allows strong enforcement

## Reduction Strategies by Plan Type

### Self-Funded ERISA (Limited Options)
| Strategy | Applicability |
|----------|---------------|
| Common fund | May apply if plan silent on fees |
| Dispute unrelated charges | Always available |
| Negotiate courtesy reduction | Plan discretion |
| Equitable defenses | Very limited post-Montanile |

### Fully Insured (More Options)
| Strategy | Applicability |
|----------|---------------|
| Made-whole doctrine | State law applies |
| Common fund doctrine | Automatic 1/3 reduction |
| State insurance regulations | May limit recovery |
| Anti-subrogation statutes | Check state law |

## Key Cases

| Case | Holding |
|------|---------|
| *US Airways v. McCutchen* (2013) | Plan language controls; common fund may apply if silent |
| *Montanile v. Board of Trustees* (2016) | Equitable remedies limited; must trace funds |
| *FMC Corp. v. Holliday* (1990) | ERISA preempts state anti-subrogation laws for self-funded plans |
| *Davila* (2004) | Complete preemption for ERISA benefit claims |

## Obtaining Plan Documents

1. **Request from client**: HR department or benefits portal
2. **Request from plan**: Written request citing 29 CFR § 2520.104b-1
3. **Required documents**: Summary Plan Description (SPD), Plan Document
4. **Timeline**: Plan must provide within 30 days of request

## Data Target

```json
{
  "type": "erisa",
  "plan_type": "self_funded|fully_insured",
  "governing_law": "federal|state",
  "plan_language": {
    "subrogation_type": "reimbursement|subrogation",
    "made_whole": true|false,
    "attorney_fees": true|false,
    "first_dollar": true|false
  },
  "reduction_potential": "limited|moderate|high"
}
```

