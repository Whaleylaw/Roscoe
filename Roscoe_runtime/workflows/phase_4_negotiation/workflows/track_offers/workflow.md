---
name: track_offers
description: >
  Document and track all offers and counteroffers throughout the negotiation
  process. This workflow maintains a complete record of negotiation history
  for each claim.
phase: negotiation
workflow_id: track_offers
related_skills:
  - offer-tracking
related_tools: []
templates:
  - negotiation_summary.md
---

# Track Offers Workflow

## Overview

This workflow maintains a comprehensive record of all offers and counteroffers exchanged during negotiation. It provides visibility into negotiation progress and history for each claim.

**Workflow ID:** `track_offers`  
**Phase:** `negotiation`  
**Owner:** Agent  
**Repeatable:** Yes (ongoing)

---

## Prerequisites

- Case in `negotiation` phase
- At least one claim in negotiation

---

## Offer Tracking Structure

### Per-Claim Offer History

Each claim in `insurance.json` maintains an offers array:

```json
{
  "claims": [
    {
      "id": "bi_001",
      "type": "BI",
      "carrier": "State Farm",
      "policy_limits": 100000,
      "demand_sent_date": "2024-01-15",
      "demand_amount": 100000,
      "offers": [
        {
          "date": "2024-02-01",
          "round": 1,
          "type": "initial_offer",
          "from": "insurance",
          "amount": 15000,
          "adjuster_notes": "Disputed causation",
          "status": "countered"
        },
        {
          "date": "2024-02-05",
          "round": 1,
          "type": "counter",
          "from": "plaintiff",
          "amount": 85000,
          "reasoning": "Full records support causation",
          "status": "responded"
        },
        {
          "date": "2024-02-15",
          "round": 2,
          "type": "revised_offer",
          "from": "insurance",
          "amount": 35000,
          "adjuster_notes": "Increased based on records review",
          "status": "pending"
        }
      ],
      "negotiation_status": "active"
    }
  ]
}
```

---

## Workflow Steps

### Step 1: Document New Entry

**Step ID:** `document_entry`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
When offer or counter is made, create new entry in offers array.

**Entry Fields:**

| Field | Description | Required |
|-------|-------------|----------|
| `date` | Date of offer/counter | Yes |
| `round` | Negotiation round number | Yes |
| `type` | Entry type (see below) | Yes |
| `from` | Who made this (insurance/plaintiff) | Yes |
| `amount` | Dollar amount | Yes |
| `conditions` | Any conditions | If applicable |
| `notes` | Adjuster/attorney notes | Optional |
| `reasoning` | Justification for counter | For counters |
| `deadline` | Response deadline | If time-limited |
| `status` | Current status | Yes |

**Entry Types:**
| Type | Description |
|------|-------------|
| `initial_offer` | Insurance's first offer |
| `revised_offer` | Subsequent insurance offers |
| `counter` | Plaintiff's counter-offer |
| `final_offer` | Stated as final |
| `acceptance` | Offer accepted |
| `rejection` | Offer rejected |

---

### Step 2: Update Status

**Step ID:** `update_status`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Update entry status as negotiation progresses.

**Status Values:**
| Status | Meaning |
|--------|---------|
| `pending` | Awaiting response |
| `under_review` | Being evaluated |
| `countered` | Counter was sent |
| `responded` | Response received |
| `accepted` | Offer accepted |
| `rejected` | Offer rejected |
| `expired` | Deadline passed |

---

### Step 3: Generate Summary

**Step ID:** `generate_summary`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Create negotiation summary report.

**Summary Format:**
```
NEGOTIATION SUMMARY
Claim: {{carrier}} ({{claim_type}})
Claim #: {{claim_number}}
Policy Limits: ${{limits}}

Demand: ${{demand_amount}} (sent {{demand_date}})

OFFER HISTORY:
Round 1:
  - Insurance: ${{amount}} ({{date}})
  - Our Counter: ${{amount}} ({{date}})
  
Round 2:
  - Insurance: ${{amount}} ({{date}})
  - Our Counter: ${{amount}} ({{date}})

Current Status: {{status}}
Last Activity: {{date}}
Gap: ${{our_last - their_last}}
```

---

## Tracking Metrics

### Key Metrics to Track

| Metric | Calculation | Purpose |
|--------|-------------|---------|
| Gap | Our position - Their position | Progress indicator |
| Movement | Change from previous offer | Momentum |
| Days in negotiation | Today - demand sent | Timeline |
| Rounds | Count of offer exchanges | Progress |
| % of limits | Current offer / limits | Value indicator |

---

## Outputs

### Data Maintained
- Complete offer history per claim
- Negotiation status
- Key metrics

### Reports Available
- Negotiation summary
- Offer history timeline
- Gap analysis

---

## Completion Criteria

This workflow runs continuously during negotiation.

Ends when:
- Settlement reached
- Negotiation impasse declared
- Case moves to litigation

---

## State Updates

Continuously update `case_state.json`:
```json
{
  "negotiation_tracking": {
    "claims_in_negotiation": {{count}},
    "total_rounds": {{count}},
    "current_offer": {{amount}},
    "our_last_counter": {{amount}},
    "gap": {{difference}},
    "last_activity_date": "{{date}}"
  }
}
```

---

## Related Workflows

- **Runs Alongside:** `negotiate_claim`
- **Provides Data To:** Settlement evaluation, litigation decision

---

## Skills Used

| Skill | Location | Purpose |
|-------|----------|---------|
| `offer-tracking` | `skills/offer-tracking/skill.md` | Track and document offers |

---

## Templates

| Template | Location | Purpose |
|----------|----------|---------|
| Negotiation Summary | `templates/negotiation_summary.md` | Summary report of offer history |

---

## Best Practices

### Document Everything
- Record every communication
- Note adjuster's stated reasoning
- Document our justification for counters

### Track Timing
- Response times
- Deadline compliance
- Negotiation velocity

### Identify Patterns
- Adjuster negotiation style
- Movement patterns
- Sticking points

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Conflicting records | Review communications, reconcile |
| Missing entry | Add retroactively with accurate date |
| Status unclear | Clarify with most recent communication |
| Multiple claims | Track separately, may combine for resolution |

