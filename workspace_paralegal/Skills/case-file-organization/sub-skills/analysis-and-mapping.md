# Phase 2 Sub-skill: Analysis & Mapping (Ops Manual)

**Purpose:** Produce the **complete, automation-ready** reorganization map from content-only reading (no filename bias).

**You are a sub-agent.** You read files and write a mapping. You do **not** execute moves/deletes.

## Quick start (router)

1) If you have not already, **read the rules**:
- `/Skills/case-file-organization/docs/REFERENCE.md`

2) Then follow the procedure in **“Operations (step-by-step)”** below.

## Inputs (read-only)

- **Inventory**: `/projects/{case_name}/Reports/file_inventory_{case_name}.md`
- **Case root**: `/projects/{case_name}/` (contains scrambled `doc_####.md` and other `.md` companions)

## Output (write)

- **Mapping**: `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`

## Non-negotiable rules

- **Scrambled docs are real documents**: every `doc_####.md` must be read and mapped.
- **No placeholders**: no “omitted for brevity”, no “rows would be listed here”.
- **One row per file**: every inventory item must appear in the plan table.
- **Email pairing**: if there is an `.eml` and `.md` companion, treat as a pair in the map.
- **Multi-party discipline**: if a document is clearly another client’s document, flag for review (don’t “fix” by guessing).

## Operations (step-by-step)

### Step 1 — Read inventory and build your worklist

- Read `/projects/{case_name}/Reports/file_inventory_{case_name}.md`.
- Create a checklist of every file path listed.

### Step 2 — For each file, read content and classify

For each file:
1. If it’s a **scrambled doc** (`doc_####.md`), read it directly.
2. If it’s an **email**, read the `.md` companion for content (not the `.eml`).
3. Determine (from content only):
   - **Bucket folder**
   - **Correct date** (per Dating Protocol in `REFERENCE.md`)
   - **Originator** (facility/carrier/plaintiff/defendant/etc.)
   - **Short description**
4. Decide action:
   - **MOVE** (most common)
   - **DELETE** (only if you are confident it is a true duplicate and you identify what to keep)
   - **REVIEW** (cannot determine category/date/originator confidently)

### Step 3 — Duplicates (be conservative)

Mark as **DELETE** only when:
- You read both documents and they are clearly duplicates, and
- You can name which file to keep (in your duplicates table).

Otherwise mark as **REVIEW**.

### Step 4 — Build the mapping table (complete)

Write the reorganization plan table with **every file** as a row:

| Current Path | Action | Target Path | New Filename | Notes |
|--------------|--------|-------------|--------------|-------|
| doc_0001.md | MOVE | Medical Records/Norton Healthcare/Medical Records/ | 2023-07-30 - Caryn McCay - Medical Record - Norton Healthcare - Emergency Department Visit.md | Date of service |
| 2024.10.02-Example.eml | MOVE | Litigation/ | 2024-10-02 - Client - Litigation - BK to DC - Filing Confirmation Complaint.eml | Email |
| 2024.10.02-Example.md | MOVE | Litigation/ | 2024-10-02 - Client - Litigation - BK to DC - Filing Confirmation Complaint.md | Email companion |
| doc_0042.md | REVIEW | [REVIEW NEEDED] | - | Unclear document type |

### Step 5 — Add the “review” and “duplicates” sections

Add:
- **Files Requiring User Review**: bullet list with why you flagged each.
- **Duplicates Identified for Deletion**: table listing duplicate vs keep.

### Step 6 — Final validation (must do)

Before saving:
- Confirm: **every inventory item** has a row.
- Confirm: **no placeholders** exist.
- Confirm: email pairs are represented (both `.eml` and `.md` if present).

## Troubleshooting

- **Too ambiguous**: mark `REVIEW` and explain what’s missing (date unclear, document type unclear, client unclear).
- **Litigation date confusion**: re-check for **Certificate of Service** (use that date).
- **Provider naming**: use facility/practice (not individual doctor) unless clearly solo practice.

## Deliverable checklist (must be true)

- [ ] `file_reorganization_map_{case_name}.md` written to `/projects/{case_name}/Reports/`
- [ ] Contains a complete plan table (one row per file)
- [ ] Contains “Files Requiring User Review” section
- [ ] Contains “Duplicates Identified for Deletion” section (even if empty)
