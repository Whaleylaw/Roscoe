"""
Roscoe Workflow Engine - State Machine Orchestrator

This module provides the core state machine logic for tracking and advancing
personal injury cases through their lifecycle.

Calendar Integration:
- Automatically creates SOL deadline when case is initialized
- Creates client check-in reminders during treatment phase
- Creates discovery deadlines when complaint is filed
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field, asdict


class PhaseStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    WAITING_ON_USER = "waiting_on_user"
    WAITING_ON_EXTERNAL = "waiting_on_external"
    COMPLETE = "complete"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class ItemOwner(Enum):
    AGENT = "agent"
    USER = "user"
    CLIENT = "client"
    EXTERNAL = "external"


@dataclass
class PendingItem:
    """Represents something the case is waiting on."""
    id: str
    description: str
    owner: str  # Using str for JSON serialization
    phase: str
    workflow: str
    blocking: bool = False
    created_at: str = ""
    due_date: Optional[str] = None
    follow_up_date: Optional[str] = None
    notes: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class NextAction:
    """Represents the next action to take on a case."""
    description: str
    owner: str
    workflow: str
    step: str
    blocking: bool
    can_automate: bool
    prompt: Optional[str] = None
    tool_available: bool = False
    manual_fallback: Optional[str] = None


class StateMachine:
    """
    Core state machine for PI case lifecycle management.
    
    This class:
    1. Loads and manages case state
    2. Determines current phase and active workflows
    3. Identifies what's complete, pending, and blocking
    4. Provides next actions to the agent
    5. Updates state based on user/agent actions
    6. Integrates with calendar system for deadline tracking
    """
    
    # Calendar tool paths (relative to workspace root)
    CALENDAR_ADD_TOOL = "/Tools/calendar/calendar_add_event.py"
    CALENDAR_LIST_TOOL = "/Tools/calendar/calendar_list_events.py"
    CALENDAR_UPDATE_TOOL = "/Tools/calendar/calendar_update_event.py"
    CALENDAR_DATABASE = "/Database/calendar.json"
    
    def __init__(self, schemas_dir: Optional[Path] = None, workspace_dir: Optional[Path] = None):
        """Initialize with path to schema definitions and workspace."""
        if schemas_dir is None:
            schemas_dir = Path(__file__).parent.parent / "schemas"
        
        if workspace_dir is None:
            workspace_dir = Path(__file__).parent.parent.parent
        
        self.schemas_dir = schemas_dir
        self.workspace_dir = workspace_dir
        self._load_definitions()
    
    def _load_definitions(self):
        """Load phase and workflow definitions from JSON schemas."""
        with open(self.schemas_dir / "phase_definitions.json") as f:
            self.phase_defs = json.load(f)
        
        with open(self.schemas_dir / "workflow_definitions.json") as f:
            self.workflow_defs = json.load(f)
    
    def create_new_case(self, case_id: str, client_name: str, accident_date: str, 
                        accident_type: str = "mva") -> Dict[str, Any]:
        """Create a new case with initial state."""
        now = datetime.now().isoformat()
        
        case_state = {
            "case_id": case_id,
            "client": {
                "name": client_name
            },
            "accident": {
                "date": accident_date,
                "type": accident_type
            },
            "injuries": [],
            "insurance_claims": [],
            "medical_providers": [],
            "liens": [],
            "current_phase": "file_setup",
            "phases": {
                "file_setup": {
                    "status": "in_progress",
                    "entered_at": now,
                    "workflows": {
                        "intake": {
                            "status": "in_progress",
                            "started_at": now
                        }
                    },
                    "exit_criteria": {}
                }
            },
            "pending_items": [],
            "deadlines": [],
            "documents": {
                "retainer": {"required": True, "status": "not_sent"},
                "hipaa": {"required": True, "status": "not_sent"},
                "medicare_auth": {"required": False, "status": "not_applicable"}
            },
            "financials": {},
            "notes": [],
            "created_at": now,
            "updated_at": now
        }
        
        # Calculate statute of limitations
        case_state["statute_of_limitations"] = self._calculate_sol(
            accident_date, "Kentucky", accident_type
        )
        
        # Create SOL deadline in calendar
        self._create_sol_calendar_event(case_state)
        
        # Schedule first client check-in (2 weeks from now)
        self._schedule_client_checkin(case_state)
        
        return case_state
    
    def _calculate_sol(self, accident_date: str, jurisdiction: str, 
                       claim_type: str) -> Dict[str, Any]:
        """Calculate statute of limitations for the case."""
        accident_dt = datetime.fromisoformat(accident_date)
        
        # Kentucky SOL rules
        sol_years = {
            "mva": 2,
            "premises": 1,
            "slip_fall": 1,
            "product": 1,
            "medical_malpractice": 1
        }.get(claim_type, 2)
        
        deadline = accident_dt + timedelta(days=sol_years * 365)
        days_remaining = (deadline - datetime.now()).days
        
        # Status thresholds
        if days_remaining <= 60:
            status = "critical"
        elif days_remaining <= 180:
            status = "warning"
        else:
            status = "safe"
        
        return {
            "base_date": accident_date,
            "jurisdiction": jurisdiction,
            "claim_type": claim_type,
            "years": sol_years,
            "deadline": deadline.strftime("%Y-%m-%d"),
            "days_remaining": days_remaining,
            "status": status,
            "pip_extension": None  # Will be updated if PIP pays
        }
    
    def get_case_status(self, case_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive status of a case.
        
        Returns:
            Dict with:
            - current_phase: Current phase name
            - phase_progress: Percentage complete
            - completed_items: List of completed workflows/steps
            - pending_items: List of items waiting on someone
            - blocking_items: Items blocking phase progression
            - next_actions: List of next actions to take
            - alerts: Any critical alerts (SOL, deadlines, etc.)
        """
        current_phase = case_state.get("current_phase", "file_setup")
        phase_state = case_state.get("phases", {}).get(current_phase, {})
        
        # Get completed items
        completed = self._get_completed_items(case_state, current_phase)
        
        # Get pending items
        pending = case_state.get("pending_items", [])
        active_pending = [p for p in pending if not p.get("resolved_at")]
        
        # Get blocking items
        blocking = [p for p in active_pending if p.get("blocking")]
        
        # Get next actions
        next_actions = self._determine_next_actions(case_state, current_phase)
        
        # Check for alerts
        alerts = self._check_alerts(case_state)
        
        # Calculate phase progress
        progress = self._calculate_phase_progress(case_state, current_phase)
        
        return {
            "case_id": case_state.get("case_id"),
            "client_name": case_state.get("client", {}).get("name"),
            "current_phase": current_phase,
            "phase_display_name": self.phase_defs["phases"].get(current_phase, {}).get("name", current_phase),
            "phase_progress": progress,
            "completed_items": completed,
            "pending_items": active_pending,
            "blocking_items": blocking,
            "next_actions": next_actions,
            "alerts": alerts
        }
    
    def _get_completed_items(self, case_state: Dict, phase: str) -> List[Dict]:
        """Get list of completed workflows and steps in current phase."""
        completed = []
        phase_state = case_state.get("phases", {}).get(phase, {})
        workflows = phase_state.get("workflows", {})
        
        for wf_name, wf_state in workflows.items():
            if wf_state.get("status") == "complete":
                completed.append({
                    "type": "workflow",
                    "name": wf_name,
                    "completed_at": wf_state.get("completed_at")
                })
            elif wf_state.get("status") in ["in_progress", "waiting_on_user", "waiting_on_external"]:
                # Check individual steps
                for step_name, step_state in wf_state.get("steps", {}).items():
                    if step_state.get("status") == "complete":
                        completed.append({
                            "type": "step",
                            "workflow": wf_name,
                            "name": step_name,
                            "completed_at": step_state.get("completed_at")
                        })
        
        return completed
    
    def _determine_next_actions(self, case_state: Dict, phase: str) -> List[NextAction]:
        """Determine what actions should be taken next."""
        actions = []
        phase_def = self.phase_defs["phases"].get(phase, {})
        phase_state = case_state.get("phases", {}).get(phase, {})
        
        # Get workflows for this phase
        phase_workflows = phase_def.get("workflows", [])
        
        for wf_name in phase_workflows:
            wf_state = phase_state.get("workflows", {}).get(wf_name, {})
            wf_def = self.workflow_defs["workflows"].get(wf_name, {})
            
            if not wf_def:
                continue
            
            wf_status = wf_state.get("status", "not_started")
            
            # Skip completed or skipped workflows
            if wf_status in ["complete", "skipped"]:
                continue
            
            # Check if workflow should start
            if wf_status == "not_started":
                # Check dependencies
                if self._can_start_workflow(case_state, wf_name):
                    actions.append(self._get_first_action(wf_def, wf_name))
                continue
            
            # Workflow is in progress - find current step
            steps = wf_def.get("steps", [])
            steps_state = wf_state.get("steps", {})
            
            for step in steps:
                step_id = step.get("id")
                step_state = steps_state.get(step_id, {})
                step_status = step_state.get("status", "not_started")
                
                if step_status == "complete":
                    continue
                
                # Check conditions
                condition = step.get("condition")
                if condition and not self._evaluate_condition(case_state, condition):
                    continue
                
                # This is the current step
                action = NextAction(
                    description=step.get("description", step.get("name")),
                    owner=step.get("owner", "agent"),
                    workflow=wf_name,
                    step=step_id,
                    blocking=True,
                    can_automate=step.get("can_automate", False),
                    prompt=step.get("prompt_user"),
                    tool_available=step.get("tool_available", False),
                    manual_fallback=step.get("manual_fallback")
                )
                actions.append(action)
                break  # Only get first incomplete step per workflow
        
        return actions
    
    def _can_start_workflow(self, case_state: Dict, workflow_name: str) -> bool:
        """Check if a workflow's dependencies are met."""
        deps = self.workflow_defs.get("workflow_dependencies", {}).get(workflow_name, {})
        requires = deps.get("requires", [])
        
        if not requires:
            return True
        
        for req in requires:
            # Simple check - could be enhanced with more complex logic
            if " OR " in req:
                # At least one must be true
                alternatives = req.split(" OR ")
                if not any(self._check_requirement(case_state, alt.strip()) for alt in alternatives):
                    return False
            else:
                if not self._check_requirement(case_state, req):
                    return False
        
        return True
    
    def _check_requirement(self, case_state: Dict, requirement: str) -> bool:
        """Check if a single requirement is met."""
        # Handle document checks
        if requirement.startswith("documents."):
            parts = requirement.split(".")
            doc_type = parts[1]
            doc = case_state.get("documents", {}).get(doc_type, {})
            if len(parts) > 2 and parts[2] == "signed":
                return doc.get("status") == "signed"
            return doc.get("status") not in ["not_sent", "not_applicable"]
        
        # Handle workflow completion checks
        for phase_name, phase_state in case_state.get("phases", {}).items():
            workflows = phase_state.get("workflows", {})
            if requirement in workflows:
                return workflows[requirement].get("status") == "complete"
        
        # Handle field existence checks
        return self._get_nested_value(case_state, requirement) is not None
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get a nested value from a dict using dot notation."""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and key.isdigit():
                value = value[int(key)] if int(key) < len(value) else None
            else:
                return None
            if value is None:
                return None
        return value
    
    def _get_first_action(self, workflow_def: Dict, workflow_name: str) -> NextAction:
        """Get the first action for a workflow."""
        steps = workflow_def.get("steps", [])
        if not steps:
            return NextAction(
                description=f"Start {workflow_def.get('name', workflow_name)}",
                owner="agent",
                workflow=workflow_name,
                step="start",
                blocking=True,
                can_automate=True
            )
        
        first_step = steps[0]
        return NextAction(
            description=first_step.get("description", first_step.get("name")),
            owner=first_step.get("owner", "agent"),
            workflow=workflow_name,
            step=first_step.get("id"),
            blocking=True,
            can_automate=first_step.get("can_automate", False),
            prompt=first_step.get("prompt_user"),
            tool_available=first_step.get("tool_available", False),
            manual_fallback=first_step.get("manual_fallback")
        )
    
    def _evaluate_condition(self, case_state: Dict, condition: str) -> bool:
        """Evaluate a condition string against case state."""
        # Simple condition evaluation - could be enhanced
        if "==" in condition:
            parts = condition.split("==")
            left = self._get_nested_value(case_state, parts[0].strip())
            right = parts[1].strip().strip("'\"")
            return str(left) == right
        elif " OR " in condition:
            parts = condition.split(" OR ")
            return any(self._evaluate_condition(case_state, p.strip()) for p in parts)
        elif " AND " in condition:
            parts = condition.split(" AND ")
            return all(self._evaluate_condition(case_state, p.strip()) for p in parts)
        else:
            # Check if field exists and is truthy
            return bool(self._get_nested_value(case_state, condition))
    
    def _calculate_phase_progress(self, case_state: Dict, phase: str) -> int:
        """Calculate percentage progress through current phase."""
        phase_def = self.phase_defs["phases"].get(phase, {})
        phase_state = case_state.get("phases", {}).get(phase, {})
        
        workflows = phase_def.get("workflows", [])
        if not workflows:
            return 0
        
        completed = 0
        for wf_name in workflows:
            wf_state = phase_state.get("workflows", {}).get(wf_name, {})
            if wf_state.get("status") == "complete":
                completed += 1
            elif wf_state.get("status") == "skipped":
                completed += 1
        
        return int((completed / len(workflows)) * 100)
    
    def _check_alerts(self, case_state: Dict) -> List[Dict]:
        """Check for any critical alerts."""
        alerts = []
        
        # Check SOL
        sol = case_state.get("statute_of_limitations", {})
        if sol.get("status") == "critical":
            alerts.append({
                "type": "critical",
                "category": "sol",
                "message": f"CRITICAL: Statute of limitations expires in {sol.get('days_remaining')} days ({sol.get('deadline')}). Must file suit or decline representation.",
                "action_required": "File complaint immediately or decline case"
            })
        elif sol.get("status") == "warning":
            alerts.append({
                "type": "warning",
                "category": "sol",
                "message": f"WARNING: Statute of limitations expires in {sol.get('days_remaining')} days ({sol.get('deadline')}).",
                "action_required": "Evaluate case for demand or litigation"
            })
        
        # Check last client contact
        last_contact = case_state.get("last_client_contact")
        if last_contact:
            last_contact_dt = datetime.fromisoformat(last_contact)
            days_since = (datetime.now() - last_contact_dt).days
            if days_since > 30:
                alerts.append({
                    "type": "warning",
                    "category": "client_contact",
                    "message": f"No client contact in {days_since} days",
                    "action_required": "Schedule client check-in"
                })
        
        # Check overdue pending items
        for item in case_state.get("pending_items", []):
            if item.get("resolved_at"):
                continue
            due_date = item.get("due_date")
            if due_date:
                due_dt = datetime.fromisoformat(due_date)
                if due_dt < datetime.now():
                    alerts.append({
                        "type": "warning",
                        "category": "overdue",
                        "message": f"Overdue: {item.get('description')}",
                        "action_required": "Follow up or resolve"
                    })
        
        return alerts
    
    def complete_step(self, case_state: Dict, workflow_name: str, step_id: str,
                      updates: Optional[Dict] = None) -> Dict:
        """Mark a workflow step as complete and apply updates."""
        now = datetime.now().isoformat()
        current_phase = case_state.get("current_phase")
        
        # Ensure phase and workflow structures exist
        if "phases" not in case_state:
            case_state["phases"] = {}
        if current_phase not in case_state["phases"]:
            case_state["phases"][current_phase] = {"status": "in_progress", "workflows": {}}
        if "workflows" not in case_state["phases"][current_phase]:
            case_state["phases"][current_phase]["workflows"] = {}
        if workflow_name not in case_state["phases"][current_phase]["workflows"]:
            case_state["phases"][current_phase]["workflows"][workflow_name] = {
                "status": "in_progress",
                "started_at": now,
                "steps": {}
            }
        
        wf_state = case_state["phases"][current_phase]["workflows"][workflow_name]
        
        if "steps" not in wf_state:
            wf_state["steps"] = {}
        
        # Mark step complete
        wf_state["steps"][step_id] = {
            "status": "complete",
            "completed_at": now
        }
        
        # Apply any updates
        if updates:
            self._apply_updates(case_state, updates)
        
        # Check if workflow is complete
        wf_def = self.workflow_defs["workflows"].get(workflow_name, {})
        all_steps = [s.get("id") for s in wf_def.get("steps", [])]
        completed_steps = [s for s, state in wf_state.get("steps", {}).items() 
                         if state.get("status") == "complete"]
        
        if set(all_steps) <= set(completed_steps):
            wf_state["status"] = "complete"
            wf_state["completed_at"] = now
            
            # Check if phase is complete
            self._check_phase_complete(case_state, current_phase)
        
        case_state["updated_at"] = now
        return case_state
    
    def _apply_updates(self, case_state: Dict, updates: Dict):
        """Apply field updates to case state."""
        for path, value in updates.items():
            self._set_nested_value(case_state, path, value)
    
    def _set_nested_value(self, data: Dict, path: str, value: Any):
        """Set a nested value in a dict using dot notation."""
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _check_phase_complete(self, case_state: Dict, phase: str):
        """Check if a phase is complete and advance if so."""
        phase_def = self.phase_defs["phases"].get(phase, {})
        phase_state = case_state.get("phases", {}).get(phase, {})
        
        # Check exit criteria
        exit_criteria = phase_def.get("exit_criteria", {})
        hard_blockers = exit_criteria.get("hard_blockers", {})
        
        all_met = True
        for blocker_name, blocker in hard_blockers.items():
            field_path = blocker.get("field_path")
            required_value = blocker.get("required_value")
            check_function = blocker.get("check_function")
            
            if field_path:
                actual_value = self._get_nested_value(case_state, field_path)
                if str(actual_value) != str(required_value):
                    all_met = False
                    break
            elif check_function:
                # Would call a check function here
                pass
        
        if all_met:
            # Check all workflows complete
            workflows = phase_def.get("workflows", [])
            all_workflows_done = True
            for wf_name in workflows:
                wf_state = phase_state.get("workflows", {}).get(wf_name, {})
                if wf_state.get("status") not in ["complete", "skipped"]:
                    all_workflows_done = False
                    break
            
            if all_workflows_done:
                self._advance_phase(case_state, phase)
    
    def _advance_phase(self, case_state: Dict, current_phase: str):
        """Advance to the next phase."""
        now = datetime.now().isoformat()
        phase_def = self.phase_defs["phases"].get(current_phase, {})
        next_phase = phase_def.get("next_phase")
        
        if not next_phase:
            return
        
        # Complete current phase
        case_state["phases"][current_phase]["status"] = "complete"
        case_state["phases"][current_phase]["completed_at"] = now
        
        # Start next phase
        case_state["current_phase"] = next_phase
        case_state["phases"][next_phase] = {
            "status": "in_progress",
            "entered_at": now,
            "workflows": {},
            "exit_criteria": {}
        }
        
        case_state["updated_at"] = now
    
    def add_pending_item(self, case_state: Dict, description: str, owner: str,
                        workflow: str, blocking: bool = False,
                        due_date: Optional[str] = None) -> Dict:
        """Add a pending item to the case."""
        now = datetime.now().isoformat()
        current_phase = case_state.get("current_phase")
        
        item_id = f"pending_{len(case_state.get('pending_items', []))+1}"
        
        item = {
            "id": item_id,
            "description": description,
            "owner": owner,
            "phase": current_phase,
            "workflow": workflow,
            "blocking": blocking,
            "created_at": now,
            "due_date": due_date
        }
        
        if "pending_items" not in case_state:
            case_state["pending_items"] = []
        
        case_state["pending_items"].append(item)
        case_state["updated_at"] = now
        
        return case_state
    
    def resolve_pending_item(self, case_state: Dict, item_id: str) -> Dict:
        """Mark a pending item as resolved."""
        now = datetime.now().isoformat()
        
        for item in case_state.get("pending_items", []):
            if item.get("id") == item_id:
                item["resolved_at"] = now
                break
        
        case_state["updated_at"] = now
        return case_state
    
    def format_status_for_agent(self, status: Dict) -> str:
        """Format case status as a readable message for the agent to relay."""
        lines = []
        
        # Header
        lines.append(f"**{status['client_name']}** - Case {status['case_id']}")
        lines.append(f"Phase: {status['phase_display_name']} ({status['phase_progress']}% complete)")
        lines.append("")
        
        # Alerts first
        if status['alerts']:
            lines.append("⚠️ **Alerts:**")
            for alert in status['alerts']:
                icon = "🚨" if alert['type'] == 'critical' else "⚠️"
                lines.append(f"  {icon} {alert['message']}")
            lines.append("")
        
        # Completed items
        if status['completed_items']:
            lines.append("✅ **Completed:**")
            for item in status['completed_items'][-5:]:  # Last 5
                if item['type'] == 'workflow':
                    lines.append(f"  - {item['name']} workflow")
                else:
                    lines.append(f"  - {item['workflow']}: {item['name']}")
            lines.append("")
        
        # Pending items
        if status['pending_items']:
            lines.append("⏳ **Waiting on:**")
            for item in status['pending_items']:
                owner = item.get('owner', 'unknown')
                blocking = " (BLOCKING)" if item.get('blocking') else ""
                lines.append(f"  - [{owner}] {item['description']}{blocking}")
            lines.append("")
        
        # Next actions
        if status['next_actions']:
            lines.append("📋 **Next Actions:**")
            for action in status['next_actions']:
                owner = action.owner
                auto = " (I can do this)" if action.can_automate and action.tool_available else ""
                manual = f" → Manual: {action.manual_fallback}" if action.manual_fallback and not action.tool_available else ""
                lines.append(f"  - [{owner}] {action.description}{auto}{manual}")
                if action.prompt:
                    lines.append(f"    📝 {action.prompt}")
        
        return "\n".join(lines)


    # ========== Calendar Integration Methods ==========
    
    def _create_sol_calendar_event(self, case_state: Dict) -> Optional[Dict]:
        """Create a calendar event for statute of limitations deadline."""
        sol = case_state.get("statute_of_limitations", {})
        sol_deadline = sol.get("deadline")
        case_id = case_state.get("case_id", "unknown")
        client_name = case_state.get("client", {}).get("name", "Unknown Client")
        
        if not sol_deadline:
            return None
        
        # Create critical SOL deadline event
        event = {
            "title": f"⚠️ SOL DEADLINE: {client_name}",
            "date": sol_deadline,
            "event_type": "deadline",
            "project_name": case_id,
            "priority": "critical",
            "status": "pending",
            "notes": f"Statute of limitations expires. Must file suit or decline before this date. Claim type: {sol.get('claim_type', 'unknown')}",
            "prerequisite_for": None,
            "depends_on": None
        }
        
        return self._add_calendar_event(event, case_state)
    
    def _schedule_client_checkin(self, case_state: Dict, days_from_now: int = 14) -> Optional[Dict]:
        """Schedule a client check-in event."""
        case_id = case_state.get("case_id", "unknown")
        client_name = case_state.get("client", {}).get("name", "Unknown Client")
        
        checkin_date = (datetime.now() + timedelta(days=days_from_now)).strftime("%Y-%m-%d")
        
        event = {
            "title": f"Client Check-In: {client_name}",
            "date": checkin_date,
            "event_type": "task",
            "project_name": case_id,
            "priority": "medium",
            "status": "pending",
            "notes": "Bi-weekly client check-in. Ask about: treatment status, new providers, symptoms, work status.",
            "prerequisite_for": None,
            "depends_on": None
        }
        
        return self._add_calendar_event(event, case_state)
    
    def _create_discovery_deadlines(self, case_state: Dict, 
                                    discovery_period_days: int = 90) -> List[Dict]:
        """Create discovery-related calendar events when complaint is filed."""
        case_id = case_state.get("case_id", "unknown")
        client_name = case_state.get("client", {}).get("name", "Unknown Client")
        complaint_date = case_state.get("litigation", {}).get("complaint_filed_date")
        
        if not complaint_date:
            return []
        
        complaint_dt = datetime.fromisoformat(complaint_date)
        events = []
        
        # Discovery propound deadline (30 days after answer)
        propound_deadline = (complaint_dt + timedelta(days=60)).strftime("%Y-%m-%d")
        events.append({
            "title": f"Propound Discovery: {client_name}",
            "date": propound_deadline,
            "event_type": "deadline",
            "project_name": case_id,
            "priority": "high",
            "status": "pending",
            "notes": "Send initial discovery requests to defendant(s)"
        })
        
        # Discovery close deadline
        close_deadline = (complaint_dt + timedelta(days=discovery_period_days)).strftime("%Y-%m-%d")
        events.append({
            "title": f"Discovery Close: {client_name}",
            "date": close_deadline,
            "event_type": "deadline",
            "project_name": case_id,
            "priority": "high",
            "status": "pending",
            "notes": "All discovery must be completed by this date"
        })
        
        created_events = []
        for event in events:
            result = self._add_calendar_event(event, case_state)
            if result:
                created_events.append(result)
        
        return created_events
    
    def _add_calendar_event(self, event: Dict, case_state: Dict) -> Optional[Dict]:
        """
        Add an event to the calendar database.
        
        This directly updates the calendar.json file rather than calling the
        Python tool, which is designed for agent shell execution.
        """
        try:
            calendar_path = self.workspace_dir / "Database" / "calendar.json"
            
            if not calendar_path.exists():
                calendar_data = {
                    "version": "1.0.0",
                    "description": "Agent calendar for tracking deadlines, tasks, and events",
                    "events": []
                }
            else:
                with open(calendar_path, 'r') as f:
                    calendar_data = json.load(f)
            
            # Generate event ID
            existing_ids = [e.get("id", "") for e in calendar_data.get("events", [])]
            event_num = 1
            while f"evt-{event_num:03d}" in existing_ids:
                event_num += 1
            event_id = f"evt-{event_num:03d}"
            
            # Add metadata
            event["id"] = event_id
            event["created_at"] = datetime.now().isoformat() + "Z"
            event["created_by"] = "workflow_engine"
            
            calendar_data["events"].append(event)
            
            with open(calendar_path, 'w') as f:
                json.dump(calendar_data, f, indent=2)
            
            # Also track in case state
            if "calendar_events" not in case_state:
                case_state["calendar_events"] = []
            case_state["calendar_events"].append(event_id)
            
            return event
            
        except Exception as e:
            # Log error but don't fail - calendar is non-critical
            print(f"Warning: Could not add calendar event: {e}")
            return None
    
    def get_upcoming_deadlines(self, case_state: Dict, days_ahead: int = 30) -> List[Dict]:
        """Get upcoming deadlines for a case from the calendar."""
        case_id = case_state.get("case_id")
        if not case_id:
            return []
        
        try:
            calendar_path = self.workspace_dir / "Database" / "calendar.json"
            if not calendar_path.exists():
                return []
            
            with open(calendar_path, 'r') as f:
                calendar_data = json.load(f)
            
            cutoff_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            
            upcoming = []
            for event in calendar_data.get("events", []):
                if event.get("project_name") != case_id:
                    continue
                if event.get("status") == "completed":
                    continue
                event_date = event.get("date", "")
                if today <= event_date <= cutoff_date:
                    upcoming.append(event)
            
            # Sort by date
            upcoming.sort(key=lambda e: e.get("date", ""))
            return upcoming
            
        except Exception as e:
            print(f"Warning: Could not read calendar: {e}")
            return []
    
    def mark_deadline_complete(self, case_state: Dict, event_id: str) -> bool:
        """Mark a calendar event as completed."""
        try:
            calendar_path = self.workspace_dir / "Database" / "calendar.json"
            if not calendar_path.exists():
                return False
            
            with open(calendar_path, 'r') as f:
                calendar_data = json.load(f)
            
            for event in calendar_data.get("events", []):
                if event.get("id") == event_id:
                    event["status"] = "completed"
                    event["completed_at"] = datetime.now().isoformat() + "Z"
                    
                    with open(calendar_path, 'w') as f:
                        json.dump(calendar_data, f, indent=2)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Warning: Could not update calendar: {e}")
            return False


# Convenience function for agent use
def get_case_status_message(case_state: Dict, schemas_dir: Optional[Path] = None) -> str:
    """Get a formatted status message for a case."""
    sm = StateMachine(schemas_dir)
    status = sm.get_case_status(case_state)
    return sm.format_status_for_agent(status)


def create_case_with_calendar(case_id: str, client_name: str, accident_date: str,
                              accident_type: str = "mva", 
                              workspace_dir: Optional[Path] = None) -> Dict:
    """
    Create a new case and set up all calendar events.
    
    This is the recommended way to create a new case as it:
    1. Creates the case state
    2. Calculates SOL deadline
    3. Creates SOL deadline in calendar
    4. Schedules first client check-in
    """
    sm = StateMachine(workspace_dir=workspace_dir)
    return sm.create_new_case(case_id, client_name, accident_date, accident_type)
