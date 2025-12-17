---
name: police-report-analysis
description: >
  Extracts insurance information, accident details, and liability indicators from Kentucky
  police/collision reports (typically from BuyCrash). Requires PDF to be converted to 
  markdown first using read_pdf.py tool. Use when analyzing police reports, crash reports, 
  extracting insurance carriers, identifying at-fault parties, determining PIP eligibility, 
  or gathering accident details for MVA cases. Integrates with PIP waterfall and insurance 
  claim setup workflows.
---

# Police Report Analysis

Extracts structured data from Kentucky collision reports after PDF conversion to markdown.

## Capabilities

- Convert crash report PDF to readable markdown
- Extract insurance information for all parties
- Identify at-fault parties and liability indicators
- Extract witness information
- Determine PIP waterfall inputs
- Decode Kentucky collision report codes

**Keywords**: police report, crash report, collision report, BuyCrash, accident report, insurance extraction, liability, PIP waterfall, Kentucky codes

## CRITICAL: PDF Conversion Required

**The agent cannot read PDFs directly.** Before analyzing a police report:

1. **Convert PDF to Markdown** using `read_pdf.py`
2. **Read the resulting .md file** for analysis

## Tool Usage

### Step 1: Convert PDF to Markdown

**Tool**: `read_pdf.py` at `tools/read_pdf.py` or `/Tools/document_processing/read_pdf.py`

```bash
# Convert crash report PDF to readable markdown
python read_pdf.py "/path/to/crash_report.pdf" --pretty

# Output: Creates crash_report.md alongside the PDF
```

The tool will:
- Auto-detect if PDF is text-based or scanned
- Use OCR if needed for scanned documents
- Create a `.md` file with extracted text
- Cache results for instant re-access

### Step 2: Read Converted Markdown

```bash
# Read the converted markdown file
read_file("/path/to/crash_report.md")
```

### Step 3: Analyze Content

Use the Kentucky codes reference to decode numeric values and extract:
- Report details (number, officer, agency)
- All unit information (vehicles, drivers, insurance)
- Liability indicators (citations, contributing factors)
- PIP waterfall inputs

## Workflow

```
1. RECEIVE PDF
   └── User uploads crash report PDF

2. CONVERT TO MARKDOWN
   └── Tool: read_pdf.py
   └── Creates .md file for agent to read

3. READ MARKDOWN
   └── Agent reads converted text

4. IDENTIFY CLIENT UNIT
   └── Determine which Unit (1, 2, etc.) is the client

5. EXTRACT CORE DATA
   └── Report details, accident info, all units

6. EXTRACT INSURANCE
   └── PIP source, BI source for each unit

7. ANALYZE LIABILITY
   └── Citations, contributing factors, fault indicators

8. EXTRACT WITNESSES
   └── Names, contact info, statements

9. COMPARE TO CLIENT STORY
   └── Flag any discrepancies

10. IDENTIFY RED FLAGS
    └── Client cited, refused treatment, no insurance, etc.

11. GENERATE OUTPUT
    └── Use template: references/output_template.md
```

## Quick Reference

| Data Needed | Source in Report |
|-------------|------------------|
| PIP Insurance | Client's Unit insurance section |
| BI Insurance | At-fault Unit insurance section |
| At-fault determination | Citations, Contributing Factors, Narrative |
| Driver vs Owner | "Is Driver Owner?" field (critical for PIP) |
| Witnesses | Witness section at end of report |

## Output Format

**Use the full template at:** `references/output_template.md`

The template includes structured sections for:
- Accident summary with decoded Kentucky codes
- All unit details (vehicles, drivers, insurance)
- PIP and BI insurance extraction
- Liability assessment with citations and contributing factors
- Officer's narrative (verbatim + summary)
- Story comparison (client vs report)
- Witness information
- Red flags checklist
- PIP waterfall input data
- Next actions checklist
- Data targets for case file updates

**Quick Output Preview:**

```markdown
## Police Report Analysis Complete

**Report**: #[NUMBER] | Officer: [NAME] | Agency: [AGENCY] | Date: [DATE]

**Insurance Extracted**:
- PIP Source: Unit [#] - [Carrier] ✅
- BI Source: Unit [#] - [Carrier] ✅

**Liability**: Unit [#] ([Driver Name]) - [Confidence Level]

**Red Flags**: [Count] found - see details

**Next Actions**: [X] items pending
```

See `references/output_template.md` for the complete structured template.

## Red Flags to Check

- ⚠️ **Client was cited** - Liability concern
- ⚠️ **Client refused medical attention** - Gap in treatment
- ⚠️ **No insurance for any party** - Recovery concern
- ⚠️ **Driver impairment codes** - Punitive damages potential
- ⚠️ **Pre-existing damage noted** - Causation defense
- ⚠️ **Story discrepancy** - Credibility issue

## References

| Reference | Purpose | Location |
|-----------|---------|----------|
| Output Template | Complete extraction template | `references/output_template.md` |
| Kentucky Codes | Decode numeric codes on reports | `references/kentucky_codes.md` |
| Tool Usage | PDF conversion instructions | `references/tool-usage.md` |
| Tools Manifest | All available tools | `/Tools/tools_manifest.json` |
| PIP Waterfall | Determine PIP carrier | `/Tools/insurance/pip_waterfall.py` |

## Integration

### This Skill Triggers:
- Insurance claim setup (creates entries in insurance.json)
- PIP waterfall analysis
- Contact card creation for at-fault parties and witnesses

### Triggered By:
- `accident_report` workflow when PDF is received
