---
name: demand-letter-generation
description: >
  Demand letter drafting using the unified document generation system. Copy demand
  template to Documents/Demand folder, fill with case facts and exhibits, then run
  generate_document.py for PDF generation with letterhead and attached exhibits.
  When Claude needs to draft a demand letter, create settlement documentation, or
  generate a demand package with all exhibits. Use for bodily injury claims, UM/UIM
  claims, and property damage demands. Not for litigation pleadings.
---

# Demand Letter Generation

Create professional demand letters by copying the template to the case folder, filling it,
and using the unified document generator.

## Capabilities

- Fill structured markdown demand template
- Draft demand narrative from case facts
- Compile ICD-10 diagnosis codes
- Generate treatment summaries by provider
- Calculate special damages
- Embed photos in narrative
- Compile exhibits with separator pages
- Generate professional PDF matching firm format

**Keywords**: demand letter, settlement demand, bodily injury, special damages, ICD codes, demand package

## Workflow

```
1. COPY TEMPLATE TO DESTINATION
   └── Copy templates/demand_template.md to /{project}/Documents/Demand/
   └── Name: demand_draft_[client]_[date].md

2. FILL YAML FRONTMATTER
   └── Client name, defendant, date of incident
   └── Insurance company, adjuster, claim number
   └── Read from case JSONs

3. WRITE SECTIONS
   └── Introduction - representation, Rule 408
   └── Facts & Liability - narrative, negligence
   └── Injuries table - diagnoses with ICD codes
   └── Treatment chronology - by provider
   └── Special damages - medical, wages
   └── Demand - amount and deadline
   └── Exhibits - file paths to attach

4. CALL GENERATE_DOCUMENT
   └── Tool: generate_document.py
   └── Input: Path to filled demand.md
   └── Creates PDF with letterhead and exhibits

5. VERIFY OUTPUT
   └── demand.docx created
   └── demand.pdf created with exhibits
```

## Step-by-Step Instructions

### Step 1: Copy Template

```python
import shutil
from pathlib import Path
from datetime import datetime

# Source template
templates_dir = Path("${ROSCOE_ROOT}/templates")
demand_template = templates_dir / "demand_template.md"

# Destination
project = "John-Doe-MVA-01-01-2025"
dest_folder = Path(f"${ROSCOE_ROOT}/{project}/Documents/Demand")
dest_folder.mkdir(parents=True, exist_ok=True)

# Copy with descriptive name
date_str = datetime.now().strftime("%Y-%m-%d")
shutil.copy(demand_template, dest_folder / f"demand_draft_{date_str}.md")
```

### Step 2: Fill Template

The template has YAML frontmatter and sections:

```markdown
---
client_name: "John Doe"
defendant_name: "Jane Smith"
date_of_incident: "January 1, 2025"
case_type: "MVA"
insurance_company: "State Farm"
claim_number: "12-345-6789"
adjuster_name: "Bob Johnson"
adjuster_email: "bob@statefarm.com"
adjuster_address: |
  123 Insurance Way
  Louisville, KY 40202
demand_amount: "$50,000.00"
---

# INTRODUCTION
[Write opening paragraph]

# FACTS & LIABILITY
[Write accident narrative]

# INJURIES & TREATMENTS
## Summary of Injuries
| Injury/Diagnosis | ICD Code |
|------------------|----------|
| Cervical Strain | S13.4XXA |

## Treatment Chronology
### Provider Name
- **Treatment Timeline**: ...
- **Summary**: ...

# SPECIAL DAMAGES
## Past Medical Expenses
| Provider | Dates | Amount |
|----------|-------|--------|

# DEMAND
[Write demand amount and deadline]

# EXHIBITS
1. Medical Records - Provider | /path/to/records.pdf
2. Bills - Provider | /path/to/bills.pdf
```

### Step 3: Generate Document

```bash
python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
    "${ROSCOE_ROOT}/John-Doe-MVA-01-01-2025/Documents/Demand/demand_draft_2025-01-15.md" \
    --pretty
```

**Python Usage**:

```python
import sys
sys.path.insert(0, "${ROSCOE_ROOT}/Tools/document_generation")
from generate_document import generate_document

result = generate_document(
    "${ROSCOE_ROOT}/John-Doe-MVA-01-01-2025/Documents/Demand/demand_draft_2025-01-15.md"
)

if result["status"] == "success":
    print(f"DOCX: {result['docx_path']}")
    print(f"PDF: {result['pdf_path']}")
```

## Auto-Fill vs Agent-Fill Fields

| Auto-Fill (from case data) | Agent Fills |
|---------------------------|-------------|
| `{{TODAY}}` | YAML frontmatter values |
| `{{client.name}}` | Facts narrative |
| `{{firm.letterhead}}` | Injuries table |
| `{{firm.signature}}` | Treatment chronology |
| `{{incidentDate}}` | Damages sections |
| | Demand amount |
| | Exhibit paths |

## Exhibit Organization

Standard order:
1. Medical Records (by provider, chronologically)
2. Medical Bills (by provider)
3. Accident/Police Report
4. Photographs
5. Wage Documentation
6. Property Damage
7. Expert Reports

Format in template:
```markdown
# EXHIBITS
1. UK Healthcare Medical Records | /path/to/uk_records.pdf
2. UK Healthcare Bills | /path/to/uk_bills.pdf
3. Police Report | /path/to/police_report.pdf
```

## Output

- Filled markdown template (saved for reference)
- `demand.docx` - Word document
- `demand.pdf` - Complete demand packet with:
  - Professional letterhead
  - Formatted sections with tables
  - Embedded photos
  - Exhibit separator pages
  - All exhibit PDFs attached

## References

- **Narrative writing** → `references/narrative-sections.md`
- **Demand valuation** → `references/demand-valuation.md`
- **Exhibit compilation** → `references/exhibit-compilation.md`
- **Template** → `/templates/demand_template.md`
- **Unified tool** → `/Tools/document_generation/generate_document.py`
