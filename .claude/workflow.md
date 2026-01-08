# Workflow Engine

## Overview

Graph-based state machine for PI case lifecycle. State stored explicitly in FalkorDB.

## Phases

Onboarding → Intake → Pre-Lit → Litigation → Settlement → Closed

## Graph Storage

```cypher
(Case)-[:IN_PHASE]->(Phase)
(Case)-[:HAS_STATUS]->(LandmarkStatus {status: 'complete', updated_at: timestamp})
(LandmarkStatus)-[:FOR_LANDMARK]->(Landmark)
```

## Agent Tools

```python
# Get workflow status
get_case_workflow_status(case_name="Wilson-MVA-2024")

# Update landmark
update_landmark(
    case_name="Wilson-MVA-2024",
    landmark_id="retainer_signed",
    status="complete",
    notes="Signed via DocuSign 2024-12-01"
)

# Advance phase
advance_phase(case_name="Wilson-MVA-2024")

# Recalculate readiness
recalculate_case_phase(case_name="Wilson-MVA-2024")
```

## Phase Progression

| Phase | Entry Criteria | Hard Blockers |
|-------|---------------|---------------|
| Onboarding | Case created | None |
| Intake | Client contacted | Missing retainer |
| Pre-Litigation | Retainer signed | MMI not reached |
| Litigation | Demand rejected OR SOL approaching | Complaint not filed |
| Settlement | Negotiation active | Authorization missing |
| Closed | Settlement paid OR dismissed | N/A |

## Modules

| Module | Purpose |
|--------|---------|
| `graph_state_computer.py` | Computes state from graph |
| `workflow_middleware.py` | Injects guidance into prompts |
