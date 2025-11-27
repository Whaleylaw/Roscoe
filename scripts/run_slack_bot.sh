#!/usr/bin/env bash
# Helper script to launch the Slack Socket Mode bridge locally or on a VM.
# Usage:
#   ./scripts/run_slack_bot.sh
# Environment variables (exported or stored in .env) must include:
#   SLACK_BOT_TOKEN, SLACK_APP_TOKEN, LANGGRAPH_API_URL (optional), SLACK_ASSISTANT_ID (optional)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Starting Roscoe Slack bot from ${ROOT_DIR}"
exec python slack_bot.py "$@"

