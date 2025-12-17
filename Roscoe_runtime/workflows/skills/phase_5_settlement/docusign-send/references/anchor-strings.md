# DocuSign Anchor Strings

## What Are Anchor Strings?

Anchor strings are text markers in documents that tell DocuSign where to place signature fields. When DocuSign processes the document, it searches for these text strings and places the signature field at that location.

## Standard Anchors

| Anchor | Purpose | Typical Location |
|--------|---------|------------------|
| `/sig1/` | First signer signature | Last page, signature line |
| `/sig2/` | Second signer signature | For co-signers |
| `/date1/` | Date field for signer 1 | Next to signature |
| `/init1/` | Initials for signer 1 | Page footers or acknowledgments |

## How Anchors Work

1. Document contains text `/sig1/` (often white text on white background)
2. DocuSign scans document for this text
3. Signature field is placed at anchor location
4. Anchor text is hidden in final document

## Whaley Law Templates

| Template | Anchor Present | Location |
|----------|:--------------:|----------|
| MVA Fee Agreement | Yes `/sig1/` | Last page signature line |
| S&F Fee Agreement | Yes `/sig1/` | Last page signature line |
| WC Fee Agreement | Yes `/sig1/` | Last page signature line |
| HIPAA Authorization | Yes `/sig1/` | Signature block |
| Digital Signature Auth | Yes `/sig1/` | Bottom of form |

## When No Anchor Exists

If document doesn't have an anchor string, DocuSign uses fixed position:

```python
# Fallback to fixed position
sign_here_fixed = SignHere(
    document_id="1",
    page_number="1",      # Last page recommended
    x_position="100",     # Pixels from left
    y_position="700"      # Pixels from top
)
```

## Adding Anchors to Documents

To add anchor to a Word document:

1. Open document in Word
2. Position cursor at signature location
3. Type `/sig1/`
4. Select the text
5. Change font color to white (if on white background)
6. Save and convert to PDF

## Multiple Signers

For documents requiring multiple signatures:

```python
# First signer uses /sig1/
# Second signer automatically looks for /sig2/
result = send_document(
    document_path="joint_agreement.pdf",
    signer_emails=["client@email.com", "spouse@email.com"],
    signer_names=["John Smith", "Jane Smith"],
    anchor_string="/sig1/"  # /sig2/ used for second signer
)
```

## Anchor Offset

Fine-tune signature position relative to anchor:

```python
sign_here = SignHere(
    anchor_string="/sig1/",
    anchor_units="pixels",
    anchor_y_offset="10",   # Move 10 pixels down
    anchor_x_offset="20"    # Move 20 pixels right
)
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Signature in wrong place | Wrong anchor position | Adjust anchor in document |
| Signature not appearing | Anchor not found | Check spelling, use fallback |
| Anchor visible in signed doc | Font color not white | Change anchor color |
| Multiple signatures overlapping | Same anchor for both | Use /sig1/ and /sig2/ |

