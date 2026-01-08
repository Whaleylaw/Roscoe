# Workflow System Implementation - Progress Status

**Date:** December 23, 2025
**Session Start:** Token count 440K/1M

---

## ✅ COMPLETED

### 1. Pydantic Models Added to graphiti_client.py

**Added:**
- ✅ `SubPhase` model (line 321-326) - For litigation sub-phases
- ✅ `LandmarkStatus` model (line 412-423) - For status tracking with audit trail
- ✅ Updated `Landmark` model - Added `subphase` field (line 335)
- ✅ Updated `WorkflowDef` model - Added `subphase` field (line 363)
- ✅ Updated `Phase` model - Fixed track values to include 'settlement', 'closed'
- ✅ Both new models added to ENTITY_TYPES list (lines 464, 473)

**Verified:**
- All workflow models are now Pydantic BaseModel classes
- Compatible with Graphiti's entity system
- Ready for graph ingestion

### 2. Insurance Claim Query Updates

**Updated:**
- ✅ `graph_state_computer.py` line 341-342 - Use specific claim types (BIClaim, PIPClaim, etc.)
- ✅ `case_context_middleware.py` line 680-681 - Use specific claim types

**Query Pattern Changed:**
```cypher
# FROM:
MATCH (case)-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})

# TO:
MATCH (case)-[:HAS_CLAIM]->(claim:Entity)
WHERE claim.entity_type IN ['BIClaim', 'PIPClaim', 'UMClaim', 'UIMClaim', 'WCClaim', 'MedPayClaim']
```

---

## 🔄 IN PROGRESS

### Updating Landmark Status Queries for LandmarkStatus Nodes

**Files to Update:**
1. `src/roscoe/core/graphiti_client.py` - Multiple functions

**Functions Requiring Updates:**

#### A. get_case_landmark_statuses() - Line 1985-2043

**Current Pattern (line 2005):**
```cypher
OPTIONAL MATCH (c)-[r:LANDMARK_STATUS]->(l)
RETURN ..., r.status, r.sub_steps, r.notes, r.completed_at
```

**New Pattern (LandmarkStatus nodes):**
```cypher
OPTIONAL MATCH (c)-[:HAS_STATUS]->(ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l)
RETURN ..., ls.status, ls.sub_steps, ls.notes, ls.completed_at, ls.version, ls.updated_by
```

#### B. get_landmark_status() - Line 2046-2071

**Current Pattern (line 2058):**
```cypher
MATCH (c)-[r:LANDMARK_STATUS]->(l)
RETURN ..., r.status, r.sub_steps, r.notes, r.completed_at
```

**New Pattern:**
```cypher
MATCH (c)-[:HAS_STATUS]->(ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l)
RETURN ..., ls.status, ls.sub_steps, ls.notes, ls.completed_at, ls.version, ls.updated_by
```

#### C. update_case_landmark_status() - Line 2076+

**Current Pattern:**
```cypher
MERGE (c)-[r:LANDMARK_STATUS]->(l)
SET r.status = $status, r.notes = $notes, ...
```

**New Pattern (with versioning):**
```cypher
// Get current version
OPTIONAL MATCH (c)-[:HAS_STATUS]->(old_ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l)
WHERE old_ls.archived_at IS NULL
WITH c, l, old_ls, COALESCE(old_ls.version, 0) as current_version

// Create new LandmarkStatus node
CREATE (new_ls:Entity {
  entity_type: 'LandmarkStatus',
  uuid: $uuid,
  case_name: $case_name,
  landmark_id: $landmark_id,
  status: $status,
  sub_steps: $sub_steps,
  notes: $notes,
  completed_at: $completed_at,
  created_at: $now,
  updated_at: $now,
  updated_by: $updated_by,
  version: current_version + 1
})

// Link new status
MERGE (c)-[:HAS_STATUS]->(new_ls)
MERGE (new_ls)-[:FOR_LANDMARK]->(l)

// Archive old version
WITH old_ls WHERE old_ls IS NOT NULL
SET old_ls.archived_at = $now
```

---

## ⏸️ REMAINING WORK

### Step 2 Remaining: More Landmark Status Query Updates

**Files:**
- check_phase_can_advance() function
- Other utility queries that reference LANDMARK_STATUS

### Step 3: Add SubPhase Support

**Update get_case_phase():**
- Add OPTIONAL MATCH for IN_SUBPHASE
- Return subphase info

### Step 4: Enhance ingest_workflow_definitions.py

**Add:**
- SubPhase node creation
- Parse litigation/subphases/ folders
- Link workflows to actual skills/templates/tools from folders

### Step 5: Create initialize_case_states.py

**Generate:**
- Script to set all 110 cases to Phase 0
- Create ~7,480 LandmarkStatus nodes

### Step 6: Add recalculate_case_phase() Agent Tool

**Add to tools.py:**
- Phase recalculation logic
- Landmark completion analysis

### Step 7: Test & Verify

---

## Next Steps

**Continue from Step 2:** Update remaining landmark status queries in graphiti_client.py

**Estimated Remaining Time:** ~60 minutes

**Files Modified So Far:**
1. ✅ src/roscoe/core/graphiti_client.py (Pydantic models, insurance query)
2. ✅ src/roscoe/workflow_engine/orchestrator/graph_state_computer.py (insurance query)
3. ✅ src/roscoe/core/case_context_middleware.py (insurance query)

**Files Still To Modify:**
4. ⏸️ src/roscoe/core/graphiti_client.py (landmark status queries - in progress)
5. ⏳ src/roscoe/scripts/ingest_workflow_definitions.py (SubPhase support)
6. ⏳ src/roscoe/scripts/initialize_case_states.py (create new)
7. ⏳ src/roscoe/agents/paralegal/tools.py (add phase recalculation tool)
