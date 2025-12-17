---
name: damages-calculation
description: >
  Special damages calculation toolkit for personal injury cases. Compiles medical
  expenses with CPT/ICD codes, calculates lost wages, property damage, and out-of-pocket
  costs. When Claude needs to total medical bills, calculate lost wages, compile
  special damages for demand, or create damages summaries. Use for demand preparation,
  settlement analysis, or case valuation. Not for general damages (pain and suffering)
  which requires attorney judgment.
---

# Damages Calculation Skill

Calculate and compile special damages from case data for demand preparation.

## Capabilities

- Total medical expenses by provider
- Extract CPT and ICD-10 codes from bills
- Calculate lost wages from employment records
- Compile property damage costs
- Track out-of-pocket expenses
- Generate damages summary tables

**Keywords**: special damages, medical bills, CPT codes, ICD codes, lost wages, property damage, damages calculation, medical expenses, demand preparation

## Damage Categories

| Category | Data Source | Calculation |
|----------|-------------|-------------|
| Past Medical | `medical_providers.json` bills | Sum all itemized charges |
| Future Medical | Physician estimate or LCP | Document amount |
| Past Lost Wages | Pay stubs + off-work notes | Days × daily rate |
| Future Lost Wages | Disability assessment | Document if applicable |
| Property Damage | Repair estimate or total loss | Document amount |
| Out-of-Pocket | Client receipts | Sum documented expenses |

## Workflow

```
1. COMPILE MEDICAL BILLS
   └── For each provider in medical_providers.json
       └── Extract total charges
       └── Extract CPT codes
       └── Extract ICD-10 codes
       └── Note date range

2. CALCULATE LOST WAGES
   └── Verify off-work notes exist
   └── Calculate daily rate
   └── Multiply by days missed

3. COMPILE OTHER DAMAGES
   └── Property damage (if applicable)
   └── Out-of-pocket expenses

4. GENERATE SUMMARY
   └── Update expenses.json
   └── Generate damages table
```

## Medical Expenses Calculation

### Per Provider Entry

```json
{
  "provider_id": 1,
  "provider_name": "Baptist Health ER",
  "dates_of_service": "04/26/2024",
  "total_charges": 3500.00,
  "cpt_codes": ["99284", "72131", "73030"],
  "icd_codes": ["S13.4XXA", "M54.2"],
  "paid_by_insurance": 2800.00,
  "patient_responsibility": 700.00
}
```

### CPT Code Categories

| Range | Category | Examples |
|-------|----------|----------|
| 99201-99499 | E/M (Office visits) | 99213, 99214, 99284 |
| 97110-97799 | Physical therapy | 97110, 97140, 97530 |
| 20550-29999 | Musculoskeletal | Injections, procedures |
| 64400-64999 | Nerve blocks | Epidurals, facet injections |
| 72XXX | Spine imaging | 72141 (MRI), 72100 (X-ray) |

## Lost Wages Calculation

### Required Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| Off-work notes | Physician authorization | Medical records |
| Pay stubs | Pre-accident income | Client documents |
| W-2/Tax returns | Income verification | Client documents |
| Employer letter | Missed time confirmation | Request from employer |

### Calculation Methods

**Hourly Employee**:
```
Daily Rate = Hourly Rate × Hours/Day
Lost Wages = Days Missed × Daily Rate
```

**Salaried Employee**:
```
Daily Rate = Annual Salary / 260 (working days)
Lost Wages = Days Missed × Daily Rate
```

**Self-Employed**:
```
Use average daily revenue from tax returns
Document lost contracts/jobs if applicable
```

## Output Format

### expenses.json Structure

```json
{
  "special_damages": {
    "medical_expenses": {
      "total": 25000.00,
      "by_provider": [...],
      "by_category": {
        "emergency": 3500.00,
        "specialist": 8000.00,
        "physical_therapy": 6500.00,
        "imaging": 3500.00,
        "injections": 3500.00
      }
    },
    "lost_wages": {
      "past": 9000.00,
      "future": 0.00,
      "calculation": "45 days × $200/day"
    },
    "property_damage": {
      "vehicle_repair": 5500.00,
      "rental": 800.00,
      "total": 6300.00
    },
    "out_of_pocket": {
      "mileage": 450.00,
      "prescriptions": 320.00,
      "total": 770.00
    },
    "grand_total": 41070.00
  }
}
```

## References

For detailed guidance:
- **CPT/ICD extraction** → `references/code-extraction.md`
- **Wage calculation** → `references/wage-calculation.md`

## Output

- Updated `expenses.json` with complete special damages
- Damages summary table for demand letter
- Supporting calculation documentation

