"""
Slack client adapter for ProactiveSurfacingMiddleware.

Reuses the existing Slack integration from tools.py.
Provides slack_client.send_message() interface expected by middleware.
"""
import os
import logging

logger = logging.getLogger(__name__)


class SlackClientAdapter:
    """
    Adapter to provide slack_client.send_message() interface.

    Uses the existing _get_slack_client() from tools.py.
    """

    def send_message(self, message: str, channel: str = None) -> bool:
        """
        Send message to Slack using existing integration.

        Args:
            message: Message content (markdown supported)
            channel: Target channel (defaults to SLACK_DEFAULT_CHANNEL)

        Returns:
            True if sent successfully, False otherwise
        """
        from roscoe.agents.paralegal.tools import _get_slack_client

        client = _get_slack_client()
        if not client:
            logger.warning("[SLACK ADAPTER] Slack not configured, skipping message")
            return False

        target_channel = channel or os.environ.get("SLACK_DEFAULT_CHANNEL", "#legal-updates")

        try:
            client.chat_postMessage(
                channel=target_channel,
                text=f"📬 {message}"
            )
            logger.info(f"[SLACK ADAPTER] Message sent to {target_channel}")
            return True
        except Exception as e:
            logger.error(f"[SLACK ADAPTER] Failed to send message: {e}")
            return False


_slack_client = None


def get_slack_client():
    """Get or create Slack client singleton."""
    global _slack_client
    if _slack_client is None:
        _slack_client = SlackClientAdapter()
    return _slack_client
