---
name: corp_rep_deposition
description: >
  Plan and conduct corporate representative depositions under CR 30.02(6). Covers
  strategic goal identification, topic drafting with reasonable particularity,
  coordinated document requests, and handling know-nothing witnesses. Use when
  deposing corporate defendants to bind them to facts.
phase: 7.2_discovery
workflow_id: corp_rep_deposition
related_skills:
  - corp-rep-deposition
related_tools:
  - generate_document.py
templates:
  - deposition_library/templates/notices/notice_corp_rep.md
  - deposition_library/templates/outlines/outline_corp_rep.md
---

# Corporate Representative Deposition Workflow

## Overview

Plan and conduct CR 30.02(6) corporate representative depositions to bind corporate defendants to facts, verify discovery compliance, and establish foundational rules.

## Entry Criteria

- Corporate defendant named in lawsuit
- Answer filed
- Discovery period open
- Strategic need for corporate testimony identified

## Steps

### 1. Identify Strategic Goals

**Owner:** Agent/User  
**Action:** Determine primary objectives for the deposition.

| Goal | Use When |
|------|----------|
| Discovery Mapping | Need to find documents, custodians |
| Compliance Verification | Discovery responses seem incomplete |
| Document Explanation | Complex documents need context |
| Liability Pin-Down | Need to bind corporation to facts |
| ESI Mapping | Electronic data may be relevant |
| Foundational Rules | Want corporation to endorse standards |

**Reference:** `deposition_library/references/corp_rep/strategic_goals.md`

### 2. Draft Notice Topics

**Owner:** Agent  
**Skill:** `corp-rep-deposition`  
**Action:** Draft topics with "reasonable particularity."

**Each topic must:**
- Allow corporation to identify scope
- Allow selection of appropriate witness
- Allow adequate preparation

**Document Generation Pattern:**
```bash
# Copy notice template
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/notices/notice_corp_rep.md" \
   "/{project}/Litigation/Discovery/Corp_Rep_Notice.md"

# Agent fills topics based on strategic goals
# Generate DOCX/PDF
python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
    "/{project}/Litigation/Discovery/Corp_Rep_Notice.md"
```

**For Insurance Carriers:**
- PIP: Use `notice_corp_rep_pip.md`
- UIM: Use `notice_corp_rep_uim.md`

**Reference:** `deposition_library/references/corp_rep/topic_drafting.md`

### 3. Prepare Coordinated RFP

**Owner:** Agent  
**Action:** Draft RFP aligned with notice topics.

**Timing:** Serve at least 60 days before deposition.
- 30-day response period
- 30-day buffer for motion to compel if needed

### 4. Serve Notice and RFP

**Owner:** User  
**Action:** Serve notice and RFP on defense counsel.

### 5. Prepare Deposition Outline

**Owner:** Agent  
**Skill:** `corp-rep-deposition`  
**Action:** Create topic-by-topic examination outline.

**Copy Template:**
```bash
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/outlines/outline_corp_rep.md" \
   "/{project}/Litigation/Discovery/Corp_Rep_Outline.md"
```

**Include:**
- Opening designation confirmations
- Topic-by-topic questions
- Know-nothing witness handling script
- Document exhibit list

### 6. Conduct Deposition

**Owner:** User (Attorney)  
**Action:** Conduct the deposition.

**Opening Confirmations (on record):**
- Witness designated by corporation
- Testimony binds corporation
- Prepared on each noticed topic

**For Each Topic:**
- Confirm preparation
- Exhaust the topic
- Document any "I don't know" responses

### 7. Handle Know-Nothing Witness

**Owner:** User (Attorney)  
**Action:** If witness cannot answer on noticed topic, build record.

```
Q. You were designated to testify about [topic]?
Q. You cannot answer questions about [topic]?
Q. Did [Corporation] make any effort to prepare you?
Q. So [Corporation's] position is it simply doesn't know?
```

**Reference:** `deposition_library/references/corp_rep/know_nothing.md`

### 8. Post-Deposition Analysis

**Owner:** Agent  
**Action:** Analyze testimony and document outcomes.

**Document:**
- Topics fully addressed
- Topics where witness unprepared (know-nothing)
- Key corporate admissions
- Issues requiring follow-up

### 9. Motion to Compel (if needed)

**Owner:** User  
**Action:** If topics not adequately addressed, file motion.

## Exit Criteria

- [ ] CR 30.02(6) notice served with proper topics
- [ ] Coordinated RFP served (60+ days before)
- [ ] Deposition conducted
- [ ] Corporate testimony obtained or failure documented
- [ ] Key admissions documented with page:line citations

## Templates

| Template | Purpose |
|----------|---------|
| `notice_corp_rep.md` | CR 30.02(6) deposition notice |
| `notice_corp_rep_pip.md` | PIP carrier notice |
| `notice_corp_rep_uim.md` | UIM carrier notice |
| `outline_corp_rep.md` | Topic-by-topic examination outline |

## Related Workflows

- **Related:** `propound_discovery` (written discovery before deposition)
- **Related:** `party_depositions` (individual party depositions)
- **Related:** `defense_expert_depo` (expert depositions)

