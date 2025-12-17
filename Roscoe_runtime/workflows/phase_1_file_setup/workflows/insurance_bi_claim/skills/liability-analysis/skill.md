---
name: liability-analysis
description: >
  Liability determination analysis toolkit for evaluating insurance carrier responses 
  and identifying additional claim opportunities. Flags user when liability is not 
  100% accepted, analyzes comparative fault implications, identifies UM/UIM claim 
  needs, and handles passenger multi-vehicle scenarios. When Claude needs to evaluate 
  a liability determination, assess comparative fault impact, identify additional 
  liable parties, or recommend UM/UIM claims. Use when BI carrier responds with 
  anything other than full liability acceptance. Not for liability investigation 
  before carrier response or for non-MVA cases.
---

# Liability Analysis Skill

Analyze liability determinations from insurance carriers and flag potential additional claims.

## Capabilities

- Analyze liability status (accepted/denied/partial/investigating)
- Flag user when liability not 100% accepted
- Identify UM/UIM claim opportunities
- Analyze passenger scenarios with multiple vehicles
- Recommend evidence gathering for disputed cases

**Keywords**: liability, comparative fault, UM, UIM, underinsured, uninsured, denied liability, partial fault, passenger claim, multiple vehicles, fault determination

## Workflow

```
1. RECEIVE LIABILITY STATUS
   └── Record: status, percentage, reason, date

2. ANALYZE IMPLICATIONS
   └── Denied → See references/denied-liability.md
   └── Partial → See references/comparative-fault.md
   └── Investigating → Schedule follow-up

3. FLAG USER (if not 100% accepted)
   └── Present implications
   └── Identify additional claim options
   └── Recommend next steps

4. DOCUMENT ANALYSIS
   └── Save to insurance.json → liability_analysis
```

## Liability Status Values

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| `accepted` | 100% liability accepted | Proceed normally |
| `denied` | Carrier denies liability | **FLAG USER** - UM/UIM analysis |
| `partial` | Comparative fault | **FLAG USER** - reduced recovery |
| `investigating` | Still determining | Schedule 7-14 day follow-up |

## Quick Decision Tree

```
Liability Status Received
         │
    ┌────┴────┐
    │         │
  100%?     <100%
    │         │
    ▼         ▼
 Proceed   FLAG USER
           ├── Denied? → UM/UIM check
           ├── Partial? → Calculate impact
           └── Passenger? → Check all vehicles
```

## User Flag Template

```
⚠️ LIABILITY NOT FULLY ACCEPTED

Status: [liability_status]
At-fault percentage: [liability_percentage]%
Reason: [liability_denial_reason]

IMPLICATIONS:
[See references for detailed implications by status type]

RECOMMENDED ACTIONS:
1. [Action 1]
2. [Action 2]
3. [Action 3]

Do you want me to help analyze potential additional claims?
```

## References

For detailed guidance, see:
- **Denied liability** → `references/denied-liability.md`
- **Comparative fault** → `references/comparative-fault.md`
- **Passenger analysis** → `references/passenger-scenarios.md`
- **UM/UIM claims** → `references/um-uim-claims.md`
- **Evidence gathering** → `references/evidence-recommendations.md`

## Output

- Liability analysis documented in insurance.json
- User flagged if action needed
- Additional claims identified
- Evidence recommendations provided
