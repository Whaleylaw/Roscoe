# DocuSign Envelope Tracking

## Envelope States

| Status | Meaning |
|--------|---------|
| `created` | Envelope created but not sent |
| `sent` | Sent to signer(s), awaiting action |
| `delivered` | Delivered to signer's inbox |
| `signed` | Signer completed signing |
| `completed` | All signers done, processing complete |
| `declined` | Signer declined to sign |
| `voided` | Envelope cancelled |

## Tracking in Case File

Store envelope info in `workflow_state.json`:

```json
{
  "docusign_envelopes": [
    {
      "document": "Fee Agreement",
      "envelope_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "sent_date": "2024-12-06T10:30:00",
      "signer_email": "client@email.com",
      "status": "sent",
      "follow_up_date": "2024-12-09T10:30:00"
    }
  ]
}
```

## Follow-Up Schedule

| Day | Action |
|-----|--------|
| 0 | Document sent |
| 3 | First follow-up (if not signed) |
| 7 | Second follow-up |
| 14 | Escalation / resend |

## Follow-Up Message

When follow-up date arrives:

```
📋 DOCUSIGN FOLLOW-UP DUE

Document: Fee Agreement
Sent: December 6, 2024 (3 days ago)
Envelope ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Signer: John Smith (client@email.com)
Status: Sent (not yet signed)

Options:
A) Send reminder via DocuSign
B) Contact client directly
C) Resend with new envelope
D) Extend follow-up 3 more days
E) Mark as signed (if completed)
```

## When Document is Signed

1. DocuSign sends notification (webhook or email)
2. Download signed document
3. Save to case folder
4. Update landmark status

```python
# Update tracking
workflow_state["docusign_envelopes"][0]["status"] = "completed"
workflow_state["docusign_envelopes"][0]["completed_date"] = "2024-12-07T14:22:00"
workflow_state["docusign_envelopes"][0]["signed_document_path"] = "Client/Fee Agreement - SIGNED.pdf"

# Update landmark (for Fee Agreement)
workflow_state["landmarks"]["contract_signed"] = True
```

## Checking Envelope Status

```python
# If status check needed
from docusign_config import get_config
from docusign_esign import EnvelopesApi

config = get_config(use_production=True)
api_client = config.get_api_client()
envelopes_api = EnvelopesApi(api_client)

envelope = envelopes_api.get_envelope(
    account_id=config.account_id,
    envelope_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
)

print(f"Status: {envelope.status}")
```

## Downloading Signed Document

```python
# Get completed document
documents = envelopes_api.list_documents(
    account_id=config.account_id,
    envelope_id=envelope_id
)

# Download
document_bytes = envelopes_api.get_document(
    account_id=config.account_id,
    envelope_id=envelope_id,
    document_id="1"
)

# Save
with open(f"{case_folder}/Client/Fee Agreement - SIGNED.pdf", "wb") as f:
    f.write(document_bytes)
```

## User Notification on Completion

```
✅ DOCUMENT SIGNED

Document: Fee Agreement
Signed by: John Smith
Date: December 7, 2024 at 2:22 PM

Signed document saved to:
Client/Fee Agreement - SIGNED.pdf

✓ Landmark updated: Contract Signed = TRUE
```

