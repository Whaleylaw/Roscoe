# Workflow Graph Implementation Plan (Based on Actual Data)

**Date:** December 23, 2025
**Source:** User's accurate outline in `workflow_state_machine.md` + actual `/mnt/workspace/workflows/` directory

---

## Verified Counts from Actual Workflow Directory

### Phases (9 total)

| # | Folder Name | Phase ID | Display Name | Track | Next Phase |
|---|-------------|----------|--------------|-------|------------|
| 0 | phase_0_onboarding | onboarding | Onboarding | pre_litigation | file_setup |
| 1 | phase_1_file_setup | file_setup | File Setup | pre_litigation | treatment |
| 2 | phase_2_treatment | treatment | Treatment | pre_litigation | demand |
| 3 | phase_3_demand | demand | Demand | pre_litigation | negotiation |
| 4 | phase_4_negotiation | negotiation | Negotiation | pre_litigation | settlement |
| 5 | phase_5_settlement | settlement | Settlement | settlement | lien |
| 6 | phase_6_lien | lien | Lien Resolution | settlement | closed |
| 7 | phase_7_litigation | litigation | Litigation | litigation | settlement |
| 8 | phase_8_closed | closed | Closed/Archived | closed | NULL |

**Note:** Litigation can loop back to settlement. Settlement can skip to closed (bypassing lien if no liens).

### Landmarks (from your accurate outline)

| Phase | Landmark Count | Landmark IDs |
|-------|----------------|--------------|
| 0: Onboarding | **3** | client_info_received, contract_signed, medical_auth_signed |
| 1: File Setup | **4** | full_intake_complete, accident_report_obtained, insurance_claims_setup (has BI/PIP sub-steps), providers_setup |
| 2: Treatment | **9** | client_check_in_schedule_active, all_providers_have_records_requested, records_received, bills_received, liens_identified, medical_chronology_started, treatment_status_known, treatment_complete, exit_conditions (has 2 sub: early_demand, sol_critical) |
| 3: Demand | **12** | all_records_received, all_bills_received, special_damages_calculated, medical_chronology_finalized, liens_identified, wage_loss_documented, demand_draft_prepared, exhibits_compiled, attorney_approved, demand_sent, client_notified, follow_up_scheduled |
| 4: Negotiation | **10** | one_week_followup_completed, deficiencies_addressed, thirty_day_follow_up_completed, initial_offer_received, net_to_client_calculated, offer_evaluated_by_attorney, client_authorized_decision, iterative_negotiation_documented, settlement_reached, negotiation_impasse |
| 5: Settlement | **11** | settlement_statement_prepared, authorization_to_settle_prepared, client_signed_authorization, settlement_confirmed_with_adjuster, release_received, release_signed_by_client, release_returned_to_insurance, settlement_check_received, check_deposited_and_cleared, liens_paid, client_received_funds |
| 6: Lien | **7** | outstanding_liens_identified, final_lien_amounts_requested, medicare_final_demand_received, lien_negotiations_complete, all_liens_paid, supplemental_settlement_statement_prepared, final_distribution_complete |
| 7: Litigation | **6 phase-level** | litigation_commenced, complaint_filed (HARD), defendant_served, answer_response_received, scheduling_order_entered, discovery (composite), mediation (composite), trial_prep (composite), trial_concluded |
| 8: Closed | **6** | all_obligations_verified, final_letter_sent, review_requested, physical_file_archived, digital_file_archived, case_fully_closed |

**TOTAL LANDMARKS: ~68** (exact count requires parsing all landmarks.md files)

### Litigation Sub-Phases (5 total)

Phase 7 has **sub-phases** instead of simple workflows:

| Sub-Phase | Folder | Landmarks | Workflows |
|-----------|--------|-----------|-----------|
| 7.1 | 7_1_complaint | 6 (complaint_drafted, complaint_filed, summons_issued, defendant_served, answer_received_or_default_sought, all_defendants_resolved) | draft_file_complaint, prepare_filing_package, serve_defendant |
| 7.2 | 7_2_answer_discovery | ~6 (our_discovery_propounded, defendant_responses_received, our_responses_served, client_deposition_complete, defendant_deposition_complete, discovery_cutoff_passed) | answer_response, initial_discovery |
| 7.3 | 7_3_depositions | ~6 (from landmarks.md) | deposition_prep, expert_witness |
| 7.4 | 7_4_mediation | 4 (mediation_scheduled, brief_submitted, client_prepared, mediation_attended) | mediation_prep, attend_mediation |
| 7.5 | 7_5_trial | 6 (expert_disclosures_filed, expert_depositions_complete, exhibit_list_filed, witness_list_filed, pretrial_brief_filed, trial_ready) | trial_prep, conduct_trial |

### Workflows (~35 total, from your outline)

| Phase | Workflows | Count |
|-------|-----------|-------|
| 0 | case_setup, document_collection | 2 |
| 1 | accident_report, insurance_bi_claim, insurance_pip_claim, medical_provider_setup | 4 |
| 2 | client_check_in, lien_identification, medical_chronology, medical_provider_status, referral_new_provider, request_records_bills | 6 |
| 3 | draft_demand, gather_demand_materials, send_demand | 3 |
| 4 | negotiate_claim, offer_evaluation, track_offers | 3 |
| 5 | lien_negotiation, settlement_processing | 2 |
| 6 | final_distribution, get_final_lien, negotiate_lien | 3 |
| 7.1 | draft_file_complaint, prepare_filing_package, serve_defendant | 3 |
| 7.2 | answer_response, initial_discovery | 2 |
| 7.3 | deposition_prep, expert_witness | 2 |
| 7.4 | mediation_prep, attend_mediation | 2 |
| 7.5 | trial_prep, conduct_trial | 2 |
| 8 | close_case | 1 |

**TOTAL: 35 workflows**

### Skills (47 from skills_manifest.json)

Verified from your outline - these are cataloged in `/workflows/skills/skills_manifest.json`

### Templates (Collections from templates_manifest.json)

- demand (2 templates)
- complaint (11 base + 8 modules)
- deposition (multiple)
- discovery (interrogatories, RFAs, RFPs)
- mediation
- medical
- negotiation
- output

**TOTAL: ~50+ templates**

### Tools (10 from tools_manifest.json)

1. create_case.py
2. pip_waterfall.py
3. lexis_crash_order.py
4. read_pdf.py
5. docusign_send.py
6. docusign_config.py
7. chronology_tools.py
8. medical_request_generator.py
9. generate_demand_pdf.py
10. generate_document.py

---

## Graph Schema Design

### Node Types to Create

#### 1. Phase Nodes (9 total)
```
entity_type: 'Phase'
group_id: '__workflow_definitions__'
Properties:
  - name: 'onboarding' | 'file_setup' | 'treatment' | ...
  - display_name: 'Onboarding' | 'File Setup' | ...
  - order: 0-8
  - track: 'pre_litigation' | 'litigation' | 'settlement' | 'closed'
  - next_phase: 'file_setup' | 'treatment' | ...
  - uuid: 'phase_onboarding' | 'phase_file_setup' | ...
```

#### 2. SubPhase Nodes (5 for litigation)
```
entity_type: 'SubPhase'
group_id: '__workflow_definitions__'
Properties:
  - name: 'complaint' | 'answer_discovery' | 'depositions' | 'mediation' | 'trial'
  - display_name: 'Complaint' | 'Answer & Discovery' | ...
  - parent_phase: 'litigation'
  - order: 1-5
  - uuid: 'subphase_litigation_complaint' | ...
```

#### 3. Landmark Nodes (~68 total)
```
entity_type: 'Landmark'
group_id: '__workflow_definitions__'
Properties:
  - landmark_id: 'client_info_received' | 'contract_signed' | ...
  - name: 'Client Info Received' | 'Contract Signed' | ...
  - phase: 'onboarding' | 'file_setup' | ...
  - subphase: NULL | 'complaint' | 'discovery' | ... (for litigation landmarks)
  - is_hard_blocker: true | false
  - can_override: true | false
  - order: 1, 2, 3...
  - sub_steps: NULL | ['step_a', 'step_b', ...] (for composite landmarks like insurance_claims_setup)
  - uuid: 'landmark_onboarding_client_info_received' | ...
```

#### 4. WorkflowDef Nodes (~35 total)
```
entity_type: 'WorkflowDef'
group_id: '__workflow_definitions__'
Properties:
  - name: 'case_setup' | 'document_collection' | ...
  - display_name: 'Case Setup' | 'Document Collection' | ...
  - phase: 'onboarding' | 'file_setup' | ...
  - subphase: NULL | 'complaint' | ... (for litigation workflows)
  - description: '...'
  - trigger: '...' (from workflow.md YAML frontmatter)
  - prerequisites: [...] (from workflow.md YAML frontmatter)
  - uuid: 'workflow_case_setup' | ...
```

#### 5. WorkflowSkill Nodes (47 from manifest)
```
entity_type: 'WorkflowSkill'
group_id: '__workflow_definitions__'
Properties:
  - name: 'docusign-send' | 'pip-waterfall' | ...
  - display_name: 'DocuSign Send' | 'PIP Waterfall' | ...
  - path: 'phase_0_onboarding/docusign-send/skill.md'
  - phase: 'onboarding' | 'file_setup' | ...
  - category: 'esignature' | 'insurance' | ...
  - description: '...'
  - keywords: ['DocuSign', 'signature', ...]
  - uuid: 'skill_docusign_send' | ...
```

#### 6. WorkflowTemplate Nodes (~50 from manifest)
```
entity_type: 'WorkflowTemplate'
group_id: '__workflow_definitions__'
Properties:
  - name: 'demand_template' | 'complaint_mva_standard' | ...
  - path: 'templates/demand/demand_template.md'
  - collection: 'demand' | 'complaint' | ...
  - file_type: 'md' | 'docx' | 'pdf'
  - case_type: NULL | 'MVA' | 'Premises' (for complaint templates)
  - uuid: 'template_demand_template' | ...
```

#### 7. WorkflowTool Nodes (10 from manifest)
```
entity_type: 'WorkflowTool'
group_id: '__workflow_definitions__'
Properties:
  - name: 'create_case' | 'pip_waterfall' | ...
  - path: 'tools/create_case.py'
  - category: 'case_management' | 'insurance' | ...
  - description: '...'
  - inputs: ['client_name', 'case_type', ...]
  - outputs: ['case_folder', ...]
  - uuid: 'tool_create_case' | ...
```

### Definition Relationships (Between Workflow Components)

| Relationship | From | To | Properties | Purpose |
|--------------|------|-----|-----------|---------|
| **HAS_LANDMARK** | Phase | Landmark | {order: 1} | Phase contains landmarks |
| **HAS_SUBPHASE** | Phase | SubPhase | {order: 1} | Litigation has sub-phases |
| **HAS_LANDMARK** | SubPhase | Landmark | {order: 1} | Sub-phase landmarks |
| **NEXT_PHASE** | Phase | Phase | {} | Phase progression |
| **HAS_WORKFLOW** | Phase | WorkflowDef | {} | Phase's workflows |
| **HAS_WORKFLOW** | SubPhase | WorkflowDef | {} | Sub-phase's workflows |
| **ACHIEVED_BY** | Landmark | WorkflowDef | {} | Workflow completes landmark |
| **USES_SKILL** | WorkflowDef | WorkflowSkill | {} | Workflow uses skill |
| **USES_TEMPLATE** | WorkflowDef | WorkflowTemplate | {} | Workflow uses template |
| **USES_TOOL** | WorkflowDef | WorkflowTool | {} | Workflow uses tool |

### State Relationships (Per-Case, 110 cases)

| Relationship | From | To | Properties | Purpose |
|--------------|------|-----|-----------|---------|
| **IN_PHASE** | Case | Phase | {entered_at: datetime} | Current phase |
| **IN_SUBPHASE** | Case | SubPhase | {entered_at: datetime} | Current litigation sub-phase (if applicable) |
| **LANDMARK_STATUS** | Case | Landmark | {status: str, sub_steps: dict, notes: str, completed_at: datetime, updated_at: datetime} | Landmark progress |

---

## Landmark Completion Tracking - Design Decision

### **APPROVED: Option B - Separate LandmarkStatus Nodes**

```cypher
// Each case has a HAS_STATUS relationship to a LandmarkStatus node for each landmark
MATCH (c:Entity {entity_type: 'Case'})-[:HAS_STATUS]->(ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l:Entity {entity_type: 'Landmark'})

// LandmarkStatus node properties:
ls.status = 'complete' | 'incomplete' | 'in_progress' | 'not_started' | 'not_applicable'
ls.sub_steps = {
  'bi_lor_sent': true,
  'bi_claim_acknowledged': true,
  'bi_coverage_confirmed': false,  // Still waiting
  'pip_application_sent': true,
  ...
}
ls.notes = 'Waiting on coverage limits from State Farm'
ls.completed_at = '2025-12-15T10:30:00Z'
ls.updated_at = '2025-12-20T14:22:00Z'
ls.updated_by = 'agent' | 'user' | 'system'
ls.version = 1  // Increment on each update for audit trail
```

**Pros:**
- ✅ Cleaner separation of concerns
- ✅ Versioning support (can keep historical status nodes)
- ✅ Audit trail (who updated, when, version number)
- ✅ Can add status-specific metadata without bloating Case or Landmark
- ✅ Two-hop traversal is trivial in graph databases

**Cons:**
- Requires updating queries in graph_state_computer.py (acceptable - we're updating anyway)
- More nodes (~7,480 LandmarkStatus nodes for 110 cases × 68 landmarks)

**DECISION: Use Option B (LandmarkStatus nodes) per user preference**

**Schema:**
```
entity_type: 'LandmarkStatus'
group_id: 'roscoe_graph'  // NOT __workflow_definitions__ (this is case-specific state)
Properties:
  - case_name: str (denormalized for easier queries)
  - landmark_id: str (denormalized for easier queries)
  - status: 'complete' | 'incomplete' | 'in_progress' | 'not_started' | 'not_applicable'
  - sub_steps: dict (for composite landmarks)
  - notes: str
  - completed_at: datetime
  - created_at: datetime
  - updated_at: datetime
  - updated_by: 'agent' | 'user' | 'system'
  - version: int
  - uuid: f'status_{case_name}_{landmark_id}'
```

**Query Example:**
```cypher
// Get all landmark statuses for a case
MATCH (c:Entity {entity_type: 'Case', name: 'Caryn-McCay-MVA-7-30-2023'})-[:HAS_STATUS]->(ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l:Entity {entity_type: 'Landmark'})
WHERE l.phase = 'onboarding'
RETURN l.landmark_id, l.name, ls.status, ls.completed_at, ls.sub_steps, ls.version
ORDER BY l.order
```

---

## Implementation Steps

### Step 1: Fix InsuranceClaim Entity Type (30 seconds)

**Create:** `fix_claim_types.py`

```python
#!/usr/bin/env python3
"""Fix InsuranceClaim entity types to match graph_state_computer.py queries."""

import asyncio

async def fix_claim_types():
    from roscoe.core.graphiti_client import run_cypher_query

    print("=" * 70)
    print("FIXING INSURANCE CLAIM ENTITY TYPES")
    print("=" * 70)

    # Update all claim entities
    query = """
    MATCH (c:Entity)
    WHERE c.entity_type IN ['BIClaim', 'PIPClaim', 'UMClaim', 'UIMClaim', 'WCClaim']
    SET c.claim_type = c.entity_type,
        c.entity_type = 'InsuranceClaim'
    RETURN c.claim_type as claim_type, count(*) as count
    """

    results = await run_cypher_query(query, {})

    print("\nUpdated claim entities:")
    total = 0
    for r in results:
        count = r['count']
        total += count
        print(f"  {r['claim_type']}: {count}")

    print(f"\nTotal claims updated: {total}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(fix_claim_types())
```

**Run:**
```bash
sudo docker exec roscoe-agents python -m roscoe.scripts.fix_claim_types
```

**Expected Output:**
```
Updated claim entities:
  BIClaim: 119
  PIPClaim: 120
  UMClaim: 14
  UIMClaim: 2
  WCClaim: 5

Total claims updated: 260
```

**Verify:**
```cypher
MATCH (c:Entity {entity_type: 'InsuranceClaim'})
RETURN c.claim_type, count(*) as count
ORDER BY count DESC
```

---

### Step 2: Load Workflow Definitions (2-3 minutes)

**Enhance Existing:** `ingest_workflow_definitions.py`

**Changes Needed:**

1. **Add SubPhase Support:**
```python
async def create_subphase_nodes(graph, phase_folder: Path, phase_name: str, dry_run: bool):
    """Create SubPhase nodes for phase_7_litigation/subphases/."""
    subphases_dir = phase_folder / 'subphases'
    if not subphases_dir.exists():
        return

    for subphase_folder in sorted(subphases_dir.iterdir()):
        if not subphase_folder.is_dir():
            continue

        # Parse folder name: 7_1_complaint → (1, 'complaint')
        match = re.match(r'7_(\d+)_(\w+)', subphase_folder.name)
        if not match:
            continue

        order = int(match.group(1))
        name = match.group(2)

        node_props = {
            'name': name,
            'display_name': name.replace('_', ' ').title(),
            'parent_phase': phase_name,
            'order': order,
            'entity_type': 'SubPhase',
            'group_id': WORKFLOW_GROUP_ID,
            'uuid': f'subphase_{phase_name}_{name}'
        }

        if not dry_run:
            # Create SubPhase node
            query = "MERGE (sp:Entity {uuid: $uuid}) SET sp += $props"
            execute_cypher(graph, query, {"uuid": node_props['uuid'], "props": node_props})

            # Link to parent Phase
            query = """
            MATCH (sp:Entity {uuid: $sp_uuid})
            MATCH (p:Entity {uuid: $phase_uuid})
            MERGE (p)-[:HAS_SUBPHASE {order: $order}]->(sp)
            """
            execute_cypher(graph, query, {
                "sp_uuid": node_props['uuid'],
                "phase_uuid": f'phase_{phase_name}',
                "order": order
            })

            logger.info(f"  Created SubPhase: {name}")

        # Parse landmarks.md for this subphase
        landmarks_file = subphase_folder / 'landmarks.md'
        if landmarks_file.exists():
            content = landmarks_file.read_text()
            landmarks = parse_landmarks_md(content)

            for lm in landmarks:
                # Create landmark linked to SubPhase
                # ... (similar to phase landmark creation)
```

2. **Parse Workflow-to-Resource Links from Actual Folders:**

Instead of just using manifests, scan actual workflow folders:
```python
async def link_workflow_resources(graph, workflow_folder: Path, workflow_uuid: str):
    """Link workflow to its actual skills/templates/tools."""

    # Scan skills/ subfolder
    skills_dir = workflow_folder / 'skills'
    if skills_dir.exists():
        for skill_folder in skills_dir.iterdir():
            if skill_folder.is_dir():
                skill_name = skill_folder.name
                # Link to WorkflowSkill node
                query = """
                MATCH (w:Entity {uuid: $wf_uuid})
                MATCH (s:Entity {entity_type: 'WorkflowSkill'})
                WHERE s.name = $skill_name OR s.uuid = $skill_uuid
                MERGE (w)-[:USES_SKILL]->(s)
                """
                execute_cypher(graph, query, {
                    "wf_uuid": workflow_uuid,
                    "skill_name": skill_name,
                    "skill_uuid": f"skill_{skill_name}"
                })

    # Scan templates/ subfolder
    templates_dir = workflow_folder / 'templates'
    if templates_dir.exists():
        for template_file in templates_dir.iterdir():
            if template_file.is_file():
                template_name = template_file.stem
                # Link to WorkflowTemplate node
                # ...

    # Scan tools/ subfolder
    tools_dir = workflow_folder / 'tools'
    if tools_dir.exists():
        for tool_file in tools_dir.glob('*.py'):
            tool_name = tool_file.stem
            # Link to WorkflowTool node
            # ...
```

**Data Sources (in order):**

**A. JSON Schemas:**
1. `/mnt/workspace/workflow_engine/schemas/phase_definitions.json`
2. `/mnt/workspace/workflow_engine/schemas/workflow_definitions.json`

**B. Markdown Files (parse):**
3. `/mnt/workspace/workflows/phase_*/landmarks.md` (9 files)
4. `/mnt/workspace/workflows/phase_7_litigation/subphases/*/landmarks.md` (5 files)
5. `/mnt/workspace/workflows/phase_*/workflows/*/workflow.md` (~25 files)
6. `/mnt/workspace/workflows/phase_7_litigation/subphases/*/workflows/*/workflow.md` (~10 files)

**C. Manifest Files:**
7. `/mnt/workspace/workflows/skills/skills_manifest.json`
8. `/mnt/workspace/workflows/templates/templates_manifest.json`
9. `/mnt/workspace/workflows/tools/tools_manifest.json`

**D. Actual Folder Structure (verification):**
10. Scan workflow folders for actual skills/templates/tools present

**Creates:**
- 9 Phase nodes
- 5 SubPhase nodes
- ~68 Landmark nodes
- ~35 WorkflowDef nodes
- 47 WorkflowSkill nodes
- ~50 WorkflowTemplate nodes
- 10 WorkflowTool nodes
- All definition relationships

**Run:**
```bash
sudo docker exec roscoe-agents python -m roscoe.scripts.ingest_workflow_definitions --workspace /mnt/workspace
```

---

### Step 3: Initialize Case Workflow States (3-5 minutes)

**Create:** `initialize_case_states.py`

```python
#!/usr/bin/env python3
"""Initialize workflow state for all cases."""

import asyncio
from datetime import datetime

async def determine_initial_phase(case_name: str, case_data: dict) -> str:
    """Determine intelligent starting phase based on case data."""

    # Check for phase indicators (in order of advancement)
    if case_data.get('settlement_date'):
        return 'closed'  # Phase 8
    elif case_data.get('settlement_check_received'):
        return 'lien'  # Phase 6
    elif case_data.get('settlement_amount'):
        return 'settlement'  # Phase 5
    elif case_data.get('demand_sent_date'):
        return 'negotiation'  # Phase 4
    elif case_data.get('treatment_complete') or case_data.get('mmi_date'):
        return 'demand'  # Phase 3
    elif case_data.get('treatment_started'):
        return 'treatment'  # Phase 2
    elif case_data.get('retainer_signed_date') or case_data.get('client_signed_date'):
        return 'file_setup'  # Phase 1
    else:
        return 'onboarding'  # Phase 0 (default)

async def initialize_case_state(case_name: str):
    """Initialize workflow state for a single case."""
    from roscoe.core.graphiti_client import run_cypher_query

    # Get case data to determine initial phase
    case_query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})
    RETURN c.name, c.accident_date, c.status, c.phase
    """
    case_results = await run_cypher_query(case_query, {"case_name": case_name})
    case_data = case_results[0] if case_results else {}

    # Determine initial phase
    initial_phase = await determine_initial_phase(case_name, case_data)
    now = datetime.now().isoformat()

    # Set IN_PHASE
    phase_query = """
    MATCH (case:Entity {entity_type: 'Case', name: $case_name})
    MATCH (phase:Entity {entity_type: 'Phase', name: $phase_name})
    MERGE (case)-[r:IN_PHASE]->(phase)
    SET r.entered_at = $now
    """
    await run_cypher_query(phase_query, {
        "case_name": case_name,
        "phase_name": initial_phase,
        "now": now
    })

    # Create LANDMARK_STATUS for ALL landmarks
    landmarks_query = """
    MATCH (case:Entity {entity_type: 'Case', name: $case_name})
    MATCH (l:Entity {entity_type: 'Landmark'})
    WHERE l.group_id = '__workflow_definitions__'
    MERGE (case)-[r:LANDMARK_STATUS]->(l)
    SET r.status = 'not_started',
        r.created_at = $now,
        r.updated_at = $now
    """
    await run_cypher_query(landmarks_query, {"case_name": case_name, "now": now})

    return initial_phase

async def initialize_all_cases():
    """Initialize workflow state for all cases."""
    from roscoe.core.graphiti_client import run_cypher_query

    print("=" * 70)
    print("INITIALIZING CASE WORKFLOW STATES")
    print("=" * 70)

    # Get all cases
    cases_query = "MATCH (c:Entity {entity_type: 'Case'}) RETURN c.name as name ORDER BY c.name"
    cases = await run_cypher_query(cases_query, {})

    print(f"\nInitializing {len(cases)} cases...")

    phase_distribution = {}

    for i, case in enumerate(cases, 1):
        case_name = case['name']
        initial_phase = await initialize_case_state(case_name)

        phase_distribution[initial_phase] = phase_distribution.get(initial_phase, 0) + 1

        if i % 10 == 0:
            print(f"  Progress: {i}/{len(cases)} cases initialized...")

    print("\n" + "=" * 70)
    print("INITIALIZATION COMPLETE")
    print("=" * 70)
    print(f"Total cases: {len(cases)}")
    print("\nPhase distribution:")
    for phase, count in sorted(phase_distribution.items()):
        print(f"  {phase}: {count}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(initialize_all_cases())
```

**Run:**
```bash
sudo docker exec roscoe-agents python -m roscoe.scripts.initialize_case_states
```

**Expected:**
- 110 IN_PHASE relationships
- ~7,480 LANDMARK_STATUS relationships (110 cases × 68 landmarks)

---

## Sub-Phases Implementation

### Graph Structure

```
Phase:litigation (order=7)
  ├─[HAS_SUBPHASE {order: 1}]→ SubPhase:complaint
  │   ├─[HAS_LANDMARK]→ Landmark:complaint_drafted
  │   ├─[HAS_LANDMARK]→ Landmark:complaint_filed
  │   ├─[HAS_LANDMARK]→ Landmark:summons_issued
  │   ├─[HAS_LANDMARK]→ Landmark:defendant_served
  │   ├─[HAS_LANDMARK]→ Landmark:answer_received_or_default_sought
  │   ├─[HAS_LANDMARK]→ Landmark:all_defendants_resolved
  │   ├─[HAS_WORKFLOW]→ WorkflowDef:draft_file_complaint
  │   ├─[HAS_WORKFLOW]→ WorkflowDef:prepare_filing_package
  │   └─[HAS_WORKFLOW]→ WorkflowDef:serve_defendant
  │
  ├─[HAS_SUBPHASE {order: 2}]→ SubPhase:answer_discovery
  │   ├─[HAS_LANDMARK]→ Landmark:our_discovery_propounded
  │   ├─[HAS_LANDMARK]→ Landmark:defendant_responses_received
  │   ├─[HAS_LANDMARK]→ Landmark:our_responses_served
  │   ├─[HAS_LANDMARK]→ Landmark:client_deposition_complete
  │   ├─[HAS_LANDMARK]→ Landmark:defendant_deposition_complete
  │   ├─[HAS_LANDMARK]→ Landmark:discovery_cutoff_passed
  │   ├─[HAS_WORKFLOW]→ WorkflowDef:answer_response
  │   └─[HAS_WORKFLOW]→ WorkflowDef:initial_discovery
  │
  ├─[HAS_SUBPHASE {order: 3}]→ SubPhase:depositions
  ├─[HAS_SUBPHASE {order: 4}]→ SubPhase:mediation
  └─[HAS_SUBPHASE {order: 5}]→ SubPhase:trial
```

### Case State for Litigation

```cypher
// Case in litigation
Case:Caryn-McCay-MVA-7-30-2023
  ├─[IN_PHASE {entered_at: '2025-01-15'}]→ Phase:litigation
  └─[IN_SUBPHASE {entered_at: '2025-02-01'}]→ SubPhase:depositions
```

### State Computer Queries (Updates Needed)

**Current** (line 1946):
```cypher
MATCH (c:Entity {entity_type: 'Case'})-[r:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
```

**Enhanced** (for litigation cases):
```cypher
MATCH (c:Entity {entity_type: 'Case'})-[r:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
OPTIONAL MATCH (c)-[sr:IN_SUBPHASE]->(sp:Entity {entity_type: 'SubPhase'})
RETURN p.name, p.display_name, p.track,
       sp.name as subphase_name, sp.display_name as subphase_display
```

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
// Landmark: ~68
// WorkflowDef: ~35
// WorkflowSkill: 47
// WorkflowTemplate: ~50
// WorkflowTool: 10
// SubPhase: 5
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
// lien (6) → closed (8)
// litigation (7) → settlement (5)
```

### Check SubPhase Chain

```cypher
// Verify litigation sub-phases
MATCH (p:Entity {entity_type: 'Phase', name: 'litigation'})-[:HAS_SUBPHASE]->(sp:Entity)
RETURN sp.name, sp.order
ORDER BY sp.order

// Expected:
// complaint (1)
// answer_discovery (2)
// depositions (3)
// mediation (4)
// trial (5)
```

### Check Landmark-to-Phase Links

```cypher
// Verify landmarks linked to phases
MATCH (p:Entity {entity_type: 'Phase'})-[:HAS_LANDMARK]->(l:Entity {entity_type: 'Landmark'})
WHERE l.subphase IS NULL
RETURN p.name as phase, count(l) as landmark_count
ORDER BY p.order

// Expected:
// onboarding: 3
// file_setup: 4
// treatment: 9
// demand: 12
// negotiation: 10
// settlement: 11
// lien: 7
// litigation: 6 (phase-level only, not sub-phase)
// closed: 6
```

### Check SubPhase Landmarks

```cypher
// Verify sub-phase landmarks
MATCH (sp:Entity {entity_type: 'SubPhase'})-[:HAS_LANDMARK]->(l:Entity)
RETURN sp.name as subphase, count(l) as landmark_count
ORDER BY sp.order

// Expected:
// complaint: 6
// answer_discovery: 6
// depositions: ~6
// mediation: 4
// trial: 6
```

### Test Case State Query

```cypher
// Check a specific case's workflow state
MATCH (c:Entity {entity_type: 'Case', name: 'Caryn-McCay-MVA-7-30-2023'})-[r:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
OPTIONAL MATCH (c)-[sr:IN_SUBPHASE]->(sp:Entity {entity_type: 'SubPhase'})
RETURN c.name as case_name,
       p.name as current_phase,
       p.display_name,
       sp.name as subphase,
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
// This should work after Step 1
MATCH (case:Entity {entity_type: 'Case', name: 'Caryn-McCay-MVA-7-30-2023'})-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})
OPTIONAL MATCH (claim)-[:INSURED_BY]->(insurer:Entity {entity_type: 'Insurer'})
OPTIONAL MATCH (claim)-[:ASSIGNED_ADJUSTER]->(adjuster:Entity {entity_type: 'Adjuster'})
RETURN claim.claim_type,
       claim.claim_number,
       insurer.name,
       adjuster.name
```

---

## Files to Create/Modify

### New Files

1. **fix_claim_types.py** (Simple, 30 lines)
   - Update claim entity_type to 'InsuranceClaim'
   - Preserve specific type in claim_type attribute

2. **initialize_case_states.py** (Moderate, 150 lines)
   - Set IN_PHASE for each case (intelligent detection)
   - Create LANDMARK_STATUS relationships
   - Optional: Infer completion statuses

### Files to Modify

3. **ingest_workflow_definitions.py** (Enhancements, +200 lines)
   - Add SubPhase node creation
   - Parse litigation subphase folders
   - Link workflows to actual skills/templates/tools from folder structure
   - Enhanced landmark parsing for composite landmarks (sub_steps)

### Optional Enhancements

4. **graph_state_computer.py** (+50 lines)
   - Add SubPhase support to _get_case_info()
   - Update DerivedWorkflowState dataclass for subphase fields
   - Update format_for_prompt() to show subphase

---

## Timeline

| Step | Task | Time | Cumulative |
|------|------|------|------------|
| 1 | Create fix_claim_types.py | 5 min | 5 min |
| 2 | Run fix_claim_types.py | 30 sec | 6 min |
| 3 | Enhance ingest_workflow_definitions.py | 20 min | 26 min |
| 4 | Run enhanced ingest script | 3 min | 29 min |
| 5 | Create initialize_case_states.py | 15 min | 44 min |
| 6 | Run initialization script | 5 min | 49 min |
| 7 | Verify with test queries | 5 min | 54 min |
| 8 | (Optional) Enhance graph_state_computer.py | 10 min | 64 min |

**Total: ~50-60 minutes coding + execution**

---

## Expected Graph Size After Completion

### Nodes

| Type | Count | Purpose |
|------|-------|---------|
| **Case Data (existing)** | | |
| Case | 110 | Case entities |
| Client | 105 | Client entities |
| MedicalProvider | 771 | Provider entities |
| InsuranceClaim | 260 | Claim entities (fixed type) |
| Insurer | 99 | Insurance companies |
| Adjuster | 148 | Adjusters |
| Lien | 103 | Lien entities |
| LienHolder | 50 | Lien holders |
| Other entities | ~308 | Attorneys, Pleadings, Courts, etc. |
| **Workflow Definitions (new)** | | |
| Phase | 9 | Case lifecycle phases |
| SubPhase | 5 | Litigation sub-phases |
| Landmark | ~68 | Checkpoints |
| WorkflowDef | ~35 | Workflow definitions |
| WorkflowSkill | 47 | Skill references |
| WorkflowTemplate | ~50 | Template references |
| WorkflowTool | 10 | Tool references |
| **TOTAL** | **~2,178 nodes** | |

### Relationships

| Type | Count | Purpose |
|------|-------|---------|
| **Case Data (existing)** | | |
| HAS_CLIENT | 106 | Case → Client |
| TREATING_AT | 573 | Case → Provider |
| HAS_CLAIM | 260 | Case → Claim |
| INSURED_BY | 254 | Claim → Insurer |
| ASSIGNED_ADJUSTER | 212 | Claim → Adjuster |
| HAS_LIEN | 103 | Case → Lien |
| Other relationships | ~909 | Various |
| **Workflow Definitions (new)** | | |
| HAS_LANDMARK | ~68 | Phase/SubPhase → Landmark |
| HAS_SUBPHASE | 5 | Phase → SubPhase |
| NEXT_PHASE | 8 | Phase → Phase |
| HAS_WORKFLOW | ~35 | Phase/SubPhase → WorkflowDef |
| ACHIEVED_BY | ~50 | Landmark → WorkflowDef |
| USES_SKILL | ~80 | WorkflowDef → Skill |
| USES_TEMPLATE | ~60 | WorkflowDef → Template |
| USES_TOOL | ~40 | WorkflowDef → Tool |
| **Workflow State (new)** | | |
| IN_PHASE | 110 | Case → Phase |
| IN_SUBPHASE | ~15 | Case → SubPhase (litigation cases) |
| LANDMARK_STATUS | ~7,480 | Case → Landmark (110 × 68) |
| **TOTAL** | **~10,368 relationships** | |

---

## Open Questions for User

### 1. Intelligent Phase Detection

**Question:** Should all 110 cases start at Phase 0 (onboarding), or intelligently determine phase based on existing data?

**Options:**
- **A) All start at onboarding** - Simple, but inaccurate for cases already in progress
- **B) Intelligent detection** - Use indicators like demand_sent_date, treatment_complete, etc.

**Recommendation:** B (intelligent detection)

### 2. Landmark Status Inference

**Question:** For cases initialized beyond Phase 0, should we mark earlier phase landmarks as 'complete'?

**Example:** If case starts at 'negotiation':
- Mark all onboarding landmarks: complete
- Mark all file_setup landmarks: complete
- Mark all treatment landmarks: complete
- Mark all demand landmarks: complete
- Mark negotiation landmarks: not_started

**Options:**
- **A) All landmarks start as 'not_started'** - Conservative, but causes false blockers
- **B) Infer completion for passed phases** - Smart, but assumes prior work done

**Recommendation:** B (infer completion) - prevents "missing retainer" errors for cases in negotiation

### 3. Sub-Phase Support in graph_state_computer.py

**Question:** Should we add SubPhase awareness to graph_state_computer.py now or later?

**Options:**
- **A) Now** - Complete implementation from start
- **B) Later** - Get basic system working, add sub-phase later

**Recommendation:** A (now) - avoid having to refactor later

### 4. Workflow-to-Resource Linking

**Question:** How to link WorkflowDef → Skills/Templates/Tools?

**Options:**
- **A) From manifests only** - Fast but may miss embedded resources
- **B) Scan actual folder structure** - Accurate but slower
- **C) Parse workflow.md YAML frontmatter** - Most accurate

**Recommendation:** C + B (parse YAML, verify files exist)

---

## After Workflow System is Working

**Then Discuss:**
1. Episode notes ingestion (adds unstructured Graphiti layer on top of structured data)
2. Workflow middleware testing
3. Agent integration testing
4. Whether to keep OpenAI or try Gemini again with proper config

---

## Summary

**Current State:**
- ✅ 1,954 structured entities loaded (Cases, Clients, Providers, Claims, etc.)
- ✅ 2,417 structured relationships loaded
- ❌ NO workflow definition nodes
- ❌ NO workflow state relationships

**After Execution:**
- ✅ All workflow definitions loaded from actual /workflows/ directory
- ✅ All 110 cases have workflow state (IN_PHASE, LANDMARK_STATUS)
- ✅ Sub-phase support for litigation
- ✅ graph_state_computer.py works end-to-end
- ✅ WorkflowMiddleware can inject phase-specific guidance
