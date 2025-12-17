"""
Roscoe Workflow Engine - State Machine Orchestrator

This module provides the core state machine logic for tracking and advancing
personal injury cases through their lifecycle.

Enhanced with data validation from CaseData adapter for self-healing workflows.
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field, asdict

# Resolve Roscoe runtime root and ensure workflow_engine is importable.
# This bundle is intended to be relocatable across environments (VM paths will differ).
ROSCOE_ROOT = Path(os.environ.get("ROSCOE_ROOT", Path(__file__).resolve().parents[2]))
ENGINE_DIR = Path(__file__).resolve().parent.parent  # .../workflow_engine
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

try:
    from _adapters.case_data import CaseData
except ImportError:
    # Fallback for when running from different context
    CaseData = None


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
    """
    
    def __init__(self, schemas_dir: Optional[Path] = None):
        """Initialize with path to schema definitions."""
        if schemas_dir is None:
            schemas_dir = Path(__file__).parent.parent / "schemas"

        self.schemas_dir = schemas_dir
        self._load_definitions()
        self._load_derivation_rules()

        # Cache for CaseData instances
        self._case_data_cache = {}
    
    def _load_definitions(self):
        """Load phase and workflow definitions from JSON schemas."""
        with open(self.schemas_dir / "phase_definitions.json") as f:
            self.phase_defs = json.load(f)

        with open(self.schemas_dir / "workflow_definitions.json") as f:
            self.workflow_defs = json.load(f)

    def _load_derivation_rules(self):
        """Load derivation rules for validation."""
        rules_path = self.schemas_dir / "derivation_rules.json"
        if rules_path.exists():
            with open(rules_path) as f:
                self.derivation_rules = json.load(f)
        else:
            self.derivation_rules = {}

    def load_case_data(self, case_id: str) -> Optional['CaseData']:
        """
        Load case data using CaseData adapter.
        Caches result to avoid repeated file reads.

        Args:
            case_id: Case/project name

        Returns:
            CaseData instance or None if adapter not available
        """
        if CaseData is None:
            return None

        # Check cache
        if case_id in self._case_data_cache:
            return self._case_data_cache[case_id]

        # Load and cache
        try:
            case_data = CaseData(case_id)
            self._case_data_cache[case_id] = case_data
            return case_data
        except Exception as e:
            print(f"Error loading case data for {case_id}: {e}")
            return None

    def validate_workflow_against_data(
        self,
        workflow_name: str,
        wf_state: Dict,
        case_data: 'CaseData',
        case_state: Optional[Dict] = None
    ) -> Tuple[bool, Optional[str], str]:
        """
        Check if workflow completion status matches actual data.

        Args:
            workflow_name: Workflow identifier
            wf_state: Current workflow state dict
            case_data: CaseData instance with actual case data

        Returns:
            (is_valid, suggested_status, reason)
            - is_valid: True if current status matches data
            - suggested_status: Suggested status if invalid, None if valid
            - reason: Explanation of validation result
        """
        if not case_data:
            return (True, None, "No case data available for validation")

        current_status = wf_state.get("status", "not_started")

        # Get derivation rules for this workflow
        workflow_derivations = self.derivation_rules.get("workflow_derivations", {})
        wf_rules = workflow_derivations.get(workflow_name, {})

        if not wf_rules:
            return (True, None, f"No derivation rules for {workflow_name}")

        # Check completion rules
        complete_when = wf_rules.get("complete_when")
        in_progress_when = wf_rules.get("in_progress_when")

        # INTAKE workflow
        if workflow_name == "intake":
            has_client_name = bool(case_data.overview.get("client_name"))
            has_accident_date = bool(case_data.overview.get("accident_date"))

            if has_client_name and has_accident_date:
                if current_status != "complete":
                    return (False, "complete", "client_name and accident_date present")
            return (True, None, "Status matches data")

        # OPEN BI CLAIM workflow
        elif workflow_name == "open_bi_claim" or workflow_name == "open_insurance_claims":
            bi_claims = case_data.bi_claims
            if bi_claims:
                has_claim_number = any(c.get("claim_number") for c in bi_claims)
                if has_claim_number:
                    if current_status != "complete":
                        claim_num = [c.get("claim_number") for c in bi_claims if c.get("claim_number")][0]
                        return (False, "complete", f"BI claim #{claim_num} found in data")
                elif current_status == "not_started":
                    insurer = bi_claims[0].get("insurance_company_name", "unknown")
                    return (False, "in_progress", f"BI insurer identified: {insurer}")
            return (True, None, "Status matches data")

        # OPEN PIP CLAIM workflow
        elif workflow_name == "open_pip_claim":
            pip_claims = case_data.pip_claims
            if pip_claims:
                has_claim_number = any(c.get("claim_number") for c in pip_claims)
                if has_claim_number:
                    if current_status != "complete":
                        claim_num = [c.get("claim_number") for c in pip_claims if c.get("claim_number")][0]
                        return (False, "complete", f"PIP claim #{claim_num} found in data")
                elif current_status == "not_started":
                    return (False, "in_progress", "PIP insurer identified")
            return (True, None, "Status matches data")

        # SEND DOCUMENTS FOR SIGNATURE workflow
        elif workflow_name == "send_documents_for_signature":
            # Check case_state for document signatures (not in data files)
            if case_state:
                retainer_status = case_state.get("documents", {}).get("retainer", {}).get("status")
                hipaa_status = case_state.get("documents", {}).get("hipaa", {}).get("status")

                if retainer_status == "signed":
                    if current_status != "complete":
                        docs_signed = ["retainer"]
                        if hipaa_status == "signed":
                            docs_signed.append("HIPAA")
                        return (False, "complete", f"Required documents signed: {', '.join(docs_signed)}")
                elif retainer_status == "sent":
                    if current_status == "not_started":
                        return (False, "in_progress", "Documents sent, awaiting signatures")
            return (True, None, "Status matches document state")

        # MEDICAL PROVIDER SETUP workflow
        elif workflow_name == "medical_provider_setup":
            if len(case_data.medical_providers) > 0:
                if current_status != "complete":
                    return (False, "complete", f"{len(case_data.medical_providers)} providers in data")
            return (True, None, "Status matches data")

        # REQUEST RECORDS & BILLS workflow
        elif workflow_name == "request_records_bills":
            providers = case_data.medical_providers
            if providers:
                all_have_records = all(p.get("date_medical_records_received") for p in providers)
                all_have_bills = all(p.get("medical_bills_received_date") for p in providers)

                if all_have_records and all_have_bills:
                    if current_status != "complete":
                        return (False, "complete", f"All {len(providers)} providers have records and bills")
                elif any(p.get("date_medical_records_requested") for p in providers):
                    if current_status == "not_started":
                        return (False, "in_progress", "Records requested from providers")
            return (True, None, "Status matches data")

        # SEND DEMAND workflow
        elif workflow_name == "send_demand":
            bi_claims = case_data.bi_claims
            if bi_claims:
                has_demand_sent = any(c.get("date_demand_sent") for c in bi_claims)
                if has_demand_sent:
                    if current_status != "complete":
                        demand_date = [c.get("date_demand_sent") for c in bi_claims if c.get("date_demand_sent")][0]
                        return (False, "complete", f"Demand sent on {demand_date}")
            return (True, None, "Status matches data")

        # NEGOTIATION workflow
        elif workflow_name == "bi_negotiation" or workflow_name == "negotiate_claim":
            bi_claims = case_data.bi_claims
            if bi_claims:
                has_settlement = any(c.get("settlement_amount") for c in bi_claims)
                has_offer = any(c.get("current_offer") for c in bi_claims)

                if has_settlement:
                    if current_status != "complete":
                        return (False, "complete", "Settlement reached")
                elif has_offer:
                    if current_status not in ["in_progress", "waiting_on_user"]:
                        offer = [c.get("current_offer") for c in bi_claims if c.get("current_offer")][0]
                        return (False, "in_progress", f"Active negotiation - offer: ${offer:,.0f}")
            return (True, None, "Status matches data")

        # SETTLEMENT PROCESSING workflow
        elif workflow_name == "settlement_processing":
            all_claims = case_data.insurance_claims
            if all_claims:
                has_settlement = any(c.get("settlement_amount") for c in all_claims)
                has_settlement_date = any(c.get("settlement_date") for c in all_claims)

                if has_settlement_date:
                    if current_status != "complete":
                        return (False, "complete", "Settlement date recorded")
                elif has_settlement:
                    if current_status not in ["in_progress", "waiting_on_user"]:
                        return (False, "in_progress", "Settlement reached, processing")
            return (True, None, "Status matches data")

        # Default: no validation rules
        return (True, None, f"No specific validation for {workflow_name}")

    def _log_audit(self, case_state: Dict, action: str, details: Dict):
        """Add entry to audit log."""
        if "audit_log" not in case_state:
            case_state["audit_log"] = []

        case_state["audit_log"].append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        })

    def sync_workflows_with_data(
        self,
        case_state: Dict,
        case_data: 'CaseData'
    ) -> List[Dict[str, Any]]:
        """
        Auto-update workflow statuses when data proves completion.
        Only upgrades statuses (never downgrades from complete to in_progress).

        Args:
            case_state: Current case state dict
            case_data: CaseData instance with actual case data

        Returns:
            List of corrections made:
            [{"workflow": "open_bi_claim", "old_status": "in_progress",
              "new_status": "complete", "reason": "claim_number exists",
              "data_evidence": "insurance[0].claim_number = '12345'"}]
        """
        if not case_data:
            return []

        corrections = []
        current_phase = case_state.get("current_phase")

        if not current_phase or "phases" not in case_state:
            return []

        phase_state = case_state["phases"].get(current_phase, {})
        workflows = phase_state.get("workflows", {})

        # Also check previous phases for completion
        all_phases = case_state.get("phases", {})

        for phase_name, p_state in all_phases.items():
            phase_workflows = p_state.get("workflows", {})

            for wf_name, wf_state in phase_workflows.items():
                # Skip if already complete
                if wf_state.get("status") == "complete":
                    continue

                # Validate against data (pass case_state for document signature checks)
                is_valid, suggested_status, reason = self.validate_workflow_against_data(
                    wf_name, wf_state, case_data, case_state
                )

                if not is_valid and suggested_status:
                    old_status = wf_state.get("status", "not_started")

                    # Only upgrade status (not_started → in_progress → complete)
                    status_order = {"not_started": 0, "in_progress": 1, "waiting_on_user": 1,
                                  "waiting_on_external": 1, "complete": 2}
                    old_order = status_order.get(old_status, 0)
                    new_order = status_order.get(suggested_status, 0)

                    if new_order > old_order:
                        # Update workflow status
                        wf_state["status"] = suggested_status

                        if suggested_status == "complete":
                            wf_state["completed_at"] = datetime.now().isoformat()

                        # Create correction record
                        correction = {
                            "workflow": wf_name,
                            "phase": phase_name,
                            "old_status": old_status,
                            "new_status": suggested_status,
                            "reason": reason,
                            "data_evidence": self._get_data_evidence(wf_name, case_data, case_state)
                        }
                        corrections.append(correction)

                        # Log to audit trail
                        self._log_audit(case_state, "workflow_auto_completed", correction)

        case_state["updated_at"] = datetime.now().isoformat()
        return corrections

    def _get_data_evidence(self, workflow_name: str, case_data: 'CaseData', case_state: Optional[Dict] = None) -> str:
        """Get data evidence string for a workflow completion."""
        if workflow_name in ["open_bi_claim", "open_insurance_claims"]:
            bi_claims = case_data.bi_claims
            if bi_claims and bi_claims[0].get("claim_number"):
                return f"insurance[BI].claim_number = '{bi_claims[0].get('claim_number')}'"

        elif workflow_name == "open_pip_claim":
            pip_claims = case_data.pip_claims
            if pip_claims and pip_claims[0].get("claim_number"):
                return f"insurance[PIP].claim_number = '{pip_claims[0].get('claim_number')}'"

        elif workflow_name == "send_documents_for_signature":
            if case_state:
                retainer = case_state.get("documents", {}).get("retainer", {}).get("status")
                hipaa = case_state.get("documents", {}).get("hipaa", {}).get("status")
                docs = []
                if retainer == "signed":
                    docs.append("retainer")
                if hipaa == "signed":
                    docs.append("HIPAA")
                if docs:
                    return f"documents.{','.join(docs)}.status = 'signed'"
            return "Document signatures in case_state"

        elif workflow_name == "medical_provider_setup":
            return f"{len(case_data.medical_providers)} providers in medical_providers.json"

        elif workflow_name == "send_demand":
            bi_claims = case_data.bi_claims
            if bi_claims and bi_claims[0].get("date_demand_sent"):
                return f"insurance[BI].date_demand_sent = '{bi_claims[0].get('date_demand_sent')}'"

        elif workflow_name == "settlement_processing":
            all_claims = case_data.insurance_claims
            if all_claims:
                for claim in all_claims:
                    if claim.get("settlement_date"):
                        return f"insurance[].settlement_date = '{claim.get('settlement_date')}'"

        return "Data validation confirmed completion"

    def load_litigation_data(self, project_name: str) -> Optional[Dict]:
        """
        Load litigation data for a case.

        Checks both:
        1. Project-specific litigation.json file
        2. Centralized Database/litigation.json

        Args:
            project_name: Case/project name

        Returns:
            Litigation data dict or None if not found
        """
        # Get workspace path (same logic as CaseData adapter)
        if CaseData:
            from _adapters.case_data import get_workspace_path
            workspace_path = get_workspace_path()
        else:
            workspace_path = Path(".")

        # First check project-specific file (note: folder has space, not underscore)
        litigation_file = workspace_path / "projects" / project_name / "Case Information" / "litigation.json"
        if litigation_file.exists():
            try:
                with open(litigation_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        # Fall back to centralized database
        centralized_file = workspace_path / "Database" / "litigation.json"
        if centralized_file.exists():
            try:
                with open(centralized_file, 'r') as f:
                    all_litigation = json.load(f)
                    # Find the entry for this project
                    for entry in all_litigation:
                        if entry.get("project_name", "").lower() == project_name.lower():
                            return entry
            except Exception:
                pass

        return None

    def derive_litigation_workflows(self, litigation_data: Dict) -> Dict[str, Dict]:
        """
        Derive litigation-specific workflows from litigation.json.

        Args:
            litigation_data: Litigation data dict

        Returns:
            Dict of workflow states to add/update in case_state
            Format: {workflow_id: {status, completion_pct, details, ...}}
        """
        workflows: Dict[str, Dict] = {}

        if not litigation_data:
            return workflows

        # === COMPLAINT FILED ===
        if litigation_data.get("complaint_filed_date"):
            case_number = litigation_data.get("case_number", "")
            court = litigation_data.get("court", "")
            workflows["draft_file_complaint"] = {
                "status": "complete",
                "completed_at": litigation_data.get("complaint_filed_date"),
                "details": f"Case #{case_number} in {court}" if case_number else "Complaint filed"
            }

        # === DISCOVERY PROPOUNDED ===
        if litigation_data.get("interrogatories_sent_to_defendant_date"):
            workflows["propound_discovery"] = {
                "status": "complete",
                "completed_at": litigation_data.get("interrogatories_sent_to_defendant_date"),
                "details": f"Discovery sent {litigation_data['interrogatories_sent_to_defendant_date']}"
            }

        # === DISCOVERY RESPONSES RECEIVED ===
        # Our workflows separate: respond_to_discovery (our responses) vs review_responses (defendant responses).
        if litigation_data.get("interrogatories_received_from_defendant_date"):
            workflows["review_responses"] = {
                "status": "in_progress",
                "details": f"Defendant responses received {litigation_data.get('interrogatories_received_from_defendant_date')}; review for deficiencies"
            }

        # === CLIENT DEPOSITION (occurred) ===
        if litigation_data.get("plaintiff_deposition_date"):
            workflows["party_depositions"] = {
                "status": "complete",
                "completed_at": litigation_data.get("plaintiff_deposition_date"),
                "details": f"Deposed on {litigation_data['plaintiff_deposition_date']}"
            }

        # === MEDIATION ===
        if litigation_data.get("mediation_date"):
            mediation_date = litigation_data.get("mediation_date")
            days_until_mediation = self._days_until(mediation_date) if mediation_date else 999

            if litigation_data.get("mediation_completed"):
                result = litigation_data.get("mediation_result", "unknown")
                workflows["attend_mediation"] = {
                    "status": "complete",
                    "completed_at": mediation_date,
                    "details": f"Mediation {mediation_date} - Result: {result}"
                }
            elif days_until_mediation > 0:
                workflows["attend_mediation"] = {
                    "status": "in_progress",
                    "details": f"Scheduled for {mediation_date}"
                }
            else:
                workflows["attend_mediation"] = {
                    "status": "complete",
                    "completed_at": mediation_date,
                    "details": f"Mediation occurred {mediation_date}"
                }

        # === TRIAL ===
        if litigation_data.get("trial_date"):
            trial_date = litigation_data.get("trial_date")
            days_to_trial = self._days_until(trial_date) if trial_date else 999

            if days_to_trial > 0:
                workflows["trial_materials"] = {
                    "status": "in_progress",
                    "details": f"Trial in {days_to_trial} days ({trial_date})"
                }
            else:
                # Trial date passed
                workflows["conduct_trial"] = {
                    "status": "complete",
                    "completed_at": trial_date,
                    "details": f"Trial date: {trial_date}"
                }

        return workflows

    def _days_until(self, date_str: Optional[str]) -> int:
        """Calculate days until a date."""
        if not date_str:
            return 999
        try:
            date = datetime.fromisoformat(date_str[:10])
            return (date - datetime.now()).days
        except:
            return 999

    def validate_litigation_state(
        self,
        case_state: Dict,
        litigation_data: Dict
    ) -> List[Dict[str, Any]]:
        """
        Check if litigation workflows match litigation.json data.
        Auto-complete workflows when data proves completion.

        Args:
            case_state: Current case state dict
            litigation_data: Litigation data from litigation.json

        Returns:
            List of corrections made
        """
        if not litigation_data:
            return []

        corrections = []

        # Derive what workflows should exist based on litigation data
        derived_workflows = self.derive_litigation_workflows(litigation_data)

        # Nested litigation model:
        # case_state.phases.phase_7_litigation.subphases.{phase_7_1_complaint,...}.workflows
        lit_phase_id = "phase_7_litigation"
        if lit_phase_id not in case_state.get("phases", {}):
            return []

        lit_state = case_state["phases"][lit_phase_id]
        subphases_state = lit_state.setdefault("subphases", {})

        wf_subphase_map = {
            "draft_file_complaint": "phase_7_1_complaint",
            "serve_defendant": "phase_7_1_complaint",
            "process_answer": "phase_7_1_complaint",
            "propound_discovery": "phase_7_2_discovery",
            "respond_to_discovery": "phase_7_2_discovery",
            "review_responses": "phase_7_2_discovery",
            "party_depositions": "phase_7_2_discovery",
            "client_deposition_prep": "phase_7_2_discovery",
            "corp_rep_deposition": "phase_7_2_discovery",
            "defense_expert_depo": "phase_7_2_discovery",
            "third_party_deposition": "phase_7_2_discovery",
            "prepare_mediation": "phase_7_3_mediation",
            "attend_mediation": "phase_7_3_mediation",
            "expert_management": "phase_7_4_trial_prep",
            "trial_materials": "phase_7_4_trial_prep",
            "conduct_trial": "phase_7_5_trial"
        }

        status_order = {"not_started": 0, "pending": 1, "in_progress": 2, "complete": 3}

        for wf_name, derived_wf in derived_workflows.items():
            subphase_id = wf_subphase_map.get(wf_name)
            if not subphase_id:
                continue

            sp_state = subphases_state.setdefault(subphase_id, {"status": "in_progress", "workflows": {}})
            sp_workflows = sp_state.setdefault("workflows", {})
            current_wf = sp_workflows.get(wf_name, {"status": "not_started"})
            current_status = current_wf.get("status", "not_started")
            derived_status = derived_wf.get("status", "not_started")

            if status_order.get(derived_status, 0) > status_order.get(current_status, 0):
                sp_workflows[wf_name] = {**current_wf, **derived_wf}
                correction = {
                    "workflow": wf_name,
                    "phase": lit_phase_id,
                    "subphase": subphase_id,
                    "old_status": current_status,
                    "new_status": derived_status,
                    "reason": f"Litigation data confirms {wf_name}",
                    "data_evidence": f"litigation.json indicates status for {wf_name}"
                }
                corrections.append(correction)
                self._log_audit(case_state, "litigation_workflow_synced", correction)

        if corrections:
            case_state["updated_at"] = datetime.now().isoformat()

        return corrections

    def suggest_phase_change(
        self,
        case_state: Dict,
        case_data: 'CaseData'
    ) -> Optional[Dict]:
        """
        Detect when phase should advance based on data.
        Does NOT auto-advance - only creates suggestion for user approval.

        Args:
            case_state: Current case state dict
            case_data: CaseData instance with actual case data

        Returns:
            Pending phase change suggestion dict or None
            {
                "from_phase": "phase_2_treatment",
                "to_phase": "phase_3_demand",
                "reason": "All criteria met for phase advancement",
                "data_evidence": [
                    "✓ All providers have date_treatment_completed",
                    "✓ All providers have date_medical_records_received"
                ],
                "criteria_met": ["treatment_complete", "all_records_received"],
                "suggested_at": "2024-01-20T10:30:00"
            }
        """
        if not case_data:
            return None

        current_phase = case_state.get("current_phase")
        if not current_phase:
            return None

        phase_def = self.phase_defs["phases"].get(current_phase, {})
        next_phase = phase_def.get("next_phase")

        if not next_phase:
            return None

        # Check exit criteria
        exit_criteria = phase_def.get("exit_criteria", {})
        hard_blockers = exit_criteria.get("hard_blockers", {})

        # Collect evidence
        data_evidence = []
        criteria_met = []
        all_criteria_satisfied = True

        # Check hard blockers against both state and data
        for blocker_name, blocker in hard_blockers.items():
            field_path = blocker.get("field_path")
            required_value = blocker.get("required_value")

            if field_path:
                actual_value = self._get_nested_value(case_state, field_path)
                if str(actual_value) == str(required_value):
                    data_evidence.append(f"✓ {blocker.get('description', blocker_name)}")
                    criteria_met.append(blocker_name)
                else:
                    all_criteria_satisfied = False
                    break

        if not all_criteria_satisfied:
            return None

        # Check workflows complete
        phase_state = case_state.get("phases", {}).get(current_phase, {})
        workflows = phase_def.get("workflows", [])

        all_workflows_done = True
        for wf_name in workflows:
            wf_state = phase_state.get("workflows", {}).get(wf_name, {})
            wf_status = wf_state.get("status", "not_started")

            if wf_status in ["complete", "skipped"]:
                data_evidence.append(f"✓ {wf_name} workflow complete")
                criteria_met.append(wf_name)
            else:
                all_workflows_done = False

        if not all_workflows_done:
            return None

        # Add data-based evidence for phase-specific transitions
        if current_phase == "phase_2_treatment" and next_phase == "phase_3_demand":
            providers = case_data.medical_providers
            if providers:
                all_complete = all(p.get("date_treatment_completed") for p in providers)
                all_records = all(p.get("date_medical_records_received") for p in providers)

                if all_complete:
                    data_evidence.append(f"✓ All {len(providers)} providers have completed treatment")
                if all_records:
                    data_evidence.append(f"✓ All {len(providers)} providers have records received")

        elif current_phase == "phase_3_demand" and next_phase == "phase_4_negotiation":
            bi_claims = case_data.bi_claims
            if bi_claims:
                demands_sent = [c for c in bi_claims if c.get("date_demand_sent")]
                if demands_sent:
                    data_evidence.append(f"✓ Demand sent to {len(demands_sent)} BI claim(s)")

        # All criteria met - create suggestion
        return {
            "from_phase": current_phase,
            "to_phase": next_phase,
            "reason": f"All exit criteria met for {phase_def.get('name', current_phase)} phase",
            "data_evidence": data_evidence,
            "criteria_met": criteria_met,
            "suggested_at": datetime.now().isoformat()
        }

    def approve_phase_change(
        self,
        case_state: Dict,
        approve: bool = True,
        reason: Optional[str] = None
    ) -> Dict:
        """
        User approves or rejects phase change.

        Args:
            case_state: Current case state dict
            approve: True to approve, False to reject
            reason: Optional reason for rejection

        Returns:
            Updated case_state
        """
        pending_change = case_state.get("pending_phase_change")

        if not pending_change:
            return case_state

        if approve:
            # Execute phase advancement
            from_phase = pending_change.get("from_phase")
            to_phase = pending_change.get("to_phase")

            if from_phase and to_phase:
                self._advance_phase(case_state, from_phase)

                # Log approval
                self._log_audit(case_state, "phase_change_approved", {
                    "from_phase": from_phase,
                    "to_phase": to_phase,
                    "criteria_met": pending_change.get("criteria_met", []),
                    "approved_at": datetime.now().isoformat()
                })

                # Add to phase change history
                if "phase_change_history" not in case_state:
                    case_state["phase_change_history"] = []

                case_state["phase_change_history"].append({
                    "from_phase": from_phase,
                    "to_phase": to_phase,
                    "approved": True,
                    "reason": "All criteria met",
                    "changed_at": datetime.now().isoformat()
                })

        else:
            # Log rejection
            self._log_audit(case_state, "phase_change_rejected", {
                "from_phase": pending_change.get("from_phase"),
                "to_phase": pending_change.get("to_phase"),
                "reason": reason or "User declined phase change",
                "rejected_at": datetime.now().isoformat()
            })

            # Store rejection (to avoid re-suggesting immediately)
            if "rejected_phase_changes" not in case_state:
                case_state["rejected_phase_changes"] = []

            case_state["rejected_phase_changes"].append({
                "from_phase": pending_change.get("from_phase"),
                "to_phase": pending_change.get("to_phase"),
                "reason": reason,
                "rejected_at": datetime.now().isoformat()
            })

        # Clear pending change
        case_state.pop("pending_phase_change", None)
        case_state["updated_at"] = datetime.now().isoformat()

        return case_state

    def compute_sol_status(
        self,
        case_data: 'CaseData',
        litigation_data: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate statute of limitations status.

        Checks if complaint filed (from litigation data) - if so, SOL is fulfilled.
        Otherwise calculates remaining days based on accident date + SOL years.

        Args:
            case_data: CaseData instance with case overview
            litigation_data: Optional litigation data to check for complaint filing

        Returns:
            Dict with:
            - status: "safe" | "attention" | "urgent" | "critical" | "fulfilled"
            - days_remaining: int or None (if fulfilled)
            - sol_date: str
            - sol_years: int
            - sol_type: "mva" | "premise" | "workers_comp"
            - message: str
            - complaint_filed_date: str or None (if complaint filed)
        """
        if not case_data:
            return {"status": "unknown", "message": "No case data available"}

        # Check if complaint has been filed - SOL is fulfilled once complaint is filed
        if litigation_data and litigation_data.get("complaint_filed_date"):
            complaint_date = litigation_data.get("complaint_filed_date")
            if complaint_date:  # Ensure it's not None or empty string
                return {
                    "status": "fulfilled",
                    "message": f"SOL fulfilled - Complaint filed on {complaint_date}",
                    "complaint_filed_date": complaint_date,
                    "days_remaining": None,
                    "sol_date": None,
                    "sol_years": None,
                    "sol_type": None
                }

        # Continue with normal SOL calculation if no complaint filed
        accident_date = case_data.overview.get("accident_date")
        if not accident_date:
            return {"status": "unknown", "message": "No accident date recorded"}

        # Determine case type for SOL
        project_name = case_data.overview.get("project_name", "").lower()

        # Get SOL config from derivation rules
        sol_config = self.derivation_rules.get("sol_tracking", {})
        sol_types = sol_config.get("sol_types", {})

        # Default to MVA if not specified
        sol_years = 2  # Kentucky MVA default
        sol_type = "mva"

        if "wc" in project_name or "workers" in project_name:
            sol_years = sol_types.get("workers_comp", {}).get("years", 2)
            sol_type = "workers_comp"
        elif "premise" in project_name or "slip" in project_name:
            sol_years = sol_types.get("premise", {}).get("years", 1)
            sol_type = "premise"
        elif "mva" in project_name or "auto" in project_name:
            sol_years = sol_types.get("mva", {}).get("years", 2)
            sol_type = "mva"

        try:
            acc_date = datetime.fromisoformat(accident_date[:10])
            sol_date = acc_date + timedelta(days=sol_years * 365)
            days_remaining = (sol_date - datetime.now()).days

            # Determine status using thresholds from derivation rules
            thresholds = sol_config.get("warning_thresholds", {})
            if days_remaining <= thresholds.get("critical", {}).get("days_remaining", 14):
                status = "critical"
            elif days_remaining <= thresholds.get("urgent", {}).get("days_remaining", 30):
                status = "urgent"
            elif days_remaining <= thresholds.get("attention", {}).get("days_remaining", 90):
                status = "attention"
            else:
                status = "safe"

            return {
                "status": status,
                "days_remaining": days_remaining,
                "sol_date": sol_date.strftime("%Y-%m-%d"),
                "sol_years": sol_years,
                "sol_type": sol_type,
                "message": f"{days_remaining} days remaining ({status})",
                "complaint_filed_date": None
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_new_case(
        self,
        case_id: str,
        client_name: str,
        accident_date: str,
        accident_type: str = "mva"
    ) -> Dict[str, Any]:
        """
        Create a new case with initial state.

        NOTE: Phases are directory-style IDs (phase_0_onboarding, phase_1_file_setup, ...).
        Litigation is nested under phase_7_litigation and tracked via current_subphase.
        """
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
            "current_phase": "phase_0_onboarding",
            "current_subphase": None,
            "phases": {
                "phase_0_onboarding": {
                    "status": "in_progress",
                    "entered_at": now,
                    "workflows": {
                        "case_setup": {
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
                "client_info_sheet": {"required": True, "status": "not_started"},
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

        Enhanced with data validation from CaseData adapter.

        Returns:
            Dict with:
            - current_phase: Current phase name
            - phase_progress: Percentage complete
            - completed_items: List of completed workflows/steps
            - pending_items: List of items waiting on someone
            - blocking_items: Items blocking phase progression
            - next_actions: List of next actions to take
            - alerts: Any critical alerts (SOL, deadlines, etc.)
            - data_corrections: List of auto-corrections made (NEW)
        """
        current_phase = case_state.get("current_phase", "phase_0_onboarding")
        phase_state = case_state.get("phases", {}).get(current_phase, {})

        # NEW: Load case data and sync workflows
        corrections = []
        case_data = self.load_case_data(case_state.get("case_id"))
        if case_data:
            corrections = self.sync_workflows_with_data(case_state, case_data)

        # NEW: Check for litigation and validate if in litigation track (nested model)
        if current_phase == "phase_7_litigation":
            litigation_data = self.load_litigation_data(case_state.get("case_id"))
            if litigation_data:
                lit_corrections = self.validate_litigation_state(case_state, litigation_data)
                corrections.extend(lit_corrections)

        # NEW: Check for phase change suggestion
        phase_suggestion = None
        if case_data:
            phase_suggestion = self.suggest_phase_change(case_state, case_data)
            if phase_suggestion:
                case_state["pending_phase_change"] = phase_suggestion

        # NEW: Compute SOL status with litigation check
        sol_status = None
        if case_data:
            litigation_data = None
            if current_phase == "phase_7_litigation":
                litigation_data = self.load_litigation_data(case_state.get("case_id"))
            sol_status = self.compute_sol_status(case_data, litigation_data)

        # Get completed items
        completed = self._get_completed_items(case_state, current_phase)

        # Get pending items
        pending = case_state.get("pending_items", [])
        active_pending = [p for p in pending if not p.get("resolved_at")]

        # Get blocking items
        blocking = [p for p in active_pending if p.get("blocking")]

        # Get next actions
        next_actions = self._determine_next_actions(case_state, current_phase)

        # Check for alerts (including SOL alerts)
        alerts = self._check_alerts(case_state)

        # Add SOL alert if urgent/critical
        if sol_status and sol_status.get("status") in ["urgent", "critical"]:
            alert_type = "critical" if sol_status.get("status") == "critical" else "warning"
            alerts.insert(0, {  # Insert at front for visibility
                "type": alert_type,
                "category": "sol",
                "message": sol_status.get("message", "SOL deadline approaching"),
                "action_required": "File complaint immediately" if alert_type == "critical" else "Evaluate case for litigation",
                "days_remaining": sol_status.get("days_remaining"),
                "sol_date": sol_status.get("sol_date")
            })
        elif sol_status and sol_status.get("status") == "fulfilled":
            # Add info alert that SOL is fulfilled
            alerts.append({
                "type": "info",
                "category": "sol",
                "message": sol_status.get("message", "SOL fulfilled"),
                "complaint_filed_date": sol_status.get("complaint_filed_date")
            })

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
            "alerts": alerts,
            "data_corrections": corrections,  # NEW
            "pending_phase_change": phase_suggestion  # NEW
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

        # Nested litigation model: compute next actions across subphases.
        if phase == "phase_7_litigation":
            lit_def = phase_def
            lit_state = phase_state
            subphase_defs = lit_def.get("subphase_definitions", {}) or {}
            subphases_state = lit_state.setdefault("subphases", {})

            preferred = case_state.get("current_subphase")
            subphase_order = list(subphase_defs.keys())
            if preferred and preferred in subphase_defs:
                subphase_order = [preferred] + [s for s in subphase_order if s != preferred]

            def add_actions_for_workflows(workflow_ids: List[str], workflows_state: Dict[str, Any]):
                for wf_name in workflow_ids:
                    wf_state = workflows_state.get(wf_name, {})
                    wf_def = self.workflow_defs["workflows"].get(wf_name, {})
                    if not wf_def:
                        continue

                    wf_status = wf_state.get("status", "not_started")

                    # Skip completed/skipped
                    if wf_status in ["complete", "skipped"]:
                        continue

                    # If not started, suggest first action (dependency-aware)
                    if wf_status == "not_started":
                        if self._can_start_workflow(case_state, wf_name):
                            actions.append(self._get_first_action(wf_def, wf_name))
                        continue

                    # In progress: find first incomplete step
                    steps = wf_def.get("steps", [])
                    steps_state = wf_state.get("steps", {})
                    for step in steps:
                        step_id = step.get("id")
                        step_state = steps_state.get(step_id, {})
                        step_status = step_state.get("status", "not_started")
                        if step_status == "complete":
                            continue

                        condition = step.get("condition")
                        if condition and not self._evaluate_condition(case_state, condition):
                            continue

                        actions.append(NextAction(
                            description=step.get("description", step.get("name")),
                            owner=step.get("owner", "agent"),
                            workflow=wf_name,
                            step=step_id,
                            blocking=True,
                            can_automate=step.get("can_automate", False),
                            prompt=step.get("prompt_user"),
                            tool_available=step.get("tool_available", False),
                            manual_fallback=step.get("manual_fallback")
                        ))
                        break

            for subphase_id in subphase_order:
                sp_def = subphase_defs.get(subphase_id, {})
                wf_ids = sp_def.get("workflows", []) or []
                sp_state = subphases_state.setdefault(subphase_id, {"status": "in_progress", "workflows": {}})
                sp_workflows_state = sp_state.setdefault("workflows", {})
                add_actions_for_workflows(wf_ids, sp_workflows_state)

            return actions
        
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

            # Also check nested litigation subphases
            if phase_name == "phase_7_litigation":
                subphases = phase_state.get("subphases", {}) or {}
                for _, sp_state in subphases.items():
                    sp_workflows = (sp_state or {}).get("workflows", {}) or {}
                    if requirement in sp_workflows:
                        return sp_workflows[requirement].get("status") == "complete"
        
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

        # Nested litigation: compute progress across all subphase workflows.
        if phase == "phase_7_litigation":
            subphase_defs = (phase_def.get("subphase_definitions") or {})
            if not subphase_defs:
                return 0

            subphases_state = (phase_state.get("subphases") or {})
            total = 0
            completed = 0

            for subphase_id, sp_def in subphase_defs.items():
                wf_ids = sp_def.get("workflows", []) or []
                sp_state = (subphases_state.get(subphase_id) or {})
                sp_workflows = (sp_state.get("workflows") or {})
                for wf_name in wf_ids:
                    total += 1
                    wf_state = sp_workflows.get(wf_name, {})
                    if wf_state.get("status") in ["complete", "skipped"]:
                        completed += 1

            return int((completed / total) * 100) if total else 0
        
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
        current_subphase = case_state.get("current_subphase")
        
        # Nested litigation: write workflow progress under phases.phase_7_litigation.subphases.{subphase}.workflows
        if current_phase == "phase_7_litigation":
            if not current_subphase:
                # Default to complaint subphase if not explicitly set
                current_subphase = "phase_7_1_complaint"
                case_state["current_subphase"] = current_subphase

            case_state.setdefault("phases", {})
            case_state["phases"].setdefault("phase_7_litigation", {"status": "in_progress", "entered_at": now, "workflows": {}, "subphases": {}})
            lit_state = case_state["phases"]["phase_7_litigation"]
            subphases = lit_state.setdefault("subphases", {})
            sp_state = subphases.setdefault(current_subphase, {"status": "in_progress", "workflows": {}})
            sp_workflows = sp_state.setdefault("workflows", {})

            if workflow_name not in sp_workflows:
                sp_workflows[workflow_name] = {
                    "status": "in_progress",
                    "started_at": now,
                    "steps": {}
                }

            wf_state = sp_workflows[workflow_name]
            wf_state.setdefault("steps", {})

            wf_state["steps"][step_id] = {"status": "complete", "completed_at": now}

            if updates:
                self._apply_updates(case_state, updates)

            wf_def = self.workflow_defs["workflows"].get(workflow_name, {})
            all_steps = [s.get("id") for s in wf_def.get("steps", [])]
            completed_steps = [s for s, state in wf_state.get("steps", {}).items() if state.get("status") == "complete"]

            if all_steps and set(all_steps) <= set(completed_steps):
                wf_state["status"] = "complete"
                wf_state["completed_at"] = now

            case_state["updated_at"] = now
            return case_state

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
        """
        Check if a phase is complete.

        NOTE: This method no longer auto-advances phases. Phase advancement
        now requires user approval via suggest_phase_change() and approve_phase_change().
        """
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

            # Phase is complete - suggestion will be created in get_case_status()
            # User must approve via approve_phase_change() to actually advance
            # OLD: self._advance_phase(case_state, phase)  # REMOVED: No auto-advancement
            pass
    
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


# Convenience function for agent use
def get_case_status_message(case_state: Dict, schemas_dir: Optional[Path] = None) -> str:
    """Get a formatted status message for a case."""
    sm = StateMachine(schemas_dir)
    status = sm.get_case_status(case_state)
    return sm.format_status_for_agent(status)
