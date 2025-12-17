---
name: complaint-drafting
description: >
  Draft Kentucky circuit court complaints for personal injury cases using the
  unified document generation system. Uses complaint_library for template selection
  with decision trees for MVA, premises, and combined claims. Copy appropriate template
  to Litigation folder, fill agent sections, then run generate_document.py for auto-fill
  and PDF generation.
---

# Complaint Drafting Skill

## Overview

Generate properly formatted Kentucky circuit court complaints using the complaint library's
decision tree to select the appropriate template, then fill and generate the final document.

## Complaint Library

**Location:** `complaint_library/`

The complaint library provides:
- **11 Base Templates** - Complete complaints for common case types
- **8 Count Modules** - Mix-and-match legal theories for custom complaints
- **Decision Tree** - Flowchart for template selection

### Quick Template Selection

| Case Type | Template |
|-----------|----------|
| Standard MVA | `mva_standard.md` |
| MVA + Underinsured | `mva_uim.md` |
| MVA + Uninsured | `mva_um.md` |
| MVA + Employer Liable | `mva_vicarious_liability.md` |
| MVA + Owner Entrusted | `mva_negligent_entrustment.md` |
| MVA + Stolen Vehicle Fraud | `mva_stolen_vehicle_fraud.md` |
| Slip/Fall | `premises_standard.md` |
| Dog Bite | `premises_dog_bite.md` |
| Government Defendant | `premises_government_entity.md` |
| Bad Faith by Carrier | `bi_with_bad_faith.md` |
| Bad Faith + UIM | `bi_bad_faith_uim.md` |

**Full Decision Tree:** See `complaint_library/decision_tree.md`

## When to Use

Use when:
- Filing new personal injury lawsuit
- Need complaint with all required sections
- Must comply with Kentucky Civil Rules

DO NOT use if:
- Federal court filing (different format)
- Administrative proceeding
- Small claims court

## Workflow

```
1. ANALYZE CASE → SELECT TEMPLATE
   └── Review case facts
   └── Follow complaint_library/decision_tree.md
   └── Select appropriate base template OR build custom with modules

2. COPY TEMPLATE TO DESTINATION
   └── Copy selected template from complaint_library/templates/base/ to /{project}/Litigation/
   └── Name: Complaint.md

3. FILL AGENT SECTIONS
   └── [COUNTY]: Venue county
   └── [FACTS]: Accident narrative
   └── [INJURIES]: List of injuries
   └── [NEGLIGENT ACTS]: List of negligent acts
   └── [DAMAGES]: Damages sought

3. CALL GENERATE_DOCUMENT
   └── Tool: generate_document.py
   └── Input: Path to saved Complaint.md
   └── Auto-fills: {{client.name}}, {{defendant.name}}, {{incidentDate}}, firm info

4. VERIFY OUTPUT
   └── Complaint.docx created
   └── Complaint.pdf created
   └── All placeholders filled
```

## Step-by-Step Instructions

### Step 0: Select Template Using Decision Tree

1. Open `complaint_library/decision_tree.md`
2. Follow the flowchart based on case facts:
   - Case type? (MVA / Premises / Other)
   - Insurance status? (Insured / Underinsured / Uninsured)
   - Special circumstances? (Employment / Entrustment / Bad Faith / etc.)
3. Identify the appropriate template

**Example:** Standard MVA case → `mva_standard.md`

### Step 1: Copy Template to Destination

```python
import shutil
from pathlib import Path

# Complaint library location
library_dir = Path("${ROSCOE_ROOT}/workflows/phase_7_litigation/subphases/7_1_complaint/complaint_library/templates/base")

# Select template based on decision tree
# Options: mva_standard.md, mva_uim.md, mva_vicarious_liability.md, etc.
selected_template = library_dir / "mva_standard.md"

# Destination (project's Litigation folder)
project = "John-Doe-MVA-01-01-2025"
dest_folder = Path(f"${ROSCOE_ROOT}/{project}/Litigation")
dest_folder.mkdir(parents=True, exist_ok=True)

# Copy template
shutil.copy(selected_template, dest_folder / "Complaint.md")
```

### Building Custom Complaints

If no base template fits, build using modules:

1. Start with `count_negligence.md` from `complaint_library/templates/modules/`
2. Add applicable count modules (UIM, Bad Faith, Vicarious Liability, etc.)
3. Combine into single document following structure in `complaint_library/README.md`

### Step 2: Fill Agent Sections

Open the copied `Complaint.md` and fill in:

| Section | Agent Fills |
|---------|-------------|
| `[COUNTY]` | Jefferson, Fayette, etc. |
| `[DIVISION NUMBER]` | Court division if known |
| `[CLIENT ADDRESS]` | Client's street address |
| `[CITY]` | City of residence |
| `[DEFENDANT ADDRESS]` | Defendant's address |
| `[LOCATION/ACTIVITY]` | Where plaintiff was at incident |
| `[DESCRIBE DEFENDANT'S CONDUCT]` | What defendant was doing |
| `[DESCRIBE HOW INCIDENT OCCURRED]` | How accident happened |
| `[SPECIFIC NEGLIGENT ACT]` | Acts of negligence |
| `[LIST INJURIES]` | Injuries sustained |
| `[ADDITIONAL DAMAGES]` | Other damages if applicable |

**Auto-fill fields** (handled by tool):
- `{{client.name}}` - From overview.json
- `{{defendant.name}}` - From contacts.json
- `{{incidentDate}}` - From overview.json
- `{{firm.attorney}}`, `{{firm.barNumber}}`, etc. - From firm config

### Step 3: Generate Document

```bash
# Call unified document generator
python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
    "${ROSCOE_ROOT}/John-Doe-MVA-01-01-2025/Litigation/Complaint.md" \
    --pretty
```

**Python Usage**:

```python
import sys
sys.path.insert(0, "${ROSCOE_ROOT}/Tools/document_generation")
from generate_document import generate_document

result = generate_document(
    "${ROSCOE_ROOT}/John-Doe-MVA-01-01-2025/Litigation/Complaint.md"
)

if result["status"] == "success":
    print(f"DOCX: {result['docx_path']}")
    print(f"PDF: {result['pdf_path']}")
```

## Output

- `Complaint.md` - Filled markdown (saved for reference)
- `Complaint.docx` - Word document
- `Complaint.pdf` - PDF for filing/service
- Location: `/{project}/Litigation/`

## Key Formatting Rules

- Number paragraphs consecutively
- Uppercase section headers
- Proper indentation for subparagraphs
- Include jury demand

**See:** `references/court-rules.md` for Kentucky requirements

## References

- **Complaint Library** → `complaint_library/README.md`
- **Decision Tree** → `complaint_library/decision_tree.md`
- **Base Templates** → `complaint_library/templates/base/`
- **Count Modules** → `complaint_library/templates/modules/`
- **Court rules** → `references/court-rules.md`
- **Caption format** → `references/caption-format.md`
- **Causes of action** → `references/cause-action-templates.md`
- **Unified tool** → `/Tools/document_generation/generate_document.py`

## Related Skills

- `service-of-process` - For serving the filed complaint
- `answer-analysis` - For reviewing defendant's response
