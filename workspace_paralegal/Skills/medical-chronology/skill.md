# Medical Chronology Skill

## When to Use This Skill

Use this skill when:
- User requests a medical chronology or treatment timeline
- User asks to "create chronology" or "synthesize timeline"
- You have extraction reports from medical records and need to combine them into a narrative
- You need a standalone chronology without running the full 5-phase medical analysis

**DO NOT use this skill if:**
- User wants full medical analysis (use medical-records-analysis instead)
- No medical records have been extracted yet (run extractions first or use medical-records-analysis)

## Prerequisites

Before using this skill, verify:
- Medical record extraction reports exist in `Reports/extractions/`
- If no extractions exist, you must run record extractions first

## What This Skill Does

This skill synthesizes all individual medical record extraction reports into a comprehensive chronological narrative timeline. It combines visits and billing entries from multiple extraction reports, sorts them by date, and creates an attorney-ready medical chronology.

## Workflow

### Step 1: Verify Extractions Exist

Check if extraction reports are available:
```bash
ls /Reports/extractions/
```

**If no extractions found:**
- Inform user that extractions must be run first
- Offer to run medical-records-analysis skill or standalone extractions
- Do not proceed with chronology

### Step 2: Read All Extraction Reports

Read every extraction report from `Reports/extractions/`:
```bash
ls /Reports/extractions/
# Read each file individually
```

### Step 3: Combine and Sort All Visits/Bills

1. **Extract all visit entries** from all reports
2. **Extract all billing entries** from all reports
3. **Combine into single dataset** with these fields:
   - Date (YYYY-MM-DD format)
   - Provider/Facility
   - Visit Type or Service Description
   - Key Details (diagnoses, treatments, complaints)
   - Source Document (original filename from extraction)

4. **Sort chronologically** by date (earliest first)
5. **Flag duplicates** (same date + same provider + similar details)
6. **Identify timeline gaps** (> 30 days between visits)

### Step 4: Build Narrative Chronology

Create a **narrative medical chronology** with:

#### A. Timeline Structure
Organize by date with clear sections:
```markdown
## DATE: YYYY-MM-DD | PROVIDER | VISIT TYPE

**Chief Complaint:** [patient's reported symptoms]

**Clinical Findings:** [exam findings, test results]

**Diagnoses:**
- [Diagnosis 1]
- [Diagnosis 2]

**Treatment:**
- [Medications prescribed]
- [Procedures performed]
- [Referrals made]

**Source:** [filename, page number if available]

---
```

#### B. Timeline Gaps
After each gap > 30 days, insert:
```markdown
⚠️ **TREATMENT GAP: [X] days** (YYYY-MM-DD to YYYY-MM-DD)
- No documented medical visits during this period
- **Attorney Note:** Consider obtaining records or addressing gap in narrative

---
```

#### C. Key Milestones
Highlight critical events:
- First post-incident treatment (ER, urgent care)
- Diagnostic imaging (X-rays, MRIs, CT scans)
- Specialist referrals
- Physical therapy start/end
- Surgical interventions
- Treatment conclusion or ongoing care

#### D. Running Totals Section
Include financial summary:
```markdown
## Financial Summary

**Total Medical Bills:** $[amount]
**Total Visits:** [count]
**Total Providers:** [count]
**Treatment Duration:** [earliest date] to [latest date] ([X] days)
```

### Step 5: Create Structured Data Output

In addition to narrative chronology, create a **structured data file** (`visits_summary.md`) with tabular format for easy reference:

```markdown
| Date | Provider | Type | Diagnoses | Treatments | Bill Amount | Source |
|------|----------|------|-----------|------------|-------------|---------|
| YYYY-MM-DD | [name] | [type] | [diagnoses] | [treatments] | $XXX | [file] |
```

This enables quick filtering, sorting, and data analysis.

### Step 6: Save Outputs

Save two files to `Reports/` directory:

1. **`Reports/chronology.md`** - Full narrative chronology with gaps, milestones, attorney notes
2. **`Reports/visits_summary.md`** - Structured tabular data for all visits and bills

### Step 7: Create Chronology Summary

After saving, read `Reports/chronology.md` and provide user with:

1. **Executive Summary:**
   - Total number of visits
   - Date range of treatment
   - Key providers involved
   - Treatment gaps identified
   - Total medical bills

2. **Key Observations:**
   - First treatment after incident
   - Continuity of care assessment
   - Significant diagnostic findings
   - Treatment compliance indicators

3. **File Location:** Inform user where full chronology is saved

## Output Format Specifications

### Narrative Chronology (`chronology.md`)

```markdown
# Medical Chronology: [Client Name]

**Case:** [Project Name]
**Incident Date:** [YYYY-MM-DD] (from case facts)
**Treatment Period:** [First Visit] to [Last Visit]
**Total Duration:** [X] days
**Total Visits:** [count]
**Total Bills:** $[amount]

---

## TIMELINE

### DATE: YYYY-MM-DD | PROVIDER NAME | VISIT TYPE

[Full narrative entry with all details]

**Source:** [document name, page X]

---

### DATE: YYYY-MM-DD | PROVIDER NAME | VISIT TYPE

[Next entry...]

---

⚠️ **TREATMENT GAP: 45 days** (YYYY-MM-DD to YYYY-MM-DD)

---

[Continue chronologically...]

---

## FINANCIAL SUMMARY

**Total Medical Bills:** $XX,XXX.XX
**Bills by Provider:**
- Provider A: $X,XXX.XX
- Provider B: $X,XXX.XX
[etc.]

## TREATMENT GAPS SUMMARY

1. **Gap 1:** [dates] - [X] days
2. **Gap 2:** [dates] - [X] days

**Attorney Note:** Treatment gaps > 30 days may require explanation in settlement narrative or deposition prep.

## KEY MILESTONES

1. **First Treatment:** [date] - [provider] - [details]
2. **Diagnostic Imaging:** [date] - [findings]
3. **Specialist Referral:** [date] - [specialist type]
4. **Physical Therapy:** [start date] to [end date] - [sessions]
5. **Treatment Conclusion:** [date] or "Ongoing"
```

### Structured Data (`visits_summary.md`)

```markdown
# Medical Visits & Bills Summary

| Date | Day # | Provider | Type | Chief Complaint | Diagnoses | Treatments | Bill | Source |
|------|-------|----------|------|-----------------|-----------|------------|------|--------|
| YYYY-MM-DD | 0 | [Provider] | ER | [complaint] | [diagnoses] | [treatments] | $XXX | [file] |
| YYYY-MM-DD | 7 | [Provider] | Follow-up | [complaint] | [diagnoses] | [treatments] | $XXX | [file] |

*Day # = days since incident*

**Summary Stats:**
- Total Visits: [count]
- Total Bills: $[amount]
- Average Visit Cost: $[amount]
- Treatment Duration: [X] days
- Unique Providers: [count]
- Treatment Gaps > 30 days: [count]
```

## Important Notes

### Citation Requirements
- Every entry MUST cite source document (extraction report filename)
- Include page numbers when available from extraction reports
- Direct quotes from medical records should be in quotation marks

### Timeline Gap Definitions
- **Minor Gap:** 14-30 days between visits (note but don't flag)
- **Moderate Gap:** 31-60 days (flag with ⚠️)
- **Major Gap:** > 60 days (flag with 🚩 and highlight for attorney review)

### Duplicate Detection
If same visit appears in multiple extraction reports:
- Use most complete version
- Note discrepancy if details conflict
- Cite both sources

### Incident Date
If available, read `Reports/case_facts.md` to get incident date. Use this to calculate:
- Days from incident to first treatment
- Timeline relative to accident

### Financial Data
- Sum all bill amounts from billing entries
- Flag any bills with missing amounts
- Separate by provider for settlement demand purposes

## Tools Available

You have access to:
- `read_file` - Read extraction reports and case facts
- `ls` - List files in directories
- `grep` - Search for patterns in files
- `write_file` - Save chronology outputs
- Bash tool for text processing (sed, awk, sort, etc.)

## File Path Conventions

**ALWAYS use workspace-relative paths:**
- ✅ CORRECT: `Reports/extractions/file1_extraction.md`
- ✅ CORRECT: `Reports/chronology.md`
- ❌ WRONG: `/Volumes/X10 Pro/Roscoe/workspace/Reports/chronology.md`

All paths start with `/` and are relative to workspace root.

## Common Issues and Solutions

### Issue: Dates in different formats
**Solution:** Normalize all dates to YYYY-MM-DD format. If date is unclear or "circa YYYY-MM", flag it and sort to end of that month.

### Issue: Extraction reports have inconsistent structure
**Solution:** Parse flexibly - look for date patterns, provider names, visit types. Don't assume rigid structure.

### Issue: Very large case (100+ visits)
**Solution:** Still create complete chronology. Consider adding table of contents with year/month sections for navigation.

### Issue: Conflicting information across sources
**Solution:** Note discrepancy in chronology entry, cite both sources, flag for attorney review.

## Success Criteria

✅ All extraction reports read and incorporated
✅ All visits and bills sorted chronologically
✅ Treatment gaps > 30 days identified and flagged
✅ Key milestones highlighted
✅ Financial summary complete
✅ Both narrative and structured outputs saved to `Reports/`
✅ User receives executive summary with file locations

## Example Usage

**User:** "Create a medical chronology for this case"

**Your workflow:**
1. Check `Reports/extractions/` - 24 extraction reports found
2. Read all 24 reports, extract 87 visits and 45 billing entries
3. Sort chronologically from 2024-01-15 to 2024-11-20
4. Identify 3 treatment gaps (45 days, 31 days, 62 days)
5. Calculate totals: $34,521 in bills, 87 visits, 12 providers
6. Build narrative chronology with all visits in timeline order
7. Create structured table with all data
8. Save to `Reports/chronology.md` and `Reports/visits_summary.md`
9. Present executive summary to user with key findings

**Result:** User receives comprehensive medical chronology ready for settlement demand letter, deposition prep, or trial preparation.
