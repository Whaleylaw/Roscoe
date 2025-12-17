"""
Slack Socket Mode bridge for Roscoe.

This module enables bidirectional chat with the LangGraph agent from Slack:
- Receives @mentions / DMs / slash commands via Slack Socket Mode
- Forwards user messages to a LangGraph deployment (LANGGRAPH_API_URL)
- Posts the final assistant response back to Slack

Required environment variables:
- SLACK_BOT_TOKEN: xoxb-...
- SLACK_APP_TOKEN: xapp-... (Socket Mode)
- LANGGRAPH_API_URL: e.g. http://127.0.0.1:2024
- SLACK_ASSISTANT_ID: graph/assistant name, e.g. roscoe_paralegal (default)
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from threading import Thread
from typing import Any, Dict, Optional, Tuple

from langgraph_sdk import get_sync_client
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logger = logging.getLogger("roscoe.slack")


class SlackConfigError(RuntimeError):
    pass


_MENTION_RE = re.compile(r"<@[^>]+>")
_thread_map: Dict[Tuple[str, str], str] = {}


@dataclass(frozen=True)
class SlackBridgeConfig:
    bot_token: str
    app_token: str
    langgraph_api_url: str
    assistant_id: str = "roscoe_paralegal"
    default_channel: str = "#legal-updates"

    @staticmethod
    def from_env() -> "SlackBridgeConfig":
        bot_token = (os.environ.get("SLACK_BOT_TOKEN") or "").strip()
        app_token = (os.environ.get("SLACK_APP_TOKEN") or "").strip()
        langgraph_api_url = (os.environ.get("LANGGRAPH_API_URL") or "http://127.0.0.1:2024").strip()
        assistant_id = (os.environ.get("SLACK_ASSISTANT_ID") or "roscoe_paralegal").strip()
        default_channel = (os.environ.get("SLACK_DEFAULT_CHANNEL") or "#legal-updates").strip()

        missing = []
        if not bot_token:
            missing.append("SLACK_BOT_TOKEN")
        if not app_token:
            missing.append("SLACK_APP_TOKEN")

        if missing:
            raise SlackConfigError(f"Missing Slack env vars: {', '.join(missing)}")

        # Light validation (avoid hard failure on enterprise/custom tokens)
        if not bot_token.startswith("xoxb-"):
            logger.warning("SLACK_BOT_TOKEN does not look like a bot token (expected xoxb-...)")
        if not app_token.startswith("xapp-"):
            logger.warning("SLACK_APP_TOKEN does not look like an app-level token (expected xapp-...)")

        return SlackBridgeConfig(
            bot_token=bot_token,
            app_token=app_token,
            langgraph_api_url=langgraph_api_url,
            assistant_id=assistant_id,
            default_channel=default_channel,
        )


def slack_configured() -> bool:
    """Return True if required Slack tokens are present."""
    try:
        SlackBridgeConfig.from_env()
        return True
    except SlackConfigError:
        return False


def _normalize_user_text(text: str) -> str:
    """Strip Slack mention markup and whitespace."""
    cleaned = _MENTION_RE.sub("", text or "")
    return cleaned.strip()


def _truncate_for_slack(text: str, limit: int = 3800) -> str:
    """Slack message practical limit is ~4k chars; keep some margin."""
    if len(text) <= limit:
        return text
    return text[: limit - 40].rstrip() + "\n\n[truncated to fit Slack message limit]"


def _extract_text_from_langgraph_state(state: Any) -> str:
    """
    Extract a human-readable assistant response from a LangGraph run output.

    Local deployments commonly return:
      {"messages": [HumanMessage-like dict, AIMessage-like dict]}

    AI message content may be a list of parts (e.g. Responses API):
      [{"type":"reasoning",...},{"type":"text","text":"..."}]
    """
    if not isinstance(state, dict):
        return str(state)

    msgs = state.get("messages")
    if not isinstance(msgs, list) or not msgs:
        return str(state)

    ai_msg = None
    for m in reversed(msgs):
        if isinstance(m, dict) and (m.get("type") in {"ai", "assistant"} or m.get("role") == "assistant"):
            ai_msg = m
            break

    if not isinstance(ai_msg, dict):
        return ""

    content = ai_msg.get("content", "")
    if isinstance(content, str):
        return content

    # Content parts (Responses API)
    if isinstance(content, list):
        parts: list[str] = []
        for p in content:
            if not isinstance(p, dict):
                continue
            if p.get("type") == "text" and isinstance(p.get("text"), str):
                parts.append(p["text"])
        if parts:
            return "\n".join(parts).strip()

        # Fallback: stringify minimal
        return ""

    return str(content)


def _get_or_create_thread_id(client: Any, key: Tuple[str, str]) -> str:
    thread_id = _thread_map.get(key)
    if thread_id:
        return thread_id
    thread = client.threads.create(metadata={"source": "slack", "slack_channel": key[0], "slack_conversation": key[1]})
    # Thread object is dict-like in sync client
    thread_id = thread.get("thread_id") if isinstance(thread, dict) else getattr(thread, "thread_id")
    _thread_map[key] = thread_id
    return thread_id


def _run_once(config: SlackBridgeConfig, user_text: str, conversation_key: Tuple[str, str]) -> str:
    client = get_sync_client(url=config.langgraph_api_url)
    thread_id = _get_or_create_thread_id(client, conversation_key)

    state = client.runs.wait(
        thread_id,
        config.assistant_id,
        input={"messages": [{"role": "user", "content": user_text}]},
        raise_error=True,
        metadata={
            "source": "slack",
            "slack_channel": conversation_key[0],
            "slack_conversation": conversation_key[1],
        },
    )
    return _extract_text_from_langgraph_state(state)


def _build_bolt_app(config: SlackBridgeConfig) -> App:
    # signing_secret is not required for Socket Mode, but App() accepts it; keep unset.
    app = App(token=config.bot_token)

    @app.event("app_mention")
    def handle_mention(event, say):  # type: ignore[no-redef]
        channel = event.get("channel")
        user = event.get("user") or ""
        ts = event.get("thread_ts") or event.get("ts") or ""
        text = _normalize_user_text(event.get("text") or "")
        if not channel or not text:
            return
        conv_key = (channel, ts or user)
        try:
            reply = _run_once(config, text, conv_key)
            reply = _truncate_for_slack(reply or "(no response)")
            say(text=reply, thread_ts=event.get("thread_ts") or event.get("ts"))
        except Exception as exc:
            logger.exception("Slack mention handling failed")
            say(text=f"Error while running agent: {exc}", thread_ts=event.get("thread_ts") or event.get("ts"))

    @app.event("message")
    def handle_message(event, say):  # type: ignore[no-redef]
        # Only respond to DMs (im)
        if event.get("channel_type") != "im":
            return
        if event.get("subtype") in {"bot_message", "message_changed"}:
            return
        if event.get("bot_id"):
            return

        channel = event.get("channel")
        user = event.get("user") or ""
        ts = event.get("thread_ts") or event.get("ts") or ""
        text = _normalize_user_text(event.get("text") or "")
        if not channel or not text:
            return
        conv_key = (channel, ts or user)
        try:
            reply = _run_once(config, text, conv_key)
            reply = _truncate_for_slack(reply or "(no response)")
            say(text=reply, thread_ts=event.get("thread_ts") or event.get("ts"))
        except Exception as exc:
            logger.exception("Slack DM handling failed")
            say(text=f"Error while running agent: {exc}", thread_ts=event.get("thread_ts") or event.get("ts"))

    @app.command("/roscoe")
    def handle_slash_command(ack, body, respond):  # type: ignore[no-redef]
        ack()
        channel = body.get("channel_id") or ""
        user = body.get("user_id") or ""
        text = (body.get("text") or "").strip()
        if not text:
            respond("Usage: /roscoe <your request>")
            return
        conv_key = (channel, user)
        try:
            reply = _run_once(config, text, conv_key)
            respond(_truncate_for_slack(reply or "(no response)"))
        except Exception as exc:
            logger.exception("Slack /roscoe failed")
            respond(f"Error while running agent: {exc}")

    @app.command("/roscoe-reset")
    def handle_reset(ack, body, respond):  # type: ignore[no-redef]
        ack()
        channel = body.get("channel_id") or ""
        user = body.get("user_id") or ""
        # reset all keys that match this user/channel
        to_delete = [k for k in _thread_map.keys() if k[0] == channel and k[1] == user]
        for k in to_delete:
            _thread_map.pop(k, None)
        respond("✅ Reset conversation context for this channel/user.")

    return app


def run_slack_bridge(*, blocking: bool = True) -> Thread:
    """
    Start the Slack Socket Mode handler.

    - blocking=True: runs in the current thread (never returns)
    - blocking=False: starts a daemon thread and returns it
    """
    config = SlackBridgeConfig.from_env()
    app = _build_bolt_app(config)
    handler = SocketModeHandler(app, config.app_token)

    def _target():
        logger.info("Slack bridge starting (Socket Mode). LangGraph API: %s assistant_id=%s", config.langgraph_api_url, config.assistant_id)
        handler.start()

    if blocking:
        _target()
        # Unreachable, but keep type contract
        return Thread()

    t = Thread(target=_target, name="roscoe-slack-bridge", daemon=True)
    t.start()
    return t


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    run_slack_bridge(blocking=True)

