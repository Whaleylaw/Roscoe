# Net to Client Calculation Details

## Overview

This reference provides detailed formulas and considerations for calculating the net amount a client would receive from a settlement offer.

---

## Basic Formula

```
Net to Client = Gross Settlement - Attorney Fee - Case Costs - Liens
```

---

## Attorney Fee Calculation

### Pre-Litigation (Standard)

```
Attorney Fee = Gross Settlement × 0.3333 (33⅓%)
```

### Post-Litigation (After Filing)

```
Attorney Fee = Gross Settlement × 0.40 (40%)
```

### Fee Agreement Variations

Always check the actual fee agreement for:
- Sliding scale fees (higher % for larger recoveries)
- Referral fee splits
- Enhanced fees for appellate work
- Reduced fees for quick settlements

---

## Case Costs

### Common Cost Categories

| Category | Examples |
|----------|----------|
| Medical Records | $50-500 per provider |
| Filing Fees | $200-500 |
| Service of Process | $50-100 per defendant |
| Expert Fees | $1,000-10,000+ |
| Deposition Costs | $500-2,000 per deposition |
| Court Reporter | $300-1,000 |
| Mediation Fees | $500-3,000 |
| Postage/Copies | $100-500 |

### Cost Tracking

Pull total costs from case file:
- `case_expenses.json` if maintained
- Or itemize from records

---

## Medical Liens

### Lien Types to Include

| Lien Type | Priority | Negotiable? |
|-----------|----------|-------------|
| Medicare | High | Limited (MSPRC) |
| Medicaid | High | By statute |
| ERISA Plans | Medium | Yes (federal law) |
| Hospital Liens | Medium | Yes |
| Provider Liens | Lower | Often negotiable |
| Health Insurance | Varies | Subrogation rules apply |

### Lien Calculation

```
Total Liens = Medicare + Medicaid + ERISA + Hospital + Provider + Other
```

**Important:** Use actual lien amounts, not estimated. If amounts unknown, flag as estimated.

---

## Net Calculation Example

### Scenario

- Offer: $75,000
- Fee Rate: 33.33% (pre-litigation)
- Case Costs: $3,500
- Medicare Lien: $8,000
- Hospital Lien: $12,000
- Provider Liens: $5,000

### Calculation

```
Gross Settlement:          $75,000.00
Less: Attorney Fee (33%):  -$25,000.00
Less: Case Costs:           -$3,500.00
Less: Medicare Lien:        -$8,000.00
Less: Hospital Lien:       -$12,000.00
Less: Provider Liens:       -$5,000.00
                          ────────────
Net to Client:             $21,500.00
```

### Net as Percentage

```
Net % = (Net to Client / Gross Settlement) × 100
Net % = ($21,500 / $75,000) × 100 = 28.7%
```

---

## Scenarios to Present

### Best Case (Liens Negotiated)

If liens reduced by 30%:
```
Reduced Liens = $25,000 × 0.70 = $17,500
Savings = $7,500
New Net = $29,000
```

### Worst Case (Full Liens)

As calculated above: Net = $21,500

### Range to Client

"Your net recovery would be approximately $21,500 to $29,000 depending on lien negotiations."

---

## Red Flags

### Client Would Owe Money

If calculation results in negative net:
- Client owes money even with settlement
- Discuss with attorney immediately
- May need higher offer or lien negotiation

### Net Less Than Medical Bills Paid

If client's out-of-pocket exceeds net:
- Explain recovery vs. expenses
- Discuss non-economic compensation
- Consider whether to proceed

---

## Documentation

Record all calculations in:
```json
{
  "offer_analysis": {
    "offer_amount": 75000,
    "attorney_fee_rate": 0.3333,
    "attorney_fee": 25000,
    "case_costs": 3500,
    "liens": {
      "medicare": 8000,
      "hospital": 12000,
      "provider": 5000,
      "total": 25000
    },
    "net_to_client": 21500,
    "analysis_date": "2024-XX-XX"
  }
}
```

