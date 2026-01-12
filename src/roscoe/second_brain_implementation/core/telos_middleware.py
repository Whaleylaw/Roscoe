"""
TELOSMiddleware - Loads attorney context at session start.

Based on PAI TELOS pattern: deep goal understanding for better recommendations.

TELOS (Greek: τέλος) = "end, goal, purpose" - understanding the attorney's
ultimate goals and preferences enables better strategic recommendations.

Architecture:
- Loads attorney context from /memories/TELOS/ at session start (before_agent hook)
- Injects into system message on every model call (wrap_model_call)
- Loads once per session (checks telos_loaded flag in state)
- Skips template files containing "[Attorney fills this in]"

Files loaded (in order):
1. mission.md - Professional mission and core values
2. goals.md - Current goals and objectives
3. preferences.md - Work style and communication preferences
4. contacts.md - VIP contacts and relationships (optional)
5. strategies.md - Legal strategies and approaches (optional)

Example system prompt injection:
    # Attorney Context (TELOS)

    The following context helps you understand the attorney's goals and preferences:

    ## mission.md

    # Professional Mission
    Provide excellent legal representation with compassion...

    ## goals.md

    # Current Goals
    - Expand medical malpractice practice
    - Improve client communication systems

This enables the agent to:
- Make recommendations aligned with attorney's values
- Prioritize work based on current goals
- Adapt communication style to preferences
- Surface relevant contacts proactively
"""

import os
from pathlib import Path
import logging
from typing import Optional, Dict, Any

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import SystemMessage

# Configure logger
logger = logging.getLogger(__name__)


class TELOSMiddleware(AgentMiddleware):
    """
    Load attorney context from /memories/TELOS/ at session start.

    Files loaded:
    - mission.md - Professional mission
    - goals.md - Current goals
    - preferences.md - Work style preferences
    - contacts.md - VIP contacts (optional)
    - strategies.md - Legal strategies (optional)

    Lifecycle:
    1. before_agent(): Loads TELOS files once per session, sets telos_loaded flag
    2. wrap_model_call(): Injects TELOS content into system message if loaded

    The content is loaded once and stored in request.state['telos_content'],
    then injected into every model call for that session.
    """

    name: str = "telos"  # Unique name required by LangChain middleware framework
    tools: list = []  # Required by AgentMiddleware base class

    def __init__(self, workspace_dir: Optional[str] = None):
        """
        Initialize TELOS middleware.

        Args:
            workspace_dir: Path to workspace directory (default: WORKSPACE_DIR env var or /mnt/workspace)
        """
        self.workspace_dir = workspace_dir or os.getenv('WORKSPACE_DIR', '/mnt/workspace')
        self.telos_dir = Path(self.workspace_dir) / 'memories' / 'TELOS'

        logger.info(f"[TELOS] Initialized with workspace_dir={self.workspace_dir}")
        print(f"🎯 TELOS MIDDLEWARE INITIALIZED - dir: {self.telos_dir}", flush=True)

    def before_agent(self, state: Dict[str, Any], runtime) -> Optional[Dict[str, Any]]:
        """
        Load TELOS files once per session.

        Called by Deep Agents framework before agent execution starts.
        Checks telos_loaded flag in state to avoid reloading.

        Args:
            state: Current agent state
            runtime: Runtime instance (not used)

        Returns:
            Dict with telos_loaded=True and telos_content, or None if already loaded or no content
        """
        # Check if already loaded
        if state.get('telos_loaded'):
            logger.info("[TELOS] Already loaded, skipping")
            return None

        logger.info("[TELOS] Loading TELOS files from session start")
        print("🎯 [TELOS] Loading attorney context...", flush=True)

        # Read TELOS files in priority order
        telos_files = [
            'mission.md',
            'goals.md',
            'preferences.md',
            'contacts.md',
            'strategies.md',
        ]

        telos_content_parts = []
        loaded_count = 0

        for filename in telos_files:
            file_path = self.telos_dir / filename
            try:
                if not file_path.exists():
                    logger.debug(f"[TELOS] File not found: {filename}")
                    continue

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Skip empty files
                if not content.strip():
                    logger.debug(f"[TELOS] Skipping empty file: {filename}")
                    continue

                # Skip template files with placeholder text
                if '[Attorney fills this in]' in content:
                    logger.debug(f"[TELOS] Skipping template file: {filename}")
                    continue

                # Add to content parts with filename header
                telos_content_parts.append(f"## {filename}\n\n{content}")
                loaded_count += 1
                logger.info(f"[TELOS] Loaded: {filename}")

            except FileNotFoundError:
                logger.debug(f"[TELOS] File not found: {filename}")
                continue
            except Exception as e:
                logger.error(f"[TELOS] Error reading {filename}: {e}", exc_info=True)
                continue

        # If no content loaded, return None
        if not telos_content_parts:
            logger.warning("[TELOS] No TELOS content found or all files are templates")
            print("⚠️ [TELOS] No attorney context found", flush=True)
            return None

        # Build final TELOS content
        telos_content = "\n\n".join([
            "# Attorney Context (TELOS)",
            "The following context helps you understand the attorney's goals and preferences:",
            "\n\n".join(telos_content_parts)
        ])

        logger.info(f"[TELOS] ✅ Loaded {loaded_count} TELOS files")
        print(f"✅ [TELOS] Loaded {loaded_count} attorney context files", flush=True)

        return {
            'telos_loaded': True,
            'telos_content': telos_content
        }

    def wrap_model_call(self, request, handler):
        """
        Inject TELOS into system message if loaded.

        Called on every model invocation. Checks if TELOS content was loaded
        by before_agent() and injects it into the system message.

        Args:
            request: ModelRequest with messages, state, config
            handler: Callable to invoke the next middleware or model

        Returns:
            Model response from handler
        """
        telos_content = request.state.get('telos_content') if request.state else None

        if not telos_content:
            # No TELOS content loaded, pass through
            return handler(request)

        logger.debug("[TELOS] Injecting TELOS content into system message")

        # Inject into system message
        # Append to existing system message content
        existing_content = request.system_message.content if request.system_message else ""
        new_system_message = SystemMessage(
            content=f"{existing_content}\n\n{telos_content}"
        )

        # Pass modified request to next handler
        return handler(request.override(system_message=new_system_message))

    async def awrap_model_call(self, request, handler):
        """
        Async version of wrap_model_call.

        Deep Agents may call this for async execution. Implementation is the same
        as sync version since we're just reading from state and modifying messages.
        """
        telos_content = request.state.get('telos_content') if request.state else None

        if not telos_content:
            # No TELOS content loaded, pass through
            return await handler(request)

        logger.debug("[TELOS] Injecting TELOS content into system message (async)")

        # Inject into system message
        existing_content = request.system_message.content if request.system_message else ""
        new_system_message = SystemMessage(
            content=f"{existing_content}\n\n{telos_content}"
        )

        # Pass modified request to next handler
        return await handler(request.override(system_message=new_system_message))
