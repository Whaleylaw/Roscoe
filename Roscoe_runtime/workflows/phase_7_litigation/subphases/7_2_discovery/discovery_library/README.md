# Discovery Library

## Overview

This library provides a comprehensive collection of discovery templates for Kentucky personal injury litigation. The library includes:

1. **Propounding Discovery** - Interrogatories, RFPs, and RFAs organized by case type
2. **Responding to Discovery** - Response templates with objection guidance
3. **Analysis Tools** - Workflows for reviewing defense responses and building motions

---

## Quick Start

### Propounding Discovery
1. **Determine case type and defendant** using the [Propounding Decision Tree](propounding/decision_tree.md)
2. **Select appropriate base template** from `propounding/templates/`
3. **Add modular question sets** as needed from `propounding/modules/`
4. **Fill placeholders** and customize for case-specific facts
5. **Generate final document** using `generate_document.py`

### Responding to Discovery
1. **Review incoming requests** for objectionable items
2. **Use response shell** from `responding/templates/response_shell.md`
3. **Apply appropriate objections** per `responding/references/valid_objections.md`
4. **Draft substantive responses** with verification

### Analyzing Defense Responses
1. **Use deficiency checklist** from `analysis/response_deficiency_checklist.md`
2. **Apply defense answer review** workflow for Rule 8(b) violations
3. **Draft meet and confer** using `analysis/meet_and_confer_guide.md`
4. **If needed, file motion** per `analysis/motion_to_compel_outline.md`

---

## Directory Structure

```
discovery_library/
├── README.md                         # This file
├── propounding/
│   ├── decision_tree.md              # Template selection flowchart
│   ├── templates/
│   │   ├── interrogatories/          # By case type
│   │   │   ├── mva_standard.md
│   │   │   ├── mva_trucking_driver.md
│   │   │   ├── mva_trucking_company.md
│   │   │   ├── mva_um_uim.md
│   │   │   ├── mva_respondeat_superior.md
│   │   │   ├── mva_pip.md
│   │   │   ├── premises_standard.md
│   │   │   └── bad_faith.md
│   │   ├── rfps/                     # Requests for Production
│   │   │   ├── mva_standard.md
│   │   │   ├── mva_trucking.md
│   │   │   ├── premises_standard.md
│   │   │   └── bad_faith.md
│   │   └── rfas/                     # Requests for Admission
│   │       ├── mva_liability.md
│   │       ├── mva_damages.md
│   │       ├── premises_liability.md
│   │       └── bad_faith.md
│   └── modules/                      # Mix-and-match question blocks
│       ├── mod_witness_identification.md
│       ├── mod_insurance_coverage.md
│       ├── mod_expert_disclosure.md
│       ├── mod_prior_incidents.md
│       ├── mod_cell_phone.md
│       └── mod_employment_scope.md
├── responding/
│   ├── decision_tree.md              # Response strategy flowchart
│   ├── templates/
│   │   ├── response_shell.md
│   │   └── general_objections.md
│   └── references/
│       ├── valid_objections.md
│       ├── privilege_log.md
│       └── verification_page.md
└── analysis/
    ├── defense_answer_review.md
    ├── response_deficiency_checklist.md
    ├── meet_and_confer_guide.md
    └── motion_to_compel_outline.md
```

---

## Propounding Discovery Index

### Interrogatory Templates

| Template | Defendant Type | Key Focus Areas |
|----------|---------------|-----------------|
| `mva_standard.md` | Individual driver | Collision facts, witnesses, insurance, prior incidents |
| `mva_trucking_driver.md` | CDL driver | Employment, training, hours of service, drug testing |
| `mva_trucking_company.md` | Motor carrier | Hiring practices, FMCSR compliance, CSA scores |
| `mva_um_uim.md` | UM/UIM carrier | Policy terms, claims handling, valuation |
| `mva_respondeat_superior.md` | Employer | Employment relationship, scope, supervision |
| `mva_pip.md` | PIP carrier | Coverage, payment history, denial reasons |
| `premises_standard.md` | Property owner | Notice, maintenance, inspections, prior incidents |
| `bad_faith.md` | Insurance carrier | Claims handling, UCSPA violations |

### RFP Templates

| Template | Use Case |
|----------|----------|
| `mva_standard.md` | Photos, statements, policies, cell phone records |
| `mva_trucking.md` | DQ files, logs, maintenance, GPS data |
| `premises_standard.md` | Incident reports, surveillance, policies |
| `bad_faith.md` | Claim files, adjuster notes, guidelines |

### RFA Templates

| Template | Use Case |
|----------|----------|
| `mva_liability.md` | Admissions on negligence elements |
| `mva_damages.md` | Injury causation, medical necessity |
| `premises_liability.md` | Notice, control, dangerous condition |
| `bad_faith.md` | UCSPA requirements, failure to investigate |

### Modular Question Sets

| Module | Purpose | Add To |
|--------|---------|--------|
| `mod_witness_identification.md` | CR 26.02 witness disclosure | Any template |
| `mod_insurance_coverage.md` | Policy ID, limits, reservations | Any template |
| `mod_expert_disclosure.md` | Expert identity, opinions | Any template |
| `mod_prior_incidents.md` | Substantially similar incidents | Premises, products |
| `mod_cell_phone.md` | Phone records, distraction | MVA templates |
| `mod_employment_scope.md` | Scope of employment | Vicarious liability |

---

## Kentucky Civil Procedure Rules Reference

### CR 33 - Interrogatories
- **Limit:** 30 interrogatories (including subparts), unless leave granted
- **Response time:** 30 days from service (45 if served with complaint)
- **Three "free" questions:** CR 33.01(3) - identity, address, willingness to supplement

### CR 34 - Production of Documents
- **Response time:** 30 days from service
- **Must state:** Will comply, object, or unable to produce
- **Production:** As kept in ordinary course OR organized by request category

### CR 36 - Requests for Admission
- **Response time:** 30 days from service
- **Failure to respond:** Deemed admitted
- **Cost of proof:** CR 36.02 - If denied and later proven, costs recoverable

### CR 37 - Failure to Make Discovery
- **Motion to compel:** After good faith meet and confer
- **Sanctions available:** Fees, issue preclusion, striking pleadings

---

## Template Placeholders

All templates use consistent placeholders:

### Case Information
- `[case.number]` - Case number
- `[case.county]` - Filing county
- `[case.division]` - Division number
- `[accident.date]` - Date of incident

### Parties
- `[plaintiff.name]` - Plaintiff's full name
- `[defendant.name]` - Defendant's full name
- `[defendant.address]` - Defendant's address

### Firm Information (auto-filled)
- `[firm.name]` - Law firm name
- `[firm.attorney]` - Attorney name
- `[firm.address]` - Firm address
- `[firm.phone]` - Phone number
- `[firm.bar_number]` - Bar number

---

## Building Custom Discovery

When no single template fits your needs:

1. **Start with closest base template**
2. **Add modular question sets:**
   - Copy relevant questions from `propounding/modules/`
   - Renumber to maintain sequence
3. **Customize for case facts:**
   - Replace generic descriptions with specifics
   - Add case-specific questions as needed
4. **Review Kentucky limits:**
   - Count interrogatories (including subparts)
   - Request leave if exceeding 30

### Example: MVA with Cell Phone Distraction + Expert

```markdown
# Base Template
mva_standard.md (Questions 1-27)

# Add Modules
+ mod_cell_phone.md (Questions 28-32)
+ mod_expert_disclosure.md (Questions 33-35)

# Total: 35 interrogatories
# Note: Request leave or streamline to stay under 30
```

---

## Related Resources

- [Propounding Decision Tree](propounding/decision_tree.md)
- [Response Decision Tree](responding/decision_tree.md)
- [Defense Answer Review Workflow](analysis/defense_answer_review.md)
- [Meet and Confer Guide](analysis/meet_and_confer_guide.md)
- [CR 33/34/36 Full Text](https://courts.ky.gov/courts/rules/)

