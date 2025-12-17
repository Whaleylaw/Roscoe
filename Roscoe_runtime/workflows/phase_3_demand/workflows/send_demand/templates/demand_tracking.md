# Demand Tracking Template

**Case**: {{client_name}} | DOI: {{accident_date}}

---

## Demand Summary

| Field | Value |
|-------|-------|
| Demand Amount | ${{demand_amount}} |
| Attorney Approved | {{date}} |
| Demand Finalized | {{date}} |

---

## Recipients

### BI Claim #1

| Field | Value |
|-------|-------|
| Carrier | {{insurance_company}} |
| Claim Number | {{claim_number}} |
| Adjuster | {{adjuster_name}} |
| Email | {{adjuster_email}} |
| Address | {{adjuster_address}} |
| Defense Attorney | {{defense_attorney or "N/A"}} |

**Sending Details**:
| Method | Date Sent | Tracking/Confirmation |
|--------|-----------|----------------------|
| Certified Mail | {{date}} | {{tracking_number}} |
| Email | {{date}} | {{confirmation}} |

### BI Claim #2 (if applicable)

| Field | Value |
|-------|-------|
| Carrier | {{insurance_company}} |
| Claim Number | {{claim_number}} |
| Adjuster | {{adjuster_name}} |

**Sending Details**:
| Method | Date Sent | Tracking/Confirmation |
|--------|-----------|----------------------|
| Certified Mail | {{date}} | {{tracking_number}} |
| Email | {{date}} | {{confirmation}} |

---

## Client Notification

| Field | Value |
|-------|-------|
| Notification Date | {{date}} |
| Method | {{phone|email|text}} |
| Summary Provided | ☐ Yes |
| Client Acknowledged | ☐ Yes |

**Message Sent**:
```
Demand letter sent to {{carrier}} on {{date}}.
Amount demanded: ${{amount}}
Expected response within 30 days.
```

---

## Follow-Up Schedule

| Event | Date | Status |
|-------|------|--------|
| 7-Day Receipt Check | {{demand_date + 7}} | ☐ Pending |
| 30-Day Follow-Up | {{demand_date + 30}} | ☐ Pending |
| 45-Day Escalation | {{demand_date + 45}} | ☐ Pending |

---

## Response Tracking

| Date | From | Response Type | Details |
|------|------|---------------|---------|
| {{date}} | {{carrier}} | {{acknowledgment|offer|denial}} | {{details}} |

---

## Demand Package Contents

☐ Demand Letter (PDF)
☐ Exhibit A: Medical Records Index
☐ Exhibit B: Medical Records
☐ Exhibit C: Medical Bills (Itemized)
☐ Exhibit D: Medical Chronology
☐ Exhibit E: Accident/Police Report
☐ Exhibit F: Photos
☐ Exhibit G: Wage Loss Documentation
☐ Exhibit H: Property Damage

**Total Package Size**: {{size}} MB
**Delivery Method for Large Files**: {{email|file_share|cd}}

---

## Notes

{{Additional notes about the demand}}

---

## Status Updates

| Date | Update | By |
|------|--------|-----|
| {{date}} | Demand sent | {{agent|user}} |
| {{date}} | Receipt confirmed | {{agent|user}} |
| {{date}} | {{update}} | {{agent|user}} |

---

**Last Updated**: {{timestamp}}
**Phase Status**: ☐ Demand Sent → Ready for Negotiation

