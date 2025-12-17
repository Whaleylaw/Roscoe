# PDF Tool Usage for Police Report Analysis

## The Problem

Agents cannot natively read PDF files. Police/crash reports from BuyCrash and law enforcement are always PDFs.

## The Solution

Use `read_pdf.py` to convert the PDF to markdown, then read the markdown file.

---

## Step-by-Step Process

### 1. Locate the Crash Report PDF

```
{project}/Reports/crash_report.pdf
-or-
{project}/Investigation/police_report.pdf
```

### 2. Convert PDF to Markdown

```bash
python tools/read_pdf.py "{project}/Reports/crash_report.pdf" --pretty
```

**Output:**
```json
{
  "status": "success",
  "input_file": "{project}/Reports/crash_report.pdf",
  "output_file": "{project}/Reports/crash_report.md",
  "method": "pdfplumber",  // or "ocr" for scanned
  "quality_score": 85,
  "pages": 3
}
```

### 3. Read the Converted Markdown

```bash
read_file("{project}/Reports/crash_report.md")
```

The `.md` file contains:
- Frontmatter with metadata (quality score, extraction method)
- Full text content of the report
- Tables preserved in markdown format

---

## Tool Location

The `read_pdf.py` tool exists in two places:

1. **Local copy**: `tools/read_pdf.py` (in this workflow folder)
2. **Canonical**: `/Tools/document_processing/read_pdf.py`

Use the local copy when running from workflow context.

---

## Handling Poor Quality Scans

If the quality score is low (<60) or text is garbled:

1. **Request better copy** from law enforcement
2. **Use OCR mode** explicitly:
   ```bash
   python tools/read_pdf.py crash_report.pdf --force-ocr
   ```
3. **Manual transcription** for critical sections

---

## Caching Behavior

- First run creates `.md` file alongside PDF
- Subsequent runs use cached `.md` if PDF unchanged
- Use `--no-cache` to force re-processing:
  ```bash
  python tools/read_pdf.py crash_report.pdf --no-cache
  ```

---

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Empty output | Scanned PDF without OCR | Use `--force-ocr` |
| Garbled text | Poor scan quality | Request better copy |
| Missing tables | Complex formatting | Manual extraction |
| Wrong encoding | Non-standard PDF | Try `--force-ocr` |

