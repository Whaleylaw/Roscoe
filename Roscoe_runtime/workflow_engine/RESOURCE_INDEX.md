# Workflow Engine Resource Index

This file provides a quick reference for finding the right resources for each workflow step.

## Directory Structure

```
Roscoe_workflows/
├── Skills/                          # Agent skill definitions
│   ├── calendar-scheduling/         # Calendar & deadline management
│   ├── email-management/            # Gmail integration
│   ├── medical-records/             # Medical chronology tools
│   ├── liens/                       # Lien classification
│   ├── negotiations/                # Demand drafting
│   ├── depositions/                 # 30(b)(6) topics
│   ├── cross-examination/           # DME/IME cross, fundamentals
│   ├── insurance/                   # Liable party identification
│   ├── docx/                        # Word document creation
│   ├── pdf/                         # PDF manipulation
│   ├── xlsx/                        # Spreadsheet creation
│   └── pptx/                        # Presentation creation
│
├── Tools/                           # Executable Python tools
│   ├── calendar/                    # CRUD for calendar.json
│   ├── document_processing/         # PDF batch convert, split, cleanup
│   ├── medical_chronology/          # Term research, PDF generation
│   ├── web_scraping/                # KY eCourts automation
│   └── UI/                          # Dashboard components
│
├── workflows/                       # Detailed workflow documentation
│   ├── phase_1_intake/              # File Setup workflows
│   ├── phase_2_treatment/           # Treatment workflows
│   ├── phase_3_demand/              # Demand workflows
│   ├── phase_4_negotiation/         # Negotiation workflows
│   ├── phase_5_settlement/          # Settlement & Lien workflows
│   └── phase_6_litigation/          # Complaint through Trial
│
├── forms/                           # Document templates
│
└── workflow_engine/                 # State machine and orchestration
    ├── schemas/
    │   ├── case_state.schema.json   # Case data structure
    │   ├── phase_definitions.json   # Phase entry/exit criteria
    │   ├── workflow_definitions.json # Step-by-step workflows
    │   └── resource_mappings.json   # Links to Skills/Tools/Workflows
    ├── orchestrator/
    │   └── state_machine.py         # State tracking logic
    └── templates/
        ├── new_case_state.json      # Template for new cases
        └── response_templates.md     # Agent response formats
```

## Quick Reference by Workflow

### File Setup Phase

| Workflow | Skills | Tools | Workflow Docs |
|----------|--------|-------|---------------|
| Intake | calendar-scheduling | calendar/, UI/ | phase_1_intake/ |
| Send Documents | pdf, docx | - | phase_1_intake/ |
| Accident Report | pdf | document_processing/ | phase_1_intake/ |
| Open Insurance Claims | insurance/liable-party-id, calendar | calendar/, UI/ | phase_1_intake/ |
| Medical Provider Setup | - | UI/ | phase_1_intake/ |

### Treatment Phase

| Workflow | Skills | Tools | Workflow Docs |
|----------|--------|-------|---------------|
| Client Check-In | calendar-scheduling, email-management | calendar/ | phase_2_treatment/ |
| Request Records & Bills | pdf | calendar/ | phase_2_treatment/ |
| Lien Identification | liens/lien-classification | UI/ | phase_2_treatment/ |

### Demand Phase

| Workflow | Skills | Tools | Workflow Docs |
|----------|--------|-------|---------------|
| Gather Demand Materials | medical-records/chronology, xlsx | document_processing/, medical_chronology/ | phase_3_demand/ |
| Draft Demand | negotiations/demand-letter, docx | medical_chronology/ | phase_3_demand/ |
| Send Demand | email-management, calendar | calendar/ | phase_3_demand/ |

### Negotiation Phase

| Workflow | Skills | Tools | Workflow Docs |
|----------|--------|-------|---------------|
| Negotiate Claim | calendar-scheduling | calendar/, UI/negotiations.py | phase_4_negotiation/ |

### Settlement Phase

| Workflow | Skills | Tools | Workflow Docs |
|----------|--------|-------|---------------|
| Settlement Processing | xlsx, pdf | UI/liens.py | phase_5_settlement/ |

### Lien Phase

| Workflow | Skills | Tools | Workflow Docs |
|----------|--------|-------|---------------|
| Get Final Lien | liens/lien-classification | UI/liens.py | phase_5_settlement/ |
| Negotiate Lien | liens/lien-classification, xlsx | UI/ | phase_5_settlement/ |

### Litigation Phases

| Workflow | Skills | Tools | Workflow Docs |
|----------|--------|-------|---------------|
| Draft/File Complaint | docx, pdf, calendar | calendar/, web_scraping/ | phase_6_litigation/ |
| Discovery | docx, depositions/30b6, cross-exam | document_processing/, calendar/ | phase_6_litigation/ |
| Mediation | pptx, docx, calendar | calendar/ | phase_6_litigation/ |
| Trial Prep | cross-exam/dme-ime, pptx, docx | document_processing/ | phase_6_litigation/ |
| Trial | cross-exam/* | UI/ | phase_6_litigation/ |

## Tool Availability Matrix

| Tool Category | Tool Files | Available | Quality |
|---------------|------------|-----------|---------|
| **Calendar** | calendar_add/list/update/delete.py | ✅ Yes | 5.0 |
| **PDF Processing** | batch_convert_pdfs.py, split_pdf.py, cleanup_markdown.py | ✅ Yes | 4.5 |
| **Medical Chronology** | chronology_*.py | ✅ Yes | 4.0 |
| **Court Monitoring** | kyecourts_docket.py, kyecourts_download_documents.py | ✅ Yes | 5.0 |
| **UI Components** | case_dashboard.py, negotiations.py, liens.py, etc. | ✅ Yes | 5.0 |
| **DocuSign** | - | ❌ No | - |
| **Email Automation** | - | ❌ No | - |
| **E-Filing** | - | ❌ No | - |

## Skill Quality Scores

| Skill | Quality | Agent-Ready | Notes |
|-------|---------|-------------|-------|
| calendar-scheduling | 5.0 | ✅ | Cross-cutting, excellent |
| email-management | 4.75 | ✅ | Good Gmail integration |
| medical-records/chronology | 5.0 | ✅ | Anti-hallucination framework |
| liens/classification | 3.5 | ❌ | Needs output schema |
| negotiations/demand-drafting | 2.5 | ❌ | Needs templates, examples |
| insurance/liable-party-id | 3.5 | ❌ | Needs tool integration |
| cross-exam/fundamentals | 3.5 | ❌ | Needs concrete examples |
| cross-exam/dme-ime | 4.5 | ✅ | Good specialized skill |
| depositions/30b6 | 4.0 | ✅ | Good corporate depo skill |
| docx | 5.0 | ✅ | Excellent doc creation |
| pdf | 5.0 | ✅ | Excellent PDF tools |
| xlsx | 5.0 | ✅ | Excellent spreadsheets |
| pptx | 4.5 | ✅ | Good presentations |

## Data File Locations

| Data Type | File Path | Description |
|-----------|-----------|-------------|
| Calendar Events | Database/calendar.json | All deadlines, meetings, tasks |
| Master Contacts | Database/master_lists/Database_directory.json | Firm-wide contacts |
| Case Overview | projects/[CASE]/Case Information/overview.json | Case metadata |
| Case Contacts | projects/[CASE]/Case Information/contacts.json | Case-specific contacts |
| Insurance | projects/[CASE]/Case Information/insurance.json | Insurance claims |
| Medical Providers | projects/[CASE]/Case Information/medical_providers.json | Provider tracking |
| Liens | projects/[CASE]/Case Information/liens.json | Lien tracking |
| Expenses | projects/[CASE]/Case Information/expenses.json | Case expenses |
| Medical Terms | Resources/medical_research_cache.json | Researched terminology |

## Environment Variables Required

| Variable | Used By | Description |
|----------|---------|-------------|
| WORKSPACE_DIR | All tools | Base workspace path |
| KYECOURTS_USERNAME | web_scraping/ | KBA number for court access |
| KYECOURTS_PASSWORD | web_scraping/ | Court system password |

## Gap Summary

### High Priority Gaps (Need Development)

1. **DocuSign Integration** - Document signing workflow
2. **Client Communication Automation** - Check-in reminders, SMS
3. **Medical Records Request Generator** - HIPAA-compliant request forms
4. **Demand Package Assembly** - Automated compilation
5. **Settlement Statement Generator** - Financial calculations
6. **Complaint Template System** - Document generation from case data
7. **E-Filing Integration** - Court filing automation

### Existing Tool Enhancement Needs

1. **liens/lien-classification** - Add output schemas, tool integration
2. **negotiations/demand-drafting** - Add templates, calculation examples
3. **insurance/liable-party-id** - Add tool integration, research tools
4. **cross-exam/fundamentals** - Add concrete examples

## How Agent Should Use This

1. **Before starting a workflow**: Check `resource_mappings.json` for:
   - Which skills to reference for guidance
   - Which tools are available vs. need manual fallback
   - Where workflow documentation lives

2. **When executing a step**: 
   - If `tool_available: true` → Use the tool
   - If `tool_available: false` → Follow `manual_fallback` instructions

3. **For status updates**: Use UI components in `Tools/UI/` to generate displays

4. **For deadlines**: Use `Tools/calendar/` for all deadline tracking

5. **For medical records work**: Use `Tools/medical_chronology/` + `Skills/medical-records/`
