# Provider Status Summary Template

Use this template to track treatment status across all medical providers.

---

## Medical Provider Status Report

**Case**: {{client_name}} | DOI: {{accident_date}}
**Report Date**: {{date}}

---

### Provider Status Overview

| Provider | Specialty | First Visit | Last Visit | Status | Records |
|----------|-----------|-------------|------------|--------|---------|
| {{name}} | {{specialty}} | {{date}} | {{date}} | {{status}} | {{Y/N}} |
| {{name}} | {{specialty}} | {{date}} | {{date}} | {{status}} | {{Y/N}} |
| {{name}} | {{specialty}} | {{date}} | {{date}} | {{status}} | {{Y/N}} |

**Status Key**: 
- `active` - Currently treating
- `discharged` - Treatment complete, discharged by provider
- `self_discharged` - Client stopped attending
- `referred` - Referred to another provider
- `unknown` - Status not confirmed

---

### Active Treatment Providers

#### {{Provider Name}} - {{Specialty}}

| Field | Value |
|-------|-------|
| First Visit | {{date}} |
| Last Visit | {{date}} |
| Next Appointment | {{date or "Not scheduled"}} |
| Treatment Frequency | {{weekly|2x week|monthly|as needed}} |
| Treatment Type | {{description}} |
| Status | Active |

**Notes**: {{any relevant notes}}

---

### Completed Treatment Providers

#### {{Provider Name}} - {{Specialty}}

| Field | Value |
|-------|-------|
| First Visit | {{date}} |
| Last Visit | {{date}} |
| Reason for Discharge | {{provider discharged|treatment complete|referred out}} |
| Records Requested | {{date or "Not yet"}} |
| Records Received | {{date or "Pending"}} |
| Bills Received | {{date or "Pending"}} |

---

### Providers Needing Follow-Up

| Provider | Issue | Action Needed | Deadline |
|----------|-------|---------------|----------|
| {{name}} | {{issue}} | {{action}} | {{date}} |

---

### Treatment Completion Assessment

**Total Providers**: {{count}}
**Active**: {{count}}
**Discharged**: {{count}}
**Unknown Status**: {{count}}

**Treatment Complete?**:
- [ ] Yes - All providers show discharged/complete
- [ ] No - Active treatment ongoing
- [ ] Partial - Some complete, some active
- [ ] Unknown - Status needs verification

**Ready for Demand?**:
- [ ] Yes
- [ ] No - {{reason}}

---

### Medical Records Status

| Provider | Requested | Received | Complete | Bills |
|----------|-----------|----------|----------|-------|
| {{name}} | {{date}} | {{date}} | {{Y/N}} | {{Y/N}} |

**Records Completion**: {{X}} of {{Y}} providers ({{%}})

---

**Last Updated**: {{timestamp}}
**Updated By**: {{agent|user}}

