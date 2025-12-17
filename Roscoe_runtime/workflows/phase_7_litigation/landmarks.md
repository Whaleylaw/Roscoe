# Phase 7: Litigation - Landmarks

## Overview

Litigation landmarks track progress through the formal legal process. Because litigation contains sub-phases, landmarks are organized hierarchically:
- **Phase-level landmarks**: Major milestones spanning all sub-phases
- **Sub-phase landmarks**: Detailed progress within each sub-phase

---

## Phase-Level Landmarks

### L7.0: Litigation Commenced

**Description:** Decision made to proceed with litigation.

**Verification:**
```json
{
  "check_function": "check_litigation_commenced",
  "checks": [
    "litigation_decision_date populated",
    "case_state.track = 'litigation'"
  ]
}
```

---

### L7.1: Complaint Filed ⭐ HARD BLOCKER

**Description:** Complaint filed with court.

**Verification:**
```json
{
  "check_function": "check_complaint_filed",
  "checks": [
    "complaint_file_date populated",
    "case_number assigned",
    "filing receipt obtained"
  ]
}
```

**Sub-Phase:** 7.1 Complaint

---

### L7.2: Defendant Served

**Description:** All defendants properly served.

**Verification:**
```json
{
  "check_function": "check_all_served",
  "checks": [
    "Each defendant has service_date",
    "Proof of service filed"
  ]
}
```

**Sub-Phase:** 7.1 Complaint

---

### L7.3: Answer/Response Received

**Description:** Defendant's response to complaint received.

**Verification:**
```json
{
  "check_function": "check_answer_received",
  "checks": [
    "answer_date OR default_date populated"
  ]
}
```

**Sub-Phase:** 7.1 Complaint

---

### L7.4: Scheduling Order Entered

**Description:** Court issues scheduling order with deadlines.

**Verification:**
```json
{
  "check_function": "check_scheduling_order",
  "checks": [
    "scheduling_order_date populated",
    "All deadlines calendared"
  ]
}
```

**Sub-Phase:** 7.2 Discovery (entry)

---

### L7.5: Written Discovery Complete

**Description:** All written discovery exchanged.

**Verification:**
```json
{
  "check_function": "check_written_discovery_complete",
  "checks": [
    "Our discovery propounded and responses received",
    "Their discovery responded to"
  ]
}
```

**Sub-Phase:** 7.2 Discovery

---

### L7.6: Depositions Complete

**Description:** All necessary depositions taken.

**Verification:**
```json
{
  "check_function": "check_depositions_complete",
  "checks": [
    "All party depositions completed",
    "Key witness depositions completed",
    "Expert depositions completed (if applicable)"
  ]
}
```

**Sub-Phase:** 7.2 Discovery

---

### L7.7: Mediation Attended

**Description:** Court-ordered mediation conducted.

**Verification:**
```json
{
  "check_function": "check_mediation_complete",
  "checks": [
    "mediation_date populated",
    "mediation_outcome documented"
  ]
}
```

**Sub-Phase:** 7.3 Mediation

---

### L7.8: Expert Disclosures Filed

**Description:** Expert witness disclosures filed per scheduling order.

**Verification:**
```json
{
  "check_function": "check_expert_disclosure",
  "checks": [
    "Our expert disclosures filed by deadline",
    "Defense expert disclosures received"
  ]
}
```

**Sub-Phase:** 7.4 Trial Prep

---

### L7.9: Trial Ready ⭐ HARD BLOCKER

**Description:** All trial preparation complete.

**Verification:**
```json
{
  "check_function": "check_trial_ready",
  "checks": [
    "Exhibit list filed",
    "Witness list filed",
    "Pretrial brief filed",
    "Jury instructions submitted"
  ]
}
```

**Sub-Phase:** 7.4 Trial Prep

---

### L7.10: Trial Concluded ⭐ HARD BLOCKER

**Description:** Trial completed with verdict or other resolution.

**Verification:**
```json
{
  "check_function": "check_trial_complete",
  "checks": [
    "trial_end_date populated",
    "verdict OR settlement OR other_disposition documented"
  ]
}
```

**Sub-Phase:** 7.5 Trial

---

## Landmark Summary by Sub-Phase

| Sub-Phase | Landmarks | Hard Blockers |
|-----------|-----------|---------------|
| 7.1 Complaint | L7.1, L7.2, L7.3 | L7.1 (Complaint Filed) |
| 7.2 Discovery | L7.4, L7.5, L7.6 | None |
| 7.3 Mediation | L7.7 | None |
| 7.4 Trial Prep | L7.8, L7.9 | L7.9 (Trial Ready) |
| 7.5 Trial | L7.10 | L7.10 (Trial Concluded) |

---

## Phase Exit Requirements

**To exit to Settlement (Phase 5):**
- Settlement reached at any point
- Settlement documents executed

**To exit to Closed (Phase 8):**
- L7.10 (Trial Concluded) with verdict
- OR Case dismissed
- OR Voluntary dismissal

---

## Critical Timeline Considerations

### Statute of Limitations
- L7.1 (Complaint Filed) MUST occur before SOL expires
- Kentucky personal injury: 1 year from accident (KRS 304.39-230 for MVA)
- Kentucky general negligence: 1 year (KRS 413.140)

### Discovery Deadlines
- All discovery must complete by cutoff in scheduling order
- Late discovery = excluded evidence

### Expert Deadlines
- Disclosure deadlines are firm
- Missing deadline = expert excluded

### Trial Continuances
- Limited grounds for continuance
- Failure to be ready = possible sanctions or dismissal

