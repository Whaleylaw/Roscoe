---
name: mediation-strategy
description: >
  Execute negotiation strategy at mediation. Handles offer analysis,
  counteroffers, and settlement tactics. Use during mediation session
  to work toward fair settlement.
---

# Mediation Strategy Skill

## Overview

Execute effective negotiation strategy during mediation to achieve optimal settlement.

## When to Use

Use when:
- At mediation session
- Evaluating settlement offers
- Developing counteroffer strategy

DO NOT use if:
- Preparing for mediation (use mediation-prep)
- Direct negotiation outside mediation

## Workflow

### Step 1: Opening Positioning

Present compelling opening:
- Case strengths
- Damage support
- Reasonable demand

### Step 2: Respond to Offers

For each offer:
1. Calculate net to client
2. Compare to case value
3. Advise client
4. Develop counteroffer

**See:** `references/negotiation-tactics.md` for strategies.

### Step 3: Bridge the Gap

Tactics to close:
- Bracketing
- Mediator's proposal
- Creative terms

### Step 4: Confirm Settlement

If settling:
- Document essential terms
- Payment timeline
- Release scope
- Dismissal provisions

**See:** `references/settlement-authority.md` for client guidance.

## Output Format

```markdown
## Mediation Result

**Date:** [Date]
**Outcome:** [Settled / Impasse / Continued]

### If Settled:
- Amount: $[X]
- Payment terms: [Terms]
- Release scope: [Scope]

### If Impasse:
- Final positions: Plaintiff $[X], Defendant $[Y]
- Reason for impasse: [Reason]
- Next steps: [Steps]
```

## Related Skills

- `mediation-prep` - For preparing materials
- `offer-evaluation` - For analyzing settlements

