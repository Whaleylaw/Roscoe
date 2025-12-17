# Demand Package Tracking Checklist (Gap #14)

## Overview
Track demand preparation, delivery, and response timeline.

---

## Existing Data Fields (insurance.json)
- `date_demand_sent` - When demand mailed/emailed
- `date_demand_acknowledged` - When carrier confirmed receipt
- `demanded_amount` - Amount demanded
- `demand_summary` - Brief description
- `demand_negotiations` - Negotiation notes

---

## Pre-Demand Checklist

### Materials Required
- [ ] All medical records received
- [ ] All medical bills received
- [ ] All liens identified
- [ ] Wage loss documentation (if applicable)
- [ ] Photos/evidence compiled
- [ ] Medical chronology complete
- [ ] Police report obtained

### Calculations
- [ ] Total medical specials calculated
- [ ] Lost wages calculated
- [ ] Future damages estimated (if applicable)
- [ ] Demand multiplier determined

---

## Demand Letter Components

1. **Introduction** - Representation, accident facts
2. **Liability** - Why at-fault is liable
3. **Injuries** - Description of injuries sustained
4. **Treatment** - Medical treatment summary
5. **Damages** - Medical bills, lost wages, pain & suffering
6. **Demand** - Specific dollar amount requested
7. **Deadline** - Response deadline (typically 30 days)

---

## Sending the Demand

### Step 1: Finalize Demand
- [ ] Attorney review and approval
- [ ] All exhibits attached
- [ ] PDF compiled

### Step 2: Send Demand
**Recommended: Multiple Methods**
- [ ] Email to adjuster (immediate delivery)
- [ ] Certified mail (proof of delivery)

### Step 3: Track in Case File
- Update `date_demand_sent` = today's date
- Update `demanded_amount` = demand figure
- Update `demand_summary` = brief description
- Add calendar reminder for 30-day response deadline

---

## Response Timeline

| Days After Sending | Action |
|-------------------|--------|
| Day 0 | Demand sent, start clock |
| Day 7 | If no acknowledgment, follow up |
| Day 14 | Second follow-up if no response |
| Day 21 | Call adjuster directly |
| Day 30 | Deadline - evaluate next steps |
| Day 30+ | Consider litigation if no response |

---

## Response Tracking

### When Adjuster Acknowledges
- Update `date_demand_acknowledged` = date
- Note any initial comments

### When Offer Received
- Use negotiation tracker tool
- Update insurance record

---

## Follow-Up Templates

### Email Follow-Up (Day 7)
```
Subject: Demand Status - {{client_name}} v. {{insured_name}}
Claim #: {{claim_number}}

Dear {{adjuster_name}},

I am following up on our demand letter sent {{demand_date}}.
Please confirm receipt and advise when we can expect a response.

Thank you,
{{attorney_name}}
```

### Phone Follow-Up Script
1. Confirm they received demand
2. Ask if they need anything else
3. Get expected response timeline
4. Document call

---

## Integration with Negotiation Workflow

Once response received:
1. → Record offer in negotiation tracker
2. → Calculate net-to-client
3. → Present offer to client
4. → Continue negotiation or proceed to settlement

