---
name: document-request
description: >
  Generate and send intake document requests to personal injury clients. Creates 
  personalized emails with attached fillable PDF forms based on case type (MVA, S&F, WC).
  When Claude needs to request intake documents from a client, send document request
  emails, follow up on missing paperwork, or prepare document packets for new cases.
  Use for initial intake requests, reminder emails, and specific document follow-ups.
  Templates available in ../templates/intake_forms/.
---

# Document Request Skill

## Overview

Generate professional document request communications for personal injury intake. This skill creates personalized emails requesting specific documents, attaches the correct fillable PDF forms based on case type, and tracks pending requests.

## Capabilities

- Generate initial intake document request emails
- Create follow-up reminders for missing documents
- Select correct forms based on case type (MVA, S&F, WC)
- Attach fillable PDF templates to requests
- Track document request history

## When to Use

Use this skill when:
- Setting up a new case and need to request intake documents
- Following up on documents not yet received
- User asks to "send a request" or "ask the client for documents"
- Client needs specific forms sent to them

**Do NOT use when:**
- Processing documents already received (use `document-intake`)
- Creating the case folder structure (use `case_setup` workflow)

---

## Required Inputs

| Input | Source | Required |
|-------|--------|:--------:|
| Client name | `overview.json` | Yes |
| Client email | `contacts.json` or user | Yes |
| Case type | `workflow_state.json` | Yes |
| Documents to request | `workflow_state.json` | Yes |

---

## Template Files Reference

All fillable PDF templates are located in:
`../templates/intake_forms/`

### By Document Type

| Document ID | Template File |
|-------------|---------------|
| `new_client_information_sheet` | `2021 Whaley New Client Information Sheet (1).pdf` |
| `fee_agreement_mva` | `2021 Whaley MVA Fee Agreement (1).pdf` |
| `fee_agreement_sf` | `2021 Whaley S&F Fee Agreement (1).pdf` |
| `fee_agreement_wc` | `2021 Whaley WC Fee Agreement - Final (1).pdf` |
| `medical_authorization` | `2021 Whaley Medical Authorization (HIPAA) (1).pdf` |
| `medical_treatment_questionnaire` | `2021 Whaley Medical Treatment Questionnaire (1).pdf` |
| `digital_signature_authorization` | `2021 Whaley Authorization of Digitally Signature Replication (1).pdf` |
| `mva_accident_detail_sheet` | `2021 Whaley MVA Accident Detail Information Sheet (1).pdf` |
| `sf_accident_detail_sheet` | `2021 Whaley S&F Accident Detail Information Sheet (1).pdf` |
| `wage_salary_verification` | `2021 Whaley Wage & Salary Verification (1).pdf` |
| `cms_medicare_verification` | `2021 Whaley CMS Medicare Verification Form (1).pdf` |

---

## Execution Steps

### Step 1: Gather Required Information

```
Read from workflow_state.json:
- case_type
- documents_pending

Read from overview.json:
- client_name

Read from contacts.json (or ask user):
- client_email
```

### Step 2: Determine Documents to Request

Based on case type and pending documents, select appropriate templates:

**MVA Cases:**
- New Client Information Sheet
- MVA Fee Agreement
- Medical Authorization (HIPAA)
- Medical Treatment Questionnaire
- Digital Signature Authorization
- MVA Accident Detail Sheet
- (Conditional) Wage & Salary Verification
- (Conditional) CMS Medicare Verification

**S&F Cases:**
- New Client Information Sheet
- S&F Fee Agreement
- Medical Authorization (HIPAA)
- Medical Treatment Questionnaire
- Digital Signature Authorization
- S&F Accident Detail Sheet
- (Conditional) Wage & Salary Verification
- (Conditional) CMS Medicare Verification

**WC Cases:**
- New Client Information Sheet
- WC Fee Agreement
- Medical Authorization (HIPAA)
- Medical Treatment Questionnaire
- Digital Signature Authorization
- Wage & Salary Verification (always required)
- (Conditional) CMS Medicare Verification

### Step 3: Generate Email

**Initial Request Template:**

```
Subject: Documents Needed - Your Personal Injury Case

Dear {client_first_name},

Thank you for choosing Whaley Law Firm to represent you. To move forward 
with your case, please complete and return the following documents.

REQUIRED (Please return ASAP):
• New Client Information Sheet
• Fee Agreement
• Medical Authorization (HIPAA)

ADDITIONAL:
• Medical Treatment Questionnaire
• Digital Signature Authorization
• {case_type} Accident Detail Sheet

I've attached fillable PDF versions of each form. You can complete them 
electronically and email them back, or print, sign, and return by mail or fax.

Return Options:
- Email: Reply to this email with attachments
- Fax: (XXX) XXX-XXXX
- Mail: [Office Address]

Please don't hesitate to contact us if you have any questions.

Best regards,
{sender_name}
Whaley Law Firm
```

**Follow-Up Template:**

```
Subject: Reminder: Documents Still Needed - {case_name}

Dear {client_first_name},

This is a friendly reminder that we're still waiting on the following 
documents to proceed with your case:

{missing_documents_list}

Your case cannot move forward until we receive these documents. I've 
re-attached the forms for your convenience.

Thank you,
{sender_name}
Whaley Law Firm
```

### Step 4: Attach Templates

Attach the fillable PDF templates from `../templates/intake_forms/`:

```python
attachments = []
for doc_id in documents_to_request:
    template_path = get_template_path(doc_id, case_type)
    attachments.append(template_path)
```

### Step 5: Present to User

```
I've prepared a document request for {client_name}:

To: {client_email}
Subject: Documents Needed - Your Personal Injury Case

{email_body}

Attachments ({count} files):
• New Client Information Sheet.pdf
• {Case Type} Fee Agreement.pdf
• Medical Authorization (HIPAA).pdf
...

Options:
A) Send this email
B) Modify the message
C) Save as draft
```

### Step 6: Log Request

After sending, update tracking:

```json
// Add to workflow_state.json
{
  "document_requests": [
    {
      "date": "2024-12-06",
      "method": "email",
      "documents_requested": ["new_client_information_sheet", "fee_agreement", ...],
      "status": "sent"
    }
  ]
}
```

---

## Output

**Deliverables:**
- Personalized email with correct documents listed
- Fillable PDF templates attached
- Request logged in `workflow_state.json`

**Success Criteria:**
- Email sent or draft saved
- Correct templates attached based on case type
- Request tracked for follow-up
