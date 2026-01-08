#!/usr/bin/env python3
"""
Slack Bot for Roscoe - Bidirectional Chat Integration

This bot enables chatting with Roscoe from Slack using Socket Mode.
Runs as a sidecar process (local dev or VM) alongside the LangGraph server.

Usage:
    python slack_bot.py

Environment variables required:
    SLACK_BOT_TOKEN      - Bot User OAuth Token (xoxb-...)
    SLACK_APP_TOKEN      - App-Level Token for Socket Mode (xapp-...)

Optional:
    LANGGRAPH_API_URL    - URL to LangGraph API (default: http://127.0.0.1:2024)
    SLACK_ASSISTANT_ID   - LangGraph graph id (default: roscoe_paralegal)
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from threading import Thread
from typing import Dict, Optional

import requests
from requests import Response, Session
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded environment from: {env_path}")
except ImportError:
    print("Warning: python-dotenv not installed. Make sure environment variables are set manually.")
except Exception as exc:  # pragma: no cover - best effort logging
    print(f"Warning: Could not load .env file: {exc}")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
LANGGRAPH_API_URL = os.environ.get("LANGGRAPH_API_URL", "http://127.0.0.1:2024").rstrip("/")
ASSISTANT_ID = (
    os.environ.get("SLACK_ASSISTANT_ID")
    or os.environ.get("LANGGRAPH_ASSISTANT_ID")
    or "roscoe_paralegal"
)

STREAM_TIMEOUT = float(os.environ.get("SLACK_STREAM_TIMEOUT_SECONDS", "900"))
CONNECT_TIMEOUT = float(os.environ.get("SLACK_CONNECT_TIMEOUT_SECONDS", "10"))

# Configure logging
logging.basicConfig(
    level=os.environ.get("SLACK_BOT_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("roscoe.slack")

# Initialize Slack app even if tokens are absent (handlers still need registration)
app = App(token=SLACK_BOT_TOKEN or "xoxb-placeholder")

# Simple in-memory store for Slack user -> LangGraph thread ids
conversation_threads: Dict[str, str] = {}

# Reuse HTTP session for LangGraph communication
session = Session()
session.headers.update({"Content-Type": "application/json"})


class SlackConfigError(RuntimeError):
    """Raised when Slack credentials are missing or invalid."""


def slack_configured() -> bool:
    """Return True if Slack tokens are present."""
    return bool(SLACK_BOT_TOKEN and SLACK_APP_TOKEN)


def _ensure_slack_config() -> None:
    if not slack_configured():
        raise SlackConfigError(
            "Slack bridge requires SLACK_BOT_TOKEN and SLACK_APP_TOKEN environment variables."
        )
    if app is None:
        raise SlackConfigError("Slack WebClient failed to initialize (missing SLACK_BOT_TOKEN).")


def _ensure_thread(slack_user_id: str, metadata: Optional[Dict[str, str]] = None) -> str:
    """Create or load a LangGraph thread for a Slack user."""
    if slack_user_id in conversation_threads:
        return conversation_threads[slack_user_id]

    payload = {"metadata": {"slack_user": slack_user_id}}
    if metadata:
        payload["metadata"].update(metadata)

    logger.debug("Creating LangGraph thread for Slack user %s", slack_user_id)
    try:
        response: Response = session.post(
            f"{LANGGRAPH_API_URL}/threads",
            json=payload,
            timeout=(CONNECT_TIMEOUT, CONNECT_TIMEOUT),
        )
        response.raise_for_status()
        thread_id = response.json().get("thread_id")
        if thread_id:
            conversation_threads[slack_user_id] = thread_id
            return thread_id
    except requests.RequestException as exc:
        logger.warning("Thread creation failed (%s). Falling back to deterministic id.", exc)

    # Fallback: deterministic pseudo thread to avoid dropping the conversation
    fallback_id = f"slack-{slack_user_id}"
    conversation_threads[slack_user_id] = fallback_id
    return fallback_id


def _collect_streamed_response(response: Response) -> str:
    """Parse the streaming response from LangGraph and return the final assistant text."""
    agent_response = ""
    line_count = 0

    for raw_line in response.iter_lines():
        if not raw_line:
            continue

        line_count += 1
        try:
            line = raw_line.decode("utf-8")
        except UnicodeDecodeError:
            logger.debug("Skipping undecodable line %s", raw_line)
            continue

        if not line.startswith("data: "):
            continue

        try:
            payload = json.loads(line[6:])
        except json.JSONDecodeError as exc:
            if line_count <= 5:
                logger.debug("JSON decode error (%s) on line %s", exc, line_count)
            continue

        if not isinstance(payload, list) or not payload:
            continue

        message = payload[0]
        msg_type = message.get("type", "")

        # Ignore tool chatter so Slack only sees assistant responses
        if msg_type in {"tool", "tool_call"} or message.get("tool_calls"):
            continue

        if msg_type in {"ai", "assistant", "AIMessage"}:
            content = message.get("content")
            if isinstance(content, str):
                agent_response = content
            elif isinstance(content, list):
                chunks = []
                for block in content:
                    if isinstance(block, dict) and "text" in block:
                        chunks.append(block["text"])
                    elif isinstance(block, str):
                        chunks.append(block)
                agent_response = "".join(chunks)

    logger.debug("Collected response (%s lines, %s chars)", line_count, len(agent_response))
    return agent_response.strip()


def send_to_roscoe(user_message: str, slack_user_id: str, slack_channel: str = None) -> str:
    """
    Send a message to Roscoe agent via LangGraph API.

    Args:
        user_message: The user's message
        slack_user_id: Slack user ID for thread continuity
        slack_channel: Optional Slack channel ID for context

    Returns:
        Agent's response or error message
    """
    logger.info("Routing Slack user %s message: %s", slack_user_id, user_message[:80])
    
    # Inject Slack context so the agent knows to continue responding via Slack
    slack_context = f"""[SLACK CONVERSATION - User: {slack_user_id}]
For this conversation, use the send_slack_message tool for any progress updates, 
interim status messages, or notifications during long-running tasks. The initial 
response will automatically go to Slack, but subsequent updates should use the tool.
---
"""
    enhanced_message = slack_context + user_message
    
    try:
        thread_id = _ensure_thread(slack_user_id, metadata={"slack_channel": slack_channel or "dm"})
        logger.debug("Using thread %s", thread_id)

        response = session.post(
            f"{LANGGRAPH_API_URL}/threads/{thread_id}/runs/stream",
            json={
                "assistant_id": ASSISTANT_ID,
                "input": {"messages": [{"role": "user", "content": enhanced_message}]},
                "stream_mode": "messages",
            },
            stream=True,
            timeout=(CONNECT_TIMEOUT, STREAM_TIMEOUT),
        )
        response.raise_for_status()

        agent_response = _collect_streamed_response(response)
        if not agent_response:
            return "I received your message but had trouble generating a response. Please try again."

        return agent_response

    except requests.exceptions.ConnectionError:
        error_msg = (
            "⚠️ Cannot connect to Roscoe agent. Is the LangGraph server reachable? "
            "Check LANGGRAPH_API_URL."
        )
        logger.error(error_msg, exc_info=True)
        return error_msg
    except requests.RequestException as exc:
        error_msg = f"Error communicating with Roscoe: {exc}"
        logger.error(error_msg)
        return error_msg
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Unexpected error while sending message to Roscoe")
        return f"Sorry, I ran into an error: {exc}"


@app.event("app_mention")
def handle_app_mention(event, say):
    """
    Handle when someone mentions @Roscoe in a channel.

    Example: @Roscoe what's the status of the Wilson case?
    """
    logger.info("Received app_mention: %s", event.get("text", "")[:200])
    try:
        # Extract the message (remove the bot mention)
        user_message = event["text"]
        # Remove bot mention tag
        bot_user_id = event.get("bot_id") or app.client.auth_test()["user_id"]
        user_message = user_message.replace(f"<@{bot_user_id}>", "").strip()

        if not user_message:
            say("Yes? How can I help?", thread_ts=event["ts"])
            return

        # Get user and channel info
        slack_user_id = event["user"]
        slack_channel = event.get("channel")

        # Send to Roscoe agent with channel context
        response = send_to_roscoe(user_message, slack_user_id, slack_channel)

        # Reply in thread
        say(text=response, thread_ts=event["ts"])

    except Exception as e:
        logger.exception("Error while handling app mention")
        say(f"Sorry, I encountered an error: {str(e)}", thread_ts=event.get("ts"))


@app.event("message")
def handle_direct_message(event, say):
    """
    Handle direct messages to Roscoe.

    User can DM Roscoe directly without needing to @mention.
    """
    # Ignore bot's own messages
    if event.get("bot_id"):
        return

    # Only handle direct messages (DMs)
    if event.get("channel_type") != "im":
        return

    try:
        user_message = event["text"]
        slack_user_id = event["user"]
        slack_channel = event.get("channel")

        # Send to Roscoe agent with DM context
        response = send_to_roscoe(user_message, slack_user_id, slack_channel)

        # Reply
        say(text=response)

    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        logger.exception("Error while handling DM")
        say(error_msg)


@app.command("/roscoe")
def handle_slash_command(ack, command, respond):
    """
    Handle /roscoe slash command.

    Example: /roscoe status Wilson case
    """
    ack()  # Acknowledge command receipt

    try:
        user_message = command["text"]
        slack_user_id = command["user_id"]
        slack_channel = command.get("channel_id")

        if not user_message:
            respond("Usage: `/roscoe [your question or command]`\nExample: `/roscoe status Wilson case`")
            return

        # Send to Roscoe agent with channel context
        response = send_to_roscoe(user_message, slack_user_id, slack_channel)

        # Reply
        respond(text=response)

    except Exception as e:
        logger.exception("Error while handling /roscoe command")
        respond(f"Sorry, I encountered an error: {str(e)}")


@app.command("/roscoe-reset")
def handle_reset_command(ack, command, respond):
    """
    Reset conversation thread for this user.

    Example: /roscoe-reset
    """
    ack()

    slack_user_id = command["user_id"]

    if slack_user_id in conversation_threads:
        del conversation_threads[slack_user_id]
        respond("✅ Conversation reset. I've forgotten our previous conversation.")
    else:
        respond("No active conversation to reset.")


def _log_langgraph_status() -> None:
    """Log LangGraph connectivity for visibility."""
    try:
        response = session.get(f"{LANGGRAPH_API_URL}/ok", timeout=(CONNECT_TIMEOUT, CONNECT_TIMEOUT))
        if response.status_code == 200:
            logger.info("✅ Successfully connected to LangGraph API")
        else:
            logger.warning("LangGraph API returned %s", response.status_code)
    except requests.RequestException:
        logger.warning("Cannot reach LangGraph API. Continuing anyway.")


def run_slack_bridge(blocking: bool = True) -> Optional[Thread]:
    """
    Start the Slack Socket Mode bridge.

    Returns the background thread when blocking=False.
    """
    _ensure_slack_config()

    if app is None:
        raise SlackConfigError("Slack app not initialized; missing SLACK_BOT_TOKEN.")

    logger.info("Starting Slack Socket Mode handler (blocking=%s)", blocking)
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)

    if blocking:
        handler.start()
        return None

    thread = Thread(target=handler.start, name="RoscoeSlackSocketMode", daemon=True)
    thread.start()
    return thread


def main():
    """Start the Slack bot with Socket Mode."""
    logger.info("=" * 80)
    logger.info("Roscoe Slack Bot - Starting...")
    logger.info("LangGraph API: %s", LANGGRAPH_API_URL)
    logger.info("Assistant ID : %s", ASSISTANT_ID)
    logger.info("=" * 80)

    _log_langgraph_status()

    try:
        run_slack_bridge(blocking=True)
    except SlackConfigError as exc:
        logger.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
