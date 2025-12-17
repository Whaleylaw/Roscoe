# Chronology Entry Template

Use this format for individual medical chronology entries.

---

## Chronology Entry Structure

### JSON Format

```json
{
  "date": "MM/DD/YYYY",
  "provider": "Provider Name [Specialty / Facility / City, State]",
  "visit_type": "initial|follow_up|emergency|procedure|imaging|therapy|discharge",
  "medical_facts": "Formatted medical summary...",
  "diagnoses": [
    "ICD-10: M54.2 - Cervicalgia",
    "ICD-10: S13.4 - Cervical sprain"
  ],
  "treatments": [
    "MRI cervical spine ordered",
    "Physical therapy referral",
    "Medication: Flexeril 10mg"
  ],
  "comments": [
    {
      "type": "definition",
      "term": "Cervicalgia",
      "text": "Pain in the cervical (neck) region of the spine.",
      "source": "Mayo Clinic",
      "url": "https://mayoclinic.org/..."
    },
    {
      "type": "causation",
      "text": "Provider notes 'injuries consistent with MVA mechanism'"
    }
  ],
  "page_number": "BATES0051",
  "source_file": "Records/Medical/Provider/records.pdf"
}
```

---

### Medical Facts Formatting

Structure consistently for each entry:

```
VISIT TYPE (Initial Consultation / Follow-Up / Emergency Visit)

HPI: [History of present illness - symptoms, mechanism, progression]

PHYSICAL EXAM:
- [Finding 1]
- [Finding 2]
- ROM: [Range of motion findings]
- Neuro: [Neurological findings]

DIAGNOSES:
- [Diagnosis 1]
- [Diagnosis 2]

IMAGING: [If applicable]
- [Imaging type]: [Findings]

PLAN:
- [Treatment 1]
- [Treatment 2]
- Follow-up: [Timeframe]
```

---

### Comment Types

| Type | Purpose | When to Use |
|------|---------|-------------|
| `definition` | Medical term explanation | Unfamiliar terms (MUST cite source) |
| `causation` | Provider links to accident | Direct causation statements |
| `red_flag` | Potential issue | Gaps, inconsistencies, concerns |
| `author_note` | Analyst observation | Non-medical observations |

### Definition Comment Format

```json
{
  "type": "definition",
  "term": "Lumbar Radiculopathy",
  "text": "Compression of nerve roots in the lower spine causing pain, numbness, or weakness radiating down the leg.",
  "source": "Mayo Clinic",
  "url": "https://www.mayoclinic.org/diseases-conditions/radiculopathy"
}
```

### Causation Comment Format

```json
{
  "type": "causation",
  "text": "Dr. Smith states: 'Patient's cervical strain and radiculopathy are causally related to the motor vehicle accident of 04/26/2024.'"
}
```

### Red Flag Comment Format

```json
{
  "type": "red_flag",
  "category": "treatment_gap|inconsistent_history|preexisting|compliance",
  "severity": "minor|moderate|significant",
  "text": "45-day gap in treatment from 5/15 to 6/30. No documented reason."
}
```

---

### Page Reference Formats

| Source Type | Format | Example |
|-------------|--------|---------|
| Bates numbered | Use as-is | MILLS0051 |
| PDF page | pg. X | pg. 47 |
| Range | X-Y | MILLS0051-53 |

---

### Visit Type Categories

| Type | Use For |
|------|---------|
| `initial` | First visit to provider |
| `follow_up` | Return visits |
| `emergency` | ER visits |
| `procedure` | Injections, surgeries |
| `imaging` | X-ray, MRI, CT reports |
| `therapy` | PT, chiropractic |
| `discharge` | Final visit, discharge summary |

---

### Example Complete Entry

```json
{
  "date": "04/28/2024",
  "provider": "Dr. John Smith [Orthopedic Surgery / Baptist Health Orthopedics / Louisville, KY]",
  "visit_type": "initial",
  "medical_facts": "INITIAL CONSULTATION\n\nHPI: 42 y/o male presenting with neck and low back pain following MVA on 04/26/2024. Patient was restrained driver, struck from behind at stoplight. Immediate onset of neck pain and headache. Low back pain began following day.\n\nPHYSICAL EXAM:\n- Cervical: Tenderness to palpation at C5-C7 paraspinals\n- ROM: Limited flexion and rotation\n- Neuro: 5/5 strength bilateral UE, sensation intact\n- Lumbar: Tenderness L4-S1, positive straight leg raise R\n\nDIAGNOSES:\n- Cervical sprain/strain\n- Lumbar radiculopathy\n\nPLAN:\n- MRI cervical and lumbar spine\n- Physical therapy 2-3x/week\n- Flexeril 10mg TID PRN muscle spasm\n- Return 2 weeks",
  "diagnoses": [
    "S13.4XXA - Cervical sprain",
    "M54.16 - Lumbar radiculopathy"
  ],
  "treatments": [
    "MRI cervical spine",
    "MRI lumbar spine",
    "Physical therapy referral",
    "Flexeril 10mg TID PRN"
  ],
  "comments": [
    {
      "type": "definition",
      "term": "Radiculopathy",
      "text": "Compression or irritation of nerve roots causing pain, numbness, or weakness along the nerve pathway.",
      "source": "Cleveland Clinic",
      "url": "https://my.clevelandclinic.org/health/diseases/14089-radiculopathy"
    },
    {
      "type": "causation",
      "text": "Provider documents MVA as cause: 'presenting with neck and low back pain following MVA on 04/26/2024'"
    }
  ],
  "page_number": "SMITH0001-03",
  "source_file": "Records/Medical/Baptist_Ortho/smith_records.pdf"
}
```

