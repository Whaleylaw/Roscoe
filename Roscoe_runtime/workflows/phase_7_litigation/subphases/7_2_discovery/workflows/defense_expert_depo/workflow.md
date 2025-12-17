---
name: defense_expert_depo
description: >
  Plan and conduct defense expert depositions (DME/IME, liability experts). Covers
  dossier compilation, conflict mapping by juror archetype, trial preservation under
  KRE 804, and conflict-focused examination. Treats expert depositions as trial testimony.
phase: 7.2_discovery
workflow_id: defense_expert_depo
related_skills:
  - expert-deposition
related_tools:
  - generate_document.py
templates:
  - deposition_library/templates/notices/notice_expert.md
  - deposition_library/templates/outlines/outline_expert.md
---

# Defense Expert Deposition Workflow

## Overview

Plan and conduct defense expert depositions with focus on creating conflicts for trial impeachment. Philosophy: treat expert depositions as trial testimony.

## Entry Criteria

- Defendants disclosed expert witness
- Expert disclosure/report received
- Deposition date scheduled (or need to schedule)
- Discovery period allows expert depositions

## Steps

### 1. Serve Expert Discovery (60-Day Rule)

**Owner:** Agent  
**Action:** Prepare and serve discovery at least 60 days before deposition.

**Expert Interrogatory (CR 26.02(4)):**
- Expert's specialty
- Materials reviewed
- Each opinion with grounds

**Document Request (RFP):**
- Complete file and notes
- Correspondence with defense counsel
- Draft reports
- Publications relied upon
- Compensation records
- Prior testimony list (4 years)

**Privilege Log Interrogatory:**
- If materials withheld, demand privilege log
- Deficient log = waiver under *Baptist Healthcare v. Goodman*

### 2. Compile Expert Dossier

**Owner:** Agent  
**Skill:** `expert-deposition`  
**Action:** Research expert and compile dossier.

**Database Searches:**
- [ ] TrialSmith - Prior testimony
- [ ] Crowdsource Depos - Transcripts
- [ ] PACER/State ECF - Court filings

**Publications:**
- [ ] PubMed - Peer-reviewed articles
- [ ] Google Scholar - Publications
- [ ] Books authored

**Background:**
- [ ] Licensing board - Disciplinary actions
- [ ] Secretary of State - Business affiliations
- [ ] Social media - Bias indicators

**Reference:** `deposition_library/references/expert_depo/dossier_compilation.md`

### 3. Map Conflict Opportunities

**Owner:** Agent  
**Skill:** `expert-deposition`  
**Action:** Identify conflicts by type and juror archetype.

| Conflict Type | Target Jurors |
|---------------|---------------|
| Hired Gun | Tribals |
| Snap Judgment | Tribals |
| Rules of the Road | All |
| Squaring Up (prior testimony) | Moderates |
| Treatise Contradiction | Moderates |
| Methodology Flaw | Progressives |

**Reference:** `deposition_library/references/expert_depo/conflict_mapping.md`
**Reference:** `deposition_library/references/expert_depo/juror_archetypes.md`

### 4. Draft Deposition Notice

**Owner:** Agent  
**Action:** Prepare notice with trial-use language.

**Document Generation Pattern:**
```bash
# Copy notice template
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/notices/notice_expert.md" \
   "/{project}/Litigation/Discovery/Expert_Notice_[ExpertName].md"

# Agent fills expert details
# Generate DOCX/PDF
python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
    "/{project}/Litigation/Discovery/Expert_Notice_[ExpertName].md"
```

**Required Language:**
> Said deposition will be taken by stenographic and video methods and for any and all purposes permitted by the Kentucky Rules of Civil Procedure, including use as evidence at the trial in this matter.

### 5. Send KRE 804 Trial Designation Notice

**Owner:** Agent  
**Action:** Send notice 3-5 days before deposition.

**Purpose:** Puts defense on notice to examine with trial-like motive, neutralizing "similar motive" objection.

**Reference:** `deposition_library/references/expert_depo/trial_preservation.md`

### 6. Prepare Deposition Outline

**Owner:** Agent  
**Skill:** `expert-deposition`  
**Action:** Create conflict-focused examination outline.

**Copy Template:**
```bash
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/outlines/outline_expert.md" \
   "/{project}/Litigation/Discovery/Expert_Outline_[ExpertName].md"
```

**Structure:**
1. Credentials (for later credential framing)
2. Compensation/Bias (hired gun)
3. Retention Timeline (snap judgment)
4. Materials Reviewed
5. Rules of the Road
6. Specific Opinions
7. Squaring Up (prior inconsistencies)
8. Treatise Confrontation (KRE 803(18))
9. Closing

### 7. Arrange Video Recording

**Owner:** User  
**Action:** Arrange court reporter and videographer.

**Why Video:** Expert depositions used at trial; video is more impactful.

### 8. Conduct Deposition

**Owner:** User (Attorney)  
**Action:** Conduct the deposition.

**Opening (for record):**
- Deposition for trial use under notice
- KRE 804 notice provided
- Video recording for trial

**Verify CR 32.01 Criteria:**
```
Q. You are a practicing physician?
Q. Where is your primary practice?
Q. Is that more than 100 miles from [courthouse]?
```

### 9. Post-Deposition Conflict Extraction

**Owner:** Agent  
**Action:** Extract and catalog conflicts with citations.

**Document:**
- Conflicts established (with page:line)
- Impeachment opportunities
- Rules agreed to
- Closing gambit result

## Exit Criteria

- [ ] Expert discovery served (60+ days before)
- [ ] Dossier compiled with prior testimony
- [ ] Conflicts mapped by type and juror archetype
- [ ] KRE 804 notice sent
- [ ] Notice includes trial-use language
- [ ] Video deposition conducted
- [ ] CR 32.01 criteria verified on record
- [ ] Conflicts extracted with citations

## Templates

| Template | Purpose |
|----------|---------|
| `notice_expert.md` | Expert deposition notice with trial-use language |
| `outline_expert.md` | Conflict-focused examination outline |

## Related Workflows

- **Related:** `propound_discovery` (written discovery before)
- **Related:** `party_depositions` (individual party depositions)
- **Related:** `corp_rep_deposition` (corporate depositions)

