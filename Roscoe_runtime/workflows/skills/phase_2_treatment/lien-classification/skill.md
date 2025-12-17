---
name: lien-classification
description: >
  Lien identification and classification toolkit for personal injury cases. Determines
  lien type, governing law, ERISA status, and reduction potential for Medicare, Medicaid,
  ERISA health plans, hospital liens, and letters of protection. When Claude needs to
  identify potential liens on a case, classify lien types by legal basis, determine
  subrogation rights, assess made-whole doctrine applicability, or develop lien reduction
  strategies. Use for lien analysis during treatment phase, pre-settlement planning, or
  final distribution calculations. Not for lien negotiation execution (see settlement
  phase) or payment processing.
---

# Lien Classification Skill

Classify liens by type, governing law, and reduction potential for personal injury cases.

## Capabilities

- Identify lien sources (government, private insurance, provider)
- Determine ERISA vs state law applicability
- Assess made-whole and common fund defenses
- Calculate reduction potential by lien type
- Create lien inventory for case tracking

**Keywords**: lien, subrogation, Medicare, Medicaid, ERISA, hospital lien, letter of protection, LOP, made-whole, common fund, reimbursement, health insurance lien

## Workflow

```
1. IDENTIFY LIEN SOURCES
   └── Check: health insurance, Medicare/Medicaid, hospital, providers

2. CLASSIFY EACH LIEN
   └── Government → See references/medicare-liens.md or references/medicaid-liens.md
   └── Private Insurance → Determine ERISA status
       └── Self-funded → See references/erisa-subrogation.md
       └── Fully insured → State law applies
   └── Provider → See references/provider-liens.md

3. ASSESS REDUCTION POTENTIAL
   └── Apply classification table below

4. UPDATE CASE FILE
   └── Add entries to liens.json with classification
```

## Quick Classification Reference

| Lien Type | Governing Law | Reduction Potential |
|-----------|---------------|---------------------|
| Medicare | Federal MSP Act | Formula-based (procurement costs ~35%) |
| Medicaid | State law | State-specific, often 50%+ |
| ERISA Self-Funded | Federal ERISA | Plan language controls, often limited |
| Fully Insured | State law | Made-whole + common fund apply |
| Hospital Statutory | KRS 216.935 | Limited by statute |
| Letter of Protection | Contract | Highly negotiable (30-50%) |

## ERISA Quick Test

1. **Is it employer-sponsored?** If no → State law applies
2. **Is employer self-funded or fully insured?**
   - Self-funded indicators: Large employer, TPA administrator, "self-insured" in docs
   - Fully insured indicators: Small employer, insurance company is payor
3. **Self-funded = Federal ERISA controls** (harder to reduce)
4. **Fully insured = State law may apply** (made-whole doctrine available)

## Tool

No specialized tool required. Updates `liens.json` directly.

```json
{
  "id": 123,
  "type": "health_insurance",
  "holder": "Blue Cross Blue Shield",
  "asserted_amount": 15000,
  "classification": {
    "legal_basis": "erisa_self_funded",
    "governing_law": "federal",
    "reduction_potential": "limited",
    "defenses_available": ["common_fund"]
  },
  "status": "identified"
}
```

## References

For detailed guidance on specific lien types:
- **Medicare liens** → `references/medicare-liens.md`
- **Medicaid liens** → `references/medicaid-liens.md`
- **ERISA subrogation** → `references/erisa-subrogation.md`
- **Provider liens** → `references/provider-liens.md`

## Output

- Lien entries added to `liens.json` with full classification
- Classification includes: type, legal basis, governing law, reduction potential
- Triggers settlement planning when all liens identified

