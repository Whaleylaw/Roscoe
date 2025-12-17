# DocuSign Send Tool Usage

## docusign_send.py

**Location**: `tools/docusign_send.py`
**Config**: `tools/docusign_config.py`

## Requirements

- `docusign-esign` Python package installed
- DocuSign API credentials configured
- Account in demo (sandbox) or production mode

## Basic Usage

```python
from docusign_send import send_document

result = send_document(
    document_path="/path/to/document.pdf",
    signer_emails=["client@email.com"],
    signer_names=["John Smith"],
    subject="Please Sign: Document Name",
    message="Please review and sign at your earliest convenience.",
    anchor_string="/sig1/",
    use_production=True  # False for sandbox testing
)
```

## Function Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|:--------:|---------|-------------|
| `document_path` | str | Yes | - | Path to PDF or DOCX |
| `signer_emails` | list | Yes | - | List of signer email addresses |
| `signer_names` | list | Yes | - | List of signer names (same order) |
| `subject` | str | No | "Please sign this document" | Email subject |
| `message` | str | No | Generic message | Email body |
| `anchor_string` | str | No | "/sig1/" | Signature placement anchor |
| `use_production` | bool | No | False | Production vs sandbox |

## Return Value

### Success

```python
{
    "success": True,
    "envelope_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "status": "sent",
    "status_date_time": "2024-12-06T10:30:00Z",
    "uri": "/envelopes/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "document": "fee_agreement.pdf",
    "signers": [{"email": "client@email.com", "name": "John Smith"}],
    "subject": "Please Sign: Fee Agreement",
    "sent_at": "2024-12-06T10:30:00",
    "environment": "production"
}
```

### Error

```python
{
    "success": False,
    "error": "DocuSign API error: Invalid email address"
}
```

## Complete Example

```python
import json
from pathlib import Path
from datetime import datetime
from docusign_send import send_document

def send_fee_agreement(case_folder: str, client_email: str, client_name: str) -> dict:
    """Send Fee Agreement for electronic signature."""
    
    case_path = Path(case_folder)
    
    # Determine correct fee agreement based on case type
    with open(case_path / "Case Information/overview.json") as f:
        overview = json.load(f)
    
    case_type = overview.get("case_type", "MVA")
    fee_agreements = {
        "MVA": "2021 Whaley MVA Fee Agreement.pdf",
        "SF": "2021 Whaley S&F Fee Agreement.pdf",
        "WC": "2021 Whaley WC Fee Agreement - Final.pdf"
    }
    
    document_name = fee_agreements.get(case_type, fee_agreements["MVA"])
    document_path = case_path / "Client" / document_name
    
    # Send via DocuSign
    result = send_document(
        document_path=str(document_path),
        signer_emails=[client_email],
        signer_names=[client_name],
        subject=f"Whaley Law Firm - Please Sign: Fee Agreement",
        message=f"Dear {client_name},\n\nPlease review and sign the attached Fee Agreement.\n\nThank you,\nWhaley Law Firm",
        anchor_string="/sig1/",
        use_production=True
    )
    
    # Track in workflow_state
    if result["success"]:
        workflow_state_path = case_path / "Case Information/workflow_state.json"
        with open(workflow_state_path) as f:
            workflow_state = json.load(f)
        
        if "docusign_envelopes" not in workflow_state:
            workflow_state["docusign_envelopes"] = []
        
        workflow_state["docusign_envelopes"].append({
            "document": "Fee Agreement",
            "envelope_id": result["envelope_id"],
            "sent_date": datetime.now().isoformat(),
            "status": "sent",
            "follow_up_date": (datetime.now() + timedelta(days=3)).isoformat()
        })
        
        with open(workflow_state_path, "w") as f:
            json.dump(workflow_state, f, indent=2)
    
    return result
```

## Command Line Usage

```bash
python docusign_send.py "/path/to/document.pdf" \
    --signer-email "client@email.com" \
    --signer-name "John Smith" \
    --subject "Please Sign: Fee Agreement" \
    --production \
    --pretty
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| "DocuSign SDK not installed" | Missing package | `pip install docusign-esign` |
| "Document not found" | Invalid path | Verify document exists |
| "Invalid email address" | Bad email format | Get correct email |
| "Authentication failed" | Bad credentials | Check DocuSign config |
| "Anchor string not found" | Missing /sig1/ | Use fixed position fallback |

