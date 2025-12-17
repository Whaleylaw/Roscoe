---
name: draft_file_complaint
description: >
  Draft and file complaint to initiate litigation. Creates complaint document,
  files with court, obtains summons. Use when decision made to sue, SOL approaching,
  or negotiation failed.
phase: 7.1_complaint
workflow_id: draft_file_complaint
related_skills:
  - complaint-drafting
related_tools:
  - generate_document.py
templates:
  - templates/complaint_template.md
---

# Draft & File Complaint Workflow

## Overview

Draft the complaint document, file with court, and obtain summons for service.

## Entry Criteria

- Decision to file litigation approved
- All defendants identified
- SOL not expired

## Steps

### 1. Gather Case Information

**Owner:** Agent  
**Action:** Compile facts, parties, damages from case file.

### 2. Draft Complaint

**Owner:** Agent  
**Skill:** `complaint-drafting`  
**Tool:** `generate_document.py`
**Action:** Generate complaint using template and case facts.

**Document Generation Pattern:**
```bash
# Step 1: Copy template to Litigation folder
cp "/templates/complaint_mva_template.md" \
   "/{project}/Litigation/Complaint.md"

# Step 2: Agent fills all [BRACKETED] fields:
#   - [COUNTY], [FACTS], [INJURIES], [NEGLIGENT ACTS], [DAMAGES], etc.
# Auto-fill fields ({{placeholder}}) filled automatically from case data

# Step 3: Generate DOCX/PDF
python generate_document.py "/{project}/Litigation/Complaint.md"
# Creates: Complaint.docx and Complaint.pdf
```

### 3. Attorney Review

**Owner:** User (Attorney)  
**Action:** Review for legal sufficiency and strategy.

### 4. E-File with Court

**Owner:** User  
**Action:** File via eFlex, pay filing fee, receive case number.

### 5. Obtain Summons

**Owner:** User  
**Action:** Receive summons from clerk for each defendant.

## Exit Criteria

- [ ] Complaint filed
- [ ] Case number assigned
- [ ] Summons issued for each defendant

## Templates

| Template | Purpose |
|----------|---------|
| `templates/complaint_template.md` | Kentucky circuit court complaint format (local copy) |
| `/templates/complaint_mva_template.md` | Central template (registry ID: `complaint_mva`) |

**Auto-fill Fields (from path context):**
- `{{client.name}}` - From `overview.json`
- `{{defendant.name}}` - From `contacts.json`
- `{{incidentDate}}` - From `overview.json`
- `{{firm.*}}` - From `firm_config.json`

**Agent-Fill Fields:**
- `[COUNTY]` - Venue county
- `[FACTS]` - Accident narrative
- `[INJURIES]` - List of injuries
- `[NEGLIGENT ACTS]` - List of negligent acts
- `[DAMAGES]` - Damages sought

## Related Workflows

- **Triggers:** `serve_defendant`

