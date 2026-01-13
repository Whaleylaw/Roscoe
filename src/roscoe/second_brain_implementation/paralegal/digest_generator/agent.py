"""
Digest Generator Subagent

This subagent queries the knowledge graph, calendar, and memory files to
generate morning digests for the Second Brain system.

Architecture:
- Uses create_agent (not create_deep_agent) for simplicity
- Model from get_agent_llm() inherits MODEL_PROVIDER setting
- Tools: graph_query, list_events (calendar)
- Middleware: FilesystemMiddleware (provides read_file, write_file, ls, edit_file)
- Returns JSON dict (not markdown) for middleware formatting
- Lazy initialization to avoid pickle errors with LangGraph

Usage:
    digest = generate_morning_digest(user_id="aaron", thread_id="thread123", target_date="2024-12-15")
    # Returns: {"top_3_actions": [...], "calendar": [...], "stuck_or_avoiding": "...", "small_win": "..."}
"""

import json
import logging
from typing import Dict, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# Lazy initialization to avoid pickle errors
_digest_generator_instance = None


def get_digest_generator_subagent():
    """
    Get the digest generator subagent (lazily initialized).

    Uses lazy loading to avoid capturing model instances in LangGraph state,
    which would cause pickle errors due to thread locks in HTTP clients.

    Returns:
        dict: Subagent configuration with name, description, system_prompt, tools, model
    """
    global _digest_generator_instance

    if _digest_generator_instance is None:
        from deepagents import create_agent
        from deepagents.middleware import FilesystemMiddleware
        from roscoe.agents.paralegal.models import get_agent_llm
        from roscoe.agents.paralegal.tools import graph_query
        from roscoe.agents.paralegal.calendar_tools import list_events
        from .prompts import DIGEST_GENERATOR_PROMPT

        logger.info("[DIGEST GENERATOR] Initializing digest generator subagent")

        # Create subagent using create_agent (simple pattern)
        _digest_generator_instance = create_agent(
            name="digest-generator",
            system_prompt=DIGEST_GENERATOR_PROMPT,
            model=get_agent_llm(),
            tools=[
                graph_query,
                list_events,
            ],
            middleware=[
                FilesystemMiddleware(
                    system_prompt="Use read_file to access workspace files for context. Memory files are in /memories/Work/ and /memories/Signals/."
                ),
            ]
        )

        logger.info("[DIGEST GENERATOR] ✅ Digest generator subagent initialized")

    return _digest_generator_instance


def generate_morning_digest(
    user_id: str,
    thread_id: Optional[str],
    target_date: str
) -> Optional[Dict]:
    """
    Generate morning digest using subagent.

    This function invokes the digest generator subagent to query data sources
    and synthesize a morning brief with:
    - Top 3 actions for today
    - Today's calendar events
    - One thing that might be stuck
    - One small win to notice

    Args:
        user_id: User identifier (for logging)
        thread_id: Optional thread identifier (for logging)
        target_date: Date string in ISO format (YYYY-MM-DD)

    Returns:
        Dict with digest content, or None if generation fails:
        {
            "top_3_actions": ["action 1", "action 2", "action 3"],
            "calendar": ["event 1 at time", "event 2 at time"],
            "stuck_or_avoiding": "one thing that might be stuck",
            "small_win": "one recent accomplishment"
        }

    Example:
        digest = generate_morning_digest(
            user_id="aaron",
            thread_id="thread_abc123",
            target_date="2024-12-15"
        )
    """
    logger.info(
        f"[DIGEST GENERATOR] Generating digest for {user_id} "
        f"(thread: {thread_id}, date: {target_date})"
    )

    try:
        # Get subagent (lazy initialization)
        subagent = get_digest_generator_subagent()

        # Create task for subagent
        task = {
            "messages": [
                HumanMessage(content=f"""
Generate morning digest for {target_date}.

Query the knowledge graph for:
- Pending tasks (due today or overdue)
- People with pending follow-ups
- Cases with approaching deadlines

Query Google Calendar for today's events (days=1).

Return digest in JSON format:
{{
  "top_3_actions": ["action 1", "action 2", "action 3"],
  "calendar": ["event 1 at time", "event 2 at time"],
  "stuck_or_avoiding": "one thing that might be stuck",
  "small_win": "one recent accomplishment"
}}

Be specific and actionable. Use actual case/task data. Keep under 150 words total.
""".strip())
            ]
        }

        logger.debug(f"[DIGEST GENERATOR] Invoking subagent with task: {task}")

        # Invoke subagent
        result = subagent.invoke(task)

        # Extract response content
        if not result or 'messages' not in result or not result['messages']:
            logger.warning("[DIGEST GENERATOR] No response from subagent")
            return None

        response_content = result['messages'][-1].content
        logger.debug(f"[DIGEST GENERATOR] Subagent response: {response_content}")

        # Parse JSON response
        # The subagent may wrap JSON in markdown code blocks, so extract it
        if "```json" in response_content:
            # Extract JSON from code block
            json_start = response_content.find("```json") + 7
            json_end = response_content.find("```", json_start)
            json_str = response_content[json_start:json_end].strip()
        elif "```" in response_content:
            # Generic code block
            json_start = response_content.find("```") + 3
            json_end = response_content.find("```", json_start)
            json_str = response_content[json_start:json_end].strip()
        else:
            # Assume entire response is JSON
            json_str = response_content.strip()

        digest_json = json.loads(json_str)

        logger.info(
            f"[DIGEST GENERATOR] ✅ Digest generated successfully - "
            f"actions: {len(digest_json.get('top_3_actions', []))}, "
            f"calendar: {len(digest_json.get('calendar', []))}"
        )

        return digest_json

    except json.JSONDecodeError as e:
        logger.error(
            f"[DIGEST GENERATOR] Failed to parse JSON from subagent response: {e}",
            exc_info=True
        )
        logger.debug(f"[DIGEST GENERATOR] Raw response: {response_content}")
        return None

    except Exception as e:
        logger.error(
            f"[DIGEST GENERATOR] Error generating digest: {e}",
            exc_info=True
        )
        return None


def format_digest_markdown(digest: Dict) -> str:
    """
    Format digest dict into markdown for delivery.

    Args:
        digest: Digest dict from generate_morning_digest

    Returns:
        Markdown formatted digest string
    """
    lines = []

    # Top 3 Actions
    if digest.get('top_3_actions'):
        lines.append("## 🎯 TOP 3 ACTIONS")
        lines.append("")
        for i, action in enumerate(digest['top_3_actions'], 1):
            lines.append(f"{i}. {action}")
        lines.append("")

    # Calendar
    if digest.get('calendar'):
        lines.append("## 📅 TODAY'S CALENDAR")
        lines.append("")
        for event in digest['calendar']:
            lines.append(f"- {event}")
        lines.append("")

    # Stuck/Avoiding
    if digest.get('stuck_or_avoiding'):
        lines.append("## 🚧 STUCK/AVOIDING")
        lines.append("")
        lines.append(digest['stuck_or_avoiding'])
        lines.append("")

    # Small Win
    if digest.get('small_win'):
        lines.append("## 🎉 SMALL WIN")
        lines.append("")
        lines.append(digest['small_win'])
        lines.append("")

    return "\n".join(lines)
