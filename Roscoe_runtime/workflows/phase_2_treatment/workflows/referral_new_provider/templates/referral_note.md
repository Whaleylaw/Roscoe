# Provider Referral Note Template

Document new provider referrals during treatment phase.

---

## Provider Referral Documentation

**Case**: {{client_name}} | DOI: {{accident_date}}
**Date**: {{date}}

---

### Referral Information

| Field | Value |
|-------|-------|
| **Referral Source** | {{treating_provider|case_need|client_request|attorney_strategy}} |
| **Referring Provider** | {{name or "N/A"}} |
| **New Provider Type** | {{specialty}} |
| **Reason for Referral** | {{reason}} |

---

### New Provider Details

| Field | Value |
|-------|-------|
| **Provider Name** | {{name}} |
| **Specialty** | {{specialty}} |
| **Facility** | {{facility_name}} |
| **Address** | {{address}} |
| **Phone** | {{phone}} |
| **Fax** | {{fax}} |

---

### Appointment Information

| Field | Value |
|-------|-------|
| **Appointment Scheduled** | {{yes|no|pending}} |
| **Appointment Date** | {{date and time}} |
| **Referred By** | {{who made the referral}} |
| **Appointment Made By** | {{client|office|referring_provider}} |

---

### Referral Reason Categories

**Medical Referral** (from treating provider):
- [ ] Specialist evaluation needed
- [ ] Diagnostic testing
- [ ] Surgical consultation
- [ ] Second opinion
- [ ] Treatment escalation

**Case Strategy Referral** (attorney decision):
- [ ] Life care planning
- [ ] Vocational evaluation
- [ ] Independent medical exam (IME)
- [ ] Expert evaluation
- [ ] Documentation purposes

**Client-Initiated**:
- [ ] Second opinion requested
- [ ] Provider preference
- [ ] Location/convenience
- [ ] Insurance change

---

### Pre-Appointment Checklist

- [ ] Provider added to `medical_providers.json`
- [ ] Contact information verified
- [ ] HIPAA authorization covers new provider
- [ ] Client confirmed appointment
- [ ] LOR needed for new provider?
- [ ] Referral records obtained from referring provider

---

### Notes

{{Additional notes about the referral}}

---

### Follow-Up Actions

| Action | Due Date | Assigned To |
|--------|----------|-------------|
| Verify appointment kept | {{appointment_date + 1 day}} | {{agent|user}} |
| Add to treatment tracking | {{now}} | Agent |
| Request records after visit | {{appointment_date + 7 days}} | Agent |

---

### Case File Updates

**Updated Files**:
- [ ] `medical_providers.json` - New provider entry added
- [ ] `overview.json` - Treatment status updated
- [ ] `calendar.json` - Appointment added

---

**Documented By**: {{agent|user}}
**Timestamp**: {{datetime}}

