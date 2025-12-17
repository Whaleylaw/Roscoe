# Medical Chronology Extraction Fields

## Required Fields Per Visit

Every chronology entry must include these fields:

| Field | Description | Source Location |
|-------|-------------|-----------------|
| **Date of Service** | Exact date of visit | Header, usually top of note |
| **Provider Name** | Doctor/facility name | Header or signature |
| **Provider Specialty** | Type of practice | Header or implied by content |
| **Facility** | Clinic/hospital name | Header |
| **Page Number** | Bates number or page | Bottom of each page |

## Clinical Data to Extract

### History of Present Illness (HPI)
- Chief complaint
- Mechanism of injury (how it happened)
- Symptom onset and progression
- Prior treatment
- Current symptoms

### Physical Examination
- Vital signs (if relevant)
- Range of motion findings
- Palpation/tenderness
- Neurological findings
- Strength/sensation

### Diagnostic Studies
- Imaging ordered/results
- Lab results
- Special tests

### Assessment/Diagnoses
- ICD-10 codes (if listed)
- Diagnosis descriptions
- Differential diagnoses

### Treatment Plan
- Medications prescribed
- Referrals made
- Procedures performed
- Follow-up instructions

## Entry Formatting

### Medical Facts Column

Structure consistently:

```
INITIAL CONSULTATION / FOLLOW-UP / EMERGENCY VISIT

HPI: [Summary of chief complaint and history]

PHYSICAL EXAM: [Key findings only]

DIAGNOSES:
- Diagnosis 1
- Diagnosis 2

PLAN:
- Treatment 1
- Treatment 2
```

### Provider Format

```
Dr. [Last Name] [Specialty / Facility / City, State]
```

Examples:
- `Dr. Smith [Orthopedic Surgery / Baptist Health / Louisville, KY]`
- `Norton ER [Emergency Medicine / Norton Hospital / Louisville, KY]`
- `ABC Physical Therapy [Physical Therapy / Middletown, KY]`

## Special Situations

### Emergency Room Records
- Triage notes
- Nursing assessments
- Physician notes
- Discharge instructions
- All may be separate entries if different dates/times

### Hospital Admission
- Admission H&P
- Daily progress notes
- Consults
- Discharge summary
- Each becomes separate entry

### Imaging Reports
- May be separate from office visit
- Use date of imaging, not date of report
- Note ordering provider

### Physical Therapy
- Initial evaluation (detailed)
- Progress notes (summarize treatment)
- Discharge summary

## Page Reference Format

| Source Type | Format |
|-------------|--------|
| Bates numbered | Use Bates (e.g., "MILLS0051") |
| PDF page number | Use "pg. X" format |
| Multiple pages | Use range (e.g., "MILLS0051-53") |

## Data Target

Each entry should map to JSON:

```json
{
  "date": "MM/DD/YYYY",
  "provider": "Provider [Specialty / Facility / Location]",
  "visit_type": "initial|follow_up|emergency|procedure|imaging",
  "medical_facts": "Formatted text...",
  "diagnoses": ["ICD-10: Description"],
  "treatments": ["Treatment 1", "Treatment 2"],
  "page_number": "Bates or page reference",
  "source_file": "path/to/source.pdf"
}
```

