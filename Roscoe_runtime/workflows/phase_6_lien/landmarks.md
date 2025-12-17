# Phase 6: Lien Phase - Landmarks

## Overview

Lien Phase landmarks track the resolution of outstanding liens and the final distribution to the client. This phase has two hard blockers: all liens must be resolved and the final distribution must be completed.

---

## Landmark Definitions

### L6.1: Outstanding Liens Identified

**Description:** All liens requiring resolution in this phase have been identified.

**Verification:**
```json
{
  "check_function": "check_outstanding_liens_identified",
  "checks": [
    "liens array has entries with status='outstanding'",
    "Each outstanding lien has holder and type identified"
  ]
}
```

**Typically Satisfied By:**
- Entry to phase (carried from Settlement)

---

### L6.2: Final Lien Amounts Requested

**Description:** Final lien amounts have been requested from all lien holders.

**Verification:**
```json
{
  "check_function": "check_final_amounts_requested",
  "checks": [
    "Every outstanding lien has final_amount_requested_date populated"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `get_final_lien`

---

### L6.3: Medicare Final Demand Received (if applicable)

**Description:** Medicare has issued final demand letter.

**Verification:**
```json
{
  "condition": "lien with type='medicare' exists",
  "check_function": "check_medicare_final_demand",
  "checks": [
    "Medicare lien has final_demand_date populated",
    "Medicare lien has final_amount populated"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `get_final_lien`
- Medicare-specific process

**Note:** Medicare final demand can take 30-60 days after settlement information submitted.

---

### L6.4: Lien Negotiations Complete

**Description:** All negotiable liens have been negotiated.

**Verification:**
```json
{
  "check_function": "check_negotiations_complete",
  "checks": [
    "Every lien has either negotiated_amount OR not_negotiable flag",
    "Negotiation notes documented"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `negotiate_lien`

---

### L6.5: All Liens Paid ⭐ HARD BLOCKER

**Description:** All outstanding liens have been paid.

**Verification:**
```json
{
  "check_function": "check_all_liens_resolved",
  "checks": [
    "Every lien has payment_date populated",
    "Every lien has payment_amount populated",
    "No liens with status='outstanding'"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `negotiate_lien` (payment step)

---

### L6.6: Supplemental Settlement Statement Prepared

**Description:** Final settlement statement prepared showing lien resolution and additional distribution.

**Verification:**
```json
{
  "check_function": "check_supplemental_statement",
  "checks": [
    "Supplemental settlement statement exists",
    "Shows original holdback amount",
    "Shows final lien payments",
    "Shows additional distribution to client"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `final_distribution`

---

### L6.7: Final Distribution Complete ⭐ HARD BLOCKER

**Description:** Additional funds distributed to client.

**Verification:**
```json
{
  "check_function": "check_final_distribution",
  "checks": [
    "Additional distribution check issued",
    "Client received additional funds",
    "Trust account balance is zero"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `final_distribution`

**Triggers:** Phase exit to `closed`

---

## Landmark Progress Summary

| ID | Landmark | Type | Workflow Source |
|----|----------|------|-----------------|
| L6.1 | Liens Identified | Entry | (from Settlement) |
| L6.2 | Amounts Requested | Progress | get_final_lien |
| L6.3 | Medicare Final Demand | Conditional | get_final_lien |
| L6.4 | Negotiations Complete | Progress | negotiate_lien |
| L6.5 | All Liens Paid | Hard Blocker | negotiate_lien |
| L6.6 | Supp. Statement | Progress | final_distribution |
| L6.7 | Final Distribution | Hard Blocker | final_distribution |

---

## Phase Advancement Criteria

**Required to Advance to Closed:**
- ✅ L6.5 (All Liens Paid)
- ✅ L6.7 (Final Distribution Complete)

**Sequential Dependencies:**
- L6.2 must precede L6.4 (need amounts before negotiating)
- L6.4 must precede L6.5 (negotiate before paying)
- L6.5 must precede L6.7 (pay liens before distributing remainder)

---

## Special Considerations

### Medicare Liens
- Federal law priority - must be paid before client distribution
- 60-day payment deadline from final demand
- Procurement cost reduction (1/3) automatic
- Hardship/compromise available but requires application

### ERISA Liens
- Plan language controls
- May require legal analysis for reduction arguments
- Document all negotiation attempts

### State Medicaid Liens
- Contact DMS for final amount
- May have different reduction rules than private insurance

