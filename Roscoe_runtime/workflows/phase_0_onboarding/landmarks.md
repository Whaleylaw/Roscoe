# Phase 0: Onboarding - Landmarks

## Overview

Phase 0 has **3 mandatory landmarks** that must be achieved before proceeding to Phase 1. All three are document-based milestones representing signed intake documents.

---

## Landmark Summary

| # | Landmark ID | Name | Required Document | Mandatory |
|---|-------------|------|-------------------|:---------:|
| 1 | `client_info_received` | Client Info Received | New Client Information Sheet | **YES** |
| 2 | `contract_signed` | Contract Signed | Fee Agreement | **YES** |
| 3 | `medical_auth_signed` | Medical Auth Signed | HIPAA Authorization | **YES** |

**All 3 landmarks are required to exit Phase 0.**

---

## Landmark Details

### Landmark 1: Client Info Received

| Property | Value |
|----------|-------|
| **ID** | `client_info_received` |
| **Name** | Client Info Received |
| **Required Document** | New Client Information Sheet |
| **Template Location** | `/templates/2021 Whaley New Client Information Sheet (1).pdf` |
| **Storage Location** | `{case_folder}/Client/` |
| **Mandatory** | Yes |

**Verification:**
- File exists in `Client/` folder
- File name contains "Client Information" or "Intake"

**What This Document Contains:**
- Client full legal name
- Contact information (address, phone, email)
- Date of birth
- Social Security Number
- Emergency contact
- Basic accident information

---

### Landmark 2: Contract Signed

| Property | Value |
|----------|-------|
| **ID** | `contract_signed` |
| **Name** | Contract Signed |
| **Required Document** | Fee Agreement |
| **Mandatory** | Yes |

**Template by Case Type:**

| Case Type | Template Location |
|-----------|-------------------|
| MVA | `/templates/2021 Whaley MVA Fee Agreement (1).pdf` |
| S&F | `/templates/2021 Whaley S&F Fee Agreement (1).pdf` |
| WC | `/templates/2021 Whaley WC Fee Agreement - Final (1).pdf` |

**Storage Location:** `{case_folder}/Client/`

**Verification:**
- File exists in `Client/` folder
- File name contains "Fee Agreement" or "Contract" or "Retainer"

**What This Document Contains:**
- Contingency fee percentage
- Expense handling terms
- Scope of representation
- Client and attorney signatures

---

### Landmark 3: Medical Auth Signed

| Property | Value |
|----------|-------|
| **ID** | `medical_auth_signed` |
| **Name** | Medical Auth Signed |
| **Required Document** | Medical Authorization (HIPAA) |
| **Template Location** | `/templates/2021 Whaley Medical Authorization (HIPAA) (1).pdf` |
| **Storage Location** | `{case_folder}/Client/` |
| **Mandatory** | Yes |

**Verification:**
- File exists in `Client/` folder
- File name contains "Medical Authorization" or "HIPAA"

**What This Document Contains:**
- HIPAA-compliant authorization
- Client signature authorizing release of medical records
- Validity period

---

## Additional Documents (Not Landmarks)

These documents should be collected when applicable but are **not required** to proceed to Phase 1:

### Always Requested

| Document | Template | When |
|----------|----------|------|
| Medical Treatment Questionnaire | `2021 Whaley Medical Treatment Questionnaire (1).pdf` | All cases |
| Digital Signature Authorization | `2021 Whaley Authorization of Digitally Signature Replication (1).pdf` | All cases |

### Case Type Specific

| Document | Template | Case Types |
|----------|----------|------------|
| MVA Accident Detail Sheet | `2021 Whaley MVA Accident Detail Information Sheet (1).pdf` | MVA only |
| S&F Accident Detail Sheet | `2021 Whaley S&F Accident Detail Information Sheet (1).pdf` | S&F only |

### Conditional

| Document | Template | Condition |
|----------|----------|-----------|
| Wage & Salary Verification | `2021 Whaley Wage & Salary Verification (1).pdf` | If client is employed (MVA/S&F) or always (WC) |
| CMS Medicare Verification | `2021 Whaley CMS Medicare Verification Form (1).pdf` | If client is on or nearing Medicare eligibility |

---

## Landmark State in workflow_state.json

```json
{
  "phase": "onboarding",
  "landmarks": {
    "client_info_received": false,
    "contract_signed": false,
    "medical_auth_signed": false
  },
  "documents_received": [],
  "documents_pending": [
    "new_client_information_sheet",
    "fee_agreement",
    "medical_authorization",
    "medical_treatment_questionnaire",
    "digital_signature_authorization"
  ]
}
```

---

## Phase Completion Check

```
Phase 0 Complete?
├── client_info_received = true? 
│   └── NO → Blocker: "Missing New Client Information Sheet"
├── contract_signed = true?
│   └── NO → Blocker: "Missing signed Fee Agreement"
├── medical_auth_signed = true?
│   └── NO → Blocker: "Missing signed Medical Authorization"
└── ALL TRUE → Proceed to Phase 1: File Setup
```

---

## Blockers

If any landmark is not met, the system reports a blocker:

| Missing Landmark | Blocker Message | Resolution |
|------------------|-----------------|------------|
| Client Info | "Awaiting New Client Information Sheet" | Request from client or obtain from user |
| Contract | "Awaiting signed Fee Agreement" | Request from client or obtain from user |
| Medical Auth | "Awaiting signed Medical Authorization" | Request from client or obtain from user |

The agent will:
1. Report which documents are missing
2. Offer to request them from the client
3. Wait for user confirmation before proceeding
