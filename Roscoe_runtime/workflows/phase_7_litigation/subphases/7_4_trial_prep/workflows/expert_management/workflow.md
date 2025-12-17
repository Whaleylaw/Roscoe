---
name: expert_management
description: >
  Manage expert witness disclosures and preparation. Handles disclosure
  deadlines, expert depositions, and trial preparation of experts.
  Use when expert disclosure deadline approaching.
phase: 7.4_trial_prep
workflow_id: expert_management
related_skills:
  - expert-coordination
templates:
  - expert_disclosure.md
---

# Expert Management Workflow

## Overview

Coordinate expert witness disclosures, depositions, and trial preparation.

## Entry Criteria

- Expert disclosure deadline approaching
- Experts retained and working
- Opinions developed

## Steps

### 1. Confirm Expert Opinions

**Owner:** User  
**Action:** Ensure expert has finalized opinions and can support them.

### 2. Prepare Expert Disclosure

**Owner:** Agent  
**Skill:** `expert-coordination`  
**Action:** Draft disclosure with all required information.

### 3. File Disclosure

**Owner:** User  
**Action:** Serve disclosure by deadline.

### 4. Review Defense Expert Disclosure

**Owner:** Agent  
**Action:** Analyze defense expert opinions and qualifications.

### 5. Depose Defense Experts

**Owner:** User (Attorney)  
**Action:** Take depositions of defense experts.

### 6. Prepare Our Experts for Trial

**Owner:** User  
**Action:** Prepare experts for direct examination and cross.

## Exit Criteria

- [ ] Our expert disclosures filed
- [ ] Defense expert disclosures received
- [ ] Expert depositions completed
- [ ] Experts prepared for trial

## Templates

| Template | Purpose |
|----------|---------|
| `expert_disclosure.md` | Expert disclosure format |

## Related Workflows

- **Related:** `trial_materials` (exhibits may include expert reports)

