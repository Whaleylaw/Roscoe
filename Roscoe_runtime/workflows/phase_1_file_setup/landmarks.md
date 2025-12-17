# Phase 1: File Setup - Landmarks

## Overview

Phase 1 landmarks track case setup progress after Phase 0 completion. Since contract, HIPAA, and initial client info are already complete from Phase 0, these landmarks focus on:

1. Completing detailed intake information
2. Obtaining the accident report
3. Setting up insurance claims (BI and PIP)
4. Setting up medical providers with records requests

**All landmarks are soft blockers** - they can be overridden with acknowledgment but should be completed before advancing to Phase 2.

---

## Landmark Summary

| # | Landmark ID | Name | Mandatory |
|---|-------------|------|:---------:|
| 1 | `full_intake_complete` | Full Intake Complete | Soft |
| 2 | `accident_report_obtained` | Accident Report Obtained | Soft |
| 3 | `insurance_claims_setup` | Insurance Claims Set Up | Soft |
| 4 | `providers_setup` | Providers Set Up | Soft |

---

## Landmark 1: Full Intake Complete

**Description:** Complete client and case information has been collected beyond Phase 0 basics.

**Verification:**
- [ ] Full client demographics captured
- [ ] Complete incident details documented
- [ ] All injuries and treatment to date recorded
- [ ] Employment information (if wage loss claim)
- [ ] All involved parties documented

**Data Fields:**
```json
{
  "intake": {
    "completed": true,
    "date": "2024-12-06",
    "demographics_complete": true,
    "incident_details_complete": true,
    "injuries_documented": true,
    "employment_info": true,
    "parties_documented": true
  }
}
```

---

## Landmark 2: Accident Report Obtained

**Description:** Police/accident report has been requested, received, and analyzed.

**Verification:**
- [ ] Report requested (if not already in possession)
- [ ] Report received
- [ ] Report analyzed for parties and insurance
- [ ] Liability indicators documented

**Data Fields:**
```json
{
  "accident_report": {
    "requested_date": "2024-12-01",
    "received_date": "2024-12-05",
    "report_number": "KSP-2024-123456",
    "analyzed": true,
    "liability_assessment": "At-fault driver cited for following too closely"
  }
}
```

**Note:** For non-MVA cases (slip/fall, etc.), this landmark may be N/A or replaced with incident report.

---

## Landmark 3: Insurance Claims Set Up

**Description:** All applicable insurance claims have been opened with acknowledgment.

This landmark has **sub-components** for BI and PIP claims.

### BI (Bodily Injury) Sub-Landmarks

| Step | Sub-Landmark | Verification Field |
|------|--------------|-------------------|
| 3a | At-fault insurance identified | `bi.insurance_company.name` populated |
| 3b | LOR sent | `bi.date_lor_sent` populated |
| 3c | Claim acknowledged | `bi.claim_acknowledged == true` |
| 3d | Liability status obtained | `bi.liability_status` populated |
| 3e | Coverage confirmed | `bi.policy_limits_disclosed == true` |

**Liability Status Values:**
- `accepted` - Carrier accepts 100% liability
- `denied` - Carrier denies liability
- `partial` - Comparative fault (e.g., 80/20)
- `investigating` - Still determining fault

**FLAG FOR USER:** If `liability_status` is anything other than `accepted`, flag user for potential additional BI claims (especially for passengers where multiple vehicles may be liable).

**BI Data Fields:**
```json
{
  "insurance": {
    "bi": {
      "insurance_company": {
        "name": "State Farm",
        "phone": "800-555-1234",
        "address": "123 Insurance Way"
      },
      "insured_name": "John At-Fault",
      "claim_number": "BI-2024-123456",
      "date_claim_opened": "2024-12-02",
      "date_lor_sent": "2024-12-02",
      "claim_acknowledged": true,
      "date_claim_acknowledged": "2024-12-05",
      "adjuster_name": "Jane Adjuster",
      "adjuster_phone": "800-555-5678",
      "adjuster_email": "jane.adjuster@statefarm.com",
      "liability_status": "accepted",
      "liability_percentage": 100,
      "date_liability_determined": "2024-12-10",
      "policy_limits_disclosed": true,
      "coverage_limit_per_person": 25000,
      "coverage_limit_per_accident": 50000,
      "date_policy_limits_received": "2024-12-15"
    }
  }
}
```

### PIP (Personal Injury Protection) Sub-Landmarks

| Step | Sub-Landmark | Verification Field |
|------|--------------|-------------------|
| 3f | PIP carrier determined | `pip.pip_insurer` populated |
| 3g | PIP Application submitted | `pip.date_pip_application_sent` populated |
| 3h | LOR sent | `pip.date_lor_sent` populated |
| 3i | Claim acknowledged | `pip.claim_acknowledged == true` |
| 3j | Ready to pay bills | `pip.ready_to_pay_bills == true` |

**PIP Waterfall Determination:**
1. Client on title of insured vehicle → vehicle's insurer
2. Vehicle occupied was insured → vehicle's insurer
3. Client has own auto insurance → client's insurer
4. Household member has insurance → household insurer
5. None of above → Kentucky Assigned Claims (KAC)

**CRITICAL:** If client owns an UNINSURED vehicle they were occupying → **DISQUALIFIED from PIP**

**PIP Application:** The KACP (Kentucky Assigned Claims Plan) application is ALWAYS required, regardless of which carrier provides PIP coverage. All insurers accept this form.

**PIP Data Fields:**
```json
{
  "insurance": {
    "pip": {
      "pip_insurer": "GEICO",
      "pip_insurer_type": "vehicle",
      "waterfall_step": 2,
      "is_kac": false,
      "is_disqualified": false,
      "insurance_company": {
        "name": "GEICO",
        "phone": "800-555-4321"
      },
      "policy_number": "PIP-2024-789",
      "claim_number": "PIP-2024-456789",
      "date_pip_application_sent": "2024-12-02",
      "date_claim_opened": "2024-12-02",
      "date_lor_sent": "2024-12-02",
      "claim_acknowledged": true,
      "date_claim_acknowledged": "2024-12-04",
      "adjuster_name": "Bob PIP-Adjuster",
      "adjuster_phone": "800-555-9999",
      "coverage_limit": 10000,
      "ready_to_pay_bills": true,
      "date_verified_payment_ready": "2024-12-06"
    }
  }
}
```

---

## Landmark 4: Providers Set Up

**Description:** All known medical providers have been added to the case file, and records have been requested for providers with completed treatment.

**Verification:**
- [ ] All treating providers identified and added
- [ ] Provider contact information verified
- [ ] For completed treatment (EMS, ER): Records request sent with HIPAA
- [ ] Follow-up scheduled for records receipt

**Auto-Request Logic:**
When a provider with `treatment_status: "completed"` is added, the system automatically:
1. Generates a medical records request letter
2. Attaches the signed HIPAA from Phase 0
3. Sends the request (or queues for user review)
4. Schedules a 14-day follow-up

**Data Fields:**
```json
{
  "providers": {
    "setup_complete": true,
    "provider_count": 3,
    "providers": [
      {
        "provider_name": "Louisville EMS",
        "provider_type": "EMS",
        "treatment_status": "completed",
        "records_requested": true,
        "records_request_date": "2024-12-06",
        "records_received": false
      },
      {
        "provider_name": "University Hospital ER",
        "provider_type": "Hospital",
        "treatment_status": "completed",
        "records_requested": true,
        "records_request_date": "2024-12-06",
        "records_received": false
      },
      {
        "provider_name": "Dr. Smith Orthopedics",
        "provider_type": "Specialist",
        "treatment_status": "ongoing",
        "records_requested": false
      }
    ]
  }
}
```

---

## Landmark Verification Flow

```
FROM PHASE 0
(Contract, HIPAA, Client Info complete)
     │
     ▼
┌─────────────────┐
│ Landmark 1:     │
│ Full Intake     │
└────────┬────────┘
         │
    ┌────┴────────────────────┐
    │                         │
    ▼                         ▼
┌─────────────────┐   ┌─────────────────┐
│ Landmark 2:     │   │ Landmark 3:     │
│ Accident Report │   │ Insurance Setup │
└────────┬────────┘   └────────┬────────┘
         │                     │
         │            ┌────────┴────────┐
         │            │                 │
         │            ▼                 ▼
         │      ┌──────────┐     ┌──────────┐
         │      │ BI Claim │     │PIP Claim │
         │      │ Steps    │     │ Steps    │
         │      │ 3a-3e    │     │ 3f-3j    │
         │      └────┬─────┘     └────┬─────┘
         │           │                │
         │           │  ┌─────────────┘
         │           │  │
         │           ▼  ▼
         │      ┌──────────────┐
         │      │ Liability    │
         │      │ <100%?       │
         │      │ → FLAG USER  │
         │      └──────────────┘
         │
         └───────────────┬───────────────
                         │
                         ▼
              ┌─────────────────┐
              │ Landmark 4:     │
              │ Providers Setup │
              │ → AUTO records  │
              │   request       │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ ALL COMPLETE?   │
              └────────┬────────┘
                       │ Yes
                       ▼
              ┌─────────────────┐
              │ Phase 2:        │
              │ Treatment       │
              └─────────────────┘
```

---

## Phase Advancement

**Criteria for advancing to Phase 2 (Treatment):**

**Recommended Complete:**
- Landmark 1: Full Intake Complete
- Landmark 2: Accident Report Obtained
- Landmark 3: Insurance Claims Set Up (BI and PIP)
- Landmark 4: Providers Set Up

**Override Allowed:** All landmarks are soft blockers. They can be overridden with acknowledgment that certain tasks are incomplete and will be flagged for follow-up.

---

## Soft Blocker Override

If advancing without completing all landmarks:

```json
{
  "phase_advancement": {
    "from": "file_setup",
    "to": "treatment",
    "date": "2024-12-10",
    "landmarks_complete": ["full_intake_complete", "providers_setup"],
    "landmarks_overridden": [
      {
        "landmark": "accident_report_obtained",
        "reason": "Report not yet available from KSP, follow-up calendared",
        "follow_up_date": "2024-12-20"
      },
      {
        "landmark": "insurance_claims_setup",
        "sub_landmark": "bi_liability_status",
        "reason": "BI carrier still investigating liability",
        "follow_up_date": "2024-12-24"
      }
    ],
    "approved_by": "user"
  }
}
```
