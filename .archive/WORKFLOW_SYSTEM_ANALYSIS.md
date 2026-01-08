# Workflow System Analysis - Complete Inventory

**Date:** December 23, 2025
**Source:** whaley_law_firm/workflows (GCS bucket, mounted at /mnt/workspace/workflows)

---

## Actual Workflow Structure (Source of Truth)

### Phase Folders

| Phase | Folder Name | Purpose | Landmarks File | Workflows Subfolder |
|-------|-------------|---------|----------------|---------------------|
| 0 | phase_0_onboarding | Client signing intake docs | ✅ landmarks.md | ✅ /workflows/ |
| 1 | phase_1_file_setup | Case setup, insurance, initial records | ✅ landmarks.md | ✅ /workflows/ |
| 2 | phase_2_treatment | Monitor treatment, gather records | ✅ landmarks.md | ✅ /workflows/ |
| 3 | phase_3_demand | Assemble and send demand package | ✅ landmarks.md | ✅ /workflows/ |
| 4 | phase_4_negotiation | Settlement negotiations | ✅ landmarks.md | ✅ /workflows/ |
| 5 | phase_5_settlement | Process settlement, prepare distribution | ✅ landmarks.md | ✅ /workflows/ |
| 6 | phase_6_lien | Resolve liens, distribute to client | ✅ landmarks.md | ✅ /workflows/ |
| 7 | phase_7_litigation | Lawsuit filed through trial | ✅ landmarks.md | ⚠️ /subphases/ (complex) |
| 8 | phase_8_closed | Case closure and archival | ✅ landmarks.md | ✅ /workflows/ |

### Actual Landmarks by Phase

#### Phase 0: Onboarding (3 landmarks - all mandatory)
1. `client_info_received` - Client Info Received (New Client Information Sheet)
2. `contract_signed` - Contract Signed (Fee Agreement)
3. `medical_auth_signed` - Medical Auth Signed (HIPAA)

#### Phase 1: File Setup (4 landmarks - all soft blockers)
1. `full_intake_complete` - Full Intake Complete
2. `accident_report_obtained` - Accident Report Obtained
3. `insurance_claims_setup` - Insurance Claims Set Up
   - Sub-steps: BI (3a-3e), PIP (3f-3j)
4. `providers_setup` - Providers Set Up

#### Phase 2: Treatment (Landmarks focus on ongoing monitoring)
1. `client_check_in_schedule_active` (L2.1) - Bi-weekly check-ins
2. `all_providers_have_records_requested` (L2.2) - Records requested

#### Phase 3: Demand (Landmarks for demand preparation)
1. `all_records_received` (L3.1) - Medical records complete
2. `all_bills_received` (L3.2) - Medical bills complete
3. (More landmarks visible in full file)

#### Phase 4: Negotiation (Landmarks for settlement discussions)
1. `one_week_followup_completed` (L4.1) - Initial follow-up
2. `deficiencies_addressed` (L4.2) - Response to carrier requests

#### Phase 5: Settlement (Landmarks for funds processing)
1. `settlement_statement_prepared` (L5.1) - Breakdown prepared
2. `authorization_to_settle_prepared` (L5.2) - Auth doc ready

#### Phase 6: Lien Resolution (Landmarks for lien satisfaction)
1. `outstanding_liens_identified` (L6.1) - Liens identified
2. `final_lien_amounts_requested` (L6.2) - Final amounts requested
3. `medicare_final_demand_received` (L6.3) - If applicable

#### Phase 7: Litigation (Complex with sub-phases)
1. `litigation_commenced` (L7.0) - Decision to litigate
2. `complaint_filed` (L7.1) - ⭐ **HARD BLOCKER**
3. `defendant_served` (L7.2)
4. (More sub-phase landmarks)

#### Phase 8: Closed (Final closure tasks)
1. `all_obligations_verified` (L8.1) - All payments complete
2. `final_letter_sent` (L8.2) - Closing letter sent

### Central Resources

#### Skills (47 total in skills_manifest.json)
**Sample Skills by Phase:**
- **Phase 0:** `docusign-send`, `document-intake`, `document-request`
- **Phase 1:** `pip-waterfall`, `pip-application`, `lor-generator`, `liability-analysis`, `medical-records-request-setup`, `police-report-analysis`
- **Phase 2:** (Medical monitoring skills)
- **Phase 3:** (Demand preparation skills)
- **All Phases:** Referenced via manifest

**Storage:** `/workflows/skills/{phase}/{skill_name}/skill.md`

#### Templates (Multiple collections in templates_manifest.json)
**Collections:**
- **demand/** - Demand letter templates (2 variants)
- **complaint/** - Complaint templates (8 types: MVA standard, UM, UIM, vicarious, negligent entrustment, stolen vehicle, premises standard, dog bite)
- **deposition/** - Deposition templates
- **discovery/** - Discovery templates
- **mediation/** - Mediation templates
- **medical/** - Medical records request templates
- **negotiation/** - Negotiation letter templates
- **output/** - Output/report templates

**Storage:** `/workflows/templates/{collection}/{template_file}`

#### Tools (10 tools in tools_manifest.json)
1. `create_case` - Case folder creation
2. `pip_waterfall` - PIP carrier determination
3. `lexis_crash_order` - Crash report ordering (browser automation)
4. `read_pdf` - PDF extraction
5. `docusign_send` - eSignature sending
6. `docusign_config` - DocuSign configuration
7. `chronology_tools` - Medical chronology
8. `medical_request_generator` - Records request packages
9. `generate_demand_pdf` - Demand PDF generation
10. `generate_document` - Unified document generator

**Storage:** `/workflows/tools/{tool_file}.py`

---

## What graph_state_computer.py Expects

### Expected Node Types

#### 1. Phase Nodes (entity_type='Phase')
**Required Properties:**
- `name` - Phase ID (e.g., 'onboarding', 'file_setup')
- `display_name` - Human readable (e.g., 'Onboarding', 'File Setup')
- `order` - Numeric order (0, 1, 2...)
- `track` - pre_litigation | litigation | settlement
- `next_phase` - ID of next phase
- `group_id` - Must be `'__workflow_definitions__'`

**Query:** Line 1946
```cypher
MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[r:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
```

#### 2. Landmark Nodes (entity_type='Landmark')
**Required Properties:**
- `landmark_id` - Unique ID (e.g., 'client_info_received')
- `name` - Display name (e.g., 'Client Info Received')
- `phase` - Phase ID this belongs to
- `is_hard_blocker` - Boolean
- `can_override` - Boolean
- `landmark_type` - Type classification
- `order` - Order within phase
- `sub_steps` - Array of sub-step IDs (optional)
- `group_id` - Must be `'__workflow_definitions__'`

**Query:** Line 1977-1993 (for specific phase)
```cypher
MATCH (p:Entity {entity_type: 'Phase', name: $phase_name})-[:HAS_LANDMARK]->(l:Entity {entity_type: 'Landmark'})
```

**Query:** Line 1998-2016 (all landmarks)
```cypher
MATCH (l:Entity {entity_type: 'Landmark'})
WHERE l.group_id = '__workflow_definitions__'
```

#### 3. WorkflowDef Nodes (entity_type='WorkflowDef')
**Required Properties:**
- `name` - Workflow ID
- `display_name` - Human readable name
- `description` - Purpose description
- `phase` - Phase ID
- `group_id` - Must be `'__workflow_definitions__'`

**Query:** Line 2297-2301
```cypher
MATCH (l:Entity {entity_type: 'Landmark', name: $landmark_id})-[:ACHIEVED_BY]->(w:Entity {entity_type: 'WorkflowDef'})
```

### Expected Relationships (Definition Layer)

| Relationship | From | To | Used By |
|--------------|------|-----|---------|
| **HAS_LANDMARK** | Phase | Landmark | get_case_landmark_statuses() |
| **ACHIEVED_BY** | Landmark | WorkflowDef | get_case_workflow_state() line 2298 |
| **NEXT_PHASE** | Phase | Phase | (Implicit in navigation) |

### Expected Relationships (Case State Layer)

| Relationship | From | To | Properties | Used By |
|--------------|------|-----|-----------|---------|
| **IN_PHASE** | Case | Phase | entered_at (datetime) | get_case_phase() line 1946 |
| **LANDMARK_STATUS** | Case | Landmark | status, sub_steps, notes, completed_at, updated_at | get_case_landmark_statuses() line 1978, 2000 |

---

## Gap Analysis

### ✅ What's Complete

1. **Structured Case Data:**
   - 110 Case entities
   - 105 Client entities
   - 260 Insurance Claim entities (BIClaim, PIPClaim, etc.)
   - 771 MedicalProvider entities
   - 103 Lien entities
   - All relationships (HAS_CLIENT, TREATING_AT, etc.)

2. **Workflow Source Files:**
   - 9 phase folders with landmarks.md
   - 47 skills cataloged in manifest
   - 10+ template collections
   - 10 tools

### ❌ What's Missing from Graph

1. **Workflow Definition Nodes:**
   - ❌ NO Phase nodes (need 9: onboarding through closed)
   - ❌ NO Landmark nodes (need ~40-60 across all phases)
   - ❌ NO WorkflowDef nodes
   - ❌ NO WorkflowStep nodes
   - ❌ NO WorkflowSkill/Template/Tool nodes

2. **Workflow Definition Relationships:**
   - ❌ NO Phase -[HAS_LANDMARK]-> Landmark
   - ❌ NO Phase -[NEXT_PHASE]-> Phase
   - ❌ NO Landmark -[ACHIEVED_BY]-> WorkflowDef

3. **Case Workflow State:**
   - ❌ NO Case -[IN_PHASE]-> Phase (for any of the 110 cases)
   - ❌ NO Case -[LANDMARK_STATUS]-> Landmark

4. **Entity Type Issue:**
   - ⚠️ Claims have specific types (BIClaim, PIPClaim) but queries expect 'InsuranceClaim'

---

## Execution Plan

### Part 1: Fix InsuranceClaim Type (FAST - 30 seconds)

**What:** Add 'InsuranceClaim' as the entity_type for all claim entities, preserve specific type as claim_type attribute.

**Why:** graph_state_computer.py line 341 queries for `entity_type: 'InsuranceClaim'`

**Script:** Create `fix_claim_types.py`

**Cypher:**
```cypher
MATCH (c:Entity)
WHERE c.entity_type IN ['BIClaim', 'PIPClaim', 'UMClaim', 'UIMClaim', 'WCClaim']
SET c.claim_type = c.entity_type,
    c.entity_type = 'InsuranceClaim'
RETURN c.claim_type as claim_type, count(*) as count
```

**Expected Result:** 260 claim entities updated

---

### Part 2: Load Workflow Definitions (2-3 minutes)

**What:** Run existing `ingest_workflow_definitions.py` script

**Sources:**
- `/mnt/workspace/workflow_engine/schemas/phase_definitions.json`
- `/mnt/workspace/workflow_engine/schemas/workflow_definitions.json`
- `/mnt/workspace/workflows/phase_*/landmarks.md` (parse markdown)
- `/mnt/workspace/workflows/skills/skills_manifest.json`
- `/mnt/workspace/workflows/templates/templates_manifest.json`
- `/mnt/workspace/workflows/tools/tools_manifest.json`

**Creates:**
1. **Phase Nodes** (9 total)
   - onboarding, file_setup, treatment, demand, negotiation, settlement, lien, litigation, closed
   - Each with: name, display_name, order, track, next_phase

2. **Landmark Nodes** (~40-60 total, estimated)
   - Parsed from landmarks.md in each phase folder
   - Each with: landmark_id, name, phase, is_hard_blocker, order

3. **WorkflowDef Nodes** (from workflow_definitions.json)
   - Workflows that achieve landmarks

4. **WorkflowSkill/Template/Tool References**
   - Based on manifests

**Relationships Created:**
- Phase -[HAS_LANDMARK {order}]-> Landmark
- Phase -[NEXT_PHASE]-> Phase
- Landmark -[ACHIEVED_BY]-> WorkflowDef
- WorkflowDef -[USES_SKILL]-> Skill
- WorkflowDef -[USES_TEMPLATE]-> Template
- WorkflowDef -[USES_TOOL]-> Tool

**Command:**
```bash
sudo docker exec roscoe-agents python -m roscoe.scripts.ingest_workflow_definitions --workspace /mnt/workspace
```

**Expected Output:**
```
Created 9 Phase nodes
Created 45 Landmark nodes
Created 20 WorkflowDef nodes
Created 47 WorkflowSkill nodes
Created 30 Template nodes
Created 10 Tool nodes
```

---

### Part 3: Initialize Case Workflow States (3-5 minutes)

**What:** For each of the 110 Case entities, create initial workflow state

**Script:** Create `initialize_case_states.py`

**For Each Case:**

1. **Set Initial Phase** (onboarding or file_setup depending on data)
```cypher
MATCH (case:Entity {entity_type: 'Case', name: $case_name})
MATCH (phase:Entity {entity_type: 'Phase', name: 'onboarding'})
MERGE (case)-[r:IN_PHASE]->(phase)
SET r.entered_at = $now
```

2. **Create Landmark Status Relationships** (for ALL ~45 landmarks)
```cypher
MATCH (case:Entity {entity_type: 'Case', name: $case_name})
MATCH (l:Entity {entity_type: 'Landmark'})
WHERE l.group_id = '__workflow_definitions__'
MERGE (case)-[r:LANDMARK_STATUS]->(l)
SET r.status = 'not_started',
    r.created_at = $now
```

**Optimization:** Determine intelligent initial phase based on data:
- If case has signed retainer document → start at file_setup (Phase 1)
- If case has demand_sent_date → start at negotiation (Phase 4)
- Otherwise → start at onboarding (Phase 0)

**Expected:**
- 110 IN_PHASE relationships
- ~4,950 LANDMARK_STATUS relationships (110 cases × 45 landmarks)

---

## Data Sources for Workflow Definitions

### Schema Files (JSON - Structured)

Location: `/mnt/workspace/workflow_engine/schemas/`

**Files:**
1. `phase_definitions.json` - Phase metadata
2. `workflow_definitions.json` - Workflow and step definitions
3. `resource_mappings.json` - (deprecated - use manifests instead)

### Markdown Files (Parsed - Semi-Structured)

Location: `/mnt/workspace/workflows/phase_*/`

**Files:**
- `README.md` - Phase overview
- `landmarks.md` - **PRIMARY SOURCE for Landmark definitions**
  - Format: `### L{phase}.{num}: {Name}`
  - Contains: Description, verification JSON, hard blocker status

Location: `/mnt/workspace/workflows/phase_*/workflows/{workflow_name}/`

**Files:**
- `workflow.md` - Workflow instructions with YAML frontmatter
  - Frontmatter contains: name, trigger, prerequisites, related_skills

### Manifest Files (JSON - Catalogs)

Location: `/mnt/workspace/workflows/`

**Files:**
1. `skills/skills_manifest.json` - 47 skills cataloged
2. `templates/templates_manifest.json` - Template collections
3. `tools/tools_manifest.json` - 10 tools cataloged

---

## Verification After Loading

### Check Workflow Definitions Loaded

```cypher
// Count workflow definition nodes by type
MATCH (n:Entity)
WHERE n.group_id = '__workflow_definitions__'
RETURN n.entity_type as type, count(*) as count
ORDER BY count DESC

// Expected:
// Phase: 9
// Landmark: 40-60
// WorkflowDef: 15-25
// WorkflowStep: 50-100
// WorkflowSkill: 47
// WorkflowTemplate: 30+
// WorkflowTool: 10
```

### Check Phase Chain

```cypher
// Verify phase progression
MATCH (p:Entity {entity_type: 'Phase'})-[:NEXT_PHASE]->(next:Entity)
RETURN p.name, p.order, next.name
ORDER BY p.order

// Expected:
// onboarding (0) → file_setup (1)
// file_setup (1) → treatment (2)
// treatment (2) → demand (3)
// demand (3) → negotiation (4)
// negotiation (4) → settlement (5)
// settlement (5) → lien (6)
// lien (6) → closed (8)  [Note: Can skip litigation]
// litigation (7) → settlement (5) [Circles back]
```

### Check Landmark-to-Phase Links

```cypher
// Verify landmarks linked to phases
MATCH (p:Entity {entity_type: 'Phase'})-[:HAS_LANDMARK]->(l:Entity {entity_type: 'Landmark'})
RETURN p.name as phase, count(l) as landmark_count
ORDER BY p.order

// Expected distribution:
// onboarding: 3
// file_setup: 4
// treatment: 5-8
// demand: 6-8
// negotiation: 4-6
// settlement: 5-7
// lien: 4-6
// litigation: 10-15 (complex with sub-phases)
// closed: 3-4
```

### Test Case State Query

```cypher
// Check a specific case's workflow state
MATCH (c:Entity {entity_type: 'Case', name: 'Caryn-McCay-MVA-7-30-2023'})-[r:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
RETURN c.name as case_name,
       p.name as current_phase,
       p.display_name,
       r.entered_at
```

### Test Landmark Status Query

```cypher
// Check landmark statuses for a case
MATCH (c:Entity {entity_type: 'Case', name: 'Caryn-McCay-MVA-7-30-2023'})-[r:LANDMARK_STATUS]->(l:Entity {entity_type: 'Landmark'})
WHERE l.phase = 'onboarding'
RETURN l.landmark_id,
       l.name,
       r.status,
       r.completed_at
ORDER BY l.order
```

### Test Insurance Query (graph_state_computer.py line 340-351)

```cypher
// This should now work after fixing claim types
MATCH (case:Entity {entity_type: 'Case', name: 'Caryn-McCay-MVA-7-30-2023'})-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})
OPTIONAL MATCH (claim)-[:INSURED_BY]->(insurer:Entity {entity_type: 'Insurer'})
OPTIONAL MATCH (claim)-[:ASSIGNED_ADJUSTER]->(adjuster:Entity {entity_type: 'Adjuster'})
RETURN claim.claim_type,
       claim.claim_number,
       insurer.name,
       adjuster.name
```

---

## Critical Discoveries

### 1. Phase Naming Convention

**Folder names:** `phase_{num}_{name}`
- phase_0_onboarding
- phase_1_file_setup
- etc.

**Phase IDs in code:** Just the name part
- 'onboarding'
- 'file_setup'
- etc.

**Implication:** When creating Phase nodes, use the name part (without phase_N_ prefix) as the phase ID.

### 2. Landmark ID Format

**In landmarks.md:** `L{phase}.{num}: {Name}`
- L0.1, L0.2, L0.3 (Phase 0)
- L1.1, L1.2, L1.3, L1.4 (Phase 1)
- etc.

**In code:** Snake_case derived from name
- `client_info_received`
- `contract_signed`
- `medical_auth_signed`

**Implication:** Parser needs to extract both the L-number format AND convert name to snake_case ID.

### 3. Sub-Landmarks (Complex)

Phase 1's Landmark 3 (insurance_claims_setup) has **sub-steps**:
- BI steps: 3a-3e
- PIP steps: 3f-3j

**Implication:** LANDMARK_STATUS relationship needs `sub_steps` property (dict tracking each sub-step).

### 4. Skills Are Referenced, Not Embedded

Skills are cataloged in `skills_manifest.json` with paths to actual skill.md files.

**Actual skill files:** `/workflows/skills/phase_{num}_{name}/{skill_name}/skill.md`

**Implication:** WorkflowSkill nodes should reference the path, not duplicate content.

### 5. Tools Are Python Scripts

All tools are executable Python scripts in `/workflows/tools/*.py`

**Implication:** WorkflowTool nodes reference scripts that can be executed via agent's `execute_python_script` tool.

---

## Summary: What Needs to Happen

### Immediate Actions (Order Matters)

**✅ COMPLETED:**
1. Structured entities loaded (Cases, Clients, Providers, Claims, Liens, etc.)
2. Structured relationships loaded (HAS_CLIENT, TREATING_AT, HAS_CLAIM, etc.)

**🔄 NEXT:**

**Step 1:** Fix InsuranceClaim entity type
- Update 260 claim entities
- Queries will work

**Step 2:** Load workflow definitions from /workflows/
- Parse landmarks.md files (9 phases)
- Create Phase, Landmark, WorkflowDef nodes
- Create definition relationships

**Step 3:** Initialize case workflow states
- Create IN_PHASE for each of 110 cases
- Create LANDMARK_STATUS for each case × landmark

**Step 4:** Verify graph_state_computer.py works
- Test compute_state() on sample case
- Verify all queries return expected data

### After Workflow System is Working

**Then discuss:**
- Episode notes ingestion (adds unstructured layer on top)
- Workflow middleware testing
- Agent integration

---

## Files to Create

### Required New Scripts

1. **fix_claim_types.py** (Simple)
   - Update claim entity_type to 'InsuranceClaim'
   - Preserve specific type in claim_type attribute

2. **initialize_case_states.py** (Moderate complexity)
   - Set IN_PHASE for each case
   - Create LANDMARK_STATUS relationships
   - Smart phase detection based on case data

### Existing Scripts (Ready to Use)

- ✅ `ingest_workflow_definitions.py` - Loads Phase/Landmark/WorkflowDef from /workflows/

---

## Open Questions

1. **Initial Phase Logic:** Should all cases start at Phase 0 (onboarding), or intelligently determine phase based on existing data?

2. **Landmark Status Inference:** Should we infer any initial landmark completions based on existing data?
   - Example: If case has signed retainer in database, mark `contract_signed` as complete?

3. **Episode Notes:** After workflow system is working, do you want to ingest the ~103 cases of episode notes to add the unstructured layer?

4. **OpenAI vs Gemini:** Continue with OpenAI for any future episode ingestion, or reconsider?
