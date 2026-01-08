# Workflow Graph Update Plan

**Date:** December 23, 2025
**Purpose:** Update graph schema to support workflow system (graph_state_computer.py)

---

## Current State

### ✅ What's Loaded (Structured Layer)

**Entities: 1,954 total**
- 110 Cases
- 105 Clients
- 771 MedicalProviders
- 260 Insurance Claims (BIClaim: 119, PIPClaim: 120, UMClaim: 14, UIMClaim: 2, WCClaim: 5)
- 148 Adjusters
- 99 Insurers
- 103 Liens
- 50 LienHolders
- 185 Pleadings
- 39 Vendors
- 33 Attorneys
- 23 Courts
- 19 Organizations
- 7 Defendants

**Relationships: 2,417 total**
- 573 TREATING_AT (Case → MedicalProvider)
- 573 TREATED_BY (Client → MedicalProvider)
- 260 HAS_CLAIM (Case → Claims)
- 254 INSURED_BY (Claim → Insurer)
- 212 ASSIGNED_ADJUSTER (Claim → Adjuster)
- 212 HANDLES_INSURANCE_CLAIM (Adjuster → Claim)
- 212 WORKS_AT (Adjuster → Insurer)
- 106 HAS_CLIENT (Case → Client)
- 106 PLAINTIFF_IN (Client → Case)
- 103 HAS_LIEN (Case → Lien)
- 82 HELD_BY (Lien → LienHolder)
- 82 HOLDS (LienHolder → Lien)
- 73 HAS_LIEN_FROM (Client → LienHolder)

---

## Issues Preventing Workflow System

### Issue #1: InsuranceClaim Entity Type Mismatch

**Problem:**
`graph_state_computer.py:341-351` queries for:
```cypher
MATCH (case:Entity {entity_type: 'Case'})-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})
```

**Current State:**
We have specific claim types:
- `entity_type: 'BIClaim'`
- `entity_type: 'PIPClaim'`
- `entity_type: 'UMClaim'`
- `entity_type: 'UIMClaim'`
- `entity_type: 'WCClaim'`

**Solution Options:**

**Option A: Add 'InsuranceClaim' to Labels (Recommended)**
```cypher
MATCH (c:Entity)
WHERE c.entity_type IN ['BIClaim', 'PIPClaim', 'UMClaim', 'UIMClaim', 'WCClaim']
SET c.entity_type = 'InsuranceClaim', c.claim_type = c.entity_type
```
- Pros: Matches existing query patterns
- Cons: Loses specific type in entity_type field (but preserves in claim_type)

**Option B: Update All Queries to Match Specific Types**
```cypher
WHERE claim.entity_type IN ['BIClaim', 'PIPClaim', 'UMClaim', 'UIMClaim', 'WCClaim']
```
- Pros: Preserves specific types
- Cons: Requires updating multiple queries in graph_state_computer.py

**Recommendation:** Option A (simpler, less code changes)

---

### Issue #2: Missing Workflow Definition Nodes

**Required Entity Types (all with group_id='__workflow_definitions__'):**

#### 1. Phase Nodes
**Purpose:** Define the case lifecycle phases

**Schema:**
```json
{
  "entity_type": "Phase",
  "name": "file_setup",  // Phase ID
  "display_name": "File Setup",
  "description": "Initial case setup and documentation",
  "order": 1,
  "track": "pre_litigation",  // pre_litigation | litigation | settlement
  "next_phase": "intake_investigation",
  "group_id": "__workflow_definitions__",
  "uuid": "phase_file_setup"
}
```

**Examples:**
- file_setup → intake_investigation → pre_lit_medical_treatment → ...

**Source:** `/mnt/workspace/workflow_engine/schemas/phase_definitions.json`

#### 2. Landmark Nodes
**Purpose:** Define checkpoints within each phase

**Schema:**
```json
{
  "entity_type": "Landmark",
  "landmark_id": "retainer_signed",  // Unique ID
  "name": "Retainer Signed",  // Display name
  "phase": "file_setup",
  "description": "Signed retainer agreement on file",
  "is_hard_blocker": true,  // Blocks phase advancement
  "can_override": false,
  "order": 1,
  "sub_steps": ["client_signature", "attorney_signature"],
  "group_id": "__workflow_definitions__",
  "uuid": "landmark_file_setup_retainer_signed"
}
```

**Source:** `/mnt/workspace/workflows/phase_*/landmarks.md` (parsed from markdown)

#### 3. WorkflowDef Nodes
**Purpose:** Define workflows that achieve landmarks

**Schema:**
```json
{
  "entity_type": "WorkflowDef",
  "name": "initial_client_intake",
  "display_name": "Initial Client Intake",
  "phase": "file_setup",
  "description": "Conduct initial client consultation",
  "trigger": "New case created",
  "prerequisites": ["Client contact information available"],
  "group_id": "__workflow_definitions__",
  "uuid": "workflow_initial_client_intake"
}
```

**Source:** `/mnt/workspace/workflow_engine/schemas/workflow_definitions.json`

#### 4. WorkflowStep Nodes (Optional)
**Purpose:** Individual steps within workflows

**Schema:**
```json
{
  "entity_type": "WorkflowStep",
  "step_id": "collect_intake_info",
  "name": "Collect Intake Information",
  "workflow": "initial_client_intake",
  "order": 1,
  "owner": "staff",  // staff | agent | client
  "can_automate": false,
  "group_id": "__workflow_definitions__"
}
```

**Source:** Same workflow_definitions.json

---

### Issue #3: Missing Workflow Definition Relationships

**Required Relationships (Definition Layer):**

| Relationship | From | To | Purpose |
|--------------|------|-----|---------|
| **HAS_LANDMARK** | Phase | Landmark | Phase contains landmarks |
| **NEXT_PHASE** | Phase | Phase | Phase progression |
| **CAN_SKIP_TO** | Phase | Phase | Allowed phase jumps |
| **ACHIEVED_BY** | Landmark | WorkflowDef | How to complete landmark |
| **HAS_WORKFLOW** | Phase | WorkflowDef | Phase's available workflows |
| **HAS_STEP** | WorkflowDef | WorkflowStep | Workflow's steps |
| **USES_SKILL** | WorkflowDef | WorkflowSkill | Workflow uses skill |
| **USES_TEMPLATE** | WorkflowDef | WorkflowTemplate | Workflow uses template |
| **USES_TOOL** | WorkflowDef | WorkflowTool | Workflow uses tool |

**Example Graph Structure:**
```
Phase:file_setup
  └─[HAS_LANDMARK]→ Landmark:retainer_signed
      └─[ACHIEVED_BY]→ WorkflowDef:send_retainer_package
          ├─[HAS_STEP]→ WorkflowStep:draft_retainer
          ├─[HAS_STEP]→ WorkflowStep:email_to_client
          └─[USES_SKILL]→ WorkflowSkill:docx
```

---

### Issue #4: Missing Workflow State Relationships

**Required Relationships (Case-Specific State):**

| Relationship | From | To | Properties | Purpose |
|--------------|------|-----|-----------|---------|
| **IN_PHASE** | Case | Phase | entered_at (datetime) | Current phase |
| **LANDMARK_STATUS** | Case | Landmark | status (complete/incomplete/in_progress), sub_steps (dict), completed_at, notes | Landmark progress |

**Example for a Case:**
```
Case:Caryn-McCay-MVA-7-30-2023
  ├─[IN_PHASE {entered_at: '2025-12-01'}]→ Phase:intake_investigation
  ├─[LANDMARK_STATUS {status: 'complete'}]→ Landmark:retainer_signed
  ├─[LANDMARK_STATUS {status: 'complete'}]→ Landmark:liability_established
  └─[LANDMARK_STATUS {status: 'in_progress'}]→ Landmark:pip_claim_setup
```

---

## Execution Plan

### Step 1: Add 'InsuranceClaim' Label to Claim Entities (1 minute)

**Script:** Create `fix_claim_types.py`

```python
# Update all claim entities to have InsuranceClaim as entity_type
# Preserve specific type in claim_type attribute
query = """
MATCH (c:Entity)
WHERE c.entity_type IN ['BIClaim', 'PIPClaim', 'UMClaim', 'UIMClaim', 'WCClaim']
SET c.claim_type = c.entity_type,
    c.entity_type = 'InsuranceClaim'
RETURN c.claim_type as claim_type, count(*) as count
"""
```

**Expected:** 260 claims updated

### Step 2: Load Workflow Definitions (2-3 minutes)

**Script:** `ingest_workflow_definitions.py` (already exists)

**Command:**
```bash
python -m roscoe.scripts.ingest_workflow_definitions --workspace /mnt/workspace
```

**Creates:**
- ~6-8 Phase nodes
- ~40-50 Landmark nodes
- ~15-20 WorkflowDef nodes
- ~50-100 WorkflowStep nodes
- All definition relationships

**Sources:**
- `/mnt/workspace/workflow_engine/schemas/phase_definitions.json`
- `/mnt/workspace/workflow_engine/schemas/workflow_definitions.json`
- `/mnt/workspace/workflows/phase_*/landmarks.md`
- `/mnt/workspace/workflows/phase_*/workflows/*/workflow.md`

### Step 3: Initialize Case Workflow States (3-5 minutes)

**Script:** Create `initialize_case_states.py`

For each Case entity:
1. Create `IN_PHASE` relationship to starting phase (file_setup)
2. Query all Landmarks (from definitions)
3. Create `LANDMARK_STATUS` relationships (all status='not_started')

**Pseudocode:**
```python
for each Case:
    # Set initial phase
    MERGE (case)-[r:IN_PHASE]->(phase:Entity {name: 'file_setup'})
    SET r.entered_at = NOW()

    # Create landmark status relationships
    for each Landmark in phase_definitions:
        MERGE (case)-[r:LANDMARK_STATUS]->(landmark)
        SET r.status = 'not_started'
```

**Expected:**
- 110 IN_PHASE relationships
- ~5,500 LANDMARK_STATUS relationships (110 cases × ~50 landmarks)

---

## Verification Queries

After execution, verify with:

```cypher
// Check workflow definitions loaded
MATCH (n:Entity)
WHERE n.group_id = '__workflow_definitions__'
RETURN n.entity_type, count(*) as count
ORDER BY count DESC

// Check a case has workflow state
MATCH (c:Entity {entity_type: 'Case', name: 'Caryn-McCay-MVA-7-30-2023'})-[r:IN_PHASE]->(p:Entity)
RETURN c.name, p.name, p.display_name, r.entered_at

// Check landmark statuses for a case
MATCH (c:Entity {entity_type: 'Case', name: 'Caryn-McCay-MVA-7-30-2023'})-[r:LANDMARK_STATUS]->(l:Entity)
RETURN l.phase, l.name, r.status
LIMIT 10

// Test graph_state_computer query
MATCH (c:Entity {entity_type: 'Case', name: 'Caryn-McCay-MVA-7-30-2023'})-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})
OPTIONAL MATCH (claim)-[:INSURED_BY]->(insurer:Entity {entity_type: 'Insurer'})
RETURN claim.claim_type, insurer.name
```

---

## Files to Create

1. **fix_claim_types.py** - Standardize claim entity types
2. **initialize_case_states.py** - Create IN_PHASE and LANDMARK_STATUS relationships

**Existing Scripts (Ready to Use):**
- ✅ `ingest_workflow_definitions.py` - Loads Phase/Landmark/WorkflowDef nodes

---

## Summary

### What This Fixes

✅ `graph_state_computer.py` can query insurance claims
✅ `get_case_phase()` returns current phase
✅ `get_case_landmark_statuses()` returns landmark progress
✅ `update_case_landmark_status()` can mark landmarks complete
✅ `advance_case_phase()` can transition phases
✅ WorkflowMiddleware can inject phase-specific guidance

### Estimated Time

- Step 1 (Fix Claims): 1 minute
- Step 2 (Load Definitions): 2-3 minutes
- Step 3 (Initialize States): 3-5 minutes

**Total:** ~10 minutes

### Next Steps After This

Once workflow graph is ready:
1. Test workflow state queries on a sample case
2. Consider whether to reload episode notes (adds unstructured layer)
3. Verify WorkflowMiddleware injection works in agent

---

## Open Questions

1. **Episode Notes:** Do you want to reload the ~103 cases worth of episode notes on top of the structured layer?
2. **Workflow State Migration:** Do existing cases have known phase/landmark states, or should all start at file_setup?
3. **Embedding Strategy:** Continue with OpenAI for future episode ingestion (if you choose to do it)?
