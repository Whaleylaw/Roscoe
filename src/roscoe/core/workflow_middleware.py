"""
Workflow orchestration middleware for Roscoe agent.

This middleware runs AFTER CaseContextMiddleware to inject workflow guidance
into the agent's system prompt when a case is detected.

Flow:
1. CaseContextMiddleware detects case mention, sets request.state['detected_cases']
2. WorkflowMiddleware reads detected_cases
3. Queries FalkorDB knowledge graph for workflow state via GraphWorkflowStateComputer
4. Formats guidance with next actions and resource paths
5. Injects into system prompt

The guidance includes:
- Current phase and progress
- Landmark completion status
- Blockers (hard blockers that prevent phase advancement)
- Next actions with linked skills, checklists, templates
- SOL status alerts

Data Source: FalkorDB knowledge graph ONLY (no JSON fallback)
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import logging
import asyncio

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)


class WorkflowMiddleware(AgentMiddleware):
    """
    Workflow orchestration middleware.

    Runs AFTER CaseContextMiddleware to inject workflow guidance.

    1. Check if case was detected (from request.state['detected_cases'])
    2. Query FalkorDB knowledge graph via GraphWorkflowStateComputer
    3. Format guidance with phase, landmarks, blockers, next actions
    4. Inject into system prompt

    All workflow state comes from the knowledge graph. No JSON fallback.
    """

    name: str = "workflow"
    tools: list = []

    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        logger.info(f"[WORKFLOW] Middleware initialized with workspace: {workspace_dir}")
        logger.info(f"[WORKFLOW] Using GRAPH-BASED state computation (FalkorDB)")
    
    def _process_request(self, request) -> Any:
        """
        Core processing logic - compute workflow state from graph and inject guidance.

        Shared between sync and async wrappers.
        """
        # Get detected cases from request state (set by CaseContextMiddleware)
        detected_cases = []
        if request.state:
            detected_cases = request.state.get('detected_cases', [])

        if not detected_cases:
            logger.debug("[WORKFLOW] No detected cases, skipping workflow injection")
            return request

        # Get first detected case
        case_info = detected_cases[0]
        project_name = case_info.get('project_name', '')
        client_name = case_info.get('client_name', 'Unknown')

        if not project_name:
            logger.warning("[WORKFLOW] No project_name in detected case")
            return request

        logger.info(f"[WORKFLOW] Computing workflow state for {project_name}")

        try:
            # Compute workflow state from knowledge graph
            state = self._compute_state_from_graph(project_name)

            if state is None:
                logger.warning(f"[WORKFLOW] No workflow state found in graph for {project_name}")
                return request

            logger.info(f"[WORKFLOW] State computed from knowledge graph")

            # Format guidance
            guidance = self._format_workflow_guidance(state, case_info)

            # Inject into system prompt
            return self._inject_guidance(request, guidance)

        except Exception as e:
            logger.error(f"[WORKFLOW] Error computing workflow state: {e}", exc_info=True)
            return request
    
    def _compute_state_from_graph(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Compute workflow state from FalkorDB knowledge graph.

        Returns the DerivedWorkflowState as a dict, or None if not found.
        """
        from roscoe.workflow_engine.orchestrator.graph_state_computer import (
            get_case_state_from_graph_sync
        )

        # Get case state dict from graph
        # This returns the DerivedWorkflowState.to_dict() output
        case_state = get_case_state_from_graph_sync(project_name)

        if not case_state:
            return None

        return case_state
    
    def wrap_model_call(self, request, handler):
        """Synchronous model call wrapper."""
        logger.info("=" * 60)
        logger.info("🔧 WORKFLOW MIDDLEWARE EXECUTING (SYNC)")
        logger.info("=" * 60)
        
        modified_request = self._process_request(request)
        return handler(modified_request)
    
    async def awrap_model_call(self, request, handler):
        """Asynchronous model call wrapper."""
        logger.info("=" * 60)
        logger.info("🔧 WORKFLOW MIDDLEWARE EXECUTING (ASYNC)")
        logger.info("=" * 60)
        
        # Run potentially blocking I/O in thread
        modified_request = await asyncio.to_thread(self._process_request, request)
        return await handler(modified_request)
    
    def _format_workflow_guidance(self, state: Dict[str, Any], case_info: dict) -> str:
        """
        Format workflow state (from graph) as markdown for prompt injection.

        Creates a structured guidance section that tells the agent:
        - Where the case is (phase)
        - Landmark completion status
        - What's blocking phase advancement
        - SOL status

        Args:
            state: Computed workflow state dict from GraphWorkflowStateComputer
            case_info: Case information dict with client_name, project_name
        """
        client_name = case_info.get('client_name', 'Unknown')
        lines = []

        # Header
        lines.append("---")
        lines.append(f"## 🧠 Workflow Status: {client_name}")
        lines.append("*State from Knowledge Graph*")
        lines.append("")

        # Current phase
        current_phase = state.get("current_phase", {})
        phase_name = current_phase.get("display_name", "Unknown")
        lines.append(f"**Phase**: {phase_name}")

        # Progress
        landmarks = state.get("landmarks", {})
        complete = landmarks.get("complete", 0)
        total = landmarks.get("total", 0)
        if total > 0:
            pct = int((complete / total) * 100)
            lines.append(f"**Progress**: {complete}/{total} landmarks ({pct}%)")

        # Can advance?
        can_advance = state.get("can_advance", False)
        if can_advance:
            next_phase = state.get("next_phase", "")
            lines.append(f"**Ready to advance** to {next_phase}")
        lines.append("")

        # Current phase landmarks
        current_landmarks = landmarks.get("current_phase", [])
        if current_landmarks:
            lines.append("### Landmarks")
            for lm in current_landmarks:
                status = lm.get("status", "incomplete")
                # Handle both name and display_name (graph uses display_name)
                raw_name = lm.get("name") or lm.get("display_name") or ""
                # Ensure it's a string before calling replace
                if isinstance(raw_name, dict):
                    raw_name = raw_name.get("name") or raw_name.get("display_name") or str(raw_name)
                name = str(raw_name).replace("_", " ").title()
                is_blocker = lm.get("hard_blocker") or lm.get("is_hard_blocker", False)

                if status == "complete":
                    lines.append(f"- ✅ {name}")
                elif status == "in_progress":
                    lines.append(f"- 🔄 {name}")
                else:
                    blocker_tag = " **(BLOCKER)**" if is_blocker else ""
                    lines.append(f"- ⬜ {name}{blocker_tag}")
            lines.append("")

        # Blocking landmarks
        blocking = state.get("blocking_landmarks", [])
        if blocking:
            lines.append("### 🚫 Blockers (must complete before advancing)")
            for b in blocking:
                # Handle both name and display_name (graph uses display_name)
                raw_name = b.get("name") or b.get("display_name") or ""
                if isinstance(raw_name, dict):
                    raw_name = raw_name.get("name") or raw_name.get("display_name") or str(raw_name)
                name = str(raw_name).replace("_", " ").title()
                lines.append(f"- {name}")
            lines.append("")

        # Workflows needed
        workflows_needed = state.get("workflows_needed", [])
        if workflows_needed:
            lines.append("### 📋 Suggested Workflows")
            for wf in workflows_needed[:5]:
                # Handle both name and display_name (graph uses display_name)
                raw_name = wf.get("name") or wf.get("workflow_name") or wf.get("display_name") or ""
                if isinstance(raw_name, dict):
                    raw_name = raw_name.get("name") or raw_name.get("workflow_name") or str(raw_name)
                wf_name = str(raw_name).replace("_", " ").title()
                skill = wf.get("skill", "")
                lines.append(f"- {wf_name}")
                if skill:
                    lines.append(f"  - Skill: `{skill}`")
            lines.append("")

        # SOL Status
        sol = state.get("statute_of_limitations", {})
        if sol and sol.get("deadline"):
            status = sol.get("status", "unknown")
            status_icon = {
                "safe": "✅",
                "warning": "⚠️",
                "urgent": "🟠",
                "critical": "🔴"
            }.get(status, "❓")

            lines.append(f"### {status_icon} SOL Status: {status.upper()}")
            lines.append(f"- Deadline: {sol.get('deadline', 'Unknown')}")
            lines.append(f"- Days remaining: {sol.get('days_remaining', 'Unknown')}")
            if status == "critical":
                lines.append("- **CRITICAL**: Must file suit or decline representation immediately!")
            elif status == "urgent":
                lines.append("- **URGENT**: Evaluate case for immediate demand or litigation")
            lines.append("")

        # Instruction for agent
        lines.append("---")
        lines.append("")
        lines.append("**WORKFLOW CONTEXT**: This is the current workflow state for reference.")
        lines.append("Wait for the user's specific question or request before taking action.")
        lines.append("Do NOT automatically start working on incomplete landmarks - let the user guide the conversation.")
        lines.append("")
        lines.append("---")

        return "\n".join(lines)
    
    def _inject_guidance(self, request, guidance: str):
        """Inject workflow guidance into the system prompt."""
        messages = list(request.messages)

        if not messages:
            return request

        # Check if first message is a system message
        first_msg = messages[0]
        is_system = (
            hasattr(first_msg, 'type') and first_msg.type == 'system'
        ) or (
            isinstance(first_msg, dict) and first_msg.get('role') == 'system'
        )

        if is_system:
            # Append to existing system message
            # Handle both SystemMessage objects and dicts
            if isinstance(first_msg, dict):
                existing_content = first_msg.get('content', '')
            else:
                existing_content = getattr(first_msg, 'content', '')

            messages[0] = SystemMessage(content=existing_content + "\n\n" + guidance)
        else:
            # Insert new system message
            messages.insert(0, SystemMessage(content=guidance))

        # Store workflow state in request state
        state = dict(request.state) if request.state else {}
        state['workflow_guidance_injected'] = True

        return request.override(messages=messages, state=state)
