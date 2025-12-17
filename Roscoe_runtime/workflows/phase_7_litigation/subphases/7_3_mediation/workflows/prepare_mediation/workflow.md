---
name: prepare_mediation
description: >
  Prepare for mediation session. Creates mediation brief, prepares client,
  gathers settlement authority. Use when mediation scheduled to ensure
  effective negotiation.
phase: 7.3_mediation
workflow_id: prepare_mediation
related_skills:
  - mediation-prep
related_tools:
  - generate_document.py
templates:
  - templates/mediation_brief_template.md
  - templates/damage_summary.md
---

# Prepare Mediation Workflow

## Overview

Prepare comprehensive mediation materials and ensure client is ready for settlement conference.

## Entry Criteria

- Mediation date scheduled
- Discovery complete or substantially complete
- Damages calculated

## Steps

### 1. Schedule Preparation Meeting

**Owner:** Agent  
**Action:** Calendar client prep meeting before mediation.

### 2. Draft Mediation Brief

**Owner:** Agent  
**Skill:** `mediation-prep`  
**Tool:** `generate_document.py`
**Action:** Create mediation brief with case summary, liability analysis, damages.

**Document Generation Pattern:**
```bash
# Copy template to Litigation/Mediation folder
cp "/templates/mediation_brief_template.md" \
   "/{project}/Litigation/Mediation/Mediation_Brief.md"
# Agent fills case summary, liability, damages sections
# Generate professional PDF
python generate_document.py "/{project}/Litigation/Mediation/Mediation_Brief.md"
```

### 3. Prepare Damage Summary

**Owner:** Agent  
**Action:** Compile medical specials, lost wages, pain and suffering analysis.

### 4. Confirm Settlement Authority

**Owner:** User  
**Action:** Discuss range with client, confirm authority level.

### 5. Prepare Client

**Owner:** User  
**Action:** Explain mediation process, expectations, patience required.

### 6. Submit Brief

**Owner:** User  
**Action:** Send brief to mediator and opposing counsel per rules.

## Exit Criteria

- [ ] Mediation brief completed
- [ ] Damage summary prepared
- [ ] Client settlement authority confirmed
- [ ] Client understands process

## Templates

| Template | Purpose |
|----------|---------|
| `mediation_brief_template.md` | Mediation brief format |
| `damage_summary.md` | Damages presentation |

## Related Workflows

- **Triggers:** `attend_mediation`

