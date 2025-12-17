# PIP Waterfall Step-by-Step Logic

## Full Waterfall Flow

```
START
  │
  ▼
┌─────────────────────────────────────┐
│ Q1: Is CLIENT'S NAME on the TITLE   │
│     of the vehicle they were in?    │
│     (ownership, not driving)        │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │ YES                 │ NO
    ▼                     ▼
┌───────────────┐    ┌─────────────────────────────┐
│ Q1a: Was that │    │ Q2: Was the vehicle the     │
│ vehicle       │    │ client was in INSURED?      │
│ INSURED?      │    │ (regardless of owner)       │
└───────┬───────┘    └──────────────┬──────────────┘
        │                           │
   ┌────┴────┐                 ┌────┴────┐
   │YES   NO │                 │YES   NO │
   ▼      ▼  │                 ▼      ▼
┌─────┐ ┌────┴──────┐      ┌─────┐ ┌─────────────────────┐
│PIP= │ │DISQUALIFIED│     │PIP= │ │Q3: Does CLIENT have │
│Veh  │ │(See        │     │Veh  │ │OWN auto insurance?  │
│Ins  │ │disqualif.) │     │Ins  │ └──────────┬──────────┘
└─────┘ └───────────┘      └─────┘            │
                                        ┌─────┴─────┐
                                        │YES     NO │
                                        ▼        ▼
                                     ┌─────┐ ┌──────────────────┐
                                     │PIP= │ │Q4: Does HOUSEHOLD│
                                     │Clt  │ │MEMBER have auto  │
                                     │Ins  │ │insurance?        │
                                     └─────┘ └────────┬─────────┘
                                                      │
                                                 ┌────┴────┐
                                                 │YES   NO │
                                                 ▼      ▼
                                              ┌─────┐ ┌─────┐
                                              │PIP= │ │PIP= │
                                              │HH   │ │KAC  │
                                              │Ins  │ └─────┘
                                              └─────┘
```

## Step 1: Vehicle Title Check

**Question:**
```
Is the CLIENT'S NAME on the TITLE of the vehicle they were in 
at the time of the accident?

Note: This is about vehicle ownership, not who was driving.
- Yes
- No
- Don't know (assume No)
```

**If Yes:** Proceed to Step 1a (insurance check)
**If No:** Skip to Step 2

### Step 1a: Client's Titled Vehicle Insurance

**Question (only if Step 1 = Yes):**
```
Was that vehicle INSURED at the time of the accident?
- Yes → Vehicle's insurer provides PIP
- No → CLIENT IS DISQUALIFIED FROM PIP
```

**CRITICAL:** If client owned the vehicle they were in AND it was uninsured → **DISQUALIFIED**

## Step 2: Vehicle Occupied Insurance

**Question:**
```
Was the vehicle the client was in INSURED?
(Regardless of who owns it)
- Yes → Ask for insurance company name and policy
- No → Continue to Step 3
- Unknown → Continue to Step 3
```

**If Yes:** Vehicle's insurer provides PIP
**If No/Unknown:** Continue to Step 3

## Step 3: Client's Own Insurance

**Question:**
```
Does the CLIENT have their OWN auto insurance policy?
(Not the vehicle they were in, their own personal policy)
- Yes → Ask for insurance company name and policy
- No → Continue to Step 4
```

**If Yes:** Client's own insurer provides PIP
**If No:** Continue to Step 4

## Step 4: Household Member Insurance

**Question:**
```
Does any HOUSEHOLD MEMBER have auto insurance?
(Someone living in the same household as the client)
- Yes → Ask for name, insurance company, and policy
- No → Client must use Kentucky Assigned Claims (KAC)
```

**If Yes:** Household member's insurer provides PIP
**If No:** Kentucky Assigned Claims (KAC)

## Result Messages

### Normal Determination
```
✅ PIP CARRIER DETERMINED

PIP Insurer: [Name]
Type: [vehicle/client/household]
Policy: [Number if known]
Waterfall Step: [1-4]

Next Steps:
1. Complete KACP Application (required)
2. Send LOR to PIP carrier
3. Open PIP claim
4. Verify ready to pay bills
```

### KAC Required
```
📋 KENTUCKY ASSIGNED CLAIMS (KAC) REQUIRED

No PIP coverage found through normal channels.
Client must apply through Kentucky Assigned Claims Plan.

Contact:
Kentucky Assigned Claims Plan
P.O. Box 517
Frankfort, KY 40602
Phone: (502) 875-4460

Note: KAC claims may have longer processing times.
```

### Disqualified
```
⚠️ CLIENT DISQUALIFIED FROM PIP BENEFITS

Reason: Client owned an UNINSURED vehicle they were occupying.

Under Kentucky law, owners of uninsured motor vehicles are 
NOT entitled to PIP benefits.

Client must rely on:
- Health insurance
- Out-of-pocket payment
- BI settlement (eventually)
```

