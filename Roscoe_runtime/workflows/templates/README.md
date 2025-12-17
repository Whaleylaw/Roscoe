# Workflow Templates

This folder contains all templates used across workflow phases, copied here for central access.

## Quick Start

1. **Read the manifest** to discover available templates:
   ```
   templates/templates_manifest.json
   ```

2. **Find templates by collection** - browse by type (demand, complaint, discovery, etc.)

3. **Copy template to case folder** before filling:
   ```bash
   cp templates/demand/demand_template.md /case/Documents/Demand/
   ```

4. **Fill and generate** using `generate_document.py`

## Folder Structure

```
templates/
├── templates_manifest.json
├── demand/
│   ├── demand_template.md
│   └── demand_letter_TEMPLATE.md
├── complaint/
│   ├── complaint_template.md
│   ├── base/
│   │   ├── mva_standard.md
│   │   ├── mva_um.md
│   │   ├── mva_uim.md
│   │   ├── mva_vicarious_liability.md
│   │   ├── premises_standard.md
│   │   ├── premises_dog_bite.md
│   │   └── ...
│   └── modules/
│       ├── count_negligence.md
│       ├── count_vicarious_liability.md
│       ├── count_bad_faith.md
│       └── ...
├── discovery/
│   ├── interrogatories/
│   │   ├── mva_standard.md
│   │   ├── mva_pip.md
│   │   ├── mva_trucking_*.md
│   │   └── ...
│   ├── rfas/
│   │   ├── mva_liability.md
│   │   ├── mva_damages.md
│   │   └── ...
│   ├── rfps/
│   │   ├── mva_standard.md
│   │   ├── mva_trucking.md
│   │   └── ...
│   ├── response/
│   │   ├── response_shell.md
│   │   └── general_objections.md
│   └── modules/
│       ├── mod_cell_phone.md
│       ├── mod_expert_disclosure.md
│       └── ...
├── deposition/
│   ├── notices/
│   │   ├── notice_standard.md
│   │   ├── notice_video.md
│   │   ├── notice_corp_rep.md
│   │   └── ...
│   ├── client_prep/
│   │   ├── client_letter.md
│   │   ├── client_checklist.md
│   │   └── privilege_review.md
│   ├── outlines/
│   │   ├── outline_rules_based.md
│   │   ├── outline_corp_rep.md
│   │   └── outline_expert.md
│   └── tracking/
│       ├── depo_schedule.md
│       └── testimony_tracker.md
├── medical/
│   ├── records_request_TEMPLATE.md
│   ├── check_in_note.md
│   └── chronology_entry.md
├── negotiation/
│   └── offer_analysis_template.md
├── mediation/
│   └── mediation-brief-template.md
└── output/
    ├── police_report_output.md
    └── lien_inventory.md
```

## Template Collections

### Demand Templates (2)
Full demand letter with sections for facts, injuries, treatment, damages, and exhibits.

### Complaint Templates (19)
- **11 base templates**: MVA, premises, bad faith variants
- **8 module templates**: Counts for negligence, vicarious liability, bad faith, UM/UIM

### Discovery Templates (24)
- **8 interrogatories**: MVA, PIP, trucking, premises, bad faith
- **4 RFAs**: Liability, damages by case type
- **4 RFPs**: Standard and specialized requests
- **2 response templates**: Shell and objections
- **6 modules**: Cell phone, experts, witnesses, etc.

### Deposition Templates (14)
- **6 notices**: Standard, video, corporate rep, expert
- **3 client prep**: Letter, checklist, privilege review
- **3 outlines**: Rules-based, corp rep, expert
- **2 tracking**: Schedule and testimony trackers

### Medical Templates (3)
Records requests, check-in notes, chronology entries

### Other (4)
Negotiation, mediation, and output format templates

## Template Types

| Type | Description |
|------|-------------|
| `agent_filled` | Agent writes content; firm data auto-merged |
| `auto_filled` | All fields populated from case JSONs |
| `modular` | Combinable with other modules |

## DOCX/PDF Templates

For Word and PDF form templates, see:
```
${ROSCOE_ROOT}/templates/
```

With registry at `template_registry.json`.
