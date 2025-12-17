# Phase 4: Negotiation - Landmarks

## Overview

Negotiation landmarks track the progression of settlement discussions from initial follow-up through final resolution. This phase exits based on completion conditions (settlement or impasse) rather than hard blockers.

---

## Landmark Definitions

### L4.1: One-Week Follow-Up Completed

**Description:** Follow-up conducted one week after demand to confirm receipt.

**Verification:**
```json
{
  "check_function": "check_one_week_followup",
  "checks": [
    "Follow-up contact made ~7 days after demand sent",
    "Receipt confirmed or documented attempt"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `negotiate_claim`
- Automatic calendar trigger from `send_demand`

---

### L4.2: Deficiencies Addressed

**Description:** Any deficiencies or information requests from insurance have been addressed.

**Verification:**
```json
{
  "check_function": "check_deficiencies_addressed",
  "checks": [
    "No pending information requests",
    "All adjuster questions answered"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `negotiate_claim`
- Step: Response to information requests

---

### L4.3: Thirty-Day Follow-Up Completed

**Description:** Follow-up conducted 30 days after demand if no response.

**Verification:**
```json
{
  "condition": "no_response_received",
  "check_function": "check_thirty_day_followup",
  "checks": [
    "Follow-up contact made ~30 days after demand",
    "Response received OR escalation documented"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `negotiate_claim`
- Automatic calendar trigger from `send_demand`

---

### L4.4: Initial Offer Received

**Description:** Insurance company has made an initial offer.

**Verification:**
```json
{
  "check_function": "check_initial_offer_received",
  "checks": [
    "At least one offer recorded in insurance_claims[].offers[]",
    "Offer has date and amount"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `negotiate_claim`
- Step: `receive_response`, `document_offer`

---

### L4.5: Net to Client Calculated

**Description:** Net to client has been calculated for current offer.

**Verification:**
```json
{
  "check_function": "check_net_calculated",
  "checks": [
    "Current offer has net_to_client calculation",
    "Calculation includes fees, expenses, liens"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `negotiate_claim`
- Step: `calculate_net`

---

### L4.6: Offer Evaluated by Attorney

**Description:** Attorney has evaluated the current offer and provided recommendation.

**Verification:**
```json
{
  "check_function": "check_offer_evaluated",
  "checks": [
    "Current offer has attorney_recommendation field",
    "Recommendation is accept/counter/reject"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `negotiate_claim`
- Step: `evaluate_offer`

---

### L4.7: Client Authorized Decision

**Description:** Client has been informed and authorized the response to offer.

**Verification:**
```json
{
  "check_function": "check_client_authorized",
  "checks": [
    "Client contact documented regarding offer",
    "Client decision recorded (accept/counter/reject)"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `negotiate_claim`
- Step: `communicate_with_client`

---

### L4.8: Iterative Negotiation Documented

**Description:** All rounds of negotiation are documented with offers/counters.

**Verification:**
```json
{
  "check_function": "check_negotiation_documented",
  "checks": [
    "All offers recorded with dates and amounts",
    "All counters recorded with dates and amounts",
    "Negotiation notes current"
  ]
}
```

**Typically Satisfied By:**
- Workflow: `track_offers`

---

### L4.9: Settlement Reached (Exit Condition)

**Description:** Settlement agreement reached with insurance.

**Verification:**
```json
{
  "check_function": "check_settlement_reached",
  "checks": [
    "Final offer accepted by client",
    "Settlement amount documented",
    "All parties agreed"
  ]
}
```

**Triggers:** Phase exit to `settlement`

---

### L4.10: Negotiation Impasse (Exit Condition)

**Description:** Impasse reached - proceeding to litigation or closing.

**Verification:**
```json
{
  "check_function": "check_negotiation_impasse",
  "checks": [
    "Final offer rejected OR liability denied",
    "Client decision on next steps documented",
    "Impasse reason documented"
  ]
}
```

**Triggers:** Phase exit to `complaint` or `treatment` based on client decision.

---

## Landmark Progress Summary

| ID | Landmark | Type | Workflow Source |
|----|----------|------|-----------------|
| L4.1 | One-Week Follow-Up | Progress | negotiate_claim |
| L4.2 | Deficiencies Addressed | Progress | negotiate_claim |
| L4.3 | Thirty-Day Follow-Up | Progress | negotiate_claim |
| L4.4 | Initial Offer Received | Progress | negotiate_claim |
| L4.5 | Net Calculated | Progress | negotiate_claim |
| L4.6 | Attorney Evaluated | Gate | negotiate_claim |
| L4.7 | Client Authorized | Gate | negotiate_claim |
| L4.8 | Negotiation Documented | Ongoing | track_offers |
| L4.9 | Settlement Reached | Exit Condition | negotiate_claim |
| L4.10 | Impasse Reached | Exit Condition | negotiate_claim |

---

## Phase Advancement Criteria

**Exit to Settlement:**
- ✅ L4.9 (Settlement Reached)

**Exit to Complaint (Litigation):**
- ✅ L4.10 (Impasse Reached) + Client decision to litigate

**Exit to Treatment (Return):**
- ✅ L4.10 (Impasse Reached) + Client needs more treatment

**Note:** One of L4.9 or L4.10 must be satisfied to exit this phase.

