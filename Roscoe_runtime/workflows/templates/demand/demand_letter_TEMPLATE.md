# Demand Letter Template

**Template ID**: 20 (BI Demand) / 21 (UM/UIM Demand)

---

## Letter Structure

```
[FIRM LETTERHEAD]

{{date}}

VIA EMAIL AND CERTIFIED MAIL

{{adjuster_name}}
{{insurance_company}}
{{adjuster_address}}
{{city_state_zip}}

        RE:     Claimant:     {{client_name}}
                Insured:      {{at_fault_name}}
                DOA:          {{accident_date}}
                Claim #:      {{claim_number}}

Dear {{adjuster_salutation}}:

[SECTION 1: INTRODUCTION]
This firm represents {{client_name}} for injuries sustained in a motor vehicle 
collision that occurred on {{accident_date}} in {{city}}, {{county}} County, 
Kentucky. Liability for this collision rests solely with your insured, 
{{at_fault_name}}.

[SECTION 2: FACTS OF ACCIDENT]
{{accident_narrative}}

{{at_fault_name}}'s negligent conduct includes:
{{negligence_list}}

[SECTION 3: INJURIES]
As a direct and proximate result of this collision, {{client_name}} sustained 
the following injuries:

{{injuries_narrative}}

[SECTION 4: TREATMENT SUMMARY]
{{treatment_narrative}}

[SECTION 5: MEDICAL EXPENSES]
{{client_name}} has incurred the following medical expenses as a result of 
injuries caused by your insured's negligence:

| Provider | Service Dates | CPT/ICD Codes | Amount |
|----------|---------------|---------------|--------|
{{medical_expenses_table}}

TOTAL MEDICAL EXPENSES: ${{total_medical}}

[SECTION 6: OTHER DAMAGES (if applicable)]
{{other_damages}}

[SECTION 7: DEMAND]
Based upon the clear liability of your insured and the injuries, treatment, 
and damages sustained by our client, we hereby demand the sum of 
${{demand_amount}} to fully and finally settle all claims arising from 
this incident.

This demand will remain open for thirty (30) days from the date of this 
letter. Should we not receive your response within that time, we will 
assume {{insurance_company}} is unwilling to negotiate in good faith and 
will proceed accordingly.

Please contact our office to discuss resolution of this matter.

                                        Sincerely,



                                        {{attorney_name}}
                                        {{firm_name}}

Enclosures:
- Exhibit A: Medical Records Index
- Exhibit B: Medical Records
- Exhibit C: Medical Bills
- Exhibit D: Medical Chronology
{{additional_exhibits}}
```

---

## Template Variables

### Client Information
| Variable | Source | Example |
|----------|--------|---------|
| `{{client_name}}` | overview.json | John Doe |
| `{{accident_date}}` | overview.json | April 26, 2024 |
| `{{city}}` | overview.json | Louisville |
| `{{county}}` | overview.json | Jefferson |

### Insurance Information
| Variable | Source | Example |
|----------|--------|---------|
| `{{adjuster_name}}` | insurance.json | Jane Smith |
| `{{adjuster_salutation}}` | insurance.json | Ms. Smith |
| `{{insurance_company}}` | insurance.json | State Farm |
| `{{adjuster_address}}` | insurance.json | 123 Insurance Blvd |
| `{{claim_number}}` | insurance.json | 12-345-6789 |
| `{{at_fault_name}}` | contacts.json | Robert Johnson |

### Narrative Sections
| Variable | Source | Generated |
|----------|--------|-----------|
| `{{accident_narrative}}` | overview.json | Agent drafts |
| `{{negligence_list}}` | Case analysis | Agent drafts |
| `{{injuries_narrative}}` | overview.json injuries | Agent drafts |
| `{{treatment_narrative}}` | chronology | Agent drafts |

### Damages
| Variable | Source | Example |
|----------|--------|---------|
| `{{medical_expenses_table}}` | expenses.json | Generated table |
| `{{total_medical}}` | expenses.json | 25,500.00 |
| `{{other_damages}}` | expenses.json | Lost wages, property |
| `{{demand_amount}}` | Attorney decision | 75,000.00 |

### Firm Information
| Variable | Source | Example |
|----------|--------|---------|
| `{{attorney_name}}` | config | Aaron Whaley |
| `{{firm_name}}` | config | Whaley Law Firm |
| `{{date}}` | system | December 14, 2024 |

---

## Generating the Letter

### Step 1: Copy Template to Output Location

```python
import shutil
shutil.copy(
    "${ROSCOE_ROOT}/templates/demand_template.md",
    "${ROSCOE_ROOT}/John-Doe-MVA-04-26-2024/Documents/Demand/demand_draft.md"
)
```

### Step 2: Fill Template (Agent fills content)

Open the copied template and fill all sections with case-specific content.

### Step 3: Generate Document

```bash
python ${ROSCOE_ROOT}/Tools/document_generation/generate_document.py \
    "${ROSCOE_ROOT}/John-Doe-MVA-04-26-2024/Documents/Demand/demand_draft.md"
```

---

## Narrative Guidelines

### Accident Narrative
- Date, time, location
- What client was doing (lawfully proceeding)
- What defendant did wrong
- Impact description
- Immediate aftermath

### Negligence List
Bullet points of negligent acts:
- "Failed to maintain proper lookout"
- "Failed to yield right of way"
- "Followed too closely"
- "Violated KRS [statute]"

### Injuries Narrative
List by body part, severity order:
- Diagnosis
- Symptoms
- Treatment required
- Current status

### Treatment Narrative
Chronological summary:
- Initial treatment (ER)
- Specialist care
- Ongoing treatment
- Procedures
- Current status / MMI

