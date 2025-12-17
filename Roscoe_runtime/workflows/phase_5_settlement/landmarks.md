# Phase 5: Settlement - Landmarks

## Overview

Settlement landmarks track the progression from settlement agreement through final distribution to the client. This phase has one hard blocker: the client must receive their funds.

---

## Landmark Definitions

### L5.1: Settlement Statement Prepared

**Description:** Settlement breakdown has been prepared showing all deductions and net to client.

**Verification:**
```json
{
  "check_function": "check_settlement_statement_prepared",
  "checks": [
    "Settlement statement document exists",
    "Gross settlement amount documented",
    "Attorney fee calculated",
    "Expenses itemized",
    "Liens listed",
    "Net to client calculated"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `prepare_settlement_statement`

---

### L5.2: Authorization to Settle Prepared

**Description:** Authorization to settle document has been prepared for client signature.

**Verification:**
```json
{
  "field_path": "documents.settlement_auth.prepared",
  "required_value": true
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `prepare_auth_to_settle`

---

### L5.3: Client Signed Authorization

**Description:** Client has signed the authorization to settle.

**Verification:**
```json
{
  "field_path": "documents.settlement_auth.status",
  "required_value": "signed"
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `client_signs_auth`

**User Action Required:** Yes - client must sign.

---

### L5.4: Settlement Confirmed with Adjuster

**Description:** Adjuster has been notified of acceptance and release requested.

**Verification:**
```json
{
  "field_path": "settlement.adjuster_notified_date",
  "required_value": "not null"
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `confirm_with_adjuster`

---

### L5.5: Release Received

**Description:** Insurance company's release document has been received.

**Verification:**
```json
{
  "field_path": "documents.release.received_date",
  "required_value": "not null"
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `receive_release`

---

### L5.6: Release Signed by Client

**Description:** Client has signed the insurance release.

**Verification:**
```json
{
  "field_path": "documents.release.status",
  "required_value": "signed"
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `client_signs_release`

**User Action Required:** Yes - client must sign.

---

### L5.7: Release Returned to Insurance

**Description:** Signed release has been sent back to insurance company.

**Verification:**
```json
{
  "field_path": "documents.release.returned_date",
  "required_value": "not null"
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `return_release`

---

### L5.8: Settlement Check Received

**Description:** Settlement check has been received from insurance.

**Verification:**
```json
{
  "field_path": "settlement.check_received_date",
  "required_value": "not null"
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `receive_check`

---

### L5.9: Check Deposited and Cleared

**Description:** Settlement check has been deposited to trust account and cleared.

**Verification:**
```json
{
  "check_function": "check_settlement_check_cleared",
  "checks": [
    "settlement.check_deposited_date exists",
    "settlement.check_cleared_date exists OR 10 business days passed"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `receive_check` (deposit portion)

---

### L5.10: Liens Paid

**Description:** All liens have been paid from settlement proceeds.

**Verification:**
```json
{
  "check_function": "check_liens_paid",
  "checks": [
    "Every lien has payment_date populated",
    "OR lien marked as disputed (goes to Lien Phase)"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `pay_liens`

**Alternative Path:** If liens cannot be resolved, case moves to Lien Phase.

---

### L5.11: Client Received Funds ⭐ HARD BLOCKER

**Description:** Client has received their distribution check.

**Verification:**
```json
{
  "check_function": "check_client_paid",
  "checks": [
    "settlement.client_check_issued_date exists",
    "settlement.client_received_date exists OR check mailed"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `settlement_processing`
- Step: `distribute_funds`

**Triggers:** Phase exit to `closed` (if all liens resolved) or `lien_phase` (if liens outstanding).

---

## Landmark Progress Summary

| ID | Landmark | Type | Workflow Source |
|----|----------|------|-----------------|
| L5.1 | Statement Prepared | Progress | settlement_processing |
| L5.2 | Auth Prepared | Progress | settlement_processing |
| L5.3 | Auth Signed | Gate | settlement_processing |
| L5.4 | Adjuster Notified | Progress | settlement_processing |
| L5.5 | Release Received | Progress | settlement_processing |
| L5.6 | Release Signed | Gate | settlement_processing |
| L5.7 | Release Returned | Progress | settlement_processing |
| L5.8 | Check Received | Progress | settlement_processing |
| L5.9 | Check Cleared | Gate | settlement_processing |
| L5.10 | Liens Paid | Conditional | settlement_processing |
| L5.11 | Client Paid | Hard Blocker | settlement_processing |

---

## Phase Advancement Criteria

**Required to Advance to Closed:**
- ✅ L5.11 (Client Received Funds)
- ✅ L5.10 (All Liens Paid)

**Alternative Path to Lien Phase:**
- ✅ L5.11 (Client Received Funds) - partial distribution
- ❌ L5.10 (Liens NOT resolved) - disputed amounts held in trust

**Sequential Gates:**
- L5.3 (Auth Signed) must precede L5.4 (Adjuster Notified)
- L5.6 (Release Signed) must precede L5.7 (Release Returned)
- L5.9 (Check Cleared) must precede L5.10/L5.11 (Distribution)

