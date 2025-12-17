# Phase 3: Demand in Progress - Landmarks

## Overview

Demand phase landmarks track the assembly of the demand package from materials gathering through attorney approval and sending. The phase has one hard blocker: the demand must be sent before advancing.

---

## Landmark Definitions

### L3.1: All Records Received

**Description:** Medical records have been received from all providers.

**Verification:**
```json
{
  "check_function": "check_all_records_received",
  "checks": [
    "Every provider in medical_providers[] has records.received_date populated"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `gather_demand_materials`
- Step: `verify_all_records`

**Override Available:** Yes - can proceed without all records if attorney approves.

---

### L3.2: All Bills Received

**Description:** Medical bills have been received from all providers.

**Verification:**
```json
{
  "check_function": "check_all_bills_received",
  "checks": [
    "Every provider in medical_providers[] has bills.received_date populated"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `gather_demand_materials`
- Step: `verify_all_bills`

**Override Available:** Yes - may undervalue case.

---

### L3.3: Special Damages Calculated

**Description:** Total special damages have been calculated and documented.

**Verification:**
```json
{
  "field_path": "financials.total_medical_bills",
  "required_value": "greater than 0"
}
```

**Typically Satisfied By:**
- Workflow: `gather_demand_materials`
- Step: `calculate_specials`

---

### L3.4: Medical Chronology Finalized

**Description:** Medical chronology is complete and ready for demand.

**Verification:**
```json
{
  "check_function": "check_chronology_complete",
  "checks": [
    "medical_chronology file exists",
    "All providers represented",
    "Chronology marked as finalized"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `gather_demand_materials`
- Step: `complete_chronology`

---

### L3.5: Liens Identified

**Description:** All liens have been identified with conditional amounts requested.

**Verification:**
```json
{
  "check_function": "check_liens_identified",
  "checks": [
    "liens array populated",
    "Each lien has conditional_amount_requested_date OR not_applicable_reason"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `gather_demand_materials`
- Step: `identify_liens`

**Override Available:** Yes - may have surprise liens at settlement.

---

### L3.6: Wage Loss Documented (if applicable)

**Description:** Lost wages are documented with supporting evidence.

**Verification:**
```json
{
  "condition": "client.employer.missed_work == true",
  "check_function": "check_wage_loss_documented",
  "checks": [
    "Off-work notes present",
    "Pay stubs or income verification present",
    "Lost wages amount calculated"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `gather_demand_materials`
- Step: `collect_wage_loss`

---

### L3.7: Demand Draft Prepared

**Description:** Initial demand letter draft has been created.

**Verification:**
```json
{
  "field_path": "documents.demand_letter.draft_path",
  "required_value": "not null"
}
```

**Typically Satisfied By:**
- Workflow: `draft_demand`
- Step: `prepare_draft`

---

### L3.8: Exhibits Compiled

**Description:** All supporting exhibits have been compiled for the demand package.

**Verification:**
```json
{
  "check_function": "check_exhibits_compiled",
  "checks": [
    "Medical records attached",
    "Medical bills attached",
    "Medical chronology attached",
    "Accident report attached (if exists)",
    "Photos attached (if exist)"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `draft_demand`
- Step: `attach_exhibits`

---

### L3.9: Attorney Approved

**Description:** Attorney has reviewed and approved the demand letter.

**Verification:**
```json
{
  "field_path": "documents.demand_letter.attorney_approved",
  "required_value": true
}
```

**Typically Satisfied By:**
- Workflow: `draft_demand`
- Step: `attorney_review`

**User Action Required:** Yes - attorney must approve.

---

### L3.10: Demand Sent ⭐ HARD BLOCKER

**Description:** Demand letter and package sent to all BI adjusters.

**Verification:**
```json
{
  "check_function": "check_demand_sent_all_bi",
  "checks": [
    "Every BI claim has demand_sent_date populated",
    "documents.demand_letter.status == 'sent'"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `send_demand`
- Step: `send_demand`

**Triggers:** Phase exit to `negotiation`

---

### L3.11: Client Notified

**Description:** Client has been notified that demand was sent.

**Verification:**
```json
{
  "field_path": "demand_client_notification_date",
  "required_value": "not null"
}
```

**Typically Satisfied By:**
- Workflow: `send_demand`
- Step: `notify_client`

---

### L3.12: Follow-Up Scheduled

**Description:** 30-day follow-up has been scheduled for demand response.

**Verification:**
```json
{
  "check_function": "check_follow_up_scheduled",
  "checks": [
    "Calendar event exists for demand follow-up",
    "Event date is ~30 days after demand sent"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `send_demand`
- Step: `set_follow_up`

---

## Landmark Progress Summary

| ID | Landmark | Type | Workflow Source |
|----|----------|------|-----------------|
| L3.1 | Records Received | Soft Blocker | gather_demand_materials |
| L3.2 | Bills Received | Soft Blocker | gather_demand_materials |
| L3.3 | Specials Calculated | Progress | gather_demand_materials |
| L3.4 | Chronology Finalized | Progress | gather_demand_materials |
| L3.5 | Liens Identified | Soft Blocker | gather_demand_materials |
| L3.6 | Wage Loss Documented | Conditional | gather_demand_materials |
| L3.7 | Draft Prepared | Progress | draft_demand |
| L3.8 | Exhibits Compiled | Progress | draft_demand |
| L3.9 | Attorney Approved | Gate | draft_demand |
| L3.10 | Demand Sent | Hard Blocker | send_demand |
| L3.11 | Client Notified | Progress | send_demand |
| L3.12 | Follow-Up Scheduled | Progress | send_demand |

---

## Phase Advancement Criteria

**Required to Advance:**
- ✅ L3.10 (Demand Sent) - No exceptions

**Recommended Before Advancing:**
- L3.1 (All records received)
- L3.2 (All bills received)
- L3.5 (Liens identified)
- L3.11 (Client notified)
- L3.12 (Follow-up scheduled)

**Quality Gates:**
- L3.9 (Attorney approved) must be completed before L3.10

