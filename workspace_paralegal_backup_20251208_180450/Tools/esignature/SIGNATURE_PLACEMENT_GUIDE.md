# DocuSign Signature Placement Guide

This guide explains how to prepare documents and templates for electronic signature via DocuSign.

## Quick Reference

| Anchor Tag | Purpose | Example Placement |
|------------|---------|-------------------|
| `/sig1/` | Primary signer signature | Above signature line |
| `/sig2/` | Second signer signature | Spouse, co-plaintiff |
| `/date1/` | Auto-populated date for signer 1 | Next to signature |
| `/date2/` | Auto-populated date for signer 2 | Next to second signature |
| `/init1/` | Initials for signer 1 | Page footers, clause acknowledgments |
| `/init2/` | Initials for signer 2 | Page footers |
| `/text1/` | Text input field for signer 1 | Address, additional info |

## How Anchor Tags Work

DocuSign uses "anchor strings" (also called "anchor tabs") to automatically position signature fields. When the document is sent:

1. DocuSign scans the document for anchor strings
2. Places the appropriate field at each anchor location
3. The anchor text itself becomes invisible to the signer
4. Signer sees only the signature/date/initial field

## Placing Anchors in Templates

### Method 1: Visible Anchor Text (Recommended)

Place the anchor tag directly in your document where you want the field:

```markdown
Client Signature: /sig1/

Date: /date1/
```

The `/sig1/` text will be replaced with a signature field.

### Method 2: White Text (Hidden Anchors)

For cleaner templates, use white text on white background:
- In Word: Type `/sig1/`, select it, change font color to white
- The anchor is invisible but DocuSign still finds it

### Method 3: Comment/Placeholder Style

Use a format that's clearly a placeholder:

```markdown
Client Signature: [SIGNATURE_HERE:/sig1/]

Date: [DATE_HERE:/date1/]
```

## Standard Template Sections

### Single Signer (Most Common)

```markdown
## Signature

By signing below, I acknowledge that I have read and agree to the terms above.


_________________________________
Client Signature: /sig1/

Date: /date1/

Print Name: /text1/
```

### Dual Signers (Married Clients, Co-Plaintiffs)

```markdown
## Signatures

By signing below, we acknowledge that we have read and agree to the terms above.


_________________________________        _________________________________
Client Signature: /sig1/                 Spouse Signature: /sig2/

Date: /date1/                            Date: /date2/

Print Name: /text1/                      Print Name: /text2/
```

### Attorney Counter-Signature

```markdown
## Client Signature

_________________________________
Client: /sig1/
Date: /date1/


## Attorney Signature

_________________________________
Aaron Whaley, Attorney at Law
Whaley Law Office, PLLC
```

Note: Attorney signature is NOT an anchor - attorney signs separately or document is pre-signed.

## Template-Specific Conventions

### Retainer Agreement
```
Anchors needed:
- /sig1/ - Client signature (required)
- /sig2/ - Spouse signature (if applicable)
- /date1/, /date2/ - Signature dates
- /init1/ - Initial each page (optional)
```

### HIPAA Authorization
```
Anchors needed:
- /sig1/ - Patient/client signature
- /date1/ - Signature date
```

### Medicare Secondary Payer Authorization
```
Anchors needed:
- /sig1/ - Medicare beneficiary signature
- /date1/ - Signature date
```

### Settlement Authorization
```
Anchors needed:
- /sig1/ - Client signature
- /sig2/ - Spouse signature (if married, community property)
- /date1/, /date2/ - Signature dates
```

### Lien Letter of Representation
```
No client signature needed - attorney letter only.
```

## Positioning Tips

### Offset from Anchor

The signature field appears slightly below and to the right of the anchor. For precise positioning:

```markdown
Signature: /sig1/
           ↑
           Field appears here, overlapping the anchor
```

### Vertical Spacing

Leave enough vertical space below the anchor for the signature graphic:

```markdown
Signature: /sig1/


_________________________________
(signature line for visual reference)
```

### Multiple Fields on Same Line

```markdown
Signature: /sig1/                    Date: /date1/
```

## Anchor Tag Reference

### Signature Fields
| Tag | Description |
|-----|-------------|
| `/sig1/` through `/sig9/` | Signature for signer 1-9 |
| `/sigopt1/` | Optional signature (not required) |

### Date Fields
| Tag | Description |
|-----|-------------|
| `/date1/` through `/date9/` | Date signed (auto-populated) |
| `/dateopt1/` | Optional date field |

### Initial Fields
| Tag | Description |
|-----|-------------|
| `/init1/` through `/init9/` | Initials for signer 1-9 |
| `/initopt1/` | Optional initials |

### Text/Input Fields
| Tag | Description |
|-----|-------------|
| `/text1/` through `/text9/` | Text input for signer 1-9 |
| `/textopt1/` | Optional text input |

### Checkbox Fields
| Tag | Description |
|-----|-------------|
| `/check1/` | Checkbox for signer 1 |
| `/checkopt1/` | Optional checkbox |

## Workflow Integration

### When Creating New Templates

1. Use the standard anchors from this guide
2. Place `/sig1/` where client should sign
3. Add `/date1/` next to signature
4. For dual-signer docs, add `/sig2/` and `/date2/`

### When Generating Documents from Templates

1. Replace placeholders with actual client data
2. Keep anchor tags intact (don't replace them)
3. Save as PDF before sending to DocuSign

### When Sending via docusign_send.py

```bash
# Single signer
python /Tools/esignature/docusign_send.py "/path/to/doc.pdf" \
  -e "client@email.com" -n "John Smith"

# Multiple signers (order matches /sig1/, /sig2/)
python /Tools/esignature/docusign_send.py "/path/to/doc.pdf" \
  -e "client@email.com" -n "John Smith" \
  -e "spouse@email.com" -n "Jane Smith"
```

The first `-e`/`-n` pair corresponds to `/sig1/`, the second to `/sig2/`, etc.

## Common Issues

### Anchor Not Found

If DocuSign can't find the anchor:
- Check for typos (`/sig1/` not `/Sig1/` or `/sig 1/`)
- Ensure anchor isn't split across lines
- For PDFs, ensure text is selectable (not image-only)

### Signature in Wrong Position

- Adjust anchor placement in template
- Use the tool's `--anchor` flag for custom anchor strings

### Multiple Signatures Needed on Same Document

Use sequential anchor numbers:
- First signer: `/sig1/`, `/date1/`, `/init1/`
- Second signer: `/sig2/`, `/date2/`, `/init2/`
- Third signer: `/sig3/`, `/date3/`, `/init3/`

## Example: Complete Retainer Template

```markdown
# LEGAL SERVICES AGREEMENT

**Client:** {{CLIENT_NAME}}
**Attorney:** Aaron Whaley, Whaley Law Office, PLLC
**Date:** {{DATE}}
**Matter:** {{CASE_DESCRIPTION}}

[... agreement terms ...]

## SIGNATURES

By signing below, Client agrees to the terms of this Legal Services Agreement.

**CLIENT:**

/sig1/

_________________________________
{{CLIENT_NAME}}
Date: /date1/

**SPOUSE (if applicable):**

/sig2/

_________________________________
{{SPOUSE_NAME}}
Date: /date2/
```

---

*This guide is referenced by `/Tools/esignature/manifest.json` and should be read when creating or modifying signature templates.*

