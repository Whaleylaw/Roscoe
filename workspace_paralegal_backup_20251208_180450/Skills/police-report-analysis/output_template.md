# Police Report Extraction: {{REPORT_NUMBER}}

**Extraction Date:** {{EXTRACTION_DATE}}
**Client:** {{CLIENT_NAME}}
**Case:** {{CASE_NAME}}

---

## Accident Summary

**Date of Accident:** {{ACCIDENT_DATE}}
**Time:** {{ACCIDENT_TIME}}
**Location:** {{LOCATION}}
**County:** {{COUNTY}}

### Narrative Summary
{{NARRATIVE_SUMMARY}}

### Manner of Collision
- **Code:** {{COLLISION_CODE}}
- **Description:** {{COLLISION_DESCRIPTION}}

### Conditions
- **Weather:** {{WEATHER}}
- **Road Surface:** {{ROAD_SURFACE}}
- **Light Condition:** {{LIGHT_CONDITION}}

---

## Client Involvement

**Client's Role:** {{CLIENT_ROLE}} (Driver/Passenger/Pedestrian)
**Client's Unit:** Unit {{CLIENT_UNIT_NUMBER}}
**Seating Position:** {{SEATING_POSITION}}

### Injury at Scene
- **Severity Code:** {{INJURY_CODE}}
- **Description:** {{INJURY_DESCRIPTION}}
- **Transported:** {{TRANSPORTED_YN}}
- **Transported To:** {{HOSPITAL}}

### PIP-Relevant Information
- **Was client the driver?** {{CLIENT_WAS_DRIVER}}
- **Is driver the owner of the vehicle?** {{DRIVER_IS_OWNER}}
- **Owner Name (if different):** {{OWNER_NAME}}
- **Was the vehicle insured?** {{VEHICLE_INSURED}}

---

## Unit Details

### Unit 1
| Field | Value |
|-------|-------|
| Driver Name | {{U1_DRIVER_NAME}} |
| Driver Address | {{U1_DRIVER_ADDRESS}} |
| Driver License | {{U1_DRIVER_LICENSE}} |
| Is Driver Owner? | {{U1_DRIVER_IS_OWNER}} |
| Owner Name | {{U1_OWNER_NAME}} |
| Vehicle | {{U1_VEHICLE_YEAR}} {{U1_VEHICLE_MAKE}} {{U1_VEHICLE_MODEL}} |
| License Plate | {{U1_PLATE}} |
| Insurance Company | {{U1_INSURANCE_COMPANY}} |
| Policy Number | {{U1_POLICY_NUMBER}} |
| Injury Severity | {{U1_INJURY_CODE}} - {{U1_INJURY_DESC}} |
| Contributing Factors | {{U1_CONTRIBUTING_FACTORS}} |

### Unit 2
| Field | Value |
|-------|-------|
| Driver Name | {{U2_DRIVER_NAME}} |
| Driver Address | {{U2_DRIVER_ADDRESS}} |
| Driver License | {{U2_DRIVER_LICENSE}} |
| Is Driver Owner? | {{U2_DRIVER_IS_OWNER}} |
| Owner Name | {{U2_OWNER_NAME}} |
| Vehicle | {{U2_VEHICLE_YEAR}} {{U2_VEHICLE_MAKE}} {{U2_VEHICLE_MODEL}} |
| License Plate | {{U2_PLATE}} |
| Insurance Company | {{U2_INSURANCE_COMPANY}} |
| Policy Number | {{U2_POLICY_NUMBER}} |
| Injury Severity | {{U2_INJURY_CODE}} - {{U2_INJURY_DESC}} |
| Contributing Factors | {{U2_CONTRIBUTING_FACTORS}} |

{{#IF_UNIT_3}}
### Unit 3
| Field | Value |
|-------|-------|
| Driver Name | {{U3_DRIVER_NAME}} |
| ... | ... |
{{/IF_UNIT_3}}

---

## Insurance Information

### At-Fault Party Insurance (for BI claim)
- **Company:** {{AT_FAULT_INSURANCE}}
- **Policy Number:** {{AT_FAULT_POLICY}}
- **Insured Name:** {{AT_FAULT_INSURED}}

### Client's Vehicle Insurance (potential PIP)
- **Company:** {{CLIENT_VEHICLE_INSURANCE}}
- **Policy Number:** {{CLIENT_VEHICLE_POLICY}}

### Client's Own Insurance (if different)
- **Company:** {{CLIENT_OWN_INSURANCE}}
- **Policy Number:** {{CLIENT_OWN_POLICY}}

---

## Liability Analysis

### Citations Issued
| Unit | Driver | Citation | Description |
|------|--------|----------|-------------|
| {{CITATION_UNIT}} | {{CITATION_DRIVER}} | {{CITATION_CODE}} | {{CITATION_DESC}} |

### Contributing Factors
| Unit | Factor Code | Description |
|------|-------------|-------------|
| 1 | {{U1_FACTOR_CODE}} | {{U1_FACTOR_DESC}} |
| 2 | {{U2_FACTOR_CODE}} | {{U2_FACTOR_DESC}} |

### Fault Assessment
**Primary Fault Indicator:** {{PRIMARY_FAULT}}
**Basis:** {{FAULT_BASIS}}

---

## Officer's Narrative

> {{FULL_NARRATIVE}}

---

## Story Comparison

| Element | Client's Version | Police Report | Match? |
|---------|------------------|---------------|--------|
| Who caused accident | {{CLIENT_FAULT_VERSION}} | {{REPORT_FAULT}} | {{MATCH_FAULT}} |
| How collision occurred | {{CLIENT_HOW_VERSION}} | {{REPORT_HOW}} | {{MATCH_HOW}} |
| Traffic signals/signs | {{CLIENT_SIGNALS}} | {{REPORT_SIGNALS}} | {{MATCH_SIGNALS}} |
| Speed | {{CLIENT_SPEED}} | {{REPORT_SPEED}} | {{MATCH_SPEED}} |
| Weather/visibility | {{CLIENT_WEATHER}} | {{REPORT_WEATHER}} | {{MATCH_WEATHER}} |

### Discrepancies to Address
{{DISCREPANCIES_LIST}}

---

## Red Flags

{{#EACH RED_FLAG}}
- ⚠️ {{RED_FLAG_DESCRIPTION}}
{{/EACH}}

{{#IF NO_RED_FLAGS}}
✅ No red flags identified
{{/IF}}

---

## Witnesses

| Name | Phone | Address | Statement Summary |
|------|-------|---------|-------------------|
| {{W1_NAME}} | {{W1_PHONE}} | {{W1_ADDRESS}} | {{W1_STATEMENT}} |

---

## PIP Waterfall Input

Based on this report, the PIP waterfall inputs are:
```json
{
  "client_on_title": {{CLIENT_ON_TITLE}},
  "vehicle_insured": {{VEHICLE_INSURED_BOOL}},
  "vehicle_insurer": "{{VEHICLE_INSURER}}",
  "vehicle_policy": "{{VEHICLE_POLICY}}"
}
```

**Run:** `python /Tools/insurance/pip_waterfall.py --client-on-title {{CLIENT_ON_TITLE_YN}} --vehicle-insured {{VEHICLE_INSURED_YN}} --vehicle-insurer "{{VEHICLE_INSURER}}"`

---

## Insurance Claims to Open

Based on this extraction:

### BI Claim
- [ ] Open BI claim with: **{{AT_FAULT_INSURANCE}}**
- Insured: {{AT_FAULT_INSURED}}
- Policy: {{AT_FAULT_POLICY}}
- Checklist: `/workflow_engine/checklists/bi_claim_opening.md`

### PIP Claim
- [ ] Run PIP waterfall to determine insurer
- Preliminary: {{PRELIMINARY_PIP_INSURER}}

### UM/UIM Claim
- [ ] {{UM_UIM_NEEDED}} - {{UM_UIM_REASON}}

---

## Next Steps

1. {{NEXT_STEP_1}}
2. {{NEXT_STEP_2}}
3. {{NEXT_STEP_3}}

---

## Raw Data (JSON)

```json
{
  "report_number": "{{REPORT_NUMBER}}",
  "accident_date": "{{ACCIDENT_DATE}}",
  "accident_time": "{{ACCIDENT_TIME}}",
  "location": "{{LOCATION}}",
  "county": "{{COUNTY}}",
  "manner_of_collision": {{COLLISION_CODE}},
  "weather": {{WEATHER_CODE}},
  "road_condition": {{ROAD_CODE}},
  "units": [
    {
      "unit_number": 1,
      "driver_name": "{{U1_DRIVER_NAME}}",
      "driver_is_owner": {{U1_DRIVER_IS_OWNER_BOOL}},
      "owner_name": "{{U1_OWNER_NAME}}",
      "vehicle": "{{U1_VEHICLE_YEAR}} {{U1_VEHICLE_MAKE}} {{U1_VEHICLE_MODEL}}",
      "insurance_company": "{{U1_INSURANCE_COMPANY}}",
      "policy_number": "{{U1_POLICY_NUMBER}}",
      "injury_severity": {{U1_INJURY_CODE}},
      "contributing_factors": [{{U1_FACTOR_CODES}}],
      "citations": [{{U1_CITATIONS}}]
    },
    {
      "unit_number": 2,
      "driver_name": "{{U2_DRIVER_NAME}}",
      "driver_is_owner": {{U2_DRIVER_IS_OWNER_BOOL}},
      "owner_name": "{{U2_OWNER_NAME}}",
      "vehicle": "{{U2_VEHICLE_YEAR}} {{U2_VEHICLE_MAKE}} {{U2_VEHICLE_MODEL}}",
      "insurance_company": "{{U2_INSURANCE_COMPANY}}",
      "policy_number": "{{U2_POLICY_NUMBER}}",
      "injury_severity": {{U2_INJURY_CODE}},
      "contributing_factors": [{{U2_FACTOR_CODES}}],
      "citations": [{{U2_CITATIONS}}]
    }
  ],
  "client": {
    "name": "{{CLIENT_NAME}}",
    "unit": {{CLIENT_UNIT_NUMBER}},
    "role": "{{CLIENT_ROLE}}",
    "is_driver": {{CLIENT_IS_DRIVER_BOOL}},
    "is_on_title": {{CLIENT_ON_TITLE}}
  },
  "witnesses": [{{WITNESSES_JSON}}],
  "red_flags": [{{RED_FLAGS_JSON}}]
}
```

