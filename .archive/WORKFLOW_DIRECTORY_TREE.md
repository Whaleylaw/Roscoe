# Complete Workflow Directory Structure

**Source:** whaley_law_firm/workflows (GCS bucket at /mnt/workspace/workflows)
**Date:** December 23, 2025

---

## I. phase_0_onboarding

### A. README.md
### B. landmarks.md
**Landmarks:**
- L0.1: client_info_received
- L0.2: contract_signed
- L0.3: medical_auth_signed

### C. workflows/
#### C.1. case_setup/
##### C.1.a. workflow.md
##### C.1.b. tools/
- create_case.py

#### C.2. document_collection/
##### C.2.a. workflow.md
##### C.2.b. skills/
**C.2.b.i. document-intake/**
- skill.md

**C.2.b.ii. document-request/**
- skill.md

**C.2.b.iii. docusign-send/**
- skill.md
- tools/
  - docusign_config.py
  - docusign_send.py
- references/
  - anchor-strings.md
  - multiple-signers.md
  - tool-usage.md
  - tracking.md

##### C.2.c. templates/
- document-checklist.md
- request-email.md
- intake_forms/
  - 2021 Whaley Authorization of Digitally Signature Replication (1).pdf
  - 2021 Whaley CMS Medicare Verification Form (1).pdf
  - 2021 Whaley MVA Accident Detail Information Sheet (1).pdf
  - 2021 Whaley MVA Fee Agreement (1).pdf
  - 2021 Whaley Medical Authorization (HIPAA) (1).pdf
  - 2021 Whaley Medical Treatment Questionnaire (1).pdf
  - 2021 Whaley New Client Information Sheet (1).pdf
  - 2021 Whaley S&F Accident Detail Information Sheet (1).pdf
  - 2021 Whaley S&F Fee Agreement (1).pdf
  - 2021 Whaley WC Fee Agreement - Final (1).pdf
  - 2021 Whaley Wage & Salary Verification (1).pdf
  - INDEX.md

##### C.2.d. tools/

---

## II. phase_1_file_setup

### A. README.md
### B. landmarks.md
**Landmarks:**
- L1.1: full_intake_complete
- L1.2: accident_report_obtained
- L1.3: insurance_claims_setup (with BI/PIP sub-steps)
- L1.4: providers_setup

### C. workflows/
#### C.1. accident_report/
##### C.1.a. workflow.md
##### C.1.b. skills/
**C.1.b.i. police-report-analysis/**
- skill.md
- references/
  - kentucky_codes.md
  - output_template.md
  - tool-usage.md

##### C.1.c. templates/
##### C.1.d. tools/
- lexis_crash_order.py
- read_pdf.py

#### C.2. insurance_bi_claim/
##### C.2.a. workflow.md
##### C.2.b. skills/
**C.2.b.i. liability-analysis/**
- skill.md
- references/
  - comparative-fault.md
  - denied-liability.md
  - evidence-recommendations.md
  - passenger-scenarios.md
  - um-uim-claims.md

**C.2.b.ii. lor-generator/**
- skill.md
- tools/
  - generate_document.py
- references/
  - error-handling.md
  - placeholder-mapping.md
  - tool-usage.md

##### C.2.c. templates/
- 2022 Whaley LOR to BI Adjuster(1)(1)(1) (1).docx

##### C.2.d. tools/
- generate_document.py

#### C.3. insurance_pip_claim/
##### C.3.a. workflow.md
##### C.3.b. skills/
**C.3.b.i. pip-application/**
- skill.md
- references/
  - common-issues.md
  - field-mapping.md
  - form-sections.md

**C.3.b.ii. pip-waterfall/**
- skill.md
- references/
  - disqualification.md
  - kac-process.md
  - tool-usage.md
  - waterfall-steps.md

##### C.3.c. templates/
- 2022 Whaley LOR to PIP Adjuster(1)(1) (1).docx
- KACP-Application-03.2021(1) (1).pdf

##### C.3.d. tools/
- generate_document.py
- pip_waterfall.py

#### C.4. medical_provider_setup/
##### C.4.a. workflow.md
##### C.4.b. skills/
**C.4.b.i. medical-records-request/**
- skill.md
- tools/
  - generate_document.py
- references/
  - error-handling.md
  - follow-up-process.md
  - sending-methods.md
  - template-placeholders.md

##### C.4.c. templates/
- 2022 Whaley Medical Record Request (URR) (1).docx
- 2023 Whaley Initial Medical Billing Request to Provider (MBR) (1).pdf
- 2023 Whaley Law Firm Medical Request Template (1).pdf

##### C.4.d. tools/
- generate_document.py

#### C.5. send_documents_for_signature.md

---

## III. phase_2_treatment

### A. README.md
### B. landmarks.md
**Landmarks:**
- L2.1: client_check_in_schedule_active
- L2.2: all_providers_have_records_requested
- (More landmarks in file)

### C. workflows/
#### C.1. client_check_in/
##### C.1.a. workflow.md
##### C.1.b. skills/
**C.1.b.i. calendar-scheduling/**
- skill.md
- references/

##### C.1.c. templates/
- check_in_note.md

#### C.2. lien_identification/
##### C.2.a. workflow.md
##### C.2.b. skills/
**C.2.b.i. lien-classification/**
- skill.md
- references/
  - erisa-subrogation.md
  - medicaid-liens.md
  - medicare-liens.md
  - provider-liens.md

##### C.2.c. templates/
- lien_inventory.md

#### C.3. medical_chronology/
##### C.3.a. workflow.md
##### C.3.b. skills/
**C.3.b.i. medical-chronology-generation/**
- skill.md
- references/
  - extraction-fields.md
  - red-flags.md
  - research-process.md

##### C.3.c. templates/
- chronology_entry.md

##### C.3.d. tools/
- chronology_tools.py
- read_pdf.py

#### C.4. medical_provider_status/
##### C.4.a. workflow.md
##### C.4.b. templates/
- provider_status_summary.md

#### C.5. referral_new_provider/
##### C.5.a. workflow.md
##### C.5.b. templates/
- referral_note.md

#### C.6. request_records_bills/
##### C.6.a. workflow.md
##### C.6.b. skills/
**C.6.b.i. medical-records-request/**
- skill.md
- tools/
  - generate_document.py
- references/
  - error-handling.md
  - follow-up-process.md
  - sending-methods.md
  - template-placeholders.md

##### C.6.c. templates/
- records_request_TEMPLATE.md

##### C.6.d. tools/
- generate_document.py
- medical_request_generator.py
- read_pdf.py

---

## IV. phase_3_demand

### A. README.md
### B. landmarks.md
**Landmarks:**
- L3.1: all_records_received
- L3.2: all_bills_received
- (More landmarks in file)

### C. workflows/
#### C.1. draft_demand/
##### C.1.a. workflow.md
##### C.1.b. skills/
**C.1.b.i. demand-letter-generation/**
- skill.md
- references/
  - demand-valuation.md
  - exhibit-compilation.md
  - narrative-sections.md

##### C.1.c. templates/
- demand_letter_TEMPLATE.md
- demand_template.md

##### C.1.d. tools/
- firm_config.json
- generate_demand_pdf.py
- generate_document.py
- read_pdf.py

#### C.2. gather_demand_materials/
##### C.2.a. workflow.md
##### C.2.b. skills/
**C.2.b.i. damages-calculation/**
- skill.md
- references/
  - code-extraction.md
  - wage-calculation.md

**C.2.b.ii. lien-classification/**
- skill.md
- references/
  - erisa-subrogation.md
  - medicaid-liens.md
  - medicare-liens.md
  - provider-liens.md

**C.2.b.iii. medical-chronology-generation/**
- skill.md
- references/
  - extraction-fields.md
  - red-flags.md
  - research-process.md

##### C.2.c. templates/
- materials_checklist.md

##### C.2.d. tools/
- chronology_tools.py
- generate_document.py
- read_pdf.py

#### C.3. send_demand/
##### C.3.a. workflow.md
##### C.3.b. skills/
**C.3.b.i. calendar-scheduling/**
- skill.md
- references/

##### C.3.c. templates/
- demand_tracking.md

---

## V. phase_4_negotiation

### A. README.md
### B. landmarks.md
**Landmarks:**
- L4.1: one_week_followup_completed
- L4.2: deficiencies_addressed
- (More landmarks in file)

### C. workflows/
#### C.1. negotiate_claim/
##### C.1.a. workflow.md
##### C.1.b. skills/
**C.1.b.i. calendar-scheduling/**
- skill.md

**C.1.b.ii. negotiation-strategy/**
- skill.md
- references/
  - counter-strategies.md
  - tactics.md

##### C.1.c. templates/
- counter_offer_letter.md
- settlement_summary.md

##### C.1.d. tools/
- generate_document.py

#### C.2. offer_evaluation/
##### C.2.a. workflow.md
##### C.2.b. skills/
**C.2.b.i. lien-negotiation/**
- skill.md
- references/
  - reduction-strategies.md

**C.2.b.ii. offer-evaluation/**
- skill.md
- references/
  - comparable-analysis.md
  - net-calculation.md

##### C.2.c. templates/
- offer_analysis_template.md

#### C.3. track_offers/
##### C.3.a. workflow.md
##### C.3.b. skills/
**C.3.b.i. offer-tracking/**
- skill.md
- references/
  - tracking-fields.md

##### C.3.c. templates/
- negotiation_summary.md

---

## VI. phase_5_settlement

### A. README.md
### B. landmarks.md
**Landmarks:**
- L5.1: settlement_statement_prepared
- L5.2: authorization_to_settle_prepared
- (More landmarks in file)

### C. workflows/
#### C.1. lien_negotiation/
##### C.1.a. workflow.md
##### C.1.b. skills/
**C.1.b.i. lien-classification/**
- skill.md
- references/
  - erisa-subrogation.md
  - medicaid-liens.md
  - medicare-liens.md
  - provider-liens.md

**C.1.b.ii. lien-resolution/**
- skill.md
- references/
  - medicaid-process.md
  - medicare-process.md

##### C.1.c. templates/
- lien_reduction_letter.md

#### C.2. settlement_processing/
##### C.2.a. workflow.md
##### C.2.b. skills/
**C.2.b.i. docusign-send/**
- skill.md
- references/
  - anchor-strings.md
  - multiple-signers.md
  - tool-usage.md
  - tracking.md

**C.2.b.ii. settlement-statement/**
- skill.md
- references/
  - fee-calculation.md
  - trust-requirements.md

##### C.2.c. templates/
- authorization_to_settle.md
- settlement_statement.md

##### C.2.d. tools/
- generate_document.py

---

## VII. phase_6_lien

### A. README.md
### B. landmarks.md
**Landmarks:**
- L6.1: outstanding_liens_identified
- L6.2: final_lien_amounts_requested
- L6.3: medicare_final_demand_received
- (More landmarks in file)

### C. workflows/
#### C.1. final_distribution/
##### C.1.a. workflow.md
##### C.1.b. skills/
**C.1.b.i. supplemental-statement/**
- skill.md
- references/
  - calculation-guide.md

##### C.1.c. templates/
- supplemental_settlement_statement.md

##### C.1.d. tools/
- generate_document.py

#### C.2. get_final_lien/
##### C.2.a. workflow.md
##### C.2.b. skills/
**C.2.b.i. final-lien-request/**
- skill.md
- references/
  - lien-type-contacts.md

##### C.2.c. templates/
- final_lien_request.md

#### C.3. negotiate_lien/
##### C.3.a. workflow.md
##### C.3.b. skills/
**C.3.b.i. lien-reduction/**
- skill.md
- references/
  - compromise-waiver.md
  - erisa-negotiation.md

##### C.3.c. templates/
- lien_reduction_request.md

---

## VIII. phase_7_litigation

### A. README.md
### B. landmarks.md
**Phase-Level Landmarks:**
- L7.0: litigation_commenced
- L7.1: complaint_filed (HARD BLOCKER)
- L7.2: defendant_served
- (More landmarks in file)

### C. subphases/
**Note:** Litigation has subphases (7.1, 7.2, etc.) instead of workflows

#### C.1. 7_1_complaint/
##### C.1.a. README.md
##### C.1.b. landmarks.md
##### C.1.c. complaint_library/
**C.1.c.i. README.md**
**C.1.c.ii. decision_tree.md**

**C.1.c.iii. templates/base/**
- mva_standard.md
- mva_um.md
- mva_uim.md
- mva_vicarious_liability.md
- mva_negligent_entrustment.md
- mva_stolen_vehicle_fraud.md
- premises_standard.md
- premises_dog_bite.md
- premises_government_entity.md
- bi_with_bad_faith.md
- bi_bad_faith_uim.md

**C.1.c.iv. templates/modules/**
- count_negligence.md
- count_um.md
- count_uim.md
- count_vicarious_liability.md
- count_negligent_entrustment.md
- count_parental_liability.md
- count_fraud.md
- count_bad_faith.md

**C.1.c.v. supporting/**
- certificate_of_service.md
- certificate_of_eservice.md
- notice_to_bi_adjuster.md

##### C.1.d. workflows/
**C.1.d.i. draft_file_complaint/**
- workflow.md
- skills/
  - complaint-drafting/
    - skill.md
    - references/
      - case-analysis.md
      - causation-framework.md
      - damages-calculation.md
      - defendant-research.md
      - prayer-calculation.md
- templates/
  - complaint_drafting_guide.md
  - summons_template.md
- tools/
  - generate_document.py

**C.1.d.ii. prepare_filing_package/**
- workflow.md
- skills/
  - case-filing/
    - skill.md
    - references/
      - court-requirements.md
      - e-filing.md
- templates/
  - civil_cover_sheet.md

**C.1.d.iii. serve_defendant/**
- workflow.md
- templates/
  - summons_template.md

#### C.2. 7_2_answer_discovery/
##### C.2.a. README.md
##### C.2.b. landmarks.md
##### C.2.c. workflows/
**C.2.c.i. answer_response/**
- workflow.md

**C.2.c.ii. initial_discovery/**
- workflow.md
- skills/
  - discovery-requests/
    - skill.md
    - references/
      - interrogatories.md
      - production-requests.md
- templates/
  - interrogatories_TEMPLATE.md
  - request_for_production_TEMPLATE.md

#### C.3. 7_3_depositions/
##### C.3.a. README.md
##### C.3.b. landmarks.md
##### C.3.c. workflows/
**C.3.c.i. deposition_prep/**
- workflow.md
- skills/
  - deposition-preparation/
    - skill.md
    - references/
      - client-prep.md
      - expert-prep.md
- templates/
  - deposition_notice.md

**C.3.c.ii. expert_witness/**
- workflow.md

#### C.4. 7_4_mediation/
##### C.4.a. README.md
##### C.4.b. landmarks.md
##### C.4.c. workflows/
**C.4.c.i. mediation_prep/**
- workflow.md
- skills/
  - mediation-preparation/
    - skill.md
- templates/
  - mediation_statement.md

#### C.5. 7_5_trial/
##### C.5.a. README.md
##### C.5.b. landmarks.md
##### C.5.c. workflows/
**C.5.c.i. trial_prep/**
- workflow.md
- skills/
  - trial-preparation/
    - skill.md
- templates/
  - witness_list.md
  - exhibit_list.md

---

## IX. phase_8_closed

### A. README.md
### B. landmarks.md
**Landmarks:**
- L8.1: all_obligations_verified
- L8.2: final_letter_sent
- (More landmarks in file)

### C. workflows/
#### C.1. close_case/
##### C.1.a. workflow.md
##### C.1.b. templates/
- closing_letter.md
- file_retention_memo.md

---

## X. Central Resources (workflows/)

### A. skills/
**Global skills directory with manifest**

#### A.1. skills_manifest.json
**Contains 47 skills cataloged**

#### A.2. Phase-specific skill folders/
- phase_0_onboarding/
  - docusign-send/
  - document-intake/
  - document-request/
- phase_1_file_setup/
  - liability-analysis/
  - lor-generator/
  - medical-records-request-setup/
  - pip-application/
  - pip-waterfall/
  - police-report-analysis/
- phase_2_treatment/
  - (Medical monitoring skills)
- phase_3_demand/
  - (Demand preparation skills)
- (etc.)

### B. templates/
**Global templates directory with manifest**

#### B.1. templates_manifest.json
**Template collections:**

#### B.2. complaint/
- base/
  - (11 complaint base templates)
- modules/
  - (8 count modules)
- supporting/
  - (3 supporting documents)

#### B.3. demand/
- demand_template.md
- demand_letter_TEMPLATE.md

#### B.4. deposition/
#### B.5. discovery/
#### B.6. mediation/
#### B.7. medical/
#### B.8. negotiation/
#### B.9. output/

### C. tools/
**Global tools directory with manifest**

#### C.1. tools_manifest.json
**10 tools cataloged**

#### C.2. Tool files/
- create_case.py
- pip_waterfall.py
- lexis_crash_order.py
- read_pdf.py
- docusign_send.py
- docusign_config.py
- chronology_tools.py
- medical_request_generator.py
- generate_demand_pdf.py
- generate_document.py
- firm_config.json

---

## Summary Statistics

### By Phase

| Phase | Workflows | Skills | Templates | Tools | Landmarks |
|-------|-----------|--------|-----------|-------|-----------|
| 0: Onboarding | 2 | 3 | 11 intake forms | 3 | 3 |
| 1: File Setup | 4 | 6 | 5 | 4 | 4 |
| 2: Treatment | 6 | 3 | 5 | 3 | ~6 |
| 3: Demand | 3 | 4 | 3 | 4 | ~6 |
| 4: Negotiation | 3 | 4 | 4 | 1 | ~5 |
| 5: Settlement | 2 | 3 | 3 | 1 | ~6 |
| 6: Lien | 3 | 2 | 3 | 1 | ~5 |
| 7: Litigation | 5 subphases | ~10 | ~15 | 1 | ~15 |
| 8: Closed | 1 | 0 | 2 | 0 | 2-3 |
| **TOTAL** | **~30** | **47** | **~50** | **10** | **~50** |

### Resource Distribution

**Skills:** 47 total
- Cataloged in /workflows/skills/skills_manifest.json
- Stored in phase-specific folders under /workflows/skills/
- Each skill has: skill.md, optional tools/, optional references/

**Templates:** ~50 total
- Cataloged in /workflows/templates/templates_manifest.json
- Organized by collection (complaint, demand, discovery, etc.)
- Mix of .md, .docx, and .pdf formats

**Tools:** 10 total
- Cataloged in /workflows/tools/tools_manifest.json
- All Python scripts (.py files)
- Executable via agent's execute_python_script tool

---

## Key Structural Patterns

### Pattern 1: Phase Folder Structure
```
phase_{num}_{name}/
├── README.md (phase overview)
├── landmarks.md (landmark definitions)
└── workflows/ (or subphases/ for phase 7)
    └── {workflow_name}/
        ├── workflow.md (YAML frontmatter + instructions)
        ├── skills/ (skill references for this workflow)
        ├── templates/ (templates for this workflow)
        └── tools/ (tools for this workflow)
```

### Pattern 2: Skill Structure
```
skills/{phase}/{skill_name}/
├── skill.md (YAML frontmatter + instructions)
├── tools/ (Python scripts)
├── references/ (supporting documentation)
└── templates/ (skill-specific templates)
```

### Pattern 3: Central vs. Embedded Resources

**Centralized:**
- /workflows/skills/ (skills_manifest.json + all skill folders)
- /workflows/templates/ (templates_manifest.json + collections)
- /workflows/tools/ (tools_manifest.json + all tool scripts)

**Embedded (duplicated in workflows):**
- Each workflow has local copies of needed skills/templates/tools
- Allows self-contained workflow execution
- Manifest files track canonical locations

---

## Graph Node Implications

### What Needs to be Created

**1. Definition Nodes (group_id='__workflow_definitions__')**
- 9 Phase nodes
- ~50 Landmark nodes
- ~30 WorkflowDef nodes
- ~100 WorkflowStep nodes (from workflow.md step lists)
- 47 WorkflowSkill nodes (from skills_manifest.json)
- ~50 WorkflowTemplate nodes (from templates_manifest.json)
- 10 WorkflowTool nodes (from tools_manifest.json)

**2. State Nodes (per case)**
- None - state is stored as relationships (IN_PHASE, LANDMARK_STATUS)

**3. Definition Relationships**
- Phase -[HAS_LANDMARK]-> Landmark
- Phase -[NEXT_PHASE]-> Phase
- Phase -[HAS_WORKFLOW]-> WorkflowDef
- Landmark -[ACHIEVED_BY]-> WorkflowDef
- WorkflowDef -[HAS_STEP]-> WorkflowStep
- WorkflowDef -[USES_SKILL]-> WorkflowSkill
- WorkflowDef -[USES_TEMPLATE]-> WorkflowTemplate
- WorkflowDef -[USES_TOOL]-> WorkflowTool

**4. State Relationships (per case, 110 total)**
- Case -[IN_PHASE {entered_at}]-> Phase
- Case -[LANDMARK_STATUS {status, sub_steps, notes}]-> Landmark (×~50 landmarks each)

---

## Files That Will Be Parsed

### JSON Schema Files
1. `/mnt/workspace/workflow_engine/schemas/phase_definitions.json`
2. `/mnt/workspace/workflow_engine/schemas/workflow_definitions.json`
3. `/mnt/workspace/workflow_engine/schemas/resource_mappings.json`

### Markdown Files (Parsed)
4. `/mnt/workspace/workflows/phase_*/landmarks.md` (9 files)
5. `/mnt/workspace/workflows/phase_*/workflows/*/workflow.md` (~30 files)

### Manifest Files (Referenced)
6. `/mnt/workspace/workflows/skills/skills_manifest.json`
7. `/mnt/workspace/workflows/templates/templates_manifest.json`
8. `/mnt/workspace/workflows/tools/tools_manifest.json`

---

## Next Step

The `ingest_workflow_definitions.py` script will parse all these files and create the corresponding graph nodes and relationships.

**Ready to proceed?**
