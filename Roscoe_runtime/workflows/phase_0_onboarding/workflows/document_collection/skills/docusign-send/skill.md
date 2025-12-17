---
name: docusign-send
description: >
  Electronic signature toolkit for sending documents via DocuSign. Sends PDF documents
  to clients for signature with configurable anchor string placement. Supports single
  or multiple signers and returns envelope ID for tracking. When Claude needs to send
  a Fee Agreement, HIPAA authorization, or other document for electronic signature,
  collect client signatures remotely, or track pending signatures. Use for Phase 0
  intake documents requiring signature, contract execution, or any document requiring
  authenticated e-signature. Not for documents that don't require signature, when
  client prefers wet signature, or when DocuSign is not configured.
---

# DocuSign Send Skill

Send documents to clients for electronic signature via DocuSign.

## Capabilities

- Send PDF/DOCX documents for e-signature
- Support single or multiple signers
- Configure signature anchor placement
- Track envelope status
- Return envelope ID for follow-up

**Keywords**: DocuSign, electronic signature, e-signature, esign, contract signing, HIPAA signature, Fee Agreement signing, remote signing, digital signature

## Phase 0 Documents

| Document | Anchor | Priority |
|----------|--------|----------|
| Fee Agreement | `/sig1/` | **Required** |
| Medical Authorization (HIPAA) | `/sig1/` | **Required** |
| Digital Signature Auth | `/sig1/` | Recommended |

## Workflow

```
1. PREPARE DOCUMENT
   └── Must be PDF or DOCX
   └── Anchor string in place (e.g., /sig1/)

2. VERIFY SIGNER
   └── Client email address (required)
   └── Client legal name

3. COMPOSE MESSAGE
   └── Subject line
   └── Email body message

4. SEND VIA DOCUSIGN
   └── Tool: docusign_send.py

5. TRACK ENVELOPE
   └── Record envelope_id
   └── Schedule 3-day follow-up

6. PROCESS COMPLETION
   └── Download signed document
   └── Update landmark
```

## Tool

**Primary**: `tools/docusign_send.py`

```python
from docusign_send import send_document

result = send_document(
    document_path="/path/to/fee_agreement.pdf",
    signer_emails=["client@email.com"],
    signer_names=["John Smith"],
    subject="Whaley Law Firm - Please Sign: Fee Agreement",
    anchor_string="/sig1/"
)
```

## Output Patterns

**Success**:
```
✅ DOCUMENT SENT FOR SIGNATURE

Document: Fee Agreement
Sent to: John Smith (client@email.com)
Envelope ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Client will receive email from DocuSign with signing instructions.
Follow-up scheduled: [3 days]
```

**Error**:
```
⚠️ FAILED TO SEND DOCUMENT

Error: [error message]
Please verify client email and try again.
```

## References

For detailed guidance, see:
- **Tool usage** → `references/tool-usage.md`
- **Anchor strings** → `references/anchor-strings.md`
- **Tracking envelopes** → `references/tracking.md`
- **Multiple signers** → `references/multiple-signers.md`

## Output

- Document sent via DocuSign
- Envelope ID for tracking
- Follow-up scheduled (3 days)
- Landmark updated when signed
