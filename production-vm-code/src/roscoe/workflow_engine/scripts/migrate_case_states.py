#!/usr/bin/env python3
"""
Case State Migration Script

Creates case_state.json files for existing cases that don't have them.
Run this script BEFORE deploying the new workflow engine to ensure
all cases have valid state files.

Usage:
    # Dry run - show what would be created
    python -m roscoe.workflow_engine.scripts.migrate_case_states --dry-run
    
    # Actually create files
    python -m roscoe.workflow_engine.scripts.migrate_case_states
    
    # Migrate specific case
    python -m roscoe.workflow_engine.scripts.migrate_case_states --case "Smith-MVA-01-15-2024"
    
    # Custom workspace directory
    python -m roscoe.workflow_engine.scripts.migrate_case_states --workspace /mnt/workspace
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent paths for imports when running as script
script_dir = Path(__file__).parent
if str(script_dir.parent.parent.parent) not in sys.path:
    sys.path.insert(0, str(script_dir.parent.parent.parent))

from roscoe.workflow_engine.orchestrator.state_machine import StateMachine
from roscoe.workflow_engine._adapters.case_data import CaseData, get_workspace_path, get_database_path


def get_all_projects(workspace_path: Path) -> List[str]:
    """
    Get all project names from the Database/case_overview.json file.
    
    Args:
        workspace_path: Path to workspace root
    
    Returns:
        List of project names
    """
    case_overview_path = workspace_path / "Database" / "case_overview.json"
    
    if not case_overview_path.exists():
        print(f"Warning: case_overview.json not found at {case_overview_path}")
        return []
    
    try:
        with open(case_overview_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle jsonb_agg wrapper
        if isinstance(data, list) and len(data) > 0:
            first = data[0]
            if isinstance(first, dict) and "jsonb_agg" in first:
                data = first["jsonb_agg"] or []
        
        projects = []
        for record in data:
            project_name = record.get("project_name")
            if project_name:
                projects.append(project_name)
        
        return sorted(set(projects))
    
    except Exception as e:
        print(f"Error reading case_overview.json: {e}")
        return []


def infer_accident_type(project_name: str) -> str:
    """
    Infer accident type from project name.
    
    Args:
        project_name: Case/project name
    
    Returns:
        Accident type string ("mva", "premises", etc.)
    """
    name_lower = project_name.lower()
    
    if "mva" in name_lower or "auto" in name_lower or "car" in name_lower:
        return "mva"
    elif "premise" in name_lower or "slip" in name_lower or "fall" in name_lower:
        return "premises"
    elif "wc" in name_lower or "workers" in name_lower or "comp" in name_lower:
        return "workers_comp"
    elif "dog" in name_lower or "bite" in name_lower:
        return "dog_bite"
    elif "product" in name_lower:
        return "product"
    elif "med" in name_lower and "mal" in name_lower:
        return "medical_malpractice"
    else:
        return "mva"  # Default


def create_case_state(
    project_name: str,
    case_data: CaseData,
    state_machine: StateMachine
) -> Dict[str, Any]:
    """
    Create a new case_state.json from existing case data.
    
    Args:
        project_name: Case/project name
        case_data: CaseData adapter instance
        state_machine: StateMachine instance
    
    Returns:
        New case state dictionary
    """
    overview = case_data.overview
    
    # Get basic info
    client_name = overview.get("client_full_name", overview.get("client_name", project_name))
    accident_date = overview.get("accident_date", overview.get("date_of_accident", ""))
    accident_type = infer_accident_type(project_name)
    
    # If no accident date, use a default (required field)
    if not accident_date:
        accident_date = datetime.now().strftime("%Y-%m-%d")
        print(f"  Warning: No accident date found, using today's date")
    
    # Create base state using StateMachine
    case_state = state_machine.create_new_case(
        case_id=project_name,
        client_name=client_name,
        accident_date=accident_date,
        accident_type=accident_type
    )
    
    # Determine current phase from existing data
    current_phase = derive_phase_from_data(case_data, overview)
    if current_phase:
        case_state["current_phase"] = current_phase
        # Initialize phase state
        now = datetime.now().isoformat()
        if current_phase not in case_state["phases"]:
            case_state["phases"][current_phase] = {
                "status": "in_progress",
                "entered_at": now,
                "workflows": {},
                "exit_criteria": {}
            }
    
    # Run data sync to populate workflow statuses
    corrections = state_machine.sync_workflows_with_data(case_state, case_data)
    if corrections:
        print(f"  Auto-completed {len(corrections)} workflow(s) from existing data")
    
    # Handle litigation if applicable
    if current_phase == "phase_7_litigation":
        litigation_data = state_machine.load_litigation_data(project_name)
        if litigation_data:
            lit_corrections = state_machine.validate_litigation_state(case_state, litigation_data)
            if lit_corrections:
                print(f"  Synced {len(lit_corrections)} litigation workflow(s)")
    
    return case_state


def derive_phase_from_data(case_data: CaseData, overview: Dict) -> str:
    """
    Derive current phase from case data.
    
    Args:
        case_data: CaseData adapter instance
        overview: Case overview dict
    
    Returns:
        Phase ID string
    """
    # Check explicit phase in overview
    explicit_phase = overview.get("phase", "").lower().replace(" ", "_")
    
    phase_map = {
        "file_setup": "phase_1_file_setup",
        "treatment": "phase_2_treatment",
        "demand_in_progress": "phase_3_demand",
        "demand": "phase_3_demand",
        "negotiation": "phase_4_negotiation",
        "settlement": "phase_5_settlement",
        "lien": "phase_6_lien",
        "litigation": "phase_7_litigation",
        "closed": "phase_8_closed"
    }
    
    if explicit_phase in phase_map:
        return phase_map[explicit_phase]
    
    # Derive from data
    bi_claims = case_data.bi_claims
    providers = case_data.medical_providers
    
    # Check for settlement
    for claim in case_data.insurance_claims:
        if claim.get("settlement_amount"):
            return "phase_5_settlement"
    
    # Check for active negotiation
    for claim in bi_claims:
        if claim.get("current_offer") or claim.get("is_active_negotiation"):
            return "phase_4_negotiation"
    
    # Check for demand sent
    for claim in bi_claims:
        if claim.get("date_demand_sent"):
            return "phase_4_negotiation"
    
    # Check if all providers complete (ready for demand)
    if providers:
        all_complete = all(p.get("date_treatment_completed") for p in providers)
        all_records = all(p.get("date_medical_records_received") for p in providers)
        if all_complete and all_records:
            return "phase_3_demand"
    
    # Check for active treatment
    if providers:
        return "phase_2_treatment"
    
    # Check for insurance claims opened
    if case_data.insurance_claims:
        return "phase_1_file_setup"
    
    return "phase_0_onboarding"


def migrate_case(
    project_name: str,
    workspace_path: Path,
    state_machine: StateMachine,
    dry_run: bool = False,
    force: bool = False
) -> bool:
    """
    Migrate a single case to have case_state.json.
    
    Args:
        project_name: Case/project name
        workspace_path: Path to workspace root
        state_machine: StateMachine instance
        dry_run: If True, don't actually write files
        force: If True, overwrite existing state files
    
    Returns:
        True if migration was performed (or would be in dry run)
    """
    state_path = workspace_path / "projects" / project_name / "Case Information" / "case_state.json"
    
    # Check if already exists
    if state_path.exists() and not force:
        print(f"  Skipping: case_state.json already exists")
        return False
    
    # Load case data
    try:
        case_data = CaseData(project_name)
    except Exception as e:
        print(f"  Error loading case data: {e}")
        return False
    
    # Create state
    case_state = create_case_state(project_name, case_data, state_machine)
    
    if dry_run:
        print(f"  Would create: {state_path}")
        print(f"  Phase: {case_state.get('current_phase')}")
        return True
    
    # Ensure directory exists
    state_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(case_state, f, indent=2, ensure_ascii=False)
    
    print(f"  Created: {state_path}")
    print(f"  Phase: {case_state.get('current_phase')}")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate existing cases to have case_state.json files"
    )
    parser.add_argument(
        "--workspace", "-w",
        type=str,
        help="Workspace directory (defaults to WORKSPACE_DIR env var)"
    )
    parser.add_argument(
        "--case", "-c",
        type=str,
        help="Migrate a specific case only"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing case_state.json files"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Determine workspace
    if args.workspace:
        workspace_path = Path(args.workspace)
        os.environ["WORKSPACE_DIR"] = str(workspace_path)
    else:
        workspace_path = get_workspace_path()
    
    print(f"Workspace: {workspace_path}")
    
    if not workspace_path.exists():
        print(f"Error: Workspace not found at {workspace_path}")
        sys.exit(1)
    
    # Initialize StateMachine
    schemas_dir = Path(__file__).parent.parent / "schemas"
    if not schemas_dir.exists():
        print(f"Error: Schemas not found at {schemas_dir}")
        sys.exit(1)
    
    state_machine = StateMachine(schemas_dir=schemas_dir)
    print(f"Schemas: {schemas_dir}")
    
    if args.dry_run:
        print("\n=== DRY RUN - No changes will be made ===\n")
    
    # Get cases to migrate
    if args.case:
        projects = [args.case]
    else:
        projects = get_all_projects(workspace_path)
    
    if not projects:
        print("No projects found to migrate")
        sys.exit(0)
    
    print(f"\nFound {len(projects)} project(s) to process\n")
    
    # Process each case
    migrated = 0
    skipped = 0
    errors = 0
    
    for project_name in projects:
        print(f"Processing: {project_name}")
        try:
            if migrate_case(
                project_name,
                workspace_path,
                state_machine,
                dry_run=args.dry_run,
                force=args.force
            ):
                migrated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  Error: {e}")
            errors += 1
        print()
    
    # Summary
    print("=" * 50)
    print(f"Migration complete:")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped:  {skipped}")
    print(f"  Errors:   {errors}")
    
    if args.dry_run:
        print("\nThis was a dry run. Run without --dry-run to create files.")


if __name__ == "__main__":
    main()
