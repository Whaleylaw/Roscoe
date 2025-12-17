---
name: medical_chronology
description: >
  Maintain running medical chronology as records are received. Extracts treatment
  information, researches medical terminology, identifies red flags, and generates
  professional chronology documents.
phase: treatment
workflow_id: medical_chronology
related_skills:
  - skills/medical-chronology-generation/skill.md
related_tools:
  - tools/read_pdf.py (CRITICAL - convert PDFs to markdown)
  - tools/chronology_tools.py (generate chronology PDF)
templates:
  - templates/chronology_entry.md
---

# Workflow: Ongoing Medical Chronology

## Phase: treatment
## Goal: Maintain running medical chronology as records come in

**CRITICAL**: The agent cannot read PDFs directly. Use `tools/read_pdf.py` to convert medical records to markdown before processing.

---

## When to Trigger

- New medical records received
- Regular chronology update cycle
- User requests chronology update
- Preparing for client status meeting

---

## Inputs Required

- Received medical records
- Existing chronology (if any)
- Client's injury date
- List of diagnoses

---

## Step-by-Step Process

### Step 1: Identify New Records
1. Check `Records/Medical/` for newly received records
2. Cross-reference with existing chronology
3. List records not yet processed

### Step 2: Convert PDFs to Markdown
**REQUIRED before processing any record**

```bash
# Convert each medical record PDF
python tools/read_pdf.py "/path/to/medical_records.pdf" --pretty
```

Then read the resulting .md file with `read_file()`.

### Step 3: Extract Key Information
**Use skill: skills/medical-chronology-generation/skill.md**

For each new record (now in markdown), extract:
- Date of service
- Provider name and specialty
- Facility/location
- Chief complaint / reason for visit
- History of present illness
- Physical examination findings
- Diagnoses (ICD codes if available)
- Treatment plan
- Medications prescribed
- Referrals made
- Follow-up instructions
- Page numbers in source document

### Step 3: Research Medical Terms
**Use skill: medical-chronology-generation**

For unfamiliar terms:
1. Use `internet_search` to find authoritative definition
2. Search: `"[term] definition site:mayoclinic.org OR site:clevelandclinic.org"`
3. Extract definition and source URL
4. Add to research cache for future use
5. Include citation in chronology comments

### Step 4: Identify Red Flags
**Use skill: red-flag-identification**

Flag any:
- Gaps in treatment
- Inconsistent histories
- Pre-existing conditions mentioned
- Causation statements
- Unusual findings

### Step 5: Update Chronology Data
Add entries to `chronology_data.json`:
```json
{
  "date": "MM.DD.YYYY",
  "provider": "Provider Name [Specialty/Facility]",
  "medical_facts": "Detailed summary of visit...",
  "comments": [
    {
      "type": "definition",
      "term": "Medical Term",
      "text": "Definition text",
      "source": "Mayo Clinic",
      "url": "https://..."
    },
    {
      "type": "red_flag",
      "text": "Note about inconsistency..."
    },
    {
      "type": "causation",
      "text": "Provider states injury caused by..."
    }
  ],
  "page_number": "Bates000123",
  "source_file": "Records/Medical/Provider/records.pdf"
}
```

### Step 6: Note Treatment Gaps
If gap > 30 days between visits:
1. Note the gap in chronology
2. Flag for client follow-up
3. Consider impact on case

### Step 7: Update Chronology Document
1. Regenerate chronology from updated data
2. Save draft to `Reports/chronology_draft.json`
3. Note last update date
4. Track what records have been processed

---

## Skills Used

- **medical-record-extraction**: Extract information from records
- **medical-chronology-generation**: Format and structure chronology
- **red-flag-identification**: Identify issues in records
- **causation-analysis**: Identify causation statements

---

## Completion Criteria

- [ ] All new records processed
- [ ] Entries added to chronology data
- [ ] Medical terms researched and cited
- [ ] Red flags documented
- [ ] Treatment gaps noted
- [ ] Chronology draft updated

---

## Outputs

- Updated `Reports/chronology_draft.json`
- Updated `Resources/medical_research_cache.json`
- Treatment gap notes
- Red flag documentation

---

## Phase Exit Contribution

This workflow contributes to:
- `chronology_current`

---

## Chronology Update Schedule

During active treatment:
- Update within 1 week of receiving new records
- Review with attorney monthly
- Flag significant findings immediately

---

## Integration with Medical Chronology Completion

This workflow maintains the DRAFT chronology.
The `medical_chronology_completion` workflow in the Demand phase:
- Finalizes the chronology
- Generates the PDF with full formatting
- Merges with source records for clickable links

