# Comparative Fault Analysis

## When Partial Liability is Assigned

The BI carrier has assigned comparative fault, reducing the at-fault percentage below 100%.

## Kentucky Comparative Fault Rules

Kentucky uses **pure comparative fault**:
- Client can recover even if 99% at fault
- Recovery reduced by client's percentage of fault
- No threshold that bars recovery entirely

## User Flag Message

```
⚠️ COMPARATIVE FAULT INDICATED

The BI carrier has assigned comparative fault:
- At-fault party: [liability_percentage]%
- Client fault alleged: [100 - liability_percentage]%

Reason: [liability_denial_reason]

IMPLICATIONS:
- BI recovery will be reduced by client's percentage of fault
- Kentucky pure comparative fault allows recovery even at 99% fault
- Additional liable parties may increase total recovery

RECOMMENDED ACTIONS:
1. Review accident details for other potentially liable parties
2. If client was passenger:
   - Check insurance for vehicle client was in
   - Both drivers may share liability
3. Gather evidence disputing client fault
4. Calculate impact on expected recovery

Are there other vehicles/parties involved that may share liability?
```

## Recovery Impact Calculator

| At-Fault % | Client Fault | $100K Damages Recovery |
|------------|--------------|------------------------|
| 100% | 0% | $100,000 |
| 80% | 20% | $80,000 |
| 60% | 40% | $60,000 |
| 50% | 50% | $50,000 |
| 20% | 80% | $20,000 |

## Additional Liable Parties

When comparative fault exists, look for additional liable parties:

### Passenger Cases
- Driver of vehicle client was in
- Driver of other vehicle(s)
- Each may have separate BI coverage

### Multiple Vehicle Accidents
- Each at-fault driver may have BI coverage
- Combined recovery may exceed single policy

### Third-Party Liability
- Property owner (if premises involved)
- Employer (if commercial vehicle)
- Manufacturer (if defect contributed)

## Data to Record

```json
{
  "liability_analysis": {
    "analysis_date": "2024-12-10",
    "status": "partial",
    "at_fault_percentage": 80,
    "client_alleged_fault": 20,
    "fault_reason": "[reason from carrier]",
    "recovery_impact": {
      "if_damages_100k": 80000,
      "reduction_percentage": 20
    },
    "additional_claims_identified": [],
    "user_notified": true
  }
}
```

