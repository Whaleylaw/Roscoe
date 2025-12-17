# PIP Disqualification Rules

## When Client is Disqualified

Under Kentucky law (KRS 304.39-040), a person is **DISQUALIFIED** from receiving PIP benefits if:

> The injured person was the owner of an uninsured motor vehicle involved in the accident.

## The Critical Scenario

```
Client was occupying a vehicle
         │
         ▼
Client's name is on the TITLE of that vehicle
         │
         ▼
That vehicle was NOT INSURED
         │
         ▼
⚠️ CLIENT IS DISQUALIFIED FROM PIP
```

## What Disqualification Means

- Client cannot receive PIP benefits from **any source**
- Not from the uninsured vehicle they owned
- Not from their own separate policy (if they have one)
- Not from household member's policy
- Not from Kentucky Assigned Claims

## User Notification

```
⚠️ CLIENT DISQUALIFIED FROM PIP BENEFITS

Reason: Client was occupying a vehicle titled in their name 
that was UNINSURED at the time of the accident.

Under Kentucky law (KRS 304.39-040), the owner of an uninsured 
motor vehicle is NOT entitled to PIP benefits.

IMPLICATIONS:
- No PIP coverage available from any source
- Medical bills cannot be paid through PIP
- Client must rely on:
  • Health insurance
  • Out-of-pocket payment
  • BI settlement from at-fault party (eventually)

This has been documented in the case file.
Focus should be on BI claim against at-fault party.
```

## Data Recording

```json
{
  "pip": {
    "pip_insurer": null,
    "pip_insurer_type": "disqualified",
    "is_disqualified": true,
    "disqualification_reason": "Owner of uninsured motor vehicle",
    "waterfall_date": "2024-12-06",
    "waterfall_path": [
      "Step 1: Client on vehicle title = YES",
      "Step 1a: Vehicle insured = NO",
      "Result: DISQUALIFIED"
    ]
  }
}
```

## Common Questions

### What if client has their own separate auto insurance?
Still disqualified. The disqualification applies because they owned the uninsured vehicle involved.

### What if they were a named driver on someone else's policy?
Still disqualified if they **owned** the uninsured vehicle they were in.

### What if the vehicle was titled jointly?
If client's name appears on the title, they are considered an owner.

### What about KAC?
KAC is not available to disqualified individuals.

## Edge Cases

| Scenario | Disqualified? |
|----------|:-------------:|
| Client on title, vehicle uninsured | **YES** |
| Client on title, vehicle insured | No - PIP from vehicle |
| Client NOT on title, vehicle uninsured | No - continue waterfall |
| Client NOT on title, vehicle insured | No - PIP from vehicle |
| Client owned different uninsured vehicle (not involved) | No |

## Next Steps After Disqualification

1. Document disqualification in case file
2. Inform client (user should communicate this)
3. Focus on BI claim against at-fault party
4. Help client understand payment options for medical bills:
   - Health insurance primary payer
   - Medical payment coverage (if any)
   - Lien arrangements with providers
   - BI settlement distribution

