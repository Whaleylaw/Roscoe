#!/bin/bash
# Periodic JSON sync script - runs via cron
# Add to crontab: */15 * * * * /path/to/sync_json_cron.sh >> /var/log/json_sync.log 2>&1

WORKSPACE="/mnt/workspace"
SCRIPT="$WORKSPACE/Tools/sync_case_json.py"
LOGFILE="$WORKSPACE/Database/script_execution_logs/json_sync.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOGFILE")"

echo "========================================" >> "$LOGFILE"
echo "JSON Sync started at $(date)" >> "$LOGFILE"

# Run the sync
python3 "$SCRIPT" >> "$LOGFILE" 2>&1

echo "JSON Sync completed at $(date)" >> "$LOGFILE"
echo "" >> "$LOGFILE"

