---
name: send_documents_for_signature
description: >
  Prepare and send required legal documents (retainer agreement, HIPAA authorization,
  Medicare authorization) for client signature. This workflow generates documents
  from templates, sends for e-signature, and tracks signature status.
phase: file_setup
workflow_id: send_documents_for_signature
related_skills:
  - document-docx
related_tools:
  - document_generator
templates:
  - forms/intake/whaley_mva_retainer_agreement_TEMPLATE.md
  - forms/intake/whaley_hipaa_authorization_TEMPLATE.md
  - forms/intake/medicare_authorization_TEMPLATE.md
---

# Send Documents for Signature Workflow

## Overview

This workflow prepares and sends the essential legal documents that establish the attorney-client relationship and authorize us to act on the client's behalf. The retainer agreement is a hard blocker for phase advancement.

**Workflow ID:** `send_documents_for_signature`  
**Phase:** `file_setup`  
**Owner:** Agent (preparation) / User (sending)  
**Repeatable:** No

---

## Prerequisites

- Intake workflow complete
- Case accepted by attorney
- Client contact information available

---

## Workflow Steps

### Step 1: Prepare Retainer Agreement

**Step ID:** `prepare_retainer`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Generate the retainer agreement using the template and case data.

**Skill:** `Skills/document-docx/skill.md`  
**Tool:** `document_generator`  
**Tool Available:** ✅ Yes

**Template:** `forms/intake/whaley_mva_retainer_agreement_TEMPLATE.md`

**Template Variables:**
| Variable | Source | Description |
|----------|--------|-------------|
| `{{client.name}}` | overview.json | Client's full legal name |
| `{{client.address}}` | overview.json | Client's mailing address |
| `{{accident.date}}` | overview.json | Date of accident |
| `{{today}}` | system | Current date |
| `{{fee_percentage_prelit}}` | 33⅓% | Pre-litigation fee percentage |
| `{{fee_percentage_lit}}` | 40% | Litigation fee percentage |

**Agent Action:**
> "I'll prepare the retainer agreement using the template. Fee structure: 33⅓% pre-litigation, 40% if lawsuit filed."

**Output:** Generated retainer agreement document

**Data Target:** `Documents/Intake/retainer_agreement_{{client.name}}.docx`

---

### Step 2: Prepare HIPAA Authorization

**Step ID:** `prepare_hipaa`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Generate the HIPAA authorization form.

**Skill:** `Skills/document-docx/skill.md`

**Template:** `forms/intake/whaley_hipaa_authorization_TEMPLATE.md`

**Template Variables:**
| Variable | Source | Description |
|----------|--------|-------------|
| `{{client.name}}` | overview.json | Client's full legal name |
| `{{client.dob}}` | overview.json | Client's date of birth |
| `{{client.ssn_last4}}` | overview.json | Last 4 of SSN (if available) |
| `{{firm.name}}` | config | Law firm name |
| `{{firm.address}}` | config | Law firm address |

**Agent Action:**
> "I'll prepare the HIPAA authorization. This allows us to obtain medical records from all providers."

**Output:** Generated HIPAA authorization document

**Data Target:** `Documents/Intake/hipaa_authorization_{{client.name}}.docx`

---

### Step 3: Prepare Medicare Authorization (Conditional)

**Step ID:** `prepare_medicare`  
**Owner:** Agent  
**Automatable:** Yes  
**Conditional:** Only if client is Medicare-eligible

**Condition:**
```
client.age >= 65 OR client.on_disability == true
```

**Action:**
Generate Medicare authorization for lien tracking.

**Skill:** `Skills/document-docx/skill.md`

**Template:** `forms/intake/medicare_authorization_TEMPLATE.md`

**Agent Action:**
> "Client is Medicare-eligible. I'll prepare Medicare authorization for lien tracking."

**Output:** Generated Medicare authorization document

**Data Target:** `Documents/Intake/medicare_authorization_{{client.name}}.docx`

---

### Step 4: Send Documents for Signature

**Step ID:** `send_for_signature`  
**Owner:** User  
**Automatable:** No (DocuSign integration pending)

**Tool:** `docusign_api`  
**Tool Available:** ❌ No

**Manual Process:**
1. Log into DocuSign
2. Create new envelope
3. Upload prepared documents:
   - Retainer agreement (required)
   - HIPAA authorization (required)
   - Medicare authorization (if applicable)
4. Add signature/initial fields to documents
5. Add client as signer using `client.email`
6. Send envelope

**Agent Prompt to User:**
> "Documents prepared. Please send to client via DocuSign and update when sent."

**Updates on Completion:**
```json
{
  "documents.retainer.status": "sent",
  "documents.retainer.sent_date": "{{today}}",
  "documents.hipaa.status": "sent",
  "documents.hipaa.sent_date": "{{today}}"
}
```

**Data Target:** `Case Information/overview.json` → `documents` object

---

### Step 5: Track Signature Status

**Step ID:** `track_signatures`  
**Owner:** User  
**Automatable:** No  
**Waiting On:** Client

**Action:**
Monitor for returned signatures. Follow up if not received within 3 days.

**Follow-Up Schedule:**
| Days Since Sent | Action |
|-----------------|--------|
| 3 days | First follow-up call/text |
| 5 days | Second follow-up, email reminder |
| 7 days | Attorney notification if still unsigned |

**Agent Prompt to User:**
> "Waiting for client signatures. Follow up if not received in 3 days."

**On Signature Received:**
Update document status:
```json
{
  "documents.retainer.status": "signed",
  "documents.retainer.signed_date": "{{signature_date}}",
  "documents.hipaa.status": "signed",
  "documents.hipaa.signed_date": "{{signature_date}}"
}
```

---

## Outputs

### Documents Generated

| Document | Required | Blocker |
|----------|----------|---------|
| Retainer Agreement | Yes | Hard blocker for phase exit |
| HIPAA Authorization | Yes | Soft blocker (needed for records) |
| Medicare Authorization | Conditional | Soft blocker (if applicable) |

### Calendar Events Created

| Event | Timing | Description |
|-------|--------|-------------|
| Signature follow-up | +3 days | Follow up on unsigned documents |

---

## Completion Criteria

### Required
- `documents.retainer.status == "signed"` ⭐ HARD BLOCKER

### Recommended
- `documents.hipaa.status == "signed"`

---

## State Updates

On workflow completion, update `case_state.json`:
```json
{
  "workflows": {
    "send_documents_for_signature": {
      "status": "complete",
      "completed_date": "{{today}}",
      "documents_sent": ["retainer", "hipaa", "medicare"],
      "all_signed": true
    }
  }
}
```

---

## Related Workflows

- **Triggered By:** `intake` (case accepted)
- **Triggers:** None (but retainer signature unblocks phase exit)

---

## Skills Used

| Skill | Purpose |
|-------|---------|
| `document-docx` | Generate documents from templates |

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Client doesn't have email | Use text-to-sign or mail physical copies |
| Client won't sign retainer | Attorney call to address concerns. May need to decline. |
| DocuSign not working | Use alternative e-sign or physical signature |
| Client signed wrong fields | Resend with clearer instructions |
| Medicare status unclear | Verify age and disability status. When in doubt, include. |

