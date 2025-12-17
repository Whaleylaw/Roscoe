# Phase 4 Sub-skill: Execution Plan Generation (Ops Manual)

**Purpose:** Generate the single JSON plan that the main agent will execute.

**You are a sub-agent.** You create the plan; you do **not** move/delete files yourself.

## Quick start (router)

1) Read shared rules:
- `/Skills/case-file-organization/docs/REFERENCE.md`

2) Read inputs:
- `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`
- `/projects/{case_name}/Reports/pdf_md_mapping_{case_name}.json`

3) Write output:
- `/projects/{case_name}/Reports/reorganization_plan.json`

## Inputs (read-only)

- **Approved map**: `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`
- **PDF mapping**: `/projects/{case_name}/Reports/pdf_md_mapping_{case_name}.json`
- **QA summary (optional)**: `/projects/{case_name}/Reports/quality_review_summary_{case_name}.md`

## Output (write)

- **JSON plan**: `/projects/{case_name}/Reports/reorganization_plan.json`

## Non-negotiable rules

- Produce **one** JSON file containing **all operations**.
- Do **not** execute operations.
- JSON paths are **relative to the case root** (do not include `/projects/...` inside JSON).
- For scrambled PDF pairs:
  - `source` is the scrambled markdown (e.g., `doc_0001.md`)
  - `pdf_source` comes from the mapping JSON and typically starts with `_pdf_originals/...`
- Do not include “REVIEW” items as operations.

## Operations (step-by-step)

### Step 1 — Parse the map into items

From the mapping table, extract each row:
- `Current Path`
- `Action` (MOVE / DELETE / REVIEW)
- `Target Path` + `New Filename` (for MOVE)

### Step 2 — Build operations

For each row:

- **MOVE**
  - Create operation with:
    - `action: "move"`
    - `source`
    - `destination` (Target Path + New Filename)
  - If `source` is `doc_####.md`, look up `source` in `pdf_md_mapping_{case_name}.json` and add:
    - `pdf_source`
    - `pdf_destination` (same destination base name, `.pdf`)
  - If moving an email and a `.md` companion exists:
    - include `md_source` and `md_destination` for the companion pair

- **DELETE**
  - Create operation with:
    - `action: "delete"`
    - `source`
  - If `source` is `doc_####.md`, also include `pdf_source` from the mapping JSON.

- **REVIEW**
  - No operation (skip; leave for human correction).

### Step 3 — Add cleanup section

Include:

```json
"cleanup": {
  "remove_pdf_originals": true,
  "remove_mapping_file": true
}
```

### Step 4 — Write the plan

Save to `/projects/{case_name}/Reports/reorganization_plan.json` using `write_file()`.

## JSON shape (minimum)

```json
{
  "case_name": "{Case Name}",
  "case_folder": "{case_name}",
  "generated_at": "YYYY-MM-DDTHH:MM:SS",
  "operations": [],
  "cleanup": {
    "remove_pdf_originals": true,
    "remove_mapping_file": true
  }
}
```

## Operation examples

### Scrambled PDF-derived pair (md + pdf)

```json
{
  "action": "move",
  "source": "doc_0001.md",
  "destination": "Medical Records/Norton Healthcare/Medical Records/2023-07-30 - Client - Medical Record - Norton Healthcare - Emergency Department Visit.md",
  "pdf_source": "_pdf_originals/medical_records/Norton-ER-Visit.pdf",
  "pdf_destination": "Medical Records/Norton Healthcare/Medical Records/2023-07-30 - Client - Medical Record - Norton Healthcare - Emergency Department Visit.pdf"
}
```

### Email + md companion

```json
{
  "action": "move",
  "source": "some-email.eml",
  "destination": "Litigation/2025-02-07 - Client - Litigation - BK to DC - Filing Confirmation Complaint.eml",
  "md_source": "some-email.md",
  "md_destination": "Litigation/2025-02-07 - Client - Litigation - BK to DC - Filing Confirmation Complaint.md"
}
```

### Delete duplicate (with pdf)

```json
{
  "action": "delete",
  "source": "doc_0099.md",
  "pdf_source": "_pdf_originals/duplicates/old-copy.pdf"
}
```

## Handoff message to main agent

After writing the plan, send:

```
Plan generated and saved:
/projects/{case_name}/Reports/reorganization_plan.json

Main agent should execute:
execute_python_script(script_path="/Skills/case-file-organization/tools/file_reorganize.py", script_args=["{case_name}", "--dry-run"])
then run without --dry-run.
```


