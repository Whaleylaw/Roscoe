# Roscoe Knowledge Graph - Actual Schema (From FalkorDB)

**Source:** Live graph database on `roscoe-graphdb` container
**Graph Name:** `roscoe_graph`
**Query Date:** 2025-12-29

---

## Current Node Labels (31)

Labels currently in the graph:

### **Core Entities:**
- `Entity` (generic base label, may be from Graphiti)
- `Case`
- `Client`
- `Defendant`

### **Insurance:**
- `Insurer`
- `Adjuster`
- `PIPClaim`
- `BIClaim`
- `UIMClaim`
- `UMClaim`
- `WCClaim`

### **Medical:**
- `MedicalProvider`
- `Lien`
- `LienHolder`

### **Legal:**
- `Attorney`
- `LawFirm`
- `CaseManager`
- `Court`
- `Pleading`

### **Organizations:**
- `Organization`
- `Vendor`

### **Workflow (Structural):**
- `Phase`
- `SubPhase`
- `Landmark`
- `WorkflowDef`
- `WorkflowChecklist`
- `WorkflowTemplate`
- `WorkflowTool`
- `LandmarkStatus`

### **Graphiti Specific:**
- `Episodic` (from Graphiti episode ingestion)
- `Community` (from Graphiti community summaries)

### **Cached:**
- (No cache labels)

---

## Current Relationship Types (26)

Relationship types currently in the graph:

### **Case Relationships:**
- `HAS_CLIENT`
- `HAS_CLAIM`
- `HAS_LIEN`
- `HAS_LIEN_FROM`
- `PLAINTIFF_IN`

### **Insurance:**
- `INSURED_BY`
- `ASSIGNED_ADJUSTER`
- `HANDLES_CLAIM`

### **Medical:**
- `TREATING_AT`
- `TREATED_BY`
- `HELD_BY` (lien relationships)
- `HOLDS`

### **Legal:**
- `WORKS_AT` (attorney/case manager → law firm)

### **Workflow:**
- `IN_PHASE`
- `HAS_STATUS` (case → landmark status)
- `FOR_LANDMARK` (status → landmark)
- `NEXT_PHASE`
- `HAS_WORKFLOW`
- `HAS_LANDMARK`
- `HAS_SUB_LANDMARK`
- `HAS_SUBPHASE`
- `USES_TEMPLATE`

### **Graphiti:**
- `RELATES_TO` (generic)
- `MENTIONS`
- `HAS_MEMBER` (community relationships)

---

## Property Keys (78 total)

All property keys used across all nodes:

### **Identifiers:**
- `uuid`
- `name`
- `display_name`
- `id` (internal graph ID)
- `group_id`
- `entity_type`

### **Case Properties:**
- `case_name`
- `case_type` (MVA, WC, Premise, etc.)
- `accident_date`
- `created_at`
- `status`

### **Contact Information:**
- `phone`
- `email`
- `fax`
- `address`
- `county`
- `state`

### **People:**
- `role` (attorney role, etc.)
- `specialty` (medical specialty)
- `firm_name`

### **Insurance Claims:**
- `claim_number`
- `insurer_name`
- `adjuster_name`
- `coverage_confirmation`

### **Liens:**
- `lien_type`
- `amount`
- `date_notice_received`
- `date_lien_paid`
- `reduction_amount`

### **Settlements:**
- `settlement_amount`
- `settlement_date`
- `demand_amount`
- `date_demand_sent`
- `current_offer`
- `is_active_negotiation`

### **Court:**
- `division`
- `pleading_type`
- `filed_date`
- `filed_by`
- `hearing_date`
- `hearing_type`

### **Organizations:**
- `org_type`
- `vendor_type`

### **Workflow:**
- `landmark_id`
- `phase`
- `subphase`
- `order` (sequence)
- `track` (workflow track)
- `mandatory` (required landmark)
- `verification_fields`
- `instructions_path`
- `trigger`
- `prerequisites`
- `parent_landmark`
- `parent_phase`
- `when_to_use`
- `file_type`
- `path`

### **Workflow State (per case):**
- `project_name` (case name)
- `status` (complete, incomplete, etc.)
- `sub_steps` (JSON for composite landmarks)
- `notes`
- `completed_at`
- `updated_at`
- `updated_by`
- `version` (audit trail)
- `archived_at`

### **Episode/Temporal:**
- `valid_at` (timestamp)
- `expired_at`
- `invalid_at`
- `content` (episode text)
- `source`
- `source_description`
- `entered_at`

### **Episodic/Graphiti:**
- `summary` (Graphiti summary)
- `fact` (extracted facts)

### **Embeddings:**
- `embedding` (vecf32 vector for semantic search)

---

## Missing from Graph (Defined in Pydantic but not yet ingested)

### **Entity Types Not Yet in Graph:**

**Medical:**
- `HealthSystem` (just created)
- `Doctor` (20,732 defined, not ingested)

**Court Personnel:**
- `CircuitJudge` (101 defined)
- `DistrictJudge` (94 defined)
- `AppellateJudge` (15 defined)
- `SupremeCourtJustice` (8 defined)
- `CourtClerk` (121 defined)
- `MasterCommissioner` (114 defined)
- `CourtAdministrator` (7 defined)

**Court Divisions:**
- `CircuitDivision` (86 defined)
- `DistrictDivision` (94 defined)
- `AppellateDistrict` (5 defined)
- `SupremeCourtDistrict` (7 defined)

**Professional:**
- `Expert` (entity file created, not ingested)
- `Mediator` (2 defined)
- `Witness` (1 defined)

**Documents:**
- `Document`
- `Note` (defined but using Episode instead?)
- `Expense`
- `Settlement`

**Workflow:**
- `WorkflowStep`
- `WorkflowSkill`

### **Relationship Types Defined but Not Yet in Graph:**

**Court/Division:**
- `PART_OF` (Division → Court, MedicalProvider → HealthSystem)
- `PRESIDES_OVER` (Judge → Division)
- `FILED_IN` (Case → Division)
- `ASSIGNED_TO` (Case → Judge)
- `APPOINTED_BY` (Commissioner → Court)

**Medical:**
- `WORKS_AT` (Doctor → MedicalProvider) - Currently have Attorney → LawFirm only

**Professional:**
- `RETAINED_FOR` (Expert/Mediator → Case)
- `RETAINED_EXPERT`, `RETAINED_MEDIATOR` (Case → Expert/Mediator)
- `WITNESS_FOR`, `HAS_WITNESS` (Witness ↔ Case)

**Episode:**
- `ABOUT` (Episode → any entity) - Core relationship for episode ingestion
- `FOLLOWS` (Episode → Episode)
- `PART_OF_WORKFLOW` (Episode → WorkflowDef)

**Documents:**
- `HAS_DOCUMENT`, `HAS_EXPENSE`, `SETTLED_WITH`, etc.

---

## Graph Statistics (Current)

**Total Nodes:** 11,166
**Total Relationships:** 20,805
**Node Labels:** 31 (26 entity types + 5 system labels)
**Relationship Types:** 26

**Known Counts:**
- Cases: 111 (from workflow initialization)
- LandmarkStatus nodes: 9,102 (111 cases × 82 landmarks)
- Total entities imported to JSON: ~45,900
- Episodes ready for ingestion: 13,491

---

## Schema Comparison

### **Currently in Graph (26 entity types):**
✅ Core case management working (Cases, Clients, Claims, Liens, Providers, Workflow)
✅ Workflow state machine functional (Phases, Landmarks, LandmarkStatus)
✅ Basic entities linked (Cases have clients, claims, liens, providers)

### **Ready to Ingest (24 entity types):**
⏳ Doctors (20,732)
⏳ Court personnel (461 judges, clerks, commissioners, administrators)
⏳ Court divisions (192)
⏳ HealthSystem (5)
⏳ Episodes with ABOUT relationships (13,491 episodes → 40,605 proposed relationships)
⏳ Experts, Mediators, Witnesses
⏳ Documents, Expenses, Settlements

---

## Next Steps

1. **Review Approval:** Finish approving all 138 episode review documents
   - Currently: 3 approved, 135 pending
   - 47 files flagged with better medical provider matches

2. **Episode Ingestion:** Once reviews approved, ingest episodes with ABOUT relationships
   - 13,491 Episode nodes
   - 40,605+ ABOUT relationships linking episodes to entities

3. **Division Ingestion:** Add division entities and judge relationships
   - 192 division entities
   - PRESIDES_OVER relationships (judge → division)
   - Update Case-Division relationships

4. **Professional Relationships:** Add WORKS_AT for all entity types
   - Doctor → MedicalProvider
   - MedicalProvider → HealthSystem
   - Judge → Division
   - Division → Court

5. **Verify Schema:** After ingestion, re-query graph to confirm all entity types and relationships present

---

## Graph Access

**Container:** `roscoe-graphdb` (FalkorDB)
**Port:** 6379
**Graph Name:** `roscoe_graph`

**Query from VM:**
```bash
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a
sudo docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph 'YOUR_CYPHER_QUERY'
```

**Example Queries:**
```cypher
// Count nodes by label
MATCH (n:Case) RETURN count(n)

// Count relationships by type
MATCH ()-[r:HAS_CLIENT]->() RETURN count(r)

// Sample nodes with properties
MATCH (n:Case) RETURN n LIMIT 5
```
