# write_entity() Tool Deployment - Complete

**Date:** January 5, 2026
**Status:** ✅ Deployed and Operational

---

## Summary

Removed Graphiti-dependent write tools and replaced with a single universal `write_entity()` tool that uses direct Cypher queries.

---

## Changes Made

### 1. ✅ Created `write_entity()` Tool

**File:** `src/roscoe/agents/paralegal/tools.py` (lines 983-1215)

**Function Signature:**
```python
write_entity(
    entity_type: str,
    properties: Dict[str, Any],
    relationships: Optional[List[Dict[str, Any]]] = None
) -> str
```

**Features:**
- Creates any entity type using direct Cypher CREATE statements
- Supports creating multiple relationships in single call
- Handles bidirectional relationships (incoming/outgoing)
- Escapes special characters in strings
- Returns confirmation with created entity and relationship details
- No dependency on Graphiti LLM extraction

**Example Usage:**
```python
# Create a BIClaim with relationships
write_entity(
    entity_type="BIClaim",
    properties={
        "claim_number": "17-87C986K",
        "status": "active",
        "amount_demanded": 50000.00
    },
    relationships=[
        {
            "rel_type": "UNDER_POLICY",
            "target_entity_type": "InsurancePolicy",
            "target_properties": {"policy_number": "POL-123456"}
        },
        {
            "rel_type": "HAS_CLAIM",
            "target_entity_type": "Case",
            "target_properties": {"name": "Christopher-Lanier-MVA-6-28-2025"},
            "direction": "incoming"  # Case -> BIClaim
        }
    ]
)
```

---

### 2. ✅ Removed Graphiti Write Tools

**Deleted from tools.py:**
- `update_case_data()` - Used Graphiti.add_episode() for LLM entity extraction
- `associate_document()` - Used Graphiti.add_episode() for document linking

**Why Removed:**
- Depended on Graphiti library for writing
- LLM-based extraction was non-deterministic
- Replaced by deterministic `write_entity()` with direct Cypher

**Tools Kept:**
- `query_case_graph()` - Uses Graphiti for semantic search (reading only)
- `graph_query()` - Direct Cypher (reading, can write via custom_cypher)
- `get_case_structure()` - Direct Cypher queries (reading only)
- All workflow tools - Direct Cypher (reading/writing state)

---

### 3. ✅ Updated Agent Tool List

**File:** `src/roscoe/agents/paralegal/agent.py` (lines 44-64)

**Added:**
- `write_entity` - Universal write tool

**Removed:**
- `update_case_data` - Replaced by write_entity
- `associate_document` - Replaced by write_entity

**Current Graph Tools (8 total):**
1. `write_entity` - Create entities/relationships (WRITE)
2. `query_case_graph` - Semantic search (READ)
3. `get_case_structure` - Structured data (READ)
4. `graph_query` - Direct Cypher (READ/WRITE)
5. `get_workflow_resources` - Workflow structure (READ)
6. `get_case_workflow_status` - Workflow state (READ)
7. `update_landmark` - Landmark status (WRITE)
8. `advance_phase` - Phase advancement (WRITE)

---

### 4. ✅ Updated Agent Prompts

**File:** `src/roscoe/agents/paralegal/prompts.py` (lines 212-242)

**Added:**
- Write Tools section with `write_entity()` documentation
- Schema reference requirement before using write_entity
- Organized tools into Write/Workflow/Read categories

**Updated:**
- Removed `update_case_data` from tool list
- Added clear separation between write and read operations
- Emphasized schema reference: `KNOWLEDGE_GRAPH_SCHEMA.md`

---

## How write_entity() Works

### Entity Creation
```python
write_entity(
    entity_type="Facility",
    properties={"name": "Norton Orthopedic Institute", "specialty": "Orthopedics"}
)
```

**Generates Cypher:**
```cypher
CREATE (e:Facility {name: 'Norton Orthopedic Institute', specialty: 'Orthopedics'})
RETURN e.name as name, labels(e)[0] as type
```

### Relationship Creation (Outgoing)
```python
relationships=[{
    "rel_type": "PART_OF",
    "target_entity_type": "HealthSystem",
    "target_properties": {"name": "Norton Healthcare"},
    "direction": "outgoing"  # Default
}]
```

**Generates Cypher:**
```cypher
MATCH (source:Facility {name: 'Norton Orthopedic Institute'})
MATCH (target:HealthSystem {name: 'Norton Healthcare'})
CREATE (source)-[:PART_OF]->(target)
```

### Relationship Creation (Incoming)
```python
relationships=[{
    "rel_type": "TREATED_AT",
    "target_entity_type": "Client",
    "target_properties": {"name": "Christopher Lanier"},
    "direction": "incoming"
}]
```

**Generates Cypher:**
```cypher
MATCH (source:Location {name: 'Starlight Chiropractic'})
MATCH (target:Client {name: 'Christopher Lanier'})
CREATE (target)-[:TREATED_AT]->(source)
```

---

## Agent Workflow

### Before using write_entity()

**Agent must:**
1. Read `KNOWLEDGE_GRAPH_SCHEMA.md` to understand:
   - Valid entity types (52 types)
   - Required properties for each type
   - Relationship patterns
   - Examples

**Example agent interaction:**
```
User: "Create a BI claim for $50,000 for the Lanier case with State Farm"

Agent:
1. Reads KNOWLEDGE_GRAPH_SCHEMA.md
2. Identifies:
   - Entity type: BIClaim
   - Required properties: claim_number, status, amount_demanded
   - Relationships: UNDER_POLICY → InsurancePolicy, HAS_CLAIM (incoming) ← Case
3. Calls write_entity() with correct schema
4. Confirms creation
```

---

## Deployment Status

### Files Deployed to VM ✅

**1. /home/aaronwhaley/roscoe/src/roscoe/agents/paralegal/tools.py**
- Added: `write_entity()` function
- Removed: `update_case_data()`, `associate_document()`
- Kept: All read tools (query_case_graph, graph_query, etc.)

**2. /home/aaronwhaley/roscoe/src/roscoe/agents/paralegal/agent.py**
- Updated imports to include `write_entity`
- Removed `update_case_data` and `associate_document` from tool list
- Tool count unchanged (removed 2, added 1)

**3. /home/aaronwhaley/roscoe/src/roscoe/agents/paralegal/prompts.py**
- Added Write Tools section
- Documented write_entity with schema reference requirement
- Organized tools into Write/Workflow/Read categories

**4. /home/aaronwhaley/roscoe/src/roscoe/core/case_context_middleware.py**
- Fixed insurance query (Claim → InsurancePolicy → Insurer)
- Fixed provider query (Client → Facility/Location with three-tier hierarchy)

**5. /home/aaronwhaley/roscoe/src/roscoe/workflow_engine/orchestrator/graph_state_computer.py**
- Converted to Pydantic BaseModel
- Fixed provider and insurance queries

### Query Scripts Deployed to GCS ✅

**Location:** `gs://whaley_law_firm/Tools/queries/`

Scripts uploaded:
- `get_case_overview.py`
- `get_case_insurance.py`
- `get_case_providers.py`
- `get_case_liens.py`
- `get_case_timeline.py`
- `README.md`

###Documentation Deployed to GCS ✅

**Location:** `gs://whaley_law_firm/`

- `KNOWLEDGE_GRAPH_SCHEMA.md` - Complete schema reference

### Agent Container Status ✅

**Container:** `roscoe-agents`
- Status: Up 46 seconds (healthy)
- API: http://localhost:8123/ok → {"ok":true}
- Logs: "Application startup complete"
- No errors in startup

---

## Testing write_entity()

### Test 1: Create Facility with Hierarchy
```python
write_entity(
    entity_type="Facility",
    properties={
        "name": "Test Orthopedic Clinic",
        "specialty": "Orthopedics",
        "phone": "502-555-TEST"
    },
    relationships=[
        {
            "rel_type": "PART_OF",
            "target_entity_type": "HealthSystem",
            "target_properties": {"name": "Norton Healthcare"}
        }
    ]
)
```

**Expected Result:**
```
✅ Entity created in knowledge graph

**Type**: Facility
**Name**: Test Orthopedic Clinic

**Relationships** (1 created):
  ✅ -[:PART_OF]-> HealthSystem
```

### Test 2: Create Treatment Relationship
```python
write_entity(
    entity_type="Location",
    properties={
        "name": "Test Chiropractic",
        "address": "123 Test St, Louisville, KY"
    },
    relationships=[
        {
            "rel_type": "TREATED_AT",
            "target_entity_type": "Client",
            "target_properties": {"name": "Christopher Lanier"},
            "direction": "incoming"
        }
    ]
)
```

**Expected Result:**
```
✅ Entity created in knowledge graph

**Type**: Location
**Name**: Test Chiropractic

**Relationships** (1 created):
  ✅ <-[:TREATED_AT]<- Client
```

### Test 3: Create Insurance Claim
```python
write_entity(
    entity_type="BIClaim",
    properties={
        "claim_number": "TEST-123",
        "status": "active",
        "amount_demanded": 50000.00,
        "date_filed": "2026-01-05"
    },
    relationships=[
        {
            "rel_type": "HAS_CLAIM",
            "target_entity_type": "Case",
            "target_properties": {"name": "Christopher-Lanier-MVA-6-28-2025"},
            "direction": "incoming"
        }
    ]
)
```

**Expected Result:**
```
✅ Entity created in knowledge graph

**Type**: BIClaim
**Name**: TEST-123

**Relationships** (1 created):
  ✅ <-[:HAS_CLAIM]<- Case
```

---

## Benefits

### Before (Graphiti write tools)
- ❌ LLM-based entity extraction (non-deterministic)
- ❌ Required natural language descriptions
- ❌ Slower (LLM processing required)
- ❌ Less predictable results
- ❌ Dependency on Graphiti library

### After (write_entity tool)
- ✅ Direct Cypher creation (deterministic)
- ✅ Structured input (properties dict)
- ✅ Faster (no LLM overhead)
- ✅ Predictable, verifiable results
- ✅ No Graphiti dependency for writes

---

## What The Agent Can Now Do

### Create Entities
- Cases, Clients, Defendants
- Facilities, Locations (medical providers)
- Insurance policies, claims, payments
- Insurers, Adjusters
- Liens, Lien holders
- Attorneys, Law firms, offices
- Medical visits, Bills, Expenses
- Court events, Pleadings
- Any of the 52 entity types in the schema

### Create Relationships
- Treatment: Client -[:TREATED_AT]-> Facility/Location
- Hierarchy: Location -[:PART_OF]-> Facility -[:PART_OF]-> HealthSystem
- Insurance: Claim -[:UNDER_POLICY]-> InsurancePolicy -[:WITH_INSURER]-> Insurer
- Case linkage: Case -[:HAS_CLAIM]-> Claim, Case -[:HAS_CLIENT]-> Client
- Any relationship pattern from the schema

### Bulk Operations
Agent can now create entire case structures from scratch:
1. Create Case entity
2. Create Client entity
3. Link: Case -[:HAS_CLIENT]-> Client
4. Create Facilities for each provider
5. Link: Client -[:TREATED_AT]-> Facility
6. Create InsurancePolicy
7. Create BIClaim, PIPClaim
8. Link: Claim -[:UNDER_POLICY]-> Policy

**All with single `write_entity()` tool!**

---

## Next Use Case

**User mentioned:** "I have to go through and create all of the initial workflow relationships as well as the medical facility relationships from scratch"

**Agent can now:**
1. Read case data (via auto-context or query scripts)
2. Read `KNOWLEDGE_GRAPH_SCHEMA.md` for relationship patterns
3. Use `write_entity()` to create:
   - Workflow Phase entities
   - Workflow Landmark entities
   - Case -[:IN_PHASE]-> Phase relationships
   - Case -[:HAS_STATUS]-> LandmarkStatus relationships
   - Medical facility TREATED_AT relationships
4. Verify with `query_case_graph()` or `graph_query()`

**This will be MUCH faster than manually writing Cypher!**

---

## Schema-Aware Agent

The agent MUST read `KNOWLEDGE_GRAPH_SCHEMA.md` before using `write_entity()` because:
- 52 entity types with specific property requirements
- 30+ relationship types with specific patterns
- Required vs optional properties vary by type
- Relationship directions matter (incoming vs outgoing)

**Agent workflow:**
```
1. User: "Create workflow relationships for all cases"
2. Agent reads: KNOWLEDGE_GRAPH_SCHEMA.md
3. Agent understands: Case -[:IN_PHASE]-> Phase pattern
4. Agent calls: write_entity() for each case
5. Agent verifies: get_case_workflow_status()
```

---

## Verification

### Container Status
```bash
$ sudo docker ps | grep roscoe-agents
roscoe-agents   Up 46 seconds (healthy)   0.0.0.0:8123->8000/tcp
```

### API Health
```bash
$ curl http://localhost:8123/ok
{"ok":true}
```

### Logs
```
Application startup complete.
Uvicorn running on http://0.0.0.0:8000
```

### No Errors
- No syntax errors
- No import errors
- No Graphiti dependency errors

---

## Documentation Reference

**For Agent:**
- `KNOWLEDGE_GRAPH_SCHEMA.md` - Complete schema with all entity types, properties, relationships
- `TOOLS_QUERIES_README.md` - Query scripts documentation
- Tool docstring - Comprehensive examples in `write_entity()` function

**For Developers:**
- `GRAPH_TOOLS_ARCHITECTURE_COMPLETE.md` - Complete architecture guide
- `GRAPH_STATE_COMPUTER_UPDATES.md` - State computer changes
- `WRITE_ENTITY_TOOL_DEPLOYMENT.md` - This document

---

## Summary

✅ **Agent now has deterministic write capabilities**
✅ **No Graphiti dependency for writes (only for semantic search reading)**
✅ **Single universal tool reduces prompt footprint**
✅ **Schema-aware agent can create any entity type**
✅ **Perfect for bulk operations like workflow initialization**

**Ready for use!** 🎉
