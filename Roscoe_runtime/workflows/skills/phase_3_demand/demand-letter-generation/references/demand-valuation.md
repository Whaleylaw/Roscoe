# Demand Valuation Guide

## Overview

Demand valuation requires balancing case facts, injury severity, special damages, and policy limits. This guide provides frameworks for determining appropriate demand amounts.

## Valuation Methods

### Method 1: Policy Limits Demand

**When to Use**:
- Clear liability (90-100%)
- Significant injuries
- Special damages approach or exceed limits
- Surgery or permanent injury

**Application**:
```
If liability is clear AND injuries are serious:
  Demand = Policy limits
```

### Method 2: Multiplier Method

**Formula**:
```
Demand = Special Damages × Multiplier
```

**Multiplier Selection**:

| Injury Severity | Multiplier | Examples |
|-----------------|------------|----------|
| Soft tissue, resolved | 1.5-2.0× | Sprains that heal completely |
| Moderate, prolonged | 2.0-3.0× | Months of treatment, some residual |
| Significant, permanent | 3.0-4.0× | Herniated discs, chronic pain |
| Severe, surgery | 4.0-5.0× | Surgical intervention, long recovery |
| Catastrophic | 5.0+× | Permanent disability, life-altering |

### Method 3: Per Diem

**Formula**:
```
Pain & Suffering = Days of Impact × Daily Rate
Demand = Specials + Pain & Suffering
```

**Daily Rate Guidelines**:
- Minor pain: $50-100/day
- Moderate pain: $100-200/day
- Significant pain: $200-500/day
- Severe/constant: $500+/day

---

## Factors Affecting Value

### Factors That Increase Value

| Factor | Impact |
|--------|--------|
| Surgery performed | Significantly increases |
| Permanent injury | Major increase |
| Clear liability | Supports higher demand |
| Good documentation | Supports full value |
| Sympathetic plaintiff | Jury appeal factor |
| Strong causation | No pre-existing issues |
| Lost wages documented | Adds economic damages |

### Factors That Decrease Value

| Factor | Impact |
|--------|--------|
| Treatment gaps | Questions severity |
| Pre-existing conditions | Comparative value |
| Disputed liability | Risk factor |
| Low policy limits | Recovery cap |
| Poor documentation | Can't prove value |
| Late treatment start | Questions causation |
| Quick resolution | Less suffering |

---

## Kentucky-Specific Considerations

### Comparative Fault

Kentucky uses pure comparative fault (KRS 411.182):
- Client's fault reduces recovery proportionally
- Even 99% at fault can recover 1%
- Consider fault allocation in valuation

### Collateral Source Rule

- Evidence of insurance payments admissible (KRS 411.188)
- May affect jury perception
- Factor into settlement valuation

---

## Policy Limits Strategy

### When Limits Are Known

| Scenario | Strategy |
|----------|----------|
| Specials > Limits | Demand limits |
| Specials ≈ 50% of Limits | Demand limits (strong case) or 75-80% |
| Specials < 25% of Limits | Use multiplier method |

### When Limits Unknown

- Demand "policy limits or $X, whichever is greater"
- Request limits disclosure
- Preserve bad faith claim

---

## Documenting Demand Rationale

Include in attorney notes:

```json
{
  "valuation_method": "multiplier",
  "special_damages": 25000,
  "multiplier": 3.0,
  "calculated_value": 75000,
  "policy_limits": 100000,
  "demand_amount": 75000,
  "rationale": "Significant injuries with surgery, clear liability, 
               demanding 3x specials which is within limits"
}
```

---

## Common Demand Amounts by Case Type

| Case Type | Typical Range | Notes |
|-----------|---------------|-------|
| Minor soft tissue | $5K-$15K | Short treatment, full recovery |
| Moderate soft tissue | $15K-$35K | Prolonged PT, some residual |
| Disc injury (no surgery) | $35K-$75K | MRI findings, injections |
| Disc surgery | $75K-$200K+ | Depends on procedure, outcome |
| Multiple surgeries | $150K+ | Often policy limits |
| TBI/Concussion | $50K-$300K+ | Depends on severity, residuals |

**Note**: These are general guidelines only. Each case requires individual analysis.

---

## Final Checklist

Before setting demand amount:
- [ ] Reviewed all special damages
- [ ] Confirmed policy limits (if known)
- [ ] Assessed liability strength
- [ ] Considered injury severity
- [ ] Factored in treatment duration
- [ ] Evaluated permanency
- [ ] Considered comparative fault
- [ ] Attorney approved valuation

