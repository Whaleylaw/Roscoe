# Roscoe Workflow System - Master Inventory

> **Source of Truth** for all phases, workflows, skills, and SOPs in the Roscoe workflow system.

---

## Phase Inventory

| # | Phase ID | Display Name | Purpose | Workflows |
|---|----------|--------------|---------|-----------|
| 0 | `onboarding` | Onboarding | Pre-acceptance: screening, conflicts, decision | 3 |
| 1 | `file_setup` | File Setup | Post-acceptance: documents, insurance, providers | 5 |
| 2 | `treatment` | Treatment | Active medical treatment monitoring | 4 |
| 3 | `demand` | Demand | Prepare and send demand package | 3 |
| 4 | `negotiation` | Negotiation | Settlement negotiations | 2 |
| 5 | `settlement` | Settlement | Process accepted settlement | 1 |
| 6 | `lien` | Lien | Resolve all liens before distribution | 3 |
| 7 | `complaint` | Complaint | File lawsuit (if litigation) | 3 |
| 8 | `discovery` | Discovery | Written discovery and depositions | 4 |
| 9 | `mediation` | Mediation | Mediation preparation and attendance | 2 |
| 10 | `trial_prep` | Trial Prep | Prepare for trial | 2 |
| 11 | `trial` | Trial | Conduct trial | 1 |
| 12 | `closed` | Closed | Close and archive case | 1 |

**Total Workflows:** 34

---

## Phase Distinction: Pre-Acceptance vs Post-Acceptance

```
┌─────────────────────────────────────────────────────────┐
│              PHASE 0: ONBOARDING                        │
│              (Pre-Acceptance)                           │
│                                                         │
│  • Client screening                                     │
│  • Conflicts check                                      │
│  • Case evaluation                                      │
│  • Accept/Decline decision                              │
│                                                         │
│  NO CASE FILE until accepted                            │
└────────────────────────┬────────────────────────────────┘
                         │ Case Accepted
                         ▼
┌─────────────────────────────────────────────────────────┐
│              PHASE 1: FILE SETUP                        │
│              (Post-Acceptance)                          │
│                                                         │
│  • Full intake questionnaire                            │
│  • Document signing (retainer, HIPAA)                   │
│  • Accident report analysis                             │
│  • Insurance claims opened                              │
│  • Medical providers set up                             │
└─────────────────────────────────────────────────────────┘
```

---

## Complete Workflow List

### Phase 0: Onboarding (3 workflows)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `client_screening` | `workflows/client_screening.md` | Conflicts, evaluation, accept/decline |
| `case_initialization` | `workflows/case_initialization.md` | Create case file after acceptance |
| `transfer_case_assessment` | `workflows/transfer_case_assessment.md` | Onboard transferred cases |

### Phase 1: File Setup (5 workflows)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `intake` | `workflows/intake.md` | Complete client/case information |
| `send_documents_for_signature` | `workflows/send_documents_for_signature.md` | Retainer, HIPAA, authorizations |
| `accident_report` | `workflows/accident_report.md` | Request and analyze police report |
| `open_insurance_claims` | `workflows/open_insurance_claims.md` | Open BI, PIP, UM claims |
| `medical_provider_setup` | `workflows/medical_provider_setup.md` | Add treating providers |

### Phase 2: Treatment (4 workflows)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `client_check_in` | `workflows/client_check_in.md` | Regular client contact |
| `request_records_bills` | `workflows/request_records_bills.md` | Request medical records |
| `medical_provider_status` | `workflows/medical_provider_status.md` | Track provider responses |
| `referral_new_provider` | `workflows/referral_new_provider.md` | Add new providers |

### Phase 3: Demand (3 workflows)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `gather_demand_materials` | `workflows/gather_demand_materials.md` | Collect records, calculate specials |
| `draft_demand` | `workflows/draft_demand.md` | Write demand letter |
| `send_demand` | `workflows/send_demand.md` | Send demand package |

### Phase 4: Negotiation (2 workflows)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `negotiate_claim` | `workflows/negotiate_claim.md` | Settlement discussions |
| `track_offers` | `workflows/track_offers.md` | Track offers and counters |

### Phase 5: Settlement (1 workflow)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `settlement_processing` | `workflows/settlement_processing.md` | Process settlement documents |

### Phase 6: Lien (3 workflows)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `identify_liens` | `workflows/identify_liens.md` | Identify all liens |
| `negotiate_liens` | `workflows/negotiate_liens.md` | Negotiate reductions |
| `resolve_liens` | `workflows/resolve_liens.md` | Finalize and pay liens |

### Phase 7: Complaint (3 workflows)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `draft_file_complaint` | `workflows/draft_file_complaint.md` | Draft and file lawsuit |
| `serve_defendant` | `workflows/serve_defendant.md` | Serve defendants |
| `process_answer` | `workflows/process_answer.md` | Handle answer/default |

### Phase 8: Discovery (4 workflows)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `propound_discovery` | `workflows/propound_discovery.md` | Send written discovery |
| `respond_to_discovery` | `workflows/respond_to_discovery.md` | Respond to discovery |
| `review_responses` | `workflows/review_responses.md` | Review defense responses |
| `party_depositions` | `workflows/party_depositions.md` | Take/defend depositions |

### Phase 9: Mediation (2 workflows)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `prepare_mediation` | `workflows/prepare_mediation.md` | Prepare brief, client |
| `attend_mediation` | `workflows/attend_mediation.md` | Attend and document |

### Phase 10: Trial Prep (2 workflows)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `expert_management` | `workflows/expert_management.md` | Retain and disclose experts |
| `trial_materials` | `workflows/trial_materials.md` | Prepare exhibits, outlines |

### Phase 11: Trial (1 workflow)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `conduct_trial` | `workflows/conduct_trial.md` | Conduct trial to verdict |

### Phase 12: Closed (1 workflow)
| Workflow ID | SOP File | Purpose |
|-------------|----------|---------|
| `close_case` | `workflows/close_case.md` | Close and archive |

---

## Phase Documentation Status

| Phase | README | Landmarks | Workflows Dir | Status |
|-------|--------|-----------|---------------|--------|
| 0 - Onboarding | ✅ | ✅ | ✅ | Complete |
| 1 - File Setup | ✅ | ✅ | ✅ | Complete |
| 2 - Treatment | ✅ | ✅ | ✅ | Complete |
| 3 - Demand | ✅ | ✅ | ✅ | Complete |
| 4 - Negotiation | ✅ | ✅ | ✅ | Complete |
| 5 - Settlement | ✅ | ✅ | ✅ | Complete |
| 6 - Lien | ✅ | ✅ | ✅ | Complete |
| 7 - Complaint | ✅ | ✅ | ✅ | Complete |
| 8 - Discovery | ✅ | ✅ | ✅ | Complete |
| 9 - Mediation | ✅ | ✅ | ✅ | Complete |
| 10 - Trial Prep | ✅ | ✅ | ✅ | Complete |
| 11 - Trial | ✅ | ✅ | ✅ | Complete |
| 12 - Closed | ✅ | ✅ | ✅ | Complete |

---

## Key Skills by Phase

| Phase | Key Skills |
|-------|------------|
| 0 - Onboarding | conflicts-check, case-evaluation |
| 1 - File Setup | police-report-analysis, insurance-claim-setup, esignature |
| 2 - Treatment | medical-chronology, calendar-scheduling |
| 3 - Demand | negotiations, document-docx |
| 4 - Negotiation | negotiations |
| 5 - Settlement | lien-resolution, document-xlsx |
| 6 - Lien | lien-resolution |
| 7 - Complaint | litigation-pleadings |
| 8 - Discovery | litigation-discovery, depositions |
| 9 - Mediation | negotiations, document-pptx |
| 10 - Trial Prep | cross-examination |
| 11 - Trial | cross-examination |
| 12 - Closed | case-file-organization |

---

## Related Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Crosslink Index | `CROSSLINK_INDEX.md` | Navigation hub |
| Phase Definitions | `schemas/phase_definitions.json` | Phase rules |
| Workflow Definitions | `schemas/workflow_definitions.json` | Workflow steps |
| Resource Mappings | `schemas/resource_mappings.json` | Skill/tool mappings |

---

*Last Updated: December 2024*
