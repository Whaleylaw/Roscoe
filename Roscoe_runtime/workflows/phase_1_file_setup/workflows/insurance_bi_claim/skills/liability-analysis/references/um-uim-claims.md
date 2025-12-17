# UM/UIM Claims Analysis

## When to Consider UM/UIM

UM (Uninsured Motorist) and UIM (Underinsured Motorist) claims should be evaluated when:
- BI liability is denied
- At-fault party has no insurance
- At-fault party's limits are insufficient
- Comparative fault reduces BI recovery

## UM vs UIM

| Type | When It Applies |
|------|-----------------|
| **UM** (Uninsured) | At-fault party has no insurance |
| **UIM** (Underinsured) | At-fault's limits insufficient to cover damages |

## Client Coverage Check

To evaluate UM/UIM options:

```
I need the following information:

1. Does client have auto insurance? _______
2. If yes, carrier name: _______
3. Policy number: _______
4. UM/UIM limits (if known): _______

Note: Even if client didn't own a vehicle, they may have:
- Named driver on household policy
- Coverage through spouse/parent
```

## Kentucky UM/UIM Rules

### Stacking
- Kentucky allows stacking of UM/UIM coverage in some cases
- Multiple vehicles on policy may provide additional limits

### Statute of Limitations
- UM/UIM claims may have different deadlines
- Often tied to underlying tort claim deadline

### Subrogation
- UM/UIM carrier may have subrogation rights
- Coordinate with UM/UIM carrier before settling BI

## When UM/UIM Makes Sense

| Scenario | BI Recovery | UM/UIM Recommended |
|----------|-------------|-------------------|
| Liability denied | $0 | Yes - only source |
| At-fault uninsured | $0 | Yes - UM claim |
| At-fault limits $25K, damages $100K | $25K | Yes - UIM for gap |
| Comparative fault 50% | Reduced 50% | Maybe - depends on limits |

## Opening UM/UIM Claim

```json
{
  "insurance": {
    "um_uim": {
      "carrier": "Client's Insurance Co",
      "policy_number": "POL-12345",
      "claim_number": null,
      "claim_type": "UM",
      "reason": "BI liability denied",
      "coverage_limit": 50000,
      "date_claim_opened": null,
      "status": "pending_opening"
    }
  }
}
```

## User Decision

```
Based on the analysis, UM/UIM claim may be appropriate:

Reason: [BI denied / insufficient limits / uninsured at-fault]

Client's UM/UIM coverage: $[limits] (if known)
Estimated damages: $[amount]

Options:
A) Open UM/UIM claim with client's carrier
B) Gather more information about client's coverage first
C) Do not pursue UM/UIM at this time

Which would you like to do?
```

