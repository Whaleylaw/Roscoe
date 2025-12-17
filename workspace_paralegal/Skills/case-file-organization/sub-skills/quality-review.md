# Phase 3 Sub-skill: Quality Review (Ops Manual)

**Purpose:** Independently validate the Phase 2 map by re-reading content and flagging **only clear errors**. This is a full QA pass (not sampling).

**You are a sub-agent.** You review and report; you do not execute the move plan.

## Quick start (router)

1) Read the rules you must apply:
- `/Skills/case-file-organization/docs/REFERENCE.md`

2) Then follow the procedures below.

## Inputs (read-only)

- **Map**: `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`
- **Files**: `/projects/{case_name}/...` (read `.md` content as needed)

## Output (write)

- **QA Summary**: `/projects/{case_name}/Reports/quality_review_summary_{case_name}.md`

Optional (only if needed):
- **Review folder**: `/projects/{case_name}/REVIEW_NEEDED_Phase_3/` (move/copy flagged items if practical)

## Quality bar (what to flag vs what to accept)

**Flag only when clearly wrong:**
- Wrong **bucket**
- Wrong **originator/facility/carrier**
- Wrong **date** per Dating Protocol (esp. litigation Certificate of Service)
- Multi-party misfile (wrong client)
- Document type clearly mislabeled (record vs bill vs request)

**Do not flag:**
- Minor wording differences in description
- Slightly different but accurate summarization

## Operations (step-by-step)

### Step 1 — Parse the map into a checklist

- Extract all rows from the plan table.
- You must process every row.

### Step 2 — Duplicate verification first

For each “DELETE” entry:
- Read the duplicate and the “keep” candidate (if specified).
- If not fully confident: mark as **needs review** in your QA summary.

### Step 3 — Full content re-evaluation (every row)

For each “MOVE” row:
1. Read the source `.md` content (for emails, read the `.md` companion).
2. Validate:
   - Bucket correctness
   - Date correctness (per `REFERENCE.md`)
   - Originator correctness
   - Description plausibly matches content
3. If clearly wrong: add to your flagged list (include what you think is correct).

### Step 4 — Compute stats

\( \text{ErrorRate} = \frac{\text{Flagged}}{\text{TotalReviewed}} \times 100 \)

### Step 5 — Write QA summary (deliverable)

Your summary must include:
- Total reviewed
- Total flagged + error rate
- Breakdown by error type
- Duplicate verification results
- Clear recommendation (“approved” vs “needs correction”)

## QA Summary template (copy/paste)

```markdown
# Quality Review Summary: {Case Name}

**Date:** {YYYY-MM-DD}
**Map Reviewed:** /projects/{case_name}/Reports/file_reorganization_map_{case_name}.md

## Overall Assessment
- Status: ✅ APPROVED FOR EXECUTION | ⚠️ CORRECTIONS REQUIRED
- Files reviewed: {n}
- Files flagged: {k}
- Error rate: {k}/{n} = {pct}%

## Duplicate Verification
- Verified safe deletions: {n_ok}
- Needs review: {n_review}

## Error Breakdown
- Category/bucket errors: {n}
- Date errors: {n}
- Originator errors: {n}
- Multi-party/client errors: {n}
- Other: {n}

## Flagged Items
| Source | Proposed | Issue | Recommended fix |
|--------|----------|-------|-----------------|
| doc_0042.md | ... | Wrong bucket | Move to Medical Records/... |

## Recommendation
- If error rate is low and issues are isolated: main agent can correct map and proceed.
- If error rate is high: re-run Phase 2 mapping with stricter instructions.
```

## Troubleshooting

- **Can’t verify a duplicate**: treat as “needs review”; do not approve deletion.
- **Litigation dates**: re-check for Certificate of Service; if missing/unclear, flag.
