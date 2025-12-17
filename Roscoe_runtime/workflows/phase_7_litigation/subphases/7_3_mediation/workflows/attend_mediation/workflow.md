---
name: attend_mediation
description: >
  Attend and negotiate at mediation session. Executes negotiation strategy,
  responds to offers, works toward settlement. Use on mediation day to
  maximize settlement opportunity.
phase: 7.3_mediation
workflow_id: attend_mediation
related_skills:
  - mediation-strategy
templates:
  - settlement_terms.md
---

# Attend Mediation Workflow

## Overview

Conduct effective mediation session with goal of achieving fair settlement.

## Entry Criteria

- Mediation brief submitted
- Client prepared
- Settlement authority confirmed

## Steps

### 1. Opening Session

**Owner:** User (Attorney)  
**Action:** Present opening statement, establish case value.

### 2. Private Caucuses

**Owner:** User (Attorney)  
**Skill:** `mediation-strategy`  
**Action:** Negotiate through mediator, adjust positions strategically.

### 3. Evaluate Offers

**Owner:** Agent/User  
**Action:** Analyze each offer, calculate net to client, advise client.

### 4. Client Consultations

**Owner:** User  
**Action:** Keep client informed, get authority for positions.

### 5. Work Toward Resolution

**Owner:** User (Attorney)  
**Action:** Use negotiation tactics to bridge gap.

### 6. Document Outcome

**Owner:** Agent  
**Action:** Document settlement terms or impasse result.

## Exit Criteria

- [ ] Mediation attended
- [ ] Outcome documented
- [ ] If settled: terms confirmed in writing
- [ ] If impasse: next steps identified

## Templates

| Template | Purpose |
|----------|---------|
| `settlement_terms.md` | Document settlement agreement |

## Related Workflows

- **Triggered By:** `prepare_mediation`
- **Triggers:** Settlement Phase (if settled) or 7.4 Trial Prep (if impasse)

