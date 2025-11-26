# Document Processing Workflow Skill

## When to Use This Skill

Use this skill when the user asks to:
- "Process all the documents in this case"
- "Extract text from all PDFs"
- "Read all the medical records"
- "Process the case documents"
- "OCR all the scanned files"
- "Extract tables from medical records"

## Overview

This skill processes all PDF documents in a case folder using the tiered OCR pipeline, extracting text and tables, and organizing everything into the Reports directory.

## Simple Workflow (5 Steps)

### Step 1: Identify Case Documents
```bash
# Find all PDFs in the case folder
find /case_name -name "*.pdf" -type f
```

**What to look for:**
- Medical records PDFs
- Medical bills PDFs
- Litigation documents (complaints, discovery, etc.)
- Expert reports

**Output:** List of PDF file paths

---

### Step 2: Process Each PDF Automatically

For **each PDF** found, run the read_pdf tool with auto-detection:

```bash
python /Tools/read_pdf.py /path/to/document.pdf /Reports/extractions/document_name.txt --extract-tables --quality-report
```

**What happens:**
- Tool auto-detects if PDF is text-based or scanned
- Uses PDFPlumber (Tier 1) for text PDFs
- Falls back to OCR (Tier 2) for scanned PDFs
- Extracts tables to `.tables.json` files
- Provides quality metrics

**Output per file:**
- `/Reports/extractions/document_name.txt` - Extracted text
- `/Reports/extractions/document_name.tables.json` - Tables (if any)
- Quality metrics to stderr

---

### Step 3: Track Processing Results

As each PDF is processed, create a processing log:

**File:** `/Reports/document_processing_log.json`

```json
{
  "case_name": "case_name",
  "processing_date": "2025-11-23",
  "total_pdfs": 15,
  "processed": 15,
  "failed": 0,
  "documents": [
    {
      "source_path": "/case_name/medical_records/doctor_note.pdf",
      "output_text": "/Reports/extractions/doctor_note.txt",
      "output_tables": "/Reports/extractions/doctor_note.tables.json",
      "method": "pdfplumber",
      "quality": "excellent",
      "confidence_score": 95,
      "page_count": 3,
      "table_count": 1,
      "issues": []
    },
    {
      "source_path": "/case_name/medical_records/old_scan.pdf",
      "output_text": "/Reports/extractions/old_scan.txt",
      "output_tables": null,
      "method": "ocr",
      "quality": "good",
      "confidence_score": 72,
      "page_count": 5,
      "table_count": 0,
      "issues": ["Medium OCR confidence - scan quality acceptable"]
    }
  ]
}
```

---

### Step 4: Generate Document Index

Create a human-readable index of all processed documents:

**File:** `/Reports/DOCUMENT_INDEX.md`

```markdown
# Document Processing Index
**Case:** case_name
**Processing Date:** 2025-11-23
**Total Documents:** 15

## Medical Records (8 documents)

### ✓ doctor_note.pdf
- **Source:** `/case_name/medical_records/doctor_note.pdf`
- **Extracted Text:** `/Reports/extractions/doctor_note.txt`
- **Tables:** 1 table extracted
- **Method:** PDFPlumber (Tier 1)
- **Quality:** Excellent (95/100)
- **Pages:** 3

### ✓ old_scan.pdf
- **Source:** `/case_name/medical_records/old_scan.pdf`
- **Extracted Text:** `/Reports/extractions/old_scan.txt`
- **Tables:** None
- **Method:** OCR (Tier 2)
- **Quality:** Good (72/100)
- **Pages:** 5
- **Note:** Medium OCR confidence - scan quality acceptable

## Medical Bills (4 documents)

[... continue for all documents ...]

## Documents Needing Review

### ⚠️ poor_quality_scan.pdf
- **Quality:** Fair (45/100)
- **Recommendation:** Consider Google Cloud Document AI for better accuracy
- **Issues:** Low OCR confidence - poor scan quality

## Summary Statistics

- **Total Pages Processed:** 142
- **Tables Extracted:** 12
- **Text-based PDFs:** 10 (PDFPlumber)
- **Scanned PDFs:** 5 (OCR)
- **High Quality Extractions:** 12
- **Needs Review:** 3
```

---

### Step 5: Report Completion

Print summary to user:

```
✓ Document Processing Complete

Case: case_name
Documents Processed: 15/15
Total Pages: 142
Tables Extracted: 12

Quality Breakdown:
  Excellent: 10 documents
  Good: 2 documents
  Fair: 3 documents (flagged for review)

All extracted text saved to: /Reports/extractions/
Document index created: /Reports/DOCUMENT_INDEX.md
Processing log saved: /Reports/document_processing_log.json

⚠️ 3 documents flagged for review (see DOCUMENT_INDEX.md)
```

---

## Tools Required

- `/Tools/read_pdf.py` - Tiered PDF processing pipeline
- File system tools (ls, find, mkdir)
- Bash for scripting

## Error Handling

**If a PDF fails to process:**
1. Log the error in processing_log.json
2. Continue processing remaining PDFs
3. Report failed files in final summary
4. Suggest manual review for failed files

**Common errors:**
- PDF is password-protected → Skip and log
- File is corrupted → Skip and log
- Missing dependencies (pytesseract) → Provide installation instructions

## Output Organization

```
/Reports/
├── extractions/              # All extracted text files
│   ├── doctor_note.txt
│   ├── doctor_note.tables.json
│   ├── old_scan.txt
│   └── ... (all PDFs)
├── DOCUMENT_INDEX.md         # Human-readable index
└── document_processing_log.json  # Machine-readable log
```

## Model Required

**sonnet** - This workflow requires reasoning about document organization and quality assessment.

## Success Criteria

- All PDFs in case folder are processed
- Text extracted for all readable documents
- Tables extracted where present
- Quality metrics recorded for each document
- Clear index created for attorney review
- Low-quality documents flagged for potential cloud processing

## Example Usage

**User:** "Process all the documents in the mo_alif case"

**Agent Response:**
1. "I'll process all PDFs in /mo_alif/ using the tiered OCR pipeline"
2. Finds 15 PDFs in medical_records and medical_bills folders
3. Processes each with auto-detection (PDFPlumber → OCR as needed)
4. Extracts 12 tables from lab results and billing statements
5. Creates document index with quality metrics
6. Reports: "15 documents processed, 12 tables extracted, 3 flagged for review"

## Notes for Implementation

- **Parallel Processing:** If >10 PDFs, consider processing 3-5 in parallel using multiple bash processes
- **Progress Updates:** Report progress every 3-5 documents ("Processed 5/15 documents...")
- **Table Extraction:** Automatically extract tables for lab results, billing statements, medication lists
- **Quality Flagging:** Flag any document with confidence <60 for potential cloud processing
- **Citation Preparation:** Document index enables easy citation lookup for medical sub-agents
