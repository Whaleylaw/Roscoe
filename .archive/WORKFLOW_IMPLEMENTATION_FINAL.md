# Workflow System Implementation Plan (FINAL)

**Date:** December 23, 2025  
**Status:** Ready for Implementation  
**Based on:** User's accurate `workflow_state_machine.md` outline + actual `/mnt/workspace/workflows/` data

---

## USER DECISIONS (Finalized)

1. **Phase Initialization:** ✅ All 110 cases start at Phase 0 (onboarding)
   - User will manually advance cases
   - Need agent tool for phase recalculation based on landmark completion

2. **Landmark Inference:** ✅ N/A (all start at Phase 0)

3. **Sub-Phase Support:** ✅ Add to graph_state_computer.py NOW

4. **Workflow-Resource Linking:** ✅ Option C+B (parse YAML + verify actual files)

5. **Landmark Tracking:** ✅ Separate LandmarkStatus NODES (not relationship metadata)
   - Cleaner separation
   - Versioning + audit trail
   - Two-hop traversal acceptable

6. **Insurance Claim Types:** ✅ KEEP granular (BIClaim, PIPClaim, etc.)
   - DO NOT collapse types
   - UPDATE queries in graph_state_computer.py to match specific types

---

## Landmark Status Tracking Schema (APPROVED)

**Pattern:**
```
Case -[:HAS_STATUS]-> LandmarkStatus -[:FOR_LANDMARK]-> Landmark
```

**LandmarkStatus Node:**
```
entity_type: 'LandmarkStatus'
group_id: 'roscoe_graph'
uuid: 'status_{case_name}_{landmark_id}'

Properties:
  - case_name: str (denormalized)
  - landmark_id: str (denormalized)
  - status: 'complete' | 'incomplete' | 'in_progress' | 'not_started' | 'not_applicable'
  - sub_steps: dict (for composite landmarks)
  - notes: str
  - completed_at: datetime
  - created_at: datetime
  - updated_at: datetime
  - updated_by: 'agent' | 'user' | 'system'
  - version: int (increment on update for audit trail)
```

**Benefits:**
- Audit trail (who, when, version)
- Historical tracking (keep old versions, mark as archived)
- Clean separation of concerns

---

## Implementation Steps (REVISED FOR USER DECISIONS)

### Step 1: Update graph_state_computer.py Queries (20 min)

**File:** `src/roscoe/core/graphiti_client.py`

**Changes Required:**

#### A. Insurance Claim Query (line ~340)
```python
# FROM:
MATCH (case)-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})

# TO:
MATCH (case)-[:HAS_CLAIM]->(claim:Entity)
WHERE claim.entity_type IN ['BIClaim', 'PIPClaim', 'UMClaim', 'UIMClaim', 'WCClaim']
```

#### B. Landmark Status Queries (multiple locations)

**get_case_landmark_statuses() - line ~1977:**
```python
# FROM:
OPTIONAL MATCH (c)-[r:LANDMARK_STATUS]->(l)
RETURN ..., r.status, r.sub_steps, r.notes, r.completed_at

# TO:
OPTIONAL MATCH (c)-[:HAS_STATUS]->(ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l)
RETURN ..., ls.status, ls.sub_steps, ls.notes, ls.completed_at, ls.version, ls.updated_by
```

**update_case_landmark_status() - line ~2049:**
```python
# FROM:
MERGE (c)-[r:LANDMARK_STATUS]->(l)
SET r.status = $status, r.notes = $notes, r.completed_at = $completed_at

# TO:
// Create new versioned LandmarkStatus node
OPTIONAL MATCH (c)-[:HAS_STATUS]->(old_ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l)
WITH c, l, old_ls, COALESCE(old_ls.version, 0) as current_version

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

MERGE (c)-[:HAS_STATUS]->(new_ls)
MERGE (new_ls)-[:FOR_LANDMARK]->(l)

// Archive old version
WITH old_ls WHERE old_ls IS NOT NULL
SET old_ls.archived_at = $now
```

#### C. Add SubPhase Support

**get_case_phase() - line ~1946:**
```python
# FROM:
MATCH (c)-[r:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
RETURN p.name, p.display_name, p.order, p.track, r.entered_at

# TO:
MATCH (c)-[r:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
OPTIONAL MATCH (c)-[sr:IN_SUBPHASE]->(sp:Entity {entity_type: 'SubPhase'})
RETURN p.name, p.display_name, p.order, p.track, r.entered_at,
       sp.name as subphase_name, sp.display_name as subphase_display,
       sp.order as subphase_order, sr.entered_at as subphase_entered_at
```

---

### Step 2: Enhance ingest_workflow_definitions.py (25 min)

**Add Functions:**

1. `create_subphase_nodes()` - Parse litigation/subphases/ folders
2. `link_workflow_resources_from_folder()` - Scan actual folders for resources
3. `parse_workflow_yaml_frontmatter()` - Extract trigger, prerequisites, related_skills from workflow.md

**Run:**
```bash
sudo docker exec roscoe-agents python -m roscoe.scripts.ingest_workflow_definitions --workspace /mnt/workspace
```

**Creates:**
- 9 Phase + 5 SubPhase nodes
- ~68 Landmarks
- ~35 WorkflowDefs
- 47 Skills + ~50 Templates + 10 Tools
- ~350 relationships

---

### Step 3: Create & Run initialize_case_states.py (20 min)

**Creates:**
- 110 IN_PHASE relationships (all → Phase:onboarding)
- ~7,480 LandmarkStatus nodes (all status='not_started', version=1)
- ~7,480 HAS_STATUS + ~7,480 FOR_LANDMARK relationships

---

### Step 4: Add recalculate_case_phase() Agent Tool (10 min)

**File:** `src/roscoe/agents/paralegal/tools.py`

**Function:**
- Analyzes landmark completion for current phase
- Checks for hard blockers
- Recommends phase advancement
- Returns completion percentage

---

## Verification

### Check All Loaded
```cypher
MATCH (n:Entity) WHERE n.group_id = '__workflow_definitions__'
RETURN n.entity_type, count(*) ORDER BY count DESC
```

### Check Case States
```cypher
MATCH (c:Entity {entity_type: 'Case'})-[:IN_PHASE]->(p:Entity)
RETURN p.name, count(c) ORDER BY p.order
// Expected: onboarding: 110
```

### Check Landmark Statuses
```cypher
MATCH (:Entity {entity_type: 'Case', name: 'Caryn-McCay-MVA-7-30-2023'})-[:HAS_STATUS]->(ls)-[:FOR_LANDMARK]->(l:Entity {entity_type: 'Landmark'})
WHERE l.phase = 'onboarding'
RETURN l.landmark_id, l.name, ls.status, ls.version
```

---

## Total Time: ~80 minutes

Ready to begin implementation!
