#!/usr/bin/env python3
"""
Workflow State Computer

Derives workflow state from existing case data without requiring manual state tracking.
The agent sees the state but doesn't manipulate it directly - state is computed from data.

This module:
1. Loads case data via the CaseData adapter
2. Applies derivation rules to determine workflow completion
3. Identifies blockers (external waits, user actions needed)
4. Suggests next actions with linked skills/tools
5. Formats everything for agent-friendly injection

Usage:
    from roscoe.core.workflow_state_computer import compute_workflow_state
    
    state = compute_workflow_state("Smith-MVA-01-15-2024")
    print(state["formatted_status"])  # Markdown for agent prompt
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

# Get workspace path from environment (production) or fall back to local
# Production VM: /mnt/workspace (GCS bucket)
# Docker container: /app/workspace_paralegal (mounted from /mnt/workspace)
# Local dev: /Volumes/X10 Pro/Roscoe/workspace_paralegal
workspace_path = Path(os.environ.get("WORKSPACE_DIR", os.environ.get("WORKSPACE_ROOT", "/Volumes/X10 Pro/Roscoe/workspace_paralegal")))

# Add Tools directory to Python path for imports
if str(workspace_path / "Tools") not in sys.path:
    sys.path.insert(0, str(workspace_path / "Tools"))

try:
    from _adapters.case_data import CaseData
except ImportError:
    # Fallback for when running from different context
    CaseData = None


@dataclass
class WorkflowStatus:
    """Status of a single workflow."""
    workflow_id: str
    name: str
    phase: str
    status: str  # complete, in_progress, pending, blocked, not_applicable
    completion_pct: float = 0.0
    details: str = ""
    linked_skill: Optional[str] = None
    linked_tool: Optional[str] = None
    linked_checklist: Optional[str] = None
    linked_template: Optional[str] = None


@dataclass
class Blocker:
    """Something blocking progress."""
    blocker_id: str
    blocker_type: str  # external, user, agent
    message: str
    action: Optional[str] = None
    entity: Optional[str] = None  # provider name, insurer name, etc.
    days_waiting: int = 0
    overdue: bool = False


@dataclass
class NextAction:
    """A suggested next action."""
    action_id: str
    owner: str  # agent, user
    message: str
    workflow: Optional[str] = None
    skill: Optional[str] = None
    tool: Optional[str] = None
    checklist: Optional[str] = None
    template: Optional[str] = None
    priority: int = 0  # Lower = higher priority


@dataclass
class WorkflowState:
    """Complete workflow state for a case."""
    project_name: str
    client_name: str
    current_phase: str
    phase_progress: float
    sol_status: Dict
    completed_workflows: List[WorkflowStatus]
    in_progress_workflows: List[WorkflowStatus]
    pending_workflows: List[WorkflowStatus]
    blockers: List[Blocker]
    next_actions: List[NextAction]
    summary: Dict
    formatted_status: str = ""


def load_derivation_rules() -> Dict:
    """Load derivation rules from JSON."""
    rules_path = workspace_path / "workflow_engine" / "schemas" / "derivation_rules.json"
    if rules_path.exists():
        with open(rules_path, 'r') as f:
            return json.load(f)
    return {}


def load_skills_manifest() -> Dict:
    """Load skills manifest for linking."""
    manifest_path = workspace_path / "Skills" / "skills_manifest.json"
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            return json.load(f)
    return {"skills": []}


def days_since(date_str: Optional[str]) -> int:
    """Calculate days since a date."""
    if not date_str:
        return 999
    try:
        date = datetime.fromisoformat(date_str[:10])
        return (datetime.now() - date).days
    except:
        return 999


def days_until(date_str: Optional[str]) -> int:
    """Calculate days until a date."""
    if not date_str:
        return 999
    try:
        date = datetime.fromisoformat(date_str[:10])
        return (date - datetime.now()).days
    except:
        return 999


def compute_sol_status(overview: Dict, rules: Dict, litigation_data: Optional[Dict] = None) -> Dict:
    """Compute statute of limitations status.
    
    Args:
        overview: Case overview data
        rules: Derivation rules for SOL thresholds
        litigation_data: Optional litigation data to check for complaint filing
        
    Returns:
        Dict with status, message, and relevant dates
    """
    # Check if complaint has been filed - SOL is fulfilled once complaint is filed
    if litigation_data and litigation_data.get("complaint_filed_date"):
        complaint_date = litigation_data.get("complaint_filed_date")
        if complaint_date:  # Ensure it's not None or empty string
            return {
                "status": "fulfilled",
                "message": f"SOL fulfilled - Complaint filed on {complaint_date}",
                "complaint_filed_date": complaint_date,
                "days_remaining": None,
                "sol_date": None
            }
    
    # Continue with normal SOL calculation if no complaint filed
    accident_date = overview.get("accident_date")
    if not accident_date:
        return {"status": "unknown", "message": "No accident date recorded"}
    
    # Determine case type for SOL
    project_name = overview.get("project_name", "").lower()
    sol_config = rules.get("sol_tracking", {})
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
        
        # Determine status
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
            "message": f"{days_remaining} days remaining ({status})"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def derive_phase(case_data: CaseData, overview: Dict) -> Tuple[str, float]:
    """Derive current phase and progress from data."""
    # First check if phase is explicitly set in overview
    explicit_phase = overview.get("phase", "").lower().replace(" ", "_")
    
    phase_map = {
        "file_setup": "file_setup",
        "treatment": "treatment",
        "demand_in_progress": "demand_in_progress",
        "demand": "demand_in_progress",
        "negotiation": "negotiation",
        "settlement": "settlement",
        "litigation": "litigation",
        "closed": "closed"
    }
    
    if explicit_phase in phase_map:
        return phase_map[explicit_phase], 0.0
    
    # Derive from data
    bi_claims = case_data.bi_claims
    providers = case_data.medical_providers
    
    # Check for settlement
    for claim in case_data.insurance_claims:
        if claim.get("settlement_amount"):
            return "settlement", 75.0
    
    # Check for active negotiation
    for claim in bi_claims:
        if claim.get("current_offer") or claim.get("is_active_negotiation"):
            return "negotiation", 50.0
    
    # Check for demand sent
    for claim in bi_claims:
        if claim.get("date_demand_sent"):
            return "demand_sent", 40.0
    
    # Check if all providers complete (ready for demand)
    if providers:
        all_complete = all(p.get("date_treatment_completed") for p in providers)
        all_records = all(p.get("date_medical_records_received") for p in providers)
        if all_complete and all_records:
            return "demand_in_progress", 30.0
    
    # Check for active treatment
    if providers:
        return "treatment", 20.0
    
    # Check for insurance claims opened
    if case_data.insurance_claims:
        return "file_setup", 10.0
    
    return "file_setup", 0.0


def load_litigation_data(project_name: str) -> Optional[Dict]:
    """Load litigation data for a case.
    
    Checks both:
    1. Project-specific litigation.json file
    2. Centralized Database/litigation.json
    """
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


def derive_litigation_workflows(litigation_data: Dict) -> Dict[str, WorkflowStatus]:
    """Derive litigation-specific workflows from litigation.json."""
    workflows = {}

    if not litigation_data:
        return workflows

    # === COMPLAINT FILED ===
    if litigation_data.get("complaint_filed_date"):
        case_number = litigation_data.get("case_number", "")
        court = litigation_data.get("court", "")
        workflows["file_complaint"] = WorkflowStatus(
            workflow_id="file_complaint",
            name="File Complaint",
            phase="litigation",
            status="complete",
            completion_pct=100.0,
            details=f"Case #{case_number} in {court}" if case_number else "Complaint filed",
            linked_checklist="/workflow_engine/workflows/phase_6_litigation/file_complaint.md",
            linked_skill="/Skills/litigation-pleadings/complaint-drafting-skill.md"
        )

    # === DISCOVERY PROPOUNDED ===
    if litigation_data.get("interrogatories_sent_to_defendant_date"):
        workflows["propound_discovery"] = WorkflowStatus(
            workflow_id="propound_discovery",
            name="Propound Discovery",
            phase="discovery",
            status="complete",
            completion_pct=100.0,
            details=f"Discovery sent {litigation_data['interrogatories_sent_to_defendant_date']}",
            linked_checklist="/workflow_engine/workflows/phase_6_litigation/propound_discovery.md",
            linked_skill="/Skills/litigation-discovery/propound-discovery-skill.md"
        )

    # === DISCOVERY RESPONSES (Defendant to Plaintiff) ===
    if litigation_data.get("interrogatories_received_from_defendant_date"):
        reply_date = litigation_data.get("plaintiff_reply_to_interrogatories_date")
        if reply_date:
            workflows["respond_to_discovery"] = WorkflowStatus(
                workflow_id="respond_to_discovery",
                name="Respond to Discovery",
                phase="discovery",
                status="complete",
                completion_pct=100.0,
                details=f"Responses filed {reply_date}",
                linked_skill="/Skills/litigation-discovery/respond-to-discovery-skill.md"
            )
        else:
            workflows["respond_to_discovery"] = WorkflowStatus(
                workflow_id="respond_to_discovery",
                name="Respond to Discovery",
                phase="discovery",
                status="in_progress",
                completion_pct=50.0,
                details="Awaiting plaintiff responses",
                linked_checklist="/workflow_engine/workflows/phase_6_litigation/respond_to_discovery.md",
                linked_skill="/Skills/litigation-discovery/respond-to-discovery-skill.md"
            )

    # === CLIENT DEPOSITION ===
    if litigation_data.get("plaintiff_deposition_date"):
        workflows["client_deposition"] = WorkflowStatus(
            workflow_id="client_deposition",
            name="Client Deposition",
            phase="discovery",
            status="complete",
            completion_pct=100.0,
            details=f"Deposed on {litigation_data['plaintiff_deposition_date']}",
            linked_skill="/Skills/litigation-depositions/defend-client-skill.md"
        )

    # === MEDIATION ===
    if litigation_data.get("mediation_date"):
        if litigation_data.get("mediation_completed"):
            result = litigation_data.get("mediation_result", "unknown")
            workflows["mediation"] = WorkflowStatus(
                workflow_id="mediation",
                name="Mediation",
                phase="mediation",
                status="complete",
                completion_pct=100.0,
                details=f"Mediation {litigation_data['mediation_date']} - Result: {result}"
            )
        else:
            workflows["mediation"] = WorkflowStatus(
                workflow_id="mediation",
                name="Mediation",
                phase="mediation",
                status="pending",
                details=f"Scheduled for {litigation_data['mediation_date']}"
            )

    # === TRIAL ===
    if litigation_data.get("trial_date"):
        days_to_trial = days_until(litigation_data["trial_date"])
        if days_to_trial > 0:
            workflows["trial_preparation"] = WorkflowStatus(
                workflow_id="trial_preparation",
                name="Trial Preparation",
                phase="trial_prep",
                status="in_progress",
                completion_pct=max(0, 100 - (days_to_trial / 90 * 100)),  # Assume 90 day prep period
                details=f"Trial in {days_to_trial} days ({litigation_data['trial_date']})",
                linked_skill="/Skills/litigation-trial/trial-support-skill.md"
            )
        else:
            workflows["trial_occurred"] = WorkflowStatus(
                workflow_id="trial_occurred",
                name="Trial",
                phase="trial",
                status="complete",
                completion_pct=100.0,
                details=f"Trial date: {litigation_data['trial_date']}"
            )

    return workflows


def derive_workflow_completions(case_data: CaseData, rules: Dict) -> Dict[str, WorkflowStatus]:
    """Derive completion status for all workflows."""
    workflows = {}
    overview = case_data.overview

    # === LITIGATION WORKFLOWS ===
    # Check if case is in litigation phase (from case_overview.json)
    current_phase = overview.get("phase", "").strip().lower().replace(" ", "_")
    if current_phase == "litigation":
        litigation_data = load_litigation_data(case_data.overview.get("project_name", ""))
        if litigation_data:
            litigation_workflows = derive_litigation_workflows(litigation_data)
            workflows.update(litigation_workflows)
    
    # === INTAKE ===
    intake_complete = bool(overview.get("client_name") and overview.get("accident_date"))
    workflows["intake"] = WorkflowStatus(
        workflow_id="intake",
        name="Intake",
        phase="file_setup",
        status="complete" if intake_complete else "in_progress",
        completion_pct=100.0 if intake_complete else 50.0,
        linked_skill="/Skills/case-file-organization/skill.md"
    )
    
    # === BI CLAIM ===
    bi_claims = case_data.bi_claims
    if bi_claims:
        bi_with_claim_num = [c for c in bi_claims if c.get("claim_number")]
        if bi_with_claim_num:
            workflows["open_bi_claim"] = WorkflowStatus(
                workflow_id="open_bi_claim",
                name="Open BI Claim",
                phase="file_setup",
                status="complete",
                completion_pct=100.0,
                details=f"{bi_with_claim_num[0].get('insurance_company_name')} - Claim #{bi_with_claim_num[0].get('claim_number')}",
                linked_checklist="/workflow_engine/checklists/bi_claim_opening.md"
            )
        else:
            workflows["open_bi_claim"] = WorkflowStatus(
                workflow_id="open_bi_claim",
                name="Open BI Claim",
                phase="file_setup",
                status="in_progress",
                completion_pct=50.0,
                details=f"Insurer identified: {bi_claims[0].get('insurance_company_name')}",
                linked_skill="/Skills/police-report-analysis/skill.md",
                linked_checklist="/workflow_engine/checklists/bi_claim_opening.md"
            )
    
    # === PIP CLAIM ===
    pip_claims = case_data.pip_claims
    if pip_claims:
        pip_with_claim_num = [c for c in pip_claims if c.get("claim_number")]
        if pip_with_claim_num:
            workflows["open_pip_claim"] = WorkflowStatus(
                workflow_id="open_pip_claim",
                name="Open PIP Claim",
                phase="file_setup",
                status="complete",
                completion_pct=100.0,
                details=f"{pip_with_claim_num[0].get('insurance_company_name')} - Claim #{pip_with_claim_num[0].get('claim_number')}",
                linked_tool="/Tools/insurance/pip_waterfall.py"
            )
        else:
            workflows["open_pip_claim"] = WorkflowStatus(
                workflow_id="open_pip_claim",
                name="Open PIP Claim",
                phase="file_setup",
                status="in_progress",
                completion_pct=50.0,
                linked_tool="/Tools/insurance/pip_waterfall.py"
            )
    
    # === MEDICAL PROVIDERS ===
    providers = case_data.medical_providers
    if providers:
        active_providers = [p for p in providers if not p.get("date_treatment_completed")]
        complete_providers = [p for p in providers if p.get("date_treatment_completed")]
        
        provider_status = "complete" if not active_providers else "in_progress"
        workflows["medical_provider_setup"] = WorkflowStatus(
            workflow_id="medical_provider_setup",
            name="Medical Provider Setup",
            phase="file_setup",
            status=provider_status,
            completion_pct=100.0 if provider_status == "complete" else (len(complete_providers) / len(providers) * 100),
            details=f"{len(providers)} providers ({len(active_providers)} active, {len(complete_providers)} complete)"
        )
        
        # === RECORDS REQUESTS ===
        records_requested = [p for p in providers if p.get("date_medical_records_requested")]
        records_received = [p for p in providers if p.get("date_medical_records_received")]
        
        if records_received:
            records_pct = len(records_received) / len(providers) * 100
            records_status = "complete" if len(records_received) == len(providers) else "in_progress"
        elif records_requested:
            records_pct = len(records_requested) / len(providers) * 50
            records_status = "in_progress"
        else:
            records_pct = 0
            records_status = "pending"
        
        workflows["request_records_bills"] = WorkflowStatus(
            workflow_id="request_records_bills",
            name="Request Records & Bills",
            phase="treatment",
            status=records_status,
            completion_pct=records_pct,
            details=f"Records: {len(records_received)}/{len(providers)} received",
            linked_template="/forms/medical_requests/medical_records_request_TEMPLATE.md",
            linked_checklist="/workflow_engine/checklists/medical_records_request.md"
        )
    
    # === CLIENT CHECK-IN ===
    notes = case_data.notes
    last_checkin = None
    for note in notes[:20]:  # Check recent notes
        note_content = note.get("note") or ""
        note_type = note.get("note_type") or ""
        note_text = (note_content + " " + note_type).lower()
        if "check" in note_text or "spoke with client" in note_text or "client update" in note_text:
            last_checkin = note.get("last_activity")
            break
    
    checkin_days = days_since(last_checkin) if last_checkin else 999
    checkin_status = "current" if checkin_days <= 14 else "overdue"
    workflows["client_check_in"] = WorkflowStatus(
        workflow_id="client_check_in",
        name="Client Check-In",
        phase="treatment",
        status=checkin_status,
        details=f"Last contact: {checkin_days} days ago" if checkin_days < 999 else "No recent contact recorded",
        linked_tool="/Tools/client/checkin_tracker.py",
        linked_checklist="/workflow_engine/checklists/client_checkin.md"
    )
    
    # === LIENS ===
    liens = case_data.liens
    if liens:
        liens_with_amounts = [l for l in liens if l.get("final_lien_amount")]
        workflows["lien_identification"] = WorkflowStatus(
            workflow_id="lien_identification",
            name="Lien Identification",
            phase="treatment",
            status="complete" if liens_with_amounts else "in_progress",
            completion_pct=len(liens_with_amounts) / len(liens) * 100 if liens else 0,
            details=f"{len(liens)} liens identified, {len(liens_with_amounts)} with final amounts",
            linked_template="/forms/liens/final_lien_request_TEMPLATE.md"
        )
    
    # === DEMAND ===
    bi_with_demand = [c for c in bi_claims if c.get("date_demand_sent")] if bi_claims else []
    if bi_with_demand:
        demand_days = days_since(bi_with_demand[0].get("date_demand_sent"))
        workflows["send_demand"] = WorkflowStatus(
            workflow_id="send_demand",
            name="Send Demand",
            phase="demand_in_progress",
            status="complete",
            completion_pct=100.0,
            details=f"Demand sent {demand_days} days ago",
            linked_checklist="/workflow_engine/checklists/demand_tracking.md"
        )
    
    # === NEGOTIATION ===
    active_neg = case_data.active_negotiation()
    if active_neg:
        offer = active_neg.get("current_offer")
        workflows["bi_negotiation"] = WorkflowStatus(
            workflow_id="bi_negotiation",
            name="BI Negotiation",
            phase="negotiation",
            status="in_progress",
            details=f"Current offer: ${offer:,.2f}" if offer else "Awaiting response",
            linked_tool="/Tools/negotiation/negotiation_tracker.py"
        )
    
    # === SETTLEMENT ===
    settled_claims = [c for c in case_data.insurance_claims if c.get("settlement_amount")]
    if settled_claims:
        total_settlement = sum(c.get("settlement_amount", 0) for c in settled_claims)
        workflows["settlement_processing"] = WorkflowStatus(
            workflow_id="settlement_processing",
            name="Settlement Processing",
            phase="settlement",
            status="complete" if settled_claims[0].get("settlement_date") else "in_progress",
            details=f"Settlement: ${total_settlement:,.2f}",
            linked_tool="/Tools/settlement/settlement_calculator.py",
            linked_checklist="/workflow_engine/checklists/release_processing.md"
        )
    
    return workflows


def derive_blockers(case_data: CaseData, workflows: Dict[str, WorkflowStatus]) -> List[Blocker]:
    """Identify blockers preventing progress."""
    blockers = []
    
    # Check for overdue records
    for provider in case_data.medical_providers:
        requested = provider.get("date_medical_records_requested")
        received = provider.get("date_medical_records_received")
        
        if requested and not received:
            days = days_since(requested)
            if days > 21:
                blockers.append(Blocker(
                    blocker_id="waiting_medical_records",
                    blocker_type="external",
                    message=f"Waiting on medical records from {provider.get('provider_full_name')}",
                    action=f"Follow up with {provider.get('provider_full_name')}",
                    entity=provider.get("provider_full_name"),
                    days_waiting=days,
                    overdue=True
                ))
    
    # Check for overdue bills
    for provider in case_data.medical_providers:
        requested = provider.get("date_medical_bills_requested")
        received = provider.get("medical_bills_received_date")
        
        if requested and not received:
            days = days_since(requested)
            if days > 21:
                blockers.append(Blocker(
                    blocker_id="waiting_medical_bills",
                    blocker_type="external",
                    message=f"Waiting on medical bills from {provider.get('provider_full_name')}",
                    entity=provider.get("provider_full_name"),
                    days_waiting=days,
                    overdue=True
                ))
    
    # Check for client check-in overdue
    checkin_workflow = workflows.get("client_check_in")
    if checkin_workflow and checkin_workflow.status == "overdue":
        blockers.append(Blocker(
            blocker_id="client_checkin_overdue",
            blocker_type="user",
            message="Client check-in is overdue",
            action="Schedule client check-in"
        ))
    
    # Check for active treatment blocking demand
    active_providers = [p for p in case_data.medical_providers if not p.get("date_treatment_completed")]
    if active_providers and workflows.get("send_demand") is None:
        blockers.append(Blocker(
            blocker_id="treatment_in_progress",
            blocker_type="external",
            message=f"Client still treating with {len(active_providers)} provider(s)",
            action="Continue monitoring treatment progress"
        ))
    
    # Check for demand response pending
    for claim in case_data.bi_claims:
        demand_sent = claim.get("date_demand_sent")
        current_offer = claim.get("current_offer")
        
        if demand_sent and not current_offer:
            days = days_since(demand_sent)
            if days < 45:
                blockers.append(Blocker(
                    blocker_id="demand_response_pending",
                    blocker_type="external",
                    message=f"Awaiting response to demand sent {days} days ago",
                    entity=claim.get("insurance_company_name"),
                    days_waiting=days
                ))
    
    return blockers


def derive_next_actions(case_data: CaseData, workflows: Dict[str, WorkflowStatus], 
                         blockers: List[Blocker], current_phase: str) -> List[NextAction]:
    """Determine next actions based on current state."""
    actions = []
    
    # Priority 1: Unblock user actions
    for blocker in blockers:
        if blocker.blocker_type == "user":
            actions.append(NextAction(
                action_id=f"unblock_{blocker.blocker_id}",
                owner="user",
                message=blocker.action or blocker.message,
                priority=1
            ))
    
    # Priority 2: Follow up on overdue external blockers
    for blocker in blockers:
        if blocker.blocker_type == "external" and blocker.overdue:
            actions.append(NextAction(
                action_id=f"follow_up_{blocker.blocker_id}",
                owner="user",
                message=f"Follow up: {blocker.message} (overdue by {blocker.days_waiting - 21} days)",
                priority=2
            ))
    
    # Priority 3: In-progress workflow actions
    for wf_id, workflow in workflows.items():
        if workflow.status == "in_progress":
            if wf_id == "open_bi_claim" and not any(c.get("claim_number") for c in case_data.bi_claims):
                actions.append(NextAction(
                    action_id="complete_bi_claim",
                    owner="user",
                    message="Open BI claim - get claim number and adjuster info",
                    workflow="open_insurance_claims",
                    checklist="/workflow_engine/checklists/bi_claim_opening.md",
                    priority=3
                ))
            
            if wf_id == "request_records_bills":
                pending_providers = [p for p in case_data.medical_providers 
                                     if not p.get("date_medical_records_requested")]
                if pending_providers:
                    actions.append(NextAction(
                        action_id="send_records_request",
                        owner="agent",
                        message=f"Send medical records request to {pending_providers[0].get('provider_full_name')}",
                        workflow="request_records_bills",
                        template="/forms/medical_requests/medical_records_request_TEMPLATE.md",
                        priority=3
                    ))
    
    # Priority 4: Start next workflows
    if current_phase == "file_setup":
        if "open_bi_claim" not in workflows and case_data.bi_claims:
            actions.append(NextAction(
                action_id="start_bi_claim",
                owner="user",
                message="Open BI claim with at-fault insurer",
                workflow="open_insurance_claims",
                skill="/Skills/police-report-analysis/skill.md",
                priority=4
            ))
    
    if current_phase in ["treatment", "demand_in_progress"]:
        # Check if ready for demand
        all_complete = all(p.get("date_treatment_completed") for p in case_data.medical_providers)
        all_records = all(p.get("date_medical_records_received") for p in case_data.medical_providers)
        
        if all_complete and all_records and "send_demand" not in workflows:
            actions.append(NextAction(
                action_id="prepare_demand",
                owner="agent",
                message="Prepare demand package - all records received",
                workflow="gather_demand_materials",
                skill="/Skills/medical-chronology/skill.md",
                priority=4
            ))
    
    # Sort by priority
    actions.sort(key=lambda x: x.priority)
    return actions


def format_workflow_status(state: WorkflowState) -> str:
    """Format workflow state as markdown for agent injection."""
    lines = []
    
    # Header
    lines.append(f"## Workflow Status: {state.client_name}")
    lines.append("")
    
    # Phase and SOL
    lines.append(f"**Phase**: {state.current_phase.replace('_', ' ').title()} ({state.phase_progress:.0f}% complete)")
    
    sol = state.sol_status
    if sol.get("status") == "fulfilled":
        lines.append(f"**SOL**: ✅ Fulfilled - {sol.get('message', 'Complaint filed')}")
    elif sol.get("days_remaining") is not None:
        status_emoji = {"safe": "", "attention": "⚠️", "urgent": "⚠️", "critical": "🚨"}.get(sol.get("status"), "")
        lines.append(f"**SOL**: {sol.get('days_remaining')} days remaining {status_emoji}")
    lines.append("")
    
    # Active/In-Progress Workflows
    if state.in_progress_workflows:
        lines.append("### Active Workflows")
        for wf in state.in_progress_workflows:
            lines.append(f"**{wf.name}**")
            if wf.details:
                lines.append(f"- {wf.details}")
            if wf.linked_skill:
                lines.append(f"- Skill: `{wf.linked_skill}`")
            if wf.linked_tool:
                lines.append(f"- Tool: `{wf.linked_tool}`")
            if wf.linked_checklist:
                lines.append(f"- Checklist: `{wf.linked_checklist}`")
            lines.append("")
    
    # Blockers
    if state.blockers:
        lines.append("### Blockers")
        for blocker in state.blockers:
            prefix = {"external": "[external]", "user": "[user action]", "agent": "[agent]"}.get(blocker.blocker_type, "")
            overdue_note = " (OVERDUE)" if blocker.overdue else ""
            lines.append(f"- {prefix} {blocker.message}{overdue_note}")
            if blocker.action:
                lines.append(f"  - Action: {blocker.action}")
        lines.append("")
    
    # Completed Workflows
    if state.completed_workflows:
        lines.append("### Completed")
        for wf in state.completed_workflows:
            detail = f" - {wf.details}" if wf.details else ""
            lines.append(f"- {wf.name}{detail}")
        lines.append("")
    
    # Next Actions
    if state.next_actions:
        lines.append("### Next Actions")
        for action in state.next_actions[:5]:  # Limit to top 5
            owner_prefix = "[agent]" if action.owner == "agent" else "[user]"
            lines.append(f"- {owner_prefix} {action.message}")
            if action.skill:
                lines.append(f"  - Skill: `{action.skill}`")
            if action.tool:
                lines.append(f"  - Tool: `{action.tool}`")
            if action.checklist:
                lines.append(f"  - Checklist: `{action.checklist}`")
        lines.append("")
    
    return "\n".join(lines)


def compute_workflow_state(project_name: str) -> WorkflowState:
    """
    Main entry point: Compute complete workflow state for a case.
    
    Args:
        project_name: The case/project name (e.g., "Smith-MVA-01-15-2024")
    
    Returns:
        WorkflowState object with all computed state and formatted status
    """
    # Load data
    if CaseData is None:
        raise ImportError("CaseData adapter not available")
    
    case_data = CaseData(project_name)
    rules = load_derivation_rules()
    
    # Derive phase
    current_phase, phase_progress = derive_phase(case_data, case_data.overview)
    
    # Load litigation data for SOL check (complaint filing fulfills SOL)
    litigation_data = load_litigation_data(project_name)
    
    # Compute SOL (check if complaint filed first)
    sol_status = compute_sol_status(case_data.overview, rules, litigation_data)
    
    # Derive workflow completions
    workflows = derive_workflow_completions(case_data, rules)
    
    # Categorize workflows
    completed = [wf for wf in workflows.values() if wf.status == "complete"]
    in_progress = [wf for wf in workflows.values() if wf.status in ["in_progress", "overdue"]]
    pending = [wf for wf in workflows.values() if wf.status == "pending"]
    
    # Derive blockers
    blockers = derive_blockers(case_data, workflows)
    
    # Derive next actions
    next_actions = derive_next_actions(case_data, workflows, blockers, current_phase)
    
    # Build state object
    state = WorkflowState(
        project_name=project_name,
        client_name=case_data.client_name,
        current_phase=current_phase,
        phase_progress=phase_progress,
        sol_status=sol_status,
        completed_workflows=completed,
        in_progress_workflows=in_progress,
        pending_workflows=pending,
        blockers=blockers,
        next_actions=next_actions,
        summary=case_data.summary()
    )
    
    # Format for agent
    state.formatted_status = format_workflow_status(state)
    
    return state


def main():
    """CLI for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compute workflow state for a case")
    parser.add_argument("--case", "-c", required=True, help="Case/project name")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print")
    
    args = parser.parse_args()
    
    try:
        state = compute_workflow_state(args.case)
        
        if args.json:
            output = {
                "project_name": state.project_name,
                "client_name": state.client_name,
                "current_phase": state.current_phase,
                "phase_progress": state.phase_progress,
                "sol_status": state.sol_status,
                "completed_workflows": [w.workflow_id for w in state.completed_workflows],
                "in_progress_workflows": [w.workflow_id for w in state.in_progress_workflows],
                "blockers": [{"id": b.blocker_id, "message": b.message} for b in state.blockers],
                "next_actions": [{"id": a.action_id, "owner": a.owner, "message": a.message} for a in state.next_actions],
                "summary": state.summary
            }
            print(json.dumps(output, indent=2 if args.pretty else None))
        else:
            print(state.formatted_status)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

