# Sub-Phase 7.3: Mediation

## Overview

**Sub-Phase ID:** `7.3_mediation`  
**Parent Phase:** 7 (Litigation)  
**Track:** Litigation

Mediation is a formal settlement conference facilitated by a neutral mediator. In many Kentucky courts, mediation is required before trial. This sub-phase covers preparation and attendance of mediation.

---

## Entry Triggers

- Discovery substantially complete
- Court orders mediation
- Parties agree to mediate

---

## Exit Criteria

| Criterion | Description | Verification |
|-----------|-------------|--------------|
| Mediation Attended | Mediation occurred (regardless of outcome) | Mediator report filed |

---

## Workflows

| Workflow | Purpose | Path |
|----------|---------|------|
| prepare_mediation | Prepare brief and client for mediation | `workflows/prepare_mediation/workflow.md` |
| attend_mediation | Attend and negotiate at mediation | `workflows/attend_mediation/workflow.md` |

---

## Possible Outcomes

| Outcome | Next Step |
|---------|-----------|
| Full Settlement | → Phase 5 (Settlement) |
| Partial Settlement | → Resolve remaining issues |
| Impasse | → 7.4 Trial Prep |
| Mediator's Proposal | Respond within deadline |

---

## Next Sub-Phase

**→ 7.4 Trial Prep** (if no settlement)  
**→ Phase 5 Settlement** (if settled)

