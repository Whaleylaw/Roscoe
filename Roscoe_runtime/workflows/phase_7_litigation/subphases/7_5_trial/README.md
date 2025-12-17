# Sub-Phase 7.5: Trial

## Overview

**Sub-Phase ID:** `7.5_trial`  
**Parent Phase:** 7 (Litigation)  
**Track:** Litigation

Trial is the culmination of litigation. Includes jury selection, opening statements, presentation of evidence, closing arguments, and verdict. This sub-phase covers the actual trial proceedings.

---

## Entry Triggers

- All pretrial requirements complete
- Trial date arrived
- Trial ready status confirmed

---

## Exit Criteria

| Criterion | Description | Verification |
|-----------|-------------|--------------|
| Trial Concluded | Verdict rendered or other resolution | Court record |

---

## Workflows

| Workflow | Purpose | Path |
|----------|---------|------|
| conduct_trial | Execute trial from opening through verdict | `workflows/conduct_trial/workflow.md` |

---

## Trial Phases

| Phase | Duration | Activities |
|-------|----------|------------|
| Voir Dire | 1-2 hours | Jury selection |
| Opening | 15-30 min each | Case overview |
| Plaintiff's Case | Hours to days | Present evidence |
| Defense Case | Hours to days | Present defense |
| Closing | 30-60 min each | Final argument |
| Deliberation | Hours to days | Jury decides |

---

## Possible Outcomes

| Outcome | Next Step |
|---------|-----------|
| Plaintiff Verdict | → Phase 5 (Settlement) for collection |
| Defense Verdict | → Phase 8 (Closed) or appeal |
| Mistrial | → Retry or settlement |
| Settlement During | → Phase 5 (Settlement) |

---

## Next Phase

**→ Phase 5 Settlement** (for collection/distribution)  
**→ Phase 8 Closed** (if no recovery)

