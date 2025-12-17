# Release Processing Checklist

## When to Use
Use this checklist when a release document arrives (typically via email from insurance company or defense counsel) and needs to be sent to the client for signature.

---

## Pre-Send Checklist

- [ ] **Verify case is ready for settlement**
  - Settlement amount confirmed
  - Client has approved settlement
  - All liens identified and accounted for

- [ ] **Review release document**
  - Correct client name
  - Correct settlement amount
  - No unusual terms or conditions
  - Release type matches case (BI only, PD only, full release, etc.)

- [ ] **Prepare client communication**
  - Draft email explaining what client is signing
  - Include settlement statement if not already sent

---

## Send via DocuSign

```bash
# Send release to client for signature
python /Tools/esignature/docusign_send.py "/path/to/release.pdf" \
  --signer "{{CLIENT_NAME}}" \
  --email "{{CLIENT_EMAIL}}" \
  --subject "Release for Signature - {{CASE_NAME}}"
```

- [ ] **DocuSign envelope created**
- [ ] **Envelope ID recorded**: `________________`

---

## Post-Send Tracking

```bash
# Check signature status
python /Tools/esignature/docusign_status.py --envelope-id {{ENVELOPE_ID}}
```

- [ ] **Client notified** (email/call about DocuSign)
- [ ] **Follow-up scheduled** (if not signed within 48 hours)
- [ ] **Signature completed**
- [ ] **Signed release downloaded to case folder**

---

## After Signature

- [ ] **Return signed release to insurance/defense counsel**
- [ ] **Request settlement check**
- [ ] **Update case status to "Settlement Processing"**

---

## Common Release Types

| Type | Description |
|------|-------------|
| **Full Release** | Releases all claims against all parties |
| **BI-Only Release** | Releases bodily injury claim only |
| **PD-Only Release** | Releases property damage claim only |
| **Limited Release** | Releases specific defendant only |
| **Covenant Not to Sue** | Preserves claims against other parties |

---

## Notes

- Most releases come pre-formatted from insurance companies
- DocuSign can place signatures on PDFs at specified coordinates
- Always verify settlement amount matches before sending
- Keep copy of unsigned release in case file

