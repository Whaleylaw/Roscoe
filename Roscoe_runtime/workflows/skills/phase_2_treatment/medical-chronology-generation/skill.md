---
name: medical-chronology-generation
description: >
  Medical chronology creation toolkit for extracting treatment information from healthcare
  records and building chronological treatment summaries. Includes medical term research,
  red flag identification, and PDF generation. When Claude needs to create a medical
  chronology, extract treatment timelines from records, research medical terminology,
  identify gaps in treatment, document causation statements, or generate professional
  chronology PDFs. Use for demand preparation, case evaluation, or trial exhibits.
  Not for simple visit lists or when records haven't been collected yet.
---

# Medical Chronology Generation

Create professional medical chronology documents from healthcare records with cited definitions.

## Capabilities

- Extract treatment information from medical record PDFs
- Research and cite medical terminology definitions
- Identify red flags (treatment gaps, inconsistencies)
- Document causation statements from providers
- Generate formatted chronology PDFs
- Create clickable page references to source records

**Keywords**: medical chronology, treatment timeline, medical records, chronology PDF, treatment summary, medical terminology, red flags, causation, demand preparation

## CRITICAL: PDF Conversion Required

**The agent cannot read PDF medical records directly.** Before processing:

```bash
# Convert medical record PDF to markdown
python tools/read_pdf.py "/path/to/medical_records.pdf" --pretty

# Read the resulting .md file
read_file("/path/to/medical_records.md")
```

## CRITICAL: Research Medical Terms

**DO NOT hallucinate medical definitions.** Always research unfamiliar terms:

1. Use authoritative sources (Mayo Clinic, Cleveland Clinic, MedlinePlus)
2. Cite source with URL
3. Add to comment with citation

## Workflow

```
1. CONVERT PDFs TO MARKDOWN
   └── Tool: read_pdf.py (for each medical record file)

2. READ CONVERTED RECORDS
   └── read_file() on resulting .md files

3. EXTRACT KEY DATA (per visit)
   └── Date, provider, specialty, diagnoses, treatment, findings
   └── See references/extraction-fields.md

4. RESEARCH MEDICAL TERMS
   └── For unfamiliar terms → search authoritative sources
   └── See references/research-process.md

5. IDENTIFY RED FLAGS
   └── Gaps > 30 days, inconsistent histories, pre-existing conditions
   └── See references/red-flags.md

6. GENERATE CHRONOLOGY
   └── Tool: chronology_tools.py
```

## Quick Reference

| Data to Extract | Example |
|-----------------|---------|
| Date of Service | 04/26/2024 |
| Provider | Dr. Smith [Orthopedic / Baptist Health] |
| Chief Complaint | Neck pain following MVA |
| Diagnoses | Cervical strain, Lumbar radiculopathy |
| Treatment | MRI ordered, PT referral |
| Page Reference | Mills0051 |

## Tools

**Primary**: `tools/read_pdf.py` - Convert medical record PDFs
**Secondary**: `tools/chronology_tools.py` - Generate chronology PDF

```python
# Convert PDF first
python tools/read_pdf.py "/Records/Medical/provider/records.pdf"

# Then read converted markdown
read_file("/Records/Medical/provider/records.md")
```

## Chronology Entry Format

```json
{
  "date": "04.26.2024",
  "provider": "Dr. Smith [Orthopedic / Baptist Health]",
  "medical_facts": "INITIAL CONSULTATION...",
  "comments": [
    {
      "type": "definition",
      "term": "Radiculopathy",
      "text": "Nerve compression causing radiating pain",
      "source": "Mayo Clinic",
      "url": "https://mayoclinic.org/..."
    }
  ],
  "page_number": "Mills0051"
}
```

## References

For detailed guidance:
- **Extraction fields** → `references/extraction-fields.md`
- **Red flag criteria** → `references/red-flags.md`
- **Research process** → `references/research-process.md`

## Output

- Chronology JSON data for each visit
- Professional PDF document with:
  - Client name, DOB, injury date
  - Chronological entries with page references
  - Cited medical definitions
  - Red flags highlighted
  - Causation statements noted

