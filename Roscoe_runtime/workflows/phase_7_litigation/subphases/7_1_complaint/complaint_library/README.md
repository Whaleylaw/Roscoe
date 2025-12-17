# Complaint Library

## Overview

This library provides a comprehensive collection of complaint templates for Kentucky personal injury litigation. The library uses a **hybrid approach**:

1. **Base Templates** - Complete, ready-to-use complaint templates for common case types
2. **Modular Counts** - Mix-and-match legal theory modules for custom complaints
3. **Supporting Documents** - Certificates of service, notices, and forms

---

## Quick Start

1. **Determine case type** using the [Decision Tree](decision_tree.md)
2. **Select appropriate base template** from `templates/base/`
3. **If no base template fits**, build custom complaint using modules from `templates/modules/`
4. **Fill placeholders** with case-specific information
5. **Generate final document** using `generate_document.py`

---

## Directory Structure

```
complaint_library/
├── README.md                    # This file
├── decision_tree.md             # Template selection flowchart
├── templates/
│   ├── base/                    # Complete complaint templates
│   │   ├── mva_standard.md
│   │   ├── mva_uim.md
│   │   ├── mva_um.md
│   │   ├── mva_vicarious_liability.md
│   │   ├── mva_negligent_entrustment.md
│   │   ├── mva_stolen_vehicle_fraud.md
│   │   ├── premises_standard.md
│   │   ├── premises_dog_bite.md
│   │   ├── premises_government_entity.md
│   │   ├── bi_with_bad_faith.md
│   │   └── bi_bad_faith_uim.md
│   └── modules/                 # Modular count templates
│       ├── count_negligence.md
│       ├── count_uim.md
│       ├── count_um.md
│       ├── count_bad_faith.md
│       ├── count_vicarious_liability.md
│       ├── count_negligent_entrustment.md
│       ├── count_parental_liability.md
│       └── count_fraud.md
└── supporting/
    ├── notice_to_bi_adjuster.md
    ├── certificate_of_service.md
    └── certificate_of_eservice.md
```

---

## Base Templates Index

### Motor Vehicle Accident (MVA)

| Template | Use Case | Counts Included |
|----------|----------|-----------------|
| `mva_standard.md` | Basic MVA negligence | Negligence |
| `mva_uim.md` | Underinsured motorist | Negligence, UIM |
| `mva_um.md` | Uninsured motorist | Negligence, UM |
| `mva_vicarious_liability.md` | Employee driving employer vehicle | Negligence, Respondeat Superior |
| `mva_negligent_entrustment.md` | Owner entrusted vehicle to unfit driver | Negligence, Negligent Entrustment |
| `mva_stolen_vehicle_fraud.md` | Owner falsely reported vehicle stolen | Negligence, Fraud, Negligent Entrustment |

### Premises Liability

| Template | Use Case | Counts Included |
|----------|----------|-----------------|
| `premises_standard.md` | Slip/fall, dangerous conditions | Negligence |
| `premises_dog_bite.md` | Animal attack/bite | Negligence, Strict Liability |
| `premises_government_entity.md` | Metro Louisville/government defendant | Negligence (with sovereign immunity considerations) |

### Combined/Complex

| Template | Use Case | Counts Included |
|----------|----------|-----------------|
| `bi_with_bad_faith.md` | Carrier acting in bad faith | Negligence, Bad Faith (UCSPA) |
| `bi_bad_faith_uim.md` | Bad faith + underinsured | Negligence, Bad Faith, UIM |

---

## Modular Counts Index

Use these modules to build custom complaints when no base template fits:

| Module | Legal Theory | Key Statutes/Cases |
|--------|--------------|-------------------|
| `count_negligence.md` | Basic negligence | CR 8.01 |
| `count_uim.md` | Underinsured motorist | KRS 304.39-320 |
| `count_um.md` | Uninsured motorist | KRS 304.39-320 |
| `count_bad_faith.md` | Insurance bad faith | KRS 304.12-230 (UCSPA) |
| `count_vicarious_liability.md` | Respondeat Superior | Common law |
| `count_negligent_entrustment.md` | Vehicle entrustment | McGrew v. Stone; Brady v. B&B Ice |
| `count_parental_liability.md` | Minor driver liability | KRS 186.590 |
| `count_fraud.md` | Fraud/concealment | Common law |

---

## Template Placeholders

All templates use consistent placeholders:

### Case Information
- `[case.number]` - Case number (blank for new filing)
- `[case.division]` - Division number
- `[case.judge]` - Assigned judge (blank for new filing)
- `[case.county]` - Filing county

### Parties
- `[plaintiff.name]` - Plaintiff's full name
- `[plaintiff.county]` - Plaintiff's county of residence
- `[defendant.name]` - Defendant's full name  
- `[defendant.address]` - Defendant's service address
- `[defendant.county]` - Defendant's county of residence

### Accident/Incident
- `[accident.date]` - Date of accident/incident
- `[accident.location]` - Location description
- `[accident.county]` - County where incident occurred

### Insurance (when applicable)
- `[insurance.company]` - Insurance company name
- `[insurance.registered_agent]` - Registered agent for service
- `[insurance.agent_address]` - Agent's address

### Firm Information (auto-filled)
- `[firm.name]` - Law firm name
- `[firm.attorney]` - Attorney name
- `[firm.address]` - Firm address
- `[firm.phone]` - Firm phone
- `[firm.fax]` - Firm fax
- `[firm.email]` - Attorney email
- `[firm.bar_number]` - Attorney bar number

---

## Building a Custom Complaint

When no base template fits your case:

1. Start with `count_negligence.md` as the foundation
2. Add additional count modules as needed
3. Combine into single document:
   - Caption (from any base template)
   - Jurisdiction/Facts section
   - Count I: [First theory]
   - Count II: [Second theory]
   - ...
   - Wherefore/Prayer section
   - Signature block

### Example: MVA with Minor Driver + Bad Faith

```
Caption
Jurisdiction/Facts
Count I: Negligence (from count_negligence.md)
Count II: Parental Liability (from count_parental_liability.md)
Count III: Bad Faith (from count_bad_faith.md)
Wherefore
Signature
```

---

## Kentucky-Specific Requirements

### Threshold Requirements (MVA)
Per KRS 304.39-062(b), plaintiff must show:
- Medical expenses exceeding $1,000.00, OR
- Serious injuries

### Venue
- County where accident occurred, OR
- County where defendant resides

### Filing Requirements
- Original + copies for each defendant
- Filing fee
- Summons for each defendant (AOC 105)

---

## Related Resources

- [Decision Tree](decision_tree.md) - Template selection guide
- [Court Rules Reference](../workflows/draft_file_complaint/skills/complaint-drafting/references/court-rules.md)
- [Caption Format Guide](../workflows/draft_file_complaint/skills/complaint-drafting/references/caption-format.md)
- [Service Methods](../workflows/serve_defendant/skills/service-of-process/references/service-methods.md)

