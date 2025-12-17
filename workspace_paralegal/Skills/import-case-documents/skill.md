# Import Case Documents Skill

## When to Use This Skill

Use this skill when the user asks to:
- "Import all the documents for this case"
- "Process all PDFs in the case folder"
- "Convert all PDFs to markdown"
- "Pre-process the case documents"
- "Import documents from [case_name] folder"

## Overview

This skill batch-processes all PDFs in a case folder to markdown format (.md files), creating a pre-processed cache that agents can read directly without re-processing PDFs every time.

**Key Benefit:** Process PDFs once, read many times. Dramatically faster agent access to document content.

## Simple Workflow (3 Steps)

### Step 1: Run Batch Import Tool

```bash
python /Tools/import_documents.py /case_name
```

**What happens:**
- Finds all PDFs in case folder (recursively)
- Processes each PDF using tiered OCR pipeline (PDFPlumber → PyTesseract)
- Creates .md file alongside each PDF (same directory, same name)
- Tracks quality metrics for each document
- Generates two reports (JSON log + Markdown index)

**Example output:**
```
================================================================================
BATCH PDF IMPORT
================================================================================

Case Folder: /mo_alif

[Step 1] Finding PDFs...
  Found 15 PDF files

[Step 2] Processing PDFs to Markdown...
  [1/15] Processing: doctor_note_2024-03-15.pdf... ✓ (95/100)
  [2/15] Processing: labs_2024-04-01.pdf... ✓ (88/100)
  [3/15] Processing: old_scan.pdf... ✓ (72/100)
  ...

[Step 3] Generating Reports...
  ✓ Import log saved: /Reports/import_log.json
  ✓ Document index saved: /Reports/DOCUMENT_INDEX.md

================================================================================
✓ IMPORT COMPLETE
================================================================================

Documents Processed: 15/15
⚠️  Needs Review: 3 (see DOCUMENT_INDEX.md)

All extracted markdown files saved alongside PDFs
Reports saved to: /Reports/
```

---

### Step 2: Review Document Index

Open `Reports/DOCUMENT_INDEX.md` to see:
- List of all processed documents organized by folder
- Quality scores and extraction methods for each
- Documents flagged for review (low quality)
- Summary statistics

**Example index:**
```markdown
# Document Import Index
**Case:** mo_alif
**Import Date:** 2025-11-23 14:32:15
**Total Documents:** 15

## medical_records (8 documents)

### ✓ doctor_note_2024-03-15.pdf
- **Source:** `/mo_alif/medical_records/doctor_note_2024-03-15.pdf`
- **Extracted:** `/mo_alif/medical_records/doctor_note_2024-03-15.md`
- **Method:** Pdfplumber
- **Quality:** Excellent (95/100)

### ⚠️ old_scan.pdf
- **Source:** `/mo_alif/medical_records/old_scan.pdf`
- **Extracted:** `/mo_alif/medical_records/old_scan.md`
- **Method:** Ocr
- **Quality:** Good (72/100)

## Summary Statistics
- **Total Documents Processed:** 15
- **Text-based PDFs (PDFPlumber):** 10
- **Scanned PDFs (OCR):** 5
- **Excellent Quality (≥80):** 12
- **Needs Review (<60):** 3
```

---

### Step 3: Report Completion to User

Provide summary to user:

```
✓ Document Import Complete

Case: mo_alif
Documents Processed: 15/15
Total Pages: 142

Processing Methods:
  PDFPlumber (text-based): 10 documents
  OCR (scanned): 5 documents

Quality Breakdown:
  Excellent (≥80): 12 documents
  Good (60-79): 0 documents
  Needs Review (<60): 3 documents

All PDFs converted to markdown format and saved alongside originals.
Agents can now read .md files directly without re-processing.

⚠️ 3 documents flagged for review (see /Reports/DOCUMENT_INDEX.md)
```

---

## Options and Flags

### Force Re-processing
```bash
# Re-process all PDFs even if .md files already exist
python /Tools/import_documents.py /case_name --force
```

### Custom Quality Threshold
```bash
# Flag documents with quality score below 70 (default: 60)
python /Tools/import_documents.py /case_name --quality-threshold 70
```

### Custom Report Location
```bash
# Save reports to different directory
python /Tools/import_documents.py /case_name --report-dir /custom_reports
```

---

## File Structure After Import

```
/mo_alif/
├── medical_records/
│   ├── doctor_note_2024-03-15.pdf
│   ├── doctor_note_2024-03-15.md          ← NEW: Extracted text + metadata
│   ├── labs_2024-04-01.pdf
│   ├── labs_2024-04-01.md                 ← NEW: Extracted text + tables
│   └── ...
├── medical_bills/
│   ├── bill_hospital.pdf
│   ├── bill_hospital.md                   ← NEW: Extracted text + tables
│   └── ...
└── litigation/
    ├── complaint.pdf
    ├── complaint.md                        ← NEW: Extracted text
    └── ...

/Reports/
├── import_log.json                         ← NEW: Machine-readable log
└── DOCUMENT_INDEX.md                       ← NEW: Human-readable index
```

---

## Markdown File Format

Each .md file contains:

**Frontmatter (Metadata):**
```yaml
---
source: doctor_note_2024-03-15.pdf
extraction_method: pdfplumber
quality_score: 95
overall_quality: excellent
pages: 3
extracted: 2025-11-23 14:32:15
---
```

**Text Content with Page Markers:**
```markdown
# Page 1

Patient Name: John Doe
Visit Date: 03/15/2024
Chief Complaint: Lower back pain

# Page 2

History of Present Illness:
...
```

**Tables (if any):**
```markdown
---

# Extracted Tables

## Table 1 (Page 2)

| Test Name | Result | Normal Range | Units |
|-----------|--------|--------------|-------|
| Hemoglobin | 14.2 | 13.5-17.5 | g/dL |
| WBC | 7.8 | 4.5-11.0 | x10^9/L |
```

---

## Subsequent Agent Access

After import, agents can read .md files directly:

```python
# Instead of processing PDF every time:
read_file("projects/mo_alif/medical_records/doctor_note_2024-03-15.md")

# Fast, no OCR overhead, includes all metadata and tables
```

**Cache behavior:**
- If agent runs `read_pdf.py` on a PDF that has a .md file, it automatically uses the cached .md
- Cache is validated by timestamp (re-processes if PDF is newer than .md)
- Can force re-processing with `--no-cache` flag

---

## Error Handling

**If a PDF fails to process:**
1. Error is logged in import_log.json
2. Processing continues for remaining PDFs
3. Failed files listed in final summary
4. User can manually re-process failed files

**Common failures:**
- Password-protected PDFs (skip and log)
- Corrupted PDFs (skip and log)
- Timeout (>5 minutes per PDF)

---

## Tools Required

- `Tools/import_documents.py` - Batch processing tool
- `Tools/read_pdf.py` - PDF extraction pipeline
- File system tools (ls, find)

---

## Model Required

**sonnet** - This workflow requires coordination of batch processing and quality assessment.

---

## Success Criteria

- All PDFs in case folder are processed
- .md file created for each PDF
- Quality metrics recorded in reports
- Low-quality documents flagged for review
- Processing log and index created
- User receives clear summary

---

## When NOT to Use This Skill

**Don't use this skill when:**
- User wants to read a single specific document (just read the .md file directly)
- Documents have already been imported (check for existing .md files first)
- User asks to re-import (use `--force` flag instead)

---

## Example Usage

**User:** "Import all the documents from the mo_alif case"

**Agent Response:**
1. "I'll process all PDFs in /mo_alif/ to markdown format"
2. Runs `python /Tools/import_documents.py /mo_alif`
3. Waits for completion
4. Reports: "15 documents processed, 3 flagged for review, all markdown files saved"
5. Points user to /Reports/DOCUMENT_INDEX.md for details

---

## Pro Tips

**Large case folders:**
- Import may take 5-10 seconds per PDF
- For 50+ PDFs, consider processing in batches by subfolder
- OCR processing (scanned PDFs) is slower than text-based

**Quality flagging:**
- Documents <60 quality score flagged by default
- Consider cloud processing (Google Document AI) for very low quality
- Review flagged documents in DOCUMENT_INDEX.md

**Incremental imports:**
- Running import again skips PDFs that already have .md files (unless `--force`)
- Only new PDFs are processed
- Use this for cases where documents arrive over time
