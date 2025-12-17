---
name: document-intake
description: >
  Process and file received intake documents for personal injury cases. Validates 
  document type, saves to correct case folder location, and updates workflow tracking.
  Automatically updates Phase 0 landmarks when required signature documents (Client Info,
  Fee Agreement, Medical Authorization) are received. When Claude needs to process 
  documents provided by user, file intake paperwork, update document status, or check
  if Phase 0 landmarks are complete. Use for single documents or batch processing.
---

# Document Intake Skill

## Overview

Process documents received from clients, validate them, save to the correct case folder, and update workflow tracking. This skill automatically updates landmarks when required signature documents are received, enabling Phase 0 completion.

## Capabilities

- Process single or multiple documents
- Validate document type and content
- Save to correct case folder location (`Client/`)
- Update `workflow_state.json` tracking
- Automatically update landmarks for signature documents
- Check Phase 0 completion status

## When to Use

Use this skill when:
- User uploads or provides a document
- User says "I have the [document]" or "here's the [document]"
- Processing documents from email attachments
- Batch processing multiple received documents
- Checking if all intake documents are complete

**Do NOT use when:**
- Requesting documents from clients (use `document-request`)
- Creating case folder structure (use `case_setup` workflow)

---

## Document Type Recognition

### Document ID to Display Name Mapping

| Document ID | Display Name | Landmark? |
|-------------|--------------|:---------:|
| `new_client_information_sheet` | New Client Information Sheet | **YES** |
| `fee_agreement` | Fee Agreement | **YES** |
| `medical_authorization` | Medical Authorization (HIPAA) | **YES** |
| `medical_treatment_questionnaire` | Medical Treatment Questionnaire | No |
| `digital_signature_authorization` | Digital Signature Authorization | No |
| `mva_accident_detail_sheet` | MVA Accident Detail Sheet | No |
| `sf_accident_detail_sheet` | S&F Accident Detail Sheet | No |
| `wage_salary_verification` | Wage & Salary Verification | No |
| `cms_medicare_verification` | CMS Medicare Verification | No |

### Landmark Documents

These three documents trigger landmark updates:

| Document | Landmark Key |
|----------|--------------|
| New Client Information Sheet | `client_info_received` |
| Fee Agreement (any type) | `contract_signed` |
| Medical Authorization (HIPAA) | `medical_auth_signed` |

---

## Execution Steps

### Step 1: Receive Document

Accept document from user via:
- File upload
- File path reference
- Indication that document exists

### Step 2: Identify Document Type

**Method 1: User specifies**
```
User: "Here's the HIPAA authorization"
→ Document ID: medical_authorization
```

**Method 2: Filename inference**
```
Filename: "Whaley Medical Authorization - Jane Smith.pdf"
→ Document ID: medical_authorization
```

**Method 3: Ask user**
```
Which document is this?

A) New Client Information Sheet
B) Fee Agreement
C) Medical Authorization (HIPAA)
D) Medical Treatment Questionnaire
E) Digital Signature Authorization
F) Accident Detail Sheet
G) Wage & Salary Verification
H) Medicare Verification Form
```

### Step 3: Validate Document

Basic validation checks:
- File is readable (not corrupted)
- File is not empty
- File type matches expected format (PDF)

**If validation fails:**
```
This file appears to be [issue]. Could you:
- Re-upload the document, or
- Confirm this is the correct file?
```

### Step 4: Save to Case Folder

**Location:** `{case_folder}/Client/`

**Naming Convention:**
```
{DocumentType}_{ClientName}_{YYYY-MM-DD}.pdf

Examples:
- Client_Info_Jane_Smith_2024-12-06.pdf
- Fee_Agreement_Jane_Smith_2024-12-06.pdf
- Medical_Auth_Jane_Smith_2024-12-06.pdf
```

### Step 5: Update workflow_state.json

```python
# Move from pending to received
workflow_state["documents_pending"].remove(document_id)
workflow_state["documents_received"].append({
    "type": document_id,
    "filename": saved_filename,
    "received_date": "2024-12-06",
    "location": "Client/"
})

# Update landmark if applicable
landmark_map = {
    "new_client_information_sheet": "client_info_received",
    "fee_agreement": "contract_signed",
    "medical_authorization": "medical_auth_signed"
}

if document_id in landmark_map:
    workflow_state["landmarks"][landmark_map[document_id]] = True
```

### Step 6: Check Phase Completion

```python
landmarks = workflow_state["landmarks"]

if (landmarks["client_info_received"] and 
    landmarks["contract_signed"] and 
    landmarks["medical_auth_signed"]):
    
    # Phase 0 complete!
    workflow_state["phase"] = "file_setup"
    workflow_state["phase_number"] = 1
    workflow_state["workflow_status"]["document_collection"] = "completed"
```

### Step 7: Report Status

**Single document received:**
```
✓ Medical Authorization received and filed

Location: Client/Medical_Auth_Jane_Smith_2024-12-06.pdf

Landmark Status:
[✓] Client Info Received
[ ] Contract Signed
[✓] Medical Auth Signed ← Just completed!

Still needed: Fee Agreement
```

**All landmarks complete:**
```
✓ Fee Agreement received and filed

🎉 All landmarks complete!

Landmark Status:
[✓] Client Info Received
[✓] Contract Signed ← Just completed!
[✓] Medical Auth Signed

Phase 0: Onboarding is complete.
Proceeding to Phase 1: File Setup.

Remaining documents (non-blocking):
- Medical Treatment Questionnaire
- Digital Signature Authorization
```

---

## Batch Processing

When user provides multiple documents:

```
I received 3 documents. Processing...

1. fee_agreement_signed.pdf
   → Fee Agreement ✓
   → Landmark updated: contract_signed

2. hipaa_form.pdf
   → Medical Authorization ✓
   → Landmark updated: medical_auth_signed

3. client_info.pdf
   → New Client Information Sheet ✓
   → Landmark updated: client_info_received

All 3 documents filed successfully!

🎉 All landmarks complete! Phase 0 is finished.
```

---

## Error Handling

| Error | Response |
|-------|----------|
| File unreadable | "I couldn't open this file. Can you try re-uploading?" |
| Empty file | "This file appears to be empty. Please check and resend." |
| Wrong document type | "This appears to be a [X], not a [Y]. Is that correct?" |
| Duplicate document | "A [Document] already exists. Should I replace it or keep both?" |
| Missing case folder | "I can't find the case folder. Has the case been set up?" |

---

## Output

**Deliverables:**
- Document saved to `{case_folder}/Client/`
- `workflow_state.json` updated with:
  - Document added to `documents_received`
  - Document removed from `documents_pending`
  - Landmarks updated if applicable
  - Phase updated if all landmarks complete

**Success Criteria:**
- Document accessible in case folder
- Tracking correctly updated
- User informed of current status and any remaining requirements
