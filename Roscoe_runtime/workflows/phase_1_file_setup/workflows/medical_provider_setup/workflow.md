---
name: medical_provider_setup
description: >
  Add medical providers to the case file with complete contact information,
  treatment dates, and injuries treated. AUTOMATICALLY sends medical records
  requests for providers with completed treatment (e.g., EMS, ER). Uses signed
  HIPAA from Phase 0. When Claude needs to add a medical provider, request
  medical records, or track provider treatment status. Use throughout case
  lifecycle as new providers are identified.
phase: file_setup
workflow_id: medical_provider_setup
related_skills:
  - medical-records-request
related_tools:
  - generate_document.py
templates:
  - templates/2022 Whaley Medical Record Request (URR) (1).docx
  - templates/2023 Whaley Law Firm Medical Request Template (1).pdf
  - templates/2023 Whaley Initial Medical Billing Request to Provider (MBR) (1).pdf
triggered_by:
  - intake
  - client_check_in
  - referral_new_provider
---

# Medical Provider Setup Workflow

## Overview

This workflow adds medical providers to the case file and **AUTOMATICALLY** sends medical records requests for providers with completed treatment. It collects provider contact information, treatment dates, and documents which injuries each provider is treating.

**Key Feature:** When a provider with `treatment_status: "completed"` is added, the system automatically generates and sends a medical records request using the signed HIPAA from Phase 0.

**Workflow ID:** `medical_provider_setup`  
**Phase:** `file_setup` (but can run during Treatment)  
**Owner:** Agent  
**Repeatable:** Yes

---

## Prerequisites

- Case created (Phase 0 complete)
- HIPAA Authorization signed (from Phase 0)
- Provider information available from client or referral

---

## Triggers

This workflow is triggered by:
- `intake` workflow (when providers mentioned during intake)
- `client_check_in` workflow (when new providers mentioned)
- `referral_new_provider` workflow (when we refer client to new provider)
- Manual trigger when provider discovered
- Police report analysis (identifies EMS, ER)

---

## Workflow Steps

### Step 1: Collect Provider Information

**Step ID:** `collect_provider_info`

**Action:**
Gather provider contact details and classification.

**Fields to Collect:**
| Field | Description | Required |
|-------|-------------|:--------:|
| `name` | Provider/facility name | Yes |
| `type` | Provider type (see categories) | Yes |
| `address` | Street address | Yes |
| `phone` | Main phone number | Yes |
| `fax` | Fax number (for records) | Yes |
| `records_contact` | Records department contact | Recommended |
| `records_email` | Records department email | Recommended |

**Provider Type Categories:**
| Type | Examples | Typically Completed at Phase 1? |
|------|----------|:-------------------------------:|
| `ems` | Ambulance, EMS | Yes |
| `emergency` | ER, Urgent Care | Yes |
| `hospital` | Inpatient stay | Often |
| `primary_care` | Family doctor | No |
| `chiropractic` | Chiropractor | No |
| `orthopedic` | Orthopedic surgeon | No |
| `pain_management` | Pain clinic | No |
| `physical_therapy` | PT clinic | No |
| `imaging` | MRI center, radiology | Often |
| `specialist` | Other specialists | No |

### Step 2: Collect Treatment Dates

**Step ID:** `collect_treatment_dates`

**Fields to Collect:**
| Field | Description | Required |
|-------|-------------|:--------:|
| `first_visit` | Date of first visit | Yes |
| `last_visit` | Date of most recent visit | Yes |
| `treatment_status` | See options below | Yes |
| `expected_completion` | When treatment expected to end | If ongoing |

**Treatment Status Options:**
| Status | Description | Auto-Request Records? |
|--------|-------------|:---------------------:|
| `completed` | Treatment finished | **YES** |
| `ongoing` | Currently treating | No - wait until complete |
| `pending` | Scheduled but not yet seen | No |
| `on_hold` | Treatment paused | No |

### Step 3: Document Injuries Treated

**Step ID:** `collect_injuries_treated`

**Fields to Collect:**
| Field | Description |
|-------|-------------|
| `injuries_treated[]` | Array of injury descriptions |

### Step 4: AUTO-SEND Records Request (if completed)

**Step ID:** `auto_send_records_request`
**Trigger:** `treatment_status == "completed"`

**⚡ AUTOMATIC ACTION:**
When a provider is added with completed treatment, the system automatically:

1. **Copy Records Request Template to Provider Folder**
   - Template: `templates/2022 Whaley Medical Record Request (URR) (1).docx`
   - Destination: `/{project}/Medical Providers/{provider_name}/Medical Records Request.docx`

2. **Generate Filled Document**
   - Use `skills/medical-records-request/skill.md`
   - Call: `python generate_document.py "/{project}/Medical Providers/{provider_name}/Medical Records Request.docx"`
   - Tool auto-fills provider and case data from path context

3. **Attach Signed HIPAA**
   - Retrieve HIPAA from `{case_folder}/Client/`
   - Attach to records request

4. **Send Request**
   - Via fax (preferred) or email
   - Record sent date in `medical_providers.json`

5. **Schedule Follow-Up**
   - Set 14-day follow-up reminder
   - Add to case calendar

**Document Generation Pattern:**
```bash
# Copy template to provider folder (creates context)
cp "/templates/2022 Whaley Medical Record Request (URR) (1).docx" \
   "/{project}/Medical Providers/{provider_name}/Medical Records Request.docx"

# Generate filled document (path tells tool which provider)
python generate_document.py "/{project}/Medical Providers/{provider_name}/Medical Records Request.docx"
```

**Auto-Request Output:**
```
📬 MEDICAL RECORDS REQUEST SENT AUTOMATICALLY

Provider: Louisville EMS
Type: EMS
Treatment Status: Completed (single transport on 12/01/2024)

Records Request Details:
- Letter generated from template
- Signed HIPAA attached
- Sent via fax to: (502) 555-1234
- Date sent: 2024-12-06

Follow-up scheduled: 2024-12-20 (14 days)

The records request has been tracked in the case file.
```

### Step 5: Save Provider Entry

**Data Target:** `Case Information/medical_providers.json`

**Complete Provider Entry Structure:**
```json
{
  "id": "provider_001",
  "name": "Louisville EMS",
  "type": "ems",
  "address": "123 Emergency Way, Louisville, KY 40202",
  "phone": "(502) 555-1000",
  "fax": "(502) 555-1234",
  "records_contact": {
    "name": "Records Department",
    "email": "records@louisville-ems.org"
  },
  "treatment": {
    "first_visit": "2024-12-01",
    "last_visit": "2024-12-01",
    "status": "completed",
    "visit_count": 1
  },
  "injuries_treated": ["cervical_strain", "lumbar_strain"],
  "records": {
    "requested_date": "2024-12-06",
    "request_method": "fax",
    "received_date": null,
    "file_path": null,
    "follow_up_date": "2024-12-20"
  },
  "bills": {
    "requested_date": "2024-12-06",
    "received_date": null,
    "amount": null
  },
  "notes": "Transported client from accident scene to University Hospital ER"
}
```

---

## Auto-Request Decision Logic

```
Provider Added
     │
     ▼
┌─────────────────────────┐
│ treatment_status ==     │
│ "completed"?            │
└───────────┬─────────────┘
            │
     ┌──────┴──────┐
     │ YES         │ NO
     ▼             ▼
┌─────────────┐ ┌─────────────────┐
│ AUTO-SEND   │ │ Add provider,   │
│ Records     │ │ no request yet  │
│ Request     │ │ (wait for       │
│ with HIPAA  │ │ treatment       │
└──────┬──────┘ │ completion)     │
       │        └─────────────────┘
       ▼
┌─────────────────┐
│ Schedule        │
│ 14-day          │
│ follow-up       │
└─────────────────┘
```

---

## Templates Reference

### Medical Records Request (Word)

**Template:** `templates/2022 Whaley Medical Record Request (URR) (1).docx`
**Registry ID:** `medical_record_request`
**Tool:** `generate_document.py`
**Use when:** Records request via mail or email
**Destination:** Copy to `/{project}/Medical Providers/{provider}/Medical Records Request.docx`

**Auto-fill from path context:**
- Provider info from folder name → looks up in `medical_providers.json`
- Client info from `overview.json`
- Firm info from `firm_config.json`

### Medical Records Request (PDF)

**Template:** `templates/2023 Whaley Law Firm Medical Request Template (1).pdf`
**Registry ID:** `medical_request_template`
**Tool:** `generate_document.py`
**Use when:** Alternative PDF format preferred
**Destination:** Copy to `/{project}/Medical Providers/{provider}/Medical Records Request.pdf`

### Medical Billing Request

**Template:** `templates/2023 Whaley Initial Medical Billing Request to Provider (MBR) (1).pdf`
**Registry ID:** `medical_billing_request`
**Tool:** `generate_document.py`
**Use when:** Requesting itemized bills in addition to records
**Destination:** Copy to `/{project}/Medical Providers/{provider}/Medical Billing Request.pdf`

---

## Skills Reference

### medical-records-request

**Location:** `skills/medical-records-request/skill.md`
**Purpose:** Generate and send medical records request by copying template to provider folder
**Tool:** Uses `generate_document.py` - path-based provider context detection
**Triggered by:** Provider with `treatment_status: "completed"`

---

## Providers Typically Completed at Phase 1

These providers usually have completed treatment by the time we reach Phase 1:

| Provider Type | Why Completed | Records Request Priority |
|---------------|---------------|--------------------------|
| EMS | Single transport | High - send immediately |
| ER | Acute care only | High - send immediately |
| Imaging | Diagnostic only | High - need for treatment |
| Hospital (if discharged) | Acute care | High |

---

## Outputs

### Provider Entry Created
Each provider gets a complete entry in `medical_providers.json`

### Auto-Request Sent (if completed)
For completed treatment:
- Records request letter generated
- HIPAA attached
- Request sent (fax/email)
- Follow-up scheduled

### Landmark Update
When all known providers added:
- `providers.setup_complete = true`
- `providers.provider_count` updated

---

## Completion Criteria

### Per Provider (Required)
- `name` populated
- `type` populated
- `first_visit` date populated
- `treatment_status` set
- If `completed`: records request sent

### Landmark Complete
- All providers from intake added
- All completed treatment providers have records requests sent
- Contact info complete for follow-up

---

## Example Interaction

```
Agent: I'm adding Louisville EMS as a provider. Let me gather the details:

Provider: Louisville EMS
Type: EMS
Treatment Status: Completed (single transport 12/01/2024)

📬 Since treatment is complete, I'm automatically sending a records request:

✓ Medical records request generated
✓ Signed HIPAA from Phase 0 attached
✓ Request sent via fax to (502) 555-1234
✓ Follow-up scheduled for 12/20/2024

Provider added and records request sent!

---

Now adding University Hospital ER...

Provider: University Hospital ER
Type: Emergency
Treatment Status: Completed (discharged same day 12/01/2024)

📬 Automatically sending records request...

✓ Medical records request generated
✓ Signed HIPAA attached
✓ Request sent via fax to (502) 555-2000
✓ Follow-up scheduled for 12/20/2024

---

Adding Dr. Smith Orthopedics...

Provider: Dr. Smith Orthopedics
Type: Orthopedic
Treatment Status: Ongoing (started 12/05/2024)

Note: Treatment is ongoing, so no records request sent yet.
Records will be requested when treatment is complete.

Provider added to case file.
```

