# Phase 5 Sub-skill: Verification (Ops Manual)

**Purpose:** Verify Phase 4 execution results and produce a final summary report.

**You are a sub-agent.** You verify and report; you do not run scripts.

## Quick start (router)

1) Read rules (naming/date conventions, bucket expectations):
- `/Skills/case-file-organization/docs/REFERENCE.md`

2) Verify the folder state:
- Root should contain buckets and `Reports/`, not loose docs.

3) Write the summary:
- `/projects/{case_name}/Reports/reorganization_summary_{case_name}.md`

## Inputs (read-only)

- Map (what was intended): `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`
- Execution log (what happened): `/projects/{case_name}/Reports/reorganization_log_{case_name}.txt`
- Case root: `/projects/{case_name}/`

## Output (write)

- Summary: `/projects/{case_name}/Reports/reorganization_summary_{case_name}.md`

## Operations (step-by-step)

### Step 1 — Directory structure sanity check

List case root:

```python
ls("/projects/{case_name}/")
```

Expected top-level folders include:
- `Case Information/`
- `Client/`
- `Investigation/`
- `Medical Records/`
- `Insurance/`
- `Lien/`
- `Expenses/`
- `Negotiation Settlement/`
- `Litigation/`
- `Reports/`

### Step 2 — Root cleanliness check

Confirm there are no loose files left in `/projects/{case_name}/` (other than hidden/system files).

If any exist, list them in the report.

### Step 3 — Spot-check naming convention (by bucket)

Use `ls()` on each bucket and look for obvious naming issues:

```python
ls("/projects/{case_name}/Client/")
ls("/projects/{case_name}/Investigation/")
ls("/projects/{case_name}/Medical Records/")
ls("/projects/{case_name}/Insurance/")
ls("/projects/{case_name}/Lien/")
ls("/projects/{case_name}/Expenses/")
ls("/projects/{case_name}/Negotiation Settlement/")
ls("/projects/{case_name}/Litigation/")
```

You’re checking for:
- `YYYY-MM-DD` date format where expected
- Client name present
- Category aligns with bucket
- No garbled filenames / obviously wrong originators

### Step 4 — Companion checks (.pdf/.eml should have .md)

Within each bucket, identify:
- PDFs missing `.md` companions
- Emails missing `.md` companions (if your workflow expects them)

Record any missing companions in the report.

### Step 5 — Review the execution log

Read `/projects/{case_name}/Reports/reorganization_log_{case_name}.txt` and note:
- errors/warnings
- “source not found” patterns
- move/delete counts if present

### Step 6 — Produce the final summary

Write `/projects/{case_name}/Reports/reorganization_summary_{case_name}.md` using this template:

```markdown
# File Reorganization Summary: {Case Name}

**Date:** {YYYY-MM-DD}
**Status:** ✅ COMPLETE | ⚠️ ISSUES FOUND | ❌ FAILED

## Verification Results

### Directory Structure
- ✅ Buckets present
- ✅ Reports/ present

### Root Folder
- ✅ No loose files
  *(or)*
- ⚠️ Loose files present (listed below)

### Naming Convention (Spot Check)
- ✅ Looks consistent across buckets
  *(or)*
- ⚠️ Issues found (examples below)

### Companion Files
- ✅ Companions present
  *(or)*
- ⚠️ Missing companions listed below

## Issues Found (if any)

### Loose files in root
- ...

### Naming issues
- ...

### Missing companions
- ...

## Execution Log Notes

**Log:** /projects/{case_name}/Reports/reorganization_log_{case_name}.txt
- Errors: {count or description}
- Warnings: {count or description}
```

## Troubleshooting

- If many “source not found” errors appear: the map and/or plan likely referenced files that were moved/renamed earlier—flag and recommend re-running Phase 2→4.
- If lots of missing companions: either conversions failed earlier or plan didn’t include paired moves—flag clearly.


