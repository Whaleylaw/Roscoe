# Sub-Phase 7.2: Discovery

## Overview

**Sub-Phase ID:** `7.2_discovery`  
**Parent Phase:** 7 (Litigation)  
**Track:** Litigation

The Discovery sub-phase is the formal information-gathering process. Includes written discovery (interrogatories, requests for production, requests for admission), depositions, and document exchanges. Often the longest sub-phase of litigation.

---

## Entry Triggers

- Answer received from defendant
- Scheduling order entered
- Discovery period opened

---

## Exit Criteria

| Criterion | Description | Verification |
|-----------|-------------|--------------|
| Discovery Complete | Discovery cutoff passed or all needed discovery obtained | Per scheduling order |
| Depositions Done | All party depositions completed | Transcripts received |

---

## Resource Libraries

### Discovery Library

Written discovery resources including decision trees, templates, and analysis workflows.

**Location:** `discovery_library/`

| Component | Purpose |
|-----------|---------|
| `propounding/` | Templates for sending discovery |
| `responding/` | Templates for responding to discovery |
| `analysis/` | Workflows for analyzing responses |

### Deposition Library

Comprehensive deposition resources organized by deposition type.

**Location:** `deposition_library/`

| Component | Purpose |
|-----------|---------|
| `decision_tree.md` | Select appropriate deposition type |
| `templates/notices/` | Deposition notice templates |
| `templates/client_prep/` | Client preparation materials |
| `templates/outlines/` | Examination outline frameworks |
| `templates/tracking/` | Schedule and testimony tracking |
| `references/client_defense/` | Client deposition defense guidance |
| `references/corp_rep/` | Corporate representative guidance |
| `references/expert_depo/` | Defense expert deposition playbook |
| `references/rules_framework/` | Rules-based examination framework |
| `skills/` | Deposition-related skills |

---

## Workflows

### Written Discovery

| Workflow | Purpose | Path |
|----------|---------|------|
| propound_discovery | Send written discovery to defendant | `workflows/propound_discovery/workflow.md` |
| respond_to_discovery | Respond to defendant's discovery | `workflows/respond_to_discovery/workflow.md` |
| review_responses | Review and follow up on responses | `workflows/review_responses/workflow.md` |

### Depositions

| Workflow | Purpose | Path |
|----------|---------|------|
| client_deposition_prep | Prepare client for their deposition | `workflows/client_deposition_prep/workflow.md` |
| party_depositions | Take individual party depositions | `workflows/party_depositions/workflow.md` |
| corp_rep_deposition | CR 30.02(6) corporate representative depositions | `workflows/corp_rep_deposition/workflow.md` |
| defense_expert_depo | Defense expert/DME/IME depositions | `workflows/defense_expert_depo/workflow.md` |
| third_party_deposition | Third-party witness depositions | `workflows/third_party_deposition/workflow.md` |

---

## Deposition Types Quick Reference

| Type | When to Use | Workflow | Skill |
|------|-------------|----------|-------|
| Client Defense | Our client noticed for deposition | `client_deposition_prep` | `deposition-defense` |
| Individual Party | Deposing individual defendant | `party_depositions` | `rules-based-examination` |
| Corporate Rep | Deposing corporate defendant | `corp_rep_deposition` | `corp-rep-deposition` |
| Defense Expert | Deposing DME/IME or liability expert | `defense_expert_depo` | `expert-deposition` |
| Third-Party | Deposing non-party witness | `third_party_deposition` | `rules-based-examination` |

See `deposition_library/decision_tree.md` for detailed selection guidance.

---

## Key Deadlines

| Deadline | Rule | Consequence |
|----------|------|-------------|
| Response to discovery | 30 days from service | Waiver of objections |
| Discovery cutoff | Per scheduling order | Evidence excluded |
| Expert disclosure | Per scheduling order | Expert excluded |
| Expert deposition RFP | 60 days before deposition | May not get expert's file |

---

## Discovery Limits (Kentucky)

| Type | Limit |
|------|-------|
| Interrogatories | 30 total (including subparts) |
| Requests for Production | No specific limit |
| Requests for Admission | No specific limit |
| Depositions | 10 per side (without leave) |

---

## Kentucky Rules Quick Reference

| Rule | Application |
|------|-------------|
| CR 26.02(1) | Scope of discovery |
| CR 30.02(1) | Deposition notice requirements |
| CR 30.02(6) | Corporate representative designation |
| CR 30.03(3) | Objection conduct |
| CR 30.04 | Motion to terminate for bad faith |
| CR 32.01 | Deposition use at trial |
| CR 32.04 | Waiver rules for objections |
| CR 33 | Interrogatories |
| CR 34 | Requests for Production |
| CR 36 | Requests for Admission |
| KRE 503 | Attorney-client privilege |
| KRE 803(18) | Learned treatise exception |
| KRE 804 | Former testimony exception |

---

## Next Sub-Phase

**→ 7.3 Mediation** (when discovery substantially complete)
