# Roscoe Knowledge Graph - Complete Schema
**Generated from:** `graphiti_client.py`
**Entity Types:** 102
**Relationship Types:** 63

---
## Entity Types

### Core Case
#### `Case`
**Description:** A personal injury case - immutable facts only. Name is set explicitly (not auto-generated) (e.g., 'Christopher-Lanier-MVA-6-28-2025').

**Properties:**
- `case_type` (str): Type: MVA, Premise, WC, Med-Mal, Dog-Bite, Slip-Fall
- `accident_date` (date): Date of accident/incident
- `sol_date` (date): Statute of limitations deadline

#### `Client`
**Description:** A client/plaintiff in a personal injury case. Name is set explicitly (not auto-generated).

**Properties:**
- `phone` (str): Phone number
- `email` (str): Email address
- `address` (str): Mailing address
- `date_of_birth` (date): Date of birth

#### `Defendant`
**Description:** The at-fault party in a case. Name is set explicitly (not auto-generated).

**Properties:**
- `insurer` (str): Defendant's insurance company
- `policy_number` (str): Policy number for defendant's coverage
- `driver_license` (str): Driver's license number
- `phone` (str): Phone number
- `address` (str): Address
- `project_name` (str): Associated case name


### Insurance
#### `Insurer`
**Description:** An insurance company. Name is set explicitly (not auto-generated) (e.g., State Farm, Progressive).

**Properties:**
- `phone` (str): Main phone number
- `email` (str): Email address
- `fax` (str): Fax number
- `address` (str): Mailing address

#### `Adjuster`
**Description:** An insurance adjuster handling a claim. Name is set explicitly (not auto-generated).

**Properties:**
- `phone` (str): Phone number
- `email` (str): Email address
- `fax` (str): Fax number

#### `PIPClaim`
**Description:** A Personal Injury Protection (PIP) insurance claim - first-party no-fault coverage.

**Properties:**
- `claim_number` (str): PIP claim number
- `insurer_name` (str): Insurance company name
- `adjuster_name` (str): Assigned adjuster name
- `policy_limit` (float): PIP policy limit amount
- `amount_paid` (float): Amount paid out so far
- `exhausted` (bool): Whether PIP benefits are exhausted
- `lor_sent_date` (date): Date letter of representation was sent
- `coverage_confirmation` (str): Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'
- `project_name` (str): Associated case name

#### `BIClaim`
**Description:** A Bodily Injury (BI) liability insurance claim - third-party claim against at-fault driver.

**Properties:**
- `claim_number` (str): BI claim number
- `insurer_name` (str): Insurance company name
- `adjuster_name` (str): Assigned adjuster name
- `policy_limit` (float): BI policy limit amount
- `demand_amount` (float): Amount demanded
- `demand_sent_date` (date): Date demand was sent
- `current_offer` (float): Current settlement offer
- `settlement_amount` (float): Final settlement amount
- `settlement_date` (date): Date of settlement
- `lor_sent_date` (date): Date letter of representation was sent
- `coverage_confirmation` (str): Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'
- `is_active_negotiation` (bool): Whether actively negotiating settlement
- `project_name` (str): Associated case name

#### `UMClaim`
**Description:** An Uninsured Motorist (UM) insurance claim - when at-fault driver has no insurance.

**Properties:**
- `claim_number` (str): UM claim number
- `insurer_name` (str): Client's insurance company name
- `adjuster_name` (str): Assigned adjuster name
- `policy_limit` (float): UM policy limit amount
- `demand_amount` (float): Amount demanded
- `demand_sent_date` (date): Date demand was sent
- `current_offer` (float): Current settlement offer
- `settlement_amount` (float): Final settlement amount
- `settlement_date` (date): Date of settlement
- `coverage_confirmation` (str): Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'
- `is_active_negotiation` (bool): Whether actively negotiating settlement
- `project_name` (str): Associated case name

#### `UIMClaim`
**Description:** An Underinsured Motorist (UIM) insurance claim - when at-fault driver's coverage is insufficient.

**Properties:**
- `claim_number` (str): UIM claim number
- `insurer_name` (str): Client's insurance company name
- `adjuster_name` (str): Assigned adjuster name
- `policy_limit` (float): UIM policy limit amount
- `bi_settlement` (float): Amount recovered from BI claim
- `demand_amount` (float): Amount demanded
- `demand_sent_date` (date): Date demand was sent
- `current_offer` (float): Current settlement offer
- `settlement_amount` (float): Final settlement amount
- `settlement_date` (date): Date of settlement
- `coverage_confirmation` (str): Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'
- `is_active_negotiation` (bool): Whether actively negotiating settlement
- `project_name` (str): Associated case name

#### `WCClaim`
**Description:** A Workers Compensation (WC) insurance claim - workplace injury coverage.

**Properties:**
- `claim_number` (str): WC claim number
- `insurer_name` (str): Workers comp insurance company name
- `adjuster_name` (str): Assigned adjuster name
- `employer_name` (str): Employer name
- `injury_date` (date): Date of workplace injury
- `ttd_rate` (float): Temporary Total Disability weekly rate
- `medical_paid` (float): Medical expenses paid by WC
- `settlement_amount` (float): Final settlement amount
- `settlement_date` (date): Date of settlement
- `coverage_confirmation` (str): Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'
- `is_active_negotiation` (bool): Whether actively negotiating settlement
- `project_name` (str): Associated case name

#### `MedPayClaim`
**Description:** A Medical Payments (MedPay) insurance claim - first-party medical expense coverage.

**Properties:**
- `claim_number` (str): MedPay claim number
- `insurer_name` (str): Insurance company name
- `adjuster_name` (str): Assigned adjuster name
- `policy_limit` (float): MedPay policy limit amount
- `amount_paid` (float): Amount paid out so far
- `exhausted` (bool): Whether MedPay benefits are exhausted
- `coverage_confirmation` (str): Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'
- `project_name` (str): Associated case name


### Medical
#### `HealthSystem`
**Description:** Parent healthcare organization (UofL Health, Norton Healthcare, etc.). Individual locations connect via PART_OF. Name is set explicitly (not auto-generated).

**Properties:**
- `medical_records_endpoint` (str): Central endpoint for medical records requests
- `billing_endpoint` (str): Central endpoint for billing/medical bills
- `phone` (str): Main phone number
- `fax` (str): Main fax number
- `email` (str): Contact email
- `address` (str): Corporate headquarters address
- `website` (str): Website URL

#### `MedicalProvider`
**Description:** A specific medical provider location (hospital, clinic, imaging center, etc.). Connected to HealthSystem via PART_OF if part of larger system. Name is set explicitly (not auto-generated).

**Properties:**
- `specialty` (str): Medical specialty: chiropractic, orthopedic, PT, pain management, primary care, ER, imaging, etc.
- `phone` (str): Phone number
- `email` (str): Email address
- `fax` (str): Fax number
- `address` (str): Address
- `provider_type` (str): Type: hospital, clinic, imaging_center, therapy_center, etc.
- `parent_system` (str): Parent HealthSystem name if applicable
- `medical_records_endpoint` (str): Where to request records (overrides parent HealthSystem if set)
- `billing_endpoint` (str): Where to request bills (overrides parent HealthSystem if set)

#### `Doctor`
**Description:** An individual physician. Name is set explicitly (not auto-generated). Connected to MedicalProvider via WORKS_AT.

**Properties:**
- `specialty` (str): Medical specialty: orthopedic, neurology, pain management, etc.
- `credentials` (str): Credentials: MD, DO, DC, PT, etc.
- `phone` (str): Phone number
- `email` (str): Email address
- `npi` (str): National Provider Identifier

#### `Lien`
**Description:** A lien on a specific case. Name is set explicitly (not auto-generated). Lienholder identified via HELD_BY relationship.

**Properties:**
- `amount` (float): Original lien amount
- `account_number` (str): Account or reference number
- `project_name` (str): Associated case name
- `date_notice_received` (date): When lien notice was received
- `date_lien_paid` (date): When lien was satisfied
- `reduction_amount` (float): Negotiated reduction amount

#### `LienHolder`
**Description:** An entity holding a lien (hospital, ERISA plan, Medicare, collection agency, litigation funding company, etc.). Name is set explicitly (not auto-generated).

**Properties:**
- `lien_type` (str): Primary lien type: medical, ERISA, Medicare, Medicaid, child_support, case_funding, collection, other
- `phone` (str): Phone number
- `email` (str): Email address
- `fax` (str): Fax number
- `address` (str): Address


### Legal/Courts
#### `LawFirm`
**Description:** A law firm. Name is set explicitly (not auto-generated).

**Properties:**
- `phone` (str): Main phone number
- `fax` (str): Fax number
- `address` (str): Address

#### `Attorney`
**Description:** An attorney on a case. Name is set explicitly (not auto-generated).

**Properties:**
- `role` (str): Role: plaintiff_counsel, defense_counsel, co_counsel, referring_attorney
- `bar_number` (str): State bar number
- `firm_name` (str): Law firm name
- `phone` (str): Phone number
- `email` (str): Email address

#### `CaseManager`
**Description:** Law firm case manager or paralegal. Name is set explicitly.

**Properties:**
- `role` (str): Role: case_manager, paralegal, legal_assistant
- `firm_name` (str): Law firm name
- `phone` (str): Phone number
- `email` (str): Email address

#### `Court`
**Description:** A court where a case is filed. Name is set explicitly (not auto-generated).

**Properties:**
- `county` (str): County
- `state` (str): State
- `case_number` (str): Court case number
- `division` (str): Division: civil, circuit, district, etc.
- `phone` (str): Court clerk phone number
- `email` (str): Court clerk email
- `address` (str): Court mailing address

#### `CircuitDivision`
**Description:** Circuit court division. Name format: 'County Circuit Court, Division II'. Connected to Court via PART_OF, Judge via PRESIDES_OVER.

**Properties:**
- `division_number` (str): Division number: 01, 02, etc.
- `court_name` (str): Parent court name
- `circuit_number` (str): Circuit number: 30, 18, etc.
- `local_rules` (str): Division-specific local rules
- `scheduling_preferences` (str): Judge's scheduling preferences
- `mediation_required` (bool): Whether mediation is required before trial

#### `DistrictDivision`
**Description:** District court division. Name format: 'County District Court, Division 1'. Connected to Court via PART_OF, Judge via PRESIDES_OVER.

**Properties:**
- `division_number` (str): Division number: 01, 02, etc.
- `court_name` (str): Parent court name
- `district_number` (str): District number: 30, 18, etc.

#### `AppellateDistrict`
**Description:** Court of Appeals district. Connected to Court of Appeals via PART_OF, Judge via PRESIDES_OVER.

**Properties:**
- `district_number` (str): Appellate district number
- `region` (str): Geographic region served
- `counties` (str): Counties in district

#### `SupremeCourtDistrict`
**Description:** Kentucky Supreme Court district. Justices are elected from districts. Connected to Supreme Court via PART_OF, Justice via PRESIDES_OVER.

**Properties:**
- `district_number` (str): Supreme Court district number (1-7)
- `counties` (str): Counties in district
- `region` (str): Geographic region

#### `CircuitJudge`
**Description:** Circuit court judge. Name is set explicitly (not auto-generated). Connected to Court via PRESIDES_OVER.

**Properties:**
- `county` (str): County or multi-county area served
- `circuit` (str): Circuit number (e.g., Cir. 18, Div. 01)
- `division` (str): Division number
- `phone` (str): Phone number
- `email` (str): Email address
- `address` (str): Chambers address

#### `DistrictJudge`
**Description:** District court judge. Name is set explicitly (not auto-generated). Connected to Court via PRESIDES_OVER.

**Properties:**
- `county` (str): County or multi-county area served
- `district` (str): District number (e.g., Dist. 18, Div. 01)
- `division` (str): Division number
- `phone` (str): Phone number
- `email` (str): Email address
- `address` (str): Chambers address

#### `AppellateJudge`
**Description:** Court of Appeals judge. Name is set explicitly (not auto-generated).

**Properties:**
- `phone` (str): Phone number
- `email` (str): Email address
- `address` (str): Chambers address

#### `SupremeCourtJustice`
**Description:** Kentucky Supreme Court justice. Name is set explicitly (not auto-generated).

**Properties:**
- `phone` (str): Phone number
- `email` (str): Email address
- `address` (str): Chambers address

#### `CourtClerk`
**Description:** Circuit or district court clerk. Name is set explicitly (not auto-generated). Connected to Court via WORKS_AT.

**Properties:**
- `clerk_type` (str): Type: circuit, district
- `county` (str): County served
- `phone` (str): Phone number
- `email` (str): Email address
- `address` (str): Office address

#### `MasterCommissioner`
**Description:** Court-appointed master commissioner. Name is set explicitly (not auto-generated). Connected to Court via APPOINTED_BY.

**Properties:**
- `county` (str): County served
- `phone` (str): Phone number
- `email` (str): Email address
- `address` (str): Office address

#### `CourtAdministrator`
**Description:** Court administrator or staff. Name is set explicitly (not auto-generated). Connected to Court via WORKS_AT.

**Properties:**
- `role` (str): Specific role or title
- `phone` (str): Phone number
- `email` (str): Email address
- `address` (str): Office address

#### `Pleading`
**Description:** A litigation pleading or court filing. Name is set explicitly (not auto-generated) (title).

**Properties:**
- `pleading_type` (str): Type: complaint, answer, motion, discovery_request, discovery_response, subpoena, order, judgment
- `filed_date` (date): Date filed
- `due_date` (date): Response due date if applicable
- `filed_by` (str): Who filed it: plaintiff, defendant


### Professional Services
#### `Expert`
**Description:** An expert witness (vocational, medical, accident reconstruction, life care planner, etc.). Name is set explicitly (not auto-generated).

**Properties:**
- `expert_type` (str): Type: vocational, medical, accident_reconstruction, life_care_planner, economist, engineering, biomechanics, other
- `credentials` (str): Professional credentials
- `phone` (str): Phone number
- `email` (str): Email address
- `firm_name` (str): Expert firm/organization if applicable
- `hourly_rate` (float): Hourly rate for services

#### `Mediator`
**Description:** A mediator or arbitrator. Name is set explicitly (not auto-generated).

**Properties:**
- `credentials` (str): Credentials: Retired Judge, Esq., etc.
- `phone` (str): Phone number
- `email` (str): Email address
- `firm_name` (str): Mediation service organization if applicable
- `hourly_rate` (float): Hourly rate for mediation services

#### `Witness`
**Description:** A fact witness (not expert). Name is set explicitly (not auto-generated).

**Properties:**
- `witness_type` (str): Type: eyewitness, scene_witness, character_witness, treating_witness, other
- `phone` (str): Phone number
- `email` (str): Email address
- `address` (str): Address
- `relationship_to_case` (str): How they relate to case: bystander, passenger, coworker, etc.

#### `Vendor`
**Description:** A vendor/service provider used in case management (non-professional services). Name is set explicitly (not auto-generated).

**Properties:**
- `vendor_type` (str): Type: towing, court_reporting, investigation, moving, records_retrieval, process_server, litigation_funding, medical_equipment, claims_services, legal_software, other
- `phone` (str): Phone number
- `email` (str): Email address
- `fax` (str): Fax number
- `address` (str): Address


### Documents
#### `Document`
**Description:** A document in the case file system. Name is set explicitly (not auto-generated) (filename).

**Properties:**
- `path` (str): Path relative to case folder
- `document_type` (str): Type: letter_of_rep, demand_package, medical_records, medical_bills, records_request, hipaa, retainer, pleading, discovery, correspondence, evidence
- `file_type` (str): File extension: pdf, docx, jpg, etc.
- `description` (str): Brief description of document contents


### Financial
#### `Expense`
**Description:** A case expense. Name is set explicitly (not auto-generated) (description).

**Properties:**
- `amount` (float): Amount in dollars
- `expense_date` (date): Date of expense
- `category` (str): Category: filing_fee, service_fee, medical_records, expert, travel, other
- `vendor` (str): Vendor/payee name

#### `Settlement`
**Description:** Final settlement breakdown for a resolved case. Name is set explicitly (not auto-generated).

**Properties:**
- `gross_amount` (float): Gross settlement amount
- `attorney_fee` (float): Attorney fee amount
- `expenses_total` (float): Total case expenses
- `liens_total` (float): Total liens paid
- `net_to_client` (float): Net amount to client
- `settlement_date` (date): Date of settlement


### Organizations
#### `Organization`
**Description:** A generic organization not fitting other specific types. Name is set explicitly (not auto-generated).

**Properties:**
- `org_type` (str): Type: law_firm, medical_practice, insurance_company, government, vendor, trucking, other
- `phone` (str): Main phone number
- `email` (str): Email address
- `fax` (str): Fax number
- `address` (str): Address


### Workflow
#### `Phase`
**Description:** A case lifecycle phase (e.g., file_setup, treatment, negotiation). Name is set explicitly.

**Properties:**
- `display_name` (str): Human-readable phase name
- `description` (str): Description of the phase
- `order` (int): Phase order in lifecycle (0-8)
- `track` (str): Track: pre_litigation, litigation, settlement, closed
- `next_phase` (str): Default next phase name

#### `SubPhase`
**Description:** A sub-phase within litigation (e.g., complaint, discovery, trial). Name is set explicitly.

**Properties:**
- `display_name` (str): Human-readable sub-phase name
- `parent_phase` (str): Parent phase name (litigation)
- `order` (int): Sub-phase order (1-5)
- `description` (str): Description of the sub-phase

#### `Landmark`
**Description:** A checkpoint within a phase that must be verified before advancing. Name is set explicitly.

**Properties:**
- `landmark_id` (str): Unique landmark identifier (e.g., 'retainer_signed')
- `display_name` (str): Human-readable name
- `phase` (str): Phase this landmark belongs to
- `subphase` (str): SubPhase this landmark belongs to (for litigation landmarks)
- `description` (str): What this landmark verifies
- `landmark_type` (str): Type: document, entity, communication, verification
- `is_hard_blocker` (bool): If true, MUST complete before advancing phase
- `can_override` (bool): If true, user can manually override if stuck
- `verification_method` (str): How to verify: 'graph_query', 'manual', 'hybrid'
- `verification_entities` (str): JSON list of entity types that satisfy this landmark
- `verification_relationships` (str): JSON list of required relationships
- `verification_query` (str): Cypher query to verify completion (must return 'verified' boolean)
- `auto_verify` (bool): If true, system auto-updates status when verification query passes
- `sub_steps` (str): JSON dict of sub-steps {step_name: description}
- `parent_landmark` (str): Parent landmark ID for sub-landmarks
- `mandatory` (bool): DEPRECATED: Use is_hard_blocker instead
- `verification_fields` (str): DEPRECATED: Use verification_query instead

#### `WorkflowDef`
**Description:** A workflow definition within a phase. Name is set explicitly.

**Properties:**
- `display_name` (str): Human-readable workflow name
- `phase` (str): Phase this workflow belongs to
- `subphase` (str): SubPhase this workflow belongs to (for litigation workflows)
- `description` (str): What this workflow accomplishes
- `trigger` (str): When this workflow is triggered
- `prerequisites` (str): What must be complete before starting
- `instructions_path` (str): Path to workflow.md with detailed instructions

#### `WorkflowStep`
**Description:** A step within a workflow. Name is set explicitly.

**Properties:**
- `step_id` (str): Step identifier within workflow
- `workflow` (str): Parent workflow name
- `description` (str): What this step does
- `owner` (str): Who executes: 'agent' or 'user'
- `can_automate` (bool): Whether agent can execute without user
- `prompt_user` (str): Question to ask user if needed
- `completion_check` (str): Condition to verify step completion
- `order` (int): Step order within workflow

#### `WorkflowChecklist`
**Description:** A procedural checklist for completing a task. Name is set explicitly.

**Properties:**
- `path` (str): Path to checklist file
- `when_to_use` (str): When to use this checklist
- `related_workflow` (str): Associated workflow name

#### `WorkflowSkill`
**Description:** An agent skill that can be used in workflows. Name is set explicitly.

**Properties:**
- `path` (str): Path to skill.md file
- `description` (str): What this skill does
- `capabilities` (str): List of capabilities
- `agent_ready` (bool): Whether skill is ready for agent use
- `quality_score` (float): Quality score 0-5

#### `WorkflowTemplate`
**Description:** A document template used in workflows. Name is set explicitly.

**Properties:**
- `path` (str): Path to template file
- `purpose` (str): What this template is for
- `file_type` (str): File type: docx, pdf, md
- `placeholders` (str): Placeholder fields in template

#### `WorkflowTool`
**Description:** A Python tool used in workflows. Name is set explicitly.

**Properties:**
- `path` (str): Path to Python script
- `purpose` (str): What this tool does

#### `LandmarkStatus`
**Description:** Tracks completion status of a landmark for a specific case. Name is set explicitly.

**Properties:**
- `case_name` (str): Case this status belongs to
- `landmark_id` (str): Landmark this status tracks
- `status` (str): Status: complete, incomplete, in_progress, not_started, not_applicable
- `sub_steps` (str): JSON dict tracking sub-step completion for composite landmarks
- `notes` (str): Notes about current status or blockers
- `completed_at` (datetime): When landmark was completed
- `updated_at` (datetime): Last update timestamp
- `updated_by` (str): Who updated: agent, user, system
- `version` (int): Version number for audit trail
- `archived_at` (datetime): When this version was superseded

#### `LandmarkStatus`
**Description:** Case has a landmark with a status.

**Properties:**
- `status` (str): Status: complete, incomplete, in_progress, not_applicable
- `completed_at` (datetime): When landmark was completed
- `notes` (str): Notes about completion

---

## Relationship Types

### `About`
- `(Episode)-[:About]->(Adjuster, AppellateDistrict, AppellateJudge, Attorney, BIClaim, Bill, CaseManager, CircuitDivision, CircuitJudge, Client, Community, CorrespondenceDocument, Court, CourtAdministrator, CourtClerk, Defendant, DistrictDivision, DistrictJudge, Doctor, Expert, HealthSystem, InsuranceDocument, Insurer, LetterOfRepresentation, Lien, LienHolder, MasterCommissioner, MedPayClaim, Mediator, MedicalBills, MedicalProvider, MedicalRecords, MedicalRecordsRequest, Negotiation, Organization, PIPClaim, Pleading, Settlement, SupremeCourtDistrict, SupremeCourtJustice, UIMClaim, UMClaim, Vendor, WCClaim, Witness)`

### `AchievedBy`
- `(Landmark)-[:AchievedBy]->(WorkflowDef)`

### `Achieves`
- `(WorkflowDef)-[:Achieves]->(Landmark)`

### `AppointedBy`
- `(MasterCommissioner)-[:AppointedBy]->(Court)`

### `AssignedAdjuster`
- `(BIClaim)-[:AssignedAdjuster]->(Adjuster)`
- `(PIPClaim)-[:AssignedAdjuster]->(Adjuster)`
- `(UIMClaim)-[:AssignedAdjuster]->(Adjuster)`
- `(UMClaim)-[:AssignedAdjuster]->(Adjuster)`

### `AssignedTo`
- `(Case)-[:AssignedTo]->(CircuitJudge, DistrictJudge)`

### `BelongsToPhase`
- `(Landmark)-[:BelongsToPhase]->(Phase)`

### `BilledBy`
- `(Bill)-[:BilledBy]->(Attorney, MedicalProvider, Vendor)`

### `CanSkipTo`
- `(Phase)-[:CanSkipTo]->(Phase)`

### `Covers`
- `(BIClaim)-[:Covers]->(Client)`
- `(PIPClaim)-[:Covers]->(Client)`
- `(UIMClaim)-[:Covers]->(Client)`
- `(UMClaim)-[:Covers]->(Client)`
- `(WCClaim)-[:Covers]->(Client)`

### `DefenseCounsel`
- `(Case)-[:DefenseCounsel]->(Attorney)`

### `DefinedInPhase`
- `(WorkflowDef)-[:DefinedInPhase]->(Phase)`

### `FiledClaim`
- `(Client)-[:FiledClaim]->(BIClaim, PIPClaim, UIMClaim, UMClaim, WCClaim)`

### `FiledFor`
- `(Pleading)-[:FiledFor]->(Case)`

### `FiledIn`
- `(Case)-[:FiledIn]->(CircuitDivision, Court, DistrictDivision)`
- `(Pleading)-[:FiledIn]->(Court)`

### `Follows`
- `(Episode)-[:Follows]->(Episode)`

### `ForBill`
- `(Lien)-[:ForBill]->(Bill)`

### `ForClaim`
- `(Negotiation)-[:ForClaim]->(BIClaim, PIPClaim, UIMClaim, UMClaim, WCClaim)`

### `From`
- `(InsuranceDocument)-[:From]->(Insurer)`

### `HandlesInsuranceClaim`
- `(Adjuster)-[:HandlesInsuranceClaim]->(BIClaim, MedPayClaim, PIPClaim, UIMClaim, UMClaim, WCClaim)`

### `HasBill`
- `(Case)-[:HasBill]->(Bill)`

### `HasClaim`
- `(Case)-[:HasClaim]->(BIClaim, MedPayClaim, PIPClaim, UIMClaim, UMClaim, WCClaim)`
- `(Insurer)-[:HasClaim]->(BIClaim, MedPayClaim, PIPClaim, UIMClaim, UMClaim, WCClaim)`

### `HasClient`
- `(Case)-[:HasClient]->(Client)`

### `HasDefendant`
- `(Case)-[:HasDefendant]->(Defendant)`

### `HasDocument`
- `(Case)-[:HasDocument]->(CorrespondenceDocument, Document, Document, InsuranceDocument, LetterOfRepresentation, MedicalBills, MedicalRecords, MedicalRecordsRequest)`

### `HasExpense`
- `(Case)-[:HasExpense]->(Expense)`

### `HasInsurance`
- `(Client)-[:HasInsurance]->(Insurer)`

### `HasLandmark`
- `(Phase)-[:HasLandmark]->(Landmark)`

### `HasLien`
- `(Case)-[:HasLien]->(Lien, Lien)`

### `HasLienFrom`
- `(Case)-[:HasLienFrom]->(LienHolder)`

### `HasMember`
- `(Community)-[:HasMember]->(Attorney, Case, Defendant, Doctor, MedicalProvider)`

### `HasNegotiation`
- `(Case)-[:HasNegotiation]->(Negotiation)`

### `HasStep`
- `(WorkflowDef)-[:HasStep]->(WorkflowStep)`

### `HasSubLandmark`
- `(Landmark)-[:HasSubLandmark]->(Landmark)`

### `HasTreated`
- `(Doctor)-[:HasTreated]->(Client)`
- `(MedicalProvider)-[:HasTreated]->(Client)`

### `HasWitness`
- `(Case)-[:HasWitness]->(Witness)`

### `HasWorkflow`
- `(Phase)-[:HasWorkflow]->(WorkflowDef)`

### `HeldBy`
- `(Lien)-[:HeldBy]->(LienHolder)`

### `InPhase`
- `(Case)-[:InPhase]->(Phase)`

### `InsuredBy`
- `(BIClaim)-[:InsuredBy]->(Insurer)`
- `(MedPayClaim)-[:InsuredBy]->(Insurer)`
- `(PIPClaim)-[:InsuredBy]->(Insurer)`
- `(UIMClaim)-[:InsuredBy]->(Insurer)`
- `(UMClaim)-[:InsuredBy]->(Insurer)`
- `(WCClaim)-[:InsuredBy]->(Insurer)`

### `LandmarkStatus`
- `(Case)-[:LandmarkStatus]->(Landmark)`

### `MemberOf`
- `(Attorney)-[:MemberOf]->(Community)`
- `(Case)-[:MemberOf]->(Community)`
- `(Defendant)-[:MemberOf]->(Community)`
- `(Doctor)-[:MemberOf]->(Community)`
- `(MedicalProvider)-[:MemberOf]->(Community)`

### `Mentions`
- `(Entity)-[:Mentions]->(Entity)`

### `NextPhase`
- `(Phase)-[:NextPhase]->(Phase)`

### `PartOf`
- `(AppellateDistrict)-[:PartOf]->(Court)`
- `(CircuitDivision)-[:PartOf]->(Court)`
- `(DistrictDivision)-[:PartOf]->(Court)`
- `(HealthSystem)-[:PartOf]->(Organization)`
- `(LawFirm)-[:PartOf]->(Organization)`
- `(MedicalProvider)-[:PartOf]->(HealthSystem)`
- `(Organization)-[:PartOf]->(Organization)`
- `(SupremeCourtDistrict)-[:PartOf]->(Court)`

### `PartOfWorkflow`
- `(Episode)-[:PartOfWorkflow]->(WorkflowDef)`

### `PlaintiffIn`
- `(Client)-[:PlaintiffIn]->(Case)`

### `PresidesOver`
- `(AppellateJudge)-[:PresidesOver]->(AppellateDistrict)`
- `(CircuitJudge)-[:PresidesOver]->(CircuitDivision)`
- `(DistrictJudge)-[:PresidesOver]->(DistrictDivision)`
- `(SupremeCourtJustice)-[:PresidesOver]->(SupremeCourtDistrict)`

### `ReceivedFrom`
- `(MedicalBills)-[:ReceivedFrom]->(MedicalProvider)`
- `(MedicalRecords)-[:ReceivedFrom]->(MedicalProvider)`

### `Regarding`
- `(Document)-[:Regarding]->(Case)`

### `RelatesTo`
- `(Entity)-[:RelatesTo]->(Entity)`
- `(Episode)-[:RelatesTo]->(Case)`

### `RepresentedBy`
- `(Case)-[:RepresentedBy]->(Attorney)`

### `RepresentsClient`
- `(Attorney)-[:RepresentsClient]->(Case)`

### `RetainedExpert`
- `(Case)-[:RetainedExpert]->(Expert)`

### `RetainedFor`
- `(Expert)-[:RetainedFor]->(Case)`
- `(Mediator)-[:RetainedFor]->(Case)`

### `RetainedMediator`
- `(Case)-[:RetainedMediator]->(Mediator)`

### `SentTo`
- `(LetterOfRepresentation)-[:SentTo]->(Insurer, LienHolder, MedicalProvider)`
- `(MedicalRecordsRequest)-[:SentTo]->(MedicalProvider)`

### `SettledWith`
- `(Case)-[:SettledWith]->(Settlement)`

### `StepOf`
- `(WorkflowStep)-[:StepOf]->(WorkflowDef)`

### `TreatedBy`
- `(Client)-[:TreatedBy]->(Doctor, MedicalProvider)`

### `TreatingAt`
- `(Case)-[:TreatingAt]->(MedicalProvider, MedicalProvider)`
- `(Client)-[:TreatingAt]->(MedicalProvider)`

### `WitnessFor`
- `(Witness)-[:WitnessFor]->(Case)`

### `WorksAt`
- `(Adjuster)-[:WorksAt]->(Insurer)`
- `(Attorney)-[:WorksAt]->(LawFirm)`
- `(CaseManager)-[:WorksAt]->(LawFirm)`
- `(CourtAdministrator)-[:WorksAt]->(Court)`
- `(CourtClerk)-[:WorksAt]->(Court)`
- `(Doctor)-[:WorksAt]->(MedicalProvider)`
- `(Expert)-[:WorksAt]->(Organization)`
- `(Mediator)-[:WorksAt]->(Organization)`

---

## Professional Relationship Patterns

All professional entities connect to their organizations:

| Person | Organization | Relationship |
|--------|--------------|-------------|
| Attorney | LawFirm | WORKS_AT |
| CaseManager | LawFirm | WORKS_AT |
| Doctor | MedicalProvider | WORKS_AT |
| Adjuster | Insurer | WORKS_AT |
| Expert | Organization | WORKS_AT |
| Mediator | Organization | WORKS_AT |
| CircuitJudge | CircuitDivision | PRESIDES_OVER |
| DistrictJudge | DistrictDivision | PRESIDES_OVER |
| AppellateJudge | AppellateDistrict | PRESIDES_OVER |
| SupremeCourtJustice | SupremeCourtDistrict | PRESIDES_OVER |
| CourtClerk | Court | WORKS_AT |
| MasterCommissioner | Court | APPOINTED_BY |
| CourtAdministrator | Court | WORKS_AT |

## Hierarchical Structures

### Court System:
```
Court
  ↑ [PART_OF]
CircuitDivision/DistrictDivision
  ↑ [PRESIDES_OVER]
Judge
```

### Healthcare System:
```
HealthSystem
  ↑ [PART_OF]
MedicalProvider
  ↑ [WORKS_AT]
Doctor
```

### Law Firm:
```
LawFirm
  ↑ [WORKS_AT]
Attorney/CaseManager
```
