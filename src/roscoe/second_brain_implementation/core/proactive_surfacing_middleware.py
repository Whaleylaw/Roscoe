"""
ProactiveSurfacingMiddleware - Proactive digest generation for Second Brain.

This middleware implements the "Tap on Shoulder" pattern from PAI/Membox:
- Morning digest: Triggered at 7 AM on first agent invocation
- Weekly review: Triggered on Sunday (first invocation)
- Delivery: Slack or /memories/ directory

Architecture:
- Uses before_agent hook (runs BEFORE main agent)
- Checks time and user to avoid duplicate digests
- Calls digest generator subagent (Task 10)
- Does NOT short-circuit agent (returns None or dict, handler continues)

Similar to CaptureMiddleware's before_agent pattern, but for proactive delivery.

Integration:
1. Add to middleware stack in agent.py
2. Provide graph_client for data access
3. Optional slack_client for Slack delivery
4. Digest generator subagent implemented in Task 10

Example usage:
    middleware = ProactiveSurfacingMiddleware(
        graph_client=graph_client,
        slack_client=slack_client  # Optional
    )

    # Morning digest triggers at 7 AM on first invocation
    result = middleware.before_agent(state, runtime)
    # Returns: {'digest_triggered': True, 'digest_content': '...'}
"""

from datetime import datetime, time, date, timedelta
from typing import Any, Dict, Optional
import logging
import threading

from langchain.agents.middleware import AgentMiddleware

# Configure logger
logger = logging.getLogger(__name__)


class ProactiveSurfacingMiddleware(AgentMiddleware):
    """
    Generate and deliver proactive digests (Second Brain Tap + PAI patterns).

    Triggers:
    - Morning digest: 7 AM first invocation
    - Weekly review: Sunday first invocation (future)

    Delivery:
    - Slack: If slack_client provided
    - File: /memories/digests/{date}.md (fallback)

    State tracking:
    - last_digest_dates: Dict[user_id, date] - prevents duplicate digests

    Hooks:
    - before_agent: Check time, generate digest if due, deliver
    - Does NOT short-circuit (returns None or dict, agent continues)

    Args:
        graph_client: FalkorDB client for data access
        slack_client: Optional Slack client for delivery
    """

    name: str = "proactive_surfacing"  # Unique name for LangChain middleware framework
    tools: list = []  # Required by AgentMiddleware base class

    def __init__(self, graph_client, slack_client=None):
        """
        Initialize ProactiveSurfacingMiddleware.

        Args:
            graph_client: FalkorDB client for querying memory data
            slack_client: Optional Slack client for delivery
        """
        self.graph_client = graph_client
        self.slack_client = slack_client
        self.last_digest_dates = {}  # user_id -> date
        self._digest_lock = threading.Lock()  # Thread safety for digest_dates access

        logger.info(
            f"[PROACTIVE SURFACING] Initialized - "
            f"slack_enabled: {slack_client is not None}"
        )
        print(
            f"📬 PROACTIVE SURFACING MIDDLEWARE INITIALIZED - "
            f"slack: {slack_client is not None}",
            flush=True
        )

    def before_agent(
        self,
        state: Dict[str, Any],
        runtime: Any,
        current_time: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if digest is due and generate.

        Called BEFORE main agent processes request.

        Logic:
        1. Get current time (or use provided time for testing)
        2. Check if after 7 AM
        3. Check if already generated today for this user (thread-safe)
        4. Generate digest using _generate_morning_digest
        5. Deliver via _deliver_digest
        6. Track last_digest_date (only if delivery successful)
        7. Return digest info (does NOT short-circuit agent)
        8. Clean up old digest dates (prevent memory leak)

        Args:
            state: Current agent state
            runtime: LangChain runtime (contains config)
            current_time: Optional datetime for testing (defaults to now())

        Returns:
            None: If no digest triggered
            Dict: {'digest_triggered': True/False, 'digest_content': str}
        """
        if current_time is None:
            current_time = datetime.now()

        # Extract user_id and thread_id from runtime config
        user_id = runtime.config.get('configurable', {}).get('user_id', 'default')
        thread_id = runtime.config.get('configurable', {}).get('thread_id')

        today = current_time.date()

        # Thread-safe check and update
        with self._digest_lock:
            # Check if already generated today
            last_digest_date = self.last_digest_dates.get(user_id)
            if last_digest_date == today:
                logger.debug(
                    f"[PROACTIVE SURFACING] Digest already generated today for {user_id}"
                )
                return None

            # Check if it's after 7 AM
            if current_time.time() < time(7, 0):
                logger.debug(
                    f"[PROACTIVE SURFACING] Before 7 AM - skipping digest "
                    f"(current: {current_time.time()})"
                )
                return None

            # Clean up old digest dates (prevent memory leak)
            self._cleanup_old_digest_dates(today)

            # Generate digest
            logger.info(
                f"[PROACTIVE SURFACING] Generating morning digest for {user_id} "
                f"at {current_time.strftime('%Y-%m-%d %H:%M')}"
            )
            print(
                f"📬 [PROACTIVE SURFACING] Generating morning digest for {user_id}",
                flush=True
            )

            digest = self._generate_morning_digest(user_id, thread_id)

            # Deliver digest if content generated
            if digest:
                logger.info(f"[PROACTIVE SURFACING] Delivering digest to {user_id}")
                delivered = self._deliver_digest(digest, user_id, today)

                # Track last digest date only if delivery successful
                if delivered:
                    self.last_digest_dates[user_id] = today
                    logger.info(f"[PROACTIVE SURFACING] ✅ Digest delivered for {user_id}")
                    print(f"✅ [PROACTIVE SURFACING] Digest delivered", flush=True)

                    return {
                        'digest_triggered': True,
                        'digest_content': digest
                    }
                else:
                    logger.warning(f"[PROACTIVE SURFACING] Digest delivery failed for {user_id}")
                    return None
            else:
                logger.debug(f"[PROACTIVE SURFACING] No digest content generated")
                return None

    def _cleanup_old_digest_dates(self, current_date: date) -> None:
        """
        Remove digest dates older than 30 days to prevent memory leak.

        This method should be called from before_agent while holding the
        _digest_lock to ensure thread safety.

        Args:
            current_date: Current date for calculating cutoff
        """
        cutoff_date = current_date - timedelta(days=30)

        # Find old entries
        old_users = [
            user_id for user_id, digest_date in self.last_digest_dates.items()
            if digest_date < cutoff_date
        ]

        # Remove old entries
        for user_id in old_users:
            del self.last_digest_dates[user_id]

        if old_users:
            logger.info(
                f"[PROACTIVE SURFACING] Cleaned up {len(old_users)} old digest dates"
            )

    def _generate_morning_digest(
        self,
        user_id: str,
        thread_id: Optional[str]
    ) -> Optional[str]:
        """
        Generate morning digest using digest generator subagent.

        Queries data sources via subagent and formats digest as markdown.

        Digest includes:
        - Top 3 actions for today
        - Today's calendar events
        - One thing that might be stuck
        - One recent accomplishment

        Args:
            user_id: User identifier
            thread_id: Optional thread identifier

        Returns:
            Digest content as markdown string, or None if generation fails
        """
        from roscoe.second_brain_implementation.paralegal.digest_generator.agent import (
            generate_morning_digest,
            format_digest_markdown
        )
        from datetime import datetime

        logger.debug(
            f"[PROACTIVE SURFACING] Generating digest via subagent - "
            f"user_id: {user_id}, thread_id: {thread_id}"
        )

        # Get today's date for digest
        today = datetime.now().date().isoformat()

        # Generate digest using subagent
        digest_dict = generate_morning_digest(user_id, thread_id, today)

        if not digest_dict:
            logger.warning("[PROACTIVE SURFACING] Subagent returned no digest")
            return None

        # Format as markdown
        digest_markdown = format_digest_markdown(digest_dict)

        logger.info(
            f"[PROACTIVE SURFACING] ✅ Digest generated - "
            f"{len(digest_markdown)} characters"
        )

        return digest_markdown

    def _deliver_digest(self, digest: str, user_id: str, current_date: date) -> bool:
        """
        Deliver digest to Slack or /memories/ directory.

        Delivery priority:
        1. Slack (if slack_client available)
        2. File: /memories/digests/{date}.md (fallback)

        Args:
            digest: Digest content (markdown)
            user_id: User identifier
            current_date: Date for file naming (ensures testability)

        Returns:
            True if delivery successful (Slack or file), False otherwise
        """
        delivered = False

        # Try Slack delivery first
        if self.slack_client:
            try:
                logger.info(f"[PROACTIVE SURFACING] Delivering to Slack for {user_id}")
                self.slack_client.send_message(digest)
                delivered = True
                logger.info("[PROACTIVE SURFACING] ✅ Delivered to Slack")
            except Exception as e:
                logger.warning(
                    f"[PROACTIVE SURFACING] Slack delivery failed: {e}"
                )

        # Fallback to file delivery (or primary if no Slack)
        try:
            import os
            from pathlib import Path

            # Get workspace directory
            workspace_dir = os.getenv('WORKSPACE_DIR', '/mnt/workspace')
            digests_dir = Path(workspace_dir) / 'memories' / 'digests'
            digests_dir.mkdir(parents=True, exist_ok=True)

            # Write digest file using passed date (not date.today())
            date_str = current_date.strftime('%Y-%m-%d')
            digest_file = digests_dir / f"{date_str}_{user_id}.md"

            logger.info(
                f"[PROACTIVE SURFACING] Writing digest to {digest_file}"
            )

            with open(digest_file, 'w') as f:
                f.write(f"# Morning Digest - {date_str}\n\n")
                f.write(digest)

            delivered = True
            logger.info(
                f"[PROACTIVE SURFACING] ✅ Delivered to file: {digest_file}"
            )

        except Exception as e:
            logger.error(
                f"[PROACTIVE SURFACING] File delivery failed: {e}",
                exc_info=True
            )

        return delivered

    def wrap_model_call(self, request, handler):
        """
        Synchronous model call wrapper - not used.

        ProactiveSurfacingMiddleware uses before_agent hook instead.
        """
        logger.debug("[PROACTIVE SURFACING] wrap_model_call (passthrough)")
        return handler(request)

    async def awrap_model_call(self, request, handler):
        """
        Asynchronous model call wrapper - not used.

        ProactiveSurfacingMiddleware uses before_agent hook instead.
        """
        logger.debug("[PROACTIVE SURFACING] awrap_model_call (passthrough)")
        return await handler(request)
