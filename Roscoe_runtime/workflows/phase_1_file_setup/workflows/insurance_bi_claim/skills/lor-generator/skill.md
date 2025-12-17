---
name: lor-generator
description: >
  Letter of Representation generation using the unified document generation system.
  Copies LOR template to the Insurance folder for the specific carrier, then calls
  generate_document.py which auto-fills all placeholders from case data based on the path.
  When Claude needs to create a Letter of Representation for BI or PIP insurance.
  Use for insurance claim setup, sending representation letters.
  Not for PDF forms, non-templated documents, or email-only correspondence.
---

# LOR Generator Skill

Generate Letters of Representation by copying templates to the correct location and using the unified document generator.

## Capabilities

- Generate BI LOR documents
- Generate PIP LOR documents
- Auto-fill all placeholders from case data
- Export to .docx and PDF
- Path-based context detection (insurance company, claim data)

**Keywords**: Letter of Representation, LOR, Word template, docx, insurance correspondence, adjuster letter

## Templates

| Template ID | Template File | Use For |
|-------------|---------------|---------|
| `lor_bi` | `2022 Whaley LOR to BI Adjuster(1)(1)(1) (1).docx` | At-fault party BI insurance |
| `lor_pip` | `2022 Whaley LOR to PIP Adjuster(1)(1) (1).docx` | PIP carrier |

## Workflow

```
1. IDENTIFY INSURANCE CLAIM
   └── Get insurance company name from insurance.json
   └── Determine claim type (BI or PIP)

2. CREATE DESTINATION FOLDER
   └── Path: /{project}/Insurance/{insurance_company}/
   └── Create folder if it doesn't exist

3. COPY TEMPLATE TO DESTINATION
   └── BI: Copy LOR to BI template
   └── PIP: Copy LOR to PIP template
   └── Filename: "LOR to {type} Adjuster.docx"

4. CALL GENERATE_DOCUMENT
   └── Tool: generate_document.py
   └── Input: Full path to copied template
   └── Tool auto-detects template and fills from path context

5. RECORD
   └── Update insurance.json with date_lor_sent
```

## Step-by-Step Instructions

### Step 1: Identify Insurance

```python
# Read insurance.json to find the insurance claim
import json
from pathlib import Path

project = "John-Doe-MVA-01-01-2025"
case_info = Path(f"${ROSCOE_ROOT}/{project}/Case Information")

with open(case_info / "insurance.json") as f:
    insurance_data = json.load(f)

# Find the BI or PIP insurance entry
# Note the insurance_company_name
```

### Step 2: Copy Template to Destination

```python
import shutil
from pathlib import Path

# Source templates
templates_dir = Path("${ROSCOE_ROOT}/templates")
bi_template = templates_dir / "2022 Whaley LOR to BI Adjuster(1)(1)(1) (1).docx"
pip_template = templates_dir / "2022 Whaley LOR to PIP Adjuster(1)(1) (1).docx"

# Destination (creates context for auto-fill)
project = "John-Doe-MVA-01-01-2025"
insurance_company = "State Farm"  # From insurance.json

dest_folder = Path(f"${ROSCOE_ROOT}/{project}/Insurance/{insurance_company}")
dest_folder.mkdir(parents=True, exist_ok=True)

# Copy template to destination
# For BI:
shutil.copy(bi_template, dest_folder / "LOR to BI Adjuster.docx")
# For PIP:
shutil.copy(pip_template, dest_folder / "LOR to PIP Adjuster.docx")
```

### Step 3: Generate Document

```bash
# The path tells the tool everything it needs:
# - Project name: John-Doe-MVA-01-01-2025
# - Context type: Insurance
# - Insurance company: State Farm

python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
    "${ROSCOE_ROOT}/John-Doe-MVA-01-01-2025/Insurance/State Farm/LOR to BI Adjuster.docx" \
    --pretty
```

**Python Usage**:

```python
import sys
sys.path.insert(0, "${ROSCOE_ROOT}/Tools/document_generation")
from generate_document import generate_document

result = generate_document(
    "${ROSCOE_ROOT}/John-Doe-MVA-01-01-2025/Insurance/State Farm/LOR to BI Adjuster.docx"
)

if result["status"] == "success":
    print(f"DOCX: {result['docx_path']}")
    print(f"PDF: {result['pdf_path']}")
    print(f"Fields filled: {result['fields_filled']}")
```

## How Path-Based Context Works

The path `/{project}/Insurance/{company}/LOR.docx` tells the tool:

1. **Project**: `John-Doe-MVA-01-01-2025` → Load case JSONs from Case Information/
2. **Context Type**: `Insurance` → This is an insurance-related document
3. **Context Name**: `State Farm` → Find State Farm in insurance.json
4. **Template**: `LOR to BI Adjuster.docx` → Identified as BI LOR template

The tool then:
- Loads `overview.json` for client info
- Finds "State Farm" in `insurance.json` for adjuster, claim number
- Fills all `{{placeholder}}` fields automatically

## Output

- Filled LOR document (.docx) - overwrites the template copy
- PDF export (.pdf) - created alongside
- Location: `/{project}/Insurance/{company}/LOR to {type} Adjuster.docx`

## References

For detailed information, see:
- **Tool documentation** → `/Tools/document_generation/generate_document.py`
- **Template Registry** → `/templates/template_registry.json`
- **Path parsing** → `/Tools/document_generation/path_parser.py`
