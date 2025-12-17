# Workflow Tools

This folder contains all tools used across workflow phases, copied here for central access.

## Quick Start

1. **Read the manifest** to discover available tools:
   ```
   tools/tools_manifest.json
   ```

2. **Find the tool you need** by matching task keywords to tool descriptions

3. **Execute from this folder**:
   ```bash
   python tools/{tool_file}.py [args]
   ```

## Tools in This Folder

| Tool | File | Description |
|------|------|-------------|
| Create Case | `create_case.py` | Create new case folder structure |
| PIP Waterfall | `pip_waterfall.py` | Kentucky PIP carrier determination |
| Crash Order | `lexis_crash_order.py` | Order crash reports from LexisNexis |
| Read PDF | `read_pdf.py` | Extract text from PDFs |
| DocuSign Send | `docusign_send.py` | Send documents for e-signature |
| DocuSign Config | `docusign_config.py` | DocuSign API configuration |
| Chronology Tools | `chronology_tools.py` | Medical chronology generation |
| Medical Request | `medical_request_generator.py` | Generate medical records requests |
| Demand PDF | `generate_demand_pdf.py` | Generate demand letter PDFs |
| Generate Document | `generate_document.py` | Unified document generation |

## Manifest Structure

The `tools_manifest.json` contains:
- `id`: Unique tool identifier
- `name`: Human-readable name
- `file`: Python filename
- `path`: Path within this folder
- `category`: Tool category
- `description`: What the tool does
- `usage`: How to run the tool
- `inputs`: Required inputs
- `outputs`: What it produces
- `when_to_use`: Trigger conditions

## Tool Categories

| Category | Purpose |
|----------|---------|
| `case_management` | Case folder creation and setup |
| `insurance` | PIP waterfall, claim processing |
| `document_retrieval` | Ordering crash reports, external docs |
| `document_processing` | Reading PDFs, extracting text |
| `document_generation` | Creating documents from templates |
| `esignature` | DocuSign integration |
| `medical` | Medical chronology tools |

## Central Tools Location

Additional tools are available at:
```
${ROSCOE_ROOT}/Tools/
```

That folder contains the full tool suite with `tools_manifest.json`.
