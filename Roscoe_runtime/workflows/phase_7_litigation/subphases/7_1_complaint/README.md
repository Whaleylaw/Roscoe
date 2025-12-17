# Sub-Phase 7.1: Complaint

## Overview

**Sub-Phase ID:** `7.1_complaint`  
**Parent Phase:** 7 (Litigation)  
**Track:** Litigation

The Complaint sub-phase initiates litigation by filing suit against the defendant(s). This includes drafting the complaint, filing with the court, serving the defendant(s), and processing their answer.

---

## Entry Triggers

- Decision made to file litigation
- Statute of limitations approaching (within 60 days)
- Negotiation impasse

---

## Exit Criteria

**Per-Defendant (triggers Discovery for that defendant):**

| Criterion | Description | Verification |
|-----------|-------------|--------------|
| Defendant Served | Service completed on this defendant | Proof of service filed |
| Answer/Default | Answer received OR default motion filed | Response documented |

**Full Sub-Phase Exit (7.1 closes):**

| Criterion | Description | Verification |
|-----------|-------------|--------------|
| All Resolved | All defendants have answered or defaulted | All defendant tracks complete |

> **Note:** Discovery begins per-defendant as each one is served and answers. The sub-phase remains open while any defendant is still pending service or answer.

---

## Workflows

| Workflow | Purpose | Path |
|----------|---------|------|
| draft_file_complaint | Draft and file complaint with court | `workflows/draft_file_complaint/workflow.md` |
| serve_defendant | Serve complaint on all defendants | `workflows/serve_defendant/workflow.md` |
| process_answer | Process defendant's answer or seek default | `workflows/process_answer/workflow.md` |

---

## Key Deadlines

| Deadline | Rule | Consequence |
|----------|------|-------------|
| Filing | Before SOL expires | Claim barred |
| Service | 90 days from filing | Dismissal possible |
| Answer | 20 days from service | Default available |

---

## Next Sub-Phase

**→ 7.2 Discovery** (when answer received or default sought)

