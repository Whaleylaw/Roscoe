# Roscoe Knowledge Graph - Complete Schema (Target State)

**This document represents the COMPLETE schema when all pending entities are ingested.**

**Current State:** 11,166 nodes, 20,805 relationships (26 entity types)
**Target State:** ~57,000 nodes, ~65,000+ relationships (50 entity types)

---

## Entity Types (50 total)

### **Core Case Entities (5)**

#### `Case`
The root entity for each personal injury case.

**Properties:**
- `name` (str): Unique case identifier (e.g., "Alma-Cristobal-MVA-2-15-2024")
- `case_type` (str): MVA, WC, Premise, Med-Mal, S&F, DB
- `accident_date` (date): Date of incident
- `filing_date` (date): Date case filed in court
- `status` (str): active, settled, dismissed, trial
- `created_at` (datetime): When case was created in system
- `embedding` (vecf32): Semantic embedding for search

**Current Count:** 111
**Target Count:** 138 (all cases with episode data)

#### `Client`
The injured party/plaintiff.

**Properties:**
- `name` (str): Client full name
- `phone` (str): Contact phone
- `email` (str): Email address
- `address` (str): Mailing address
- `embedding` (vecf32)

**Current Count:** 105
**Target Count:** 138

#### `Defendant`
The at-fault party or entity.

**Properties:**
- `name` (str): Defendant name
- `phone`, `email`, `address`

**Current Count:** ~10
**Target Count:** ~200 (unique defendants across cases)

#### `Episode`
Timeline narrative event explaining "why/how" something happened.

**Properties:**
- `content` (str): Natural language description
- `raw_content` (str): Original structured text [After we do this initial ingestion, we won't have raw content, so I don't think we are going to need this property.]
- `valid_at` (datetime): When episode occurred
- `invalid_at` (datetime): When episode was superseded
- `author` (str): Who created the episode
- `episode_type` (str): Type of episode
- `case_name` (str): Which case this belongs to
- `source` (str): Source system
- `source_description` (str): Source details
- `embedding` (vecf32): Enriched embedding (content + entity context)

**Current Count:** 0 (Episodic label exists from Graphiti, but not our episodes)
**Target Count:** 13,491

#### `Note` [We don't need this anymore. This has been superseded by episode.]
Timestamped note attached to any entity.

**Properties:**
- `content` (str): Note text
- `created_at` (datetime)
- `author` (str)
- `note_type` (str): general, follow_up, reminder, communication

**Current Count:** 0
**Target Count:** TBD

---

### **Insurance Entities (8)**

#### `Insurer`
Insurance company.

**Properties:**
- `name` (str): Company name
- `phone`, `fax`, `email`, `address`
- `adjuster_phone` (str): Claims department phone

**Current Count:** ~50
**Target Count:** 99

#### `Adjuster`
Insurance adjuster (WORKS_AT → Insurer).

**Properties:**
- `name` (str): Adjuster name
- `phone`, `email`
- `insurer_name` (str): Which insurer they work for

**Current Count:** ~30
**Target Count:** ~150

#### Claim Types:
Each is a distinct entity type (not subclasses):

- **`PIPClaim`** - Personal Injury Protection (first-party no-fault)
- **`BIClaim`** - Bodily Injury (third-party liability)
- **`UMClaim`** - Uninsured Motorist
- **`UIMClaim`** - Underinsured Motorist
- **`WCClaim`** - Workers Compensation
- **`MedPayClaim`** - Medical Payments coverage

**Properties (all claim types):**
- `name` (str): Unique claim identifier
- `claim_number` (str): Insurer's claim number
- `insurer_name` (str): Insurance company
- `adjuster_name` (str): Assigned adjuster
- `coverage_amount` (float): Policy limits
- `coverage_confirmation` (bool): Coverage verified
- `date_opened`, `date_closed`

**Current Count:** ~150 total claims across types
**Target Count:** ~300

---

### **Medical Entities (5)**

#### `HealthSystem`
Parent healthcare organization.

**Properties:**
- `name` (str): System name (e.g., "Norton Healthcare")
- `medical_records_endpoint` (str): Where to request records
- `billing_endpoint` (str): Where to request bills
- `phone`, `fax`, `email`, `address`
- `website` (str)

**Current Count:** 0
**Target Count:** 5 (Norton, UofL, Baptist, CHI Saint Joseph, St. Elizabeth)

#### `MedicalProvider`
Specific hospital, clinic, or medical facility (PART_OF → HealthSystem).

**Properties:**
- `name` (str): Facility name (e.g., "Norton Hospital Downtown") [We need to add the medical records endpoint and billing endpoint here as well.]
- `specialty` (str): Primary specialty
- `provider_type` (str): hospital, clinic, imaging_center, therapy_center
- `phone`, `fax`, `email`, `address`
- `parent_system` (str): HealthSystem name

**Current Count:** 773
**Target Count:** 2,159

#### `Doctor`
Individual physician (WORKS_AT → MedicalProvider).[Can we have multiple work relationships per doctor?]

**Properties:**
- `name` (str): Dr. [Name]
- `specialty` (str): Medical specialty
- `credentials` (str): MD, DO, DC, PT
- `license_number` (str): KY medical board license
- `license_status` (str): Active/Inactive
- `practice_county` (str)
- `phone`, `email`
- `npi` (str): National Provider Identifier
- `medical_school` (str)
- `year_graduated` (str)

**Current Count:** 0
**Target Count:** 20,732 (all KY licensed doctors)

#### `Lien`
Medical lien on a case (HELD_BY → LienHolder or MedicalProvider).[Medical providers do not have liens.] [This isn't just medical liens.]

**Properties:**
- `name` (str): Lien identifier
- `amount` (float): Original lien amount
- `account_number` (str)
- `project_name` (str): Case name
- `date_notice_received` (date)
- `date_lien_paid` (date)
- `reduction_amount` (float): Negotiated reduction

**Current Count:** ~50
**Target Count:** ~200

#### `LienHolder`
Entity holding a lien (hospital, ERISA plan, Medicare, etc.).

**Properties:**
- `name` (str): Lienholder name
- `lien_type` (str): medical, ERISA, Medicare, Medicaid, child_support[We also need a case funding lien.And probably need a generic "other" as well.]
- `phone`, `fax`, `email`, `address`

**Current Count:** ~20
**Target Count:** ~100

---

### **Legal/Court Entities (22)**

#### `LawFirm`[Possibly need a deep research on all of the law firms we have contacts for and get a roster and then create attorney cards for all of them.]
Law firm entity.

**Properties:**
- `name` (str): Firm name
- `phone`, `fax`, `address`
- `aliases` (list): Alternative names (e.g., "BDB Law" for "Blackburn Domene & Burchett")

**Current Count:** ~30
**Target Count:** 36

#### `Attorney`
Lawyer on a case (WORKS_AT → LawFirm).

**Properties:**
- `name` (str): Attorney name
- `role` (str): plaintiff_counsel, defense_counsel, co_counsel
- `bar_number` (str): State bar number
- `firm_name` (str): Law firm
- `phone`, `email`

**Current Count:** ~25
**Target Count:** 34

#### `CaseManager`
Paralegal or case manager (WORKS_AT → LawFirm).

**Properties:**
- `name` (str): Case manager name
- `role` (str): case_manager, paralegal, legal_assistant
- `firm_name` (str): Law firm
- `phone`, `email`

**Current Count:** 8 (Whaley Law Firm staff)
**Target Count:** 8

#### `Court`
Parent court entity (has divisions).

**Properties:**
- `name` (str): Court name (e.g., "Jefferson County Circuit Court")
- `county`, `state`
- `division` (str): Circuit, District, Appellate, Supreme
- `phone`, `email`, `address`

**Current Count:** ~23
**Target Count:** 106

#### `CircuitDivision`
Specific circuit court division (PART_OF → Court, Judge PRESIDES_OVER).

**Properties:**
- `name` (str): "County Circuit Court, Division II"
- `division_number` (str): "01", "02", etc.
- `circuit_number` (str): "30", "18", etc.
- `court_name` (str): Parent court
- `local_rules` (str): Division-specific rules
- `scheduling_preferences` (str): Judge preferences
- `mediation_required` (bool)

**Current Count:** 0
**Target Count:** 86

#### `DistrictDivision`
District court division (PART_OF → Court).

**Properties:**
- `name` (str): "County District Court, Division 1"
- `division_number` (str)
- `district_number` (str)
- `court_name` (str)

**Current Count:** 0
**Target Count:** 94

#### `AppellateDistrict`
Court of Appeals regional office (PART_OF → Court of Appeals).

**Properties:**
- `name` (str): "Kentucky Court of Appeals, Lexington Office"
- `district_number` (str): Office name
- `region` (str): Geographic region
- `counties` (str): Counties served

**Current Count:** 0
**Target Count:** 5

#### `SupremeCourtDistrict`
Supreme Court district (justices elected from districts).

**Properties:**
- `name` (str): "Kentucky Supreme Court, District 3"
- `district_number` (str): "1" through "7"
- `region` (str): Geographic region
- `counties` (str): Counties in district

**Current Count:** 0
**Target Count:** 7

#### `CircuitJudge`
Circuit court judge (PRESIDES_OVER → CircuitDivision).

**Properties:**
- `name` (str): Judge name
- `county` (str): County/counties served
- `circuit` (str): "Cir. 30, Div. 02"
- `division` (str): Division number
- `phone`, `email`, `address`

**Current Count:** 0
**Target Count:** 101

#### `DistrictJudge`
District court judge (PRESIDES_OVER → DistrictDivision).

**Properties:**
- `name` (str): Judge name
- `county` (str)
- `district` (str): "Dist. 30, Div. 01"
- `division` (str)
- `phone`, `email`, `address`

**Current Count:** 0
**Target Count:** 94

#### `AppellateJudge`
Court of Appeals judge (PRESIDES_OVER → AppellateDistrict).

**Properties:**
- `name` (str): Judge name
- `phone`, `email`, `address`

**Current Count:** 0
**Target Count:** 15

#### `SupremeCourtJustice`
Kentucky Supreme Court justice (PRESIDES_OVER → SupremeCourtDistrict).

**Properties:**
- `name` (str): Justice name
- `phone`, `email`, `address`

**Current Count:** 0
**Target Count:** 8

#### `CourtClerk`
Circuit or district court clerk (WORKS_AT → Court).

**Properties:**
- `name` (str): Clerk name
- `clerk_type` (str): circuit, district
- `county` (str)
- `phone`, `email`, `address`

**Current Count:** 0
**Target Count:** 121

#### `MasterCommissioner`
Court-appointed master commissioner (APPOINTED_BY → Court).

**Properties:**
- `name` (str): Commissioner name
- `county` (str)
- `phone`, `email`, `address`

**Current Count:** 0
**Target Count:** 114

#### `CourtAdministrator`
Court administrative staff (WORKS_AT → Court).

**Properties:**
- `name` (str): Administrator name
- `role` (str): Specific role
- `phone`, `email`, `address`

**Current Count:** 0
**Target Count:** 7

#### `Pleading`
Court filing or litigation document.

**Properties:**
- `name` (str): Pleading title
- `pleading_type` (str): complaint, answer, motion, discovery, subpoena, order, judgment
- `filed_date` (date)
- `due_date` (date): Response due date
- `filed_by` (str): plaintiff, defendant

**Current Count:** ~10
**Target Count:** ~500

---

### **Professional Service Entities (4)**

#### `Expert`
Expert witness (WORKS_AT → Organization if applicable).

**Properties:**
- `name` (str): Expert name
- `expert_type` (str): vocational, medical, accident_reconstruction, life_care_planner, economist
- `credentials` (str)
- `phone`, `email`
- `firm_name` (str): Expert firm/organization
- `hourly_rate` (float)

**Current Count:** 0
**Target Count:** ~50

#### `Mediator`
Mediator or arbitrator (WORKS_AT → Organization if applicable).

**Properties:**
- `name` (str): Mediator name
- `credentials` (str): Retired Judge, Esq., etc.
- `phone`, `email`
- `firm_name` (str): Mediation service
- `hourly_rate` (float)

**Current Count:** 0
**Target Count:** 2

#### `Witness`
Fact witness (not expert).

**Properties:**
- `name` (str): Witness name
- `witness_type` (str): eyewitness, scene_witness, character_witness, treating_witness
- `phone`, `email`, `address`
- `relationship_to_case` (str): bystander, passenger, coworker

**Current Count:** 0
**Target Count:** 1

#### `Vendor`
Service provider (non-professional services).

**Properties:**
- `name` (str): Vendor name
- `vendor_type` (str): towing, court_reporting, investigation, records_retrieval, process_server, medical_equipment
- `phone`, `fax`, `email`, `address`

**Current Count:** ~20
**Target Count:** 40

---

### **Organization Entities (2)**

#### `Organization`
Generic organization entity.

**Properties:**
- `name` (str): Organization name
- `org_type` (str): government, non_profit, business
- `phone`, `email`, `address`

**Current Count:** ~200
**Target Count:** 384

#### `Document`
Document in case file system.

**Properties:**
- `name` (str): Filename
- `path` (str): Relative path from case folder
- `document_type` (str): letter_of_rep, demand_package, medical_records, pleading, evidence
- `file_type` (str): pdf, docx, jpg
- `description` (str)

**Current Count:** 0
**Target Count:** TBD (thousands)

---

### **Financial Entities (2)**

#### `Expense`
Case expense.

**Properties:**
- `name` (str): Expense description
- `amount` (float)
- `expense_date` (date)
- `category` (str): filing_fee, service_fee, medical_records, expert, travel
- `vendor` (str): Who was paid

**Current Count:** 0
**Target Count:** TBD

#### `Settlement`
Settlement details.

**Properties:**
- `name` (str): Settlement identifier
- `settlement_amount` (float)
- `settlement_date` (date)
- `demand_amount` (float)
- `date_demand_sent` (date)
- `current_offer` (float)
- `is_active_negotiation` (bool)

**Current Count:** 0
**Target Count:** ~100

---

### **Workflow Entities (10)**

These are structural entities defining the case lifecycle workflow.

#### `Phase`
Major case stage.

**Properties:**
- `name` (str): Intake, Pre-Litigation, Litigation, Settlement, Closed[These are wrong. Look in the Google Cloud bucket here for the phase names.whaley_law_firm/workflows]
- `description` (str)
- `order` (int): Sequence number

**Current Count:** 9
**Target Count:** 9

#### `SubPhase`
Litigation sub-phases.

**Properties:**
- `name` (str): Discovery, Motions, Trial[These are wrong. Look here in the Google Cloud bucket for the phase name. whaley_law_firm/workflows/phase_7_litigation/subphases]
- `parent_phase` (str): Which phase this belongs to
- `order` (int)

**Current Count:** ~5
**Target Count:** ~10

#### `Landmark`
Checkpoint/milestone in case lifecycle.

**Properties:**
- `name` (str): Landmark name
- `landmark_id` (str): Unique ID
- `description` (str)
- `phase` (str): Which phase contains this
- `mandatory` (bool): Required or optional
- `verification_fields` (list): What to check for completion
- `parent_landmark` (str): For composite landmarks

**Current Count:** 82
**Target Count:** 82

#### `LandmarkStatus`
Tracks completion of a landmark for a specific case.

**Properties:**
- `case_name` (str): Which case
- `landmark_id` (str): Which landmark
- `status` (str): complete, incomplete, in_progress, not_started, not_applicable
- `sub_steps` (JSON): Composite landmark tracking
- `notes` (str)
- `completed_at` (datetime)
- `updated_at` (datetime)
- `updated_by` (str): agent, user, system
- `version` (int): Audit trail
- `archived_at` (datetime): When superseded

**Current Count:** 9,102 (111 cases × 82 landmarks)
**Target Count:** 11,316 (138 cases × 82 landmarks)

#### `WorkflowDef`, `WorkflowStep`, `WorkflowChecklist`, `WorkflowSkill`, `WorkflowTemplate`, `WorkflowTool`[Please add the properties of these so I can see.]
Workflow definition entities (structural, not case-specific).

**Current Count:** ~50 total
**Target Count:** ~100

---

## Relationship Types (51 total)

### **Case Relationships (9)**

- **`HAS_CLIENT`**: (Case)-[HAS_CLIENT]->(Client)
- **`HAS_DEFENDANT`**: (Case)-[HAS_DEFENDANT]->(Defendant)
- **`HAS_CLAIM`**: (Case)-[HAS_CLAIM]->(PIPClaim/BIClaim/etc.)
- **`HAS_LIEN`**: (Case)-[HAS_LIEN]->(Lien)
- **`HAS_LIEN_FROM`**: (Case)-[HAS_LIEN_FROM]->(LienHolder)
- **`FILED_IN`**: (Case)-[FILED_IN]->(CircuitDivision/DistrictDivision)
- **`ASSIGNED_TO`**: (Case)-[ASSIGNED_TO]->(Judge)
- **`HAS_DOCUMENT`**: (Case)-[HAS_DOCUMENT]->(Document)
- **`HAS_EXPENSE`**: (Case)-[HAS_EXPENSE]->(Expense)
- **`SETTLED_WITH`**: (Case)-[SETTLED_WITH]->(Settlement)

### **Client Relationships (2)**

- **`PLAINTIFF_IN`**: (Client)-[PLAINTIFF_IN]->(Case)
- **`TREATING_AT`**: (Client)-[TREATING_AT]->(MedicalProvider)

### **Medical Relationships (6)**

- **`PART_OF`**: (MedicalProvider)-[PART_OF]->(HealthSystem)
- **`WORKS_AT`**: (Doctor)-[WORKS_AT]->(MedicalProvider)
- **`TREATED_BY`**: (MedicalProvider/Doctor)-[TREATED_BY]->(Client)[This sounds backwards. Shouldn't it be something like "treated" or "has treated?"So medical provider doctor has treated client.Client treated by medical provider doctor.]
- **`HELD_BY`**: (Lien)-[HELD_BY]->(LienHolder or MedicalProvider)[We don't need this.]
- **`HOLDS`**: (LienHolder)-[HOLDS]->(Lien)[We don't need this.][But there probably needs to be a relationship though to their bill, which is different than a lien.]

### **Insurance Relationships (7)**[Where is the relationship to the client?]

- **`INSURED_BY`**: (Claim)-[INSURED_BY]->(Insurer)
- **`HAS_CLAIM`**: (Insurer)-[HAS_CLAIM]->(Claim)
- **`ASSIGNED_ADJUSTER`**: (Claim)-[ASSIGNED_ADJUSTER]->(Adjuster)
- **`HANDLES_CLAIM`**: (Adjuster)-[HANDLES_CLAIM]->(Claim)
- **`WORKS_AT`**: (Adjuster)-[WORKS_AT]->(Insurer)

### **Legal/Court Relationships (14)**

**Attorney/Firm:**
- **`WORKS_AT`**: (Attorney/CaseManager)-[WORKS_AT]->(LawFirm)
- **`REPRESENTS_CLIENT`**: (Attorney)-[REPRESENTS_CLIENT]->(Case)
- **`DEFENSE_COUNSEL`**: (Case)-[DEFENSE_COUNSEL]->(Attorney)
- **`REPRESENTED_BY`**: (Case)-[REPRESENTED_BY]->(Attorney)

**Court Structure:**
- **`PART_OF`**: (Division)-[PART_OF]->(Court)
- **`PRESIDES_OVER`**: (Judge)-[PRESIDES_OVER]->(Division)
- **`FILED_IN`**: (Case/Pleading)-[FILED_IN]->(Division/Court)

**Court Personnel:**
- **`WORKS_AT`**: (CourtClerk/CourtAdministrator)-[WORKS_AT]->(Court)
- **`APPOINTED_BY`**: (MasterCommissioner)-[APPOINTED_BY]->(Court)

**Pleadings:**
- **`FILED_FOR`**: (Pleading)-[FILED_FOR]->(Case)

### **Professional Service Relationships (6)**

- **`WORKS_AT`**: (Expert/Mediator)-[WORKS_AT]->(Organization)
- **`RETAINED_FOR`**: (Expert/Mediator)-[RETAINED_FOR]->(Case)
- **`RETAINED_EXPERT`**: (Case)-[RETAINED_EXPERT]->(Expert)
- **`RETAINED_MEDIATOR`**: (Case)-[RETAINED_MEDIATOR]->(Mediator)
- **`WITNESS_FOR`**: (Witness)-[WITNESS_FOR]->(Case)
- **`HAS_WITNESS`**: (Case)-[HAS_WITNESS]->(Witness)

### **Episode Relationships (3)**

- **`RELATES_TO`**: (Episode)-[RELATES_TO]->(Case) - Every episode links to its case
- **`ABOUT`**: (Episode)-[ABOUT]->(Any Entity) - Episode discusses entity (40,605 proposed)
- **`FOLLOWS`**: (Episode)-[FOLLOWS]->(Episode) - Sequential/topical links
- **`PART_OF_WORKFLOW`**: (Episode)-[PART_OF_WORKFLOW]->(WorkflowDef)

### **Workflow Relationships (10)**

- **`IN_PHASE`**: (Case)-[IN_PHASE]->(Phase)
- **`HAS_STATUS`**: (Case)-[HAS_STATUS]->(LandmarkStatus)
- **`FOR_LANDMARK`**: (LandmarkStatus)-[FOR_LANDMARK]->(Landmark)
- **`HAS_LANDMARK`**: (Phase)-[HAS_LANDMARK]->(Landmark)
- **`NEXT_PHASE`**: (Phase)-[NEXT_PHASE]->(Phase)
- **`HAS_SUB_LANDMARK`**: (Landmark)-[HAS_SUB_LANDMARK]->(Landmark)
- **`HAS_SUBPHASE`**: (Phase)-[HAS_SUBPHASE]->(SubPhase)
- **`HAS_WORKFLOW`**: (Phase)-[HAS_WORKFLOW]->(WorkflowDef)
- **`USES_TEMPLATE`**: (WorkflowDef)-[USES_TEMPLATE]->(WorkflowTemplate)
- **`HAS_MEMBER`**: (Community)-[HAS_MEMBER]->(Entity) - Graphiti communities[We aren't using Graphiti, but maybe we can recreate because I like the idea of the communities.]

### **Organization Relationships (1)**

- **`PART_OF`**: (Organization)-[PART_OF]->(Organization) - Hierarchies

---

## Hierarchical Structures

### **Healthcare System:**
```
HealthSystem: "Norton Healthcare"
  ↑ [PART_OF]
MedicalProvider: "Norton Hospital Downtown"
  ↑ [WORKS_AT]
Doctor: "Dr. Smith"

Client -[TREATING_AT]→ MedicalProvider
```

### **Court System:**
```
Court: "Jefferson County Circuit Court"
  ↑ [PART_OF]
CircuitDivision: "Jefferson County Circuit Court, Division II"
  ↑ [PRESIDES_OVER]
CircuitJudge: "Annie O'Connell"

Case -[FILED_IN]→ CircuitDivision
```

### **Law Firm:**
```
LawFirm: "The Whaley Law Firm"
  ↑ [WORKS_AT]
Attorney/CaseManager: "Aaron G. Whaley", "Sarena Tuttle"

Case ←[REPRESENTS_CLIENT]- Attorney
```

### **Insurance:**
```
Insurer: "State Farm"
  ↑ [WORKS_AT]
Adjuster: "John Smith"

Case -[HAS_CLAIM]→ BIClaim -[INSURED_BY]→ Insurer
BIClaim -[ASSIGNED_ADJUSTER]→ Adjuster
```

---

## Complete Entity Count (Target)

| Entity Type | Current | Target | Source |
|-------------|---------|--------|--------|
| **Doctors** | 0 | 20,732 | KY Medical Board |
| **LandmarkStatus** | 9,102 | 11,316 | Workflow state (138 cases × 82) |
| **Episodes** | 0 | 13,491 | Processed episode data |
| **MedicalProvider** | 773 | 2,159 | Healthcare systems import |
| **Organizations** | 200 | 384 | Directory + case data |
| **Court Divisions** | 0 | 192 | Extracted from judges |
| **Cases** | 111 | 138 | Episode data |
| **Clients** | 105 | 138 | Case data |
| **CircuitJudge** | 0 | 101 | KY Court directory |
| **Courts** | 23 | 106 | KY Court system |
| **DistrictJudge** | 0 | 94 | KY Court directory |
| **Insurers** | 50 | 99 | Case data |
| **Vendors** | 20 | 40 | Directory |
| **Law Firms** | 30 | 36 | Case data |
| **Attorneys** | 25 | 34 | Case data |
| **... (others)** | ... | ... | ... |
| **TOTAL** | **~11,200** | **~57,000** | All sources |

---

## Complete Relationship Count (Target)

| Relationship Type | Current | Target | Description |
|-------------------|---------|--------|-------------|
| **ABOUT** | 0 | 40,605 | Episode → Entity |
| **HAS_STATUS** | 9,102 | 11,316 | Case → LandmarkStatus |
| **WORKS_AT** | ~100 | 21,500+ | Doctor/Attorney/Judge → Org |
| **PART_OF** | ~50 | 2,500+ | Division→Court, Provider→System |
| **PRESIDES_OVER** | 0 | 300+ | Judge → Division |
| **TREATING_AT** | ~200 | ~500 | Client → Provider |
| **HAS_CLAIM** | ~150 | ~300 | Case → Claim |
| **... (others)** | ... | ... | ... |
| **TOTAL** | **~20,800** | **~65,000+** | All relationships |

---

## Query Examples (Target State)

### **Medical Records Request:**
```cypher
MATCH (c:Client {name: "Amy Mills"})-[:TREATING_AT]->(loc:MedicalProvider)
      -[:PART_OF]->(system:HealthSystem)
RETURN DISTINCT
  system.name,
  system.medical_records_endpoint,
  collect(loc.name) as locations_treated
```

### **Cases by Judge:**
```cypher
MATCH (c:Case)-[:FILED_IN]->(d:CircuitDivision)
      <-[:PRESIDES_OVER]-(j:CircuitJudge {name: "Annie O'Connell"})
RETURN c.name, c.status, c.accident_date
ORDER BY c.accident_date DESC
```

### **Doctor's Employer:**
```cypher
MATCH (d:Doctor {name: "Dr. Wallace L. Huff Jr."})-[:WORKS_AT]->(loc:MedicalProvider)
      -[:PART_OF]->(system:HealthSystem)
RETURN loc.name, system.name
```

### **Find All Episodes About an Entity:**
```cypher
MATCH (ep:Episode)-[:ABOUT]->(e:MedicalProvider {name: "Norton Hospital Downtown"})
RETURN ep.content, ep.valid_at, ep.author
ORDER BY ep.valid_at DESC
```

### **Semantic Search Across Episodes:**
```cypher
CALL db.idx.vector.queryNodes(
  'episode_embeddings',
  5,
  vecf32($query_embedding)
) YIELD node, score
RETURN node.content, node.valid_at, score
```

### **Settlement Analytics by Judge:**
```cypher
MATCH (c:Case)-[:FILED_IN]->(d:CircuitDivision)
      <-[:PRESIDES_OVER]-(j:CircuitJudge {name: "Annie O'Connell"})
MATCH (c)-[:SETTLED_WITH]->(s:Settlement)
WHERE s.settlement_date >= date('2020-01-01')
RETURN
  j.name,
  d.name,
  count(c) as total_settlements,
  avg(s.amount) as avg_settlement,
  percentileCont(s.amount, 0.5) as median_settlement,
  sum(s.amount) as total_recovered
```

### **Find Treating Doctors:**
```cypher
MATCH (c:Client {name: "Amy Mills"})-[:TREATING_AT]->(loc:MedicalProvider)
      <-[:WORKS_AT]-(doc:Doctor)
RETURN doc.name, doc.specialty, loc.name as location
```

### **Division Local Rules:**
```cypher
MATCH (d:CircuitDivision {name: "Jefferson County Circuit Court, Division II"})
RETURN
  d.local_rules,
  d.scheduling_preferences,
  d.mediation_required
```

---

## Professional Relationship Patterns (13 types)

All professional entities connect to organizations:

| Person Entity | Organization Entity | Relationship | Count |
|---------------|---------------------|--------------|-------|
| Attorney | LawFirm | WORKS_AT | ~34 |
| CaseManager | LawFirm | WORKS_AT | 8 |
| Doctor | MedicalProvider | WORKS_AT | 20,732 |
| Adjuster | Insurer | WORKS_AT | ~150 |
| Expert | Organization | WORKS_AT | ~50 |
| Mediator | Organization | WORKS_AT | 2 |
| CircuitJudge | CircuitDivision | PRESIDES_OVER | 101 |
| DistrictJudge | DistrictDivision | PRESIDES_OVER | 94 |
| AppellateJudge | AppellateDistrict | PRESIDES_OVER | 15 |
| SupremeCourtJustice | SupremeCourtDistrict | PRESIDES_OVER | 8 |
| CourtClerk | Court | WORKS_AT | 121 |
| MasterCommissioner | Court | APPOINTED_BY | 114 |
| CourtAdministrator | Court | WORKS_AT | 7 |

**Total Professional Relationships:** ~21,500

---

## Hierarchical Relationships (4 patterns)

| Child Entity | Parent Entity | Relationship | Count |
|--------------|---------------|--------------|-------|
| CircuitDivision | Court | PART_OF | 86 |
| DistrictDivision | Court | PART_OF | 94 |
| AppellateDistrict | Court | PART_OF | 5 |
| SupremeCourtDistrict | Court | PART_OF | 7 |
| MedicalProvider | HealthSystem | PART_OF | ~1,000 |
| Organization | Organization | PART_OF | ~50 |

**Total Hierarchy Relationships:** ~1,300

---

## Episode Network (Target)

**13,491 Episodes** with:
- 1 RELATES_TO per episode → Case (13,491 relationships)
- 40,605 ABOUT relationships → Entities
- ~10,000 FOLLOWS relationships → Other episodes (estimated)

**Total Episode Relationships:** ~64,000

---

## Complete Graph Metrics (Target State)

**Nodes:** ~57,000
- Entities: ~45,900 (imported from JSON files)
- LandmarkStatus: 11,316 (workflow state)
- Workflow entities: ~100

**Relationships:** ~85,000
- Episode ABOUT: 40,605
- Episode RELATES_TO: 13,491
- Episode FOLLOWS: ~10,000
- Professional WORKS_AT/PRESIDES_OVER: 21,500
- Case relationships: ~2,000
- Workflow: ~2,000
- Hierarchies (PART_OF): ~1,300

**Labels:** 50 entity types
**Relationship Types:** 51
**Property Keys:** ~100

---

## Implementation Status

### ✅ **In Graph Now:**
- Core case entities (Cases, Clients, Defendants)
- Insurance (Claims, Insurers, Adjusters)
- Medical Providers (773, basic)
- Attorneys, Law Firms
- Courts (basic), Pleadings
- Workflow state (Phases, Landmarks, LandmarkStatus)

### ⏳ **Ready to Ingest (in JSON files):**
- **20,732 Doctors**
- **1,386 new MedicalProviders**
- **5 HealthSystems**
- **192 Court Divisions**
- **461 Court Personnel**
- **13,491 Episodes with 40,605 ABOUT relationships**

### 📋 **Pending Approval:**
- 135 episode review documents need manual approval
- Then bulk ingest to graph

---

## Schema Files

**Pydantic Definitions:** `/src/roscoe/core/graphiti_client.py`
**Entity JSON Files:** `/json-files/memory-cards/entities/`
**Episode Data:** `/json-files/memory-cards/episodes/`

**Documentation:**
- `GRAPH_SCHEMA.md` - Designed schema from Pydantic
- `GRAPH_SCHEMA_ACTUAL.md` - Current graph state
- `GRAPH_SCHEMA_COMPLETE.md` - This file (target state)
- `CLAUDE_GRAPH.md` - Developer guide for graph work
