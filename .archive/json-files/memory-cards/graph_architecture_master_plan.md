# Roscoe Knowledge Graph: Architecture & Workflow Integration

**Date:** December 21, 2025
**Status:** Design & Implementation Plan
**Decision:** Hybrid Approach (Direct Cypher + Graphiti)

---

## Table of Contents

1. [Architectural Decision: Graphiti vs Direct Cypher](#architectural-decision)
2. [Recommended Hybrid Approach](#hybrid-approach)
3. [Workflow Integration Design](#workflow-integration)
4. [Implementation Plan](#implementation-plan)
5. [Complete Examples](#complete-examples)
6. [Success Criteria](#success-criteria)

---

<a name="architectural-decision"></a>
## Part 1: Architectural Decision

### **The Core Question**

**Should we use Graphiti for everything, or mix Direct Cypher with Graphiti?**

Your "memory card" workaround suggests the answer: **Hybrid approach**.

---

### **What Graphiti Provides**

#### **Core Value Propositions:**

1. **LLM-Based Entity Extraction**
   - Natural language → Entities + Relationships
   - Example: "Elizabeth saw Dr. Smith, back is worse" → Extracts Client, Provider, symptom

2. **Temporal Awareness**
   - Tracks WHEN facts were added vs WHEN they occurred
   - Historical queries: "What did we know in January?"

3. **Hybrid Search**
   - Semantic (embeddings) + keyword + graph traversal
   - Better than simple keyword search

4. **Entity Deduplication**
   - "Jennifer Howard" = "J. Howard" = "Ms. Howard"
   - Automatic merging

5. **Community Summaries**
   - Aggregates episodes into case narrative
   - LLM-generated summaries

---

### **Your Data Breakdown**

| Data Type | % | Structured? | Graphiti Value |
|-----------|---|-------------|----------------|
| Case entities (Case, Client, Defendant) | 5% | ✅ High | ❌ LOW |
| Claims (PIP, BI, UM, UIM, WC) | 20% | ✅ High | ❌ LOW |
| Insurance/Medical (Insurer, Adjuster, Provider) | 15% | ✅ High | ❌ LOW |
| Liens (Lien, LienHolder) | 5% | ✅ High | ❌ LOW |
| **Workflow** (Phase, Landmark, WorkflowDef) | 10% | ✅ High | ❌ LOW |
| **Notes** (communications, updates) | 30% | ❌ Unstructured | ✅ HIGH |
| Documents (records, pleadings) | 10% | ⚠️ Semi | ⚠️ MEDIUM |
| Episodes (events, milestones) | 5% | ❌ Unstructured | ✅ HIGH |

**Finding:** 55% of data is highly structured → Graphiti adds minimal value

**Memory cards exist** because you're forcing structure onto Graphiti → Red flag!

---

### **The Memory Card Problem**

**Current approach:**
```python
# Pre-structure everything for Graphiti
memory_card = {
  "entity_type": "BIClaim",
  "name": "Elizabeth-Lindsey-BI-24-902741838",
  "attributes": {"claim_number": "24-902741838", "insurer_name": "Progressive"},
  "relationships": [{"type": "INSURED_BY", "target": "Progressive"}]
}

# Wrap in episode
graphiti.add_episode(f"Created claim: {json.dumps(memory_card)}")
```

**Why this is wrong:**
- ❌ Pre-structuring defeats Graphiti's auto-extraction
- ❌ You don't trust the LLM → Need deterministic creation
- ❌ Graphiti becomes expensive wrapper around simple inserts

**This proves: Your data is too structured for Graphiti**

---

### **Where Each Approach Excels**

#### **Graphiti Wins: Unstructured Narratives**

```python
✅ GOOD USE OF GRAPHITI:
graphiti.add_episode("""
Spoke with Courtny Wolfe (Auto Owners PIP adjuster) on 12/10.
PIP ledger shows $8k paid, $2k remaining.
Client asking when benefits will be paid.
Courtny needs updated Aptiva Health bills before releasing funds.
""")

# Graphiti extracts:
- Adjuster: Courtny Wolfe
- Insurer: Auto Owners
- Note type: PIP communication
- Amounts: $8k paid, $2k remaining
- Provider: Aptiva Health
- Action item: Send updated bills
- Timeline: 12/10
```

---

#### **Direct Cypher Wins: Structured Forms**

```python
✅ GOOD USE OF DIRECT CYPHER:
await create_biclaim(
    case_name="Elizabeth-Lindsey-MVA-12-01-2024",
    claim_number="24-902741838",
    insurer_name="Progressive Insurance Company",
    adjuster_name="Jennifer Howard",
    adjuster_phone="859-629-4740",
    policy_limit=100000,
    lor_sent_date="2024-12-05"
)

# Creates:
- BIClaim entity (exact schema)
- Links to existing Insurer entity
- Links to existing Adjuster entity
- HAS_CLAIM, INSURED_BY, ASSIGNED_ADJUSTER relationships
# All deterministic, no hallucinations
```

---

<a name="hybrid-approach"></a>
## Part 2: Recommended Hybrid Approach

### **Architecture: Two-Layer Graph**

```
┌──────────────────────────────────────────────────────────────┐
│              FalkorDB Graph Database (roscoe_graph)           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  STRUCTURED CORE (Direct Cypher - 65%)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ - Entities: Case, Client, Claim, Provider, Lien        │ │
│  │ - Relationships: HAS_CLIENT, HAS_CLAIM, TREATING_AT    │ │
│  │ - Workflow: Phase, Landmark, IN_PHASE, LANDMARK_STATUS │ │
│  │                                                         │ │
│  │ Agent Tools (Deterministic):                           │ │
│  │   • create_case() → Direct INSERT                      │ │
│  │   • create_claim() → Direct INSERT                     │ │
│  │   • update_phase() → Direct MERGE                      │ │
│  │   • verify_landmark() → Cypher query                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  UNSTRUCTURED LAYER (Graphiti - 35%)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ - Entities: Note, Episode                              │ │
│  │ - Content: Insurance notes, medical updates            │ │
│  │                                                         │ │
│  │ Agent Tools (LLM-Extracted):                           │ │
│  │   • add_note() → Graphiti.add_episode()                │ │
│  │   • search_notes() → Graphiti.search()                 │ │
│  │   • case_summary() → Graphiti.community_summary()      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  INTEGRATION:                                               │
│  Cypher entities -[HAS_NOTE]-> Graphiti Notes              │
└──────────────────────────────────────────────────────────────┘
```

---

### **Division of Responsibility**

| Operation | Method | Reason |
|-----------|--------|--------|
| **Create Case** | Direct Cypher | Structured form (name, date, type) |
| **Create Client** | Direct Cypher | Structured contact data |
| **Create BIClaim** | Direct Cypher | Structured insurance form |
| **Create Provider** | Direct Cypher | Structured directory entry |
| **Update Phase** | Direct Cypher | State machine logic |
| **Update Landmark** | Direct Cypher | Deterministic verification |
| **Add Insurance Note** | Graphiti | Unstructured communication |
| **Add Medical Update** | Graphiti | Unstructured narrative |
| **Search Notes** | Graphiti | Semantic search needed |
| **Case Summary** | Graphiti | LLM aggregation useful |
| **Verify Landmark** | Direct Cypher | Cypher query logic |

---

### **Implementation Files**

#### **graphiti_client.py** (Limit to Unstructured)

```python
# KEEP: Unstructured data operations
async def add_case_note(case_name, note_content, category, author)
async def search_case_notes(case_name, query)
async def generate_case_summary(case_name)

# REMOVE: Structured entity creation (move to graph_manager.py)
# ❌ create_case()
# ❌ create_claim()
# ❌ update_landmark()
```

#### **graph_manager.py** (NEW - Direct Cypher)

```python
# All structured entity operations
async def create_case(client_name, accident_date, case_type)
async def create_claim(case_name, claim_type, claim_data)
async def update_phase(case_name, new_phase)
async def update_landmark(case_name, landmark_id, status)
async def verify_landmark(case_name, landmark_id)
async def initialize_phase_landmarks(case_name, phase_name)
```

---

<a name="workflow-integration"></a>
## Part 3: Workflow Integration with Hybrid Approach

### **Current State**

**What Exists:**
- ✅ Workflow entities in schema (Phase, Landmark, WorkflowDef, etc.)
- ✅ Graph State Computer queries for `Case -[IN_PHASE]-> Phase`
- ✅ Workflow Middleware injects guidance
- ❌ Workflow definitions NOT in graph (still in GCS/JSON)
- ❌ Landmarks verified manually (agent must remember)
- ❌ No auto-verification

---

### **The Gap**

#### **Problem 1: Workflow Definitions Not in Graph**

**Current:**
- Phases, Landmarks, Workflows stored in GCS `whaley_law_firm/workflows/`
- Graph State Computer queries for Phase entities... that don't exist!

**Solution:**
- Ingest workflow definitions into graph (one-time)
- Use **Direct Cypher** (not Graphiti) - workflow structure is 100% structured
- `group_id: "__workflow_definitions__"` (separate from case data)

---

#### **Problem 2: Manual Landmark Verification**

**Current:**
```python
# Agent creates claim (manual)
create_biclaim(...)

# Agent updates landmark (manual - easy to forget!)
update_landmark("insurance_claims_setup", "complete")
```

**Desired:**
```python
# Agent creates claim
create_biclaim(...)

# System auto-verifies "insurance_claims_setup" landmark
# Checks: Does case have BIClaim with INSURED_BY relationship?
# If yes → Auto-marks landmark complete
```

---

#### **Problem 3: Landmarks Don't Know What They Verify**

**Current Landmark:**
```python
Landmark {
  landmark_id: "insurance_claims_setup",
  description: "Insurance claims opened and LORs sent",
  is_hard_blocker: true
}
```

**Enhanced Landmark:**
```python
Landmark {
  landmark_id: "insurance_claims_setup",
  description: "Insurance claims opened and LORs sent",
  is_hard_blocker: true,

  # NEW: Auto-verification
  verification_method: "graph_query",
  verification_entities: ["BIClaim", "PIPClaim"],
  verification_query: '''
    MATCH (case:Case {name: $case_name})-[:HAS_CLAIM]->(claim)
    WHERE exists((claim)-[:INSURED_BY]->(:Insurer))
    RETURN count(claim) > 0 as verified
  ''',
  auto_verify: true
}
```

Now landmark contains verification logic!

---

### **Workflow Structure in Graph**

**Using Direct Cypher (NOT Graphiti):**

```
Phase: "file_setup" {
  display_name: "File Setup",
  order: 1,
  track: "pre_litigation",
  next_phase: "treatment",
  entity_type: "Phase",
  group_id: "__workflow_definitions__"  // Separate namespace
}
  |
  ├─[HAS_LANDMARK]─> Landmark: "retainer_signed" {
  │                     landmark_id: "retainer_signed",
  │                     display_name: "Retainer Signed",
  │                     is_hard_blocker: true,
  │                     verification_method: "manual",
  │                     auto_verify: false,
  │                     entity_type: "Landmark",
  │                     group_id: "__workflow_definitions__"
  │                   }
  │
  ├─[HAS_LANDMARK]─> Landmark: "insurance_claims_setup" {
  │                     landmark_id: "insurance_claims_setup",
  │                     is_hard_blocker: true,
  │                     verification_method: "graph_query",
  │                     verification_query: "MATCH...",
  │                     auto_verify: true,
  │                     entity_type: "Landmark",
  │                     group_id: "__workflow_definitions__"
  │                   }
  │
  ├─[HAS_WORKFLOW]─> WorkflowDef: "intake" {
  │                     display_name: "Client Intake",
  │                     phase: "file_setup",
  │                     instructions_path: "/workflows/file_setup/intake/workflow.md",
  │                     entity_type: "WorkflowDef",
  │                     group_id: "__workflow_definitions__"
  │                   }
  │                     |
  │                     └─[HAS_STEP]─> WorkflowStep: "collect_client_info" {
  │                                       owner: "agent",
  │                                       can_automate: true,
  │                                       order: 1
  │                                     }
  │                                       ├─[USES_SKILL]-> WorkflowSkill: "/Skills/client-intake"
  │                                       └─[USES_TEMPLATE]-> WorkflowTemplate: "/Templates/intake.docx"
  |
  └─[NEXT_PHASE]─> Phase: "treatment"
```

**All created with Direct Cypher** - no Graphiti LLM involved.

---

### **Case Workflow State**

**Per-case, using Direct Cypher for state + Graphiti for notes:**

```
Case: "Elizabeth-Lindsey-MVA-12-01-2024" {
  case_type: "MVA",
  accident_date: "2024-12-01",
  entity_type: "Case",
  group_id: "roscoe_graph"  // Case data namespace
}
  |
  ├─[IN_PHASE {entered_at: "2024-12-01", previous_phase: null}]─> Phase: "file_setup"
  │  (Created by Direct Cypher)
  |
  ├─[LANDMARK_STATUS {status: "complete", completed_at: "2024-12-05", verified_by: "agent"}]
  │    → Landmark: "retainer_signed"
  │  (Updated by Direct Cypher)
  |
  ├─[LANDMARK_STATUS {status: "in_progress", sub_steps: {...}}]
  │    → Landmark: "insurance_claims_setup"
  │  (Updated by Direct Cypher + auto-verification)
  |
  ├─[HAS_CLIENT]─> Client: "Elizabeth Lindsey"
  │  (Created by Direct Cypher)
  |
  ├─[HAS_CLAIM]─> BIClaim {claim_number: "24-902741838"}
  │  (Created by Direct Cypher)
  │                └─[INSURED_BY]─> Insurer: "Progressive"
  │                └─[ASSIGNED_ADJUSTER]─> Adjuster: "Jennifer Howard"
  |
  ├─[HAS_NOTE]─> Note {
  │                date: "2024-12-10",
  │                content: "Spoke with adjuster...",
  │                author: "Coleen Madayag",
  │                category: "insurance_note"
  │              }
  │  (Created by GRAPHITI from natural language)
  |
  └─[TREATING_AT]─> MedicalProvider: "Aptiva Health"
     (Created by Direct Cypher)
       └─[HAS_NOTE]─> Note {content: "Client finished PT..."}
          (Created by GRAPHITI)
```

**Structured entities via Cypher, unstructured notes via Graphiti**

---

<a name="workflow-integration"></a>
## Part 4: Workflow Integration Design

### **Workflow Ingestion (One-Time, Direct Cypher)**

**Source:** GCS `whaley_law_firm/workflows/` folder

**Ingestion Script:**

```python
async def ingest_workflow_definitions():
    """
    Load workflow structure from GCS into graph.

    Uses DIRECT Cypher - workflow definitions are structured data.
    NO Graphiti involvement - we need deterministic structure.
    """
    workflows_path = "/mnt/workspace/workflows/"  # GCS mount

    # 1. Create Phase entities
    phases = load_json(f"{workflows_path}/phases.json")
    for phase in phases:
        await run_cypher_query('''
            CREATE (p:Entity {
                name: $name,
                entity_type: 'Phase',
                display_name: $display_name,
                description: $description,
                order: $order,
                track: $track,
                next_phase: $next_phase,
                group_id: '__workflow_definitions__'
            })
        ''', phase)

    # 2. Create Landmark entities
    for phase_folder in list_dirs(workflows_path):
        landmarks = load_json(f"{phase_folder}/landmarks.json")
        for landmark in landmarks:
            await run_cypher_query('''
                CREATE (l:Entity {
                    name: $landmark_id,
                    entity_type: 'Landmark',
                    landmark_id: $landmark_id,
                    display_name: $display_name,
                    phase: $phase,
                    is_hard_blocker: $is_hard_blocker,
                    verification_method: $verification_method,
                    verification_query: $verification_query,
                    auto_verify: $auto_verify,
                    sub_steps: $sub_steps,  # JSON string
                    group_id: '__workflow_definitions__'
                })
            ''', landmark)

            # Link to phase
            await run_cypher_query('''
                MATCH (p:Entity {entity_type: 'Phase', name: $phase})
                MATCH (l:Entity {entity_type: 'Landmark', landmark_id: $landmark_id})
                CREATE (p)-[:HAS_LANDMARK]->(l)
            ''', {"phase": landmark["phase"], "landmark_id": landmark["landmark_id"]})

    # 3. Create WorkflowDef, WorkflowStep entities...
    # (Similar pattern - all Direct Cypher)

    return {"success": True, "phases_loaded": len(phases)}
```

**Result:** Workflow structure in graph, accessible via Cypher queries.

---

### **Enhanced Landmark Schema** (For Auto-Verification)

```python
class Landmark(BaseModel):
    """A checkpoint that must be verified before phase advancement."""
    # Basic info
    landmark_id: Optional[str] = Field(None, description="Unique ID")
    display_name: Optional[str] = Field(None, description="Human-readable name")
    phase: Optional[str] = Field(None, description="Phase this belongs to")
    description: Optional[str] = Field(None, description="What this verifies")
    landmark_type: Optional[str] = Field(None, description="Type: document, entity, communication")

    # Blocking behavior
    is_hard_blocker: Optional[bool] = Field(None, description="Must complete before advancing")
    can_override: Optional[bool] = Field(None, description="Can user manually override")

    # AUTO-VERIFICATION (KEY FEATURE)
    verification_method: Optional[str] = Field(None, description="'graph_query', 'manual', 'hybrid'")
    verification_entities: Optional[str] = Field(None, description="JSON list of required entity types")
    verification_relationships: Optional[str] = Field(None, description="JSON list of required relationships")
    verification_query: Optional[str] = Field(None, description="Cypher query to verify")
    auto_verify: Optional[bool] = Field(None, description="Auto-update when verified")

    # SUB-STEPS
    sub_steps: Optional[str] = Field(None, description="JSON dict of sub-steps")
    parent_landmark: Optional[str] = Field(None, description="Parent if nested")
```

---

### **Auto-Verification Examples**

#### **Example 1: Insurance Claims** (Auto-Verifiable via Query)

```python
Landmark {
  landmark_id: "insurance_claims_setup",
  verification_method: "graph_query",
  verification_query: '''
    MATCH (case:Case {name: $case_name})-[:HAS_CLAIM]->(claim)
    WHERE claim.entity_type IN ['BIClaim', 'PIPClaim']
      AND exists((claim)-[:INSURED_BY]->(:Insurer))
    RETURN count(claim) > 0 as verified
  ''',
  auto_verify: true
}
```

**Flow:**
1. Agent creates BIClaim (Direct Cypher)
2. System runs `verify_landmark("insurance_claims_setup")`
3. Query finds BIClaim with INSURED_BY
4. System auto-marks landmark complete

---

#### **Example 2: Retainer Signed** (Manual)

```python
Landmark {
  landmark_id: "retainer_signed",
  verification_method: "manual",  // DocuSign webhook needed
  auto_verify: false
}
```

Agent manually marks when confirmed.

---

#### **Example 3: Medical Records** (Hybrid)

```python
Landmark {
  landmark_id: "medical_records_received",
  verification_method: "hybrid",
  verification_query: '''
    MATCH (case)-[:TREATING_AT]->(provider)
    OPTIONAL MATCH (case)-[:HAS_DOCUMENT {type: 'medical_records'}]->(doc)
    WHERE doc.source_provider = provider.name
    RETURN
      count(DISTINCT provider) as total,
      count(DISTINCT doc) as received,
      (received * 100 / total) as percentage
  ''',
  auto_verify: false  // Agent confirms when "good enough"
}
```

Query shows 3/5 providers (60%). Agent decides if sufficient.

---

### **Workflow State Queries** (Single Query Gets Everything)

```cypher
// Get complete workflow state
MATCH (case:Case {name: $case_name})-[r:IN_PHASE]->(phase:Phase)
MATCH (phase)-[:HAS_LANDMARK]->(landmark:Landmark)
OPTIONAL MATCH (case)-[ls:LANDMARK_STATUS]->(landmark)

// Get workflows for incomplete landmarks
OPTIONAL MATCH (landmark)-[:ACHIEVED_BY]->(workflow:WorkflowDef)
WHERE ls.status IS NULL OR ls.status <> 'complete'

// Get workflow steps and resources
OPTIONAL MATCH (workflow)-[:HAS_STEP]->(step:WorkflowStep)
OPTIONAL MATCH (step)-[:USES_SKILL]->(skill:WorkflowSkill)
OPTIONAL MATCH (step)-[:USES_TEMPLATE]->(template:WorkflowTemplate)

RETURN
  // Phase info
  phase.name, phase.display_name, phase.track, r.entered_at,

  // Landmarks
  collect(DISTINCT {
    id: landmark.landmark_id,
    display: landmark.display_name,
    is_blocker: landmark.is_hard_blocker,
    status: coalesce(ls.status, 'not_started'),
    completed_at: ls.completed_at
  }) as landmarks,

  // Next actions
  collect(DISTINCT {
    workflow: workflow.display_name,
    action: step.description,
    skill: skill.path,
    template: template.path
  })[0..5] as next_actions,

  // Progress
  sum(CASE WHEN ls.status = 'complete' THEN 1 ELSE 0 END) as complete,
  count(DISTINCT landmark) as total
```

**One query = complete workflow state!**

---

<a name="implementation-plan"></a>
## Part 5: Implementation Plan

### **Phase A: Schema Updates** (This Session)

1. ✅ Enhanced Landmark entity with verification fields
2. ✅ Create `graph_manager.py` with Direct Cypher functions:
   - `create_case()`
   - `create_claim()`
   - `update_phase()`
   - `update_landmark()`
   - `verify_landmark()`
   - `auto_verify_all_landmarks()`
   - `initialize_phase_landmarks()`

3. ✅ Limit `graphiti_client.py` to:
   - `add_case_note()` - Unstructured notes
   - `search_case_notes()` - Semantic search
   - `generate_case_summary()` - Community summaries
   - Remove structured entity creation functions

---

### **Phase B: Workflow Ingestion** (Next Session)

1. Create ingestion script: `ingest_workflows_to_graph.py`
2. Parse GCS `whaley_law_firm/workflows/` structure
3. Use **Direct Cypher** to create:
   - Phase entities
   - Landmark entities (with verification queries)
   - WorkflowDef, WorkflowStep entities
   - Relationships (HAS_LANDMARK, HAS_WORKFLOW, HAS_STEP, etc.)
4. All use `group_id: "__workflow_definitions__"`

---

### **Phase C: Migration** (Future)

1. Bulk import entity JSON files → Graph (Direct Cypher)
2. Migrate existing notes → Graphiti episodes
3. Initialize workflow state for existing cases
4. Test auto-verification

---

### **Phase D: Agent Tools** (Future)

1. `create_new_case(client_name, accident_date, case_type)` - Direct Cypher
2. `add_case_note(case_name, content, category)` - Graphiti
3. `search_case_history(case_name, query)` - Graphiti
4. `get_case_workflow_status(case_name)` - Direct Cypher query

---

<a name="complete-examples"></a>
## Part 6: Complete Examples

### **Example 1: New Case Creation** (Hybrid Approach)

```
User: "New client - Elizabeth Lindsey, car accident December 1st 2024"

Agent (uses Direct Cypher):
1. Creates Case entity with exact schema
2. Creates Client entity
3. Creates HAS_CLIENT relationship
4. Sets IN_PHASE → "file_setup"
5. Initializes LANDMARK_STATUS for all file_setup landmarks

Then (uses Graphiti):
6. Adds searchable episode:
   "Case created for Elizabeth Lindsey, MVA on 12/1/2024"

Agent responds:
"Case created! Elizabeth Lindsey MVA (12/1/2024)

Current Phase: File Setup (0/6 landmarks)

Next Actions:
1. Collect client contact/accident info (I can do this)
2. Send retainer via DocuSign (I can do this)
3. Identify insurance carriers

Shall I start the intake interview?"
```

**Why hybrid works:**
- Case structure is deterministic (Direct Cypher)
- Creation event is searchable (Graphiti episode)

---

### **Example 2: Workflow Execution** (Hybrid Approach)

```
User: "Yes, do the intake"

Agent (Direct Cypher):
1. Queries graph for workflow:
   MATCH (w:WorkflowDef {name: 'intake'})-[:HAS_STEP]->(step)
   OPTIONAL MATCH (step)-[:USES_SKILL]->(skill)
   RETURN step.description, skill.path ORDER BY step.order

2. Gets:
   - Step 1: "Collect client info" → Skill: /Skills/client-intake/
   - Step 2: "Send retainer" → Skill: /Skills/docusign/

3. Executes Step 1:
   - Asks client questions
   - Updates Client entity with data (Direct Cypher)
   - Auto-verification runs:
       MATCH (client:Client {name: "Elizabeth Lindsey"})
       WHERE client.phone IS NOT NULL AND client.email IS NOT NULL
       RETURN true as verified
   - Marks "client_info_collected" complete

Then (Graphiti):
4. Adds searchable note:
   "Completed client intake. Elizabeth Lindsey - phone 502-210-8328,
    email elindsey611@gmail.com. Accident 12/1/2024 on I-71, rear-ended
    at traffic light. Injuries: neck/back pain, seeing chiropractor."

Agent: "✓ Client info collected (auto-verified)

Next: Sending retainer agreement.
Template: /Templates/retainer.docx

Preparing DocuSign request..."
```

**Why hybrid works:**
- Workflow execution is deterministic (Direct Cypher)
- Interview content is searchable (Graphiti note)

---

### **Example 3: Auto-Verification** (Direct Cypher Logic)

```
User: "I opened a BI claim with Progressive, claim #24-902741838"

Agent (Direct Cypher):
1. Creates BIClaim entity:
   CREATE (claim:Entity {
       name: "Elizabeth-Lindsey-BI-24-902741838",
       entity_type: "BIClaim",
       claim_number: "24-902741838",
       insurer_name: "Progressive Insurance Company",
       group_id: "roscoe_graph"
   })

2. Creates relationships:
   MATCH (case:Case {name: "Elizabeth-Lindsey-MVA-12-01-2024"})
   MATCH (claim:Entity {entity_type: "BIClaim", claim_number: "24-902741838"})
   MATCH (insurer:Entity {entity_type: "Insurer", name: "Progressive Insurance Company"})
   CREATE (case)-[:HAS_CLAIM]->(claim)
   CREATE (claim)-[:INSURED_BY]->(insurer)

3. Triggers auto-verification:
   async def auto_verify_all_landmarks("Elizabeth-Lindsey-MVA-12-01-2024")

   Runs verification query for "insurance_claims_setup":
   MATCH (case)-[:HAS_CLAIM]->(claim)
   WHERE exists((claim)-[:INSURED_BY]->())
   RETURN count(claim) > 0 as verified

   Returns: verified = true

   Auto-updates:
   MATCH (case)-[ls:LANDMARK_STATUS]->(lm:Landmark {landmark_id: 'insurance_claims_setup'})
   SET ls.status = 'complete',
       ls.completed_at = $now,
       ls.verified_by = 'auto'

Then (Graphiti):
4. Adds searchable note:
   "BI claim opened with Progressive, claim #24-902741838.
    Coverage confirmed 100/300/100 limits."

Agent: "✓ BI claim created and verified!

Landmark 'Insurance Claims Setup' auto-completed based on graph data.

File Setup Progress: 50% (3/6 landmarks)

Next: Open PIP claim with client's insurer..."
```

**Auto-verification uses Direct Cypher** - no LLM guessing!

---

### **Example 4: Adding Unstructured Notes** (Pure Graphiti)

```
User: "Adjuster called - PIP is exhausted"

Agent (Graphiti):
graphiti.add_episode(
    episode_name="PIP adjuster call",
    episode_body="""
    Received call from Courtny Wolfe (Auto Owners PIP adjuster) at 2:15pm on 12/18/2024.
    She informed that PIP benefits have been exhausted - all $10,000 paid out.
    Final payment of $1,200 went to Aptiva Health for last 3 PT sessions.
    Client asking about outstanding bills - advised PIP is done, will pursue via BI claim.
    """
)

# Graphiti extracts:
- Note entity
- Links to: Adjuster "Courtny Wolfe", Insurer "Auto Owners", Provider "Aptiva Health"
- Amounts: $10,000 total, $1,200 final
- Date: 12/18/2024
- Status: "exhausted"

Then (Direct Cypher):
Updates PIPClaim entity:
MATCH (claim:Entity {entity_type: 'PIPClaim', insurer_name: 'Auto Owners'})
SET claim.exhausted = true,
    claim.amount_paid = 10000

Agent: "Noted - PIP exhausted ✓

I've updated the PIP claim status and added a searchable note.

Would you like me to calculate remaining medical bills to include in BI demand?"
```

**Note content via Graphiti (flexible), claim status via Cypher (deterministic)**

---

<a name="success-criteria"></a>
## Part 7: Success Criteria

### **When Implementation is Complete:**

✅ **Structured entities created reliably** (Direct Cypher - no LLM hallucinations)
✅ **Workflow state managed deterministically** (Direct Cypher state machine)
✅ **Landmarks auto-verified from graph data** (Cypher queries, no manual updates)
✅ **Notes are fully searchable** (Graphiti semantic search)
✅ **Case summaries generated from notes** (Graphiti community summaries)
✅ **Single query gets workflow status** (Cypher JOIN across workflow structure)
✅ **New case creation initializes proper state** (Direct Cypher + Graphiti episode)
✅ **Agent gets resource paths from graph** (Skills, templates from WorkflowStep relationships)
✅ **Zero JSON case files needed** (All state in graph)

---

## Part 8: Decision Summary

### **Final Answer to "Do we need Graphiti?"**

**YES, but only for ~35% of operations** (unstructured data)

### **What to Change:**

| Current Approach | New Hybrid Approach |
|------------------|---------------------|
| Everything through Graphiti episodes | Split: Cypher for structured, Graphiti for unstructured |
| Memory cards force structure | Memory cards are optional hints |
| Workflow state via Graphiti | Workflow state via Direct Cypher |
| Manual landmark updates | Auto-verification via Cypher queries |
| Agent creates entities via episodes | Agent uses specific tools (create_case, create_claim, add_note) |

---

### **Graphiti's Role (Refined):**

**What Graphiti DOES:**
- Ingest unstructured notes/communications
- Semantic search across notes
- Entity deduplication in notes
- Community summaries
- Temporal queries on episodes

**What Graphiti DOESN'T DO:**
- Create structured entities (Case, Client, Claim, Provider)
- Manage workflow state (Phase, Landmark)
- Run verification logic
- Handle deterministic relationships

---

### **Implementation Priority:**

**Immediate:**
1. Create `graph_manager.py` with Direct Cypher functions
2. Update Landmark schema with verification fields
3. Build auto-verification system

**Next:**
4. Ingest workflow definitions to graph (Direct Cypher)
5. Migrate existing entity JSON to graph (Direct Cypher)
6. Keep notes/episodes in Graphiti

**Result:** Best of both worlds - reliability + flexibility

---

## Conclusion

**The memory card workaround revealed the truth:** Most of your data is too structured for Graphiti.

**Solution:** Use the right tool for each job:
- **Direct Cypher** for the structured core (cases, claims, workflow state)
- **Graphiti** for the unstructured layer (notes, search, summaries)

This gives you:
- ✅ Deterministic entity creation
- ✅ Reliable workflow state management
- ✅ Semantic search on notes
- ✅ Case summaries from accumulated knowledge
- ✅ No "memory card" workarounds needed

**Next Step:** Implement `graph_manager.py` with Direct Cypher functions for structured entity management.
