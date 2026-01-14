# Document Templates

This directory contains sample YAML metadata files for document templates. To use these templates with the agent:

## Deployment

1. **Copy to workspace:** Upload YAML files and corresponding DOCX templates to `/mnt/workspace/Templates/` on the VM:
   ```bash
   # From VM
   mkdir -p /mnt/workspace/Templates
   cp /path/to/templates/*.yaml /mnt/workspace/Templates/
   cp /path/to/templates/*.docx /mnt/workspace/Templates/
   ```

2. **Create DOCX templates:** Each YAML file needs a corresponding `.docx` file with the same base name. The DOCX file contains placeholder fields in `{{field_name}}` format.

## Creating DOCX Templates

1. Open Microsoft Word or LibreOffice Writer
2. Design your letter/document layout
3. Insert placeholders where dynamic content should go:
   - Use `{{field_name}}` syntax exactly (double curly braces)
   - Field names must match those defined in the YAML `fields` section
4. Save as `.docx` with the same name as the YAML file

### Example: medical_records_request.docx

```
{{firm_name}}
{{firm_address}}
{{firm_phone}}

{{today_date}}

{{provider_name}}
{{provider_address}}

RE: Medical Records Request
    Patient: {{client_name}}
    DOB: {{client_dob}}
    SSN (Last 4): {{client_ssn_last4}}
    Date of Injury: {{date_of_injury}}

Dear Medical Records Department:

Please be advised that this firm represents {{client_name}} regarding
injuries sustained on {{date_of_injury}}. Enclosed please find a signed
HIPAA authorization...

[Rest of letter content]

Sincerely,

{{firm_name}}
```

## Template Types

### Graph Mode (`input_mode: "graph"`)
- Agent provides `case_name` and key identifiers (like `provider_name`)
- Other fields (client info, dates) are automatically pulled from the knowledge graph
- Best for standard correspondence tied to existing cases

### Direct Mode (`input_mode: "direct"`)
- Agent must provide all required fields explicitly
- Best for one-off letters or when case data isn't in the graph

## Field Sources

| Source | Description |
|--------|-------------|
| `graph_query` | Cypher query to fetch value from knowledge graph |
| `input` | Value provided directly by agent via `inputs` parameter |
| `config` | Value from `/Database/firm_settings.json` |
| `computed` | Auto-generated value (e.g., `today_date`) |

## Usage Examples

### From the Agent

```python
# Graph-integrated template
create_document_from_template(
    template_id="med-records-request-v1",
    case_name="Wilson-MVA-2024",
    inputs={"provider_name": "Baptist Health Louisville"}
)

# Direct input template
create_document_from_template(
    template_id="simple-letter-v1",
    inputs={
        "recipient_name": "John Smith",
        "recipient_address": "123 Main St, Louisville, KY 40202",
        "subject": "Case Update",
        "body": "Thank you for your patience..."
    }
)
```

## Available Templates

| ID | Name | Mode | Description |
|----|------|------|-------------|
| `med-records-request-v1` | Medical Records Request | graph | HIPAA request for medical records |
| `letter-of-rep-v1` | Letter of Representation | graph | Notice of legal representation |
| `simple-letter-v1` | Simple Letter | direct | Generic letter template |
