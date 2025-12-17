---
name: gather_demand_materials
description: >
  Collect all materials needed for the demand package including final medical
  records, bills, liens, wage loss documentation, and complete the medical
  chronology. This workflow ensures all components are ready before drafting.
phase: demand_in_progress
workflow_id: gather_demand_materials
related_skills:
  - skills/medical-chronology-generation/skill.md
  - skills/lien-classification/skill.md
  - skills/damages-calculation/skill.md
related_tools:
  - tools/read_pdf.py (CRITICAL - convert medical record PDFs)
  - tools/chronology_tools.py (generate chronology)
  - tools/generate_document.py (fill templates)
templates:
  - templates/materials_checklist.md
---

# Gather Demand Materials Workflow

## Overview

This workflow systematically gathers and verifies all materials needed for the demand package. It ensures medical records and bills are complete, liens are identified, wage loss is documented, and the medical chronology is finalized.

**Workflow ID:** `gather_demand_materials`  
**Phase:** `demand_in_progress`  
**Owner:** Agent  
**Repeatable:** No

---

## Prerequisites

- Case in `demand_in_progress` phase
- Treatment substantially complete
- HIPAA authorization signed

---

## Workflow Steps

### Step 1: Verify All Records Received

**Step ID:** `verify_all_records`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Check that medical records have been received from all providers.

**Check:**
```python
for provider in medical_providers:
    if provider.records.received_date is None:
        missing_records.append(provider)
```

**If Records Missing:**
1. List providers with missing records
2. Trigger `request_records_bills` for each
3. Set follow-up calendar events

**Agent Report:**
> "Records status: {{received_count}} of {{total_count}} providers.
> Missing records from: {{missing_providers}}"

**If Incomplete - Options:**
| Option | When to Use |
|--------|-------------|
| Wait | Missing records are critical |
| Proceed | Missing records are minor, attorney approves |
| Override | Time-sensitive (SOL) with attorney approval |

---

### Step 2: Verify All Bills Received

**Step ID:** `verify_all_bills`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Check that itemized bills have been received from all providers.

**Check:**
```python
for provider in medical_providers:
    if provider.bills.received_date is None:
        missing_bills.append(provider)
```

**Bill Quality Check:**
- Bills are itemized (not just balance due)
- Include CPT codes
- Include ICD-10 diagnosis codes
- Show date of service

**If Bills Missing or Inadequate:**
1. List providers with issues
2. Request itemized bills specifically
3. Note for follow-up

---

### Step 3: Calculate Special Damages

**Step ID:** `calculate_specials`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Total all medical bills and other economic damages.

**Skill:** `Skills/document-xlsx/skill.md`

**Special Damages Categories:**

| Category | Source | Calculation |
|----------|--------|-------------|
| Past Medical | All providers | Sum of all bills |
| Future Medical | If documented | From life care plan or physician estimate |
| Past Lost Wages | Wage docs | Days missed × daily rate |
| Future Lost Wages | If applicable | Per economist or physician |
| Property Damage | Estimates | Vehicle repairs or total loss |
| Out-of-Pocket | Receipts | Mileage, prescriptions, etc. |

**Output:**
```json
{
  "financials": {
    "total_medical_bills": {{sum}},
    "past_lost_wages": {{amount}},
    "property_damage": {{amount}},
    "out_of_pocket": {{amount}},
    "total_special_damages": {{grand_total}}
  }
}
```

**Data Target:** `Case Information/expenses.json`

---

### Step 4: Identify All Liens

**Step ID:** `identify_liens`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Identify all potential liens and request conditional amounts.

**Triggers:** `lien_identification` workflow (if not already complete)

**Lien Types to Check:**

| Lien Type | How to Identify | Conditional Request |
|-----------|-----------------|---------------------|
| Health Insurance | Client's health insurance | Send LOR to subrogation dept |
| Medicare | Age 65+ or disabled | Query BCRC for conditional |
| Medicaid | Client receives benefits | Contact DMS |
| Hospital Lien | Statutory lien filed | Check with clerk |
| Child Support | Court order | Check records |
| Workers' Comp | Work injury | Verify coverage |

**Agent Prompt:**
> "What health insurance does the client have? I'll identify any potential liens."

**Output:**
```json
{
  "liens": [
    {
      "type": "health_insurance",
      "holder": "{{carrier}}",
      "conditional_amount": {{amount}},
      "status": "identified"
    }
  ]
}
```

**Data Target:** `Case Information/liens.json`

---

### Step 5: Collect Wage Loss Documentation

**Step ID:** `collect_wage_loss`  
**Owner:** User  
**Automatable:** No  
**Conditional:** `client.employer.missed_work == true`

**Action:**
Gather documentation supporting lost wages claim.

**Documents Needed:**

| Document | Purpose | Source |
|----------|---------|--------|
| Off-work notes | Physician authorization | Medical records |
| Pay stubs | Pre-accident income | Client |
| Tax returns/W-2s | Income verification | Client |
| Employer verification | Confirm missed time | Employer letter |

**Agent Prompt to User:**
> "Client missed work. Please gather: off-work notes, pay stubs, and employer verification of lost wages."

**Lost Wages Calculation:**
```
Hourly: Hours missed × Hourly rate
Salary: Days missed × (Annual salary / 260)
Self-employed: Lost revenue documented by tax returns
```

---

### Step 6: Complete Medical Chronology

**Step ID:** `complete_chronology`  
**Owner:** Agent  
**Automatable:** Yes

**Action:**
Finalize the medical chronology with all records received.

**Skill:** `Skills/medical-chronology/skill.md`  
**Tool:** `medical_chronology_generator`  
**Tool Available:** ✅ Yes

**Chronology Should Include:**
- All treatment dates in chronological order
- Provider name for each entry
- Treatment type/description
- Key findings and diagnoses
- Procedures performed
- Medications prescribed
- Referrals made
- Work restrictions noted

**Agent Action:**
> "I'll finalize the medical chronology using all received records."

**Output:** Completed medical chronology document

**Saves To:** `Documents/Demand/medical_chronology_{{client.name}}.pdf`

---

## Materials Checklist

Before proceeding to draft demand, verify:

### Records & Bills
- [ ] All provider records received (or approved override)
- [ ] All provider bills received (itemized)
- [ ] Records and bills organized by provider

### Damages Documentation
- [ ] Special damages calculated
- [ ] Medical chronology complete
- [ ] Wage loss documented (if applicable)
- [ ] Out-of-pocket expenses documented (if any)

### Liens
- [ ] All liens identified
- [ ] Conditional amounts requested
- [ ] Lien summary prepared

### Supporting Materials
- [ ] Accident/police report (if MVA)
- [ ] Photos (vehicle, injuries, scene)
- [ ] Property damage documentation

---

## Outputs

### Data Created
- Complete special damages calculation
- Lien summary
- Medical chronology document

### Workflows Triggered
| Condition | Workflow |
|-----------|----------|
| All materials gathered | `draft_demand` |
| Missing records | `request_records_bills` |
| Missing liens info | `lien_identification` |

---

## Completion Criteria

### Required
- All records received OR attorney override
- All bills received OR attorney override
- Medical chronology complete

### Recommended
- All liens identified
- Wage loss documented (if applicable)

---

## State Updates

On completion, update `case_state.json`:
```json
{
  "workflows": {
    "gather_demand_materials": {
      "status": "complete",
      "completed_date": "{{today}}",
      "records_complete": true,
      "bills_complete": true,
      "chronology_complete": true,
      "total_specials": {{amount}},
      "liens_identified": true
    }
  }
}
```

---

## Related Workflows

- **Triggered By:** Phase entry
- **Triggers:** `draft_demand`, `request_records_bills`, `lien_identification`

---

## Skills & Tools

| Resource | Purpose | Location |
|----------|---------|----------|
| `medical-chronology-generation` | Finalize chronology from records | `skills/medical-chronology-generation/skill.md` |
| `lien-classification` | Identify and classify liens | `skills/lien-classification/skill.md` |
| `damages-calculation` | Calculate special damages | `skills/damages-calculation/skill.md` |
| `read_pdf.py` | Convert medical record PDFs | `tools/read_pdf.py` |
| `chronology_tools.py` | Generate chronology PDF | `tools/chronology_tools.py` |
| `materials_checklist` | Track gathered materials | `templates/materials_checklist.md` |

**CRITICAL**: The agent cannot read PDFs directly. Use `tools/read_pdf.py` to convert medical records to markdown before processing.

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Provider won't send records | HIPAA to provider directly, escalate |
| Bills not itemized | Request "itemized statement" or UB-04 |
| Lien amount unknown | Send follow-up request, estimate for now |
| Wage docs unavailable | Client affidavit as alternative |
| Records contradict each other | Note discrepancy for attorney review |

