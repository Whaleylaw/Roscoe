# Forms Index

Master index of all form templates available to the Roscoe paralegal agent.

**Total Forms: 298**

## Form Categories

### Intake Documents (9 templates)
DocuSign-ready templates with signature anchors.

| Template | Purpose | Anchors |
|----------|---------|---------|
| `intake/whaley_mva_fee_agreement_TEMPLATE.md` | MVA Fee Agreement (33%) | `/sig1/`, `/date1/` |
| `intake/whaley_hipaa_authorization_TEMPLATE.md` | HIPAA Authorization | `/sig1/`, `/date1/` |
| `intake/whaley_employment_authorization_TEMPLATE.md` | Employment Info Auth | `/sig1/`, `/date1/` |
| `intake/authorization_to_settle_TEMPLATE.md` | Authorization to Settle | `/sig1/`, `/date1/` |
| `intake/property_damage_release_TEMPLATE.md` | Property Damage Release | `/sig1/`, `/date1/` |
| `intake/retainer_agreement_TEMPLATE.md` | Generic Retainer | `/sig1/`, `/date1/` |
| `intake/hipaa_authorization_TEMPLATE.md` | Generic HIPAA | `/sig1/`, `/date1/` |
| `intake/medicare_authorization_TEMPLATE.md` | Medicare Auth | `/sig1/`, `/date1/` |

### Insurance Correspondence (5 templates)

| Template | Purpose |
|----------|---------|
| `insurance/BI/lor_to_bi_adjuster_TEMPLATE.md` | Letter of Rep to BI |
| `insurance/BI/request_dec_page_TEMPLATE.md` | Dec Page Request |
| `insurance/PIP/lor_to_pip_adjuster_TEMPLATE.md` | Letter of Rep to PIP |
| `insurance/PIP/request_pip_ledger_TEMPLATE.md` | PIP Ledger Request |
| `insurance/UIM/coots_letter_TEMPLATE.md` | COOTs Letter |

### Complaints (65 templates)
Litigation complaint templates for various case types.

| Category | Count | Examples |
|----------|-------|----------|
| Standard MVA | 15 | `BI Complaint.docx`, `Complaint-MVA (negligence only).docx` |
| UM/UIM | 8 | `Complaint - UIM.docx`, `Complaint with UM.docx` |
| Premises Liability | 10 | `Complaint - Premises Liability.docx`, `Dog Bite.docx` |
| Bad Faith | 5 | `Complaint - Negligence & Bad Faith.docx` |
| Vicarious Liability | 4 | `Complaint.MVA. Respondeat Superior.docx` |
| Service Documents | 15 | `CERTIFICATE OF SERVICE.docx`, `Affidavit for Special Bailiff.docx` |
| Notices | 8 | `Notice of Complaint to BI Adjuster.docx` |

### Discovery (113 templates)
Discovery requests, responses, and related documents.

| Category | Count | Examples |
|----------|-------|----------|
| Interrogatories | 20 | `2022 Whaley Discovery Request - MVA Standard.docx` |
| Requests for Production | 18 | `2022 Whaley Discovery Request - MVA Owner Reported Stolen.docx` |
| Requests for Admission | 12 | `RFAs Template.docx` |
| Deposition Notices | 25 | `2022 Whaley NTTD - Single Depo.docx` |
| Subpoenas | 15 | `Subpoena Duces Tecum Template.docx` |
| Expert Disclosures | 8 | `2022 Whaley Expert Disclosures.docx` |
| Discovery Motions | 15 | `Motion to Compel.docx` |

### Motions (55 templates)

| Category | Count | Examples |
|----------|-------|----------|
| Summary Judgment | 8 | `Motion for Summary Judgment.docx` |
| Dismissal | 6 | `Motion to Dismiss.docx` |
| Continuance | 5 | `Motion for Continuance.docx` |
| Protective Orders | 5 | `Motion for Protective Order.docx` |
| Compel | 8 | `Motion to Compel Discovery.docx` |
| Extensions | 6 | `Motion for Extension of Time.docx` |
| Misc Procedural | 17 | `Motion for Leave to Amend.docx` |

### Trial (19 templates)

| Category | Count | Examples |
|----------|-------|----------|
| Jury Instructions | 6 | `Proposed Jury Instructions.docx` |
| Witness Lists | 3 | `Witness List.docx` |
| Exhibit Lists | 3 | `Exhibit List.docx` |
| Pretrial Orders | 4 | `Pretrial Statement.docx` |
| Verdict Forms | 3 | `Verdict Form.docx` |

### Mediation (7 templates)

| Template | Purpose |
|----------|---------|
| `mediation/Mediation Statement.docx` | Full mediation brief |
| `mediation/Settlement Authority Letter.docx` | Client authority letter |
| `mediation/Mediation Summary.xlsx` | Case summary spreadsheet |

### Liens (21 templates)

| Category | Count | Examples |
|----------|-------|----------|
| Initial Requests | 8 | `initial_lien_request_TEMPLATE.md` |
| Final Requests | 6 | `final_lien_request_TEMPLATE.md` |
| Medicare/Medicaid | 4 | `Medicare Conditional Payment Letter.docx` |
| Workers Comp | 3 | `WC Lien Notice.docx` |

### Client Letters (2 templates)

| Template | Purpose |
|----------|---------|
| `client_letters/bi_offer_to_client_TEMPLATE.md` | Notify client of BI offer |
| `client_letters/declined_representation_TEMPLATE.md` | Decline representation |

### Medical Requests (1 template)

| Template | Purpose |
|----------|---------|
| `medical_requests/medical_records_request_TEMPLATE.md` | Medical records request |

### Appeals (1 template)

| Template | Purpose |
|----------|---------|
| `appeals/Notice_of_Appeal_Template.md` | Notice of Appeal |

### Demand Letters (2 templates)

| Template | Purpose |
|----------|---------|
| `demand_letter_TEMPLATE.md` | Standard demand template |
| `demand_letter_mills_example.md` | Example demand (Mills case) |

---

## Using Templates

### DocuSign-Ready Templates
Templates with `/sig1/`, `/date1/` anchors can be sent via DocuSign:

```bash
python /Tools/esignature/docusign_send.py \
  --document "/forms/intake/whaley_mva_fee_agreement_TEMPLATE.md" \
  --signer-email "client@example.com" \
  --signer-name "John Doe"
```

### DOCX Templates
Use the docx skill to populate templates:

```bash
# See /Skills/docx/SKILL.md for usage
```

### Template Placeholders
Most templates use these placeholder patterns:
- `{{CLIENT_NAME}}` - Client full name
- `{{DEFENDANT_NAME}}` - Defendant name
- `{{ACCIDENT_DATE}}` - Date of accident
- `{{CASE_NUMBER}}` - Court case number
- `{{ATTORNEY_NAME}}` - Attorney name

---

## Phase Mappings

| Phase | Relevant Forms |
|-------|----------------|
| File Setup | `intake/`, `insurance/` |
| Treatment | `medical_requests/`, `liens/initial*` |
| Demand | `demand_letter*`, `liens/final*` |
| Negotiation | `client_letters/` |
| Settlement | `intake/authorization_to_settle*` |
| Litigation | `complaints/`, `discovery/`, `motions/`, `trial/` |

---

*Last Updated: December 8, 2025*
