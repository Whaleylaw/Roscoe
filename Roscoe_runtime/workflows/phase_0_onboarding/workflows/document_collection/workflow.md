---
name: document_collection
description: >
  Collects required intake documents from personal injury clients based on case type
  (MVA, S&F, WC). Tracks document status, updates landmarks, and determines Phase 0
  completion. Uses fillable PDF templates from templates/intake_forms/. Supports
  DocuSign for electronic signatures on Fee Agreement, HIPAA, and other documents.
  Follows case_setup workflow automatically after new case creation.
phase: onboarding
workflow_id: document_collection
related_skills:
  - document-request
  - document-intake
  - docusign-send
related_tools:
  - docusign_send.py
templates:
  - templates/document-checklist.md
  - templates/request-email.md
  - templates/intake_forms/  # Contains all fillable PDF templates
---

# Document Collection Workflow

## Purpose

Gather all required intake documents from the client to complete Phase 0. This workflow:
1. Determines which documents are needed based on case type
2. Provides fillable PDF templates for each document
3. Tracks document receipt status
4. Provides options to request, receive, or skip documents
5. Updates landmarks when signature documents are received
6. Validates when Phase 0 is complete

---

## Trigger

This workflow runs automatically after `case_setup` completes. It can also be triggered:
- When user mentions documents for a case in Phase 0
- When checking status of intake documents
- When case is loaded and `document_collection` is `in_progress`

---

## Template Files

All fillable PDF templates are located in `templates/intake_forms/`:

### Landmark Documents (Required to Exit Phase 0)

| Document | Template File | Case Types |
|----------|---------------|------------|
| New Client Information Sheet | `2021 Whaley New Client Information Sheet (1).pdf` | All |
| MVA Fee Agreement | `2021 Whaley MVA Fee Agreement (1).pdf` | MVA |
| S&F Fee Agreement | `2021 Whaley S&F Fee Agreement (1).pdf` | S&F |
| WC Fee Agreement | `2021 Whaley WC Fee Agreement - Final (1).pdf` | WC |
| Medical Authorization (HIPAA) | `2021 Whaley Medical Authorization (HIPAA) (1).pdf` | All |

### Additional Documents

| Document | Template File | Case Types |
|----------|---------------|------------|
| Medical Treatment Questionnaire | `2021 Whaley Medical Treatment Questionnaire (1).pdf` | All |
| Digital Signature Authorization | `2021 Whaley Authorization of Digitally Signature Replication (1).pdf` | All |
| MVA Accident Detail Sheet | `2021 Whaley MVA Accident Detail Information Sheet (1).pdf` | MVA |
| S&F Accident Detail Sheet | `2021 Whaley S&F Accident Detail Information Sheet (1).pdf` | S&F |

### Conditional Documents

| Document | Template File | Condition |
|----------|---------------|-----------|
| Wage & Salary Verification | `2021 Whaley Wage & Salary Verification (1).pdf` | If employed (MVA/S&F) or always (WC) |
| CMS Medicare Verification | `2021 Whaley CMS Medicare Verification Form (1).pdf` | If Medicare/65+ |

---

## Document Requirements by Case Type

### MVA (Motor Vehicle Accident)

**Landmark Documents (Required):**
- `2021 Whaley New Client Information Sheet (1).pdf`
- `2021 Whaley MVA Fee Agreement (1).pdf`
- `2021 Whaley Medical Authorization (HIPAA) (1).pdf`

**Additional:**
- `2021 Whaley Medical Treatment Questionnaire (1).pdf`
- `2021 Whaley Authorization of Digitally Signature Replication (1).pdf`
- `2021 Whaley MVA Accident Detail Information Sheet (1).pdf`

**Conditional:**
- `2021 Whaley Wage & Salary Verification (1).pdf` (if employed)
- `2021 Whaley CMS Medicare Verification Form (1).pdf` (if Medicare)

### S&F (Slip and Fall)

**Landmark Documents (Required):**
- `2021 Whaley New Client Information Sheet (1).pdf`
- `2021 Whaley S&F Fee Agreement (1).pdf`
- `2021 Whaley Medical Authorization (HIPAA) (1).pdf`

**Additional:**
- `2021 Whaley Medical Treatment Questionnaire (1).pdf`
- `2021 Whaley Authorization of Digitally Signature Replication (1).pdf`
- `2021 Whaley S&F Accident Detail Information Sheet (1).pdf`

**Conditional:**
- `2021 Whaley Wage & Salary Verification (1).pdf` (if employed)
- `2021 Whaley CMS Medicare Verification Form (1).pdf` (if Medicare)

### WC (Workers' Compensation)

**Landmark Documents (Required):**
- `2021 Whaley New Client Information Sheet (1).pdf`
- `2021 Whaley WC Fee Agreement - Final (1).pdf`
- `2021 Whaley Medical Authorization (HIPAA) (1).pdf`

**Additional:**
- `2021 Whaley Medical Treatment Questionnaire (1).pdf`
- `2021 Whaley Authorization of Digitally Signature Replication (1).pdf`
- `2021 Whaley Wage & Salary Verification (1).pdf` (always required for WC)

**Conditional:**
- `2021 Whaley CMS Medicare Verification Form (1).pdf` (if Medicare)

---

## Steps

### Step 1: Load Document Checklist

Read `workflow_state.json` to determine:
- Case type
- Documents already received
- Documents still pending

Generate a status report:

```
📋 Document Checklist for [Case Name]

LANDMARKS (Required to proceed):
[ ] New Client Information Sheet
[ ] Fee Agreement ({case_type})
[ ] Medical Authorization (HIPAA)

ADDITIONAL DOCUMENTS:
[ ] Medical Treatment Questionnaire
[ ] Digital Signature Authorization
[ ] {Case Type} Accident Detail Sheet

CONDITIONAL (if applicable):
[ ] Wage & Salary Verification
[ ] CMS Medicare Verification
```

### Step 2: For Each Missing Document

For each document not yet received, offer the user three options:

```
Missing: [Document Name]
Template: templates/intake_forms/[filename].pdf

Options:
A) Request from client (send email with form attached)
B) I have this document (user will provide)
C) Skip for now

Which would you like to do?
```

#### Option A: Request from Client

Use the `document-request` skill:
1. Get client contact information from `contacts.json`
2. Generate request email using `templates/request-email.md`
3. Attach fillable PDF templates from `templates/intake_forms/`
4. Send request (or provide draft for user approval)

#### Option B: User Provides Document

Use the `document-intake` skill:
1. User uploads or provides document
2. Validate document type
3. Save to `{case_folder}/Client/`
4. Update `workflow_state.json`
5. Update landmark if applicable

#### Option C: Skip Document

1. Confirm with user: "Are you sure you want to skip [Document]?"
2. If landmark document: "This is required to complete Phase 0. The case will remain blocked until this is received."
3. If non-landmark: "Okay, skipping [Document]. You can collect this later."

### Step 3: Update Landmarks

After each landmark document is received, update `workflow_state.json`:

| Document Received | Landmark Updated |
|-------------------|------------------|
| New Client Information Sheet | `landmarks.client_info_received = true` |
| Fee Agreement (any type) | `landmarks.contract_signed = true` |
| Medical Authorization (HIPAA) | `landmarks.medical_auth_signed = true` |

### Step 4: Check Phase Completion

After each update, check if all 3 landmarks are met:

```python
if (landmarks["client_info_received"] and 
    landmarks["contract_signed"] and 
    landmarks["medical_auth_signed"]):
    # Phase 0 complete!
    workflow_state["phase"] = "file_setup"
    workflow_state["phase_number"] = 1
```

**If complete:**
```
🎉 All intake documents received!

Phase 0: Onboarding is complete.
Proceeding to Phase 1: File Setup.

Remaining documents to collect (non-blocking):
- Medical Treatment Questionnaire
- Digital Signature Authorization
```

**If incomplete:**
```
📋 Document Collection Status

Received: 2/3 landmarks
✓ New Client Information Sheet
✓ Medical Authorization
✗ Fee Agreement (MISSING - Required)

The case cannot proceed to Phase 1 until the Fee Agreement is received.

Template available: templates/intake_forms/2021 Whaley {CaseType} Fee Agreement.pdf

Would you like me to send a request to the client with this form attached?
```

---

## Skills Reference

### document-request

**Location:** `skills/document-request/skill.md`
**Purpose:** Generate and send document requests with attached templates
**Use when:** User wants to request documents from client

### document-intake

**Location:** `skills/document-intake/skill.md`
**Purpose:** Process and file received documents, update landmarks
**Use when:** User provides a document to add to the case

### docusign-send

**Location:** `skills/docusign-send/skill.md`
**Purpose:** Send documents for electronic signature via DocuSign
**Use when:** User wants to send Fee Agreement, HIPAA, or other documents for e-signature

---

## DocuSign Integration

For signature documents (Fee Agreement, HIPAA, Digital Signature Authorization), you can offer electronic signature via DocuSign:

### Documents Suitable for DocuSign

| Document | Anchor String | Notes |
|----------|--------------|-------|
| Fee Agreement | `/sig1/` | Requires client signature |
| Medical Authorization (HIPAA) | `/sig1/` | Requires client signature |
| Digital Signature Authorization | `/sig1/` | Authorizes future e-signatures |

### When to Offer DocuSign

```
📝 Documents requiring signature:
• Fee Agreement
• Medical Authorization (HIPAA)

Options for signature collection:
A) Send via DocuSign for electronic signature
B) Email forms for client to print, sign, and return
C) User will obtain signatures in person

Which method would you prefer?
```

### DocuSign Workflow

1. **User selects DocuSign option**
2. **Verify client email** in contacts.json
3. **Call docusign-send skill**:
   - Send each document that needs signature
   - Track envelope IDs for follow-up
4. **Monitor for completion**:
   - DocuSign sends notification when signed
   - Signed document auto-downloads to case folder
5. **Update landmarks** when signed document received

### DocuSign Status Tracking

Update `workflow_state.json` with DocuSign status:

```json
{
  "docusign_envelopes": [
    {
      "document": "Fee Agreement",
      "envelope_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "sent_date": "2024-12-06",
      "status": "sent",
      "follow_up_date": "2024-12-09"
    }
  ]
}
```

---

## Templates Reference

### intake_forms/

**Location:** `templates/intake_forms/`
**Contents:** All 11 fillable PDF templates for intake documents
**Index:** `templates/intake_forms/INDEX.md`

### document-checklist.md

**Location:** `templates/document-checklist.md`
**Purpose:** Track document receipt status

### request-email.md

**Location:** `templates/request-email.md`
**Purpose:** Email templates for client document requests

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Client contact info missing | Ask user for email/phone or add to contacts.json |
| Document unreadable | Ask user to re-upload or clarify |
| Wrong document type | Inform user and provide correct template |
| Duplicate document | Ask if this replaces existing or is additional |

---

## Output

**Deliverables:**
- All documents filed in `{case_folder}/Client/`
- `workflow_state.json` updated with document status
- Landmarks updated when signature documents received

**Completion Criteria:**
- All 3 landmark documents received
- Landmarks in `workflow_state.json` all set to `true`

**Next Phase:** Phase 1: File Setup

---

## Example Interaction

```
Agent: I've created the case folder for Jane Smith. Now let's collect the intake 
       documents.
       
       📋 Document Checklist for Jane-Smith-MVA-12-05-2024
       
       LANDMARKS (Required):
       [ ] New Client Information Sheet
       [ ] MVA Fee Agreement
       [ ] Medical Authorization (HIPAA)
       
       ADDITIONAL:
       [ ] Medical Treatment Questionnaire
       [ ] Digital Signature Authorization
       [ ] MVA Accident Detail Sheet
       
       All templates are available in templates/intake_forms/
       
       Do you have any of these documents ready, or should I send a request
       to the client with the fillable forms attached?

User: I have the fee agreement and HIPAA signed. The rest needs to come from 
      the client.

Agent: Great! Please provide the Fee Agreement and Medical Authorization.
       
       [User uploads documents]
       
       ✓ Fee Agreement received and filed
       ✓ Medical Authorization received and filed
       
       Updated status:
       [✓] MVA Fee Agreement
       [✓] Medical Authorization (HIPAA)
       [ ] New Client Information Sheet ← Still needed (landmark)
       
       I'll prepare a request for the remaining documents. What's the client's
       email address?

User: jane.smith@email.com

Agent: I've prepared a document request email for Jane Smith with these forms
       attached from templates/intake_forms/:
       
       Required:
       • 2021 Whaley New Client Information Sheet (1).pdf
       
       Additional:
       • 2021 Whaley Medical Treatment Questionnaire (1).pdf
       • 2021 Whaley Authorization of Digitally Signature Replication (1).pdf
       • 2021 Whaley MVA Accident Detail Information Sheet (1).pdf
       
       Should I send this request?
```
