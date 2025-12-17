# Offer Tracking Fields Reference

## Overview

This reference provides the complete specification for all fields used in offer tracking, including required fields, optional fields, and valid values.

---

## Per-Offer Entry Fields

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `date` | string | Date of offer/counter (YYYY-MM-DD) | "2024-06-15" |
| `round` | integer | Negotiation round number | 2 |
| `type` | string | Entry type (see values below) | "revised_offer" |
| `from` | string | Who made entry | "insurance" or "plaintiff" |
| `amount` | number | Dollar amount | 35000 |
| `status` | string | Current status (see values below) | "pending" |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `conditions` | string | Any conditions attached | "Release all parties" |
| `adjuster_notes` | string | Adjuster's stated reasoning | "Liability disputed" |
| `reasoning` | string | Our justification (for counters) | "Based on comparable verdicts" |
| `deadline` | string | Response deadline (YYYY-MM-DD) | "2024-07-15" |
| `response_to` | string | ID of offer this responds to | "offer_001" |
| `communication_method` | string | How communicated | "email", "phone", "letter" |
| `contact_person` | string | Who communicated | "Jane Smith, Adjuster" |

---

## Field Value Specifications

### Entry Types (`type`)

| Value | Description | From |
|-------|-------------|------|
| `initial_offer` | Insurance's first offer | insurance |
| `revised_offer` | Subsequent insurance offers | insurance |
| `counter` | Plaintiff's counter-offer | plaintiff |
| `final_offer` | Stated as final by either party | either |
| `acceptance` | Acceptance of current offer | either |
| `rejection` | Rejection of current offer | either |

### Status Values (`status`)

| Value | Description | Transitions To |
|-------|-------------|----------------|
| `pending` | Awaiting response | under_review, countered, accepted, rejected, expired |
| `under_review` | Being evaluated | countered, accepted, rejected |
| `countered` | Counter was sent | responded |
| `responded` | Response received | (terminal for this entry) |
| `accepted` | Offer accepted | (terminal) |
| `rejected` | Offer rejected | (terminal) |
| `expired` | Deadline passed | (terminal) |

### From Values (`from`)

| Value | Description |
|-------|-------------|
| `insurance` | Entry from insurance company/adjuster |
| `plaintiff` | Entry from our firm/client |

---

## Claim-Level Tracking Fields

### Per-Claim Summary Fields

| Field | Type | Description |
|-------|------|-------------|
| `demand_sent_date` | string | Date demand letter sent |
| `demand_amount` | number | Amount demanded |
| `negotiation_status` | string | Overall claim status |
| `offers` | array | Array of offer entries |

### Negotiation Status Values (`negotiation_status`)

| Value | Description |
|-------|-------------|
| `not_started` | Demand sent, no response yet |
| `active` | Negotiation in progress |
| `settled` | Settlement reached |
| `impasse` | Negotiation failed |
| `litigation` | Moved to lawsuit |

---

## Calculated Metrics

### Track These Metrics

| Metric | Calculation | Purpose |
|--------|-------------|---------|
| `gap` | Our position - Their position | Progress indicator |
| `movement_them` | Current offer - Previous offer | Their movement |
| `movement_us` | Previous counter - Current counter | Our movement |
| `days_negotiating` | Today - Demand sent date | Timeline |
| `total_rounds` | Max round number | Progress |
| `offer_vs_limits` | Current offer / Policy limits × 100 | Value indicator |
| `offer_vs_demand` | Current offer / Demand × 100 | Progress indicator |

---

## JSON Schema

### Complete Offer Entry Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["date", "round", "type", "from", "amount", "status"],
  "properties": {
    "date": {
      "type": "string",
      "format": "date",
      "description": "Date of offer (YYYY-MM-DD)"
    },
    "round": {
      "type": "integer",
      "minimum": 1,
      "description": "Negotiation round number"
    },
    "type": {
      "type": "string",
      "enum": ["initial_offer", "revised_offer", "counter", "final_offer", "acceptance", "rejection"],
      "description": "Type of entry"
    },
    "from": {
      "type": "string",
      "enum": ["insurance", "plaintiff"],
      "description": "Who made this entry"
    },
    "amount": {
      "type": "number",
      "minimum": 0,
      "description": "Dollar amount"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "under_review", "countered", "responded", "accepted", "rejected", "expired"],
      "description": "Current status"
    },
    "conditions": {
      "type": "string",
      "description": "Any conditions attached"
    },
    "adjuster_notes": {
      "type": "string",
      "description": "Adjuster's stated reasoning"
    },
    "reasoning": {
      "type": "string",
      "description": "Our justification for counter"
    },
    "deadline": {
      "type": "string",
      "format": "date",
      "description": "Response deadline"
    },
    "communication_method": {
      "type": "string",
      "enum": ["email", "phone", "letter", "in_person"],
      "description": "How offer was communicated"
    }
  }
}
```

---

## Example Complete Tracking Record

```json
{
  "claims": [
    {
      "id": "bi_001",
      "type": "BI",
      "carrier": "State Farm",
      "claim_number": "SF-2024-123456",
      "policy_limits": 100000,
      "demand_sent_date": "2024-05-01",
      "demand_amount": 100000,
      "negotiation_status": "active",
      "offers": [
        {
          "date": "2024-06-01",
          "round": 1,
          "type": "initial_offer",
          "from": "insurance",
          "amount": 25000,
          "adjuster_notes": "Initial evaluation based on specials",
          "communication_method": "letter",
          "status": "countered"
        },
        {
          "date": "2024-06-05",
          "round": 1,
          "type": "counter",
          "from": "plaintiff",
          "amount": 85000,
          "reasoning": "Based on comparable verdicts",
          "communication_method": "letter",
          "status": "responded"
        },
        {
          "date": "2024-06-15",
          "round": 2,
          "type": "revised_offer",
          "from": "insurance",
          "amount": 35000,
          "adjuster_notes": "Reviewed medical records",
          "deadline": "2024-07-15",
          "communication_method": "email",
          "status": "pending"
        }
      ],
      "current_metrics": {
        "gap": 50000,
        "movement_them": 10000,
        "movement_us": 15000,
        "days_negotiating": 45,
        "total_rounds": 2,
        "offer_vs_limits": 35,
        "offer_vs_demand": 35
      }
    }
  ]
}
```

---

## Validation Rules

### Required Relationships

1. `round` must increment properly
2. `countered` status requires follow-up entry
3. `deadline` should be future date when set
4. `acceptance` or `rejection` terminates negotiation

### Common Errors to Avoid

| Error | Problem | Solution |
|-------|---------|----------|
| Missing round | Can't track progress | Assign round based on offer pairs |
| Wrong from value | Confuses history | Insurance offers, plaintiff counters |
| Status not updated | Stale data | Update when response received |
| Missing deadline | Missed deadlines | Always record if stated |

