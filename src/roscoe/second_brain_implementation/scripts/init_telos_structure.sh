#!/bin/bash
MEMORIES_DIR="${WORKSPACE_DIR:-/mnt/workspace}/memories"

mkdir -p "$MEMORIES_DIR/TELOS"
mkdir -p "$MEMORIES_DIR/Work"
mkdir -p "$MEMORIES_DIR/Learning"/{OBSERVE,THINK,PLAN,BUILD,EXECUTE,VERIFY,LEARN}
mkdir -p "$MEMORIES_DIR/Signals"
mkdir -p "$MEMORIES_DIR/History"/{sessions,research,decisions,learnings}
mkdir -p "$MEMORIES_DIR/Continuity"

echo "Created /memories/ directory structure"
