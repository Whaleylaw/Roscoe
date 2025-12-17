# Medicare Lien Reference

## Overview

Medicare liens arise under the Medicare Secondary Payer (MSP) Act when Medicare pays for injury-related treatment that should be covered by a liability settlement.

## Governing Law

- **Federal**: Medicare Secondary Payer Act, 42 U.S.C. § 1395y(b)
- Medicare has a direct right of action against beneficiaries and attorneys
- Federal law preempts state law defenses

## Identification

Medicare involvement exists when:
- Client is 65+ years old
- Client is disabled and receiving SSDI
- Client has End Stage Renal Disease (ESRD)

## Conditional Payment Process

1. **Register Case**: Submit to Medicare Secondary Payer Recovery Contractor (MSPRC)
2. **Obtain Conditional Payment Letter**: Lists all payments potentially related to accident
3. **Dispute Unrelated Charges**: Challenge any payments not causally related
4. **Request Final Demand**: After settlement, request final conditional payment amount

## Reduction Formula

Medicare must reduce its claim by procurement costs (attorney fees + litigation costs):

```
Example:
Gross Settlement: $100,000
Attorney Fees (33%): $33,000
Litigation Costs: $2,000
Total Procurement: $35,000 (35%)

Medicare Conditional Payment: $15,000
Reduction: $15,000 × 35% = $5,250
Final Medicare Lien: $9,750
```

## Timeline

| Stage | Timeframe |
|-------|-----------|
| Initial CP Letter | 2-4 weeks after request |
| Dispute Response | 30 days after receipt |
| Final Demand | Request within 120 days of settlement |
| Payment Due | 60 days after final demand |

## Key Contacts

- **MSPRC**: 1-855-798-2627
- **Website**: www.cob.cms.hhs.gov

## Common Issues

| Issue | Resolution |
|-------|------------|
| Unrelated charges included | Submit detailed dispute with medical records |
| Final demand higher than expected | Review for duplicate payments or errors |
| Client won't sign authorization | Explain federal reporting requirements |
| Settlement less than Medicare lien | Negotiate hardship reduction |

## Data Target

```json
{
  "type": "medicare",
  "governing_law": "federal",
  "reduction_formula": "procurement_costs",
  "typical_reduction": "35%"
}
```

