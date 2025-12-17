# Police Report Analysis Output Template

Use this template when generating the extraction output from a Kentucky crash report.

---

## Police Report Analysis Complete

**Report**: #[REPORT_NUMBER] | Officer: [OFFICER_NAME] | Agency: [AGENCY_NAME] | Date: [REPORT_DATE]

---

### Accident Summary

| Field | Value |
|-------|-------|
| Date/Time | [MM/DD/YYYY] at [HH:MM AM/PM] |
| Location | [Street Address], [City], [County] County, KY |
| Manner of Collision | [Description] (Code [#]) |
| Weather | [Condition] (Code [#]) |
| Road Surface | [Condition] (Code [#]) |
| Light Conditions | [Condition] (Code [#]) |

---

### Client Involvement

| Field | Value |
|-------|-------|
| Client Name | [FULL NAME] |
| Role | [Driver / Passenger / Pedestrian] of Unit [#] |
| Seating Position | [Position] (Code [#]) |
| Injury Severity | Code [#] - [Description] |
| Transported | [Yes/No] → [Hospital Name if yes] |
| Safety Equipment | [Description] (Code [#]) |

---

### Unit Details

#### Unit 1 [CLIENT / AT-FAULT / OTHER]

**Vehicle:**
| Field | Value |
|-------|-------|
| Year/Make/Model | [YEAR] [MAKE] [MODEL] |
| License Plate | [STATE] [NUMBER] |
| VIN | [VIN or "Not Listed"] |

**Driver:**
| Field | Value |
|-------|-------|
| Name | [FULL NAME] |
| Address | [STREET], [CITY], [STATE] [ZIP] |
| DOB | [MM/DD/YYYY] |
| License # | [STATE] [NUMBER] |
| Driver Condition | Code [#] - [Description] |
| **Is Driver the Owner?** | **[YES / NO]** ← Critical for PIP |
| Owner Name (if different) | [OWNER NAME or "Same as Driver"] |

**Insurance:**
| Field | Value |
|-------|-------|
| Company | [INSURANCE COMPANY NAME] |
| Policy # | [POLICY NUMBER] |
| Phone | [PHONE NUMBER or "Not Listed"] |

**Contributing Factors:**
- [Factor 1] (Code [##])
- [Factor 2] (Code [##])

---

#### Unit 2 [CLIENT / AT-FAULT / OTHER]

**Vehicle:**
| Field | Value |
|-------|-------|
| Year/Make/Model | [YEAR] [MAKE] [MODEL] |
| License Plate | [STATE] [NUMBER] |
| VIN | [VIN or "Not Listed"] |

**Driver:**
| Field | Value |
|-------|-------|
| Name | [FULL NAME] |
| Address | [STREET], [CITY], [STATE] [ZIP] |
| DOB | [MM/DD/YYYY] |
| License # | [STATE] [NUMBER] |
| Driver Condition | Code [#] - [Description] |
| **Is Driver the Owner?** | **[YES / NO]** |
| Owner Name (if different) | [OWNER NAME or "Same as Driver"] |

**Insurance:**
| Field | Value |
|-------|-------|
| Company | [INSURANCE COMPANY NAME] |
| Policy # | [POLICY NUMBER] |
| Phone | [PHONE NUMBER or "Not Listed"] |

**Contributing Factors:**
- [Factor 1] (Code [##])
- [Factor 2] (Code [##])

---

### Insurance Extracted

#### PIP Source (Client's Medical Bills)

| Field | Value |
|-------|-------|
| Source Unit | Unit [#] |
| Insurance Company | [COMPANY NAME] ✅ |
| Policy # | [POLICY NUMBER] |
| Driver on Title? | [YES / NO] |
| PIP Waterfall Position | [1st / 2nd / 3rd / KAC] |

#### BI Source (At-Fault Party)

| Field | Value |
|-------|-------|
| Source Unit | Unit [#] |
| Insurance Company | [COMPANY NAME] ✅ |
| Policy # | [POLICY NUMBER] |
| Driver Name | [AT-FAULT DRIVER NAME] |

---

### Liability Assessment

#### Citations Issued

| Unit | Driver | Citation | Statute |
|------|--------|----------|---------|
| [#] | [NAME] | [VIOLATION DESCRIPTION] | [KRS ###.###] |
| [#] | [NAME] | [VIOLATION DESCRIPTION] | [KRS ###.###] |

#### Contributing Factors Summary

| Unit | Driver | Primary Factor | Code |
|------|--------|----------------|------|
| [#] | [NAME] | [FACTOR] | [##] |
| [#] | [NAME] | [FACTOR] | [##] |

#### Fault Determination

**Primary Fault:** Unit [#] - [DRIVER NAME]

**Reasoning:**
- [Reason 1 - e.g., "Cited for failure to yield"]
- [Reason 2 - e.g., "Contributing factor: Disregarded traffic signal"]
- [Reason 3 - e.g., "Officer narrative indicates..."]

**Liability Confidence:** [HIGH / MEDIUM / LOW]

---

### Officer's Narrative

> [COPY NARRATIVE VERBATIM FROM REPORT]

**Narrative Summary:**
[Agent's brief summary of what happened according to the officer]

---

### Story Comparison

| Element | Client's Version | Report Version | Match? |
|---------|------------------|----------------|--------|
| Location | [Client said] | [Report shows] | ✅/⚠️ |
| How it happened | [Client said] | [Report shows] | ✅/⚠️ |
| Who was at fault | [Client said] | [Report shows] | ✅/⚠️ |
| Injuries claimed | [Client said] | [Report shows] | ✅/⚠️ |

**Discrepancies:**
- [List any inconsistencies between client's account and police report]

---

### Witnesses

| # | Name | Phone | Address | Statement Summary |
|---|------|-------|---------|-------------------|
| 1 | [NAME] | [PHONE] | [ADDRESS] | [Brief summary if available] |
| 2 | [NAME] | [PHONE] | [ADDRESS] | [Brief summary if available] |

---

### Red Flags

[Include only flags that apply - delete others]

- ⚠️ **Client was cited** - [Citation details]. May affect liability.
- ⚠️ **Client refused medical attention** - Gap in treatment documentation.
- ⚠️ **No insurance listed for Unit [#]** - UM/UIM claim may be needed.
- ⚠️ **Driver impairment noted** - Code [#] for Unit [#]. Potential punitive damages.
- ⚠️ **Pre-existing damage noted** - Defense may argue prior damage.
- ⚠️ **Story discrepancy** - Client's version differs from report in [area].
- ⚠️ **Multiple potentially liable parties** - [Details if passenger case or shared fault]

---

### PIP Waterfall Input

| Question | Answer | Notes |
|----------|--------|-------|
| Was client the driver? | [YES / NO] | |
| If driver, is client on vehicle title? | [YES / NO / UNKNOWN] | Critical for PIP position |
| Was vehicle insured? | [YES / NO] | |
| If insured, by which company? | [COMPANY NAME] | |
| Client's own auto insurance? | [COMPANY NAME or NONE] | |
| Household member insurance? | [COMPANY NAME or NONE / N/A] | |

**Recommended PIP Carrier:** [COMPANY NAME or "KAC Required"]

---

### Next Actions

1. [ ] Run PIP waterfall tool to confirm PIP carrier
2. [ ] Create insurance entry for BI carrier: [COMPANY NAME]
3. [ ] Create insurance entry for PIP carrier: [COMPANY NAME]
4. [ ] Create contact card for at-fault driver: [NAME]
5. [ ] Create contact card for witness(es): [NAME(S)]
6. [ ] Update overview.json with accident details
7. [ ] [If red flags] Flag for attorney review: [ISSUE]

---

### Data Targets

| Data | Target File | Field Path |
|------|-------------|------------|
| Accident details | overview.json | `accident.*` |
| BI insurance | insurance.json | New entry with `coverage_type: "BI"` |
| PIP insurance | insurance.json | New entry with `coverage_type: "PIP"` |
| At-fault party | contacts.json | New entry with `role: "at_fault_driver"` |
| Witnesses | contacts.json | New entries with `role: "witness"` |

---

*Analysis completed: [DATE] | Analyst: [AGENT/USER]*

