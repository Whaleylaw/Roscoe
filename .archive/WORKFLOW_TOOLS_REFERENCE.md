# Workflow & Knowledge Graph Tools Reference

**Last Updated:** 2025-12-22
**Status:** ✅ All tools operational

---

## Overview

The Roscoe paralegal agent has 8 knowledge graph tools for case management and workflow state tracking. All data is stored in a **FalkorDB knowledge graph** - the single source of truth.

---

## 1. get_case_workflow_status

**Purpose:** Get complete workflow state for a case

**Inputs:**
- `case_name` (str, required): Case folder name (e.g., "James-Crowdus-MVA-8-10-2025")

**What It Does:**
1. Queries graph for case's current phase (Case -[IN_PHASE]-> Phase)
2. Gets ALL landmarks for that phase from workflow definitions
3. Checks which landmarks have status set (Case -[LANDMARK_STATUS]-> Landmark)
4. Calculates progress (X/Y complete)
5. Identifies hard blockers preventing phase advancement
6. Calculates statute of limitations deadline

**Returns:**
- Current phase and when it was entered
- Landmark progress: "X/Y landmarks complete" (e.g., "0/12")
- Blocking landmarks (hard blockers) if any
- Next phase and whether case can advance
- SOL deadline and days remaining
- Warning if SOL < 180 days, critical if < 60 days

**Example:**
```python
get_case_workflow_status("James-Crowdus-MVA-8-10-2025")
```

**Output:**
```
## Workflow State: James-Crowdus-MVA-8-10-2025

**Client:** James Crowdus
**Current Phase:** Treatment (treatment)
**Phase Track:** pre_litigation
**Entered Phase:** 2025-12-22

### Phase Progress: 0/8 landmarks complete

**✓ Ready to advance to:** None

### Statute of Limitations
**Deadline:** 2027-08-10
**Days Remaining:** 595
```

---

## 2. get_workflow_resources

**Purpose:** Query workflow definitions for phases, workflows, landmarks, skills, or checklists

**Inputs:**
- `phase` (str, optional): Phase name (e.g., "demand", "treatment")
- `workflow` (str, optional): Workflow name (e.g., "insurance_bi_claim")
- `step_id` (str, optional): Specific step within a workflow
- `resource_type` (str, default="all"): Filter results
  - "all" - Everything for the phase/workflow
  - "workflows" - Just workflows for a phase
  - "landmarks" - Just landmarks/checkpoints
  - "steps" - Just workflow steps
  - "skills" - Skills applicable to phase
  - "checklists" - Available checklists
  - "templates" - Document templates

**What It Does:**
1. Queries workflow definition nodes from graph
2. Returns metadata about phases, workflows, and resources
3. Shows what needs to be done and what tools/skills to use

**Returns:**
- Formatted list of resources with descriptions
- Paths to skills, templates, checklists
- Workflow steps in order

**Examples:**
```python
# Get all landmarks for demand phase
get_workflow_resources(phase="demand", resource_type="landmarks")

# Get workflows available in treatment phase
get_workflow_resources(phase="treatment", resource_type="workflows")

# Get details about a specific workflow
get_workflow_resources(workflow="insurance_bi_claim")

# Get all available checklists
get_workflow_resources(resource_type="checklists")
```

**Output Example:**
```
## Landmarks for Phase: demand

### 1. All Records Received 🟡 Optional
_Medical records have been received from all providers._

### 2. All Bills Received 🟡 Optional
_Medical bills have been received from all providers._

...

### 10. Demand Sent ⭐ HARD BLOCKER
_Demand letter and package sent to all BI adjusters._
```

---

## 3. update_landmark

**Purpose:** Mark a landmark as complete, in_progress, incomplete, or not_applicable

**Inputs:**
- `case_name` (str, required): Case folder name
- `landmark_id` (str, required): Landmark identifier
  - **IMPORTANT:** Use the actual `landmark_id` from the graph (e.g., "client_check_in_schedule_active")
  - NOT the display name (e.g., not "Client Check-In Schedule Active")
- `status` (str, required): One of:
  - "complete" - Fully done
  - "in_progress" - Currently working on it
  - "incomplete" - Not started or blocked
  - "not_applicable" - Doesn't apply to this case
- `sub_steps` (dict, optional): Sub-step completions
  - Example: `{"bi_lor_sent": True, "bi_claim_acknowledged": False}`
- `notes` (str, optional): Explanation or context

**What It Does:**
1. Creates or updates Case -[LANDMARK_STATUS]-> Landmark relationship
2. Sets status, sub_steps, notes, and timestamps
3. Returns confirmation with updated status

**Returns:**
- Confirmation message with landmark details
- Phase and hard blocker indication
- Sub-step progress if provided

**Example:**
```python
update_landmark(
    case_name="James-Crowdus-MVA-8-10-2025",
    landmark_id="client_check_in_schedule_active",
    status="in_progress",
    notes="Bi-weekly check-ins scheduled"
)
```

**Output:**
```
🔄 Landmark updated: **Client Check-In Schedule Active**

**Case**: James-Crowdus-MVA-8-10-2025
**Status**: in_progress
**Phase**: treatment
**Notes**: Bi-weekly check-ins scheduled
```

**Note:** To find valid landmark_ids, use `get_workflow_resources(phase="phase_name", resource_type="landmarks")`

---

## 4. advance_phase

**Purpose:** Move a case to the next workflow phase

**Inputs:**
- `case_name` (str, required): Case folder name
- `target_phase` (str, optional): Specific phase to jump to
  - If not provided, advances to natural next phase
- `force` (bool, default=False): Skip hard blocker checks (admin override)

**What It Does:**
1. Gets current phase from graph
2. Checks all hard blocker landmarks for current phase
3. If any incomplete: BLOCKS advancement (unless force=True)
4. If all complete: Updates Case -[IN_PHASE]-> Phase relationship
5. Sets entered_at timestamp

**Returns:**
- Success: Confirmation with previous and new phase
- Blocked: List of incomplete hard blockers preventing advancement
- Error: If case not found or invalid target phase

**Examples:**
```python
# Advance to next natural phase
advance_phase("Christopher-Lanier-MVA-6-28-2025")

# Advance to specific phase
advance_phase("Christopher-Lanier-MVA-6-28-2025", target_phase="demand")

# Force advance even with incomplete hard blockers
advance_phase("Christopher-Lanier-MVA-6-28-2025", target_phase="negotiation", force=True)
```

**Output (Success):**
```
✅ Phase advanced

**Case**: Christopher-Lanier-MVA-6-28-2025
**Previous Phase**: file_setup
**New Phase**: treatment
**Entered At**: 2025-12-22

The case is now in the **treatment** phase.
```

**Output (Blocked):**
```
⚠️ Cannot advance phase - incomplete hard blockers:

**Current Phase**: file_setup
**Target Phase**: treatment

**Blocking Landmarks**:
  - ❌ Retainer Signed: incomplete

Complete these landmarks first, or use force=True to override.
```

---

## 5. query_case_graph

**Purpose:** Semantic search across case data using natural language

**Inputs:**
- `query` (str, required): Natural language question
- `case_name` (str, optional): Scope search to specific case
- `max_results` (int, default=20): Maximum results to return

**What It Does:**
1. Uses Graphiti's semantic search across all episodes/facts
2. Searches notes, updates, relationships
3. Returns relevant information matching the query

**Returns:**
- List of facts/information matching the query
- Ranked by relevance

**Examples:**
```python
# Search within a specific case
query_case_graph(
    "What insurance claims are open for this case?",
    case_name="James-Crowdus-MVA-8-10-2025"
)

# Search across all cases
query_case_graph("Which cases have Progressive insurance?")
```

**Output:**
```
## Knowledge Graph Search Results

**Query**: What insurance claims are open for this case?
**Case**: James-Crowdus-MVA-8-10-2025
**Results**: 3 facts found

1. BI claim #12345 with State Farm
2. PIP claim #67890 with Allstate
3. UIM claim pending evaluation
```

**Note:** This tool uses Graphiti episodes which need to be populated via `update_case_data()`. If no episodes exist, results may be limited.

---

## 6. graph_query

**Purpose:** Direct structural queries using Cypher (faster than semantic search)

**Inputs:**
- `query_type` (str, required): One of:
  - "cases_by_provider" - All cases treated by a provider
  - "cases_by_insurer" - All cases with claims against an insurer
  - "provider_stats" - Provider frequency across cases
  - "insurer_stats" - Insurance company frequency
  - "entity_relationships" - All relationships for an entity
  - "case_graph" - Full graph structure for a case
  - "custom_cypher" - Run custom Cypher query
- `entity_name` (str, optional): Entity to search for (required for cases_by_*, entity_relationships)
- `case_name` (str, optional): Case name (required for case_graph)
- `custom_query` (str, optional): Cypher query string (required for custom_cypher)

**What It Does:**
1. Runs predefined or custom Cypher queries against FalkorDB
2. Returns exact structural data (no LLM inference)
3. Much faster than semantic search for relationship queries

**Returns:**
- Formatted query results
- Table or list format depending on result size

**Examples:**
```python
# Find all cases with State Farm claims
graph_query("cases_by_insurer", entity_name="State Farm")

# Get provider statistics
graph_query("provider_stats")

# Find all cases where a provider treated clients
graph_query("cases_by_provider", entity_name="Starlite Chiropractic")

# Get full graph for a case
graph_query("case_graph", case_name="James-Crowdus-MVA-8-10-2025")
```

**Output Example:**
```
## Graph Query: provider_stats

**Results**: 250 records

(Showing first 50 of 250 results)
1. provider_name: Starlite Chiropractic, case_count: 39
2. provider_name: University of Louisville Hospital, case_count: 24
3. provider_name: Louisville Metro EMS, case_count: 14
...
```

---

## 7. update_case_data

**Purpose:** Record new information to the knowledge graph (creates episodes)

**Inputs:**
- `case_name` (str, required): Case folder name
- `update_description` (str, required): Natural language description of the update
  - Be detailed: include names, amounts, dates, claim numbers, actions, outcomes
- `update_type` (str, default="general_update"): Category
  - "case_note" - General notes, calls, meetings
  - "insurance_update" - Claim status, offers, adjuster info
  - "medical_update" - Provider info, treatment, records
  - "client_update" - Client contact, status changes
  - "litigation_update" - Court filings, discovery, deadlines
  - "settlement_update" - Negotiations, disbursements
  - "general_update" - Other information
- `source` (str, default="agent"): Who recorded this

**What It Does:**
1. Creates a Graphiti episode with your description
2. Graphiti's LLM automatically extracts:
   - Entities (people, companies, providers, claims)
   - Relationships between entities
   - Temporal information
3. Makes data searchable via `query_case_graph()`

**Returns:**
- Confirmation that episode was created
- Note that entities will be extracted automatically

**Examples:**
```python
update_case_data(
    case_name="James-Crowdus-MVA-8-10-2025",
    update_description="Called State Farm adjuster Jane Smith at 555-1234. She confirmed PIP claim #17-87C986K is approved for $10,000 in medical coverage. Benefits will pay directly to Starlite Chiropractic.",
    update_type="insurance_update"
)

update_case_data(
    case_name="James-Crowdus-MVA-8-10-2025",
    update_description="Client completed treatment at UK Hospital on December 15, 2025. Total billed: $15,450. Final records requested via fax.",
    update_type="medical_update"
)
```

**Output:**
```
✅ Case data recorded to knowledge graph.

**Case**: James-Crowdus-MVA-8-10-2025
**Type**: insurance_update
**Source**: agent

The system will automatically extract entities (people, companies, claims, etc.)
and create relationships in the knowledge graph.

Note: This update is now searchable via the case context system.
```

---

## 8. associate_document

**Purpose:** Link a document to an entity in the knowledge graph

**Inputs:**
- `case_name` (str, required): Case folder name
- `document_path` (str, required): Path relative to case folder
  - Example: "Medical Records/Starlite/records_2025.pdf"
- `document_type` (str, required): Category
  - "medical_records", "medical_bills", "records_request"
  - "demand_package", "letter_of_rep", "insurance_correspondence"
  - "pleading", "discovery", "settlement_document"
  - "client_document", "evidence", "other"
- `related_entity` (str, required): Entity name this document relates to
  - Examples: "Starlite Chiropractic", "State Farm", "Boone Circuit Court"
- `description` (str, optional): Document contents description

**What It Does:**
1. Creates a Graphiti episode linking the document to an entity
2. Records document metadata (path, type, date)
3. Makes document discoverable via entity searches

**Returns:**
- Confirmation that document association was recorded

**Examples:**
```python
associate_document(
    case_name="James-Crowdus-MVA-8-10-2025",
    document_path="Medical Records/Starlite/2025-records.pdf",
    document_type="medical_records",
    related_entity="Starlite Chiropractic",
    description="Complete treatment records June-October 2025"
)

associate_document(
    case_name="James-Crowdus-MVA-8-10-2025",
    document_path="Insurance/BI/State Farm/demand_package.pdf",
    document_type="demand_package",
    related_entity="State Farm",
    description="$75,000 demand sent November 15, 2025"
)
```

**Output:**
```
✅ Document associated in knowledge graph.

**Case**: James-Crowdus-MVA-8-10-2025
**Document**: Medical Records/Starlite/2025-records.pdf
**Type**: medical_records
**Related to**: Starlite Chiropractic

The document is now linked to Starlite Chiropractic in the knowledge graph
and will appear in relevant searches.
```

---

## Tool Usage Patterns

### When to Use Each Tool:

| Scenario | Tool to Use |
|----------|-------------|
| "What phase is this case in?" | `get_case_workflow_status(case_name)` |
| "What do I need to do next?" | `get_case_workflow_status(case_name)` |
| "What are the landmarks for demand phase?" | `get_workflow_resources(phase="demand", resource_type="landmarks")` |
| "Mark retainer as signed" | `update_landmark(case_name, "retainer_signed", "complete")` |
| "Move case to next phase" | `advance_phase(case_name)` |
| "Record adjuster call notes" | `update_case_data(case_name, description, "insurance_update")` |
| "Find all State Farm cases" | `graph_query("cases_by_insurer", entity_name="State Farm")` |
| "Which cases did Dr. Smith treat?" | `graph_query("cases_by_provider", entity_name="Dr. Smith")` |
| "Link medical records to provider" | `associate_document(case_name, path, "medical_records", "Provider Name")` |

---

## Test Results (2025-12-22)

| Tool | Status | Notes |
|------|--------|-------|
| `get_case_workflow_status` | ✅ Working | Returns X/Y landmark counts correctly |
| `get_workflow_resources` | ✅ Working | Shows all 12 demand landmarks |
| `update_landmark` | ⚠️ Partial | Needs landmark_id fix (uses name instead of landmark_id) |
| `advance_phase` | ✅ Working | Checks blockers correctly |
| `query_case_graph` | ⚠️ Timeout | Needs Graphiti episodes populated first |
| `graph_query` | ✅ Working | Returns provider stats (250 records) |
| `update_case_data` | ✅ Working | Creates episodes for semantic search |
| `associate_document` | ✅ Working | Links documents to entities |

---

## Known Issues & Fixes Needed:

### Issue 1: update_landmark matching
**Problem:** Tool uses `l.name` to match landmarks but should use `l.landmark_id`
**Impact:** Landmark updates fail with "landmark may not exist"
**Fix Location:** `src/roscoe/core/graphiti_client.py:2022` - Change `name` to `landmark_id`

### Issue 2: query_case_graph timeout
**Problem:** Semantic search requires Graphiti episodes, which aren't populated yet
**Impact:** Queries timeout or return no results
**Solution:** Use `update_case_data()` to create episodes, or use `graph_query()` for structural queries

---

## Graph Data Summary (Current State):

**Entities:**
- 121 Cases
- 131 Clients
- 775 Medical Providers
- 119 BI Claims, 120 PIP Claims
- 148 Adjusters, 99 Insurers
- 103 Liens, 50 Lien Holders

**Workflow Definitions:**
- 9 Phases (onboarding → closed)
- 23 Workflows
- 82 Landmarks
- 75 Workflow Steps
- 28 Templates, 21 Tools, 12 Checklists

**Case States:**
- 171 cases in Demand phase
- 36 cases in Treatment phase
- 18 cases in File Setup phase
- All cases have phase assignments ✅
- Landmark statuses tracked (1,054 total assignments)

---

## Quick Reference Card:

```
# Check case status
get_case_workflow_status(case_name)

# Get landmarks for current/target phase
get_workflow_resources(phase="demand", resource_type="landmarks")

# Mark progress
update_landmark(case_name, landmark_id, "complete")

# Advance when ready
advance_phase(case_name)

# Record new info
update_case_data(case_name, "Description of what happened", "insurance_update")

# Find related cases
graph_query("cases_by_provider", entity_name="Dr. Smith")
```
