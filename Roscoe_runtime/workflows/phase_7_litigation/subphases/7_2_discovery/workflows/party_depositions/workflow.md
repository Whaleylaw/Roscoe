---
name: party_depositions
description: >
  Plan and conduct depositions of adverse parties and key witnesses using rules-based
  examination framework. Covers deposition planning, notice drafting, rules-based
  outline preparation, and testimony extraction. Use when taking depositions of
  opposing individual parties and fact witnesses.
phase: 7.2_discovery
workflow_id: party_depositions
related_skills:
  - rules-based-examination
related_tools:
  - generate_document.py
templates:
  - deposition_library/templates/notices/notice_standard.md
  - deposition_library/templates/notices/notice_video.md
  - deposition_library/templates/outlines/outline_rules_based.md
  - deposition_library/templates/tracking/depo_schedule.md
  - deposition_library/templates/tracking/testimony_tracker.md
---

# Party Depositions Workflow

## Overview

Plan, schedule, and conduct depositions of defendants and key witnesses using the rules-based examination framework.

## Entry Criteria

- Written discovery substantially complete
- Key documents obtained
- Issues to explore identified
- Discovery period allows depositions

## Steps

### 1. Identify Deponents

**Owner:** Agent  
**Action:** List all parties and witnesses to depose.

**Deponent Categories:**
- [ ] Individual defendants
- [ ] Corporate representatives (see `corp_rep_deposition` workflow)
- [ ] Defense experts (see `defense_expert_depo` workflow)
- [ ] Third-party witnesses (see `third_party_deposition` workflow)
- [ ] Eyewitnesses

**For this workflow:** Focus on individual adverse parties.

### 2. Create Deposition Schedule

**Owner:** Agent  
**Action:** Create master schedule tracking all depositions.

**Copy Template:**
```bash
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/tracking/depo_schedule.md" \
   "/{project}/Litigation/Discovery/Depo_Schedule.md"
```

**Prioritize:**
1. Individual defendants
2. Key fact witnesses
3. Corporate representatives
4. Experts (later in discovery)

### 3. Schedule Depositions

**Owner:** User  
**Action:** Coordinate with defense counsel on dates and location.

### 4. Identify Rules for Examination

**Owner:** Agent  
**Skill:** `rules-based-examination`  
**Action:** Catalog rules from authoritative sources.

**Sources to Check:**
- Statutes and regulations
- Jury instructions
- Defendant's own policies
- Industry standards
- Common sense principles

**Four-Part Test for Each Rule:**
1. Understandable (plain language)
2. Undeniable (disagreement damages credibility)
3. Violated (clear breach evidence)
4. Important (linked to harm)

**Reference:** `deposition_library/references/rules_framework/rule_discovery.md`

### 5. Draft Deposition Notice

**Owner:** Agent  
**Action:** Prepare and generate notice.

**Document Generation Pattern:**
```bash
# Copy notice template (standard or video)
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/notices/notice_standard.md" \
   "/{project}/Litigation/Discovery/Depo_Notice_[DefendantName].md"

# Agent fills deponent details
# Generate DOCX/PDF
python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
    "/{project}/Litigation/Discovery/Depo_Notice_[DefendantName].md"
```

**For Video Deposition:** Use `notice_video.md` template.

### 6. Prepare Deposition Outline

**Owner:** Agent  
**Skill:** `rules-based-examination`  
**Action:** Create topic outline using rules-based framework.

**Copy Template:**
```bash
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/outlines/outline_rules_based.md" \
   "/{project}/Litigation/Discovery/Depo_Outline_[DefendantName].md"
```

**Outline Structure:**
1. Background (brief)
2. **Rules Establishment (BEFORE facts)**
3. Company policies/training
4. Application to case facts
5. Prior incidents/notice
6. **Closing Gambit**

**Reference:** `deposition_library/references/rules_framework/question_frameworks.md`

### 7. Prepare Exhibits

**Owner:** Agent  
**Action:** Organize documents to use as deposition exhibits.

**Document Categories:**
- Accident/incident reports
- Photographs
- Medical records (key pages)
- Defendant's policies
- Prior correspondence
- Prior statements

### 8. Conduct Deposition

**Owner:** User (Attorney)  
**Action:** Take testimony using rules-based approach.

**Key Approach:**
1. Establish general safety principles **first**
2. Get agreement to common-sense rules
3. **Then** apply to case-specific facts
4. End with closing gambit

**Closing Gambit:**
```
Q. Looking back at this incident, were any mistakes made?

[IF YES:] What mistakes? Why? What's been done to prevent?
[IF NO:] So conduct was as expected? Would do nothing different?
```

### 9. Order Transcript

**Owner:** User  
**Action:** Order transcript from court reporter.

**Options:**
- Expedited (if urgent)
- Regular turnaround
- Rough draft (for immediate review)

### 10. Review and Extract Testimony

**Owner:** Agent  
**Skill:** `rules-based-examination`  
**Action:** Review transcript, extract key testimony.

**Create Testimony Tracker:**
```bash
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/tracking/testimony_tracker.md" \
   "/{project}/Litigation/Discovery/Testimony_Tracker.md"
```

**Extract:**
- Rules established (with page:line)
- Key admissions
- Closing gambit response
- Impeachment opportunities
- Cross-witness inconsistencies

**Reference:** `deposition_library/references/rules_framework/transcript_extraction.md`

## Exit Criteria

- [ ] All necessary depositions completed
- [ ] Transcripts ordered
- [ ] Rules established documented with citations
- [ ] Key testimony extracted
- [ ] Testimony tracker updated
- [ ] Trial preparation notes created

## Templates

| Template | Purpose |
|----------|---------|
| `notice_standard.md` | Standard deposition notice |
| `notice_video.md` | Video deposition notice |
| `outline_rules_based.md` | Rules-based examination outline |
| `depo_schedule.md` | Master deposition schedule |
| `testimony_tracker.md` | Key testimony tracking |

## Related Workflows

- **Related:** `client_deposition_prep` (our client's deposition)
- **Related:** `corp_rep_deposition` (corporate depositions)
- **Related:** `defense_expert_depo` (expert depositions)
- **Related:** `third_party_deposition` (non-party witnesses)
