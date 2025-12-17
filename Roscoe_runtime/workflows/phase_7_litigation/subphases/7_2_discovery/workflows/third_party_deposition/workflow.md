---
name: third_party_deposition
description: >
  Plan and conduct depositions of third-party (non-party) witnesses. Covers subpoena
  requirements, document requests via subpoena duces tecum, and rules-based examination.
  Use for eyewitnesses, employers, records custodians, and other non-party witnesses.
phase: 7.2_discovery
workflow_id: third_party_deposition
related_skills:
  - rules-based-examination
related_tools:
  - generate_document.py
templates:
  - deposition_library/templates/notices/notice_standard.md
  - deposition_library/templates/outlines/outline_rules_based.md
---

# Third-Party Witness Deposition Workflow

## Overview

Plan and conduct depositions of non-party witnesses using subpoena, with optional subpoena duces tecum for documents.

## Entry Criteria

- Third-party witness identified
- Witness has relevant information
- Discovery period open
- Witness within subpoena power of court

## Steps

### 1. Identify Witness and Information Needed

**Owner:** Agent  
**Action:** Determine what information the witness has.

| Witness Type | Typical Information |
|--------------|---------------------|
| Eyewitness | What they saw, heard |
| Employer | Employment records, scope of employment |
| Records Custodian | Authenticate records |
| Medical Provider | Treatment provided |
| Investigating Officer | Investigation details |

### 2. Determine Subpoena Requirements

**Owner:** Agent  
**Action:** Assess subpoena power and requirements.

**Key Questions:**
- Is witness within 100 miles of courthouse?
- Is witness within state?
- Will witness appear voluntarily?
- Are documents needed?

**If witness >100 miles:**
- Consider commission or letters rogatory
- May need to depose at witness's location

### 3. Prepare Subpoena

**Owner:** Agent  
**Action:** Prepare subpoena for witness attendance.

**Include:**
- Witness name and address
- Deposition date, time, location
- Case caption and number

**If Documents Needed (Subpoena Duces Tecum):**
- List documents with reasonable particularity
- Serve in advance to allow compliance

### 4. Prepare Notice of Deposition

**Owner:** Agent  
**Action:** Prepare and serve notice to all parties.

**Document Generation Pattern:**
```bash
# Copy notice template
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/notices/notice_standard.md" \
   "/{project}/Litigation/Discovery/Depo_Notice_[WitnessName].md"

# Agent fills witness details
# Generate DOCX/PDF
python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
    "/{project}/Litigation/Discovery/Depo_Notice_[WitnessName].md"
```

**Note:** Notice goes to parties; subpoena goes to witness.

### 5. Serve Subpoena on Witness

**Owner:** User  
**Action:** Properly serve subpoena.

**Service Requirements:**
- Personal service preferred
- Include witness fee if required
- Mileage if >certain distance
- Serve reasonable time in advance

### 6. Serve Notice on Parties

**Owner:** User  
**Action:** Serve notice of deposition on all parties.

### 7. Prepare Deposition Outline

**Owner:** Agent  
**Skill:** `rules-based-examination`  
**Action:** Prepare examination outline.

**Copy Template:**
```bash
cp "${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_2_discovery/deposition_library/templates/outlines/outline_rules_based.md" \
   "/{project}/Litigation/Discovery/Depo_Outline_[WitnessName].md"
```

**Structure (adapt based on witness type):**
1. Background and relationship to case
2. Rules establishment (if applicable)
3. Fact testimony
4. Document authentication (if SDT)
5. Closing

### 8. Conduct Deposition

**Owner:** User (Attorney)  
**Action:** Conduct the deposition.

**For Eyewitnesses:**
- What they observed (chronologically)
- Position/location during events
- What they heard
- What they did afterward

**For Employers:**
- Employment relationship
- Scope of employment
- Training and supervision
- Policies and procedures

**For Records Custodians:**
- Authenticate records
- Explain record-keeping practices
- Identify gaps or missing records

### 9. Post-Deposition Analysis

**Owner:** Agent  
**Action:** Summarize testimony for case file.

**Document:**
- Key facts established
- Testimony supporting case
- Testimony hurting case
- Documents authenticated
- Follow-up needed

## Exit Criteria

- [ ] Subpoena properly served on witness
- [ ] Notice served on all parties
- [ ] Deposition conducted
- [ ] Documents produced (if SDT)
- [ ] Key testimony documented
- [ ] Transcript ordered

## Special Considerations

### Witness Refuses to Appear

**Options:**
- Motion to compel attendance
- Contempt proceedings
- Consider voluntary appearance negotiation

### Witness Outside Jurisdiction

**Options:**
- Commission to take deposition in another state
- Letters rogatory (international)
- Agreement with witness for voluntary appearance

### Records-Only Deposition

If only need records (not testimony):
- Consider subpoena duces tecum with records certification
- May not need to actually depose witness

## Templates

| Template | Purpose |
|----------|---------|
| `notice_standard.md` | Standard deposition notice |
| `outline_rules_based.md` | Examination outline |
| Subpoena form | Court-specific subpoena form |
| SDT attachment | Document request attachment |

## Related Workflows

- **Related:** `party_depositions` (adverse party depositions)
- **Related:** `corp_rep_deposition` (corporate depositions)
- **Related:** `propound_discovery` (written discovery)

