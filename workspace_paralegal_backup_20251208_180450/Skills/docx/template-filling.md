# Word Template Filling Skill

## Overview

This skill covers filling pre-existing Word templates with case data to generate final documents. Use this for standardized legal documents like:
- Letters of Representation
- Medical Records Requests
- HIPAA Authorization Forms
- Demand Letters (from template)
- Settlement Agreements
- Court Forms

## When to Use This Skill

Use template filling when:
- You have a standardized `.docx` template with placeholders
- The template uses Jinja2 syntax: `{{ variable_name }}`
- You need to produce multiple similar documents
- High layout fidelity to the original template is required

**Don't use this** for:
- Creating documents from scratch (use docx-js instead)
- Editing existing client documents with tracked changes (use OOXML redlining)
- Documents that need substantial structural changes

## Available Tools

| Tool | Description |
|------|-------------|
| `fill_word_template()` | Fill a template with data, optionally export PDF |
| `export_pdf_from_docx()` | Convert any DOCX to high-fidelity PDF |
| `convert_doc_to_docx()` | Convert legacy .doc files to .docx format |
| `list_template_variables()` | Discover placeholders in a template |
| `check_document_tools_status()` | Verify dependencies are available |

## Workflow

### 1. Identify Template

Find the appropriate template in `/forms/templates/`:

```
list_template_variables("/forms/templates/Letter_of_Rep.docx")
```

This returns all placeholder variables the template expects.

### 2. Gather Case Data

Build a context dictionary with all required values:

```python
context = {
    "client_name": "John Wilson",
    "date_of_accident": "January 15, 2024",
    "insurance_company": "State Farm Insurance",
    "claim_number": "CLM-2024-123456",
    "adjuster_name": "Sarah Smith",
    "our_file_number": "24-001",
    "date_today": "March 1, 2024"
}
```

### 3. Fill Template

```
fill_word_template(
    template_path="/forms/templates/Letter_of_Rep.docx",
    output_path="/wilson-case/Documents/Wilson_LOR.docx",
    context={
        "client_name": "John Wilson",
        "date_of_accident": "January 15, 2024",
        "insurance_company": "State Farm Insurance",
        "claim_number": "CLM-2024-123456"
    },
    export_pdf=True
)
```

### 4. Review Output

The tool reports:
- Path to generated DOCX
- Path to PDF (if requested)
- Which placeholders were filled
- Any unfilled placeholders (warnings)

## Template Locations

Standard templates are in `/forms/templates/`:
- `Letter_of_Rep.docx` - Letter of Representation
- `Medical_Records_Request.docx` - HIPAA Records Request
- `PIP_Letter.docx` - PIP Claim Letter
- `Demand_Letter_Template.docx` - Demand Letter Framework

## Placeholder Syntax

Templates use Jinja2 placeholder syntax:

| Placeholder | Example Value |
|-------------|---------------|
| `{{ client_name }}` | John Wilson |
| `{{ date_of_accident }}` | January 15, 2024 |
| `{{ insurance_company }}` | State Farm |
| `{{ claim_number }}` | CLM-123456 |

**Advanced features** (supported by docxtpl):
- Loops: `{% for item in items %}...{% endfor %}`
- Conditionals: `{% if condition %}...{% endif %}`
- Filters: `{{ amount \| currency }}`

## Data Type Handling

The tool automatically handles:
- `None` values → empty string
- `datetime` objects → "January 15, 2024" format
- `Decimal` values → string representation
- Nested dictionaries and lists

## Error Handling

Common issues:

**"Template not found"**
- Check the path is correct
- Ensure file has `.docx` extension

**"Unfilled placeholders"**
- Template has variables you didn't provide
- Review with `list_template_variables()` first

**"LibreOffice not available"**
- PDF export requires LibreOffice
- DOCX is still created
- See LIBREOFFICE_SETUP.md for installation

## Examples

### Letter of Representation

```
fill_word_template(
    template_path="/forms/templates/Letter_of_Rep.docx",
    output_path="/wilson-case/Documents/Wilson_LOR_StateFarm.docx",
    context={
        "client_name": "John Wilson",
        "client_address": "123 Main St, Louisville, KY 40202",
        "date_of_accident": "January 15, 2024",
        "insurance_company": "State Farm Insurance",
        "insurance_address": "P.O. Box 123, Bloomington, IL 61710",
        "claim_number": "CLM-2024-123456",
        "policy_number": "POL-987654",
        "insured_name": "Jane Doe",
        "date_today": "March 1, 2024"
    }
)
```

### Medical Records Request

```
fill_word_template(
    template_path="/forms/templates/Medical_Records_Request.docx",
    output_path="/wilson-case/Medical/Records_Request_Baptist.docx",
    context={
        "patient_name": "John Wilson",
        "patient_dob": "March 5, 1985",
        "patient_ssn_last4": "1234",
        "provider_name": "Baptist Health Louisville",
        "provider_address": "4000 Kresge Way, Louisville, KY 40207",
        "treatment_dates": "January 15, 2024 to Present",
        "records_requested": "All medical records, billing statements, and diagnostic imaging",
        "date_today": "March 1, 2024"
    }
)
```

### Batch Document Generation

For generating multiple documents (e.g., records requests to multiple providers):

```python
providers = [
    {"name": "Baptist Health", "address": "4000 Kresge Way..."},
    {"name": "Norton Healthcare", "address": "200 E Chestnut St..."},
    {"name": "UofL Physicians", "address": "530 S Jackson St..."},
]

for provider in providers:
    fill_word_template(
        template_path="/forms/templates/Medical_Records_Request.docx",
        output_path=f"/wilson-case/Medical/Records_Request_{provider['name'].replace(' ', '_')}.docx",
        context={
            "patient_name": "John Wilson",
            "provider_name": provider["name"],
            "provider_address": provider["address"],
            # ... other fields
        }
    )
```

## Relationship to Other Skills

- **DOCX Skill**: Use for creating new documents or editing with tracked changes
- **Template Filling**: Use for filling standardized templates
- **PDF Skill**: For working with PDF inputs; use `export_pdf_from_docx()` for outputs

## Dependencies

Requires:
- `docxtpl` (Python, installed with agent)
- `python-docx` (Python, installed with agent)
- LibreOffice (for PDF export only)

Check status with:
```
check_document_tools_status()
```
