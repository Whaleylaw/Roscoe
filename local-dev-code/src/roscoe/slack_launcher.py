"""
Utility to automatically start the Slack Socket-Mode bridge inside the agent process.
"""

from __future__ import annotations

import logging
import os
from threading import Lock
from typing import Optional

logger = logging.getLogger("roscoe.slack")

_lock = Lock()
_started = False
_thread: Optional["Thread"] = None


def _bridge_enabled() -> bool:
    """
    Determine whether the in-process Slack bridge should auto-start.

    Defaults to True; set ROSCOE_ENABLE_SLACK_BRIDGE=false to disable.
    """
    value = os.environ.get("ROSCOE_ENABLE_SLACK_BRIDGE")
    if value is None:
        return True
    return value.lower() in {"1", "true", "yes", "on"}


def ensure_bridge_started() -> bool:
    """
    Start the Slack bridge in a daemon thread if configuration is present.

    Returns True if the bridge is running (or was already running).
    """
    global _started, _thread

    if not _bridge_enabled():
        logger.info("ROSCOE_ENABLE_SLACK_BRIDGE is disabled; skipping Slack startup.")
        return False

    with _lock:
        if _started:
            return True

        try:
            from roscoe.slack_bot import (
                SlackConfigError,
                run_slack_bridge,
                slack_configured,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Slack bridge unavailable (import failed): %s", exc)
            return False

        if not slack_configured():
            logger.info("Slack tokens not configured; skipping Slack bridge startup.")
            return False

        try:
            _thread = run_slack_bridge(blocking=False)
            _started = True
            logger.info("Slack Socket-Mode bridge running inside agent container.")
            return True
        except SlackConfigError as exc:
            logger.warning("Slack bridge configuration error: %s", exc)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to start Slack bridge")

        return False

