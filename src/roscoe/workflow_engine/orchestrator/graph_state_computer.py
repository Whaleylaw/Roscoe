"""
Graph-Based Workflow State Computer (Deterministic Model)

Computes workflow state by querying the Graphiti knowledge graph using
EXPLICIT state stored in the graph, not inference.

State is stored as:
- Case -[IN_PHASE]-> Phase  (current phase)
- Case -[HAS_STATUS]-> LandmarkStatus -[FOR_LANDMARK]-> Landmark  (versioned landmark status)

This replaces the inference-based approach with deterministic queries.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class DerivedWorkflowState(BaseModel):
    """Workflow state derived from deterministic graph queries."""
    case_id: str
    client_name: str
    current_phase: str
    phase_display_name: str
    phase_track: str
    phase_entered_at: Optional[str] = None

    # Phase advancement
    next_phase: Optional[str] = None
    can_advance: bool
    blocking_landmarks: List[Dict] = Field(default_factory=list)

    # Landmark statuses
    landmarks_by_phase: Dict[str, List[Dict]] = Field(default_factory=dict)
    current_phase_landmarks: List[Dict] = Field(default_factory=list)
    landmarks_complete: int
    landmarks_total: int

    # Suggested next actions
    workflows_needed: List[Dict] = Field(default_factory=list)

    # Case data
    accident_date: Optional[str] = None
    accident_type: str
    insurance_claims: List[Dict] = Field(default_factory=list)
    medical_providers: List[Dict] = Field(default_factory=list)
    liens: List[Dict] = Field(default_factory=list)

    # Deadlines
    statute_of_limitations: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for injection into agent context."""
        return {
            "case_id": self.case_id,
            "client": {"name": self.client_name},
            "accident": {
                "date": self.accident_date,
                "type": self.accident_type,
            },
            "current_phase": {
                "name": self.current_phase,
                "display_name": self.phase_display_name,
                "track": self.phase_track,
                "entered_at": self.phase_entered_at,
            },
            "next_phase": self.next_phase,
            "can_advance": self.can_advance,
            "blocking_landmarks": self.blocking_landmarks,
            "landmarks": {
                "by_phase": self.landmarks_by_phase,
                "current_phase": self.current_phase_landmarks,
                "complete": self.landmarks_complete,
                "total": self.landmarks_total,
            },
            "workflows_needed": self.workflows_needed,
            "insurance_claims": self.insurance_claims,
            "medical_providers": self.medical_providers,
            "liens": self.liens,
            "statute_of_limitations": self.statute_of_limitations,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    def format_for_prompt(self) -> str:
        """Format state as markdown for LLM prompt injection."""
        lines = [f"## Workflow State: {self.case_id}"]
        lines.append("")
        lines.append(f"**Client:** {self.client_name}")
        lines.append(f"**Current Phase:** {self.phase_display_name} ({self.current_phase})")
        lines.append(f"**Phase Track:** {self.phase_track}")
        
        if self.phase_entered_at:
            lines.append(f"**Entered Phase:** {self.phase_entered_at[:10]}")
        
        lines.append("")
        lines.append(f"### Phase Progress: {self.landmarks_complete}/{self.landmarks_total} landmarks complete")
        
        if not self.can_advance:
            lines.append("")
            lines.append("**⚠️ Cannot advance to next phase**")
            if self.blocking_landmarks:
                lines.append("Blocking landmarks (hard blockers):")
                for lm in self.blocking_landmarks:
                    lines.append(f"  - {lm.get('display_name', lm.get('landmark_id'))}: {lm.get('current_status', 'incomplete')}")
        else:
            lines.append("")
            lines.append(f"**✓ Ready to advance to:** {self.next_phase}")
        
        if self.workflows_needed:
            lines.append("")
            lines.append("### Suggested Actions")
            for wf in self.workflows_needed[:3]:
                lm = wf.get("landmark_display", wf.get("landmark"))
                for w in wf.get("workflows", [])[:1]:
                    lines.append(f"- To complete **{lm}**: Run workflow `{w.get('workflow_name')}`")
        
        if self.statute_of_limitations:
            sol = self.statute_of_limitations
            sol_status = sol.get("status", "unknown")
            lines.append("")
            lines.append(f"### Statute of Limitations")

            # Handle special statuses first
            if sol_status == "filed":
                lines.append("**✅ FILED** - Complaint has been filed")
                if sol.get("complaint_filed_date"):
                    lines.append(f"**Filed Date:** {sol['complaint_filed_date']}")
                if sol.get("notes"):
                    lines.append(f"**Notes:** {sol['notes']}")
            elif sol_status == "tolled":
                lines.append("**⏸️ TOLLED** - Statute is paused")
                if sol.get("notes"):
                    lines.append(f"**Reason:** {sol['notes']}")
            elif sol_status == "n/a":
                lines.append("**ℹ️ N/A** - Statute does not apply")
                if sol.get("notes"):
                    lines.append(f"**Notes:** {sol['notes']}")
            else:
                # Standard deadline tracking
                lines.append(f"**Deadline:** {sol.get('deadline', 'Unknown')}")
                lines.append(f"**Days Remaining:** {sol.get('days_remaining', 'Unknown')}")
                if sol_status == "critical":
                    lines.append("**🔴 CRITICAL - Under 60 days remaining!**")
                elif sol_status == "warning":
                    lines.append("**🟡 Warning - Under 180 days remaining**")
        
        return "\n".join(lines)


class GraphWorkflowStateComputer:
    """
    Computes workflow state from EXPLICIT graph relationships.

    This uses the deterministic model where state is stored as:
    - Case -[IN_PHASE]-> Phase
    - Case -[HAS_STATUS]-> LandmarkStatus -[FOR_LANDMARK]-> Landmark

    LandmarkStatus nodes are versioned entities with archived_at timestamps for audit trail.
    No inference is performed - the graph IS the source of truth.

    Usage:
        computer = GraphWorkflowStateComputer()
        state = await computer.compute_state("Caryn-McCay-MVA-7-30-2023")

        # Format for agent prompt
        prompt_text = state.format_for_prompt()
    """
    
    async def compute_state(self, case_name: str) -> DerivedWorkflowState:
        """
        Compute the workflow state for a case from explicit graph relationships.

        Args:
            case_name: The case folder name

        Returns:
            DerivedWorkflowState with all relevant case and workflow data
        """
        # Always get client and case info first (basic data)
        client_info = await self._get_client_info(case_name)
        case_info = await self._get_case_info(case_name)

        # Try to get workflow state from graph
        try:
            from roscoe.core.graphiti_client import get_case_workflow_state
            state = await get_case_workflow_state(case_name)
        except Exception as e:
            # Workflow state not available - default to Phase 0
            state = {"error": f"Workflow state not initialized: {str(e)}"}

        if state.get("error"):
            # No workflow state - create default Phase 0 state with client info
            return await self._create_default_phase_0_state(case_name, client_info, case_info)

        # Get additional case data
        insurance = await self._get_insurance_claims(case_name)
        providers = await self._get_medical_providers(case_name)
        liens = await self._get_liens(case_name)
        
        # Extract phase info
        current_phase = state.get("current_phase", {})
        
        # Get landmark data
        current_phase_landmarks = state.get("current_phase_landmarks", {})
        landmarks_list = current_phase_landmarks.get("landmarks", [])
        
        # Calculate SOL (respects stored status overrides)
        sol = self._calculate_sol(
            case_info.get("accident_date"),
            case_info.get("accident_type", "mva"),
            sol_status=case_info.get("sol_status"),
            complaint_filed_date=case_info.get("complaint_filed_date"),
            sol_notes=case_info.get("sol_notes")
        )

        return DerivedWorkflowState(
            case_id=case_name,
            client_name=client_info.get("name", "Unknown"),
            current_phase=current_phase.get("name", "file_setup"),
            phase_display_name=current_phase.get("display_name", "File Setup"),
            phase_track=current_phase.get("track", "pre_litigation"),
            phase_entered_at=current_phase.get("entered_at"),
            next_phase=state.get("next_phase"),
            can_advance=state.get("can_advance", False),
            blocking_landmarks=state.get("blocking_landmarks", []),
            landmarks_by_phase=state.get("landmarks_by_phase", {}),
            current_phase_landmarks=landmarks_list,
            landmarks_complete=current_phase_landmarks.get("complete", 0),
            landmarks_total=current_phase_landmarks.get("total", 0),
            workflows_needed=state.get("workflows_needed", []),
            accident_date=case_info.get("accident_date"),
            accident_type=case_info.get("accident_type", "mva"),
            insurance_claims=insurance,
            medical_providers=providers,
            liens=liens,
            statute_of_limitations=sol,
            created_at=case_info.get("created_at", datetime.now().isoformat()),
            updated_at=datetime.now().isoformat(),
        )
    
    async def _create_default_phase_0_state(
        self,
        case_name: str,
        client_info: Dict[str, Any],
        case_info: Dict[str, Any]
    ) -> DerivedWorkflowState:
        """
        Create default Phase 0 (Onboarding) state when workflow not initialized.

        Uses actual client/case data from graph, defaults to Phase 0.
        Gets Phase 0 landmark definitions from graph even though case has no status nodes.
        """
        # Get additional case data even without workflow state
        insurance = await self._get_insurance_claims(case_name)
        providers = await self._get_medical_providers(case_name)
        liens = await self._get_liens(case_name)

        # Get Phase 0 landmark definitions from graph (even if case has no status for them)
        phase_0_landmarks = []
        try:
            from roscoe.core.graphiti_client import get_phase_landmarks

            # Graph uses "onboarding" not "phase_0_onboarding"
            landmarks_def = await get_phase_landmarks("onboarding")

            # Format landmarks as "incomplete" since case has no status nodes
            for lm in landmarks_def:
                phase_0_landmarks.append({
                    "landmark_id": lm.get("landmark_id"),
                    "display_name": lm.get("name") or lm.get("display_name"),
                    "status": "incomplete",
                    "is_hard_blocker": lm.get("mandatory", False),
                    "description": lm.get("description"),
                })
        except Exception as e:
            # If we can't get landmark definitions, that's okay
            # Case can still be in Phase 0 with no defined landmarks
            pass

        landmarks_complete = 0
        landmarks_total = len(phase_0_landmarks)

        # Calculate SOL (respects stored status overrides)
        sol = self._calculate_sol(
            case_info.get("accident_date"),
            case_info.get("accident_type", "mva"),
            sol_status=case_info.get("sol_status"),
            complaint_filed_date=case_info.get("complaint_filed_date"),
            sol_notes=case_info.get("sol_notes")
        )

        return DerivedWorkflowState(
            case_id=case_name,
            client_name=client_info.get("name", "Unknown"),
            current_phase="onboarding",  # Match graph schema
            phase_display_name="Phase 0: Onboarding",
            phase_track="pre_litigation",
            phase_entered_at=None,
            next_phase="file_setup",  # Match graph schema
            can_advance=True,  # Can always advance from Phase 0
            blocking_landmarks=[],
            landmarks_by_phase={"onboarding": phase_0_landmarks},
            current_phase_landmarks=phase_0_landmarks,
            landmarks_complete=landmarks_complete,
            landmarks_total=landmarks_total,
            workflows_needed=[],
            accident_date=case_info.get("accident_date"),
            accident_type=case_info.get("accident_type", "mva"),
            insurance_claims=insurance,
            medical_providers=providers,
            liens=liens,
            statute_of_limitations=sol,
            created_at=case_info.get("created_at", datetime.now().isoformat()),
            updated_at=datetime.now().isoformat(),
        )
    
    async def _get_case_info(self, case_name: str) -> Dict[str, Any]:
        """Query graph for case entity info including SOL status."""
        from roscoe.core.graphiti_client import run_cypher_query

        query = """
            MATCH (c:Case {name: $case_name})
            RETURN c.name as name, c.case_type as case_type, c.accident_date as accident_date,
                   c.sol_status as sol_status, c.complaint_filed_date as complaint_filed_date,
                   c.sol_notes as sol_notes
            LIMIT 1
        """
        results = await run_cypher_query(query, {"case_name": case_name})

        if results:
            r = results[0]
            # Parse accident date from case name if not in entity
            accident_date = r.get("accident_date")
            accident_type = r.get("case_type", "mva")

            if not accident_date:
                accident_date, accident_type = self._parse_case_name(case_name)

            return {
                "name": r.get("name", case_name),
                "accident_date": accident_date,
                "accident_type": accident_type,
                "sol_status": r.get("sol_status"),
                "complaint_filed_date": r.get("complaint_filed_date"),
                "sol_notes": r.get("sol_notes"),
                "created_at": datetime.now().isoformat(),
            }

        # Fallback to parsing case name
        accident_date, accident_type = self._parse_case_name(case_name)
        return {
            "name": case_name,
            "accident_date": accident_date,
            "accident_type": accident_type,
        }
    
    def _parse_case_name(self, case_name: str) -> tuple:
        """Parse accident date and type from case name."""
        parts = case_name.split("-")
        accident_date = None
        accident_type = "mva"
        
        if len(parts) >= 4:
            try:
                for i, part in enumerate(parts):
                    if part.upper() in ["MVA", "WC", "SLIP", "FALL", "PREMISE", "SF", "DB"]:
                        accident_type = part.lower()
                        if accident_type == "sf":
                            accident_type = "slip_fall"
                        elif accident_type == "db":
                            accident_type = "dog_bite"
                        
                        # Date is usually after the type: Name-MVA-M-D-YYYY
                        if i + 3 < len(parts):
                            month = parts[i + 1]
                            day = parts[i + 2]
                            year = parts[i + 3]
                            accident_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        break
            except (ValueError, IndexError):
                pass
        
        return accident_date, accident_type
    
    async def _get_client_info(self, case_name: str) -> Dict[str, Any]:
        """Query graph for client entity via HAS_CLIENT relationship."""
        from roscoe.core.graphiti_client import run_cypher_query

        query = """
            MATCH (case:Case {name: $case_name})-[:HAS_CLIENT]->(client:Client)
            RETURN client.name as name, client.phone as phone, client.email as email
            LIMIT 1
        """
        results = await run_cypher_query(query, {"case_name": case_name})
        
        if results:
            return {
                "name": results[0].get("name", "Unknown"),
                "phone": results[0].get("phone"),
                "email": results[0].get("email"),
            }
        
        # Fallback: Extract from case name
        parts = case_name.split("-")
        for i, part in enumerate(parts):
            if part.upper() in ["MVA", "WC", "SLIP", "FALL", "PREMISE", "SF", "DB"]:
                name_parts = parts[:i]
                return {"name": " ".join(name_parts)}
        
        return {"name": "Unknown"}
    
    async def _get_insurance_claims(self, case_name: str) -> List[Dict]:
        """Query graph for all insurance claims on the case using new InsurancePolicy structure."""
        from roscoe.core.graphiti_client import run_cypher_query

        query = """
            MATCH (case:Case {name: $case_name})-[:HAS_CLAIM]->(claim)
            WHERE claim:BIClaim OR claim:PIPClaim OR claim:UMClaim OR claim:UIMClaim OR claim:WCClaim
            OPTIONAL MATCH (claim)-[:UNDER_POLICY]->(policy:InsurancePolicy)
            OPTIONAL MATCH (policy)-[:WITH_INSURER]->(insurer:Insurer)
            OPTIONAL MATCH (claim)-[:HANDLED_BY]->(adjuster:Adjuster)
            RETURN claim.claim_number as claim_number,
                   labels(claim)[0] as claim_type,
                   policy.policy_number as policy_number,
                   insurer.name as insurer_name,
                   adjuster.name as adjuster_name,
                   policy.bi_limit as bi_limit,
                   policy.pip_limit as pip_limit,
                   policy.um_limit as um_limit,
                   policy.uim_limit as uim_limit,
                   claim.amount_demanded as demand_amount,
                   claim.amount_offered as current_offer,
                   claim.status as claim_status
        """
        results = await run_cypher_query(query, {"case_name": case_name})

        return [{
            "claim_number": r.get("claim_number"),
            "type": r.get("claim_type", "Unknown"),
            "policy_number": r.get("policy_number"),
            "insurer": r.get("insurer_name"),
            "adjuster": r.get("adjuster_name"),
            "bi_limit": r.get("bi_limit"),
            "pip_limit": r.get("pip_limit"),
            "um_limit": r.get("um_limit"),
            "uim_limit": r.get("uim_limit"),
            "demand_amount": r.get("demand_amount"),
            "current_offer": r.get("current_offer"),
            "status": r.get("claim_status"),
        } for r in results]
    
    async def _get_medical_providers(self, case_name: str) -> List[Dict]:
        """Query graph for medical providers on the case using new three-tier hierarchy."""
        from roscoe.core.graphiti_client import run_cypher_query

        query = """
            MATCH (case:Case {name: $case_name})-[:HAS_CLIENT]->(client:Client)-[:TREATED_AT]->(provider)
            WHERE provider:Facility OR provider:Location
            OPTIONAL MATCH (provider)-[:PART_OF]->(parent)
            WHERE parent:Facility OR parent:HealthSystem
            OPTIONAL MATCH (parent)-[:PART_OF]->(grandparent:HealthSystem)
            RETURN provider.name as name,
                   labels(provider)[0] as provider_type,
                   provider.specialty as specialty,
                   provider.phone as phone,
                   provider.address as address,
                   parent.name as parent_name,
                   labels(parent)[0] as parent_type,
                   grandparent.name as health_system
        """
        results = await run_cypher_query(query, {"case_name": case_name})

        return [{
            "name": r.get("name"),
            "type": r.get("provider_type"),
            "specialty": r.get("specialty"),
            "phone": r.get("phone"),
            "address": r.get("address"),
            "parent": r.get("parent_name"),
            "health_system": r.get("health_system") or r.get("parent_name") if r.get("parent_type") == "HealthSystem" else None,
        } for r in results]
    
    async def _get_liens(self, case_name: str) -> List[Dict]:
        """Query graph for liens on the case."""
        from roscoe.core.graphiti_client import run_cypher_query
        
        query = """
            MATCH (case:Case {name: $case_name})-[:HAS_LIEN]->(lien:Lien)
            OPTIONAL MATCH (lien)-[:HELD_BY]->(holder:LienHolder)
            RETURN lien.name as lien_name,
                   holder.name as holder_name,
                   lien.lien_type as lien_type,
                   lien.amount as amount,
                   lien.account_number as account_number
        """
        results = await run_cypher_query(query, {"case_name": case_name})
        
        return [{
            "lien_name": r.get("lien_name"),
            "holder": r.get("holder_name"),
            "lien_type": r.get("lien_type"),
            "amount": r.get("amount"),
            "account_number": r.get("account_number"),
        } for r in results]
    
    def _calculate_sol(
        self,
        accident_date: Optional[str],
        claim_type: str,
        sol_status: Optional[str] = None,
        complaint_filed_date: Optional[str] = None,
        sol_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate statute of limitations, respecting stored status overrides.

        If sol_status is set to 'filed', 'tolled', or 'n/a', returns that status
        instead of calculating days remaining.

        Args:
            accident_date: Date of accident (YYYY-MM-DD)
            claim_type: Type of case (mva, premise, slip_fall, etc.)
            sol_status: Stored status override (pending, filed, tolled, n/a)
            complaint_filed_date: Date complaint was filed if status='filed'
            sol_notes: Any notes about the SOL status
        """
        # Check for status overrides first
        if sol_status == "filed":
            return {
                "status": "filed",
                "message": f"Complaint filed on {complaint_filed_date}" if complaint_filed_date else "Complaint filed",
                "complaint_filed_date": complaint_filed_date,
                "notes": sol_notes,
            }

        if sol_status == "tolled":
            return {
                "status": "tolled",
                "message": sol_notes or "SOL tolled - see case notes",
                "notes": sol_notes,
            }

        if sol_status == "n/a":
            return {
                "status": "n/a",
                "message": sol_notes or "SOL not applicable to this case",
                "notes": sol_notes,
            }

        # Default calculation
        if not accident_date:
            return {"status": "unknown", "message": "Accident date not known"}

        try:
            accident_dt = datetime.fromisoformat(accident_date)
        except ValueError:
            return {"status": "unknown", "message": "Invalid accident date format"}

        sol_years = {
            "mva": 2,
            "premise": 1,
            "slip": 1,
            "slip_fall": 1,
            "fall": 1,
            "wc": 2,
            "dog_bite": 1,
        }.get(claim_type, 2)

        deadline = accident_dt + timedelta(days=sol_years * 365)
        days_remaining = (deadline - datetime.now()).days

        if days_remaining <= 60:
            status = "critical"
        elif days_remaining <= 180:
            status = "warning"
        else:
            status = "safe"

        return {
            "base_date": accident_date,
            "years": sol_years,
            "deadline": deadline.strftime("%Y-%m-%d"),
            "days_remaining": days_remaining,
            "status": status,
        }


# =============================================================================
# State Update Functions
# =============================================================================

async def update_landmark_status(
    case_name: str,
    landmark_id: str,
    status: str,
    sub_steps: dict = None,
    notes: str = None
) -> bool:
    """
    Update a landmark's status for a case.
    
    This is the main function for agents to mark landmarks complete.
    
    Args:
        case_name: Case name/identifier
        landmark_id: Landmark identifier (e.g., 'insurance_claims_setup')
        status: New status ('complete', 'incomplete', 'in_progress', 'not_applicable')
        sub_steps: Optional dict of sub-step completions
        notes: Optional notes about the status
    
    Returns:
        True if updated successfully
    """
    from roscoe.core.graphiti_client import update_case_landmark_status
    return await update_case_landmark_status(case_name, landmark_id, status, sub_steps, notes)


async def advance_case_phase(case_name: str, target_phase: str = None, force: bool = False) -> dict:
    """
    Advance a case to the next phase or a specific phase.
    
    Args:
        case_name: Case name/identifier
        target_phase: Optional target phase (if None, advances to next phase)
        force: If True, skip hard blocker checks (admin override)
    
    Returns:
        Dictionary with result info
    """
    from roscoe.core.graphiti_client import advance_case_to_phase, get_case_phase
    
    # If no target specified, get the next phase
    if not target_phase:
        current = await get_case_phase(case_name)
        if not current:
            return {"success": False, "error": "Case not found or no phase set"}
        target_phase = current.get("next_phase")
        if not target_phase:
            return {"success": False, "error": "No next phase defined for current phase"}
    
    return await advance_case_to_phase(case_name, target_phase, force)


# =============================================================================
# Convenience Functions
# =============================================================================

async def get_case_state_from_graph(case_name: str) -> Dict[str, Any]:
    """
    Get case state from graph in dictionary format.
    
    This is the main entry point for getting case workflow state.
    
    Args:
        case_name: Case folder name
    
    Returns:
        Dictionary with complete workflow state
    """
    computer = GraphWorkflowStateComputer()
    state = await computer.compute_state(case_name)
    return state.to_dict()


def get_case_state_from_graph_sync(case_name: str) -> Dict[str, Any]:
    """Synchronous wrapper for get_case_state_from_graph."""
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, get_case_state_from_graph(case_name))
                return future.result(timeout=60)
        else:
            return asyncio.run(get_case_state_from_graph(case_name))
    except RuntimeError:
        return asyncio.run(get_case_state_from_graph(case_name))


async def get_workflow_state_prompt(case_name: str) -> str:
    """
    Get case workflow state formatted for LLM prompt injection.
    
    Args:
        case_name: Case folder name
    
    Returns:
        Markdown-formatted string for prompt injection
    """
    computer = GraphWorkflowStateComputer()
    state = await computer.compute_state(case_name)
    return state.format_for_prompt()
