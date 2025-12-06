"""
WorkflowMiddleware - Orchestrates phase-driven workflow system.

This middleware:
1. Detects the current case from CaseContextMiddleware
2. Loads workflow state for the case
3. Identifies current phase and applicable workflows
4. Generates proactive suggestions
5. Injects workflow context into agent prompt
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any


class WorkflowMiddleware:
    """
    Middleware that provides workflow awareness to the agent.
    
    Runs after CaseContextMiddleware to use detected case context.
    Injects current phase, active workflows, and suggestions into prompt.
    """
    
    def __init__(
        self,
        workspace_dir: str,
        phases_manifest_path: str,
        workflows_manifest_path: str,
    ):
        self.workspace_dir = Path(workspace_dir)
        self.phases_manifest = self._load_json(phases_manifest_path)
        self.workflows_manifest = self._load_json(workflows_manifest_path)
        self.caselist = self._load_caselist()
        
    def _load_json(self, path: str) -> dict:
        """Load JSON file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load {path}: {e}")
            return {}
    
    def _load_caselist(self) -> dict:
        """Load the master caselist."""
        caselist_path = self.workspace_dir / "Database" / "caselist.json"
        return self._load_json(str(caselist_path))
    
    def _get_case_folder(self, project_name: str) -> Optional[Path]:
        """Get the folder path for a case."""
        cases = self.caselist.get("cases", [])
        for case in cases:
            if case.get("project_name") == project_name:
                folder = case.get("folder_path") or case.get("folder")
                if folder:
                    return self.workspace_dir / "projects" / folder
        return None
    
    def _get_current_phase(self, case_context: dict) -> Optional[dict]:
        """Get current phase info from case context."""
        phase_id = case_context.get("phase", "intake")
        phases = self.phases_manifest.get("phases", [])
        
        for phase in phases:
            if phase.get("id") == phase_id:
                return phase
        
        # Default to intake if phase not found
        for phase in phases:
            if phase.get("id") == "intake":
                return phase
        
        return None
    
    def _load_workflow_state(self, case_folder: Path) -> dict:
        """Load workflow state for a case."""
        state_path = case_folder / "workflow_state.json"
        if state_path.exists():
            return self._load_json(str(state_path))
        return {}
    
    def _is_case_initialized(self, case_folder: Path) -> bool:
        """Check if case has workflow state initialized."""
        state_path = case_folder / "workflow_state.json"
        return state_path.exists()
    
    def _get_applicable_workflows(self, phase_id: str) -> List[dict]:
        """Get all workflows for a given phase."""
        workflows = self.workflows_manifest.get("workflows", [])
        return [w for w in workflows if w.get("phase") == phase_id]
    
    def _categorize_workflows(
        self,
        workflows: List[dict],
        workflow_state: dict
    ) -> Dict[str, List[dict]]:
        """Categorize workflows into active, pending, completed."""
        state_workflows = workflow_state.get("workflows", {})
        
        result = {
            "active": [],
            "pending": [],
            "completed": []
        }
        
        for workflow in workflows:
            wf_id = workflow.get("id")
            wf_state = state_workflows.get(wf_id, {})
            status = wf_state.get("status", "pending")
            
            if status == "completed":
                result["completed"].append(workflow)
            elif status == "in_progress":
                result["active"].append(workflow)
            else:
                result["pending"].append(workflow)
        
        return result
    
    def _check_phase_exit_criteria(
        self,
        phase: dict,
        workflow_state: dict
    ) -> Dict[str, bool]:
        """Check which exit criteria are met for current phase."""
        criteria = phase.get("exit_criteria", [])
        exit_status = workflow_state.get("exit_criteria_status", {})
        
        result = {}
        for criterion in criteria:
            result[criterion] = exit_status.get(criterion, False)
        
        return result
    
    def _should_advance_phase(self, exit_criteria_status: Dict[str, bool]) -> bool:
        """Check if all exit criteria are met."""
        if not exit_criteria_status:
            return False
        return all(exit_criteria_status.values())
    
    def _generate_suggestion(
        self,
        categorized: Dict[str, List[dict]],
        exit_criteria: Dict[str, bool],
        phase: dict
    ) -> str:
        """Generate a proactive suggestion for the agent."""
        # Priority 1: Continue active workflow
        if categorized["active"]:
            active = categorized["active"][0]
            return f"Continue working on: {active['name']}"
        
        # Priority 2: Start pending workflow that contributes to unmet criteria
        unmet_criteria = [k for k, v in exit_criteria.items() if not v]
        for workflow in categorized["pending"]:
            contributes = workflow.get("contributes_to_exit", [])
            if any(c in unmet_criteria for c in contributes):
                return f"Start workflow: {workflow['name']} (addresses: {', '.join([c for c in contributes if c in unmet_criteria])})"
        
        # Priority 3: Any pending workflow
        if categorized["pending"]:
            return f"Consider starting: {categorized['pending'][0]['name']}"
        
        # Priority 4: Phase complete
        if all(exit_criteria.values()):
            next_phase = phase.get("next_phase")
            if next_phase:
                return f"All criteria met. Ready to advance to: {next_phase}"
            return "All workflows complete for this phase."
        
        return "Review case status and determine next steps."
    
    def _format_workflow_context(
        self,
        case_name: str,
        phase: dict,
        categorized: Dict[str, List[dict]],
        exit_criteria: Dict[str, bool],
        suggestion: str
    ) -> str:
        """Format workflow context for injection into prompt."""
        phase_name = phase.get("name", "Unknown")
        phase_order = phase.get("order", 0)
        exit_labels = phase.get("exit_criteria_labels", {})
        
        lines = [
            f"## 📋 Workflow Status: {case_name}",
            "",
            f"**Current Phase:** {phase_name} (Phase {phase_order} of 6)",
            ""
        ]
        
        # Active workflows
        if categorized["active"]:
            lines.append("### Active Workflows")
            for wf in categorized["active"]:
                lines.append(f"- 🔄 **{wf['name']}**: In progress")
            lines.append("")
        
        # Pending workflows
        if categorized["pending"]:
            lines.append("### Pending Workflows")
            for wf in categorized["pending"][:3]:  # Show top 3
                lines.append(f"- ⏳ **{wf['name']}**")
            if len(categorized["pending"]) > 3:
                lines.append(f"- ... and {len(categorized['pending']) - 3} more")
            lines.append("")
        
        # Exit criteria
        lines.append("### Phase Exit Criteria")
        for criterion, met in exit_criteria.items():
            label = exit_labels.get(criterion, criterion)
            icon = "✅" if met else "❌"
            lines.append(f"- {icon} {label}")
        lines.append("")
        
        # Suggestion
        lines.append(f"### 💡 Suggested Action")
        lines.append(suggestion)
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_initialization_prompt(self, case_name: str) -> str:
        """Generate prompt for uninitialized case."""
        return f"""## ⚠️ Case Not Initialized: {case_name}

This case does not have a workflow state file yet. Before proceeding, you should:

1. **For a NEW case**: Run the `case_initialization` workflow to set up the workflow state.

2. **For a TRANSFER case** (from another attorney): Run the `transfer_case_assessment` workflow to evaluate current status and set the appropriate phase.

### Suggested Action
Ask the user: "Is this a new case or a case transferred from another attorney?"

Then run the appropriate initialization workflow.
"""
    
    def get_workflow_context(
        self,
        detected_cases: List[dict]
    ) -> Optional[str]:
        """
        Get workflow context for detected cases.
        
        Args:
            detected_cases: List of case context dicts from CaseContextMiddleware
            
        Returns:
            Formatted workflow context string, or None
        """
        if not detected_cases:
            return None
        
        # Use first detected case
        case_context = detected_cases[0]
        project_name = case_context.get("project_name")
        
        if not project_name:
            return None
        
        # Get case folder
        case_folder = self._get_case_folder(project_name)
        if not case_folder or not case_folder.exists():
            return None
        
        # Check if initialized
        if not self._is_case_initialized(case_folder):
            return self._format_initialization_prompt(
                case_context.get("client_name", project_name)
            )
        
        # Load workflow state
        workflow_state = self._load_workflow_state(case_folder)
        
        # Get current phase
        phase = self._get_current_phase(case_context)
        if not phase:
            return None
        
        phase_id = phase.get("id")
        
        # Get and categorize workflows
        workflows = self._get_applicable_workflows(phase_id)
        categorized = self._categorize_workflows(workflows, workflow_state)
        
        # Check exit criteria
        exit_criteria = self._check_phase_exit_criteria(phase, workflow_state)
        
        # Generate suggestion
        suggestion = self._generate_suggestion(categorized, exit_criteria, phase)
        
        # Format context
        return self._format_workflow_context(
            case_context.get("client_name", project_name),
            phase,
            categorized,
            exit_criteria,
            suggestion
        )


# ============================================================================
# UTILITY FUNCTIONS FOR WORKFLOW STATE MANAGEMENT
# ============================================================================

def initialize_case_workflow(
    case_folder: Path,
    initial_phase: str = "intake",
    case_type: str = "new"
) -> dict:
    """
    Initialize workflow state for a new case.
    
    Args:
        case_folder: Path to case folder
        initial_phase: Starting phase ID
        case_type: "new" or "transfer"
        
    Returns:
        The created workflow state dict
    """
    state = {
        "current_phase": initial_phase,
        "case_type": case_type,
        "initialized_at": datetime.now().isoformat(),
        "phase_history": [
            {
                "phase": initial_phase,
                "started": datetime.now().isoformat(),
                "completed": None
            }
        ],
        "workflows": {},
        "exit_criteria_status": {}
    }
    
    state_path = case_folder / "workflow_state.json"
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    return state


def start_workflow(
    case_folder: Path,
    workflow_id: str
) -> dict:
    """Mark a workflow as in progress."""
    state_path = case_folder / "workflow_state.json"
    
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    if "workflows" not in state:
        state["workflows"] = {}
    
    state["workflows"][workflow_id] = {
        "status": "in_progress",
        "started_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    return state


def complete_workflow(
    case_folder: Path,
    workflow_id: str,
    outputs: List[str] = None
) -> dict:
    """Mark a workflow as completed."""
    state_path = case_folder / "workflow_state.json"
    
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    if workflow_id in state.get("workflows", {}):
        state["workflows"][workflow_id]["status"] = "completed"
        state["workflows"][workflow_id]["completed_at"] = datetime.now().isoformat()
        if outputs:
            state["workflows"][workflow_id]["outputs"] = outputs
    
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    return state


def update_exit_criterion(
    case_folder: Path,
    criterion: str,
    met: bool = True
) -> dict:
    """Update an exit criterion status."""
    state_path = case_folder / "workflow_state.json"
    
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    if "exit_criteria_status" not in state:
        state["exit_criteria_status"] = {}
    
    state["exit_criteria_status"][criterion] = met
    
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    return state


def advance_phase(
    case_folder: Path,
    new_phase: str
) -> dict:
    """Advance to a new phase."""
    state_path = case_folder / "workflow_state.json"
    
    with open(state_path, 'r') as f:
        state = json.load(f)
    
    # Mark current phase as completed
    if state.get("phase_history"):
        state["phase_history"][-1]["completed"] = datetime.now().isoformat()
    
    # Add new phase
    state["phase_history"].append({
        "phase": new_phase,
        "started": datetime.now().isoformat(),
        "completed": None
    })
    
    state["current_phase"] = new_phase
    state["exit_criteria_status"] = {}  # Reset for new phase
    
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    return state

