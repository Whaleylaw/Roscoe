# Multiple Signers with DocuSign

## When Multiple Signers Are Needed

Common scenarios:
- Married couples signing jointly
- Parent/guardian signing for minor
- Multiple parties to an agreement

## Sending to Multiple Signers

```python
from docusign_send import send_document

result = send_document(
    document_path="/path/to/joint_agreement.pdf",
    signer_emails=["client@email.com", "spouse@email.com"],
    signer_names=["John Smith", "Jane Smith"],
    subject="Whaley Law Firm - Please Sign: Agreement",
    anchor_string="/sig1/"  # Second signer uses /sig2/
)
```

## Routing Order

By default, signers sign in order (sequential routing):
1. First signer receives email
2. After first signs, second signer receives email
3. Process continues until all sign

For parallel signing (all at once), configure in envelope definition.

## Anchor Placement for Multiple Signers

Document should have anchors for each signer:

| Signer | Anchor | Tab Created |
|--------|--------|-------------|
| Signer 1 | `/sig1/` | Sign here tab at anchor |
| Signer 2 | `/sig2/` | Sign here tab at anchor |
| Signer 3 | `/sig3/` | Sign here tab at anchor |

## Code Example for Multiple Signers

```python
# Creating signers with proper routing
signers = []
for i, (email, name) in enumerate(zip(signer_emails, signer_names), start=1):
    # Anchor for this signer
    sign_here = SignHere(
        anchor_string=f"/sig{i}/",
        anchor_units="pixels",
        anchor_y_offset="10",
        anchor_x_offset="20"
    )
    
    signer = Signer(
        email=email,
        name=name,
        recipient_id=str(i),
        routing_order=str(i),  # Sequential signing
        tabs=Tabs(sign_here_tabs=[sign_here])
    )
    signers.append(signer)
```

## Status Tracking for Multiple Signers

```json
{
  "docusign_envelopes": [
    {
      "document": "Joint Fee Agreement",
      "envelope_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "sent_date": "2024-12-06",
      "signers": [
        {
          "name": "John Smith",
          "email": "client@email.com",
          "status": "completed",
          "signed_date": "2024-12-06T14:00:00"
        },
        {
          "name": "Jane Smith",
          "email": "spouse@email.com",
          "status": "sent",
          "signed_date": null
        }
      ],
      "overall_status": "sent"
    }
  ]
}
```

## User Output for Multiple Signers

```
✅ DOCUMENT SENT FOR SIGNATURES

Document: Joint Fee Agreement
Envelope ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Signers (in order):
1. John Smith (client@email.com) - Will receive first
2. Jane Smith (spouse@email.com) - Will receive after John signs

Signing order: Sequential
Total signers: 2

First signer will receive email from DocuSign now.
Second signer will receive email after first completes.
```

## Completion Notification

```
✅ ALL SIGNATURES COMPLETE

Document: Joint Fee Agreement
Completed: December 7, 2024

Signatures:
✓ John Smith - Signed Dec 6, 2024 at 2:00 PM
✓ Jane Smith - Signed Dec 7, 2024 at 9:30 AM

Signed document saved to:
Client/Joint Fee Agreement - SIGNED.pdf
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Second signer never receives | First hasn't signed | Follow up with first signer |
| Wrong signing order | Routing order incorrect | Verify routing_order values |
| Duplicate signatures | Same anchor for both | Use /sig1/ and /sig2/ |
| One signer declines | Signer refused | Envelope voided, resend |

