---
name: process_answer
description: >
  Process defendant's answer to complaint. Reviews for affirmative defenses,
  counterclaims, third-party claims. Handles default judgment if no answer.
  Use when answer deadline reached.
phase: 7.1_complaint
workflow_id: process_answer
related_skills:
  - answer-analysis
templates:
  - answer_summary.md
---

# Process Answer Workflow

## Overview

Review and analyze defendant's answer or initiate default proceedings if no answer received.

## Entry Criteria

- Defendant served
- Answer deadline reached OR answer received

## Steps

### 1. Check for Answer

**Owner:** Agent  
**Action:** Verify if answer filed by deadline.

**If no answer → Step 4 (Default Path)**

### 2. Review Answer

**Owner:** Agent  
**Skill:** `answer-analysis`  
**Action:** Analyze answer for key elements.

### 3. Document Findings

**Owner:** Agent  
**Action:** Create answer summary with:
- Denials
- Affirmative defenses
- Counterclaims (if any)
- Third-party claims (if any)

**→ Exit to 7.2 Discovery**

### 4. Default Path: File Default Motion

**Owner:** User  
**Action:** File motion for default judgment.

### 5. Attend Default Hearing

**Owner:** User  
**Action:** Present evidence of damages at prove-up hearing.

## Exit Criteria (Per Defendant)

For this defendant:
- [ ] Answer reviewed and documented, OR
- [ ] Default judgment motion filed

**Effect:** This defendant's track advances to 7.2 Discovery. Discovery can begin for this defendant while other defendants are still pending service/answer.

## Templates

| Template | Purpose |
|----------|---------|
| `answer_summary.md` | Document answer analysis |

## Related Workflows

- **Triggered By:** `serve_defendant` (per defendant, when that defendant is served)
- **Triggers:** 7.2 Discovery (for this defendant only)

## Multi-Defendant Tracking

When multiple defendants exist, this workflow runs independently for each:

```
Defendant A: Served May 1 → Answer May 15 → Discovery begins May 15
Defendant B: Served May 10 → Answer June 1 → Discovery begins June 1
Defendant C: Service pending → (still in serve_defendant workflow)
```

The agent tracks each defendant's status separately in `litigation.json`.

