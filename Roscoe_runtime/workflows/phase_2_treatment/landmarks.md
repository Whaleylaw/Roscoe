# Phase 2: Treatment - Landmarks

## Overview

Treatment phase landmarks focus on maintaining client contact, monitoring medical progress, and gathering documentation. Many landmarks in this phase are recurring or progressive rather than one-time achievements.

---

## Landmark Definitions

### L2.1: Client Check-In Schedule Active

**Description:** Bi-weekly client check-in schedule is established and maintained.

**Verification:**
```json
{
  "check_function": "check_client_contact_current",
  "checks": [
    "last_client_contact within 30 days",
    "next_check_in_scheduled is not null"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `client_check_in`
- Step: `schedule_next`

**Recurring:** Yes, every 14 days until demand sent

---

### L2.2: All Providers Have Records Requested

**Description:** Medical records have been requested from all known providers.

**Verification:**
```json
{
  "check_function": "check_records_requested",
  "checks": [
    "Every provider in medical_providers[] has records.requested_date populated"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `request_records_bills`
- Step: `send_request`

---

### L2.3: Records Received (Progressive)

**Description:** Medical records received from providers (tracked per provider).

**Verification:**
```json
{
  "check_function": "check_records_received_progress",
  "returns": {
    "total_providers": "count of medical_providers[]",
    "records_received": "count where records.received_date exists",
    "percentage": "records_received / total_providers * 100"
  }
}
```

**Typically Satisfied By:**
- Workflow: `request_records_bills`
- Step: `receive_records`

**Progressive:** This is not a binary landmark - track percentage completion.

---

### L2.4: Bills Received (Progressive)

**Description:** Medical bills received from providers (tracked per provider).

**Verification:**
```json
{
  "check_function": "check_bills_received_progress",
  "returns": {
    "total_providers": "count of medical_providers[]",
    "bills_received": "count where bills.received_date exists",
    "percentage": "bills_received / total_providers * 100"
  }
}
```

**Typically Satisfied By:**
- Workflow: `request_records_bills`
- Step: `receive_records`

---

### L2.5: Liens Identified

**Description:** All potential liens on the case have been identified and documented.

**Verification:**
```json
{
  "check_function": "check_liens_identified",
  "checks": [
    "Health insurance lien status documented",
    "Medicare status checked if applicable",
    "Medicaid status checked if applicable",
    "Provider liens documented if any"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `lien_identification` (parallel workflow)

---

### L2.6: Medical Chronology Started

**Description:** Initial medical chronology has been created and is being maintained.

**Verification:**
```json
{
  "check_function": "check_chronology_exists",
  "checks": [
    "medical_chronology file exists",
    "At least one entry from treatment records"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `request_records_bills`
- Trigger: After first records received

---

### L2.7: Treatment Status Known

**Description:** Current treatment status is documented for all providers.

**Verification:**
```json
{
  "check_function": "check_treatment_status_current",
  "checks": [
    "Every provider has status field (active/discharged/referred)",
    "Status updated within last 30 days"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `medical_provider_status`
- Workflow: `client_check_in` (updates during check-in)

---

### L2.8: Treatment Complete

**Description:** Client has completed treatment or reached Maximum Medical Improvement.

**Verification:**
```json
{
  "check_function": "check_treatment_complete",
  "checks": [
    "Client reported done treating",
    "OR all providers have status='discharged'",
    "OR client at MMI per physician"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `client_check_in`
- Workflow: `medical_provider_status`

**Triggers:** Phase exit to `demand_in_progress`

---

## Early Exit Landmarks

### L2.E1: Early Demand Conditions Met

**Description:** Conditions exist for early demand before treatment complete.

**Verification:**
```json
{
  "check_function": "check_early_demand_conditions",
  "checks": [
    "Policy limits are low (< $50k)",
    "Liability is clear (> 90% confidence)",
    "Injuries are significant (documented)"
  ]
}
```

**Triggers:** Can exit to `demand_in_progress` without L2.8

---

### L2.E2: SOL Critical

**Description:** Statute of limitations is approaching critical threshold.

**Verification:**
```json
{
  "check_function": "check_sol_critical",
  "checks": [
    "Days until SOL < 60",
    "Case not in litigation track"
  ]
}
```

**Triggers:** Must exit to `complaint` immediately

**CRITICAL:** This is a safety-critical landmark. If triggered, requires immediate attorney action.

---

## Landmark Progress Summary

| ID | Landmark | Type | Frequency |
|----|----------|------|-----------|
| L2.1 | Check-In Active | Recurring | Every 14 days |
| L2.2 | Records Requested | Per-provider | One-time per provider |
| L2.3 | Records Received | Progressive | Track percentage |
| L2.4 | Bills Received | Progressive | Track percentage |
| L2.5 | Liens Identified | One-time | During phase |
| L2.6 | Chronology Started | One-time | After first records |
| L2.7 | Treatment Status Known | Recurring | Track per check-in |
| L2.8 | Treatment Complete | Exit Trigger | End of phase |
| L2.E1 | Early Demand | Exit Trigger | If conditions met |
| L2.E2 | SOL Critical | Safety Exit | If < 60 days |

---

## Phase Advancement Criteria

**Normal Exit (to Demand):**
- ✅ L2.8 (Treatment Complete) OR L2.E1 (Early Demand Conditions)

**Emergency Exit (to Complaint):**
- ⚠️ L2.E2 (SOL Critical) - Requires immediate attorney decision

**Recommended Before Advancing:**
- L2.2 (All records requested)
- L2.3 (Records received > 80%)
- L2.4 (Bills received > 80%)
- L2.5 (Liens identified)
- L2.6 (Chronology started)

**Note:** Treatment phase can continue **in parallel** with litigation phases if suit is filed.

