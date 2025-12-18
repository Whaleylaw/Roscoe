"""
UI Context Middleware - Bridges CopilotKit UI state to agent.

Receives UI state from CopilotKit's useCoAgent.setState() and injects
it into the agent's system prompt so the agent knows what the user is viewing.

UI State Fields:
- openDocument: Currently open document (path, type, annotations)
- currentPath: Current workspace directory
- visibleFiles: Files shown in file browser
"""

from typing import Optional, Dict, List, Any
import logging
from langchain.agents.middleware import AgentMiddleware
from langchain.agents import AgentState
from langchain_core.messages import SystemMessage

logger = logging.getLogger(__name__)


class UIContextState(AgentState):
    """State schema for UI context from CopilotKit"""
    openDocument: Optional[Dict] = None
    currentPath: str = "/"
    visibleFiles: List[Dict] = []


class UIContextMiddleware(AgentMiddleware):
    """
    Injects UI state from CopilotKit into agent context.

    This middleware receives state sent from the frontend via useCoAgent.setState()
    and formats it for injection into the system prompt.

    State fields:
    - openDocument: {path: str, type: str, annotations: list}
    - currentPath: str (e.g., "/Database")
    - visibleFiles: [{name: str, path: str, type: str}, ...]
    """

    name: str = "ui_context"
    state_schema = UIContextState  # Tells agent to accept these state fields
    tools: list = []

    def __init__(self):
        """Initialize UI context middleware"""
        logger.info("[UI CONTEXT] Middleware initialized")
        print("🖥️ UI CONTEXT MIDDLEWARE INITIALIZED", flush=True)

    def _format_ui_context(self, open_doc: Optional[Dict], current_path: str, visible_files: List[Dict]) -> str:
        """Format UI state into markdown for system prompt injection"""

        if not open_doc and current_path == "/":
            return ""  # No UI context to inject

        context_parts = []
        context_parts.append("## 🖥️ UI Context")
        context_parts.append("_The following reflects what the user is currently viewing in their browser:_\n")

        # Open document info
        if open_doc:
            context_parts.append("### 📄 Open Document")
            context_parts.append(f"**Path**: `{open_doc.get('path', 'Unknown')}`")
            context_parts.append(f"**Type**: {open_doc.get('type', 'Unknown')}")

            annotations = open_doc.get('annotations', [])
            if annotations:
                context_parts.append(f"**User Annotations**: {len(annotations)} highlights/comments on this document")

            context_parts.append("_The user can see this document in their viewer right now._\n")

        # Current workspace location
        if current_path and current_path != "/":
            context_parts.append("### 📁 Current Location")
            context_parts.append(f"**Workspace Path**: `{current_path}`")

            if visible_files:
                file_count = len(visible_files)
                context_parts.append(f"**Visible Files**: {file_count} items in current folder")

            context_parts.append("")

        context_parts.append("---\n")
        return "\n".join(context_parts)

    def wrap_model_call(self, request, handler):
        """Inject UI context before model call"""

        # Extract UI state from request
        open_doc = request.state.get('openDocument')
        current_path = request.state.get('currentPath', '/')
        visible_files = request.state.get('visibleFiles', [])

        # Log UI state for debugging
        if open_doc:
            logger.info(f"[UI CONTEXT] Open document: {open_doc.get('path')}")
            print(f"📄 [UI CONTEXT] User viewing: {open_doc.get('path')}", flush=True)

        # Format context
        ui_context = self._format_ui_context(open_doc, current_path, visible_files)

        if not ui_context:
            return handler(request)  # No context to inject

        # Inject into system message (same pattern as CaseContextMiddleware)
        messages = list(request.messages)

        if messages and hasattr(messages[0], 'type') and messages[0].type == 'system':
            # Append to existing system message
            existing_content = messages[0].content
            messages[0] = SystemMessage(content=existing_content + "\n\n" + ui_context)
        else:
            # Insert new system message
            messages.insert(0, SystemMessage(content=ui_context))

        logger.info(f"[UI CONTEXT] Injected context into system prompt")
        return handler(request.override(messages=messages))

    async def awrap_model_call(self, request, handler):
        """Async version - same logic as sync"""
        import asyncio

        # Extract UI state from request
        open_doc = request.state.get('openDocument')
        current_path = request.state.get('currentPath', '/')
        visible_files = request.state.get('visibleFiles', [])

        # Log UI state for debugging
        if open_doc:
            logger.info(f"[UI CONTEXT] Open document: {open_doc.get('path')}")
            print(f"📄 [UI CONTEXT] User viewing: {open_doc.get('path')}", flush=True)

        # Format context
        ui_context = await asyncio.to_thread(self._format_ui_context, open_doc, current_path, visible_files)

        if not ui_context:
            return await handler(request)  # No context to inject

        # Inject into system message (same pattern as CaseContextMiddleware)
        messages = list(request.messages)

        if messages and hasattr(messages[0], 'type') and messages[0].type == 'system':
            # Append to existing system message
            existing_content = messages[0].content
            messages[0] = SystemMessage(content=existing_content + "\n\n" + ui_context)
        else:
            # Insert new system message
            messages.insert(0, SystemMessage(content=ui_context))

        logger.info(f"[UI CONTEXT] Injected context into system prompt")
        return await handler(request.override(messages=messages))
