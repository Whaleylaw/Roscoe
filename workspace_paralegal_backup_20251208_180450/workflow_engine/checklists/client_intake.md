# Client Intake Checklist

## When to Use
Use this checklist when signing a new client. Ensures all required documents are sent for signature and case file is properly set up.

---

## Documents to Send via DocuSign

### Required Documents

- [ ] **Fee Agreement**
  - Template: `/forms/intake/whaley_mva_fee_agreement_TEMPLATE.md`
  - Contains: `/sig1/`, `/date1/` anchors
  ```bash
  python /Tools/esignature/docusign_send.py "/forms/intake/whaley_mva_fee_agreement_TEMPLATE.md" \
    --signer "{{CLIENT_NAME}}" --email "{{CLIENT_EMAIL}}" \
    --subject "Fee Agreement - {{CLIENT_NAME}}"
  ```

- [ ] **HIPAA Authorization**
  - Template: `/forms/intake/whaley_hipaa_authorization_TEMPLATE.md`
  - Contains: `/sig1/`, `/date1/` anchors
  ```bash
  python /Tools/esignature/docusign_send.py "/forms/intake/whaley_hipaa_authorization_TEMPLATE.md" \
    --signer "{{CLIENT_NAME}}" --email "{{CLIENT_EMAIL}}" \
    --subject "HIPAA Authorization - {{CLIENT_NAME}}"
  ```

### Case-Specific Documents

- [ ] **Employment Authorization** (if wage loss claim)
  - Template: `/forms/intake/whaley_employment_authorization_TEMPLATE.md`
  - Send if client missed work due to accident

---

## Track Signatures

```bash
# Check status of all pending envelopes
python /Tools/esignature/docusign_status.py --envelope-id {{ENVELOPE_ID}}
```

| Document | Envelope ID | Sent | Signed |
|----------|-------------|------|--------|
| Fee Agreement | | ☐ | ☐ |
| HIPAA Authorization | | ☐ | ☐ |
| Employment Auth | | ☐ | ☐ |

---

## Case File Setup

After documents are signed:

- [ ] **Create case folder structure**
  ```
  /{{case_name}}/
  ├── medical_records/
  ├── medical_bills/
  ├── litigation/
  │   ├── discovery/
  │   └── investigation/
  └── correspondence/
  ```

- [ ] **Initialize case state** (use template)
  - Template: `/workflow_engine/templates/new_case_state.json`

- [ ] **Add client information**
  - Full name
  - Date of birth
  - Address
  - Phone number(s)
  - Email
  - SSN (last 4 for HIPAA requests)

- [ ] **Add accident information**
  - Date of accident
  - Location
  - Type (MVA, premises, etc.)
  - Brief description

- [ ] **Calculate SOL deadline**
  - Kentucky PI SOL: 1 year from date of accident (KRS 304.39-230)
  - Add to calendar

---

## Follow-Up Schedule

| Day | Action |
|-----|--------|
| Day 0 | Send documents via DocuSign |
| Day 2 | If not signed, send reminder |
| Day 5 | If not signed, call client |
| Day 7 | If still not signed, escalate |

---

## After All Documents Signed

- [ ] Download signed documents to case folder
- [ ] Update case status to "File Setup"
- [ ] Proceed to accident report workflow
- [ ] Proceed to insurance claim opening workflow

---

## Templates Index

| Document | Template Path | DocuSign Ready |
|----------|---------------|----------------|
| Fee Agreement | `/forms/intake/whaley_mva_fee_agreement_TEMPLATE.md` | ✅ |
| HIPAA Authorization | `/forms/intake/whaley_hipaa_authorization_TEMPLATE.md` | ✅ |
| Employment Auth | `/forms/intake/whaley_employment_authorization_TEMPLATE.md` | ✅ |
| Auth to Settle | `/forms/intake/authorization_to_settle_TEMPLATE.md` | ✅ |
| PD Release | `/forms/intake/property_damage_release_TEMPLATE.md` | ✅ |

