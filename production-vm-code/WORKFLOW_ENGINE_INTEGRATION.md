# Workflow Engine Integration

This document describes the integration of the Roscoe Runtime StateMachine into the production codebase.

## Overview

The monolithic `workflow_state_computer.py` (909 lines of ad-hoc logic) has been replaced with:
- A vendored `workflow_engine/` package from `Roscoe_runtime`
- A thin adapter in `workflow_state_computer.py` that delegates to the StateMachine
- A `CaseStateStore` for strict state file management

## Architecture

```
case_context_middleware.py
    │
    ├── compute_workflow_state(project_name)
    │
    └── workflow_state_computer.py (thin adapter)
            │
            ├── CaseStateStore.load() [strict mode]
            │
            ├── StateMachine.get_case_status()
            │   ├── sync_workflows_with_data() [self-healing]
            │   ├── validate_litigation_state()
            │   └── suggest_phase_change()
            │
            └── StateMachine.format_status_for_agent()
```

## Files Created/Modified

### New Files in `src/roscoe/workflow_engine/`
- `__init__.py` - Package exports
- `orchestrator/state_machine.py` - Core StateMachine class (962 lines)
- `_adapters/case_data.py` - CaseData adapter for JSON data access
- `schemas/phase_definitions.json` - Phase configuration
- `schemas/workflow_definitions.json` - Workflow steps and dependencies
- `schemas/derivation_rules.json` - Rules for data-driven status derivation
- `schemas/case_state.schema.json` - JSON schema for case_state.json
- `templates/new_case_state.json` - Template for new case states
- `scripts/migrate_case_states.py` - Migration script for existing cases

### Modified Files in `src/roscoe/core/`
- `workflow_state_computer.py` - Rewritten as thin adapter
- `case_state_store.py` - New file for state persistence

### Modified Configuration
- `pyproject.toml` - Added workflow_engine packages

## State File Location

Case state is stored at:
```
${WORKSPACE_DIR}/projects/{project_name}/Case Information/case_state.json
```

## Strict Mode

The system operates in **strict mode**:
- If `case_state.json` is missing, `CaseStateNotFoundError` is raised
- No automatic creation of state files during injection
- Run the migration script before deployment

## Migration Steps

### 1. Run Migration Script (Before Deployment)

```bash
# Dry run - see what would be created
python -m roscoe.workflow_engine.scripts.migrate_case_states --dry-run

# Actually create state files
python -m roscoe.workflow_engine.scripts.migrate_case_states

# Migrate specific case
python -m roscoe.workflow_engine.scripts.migrate_case_states --case "Smith-MVA-01-15-2024"
```

### 2. Copy Workflows Content to Workspace

The `workflow_definitions.json` references manual fallback paths like:
```
workflows/phase_0_onboarding/workflows/case_setup/workflow.md
```

These must be accessible in the workspace. Copy the workflows directory:

```bash
# From local dev
cp -r Roscoe_runtime/workflows/ /mnt/workspace/workflows/

# Or sync to GCS bucket (production)
gsutil -m rsync -r Roscoe_runtime/workflows/ gs://your-bucket/workspace/workflows/
```

### 3. Set Environment Variables

Ensure `WORKSPACE_DIR` or `WORKSPACE_ROOT` is set:

```bash
# Production VM
export WORKSPACE_DIR=/mnt/workspace

# Docker container
export WORKSPACE_DIR=/app/workspace_paralegal
```

## Key Features

### Self-Healing Workflows
The StateMachine automatically syncs workflow statuses with actual case data:
- If data shows a BI claim number exists, marks `open_bi_claim` as complete
- If medical records received date exists, updates `request_records_bills`
- Corrections are logged to `audit_log` in case_state.json

### User-Approval Gated Phase Transitions
Phase changes are not automatic:
- `suggest_phase_change()` detects when criteria are met
- Creates `pending_phase_change` in case state
- User must call `approve_phase_change()` to advance

### Litigation Subphase Support
Phase 7 (Litigation) uses nested subphases:
- `phase_7_1_complaint`
- `phase_7_2_discovery`
- `phase_7_3_mediation`
- `phase_7_4_trial_prep`
- `phase_7_5_trial`

### SOL Tracking with Complaint Awareness
- SOL status is "fulfilled" once complaint is filed
- Integrates with `litigation.json` data

## Testing

### Check if state exists
```bash
python -m roscoe.core.workflow_state_computer --case "Smith-MVA-01-15-2024" --check
```

### Get formatted status
```bash
python -m roscoe.core.workflow_state_computer --case "Smith-MVA-01-15-2024"
```

### Get JSON output
```bash
python -m roscoe.core.workflow_state_computer --case "Smith-MVA-01-15-2024" --json --pretty
```

## Backward Compatibility

### Workflow ID Aliases
The StateMachine handles both old and new workflow IDs:
- `open_bi_claim` → `insurance_bi_claim`
- `open_pip_claim` → `insurance_pip_claim`
- `bi_negotiation` → `negotiate_claim`

### Middleware Interface
The `compute_workflow_state()` function returns a `WorkflowStateResult` dataclass with:
- `formatted_status` - Markdown string for agent prompt
- `current_phase` - Phase identifier
- `phase_progress` - Percentage complete
- All other fields for compatibility

## Local Dev Parity

To maintain parity with `local-dev-code/`, copy the same changes:
1. Copy `workflow_engine/` directory
2. Update `workflow_state_computer.py`
3. Add `case_state_store.py`
4. Update `pyproject.toml` (if exists)
