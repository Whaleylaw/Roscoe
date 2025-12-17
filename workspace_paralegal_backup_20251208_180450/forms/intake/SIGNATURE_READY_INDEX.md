# Signature-Ready Document Templates

This index lists all document templates that have DocuSign signature anchors pre-embedded and are ready for electronic signature workflow.

## Quick Reference

| Document | Signers | Anchors | Phase |
|----------|---------|---------|-------|
| Retainer Agreement | Client, Spouse (opt) | `/sig1/`, `/sig2/`, `/date1/`, `/date2/` | Intake |
| HIPAA Authorization | Client | `/sig1/`, `/date1/` | Intake |
| Medicare Authorization | Client | `/sig1/`, `/date1/` | Intake |
| Authorization to Settle | Client, Spouse (opt) | `/sig1/`, `/sig2/`, `/date1/`, `/date2/` | Settlement |
| Property Damage Release | Client | `/sig1/`, `/date1/` | File Setup |

---

## Intake Documents

### 1. Retainer Agreement
**File:** `retainer_agreement_TEMPLATE.md`
**When to Use:** New client retention
**Signers:**
- `/sig1/` - Primary client signature
- `/sig2/` - Spouse signature (if married, for joint representation)
- `/date1/`, `/date2/` - Signature dates

**Placeholders:**
- `{{CLIENT_NAME}}`, `{{CLIENT_ADDRESS}}`, etc.
- `{{ACCIDENT_DATE}}`, `{{CASE_TYPE}}`
- `{{PRE_LIT_PERCENTAGE}}`, `{{LIT_PERCENTAGE}}`

---

### 2. HIPAA Authorization
**File:** `hipaa_authorization_TEMPLATE.md`
**When to Use:** Every case - required for medical records
**Signers:**
- `/sig1/` - Patient/client signature
- `/date1/` - Signature date

**Placeholders:**
- `{{CLIENT_NAME}}`, `{{CLIENT_DOB}}`
- `{{CLIENT_SSN_LAST4}}`
- `{{RECORDS_START_DATE}}`
- `{{ACCIDENT_DATE}}`

**Compliance:** HIPAA 45 CFR § 164.508

---

### 3. Medicare Authorization
**File:** `medicare_authorization_TEMPLATE.md`
**When to Use:** Clients age 65+ or on disability
**Signers:**
- `/sig1/` - Medicare beneficiary signature
- `/date1/` - Signature date

**Placeholders:**
- `{{CLIENT_NAME}}`, `{{CLIENT_MBI}}`
- `{{CLIENT_DOB}}`
- `{{ACCIDENT_DATE}}`

**Compliance:** Medicare Secondary Payer Act, 42 U.S.C. § 1395y(b)

---

## Settlement Documents

### 4. Authorization to Settle
**File:** `authorization_to_settle_TEMPLATE.md`
**When to Use:** Before finalizing settlement
**Signers:**
- `/sig1/` - Primary client signature
- `/sig2/` - Spouse signature (required if married)
- `/date1/`, `/date2/` - Signature dates

**Placeholders:**
- `{{CASE_NAME}}`, `{{FILE_NUMBER}}`
- Settlement amounts: `{{TOTAL_SETTLEMENT}}`, `{{NET_TO_CLIENT}}`
- `{{FEE_PERCENTAGE}}`, `{{ATTORNEY_FEE}}`
- Liens: `{{LIEN_1_NAME}}`, `{{LIEN_1_AMOUNT}}`

---

### 5. Property Damage Release
**File:** `property_damage_release_TEMPLATE.md`
**When to Use:** Settling PD claim separately from BI
**Signers:**
- `/sig1/` - Client signature
- `/date1/` - Signature date

**Placeholders:**
- `{{VEHICLE_YEAR}}`, `{{VEHICLE_MAKE}}`, `{{VEHICLE_MODEL}}`
- `{{PD_SETTLEMENT_AMOUNT}}`
- `{{PD_INSURER}}`, `{{PD_CLAIM_NUMBER}}`

---

## How to Use These Templates

### Agent Workflow

1. **Read the template:**
   ```
   read_file('/forms/intake/retainer_agreement_TEMPLATE.md')
   ```

2. **Fill placeholders:** Replace `{{PLACEHOLDER}}` with actual values

3. **Save as case document:**
   ```
   write_file('/case_name/documents/retainer_agreement.md', filled_content)
   ```

4. **Convert to PDF:** (if needed)
   ```
   python /Tools/document_processing/md_to_pdf.py /case/documents/retainer_agreement.md
   ```

5. **Send for signature:**
   ```
   python /Tools/esignature/docusign_send.py "/case/documents/retainer_agreement.pdf" \
     --signer-email "client@email.com" \
     --signer-name "John Smith" \
     --subject "Please sign: Retainer Agreement"
   ```

### Signature Anchor Rules

- First `--signer-email` maps to `/sig1/`
- Second `--signer-email` maps to `/sig2/`
- And so on...

### For Dual-Signer Documents

```bash
python /Tools/esignature/docusign_send.py "/case/settlement_auth.pdf" \
  --signer-email "client@email.com" --signer-name "John Smith" \
  --signer-email "spouse@email.com" --signer-name "Jane Smith" \
  --subject "Settlement Authorization - Please Sign"
```

---

## Templates NOT Needing Signatures

These documents are attorney-generated and don't require client signatures:

| Document | Location | Purpose |
|----------|----------|---------|
| Letter of Representation | `/forms/liens/LOR*.md` | Notify insurance/providers |
| Medical Records Request | `/forms/discovery/` | Request records from providers |
| Demand Letter | `/forms/demand_letter_TEMPLATE.md` | Settlement demand |
| Complaint | `/forms/complaints/` | File lawsuit |

---

## Future Templates Needed

These signature documents should be created:

- [ ] **Fee Agreement Addendum** - For fee changes or additional claims
- [ ] **Minor Settlement Authorization** - Court approval for minors
- [ ] **Structured Settlement Authorization** - For structured settlements
- [ ] **Mediation Authorization** - Pre-mediation authority
- [ ] **Appeal Authorization** - To authorize appeal
- [ ] **Withdrawal of Representation** - If client terminates

---

*Last updated: 2025-12-08*
*See `/Tools/esignature/SIGNATURE_PLACEMENT_GUIDE.md` for anchor tag details.*

