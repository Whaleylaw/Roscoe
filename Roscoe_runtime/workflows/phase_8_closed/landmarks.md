# Phase 8: Closed / Archived - Landmarks

## Overview

Closed phase landmarks track the final tasks of case closure and archival. This is a terminal phase with no advancement criteria.

---

## Landmark Definitions

### L8.1: All Obligations Verified

**Description:** All financial and legal obligations verified complete.

**Verification:**
```json
{
  "check_function": "check_all_obligations_complete",
  "checks": [
    "All settlement funds distributed",
    "All liens paid",
    "Client received funds",
    "Trust account balance is zero",
    "All releases executed"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `close_case`
- Step: `verify_complete`

---

### L8.2: Final Letter Sent

**Description:** Final closing letter sent to client.

**Verification:**
```json
{
  "field_path": "closure.final_letter_sent_date",
  "required_value": "not null"
}
```

**Typically Satisfied By:**
- Workflow: `close_case`
- Step: `send_final_letter`

---

### L8.3: Review Requested (if applicable)

**Description:** Google review requested from satisfied client.

**Verification:**
```json
{
  "condition": "good_outcome AND good_relationship",
  "field_path": "closure.review_requested_date",
  "required_value": "not null OR not_applicable"
}
```

**Typically Satisfied By:**
- Workflow: `close_case`
- Step: `request_review`

---

### L8.4: Physical File Archived

**Description:** Physical file organized and archived.

**Verification:**
```json
{
  "check_function": "check_physical_archive",
  "checks": [
    "Physical file compiled",
    "Stored in archive location",
    "Archive log updated"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `close_case`
- Step: `archive_file`

---

### L8.5: Digital File Archived

**Description:** Digital file backed up and archived.

**Verification:**
```json
{
  "check_function": "check_digital_archive",
  "checks": [
    "All digital documents saved",
    "Backup completed",
    "Case marked archived in system"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `close_case`
- Step: `archive_file`

---

### L8.6: Case Fully Closed

**Description:** Case is fully closed and archived.

**Verification:**
```json
{
  "check_function": "check_case_fully_closed",
  "checks": [
    "L8.1 complete",
    "L8.2 complete",
    "L8.4 complete",
    "L8.5 complete",
    "case_state.status = 'closed'"
  ]
}
```

**Typically Satisfied By:**
- Completion of all other landmarks

---

## Landmark Progress Summary

| ID | Landmark | Type | Workflow Source |
|----|----------|------|-----------------|
| L8.1 | Obligations Verified | Progress | close_case |
| L8.2 | Final Letter Sent | Progress | close_case |
| L8.3 | Review Requested | Conditional | close_case |
| L8.4 | Physical Archive | Progress | close_case |
| L8.5 | Digital Archive | Progress | close_case |
| L8.6 | Fully Closed | Completion | close_case |

---

## Phase Completion Criteria

**Case Considered Fully Closed When:**
- ✅ L8.1 (All obligations verified)
- ✅ L8.2 (Final letter sent)
- ✅ L8.4 (Physical file archived)
- ✅ L8.5 (Digital file archived)

**Note:** This is a terminal phase - there is no advancement to another phase.

---

## Reopening Criteria

**Can Reopen:**
- New related matter from client
- Additional insurance coverage discovered
- Appeal or post-judgment matter

**Cannot Reopen:**
- Settlement fully completed
- Judgment satisfied

**To Reopen:**
- Create new case linked to original
- Reference original case number
- Import relevant documents from archive
