# LOR Generator Tool Usage

## generate_document.py (Unified Document Generator)

**Location**: `/Tools/document_generation/generate_document.py`

The unified document generator uses a path-based approach: copy the template to the output location, then the tool infers all context from the path.

## Usage Pattern

### Step 1: Copy Template to Output Location

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

### Step 2: Generate Document

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

## Return Value

```python
{
    "status": "success",
    "docx_path": "/path/to/output.docx",
    "pdf_path": "/path/to/output.pdf",
    "fields_filled": ["TODAY_LONG", "client.name", "insurance.claimNumber", ...],
    "fields_unfilled": [],  # Any placeholders not matched to data
    "template_id": "lor_bi"
}
```

## Complete Example: BI LOR Generation

```python
import json
import shutil
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, "${ROSCOE_ROOT}/Tools/document_generation")
from generate_document import generate_document

def generate_bi_lor(case_folder: str, insurance_company: str) -> dict:
    """Generate BI Letter of Representation using unified generator."""
    
    case_path = Path(case_folder)
    
    # Step 1: Create destination folder
    dest_folder = case_path / "Insurance" / insurance_company
    dest_folder.mkdir(parents=True, exist_ok=True)
    
    # Step 2: Copy template to destination
    template_src = Path("${ROSCOE_ROOT}/templates/2022 Whaley LOR to BI Adjuster(1)(1)(1) (1).docx")
    output_path = dest_folder / "LOR to BI Adjuster.docx"
    shutil.copy(template_src, output_path)
    
    # Step 3: Generate document (auto-fills from path context)
    result = generate_document(str(output_path))
    
    # Step 4: Update tracking
    if result["status"] == "success":
        with open(case_path / "Case Information/insurance.json") as f:
            insurance = json.load(f)
        
        # Find the right insurance entry and update
        for entry in insurance.get("bi", []):
            if entry.get("insurance_company_name") == insurance_company:
                entry["date_lor_sent"] = datetime.now().strftime("%Y-%m-%d")
                break
        
        with open(case_path / "Case Information/insurance.json", "w") as f:
            json.dump(insurance, f, indent=2)
    
    return result
```

## PIP LOR Specific Notes

PIP LOR includes Kentucky-specific instructions:
- "$6,000 reserve for bills as they come in"
- Exception for hospital or hospital-related bills

Confirm this instruction with user before sending - may vary by case.
