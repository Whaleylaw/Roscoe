# Phase 1: File Setup

## Overview

**Phase ID:** `file_setup`  
**Order:** 1  
**Track:** Pre-Litigation  
**State Machine Field:** `case_state.current_phase = "file_setup"`

The File Setup phase begins **after** Phase 0: Onboarding is complete. At this point, the client has already signed the Fee Agreement, Medical Authorization (HIPAA), and provided initial information. This phase focuses on:

1. Completing detailed intake information
2. Obtaining the accident/police report
3. Opening and setting up all insurance claims (BI and PIP)
4. Setting up medical providers and requesting records for completed treatment

**Key Distinction:** Phase 0 handles acceptance (contract, HIPAA). Phase 1 handles case setup (insurance, providers, records).

---

## Entry Triggers

The case enters File Setup when Phase 0 landmarks are complete:
- Contract (Fee Agreement) signed
- Medical Authorization (HIPAA) signed
- New Client Information Sheet received

---

## Exit Criteria

### Hard Blockers (MUST be completed)

None - Phase 0 already cleared the hard blockers (contract, HIPAA).

### Soft Blockers (Should be completed, can override with acknowledgment)

| Blocker ID | Description | Verification |
|------------|-------------|--------------|
| `full_intake_complete` | Complete intake information collected | `intake.completed == true` |
| `accident_report_obtained` | Police/accident report received | `accident.report.received_date` exists |
| `bi_claims_setup` | BI claims opened and acknowledged | `insurance.bi.claim_acknowledged == true` |
| `pip_claims_setup` | PIP claims opened and ready to pay | `insurance.pip.ready_to_pay_bills == true` |
| `providers_setup` | Medical providers added, records requested | `providers.setup_complete == true` |

---

## Workflows in This Phase

| Workflow ID | Name | Description |
|-------------|------|-------------|
| `full_intake` | Full Intake | Complete client and case information |
| `accident_report` | Accident Report | Request, receive, and analyze police/accident report |
| `insurance_bi_claim` | BI Claim Setup | Open BI claims, send LOR, get liability status |
| `insurance_pip_claim` | PIP Claim Setup | Run waterfall, complete PIP application, open claim |
| `medical_provider_setup` | Medical Provider Setup | Add providers, auto-request records for completed treatment |

---

## Workflow Sequence

```
FROM PHASE 0
(Contract, HIPAA, Client Info already complete)
     │
     ▼
┌─────────────────┐
│ full_intake     │
│ (Additional     │
│ client info)    │
└────────┬────────┘
         │
    ┌────┴────┬─────────────────┐
    │         │                 │
    ▼         ▼                 ▼
┌─────────┐ ┌──────────────┐ ┌──────────────┐
│accident │ │insurance_bi  │ │insurance_pip │
│_report  │ │_claim        │ │_claim        │
└────┬────┘ └──────┬───────┘ └──────┬───────┘
     │             │                │
     │   ┌─────────┴──────┐         │
     │   │                │         │
     │   ▼                ▼         │
     │ ┌────────────┐ ┌────────────┐│
     │ │Liability   │ │PIP App +   ││
     │ │<100%? →    │ │Waterfall   ││
     │ │FLAG USER   │ │(ALWAYS)    ││
     │ └────────────┘ └────────────┘│
     │                              │
     └───────────────┬──────────────┘
                     │
                     ▼
          ┌──────────────────┐
          │medical_provider  │
          │_setup            │
          │ → AUTO records   │
          │   request for    │
          │   completed tx   │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ ALL LANDMARKS    │
          │ COMPLETE?        │
          └────────┬─────────┘
                   │ Yes
                   ▼
          ┌──────────────────┐
          │ Phase 2:         │
          │ Treatment        │
          └──────────────────┘
```

---

## Landmarks

See `landmarks.md` for detailed milestone definitions.

| # | Landmark | Description |
|---|----------|-------------|
| 1 | Full Intake Complete | All client and case information collected |
| 2 | Accident Report Obtained | Police report received and analyzed |
| 3 | Insurance Claims Set Up | BI and PIP claims opened with acknowledgment |
| 4 | Providers Set Up | Medical providers added, records requested for completed treatment |

---

## Insurance Claim Logic

### BI (Bodily Injury) Claims

**Workflow:** `insurance_bi_claim`

| Step | Action |
|------|--------|
| 1 | Identify at-fault party insurance from police report |
| 2 | Send Letter of Representation to BI carrier |
| 3 | Follow up for acknowledgment |
| 4 | Obtain liability status (accepted/denied/partial/investigating) |
| 5 | Confirm coverage and policy limits |

**Liability Flag:**
- If liability is NOT 100% accepted → **FLAG USER** for potential additional BI claims
- Passenger cases with disputed fault may have multiple liable vehicles

### PIP (Personal Injury Protection) Claims

**Workflow:** `insurance_pip_claim`

| Step | Action |
|------|--------|
| 1 | Run PIP waterfall to determine carrier |
| 2 | Complete KACP Application (ALWAYS mandatory) |
| 3 | Send Letter of Representation to PIP carrier |
| 4 | Follow up for acknowledgment |
| 5 | Confirm coverage and ready to pay bills |

**PIP Waterfall (Kentucky):**
1. Client on title of insured vehicle → vehicle's insurer
2. Vehicle occupied was insured → vehicle's insurer
3. Client has own auto insurance → client's insurer
4. Household member has insurance → household insurer
5. None of above → Kentucky Assigned Claims (KAC)

**Special Case:** If client owns uninsured vehicle they occupied → **DISQUALIFIED from PIP**

---

## Medical Provider Setup

**Workflow:** `medical_provider_setup`

| Step | Action |
|------|--------|
| 1 | Add all known medical providers to case |
| 2 | For completed treatment providers (EMS, ER): AUTO-send records request |
| 3 | Records request includes signed HIPAA from Phase 0 |
| 4 | Schedule follow-up for records receipt |

**Auto-Request Trigger:** When a provider with completed treatment is added, the system automatically generates and sends a medical records request.

---

## Skills Required

| Skill | Used By | Purpose |
|-------|---------|---------|
| `lor-generator` | insurance_bi_claim, insurance_pip_claim | Generate LOR from Word templates |
| `pip-waterfall` | insurance_pip_claim | Determine correct PIP carrier |
| `pip-application` | insurance_pip_claim | Fill KACP Application form |
| `medical-records-request` | medical_provider_setup | Generate records request with HIPAA |
| `police-report-analysis` | accident_report | Extract parties and insurance from report |

---

## Tools Required

| Tool | Location | Purpose |
|------|----------|---------|
| `generate_document.py` | `Tools/document_generation/` | **Unified document generator** - fills Word, PDF, Markdown templates |
| `pip_waterfall.py` | `Tools/insurance/` | Determine PIP carrier |
| `lexis_crash_order.py` | `Tools/crash_reports/` | Order crash reports |

---

## Templates

### BI Claim
- `2022 Whaley LOR to BI Adjuster.docx` - Letter of Rep to BI carrier

### PIP Claim
- `2022 Whaley LOR to PIP Adjuster.docx` - Letter of Rep to PIP carrier
- `KACP-Application-03.2021.pdf` - Kentucky PIP Application (universal template)

### Medical Records
- `2022 Whaley Medical Record Request (URR).docx` - Records request letter
- `2023 Whaley Law Firm Medical Request Template.pdf` - Alternative PDF version

---

## Next Phase

**→ Phase 2: Treatment**

The case advances to Treatment phase when landmarks are complete or soft blockers are consciously overridden with follow-up scheduled.
