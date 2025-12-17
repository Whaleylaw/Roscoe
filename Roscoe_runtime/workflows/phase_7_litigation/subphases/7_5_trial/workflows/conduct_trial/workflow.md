---
name: conduct_trial
description: >
  Conduct civil trial from jury selection through verdict. Handles
  voir dire, opening, evidence presentation, closing, and verdict.
  Use during trial proceedings.
phase: 7.5_trial
workflow_id: conduct_trial
related_skills:
  - trial-presentation
templates:
  - opening_outline.md
  - closing_outline.md
---

# Conduct Trial Workflow

## Overview

Execute trial from start to finish, presenting plaintiff's case effectively.

## Entry Criteria

- Trial date arrived
- All pretrial materials ready
- Client and witnesses prepared

## Steps

### 1. Jury Selection (Voir Dire)

**Owner:** User (Attorney)  
**Action:** Question and select jurors, exercise challenges.

### 2. Opening Statement

**Owner:** User (Attorney)  
**Skill:** `trial-presentation`  
**Action:** Present case overview to jury.

### 3. Present Plaintiff's Case

**Owner:** User (Attorney)  
**Skill:** `trial-presentation`  
**Action:** Call witnesses, introduce exhibits, establish elements.

### 4. Handle Motions

**Owner:** User (Attorney)  
**Action:** Respond to defense motions (directed verdict, etc.).

### 5. Cross-Examine Defense Witnesses

**Owner:** User (Attorney)  
**Action:** Challenge defense evidence and witnesses.

### 6. Closing Argument

**Owner:** User (Attorney)  
**Skill:** `trial-presentation`  
**Action:** Summarize evidence, argue for verdict.

### 7. Await Verdict

**Owner:** User  
**Action:** Answer jury questions, await deliberation result.

### 8. Document Outcome

**Owner:** Agent  
**Action:** Record verdict, next steps.

## Exit Criteria

- [ ] Trial completed
- [ ] Verdict received or other resolution
- [ ] Next steps determined

## Templates

| Template | Purpose |
|----------|---------|
| `opening_outline.md` | Opening statement structure |
| `closing_outline.md` | Closing argument structure |

## Related Workflows

- **Triggered By:** 7.4 Trial Prep
- **Triggers:** Phase 5 (Settlement) or Phase 8 (Closed)

