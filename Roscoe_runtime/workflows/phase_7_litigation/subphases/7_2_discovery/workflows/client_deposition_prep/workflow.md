---
name: client_deposition_prep
description: >
  Prepare client for their deposition. Covers pre-deposition preparation including
  document compilation, privilege identification, client coaching on rules and topics.
  Includes day-of support procedures and post-deposition transcript analysis.
  Use when client's deposition noticed to ensure effective testimony defense.
phase: 7.2_discovery
workflow_id: client_deposition_prep
related_skills:
  - deposition-defense
related_tools:
  - generate_document.py
templates:
  - deposition_library/templates/client_prep/client_letter.md
  - deposition_library/templates/client_prep/client_checklist.md
  - deposition_library/templates/client_prep/privilege_review.md
---

# Client Deposition Prep Workflow

## Overview

Thoroughly prepare client to give effective testimony at their deposition, from initial notice through post-deposition analysis.

## Entry Criteria

- Deposition notice received from defense
- Deposition date scheduled
- Adequate time for preparation (ideally 2-4 weeks)

## Steps

### 1. Review Deposition Notice

**Owner:** Agent  
**Skill:** `deposition-defense`  
**Action:** Extract and verify notice details.

- [ ] Date, time, location confirmed
- [ ] Court reporter identified
- [ ] Scope of topics/documents identified
- [ ] Notice adequacy checked (CR 30.02(1))
- [ ] All deadlines calendared

**Reference:** `deposition_library/references/client_defense/pre_deposition.md`

### 2. Schedule Prep Sessions

**Owner:** User  
**Action:** Plan 2-3 preparation sessions before deposition.

**Recommended Schedule:**
- Session 1 (2 weeks before): Process overview, rules, document review
- Session 2 (1 week before): Topic review, problem areas
- Session 3 (if needed): Practice examination
- Day-before: Final refresher

### 3. Compile Documents

**Owner:** Agent  
**Skill:** `deposition-defense`  
**Action:** Gather and organize all relevant documents.

**Document Categories:**
- [ ] Medical records (injury-related)
- [ ] Incident/accident reports
- [ ] Photographs (scene, injuries, property)
- [ ] Correspondence (emails, letters, texts)
- [ ] Employment records (if wages at issue)
- [ ] Insurance documents
- [ ] Prior statements by client
- [ ] Social media content (review for problems)

**Create:** Document index with descriptions and relevance notes.

### 4. Review Privilege Issues

**Owner:** Agent  
**Skill:** `deposition-defense`  
**Action:** Identify privileged materials and topics.

**Document Generation Pattern:**
```bash
# Copy privilege review template
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/client_prep/privilege_review.md" \
   "/{project}/Litigation/Discovery/Privilege_Review.md"
```

**Review for:**
- [ ] Attorney-client communications (KRE 503)
- [ ] Work product materials
- [ ] Court-ordered limitations

**Reference:** `deposition_library/references/client_defense/pre_deposition.md`

### 5. Send Client Letter

**Owner:** Agent  
**Action:** Send preparation letter to client.

**Document Generation Pattern:**
```bash
# Copy client letter template
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/client_prep/client_letter.md" \
   "/{project}/Client/Deposition_Letter.md"

# Generate DOCX/PDF
python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
    "/{project}/Client/Deposition_Letter.md"
```

### 6. Explain Deposition Process (Session 1)

**Owner:** User  
**Skill:** `deposition-defense`  
**Action:** Explain what deposition is and how it works.

**Cover:**
- What a deposition is
- Who will be present
- How long it typically takes
- The binding nature of sworn testimony

### 7. Cover Fundamental Rules (Session 1)

**Owner:** User  
**Skill:** `deposition-defense`  
**Action:** Teach key rules for testimony.

**Core Rules:**
1. Tell the truth
2. Listen to the entire question
3. If you don't know, say "I don't know"
4. Don't guess or speculate
5. Answer only what is asked
6. Don't volunteer information
7. Take your time
8. Ask for clarification if needed

**Reference:** `deposition_library/templates/client_prep/client_checklist.md`

### 8. Review Key Topics (Session 2)

**Owner:** Agent/User  
**Action:** Go through expected question areas.

**Anticipated Topics:**
- Background (name, address, family, employment)
- Medical history prior to accident
- Details of the accident
- Injuries sustained
- Medical treatment received
- Current condition and limitations
- Lost wages and work impact
- Impact on daily life
- Prior accidents or injuries
- Prior lawsuits or claims

### 9. Address Problem Areas (Session 2)

**Owner:** User  
**Action:** Prepare client for difficult topics.

**Common Problem Areas:**
- Prior injuries to same body parts
- Gaps in treatment
- Social media content
- Criminal history
- Inconsistent prior statements
- Unfavorable facts

**Strategy:** Acknowledge honestly; prepare truthful responses.

### 10. Practice Session (Session 3)

**Owner:** User  
**Action:** Conduct mock examination.

- Practice describing accident clearly
- Practice handling difficult questions
- Build client confidence
- Reinforce good testimony habits

### 11. Day-Before Review

**Owner:** User  
**Action:** Final refresher and logistics.

- [ ] Quick rules review
- [ ] Confirm logistics (time, location, parking)
- [ ] Address any last-minute concerns
- [ ] Ensure client will arrive 30 minutes early

### 12. Day-of Support

**Owner:** User/Agent  
**Skill:** `deposition-defense`  
**Action:** Support during deposition.

**Pre-Deposition Meeting (30 min early):**
- Final rules refresher
- Address any concerns
- Ensure client is calm and ready

**During Deposition:**
- Monitor for objectionable questions
- Make timely form objections
- Watch for privilege incursions
- Monitor for CR 30.04 bad faith conduct
- Request breaks as needed

**Reference:** `deposition_library/references/client_defense/day_of_support.md`
**Reference:** `deposition_library/references/client_defense/objections_guide.md`

### 13. Post-Deposition Analysis

**Owner:** Agent  
**Skill:** `deposition-defense`  
**Action:** Analyze transcript when received.

**Review for:**
- [ ] Typographical errors
- [ ] Substantive irregularities
- [ ] Key admissions (favorable and unfavorable)
- [ ] Testimony supporting case theory
- [ ] Testimony contradicting case theory
- [ ] Potential impeachment material

**Create:**
- Objection catalog with CR 32.04 waiver analysis
- Key testimony log with page:line citations
- Trial preparation notes

**Reference:** `deposition_library/references/client_defense/post_analysis.md`

## Exit Criteria

- [ ] Client understands deposition process
- [ ] Fundamental rules covered
- [ ] Problem areas addressed
- [ ] Practice completed (if needed)
- [ ] Client feels prepared
- [ ] Deposition completed
- [ ] Transcript reviewed (when received)

## Templates

| Template | Purpose |
|----------|---------|
| `client_letter.md` | Pre-deposition letter to client |
| `client_checklist.md` | Preparation tracking checklist |
| `privilege_review.md` | Privilege identification template |

## Related Workflows

- **Related:** `party_depositions` (taking defendant's deposition)
- **Related:** `corp_rep_deposition` (corporate representative depositions)
- **Related:** `defense_expert_depo` (expert depositions)
