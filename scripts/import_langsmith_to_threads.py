#!/usr/bin/env python3
"""
Import conversation history from LangSmith traces into LangGraph threads.

This script:
1. Fetches recent runs from LangSmith for the roscoe-local project
2. Extracts messages from run inputs/outputs
3. Creates or updates LangGraph threads with the conversation history

Usage:
    python import_langsmith_to_threads.py [--days 7] [--limit 50] [--dry-run]

Requirements:
    pip install langsmith httpx

Environment:
    LANGSMITH_API_KEY - LangSmith API key
    LANGGRAPH_URL - LangGraph API URL (default: http://localhost:8123)
"""

import os
import sys
import json
import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import argparse

# LangSmith client
try:
    from langsmith import Client as LangSmithClient
except ImportError:
    print("Error: langsmith not installed. Run: pip install langsmith")
    sys.exit(1)


LANGGRAPH_URL = os.environ.get("LANGGRAPH_URL", "http://localhost:8123")


def extract_messages_from_run(run) -> List[Dict[str, Any]]:
    """Extract messages from a LangSmith run."""
    messages = []

    # Get input messages
    if run.inputs:
        input_messages = run.inputs.get("messages", [])
        for msg in input_messages:
            if isinstance(msg, dict):
                msg_type = msg.get("type", msg.get("role", ""))
                content = msg.get("content", "")
                if msg_type in ("human", "user"):
                    messages.append({"type": "human", "content": content})
                elif msg_type in ("ai", "assistant"):
                    messages.append({"type": "ai", "content": content})

    # Get output messages (the assistant response)
    if run.outputs:
        output_messages = run.outputs.get("messages", [])
        for msg in output_messages:
            if isinstance(msg, dict):
                msg_type = msg.get("type", msg.get("role", ""))
                content = msg.get("content", "")
                # Handle Claude's content block format
                if isinstance(content, list):
                    content = "".join(
                        block.get("text", "")
                        for block in content
                        if isinstance(block, dict) and block.get("type") == "text"
                    )
                if msg_type in ("ai", "assistant") and content:
                    # Only add if not already in messages
                    if not any(m.get("content") == content for m in messages):
                        messages.append({"type": "ai", "content": content})

    return messages


def create_thread(http_client: httpx.Client, graph_id: str = "roscoe_paralegal") -> str:
    """Create a new LangGraph thread with graph_id metadata."""
    response = http_client.post(
        f"{LANGGRAPH_URL}/threads",
        json={"metadata": {"graph_id": graph_id}}
    )
    response.raise_for_status()
    return response.json()["thread_id"]


def add_messages_to_thread(
    http_client: httpx.Client,
    thread_id: str,
    messages: List[Dict[str, Any]]
) -> bool:
    """Add messages to a LangGraph thread by running the agent."""
    # LangGraph threads store state after runs
    # We need to execute a run to save the messages

    # Use the update state endpoint to directly set messages
    response = http_client.post(
        f"{LANGGRAPH_URL}/threads/{thread_id}/state",
        json={
            "values": {"messages": messages},
            "as_node": "__start__"
        }
    )

    if response.status_code == 200:
        return True
    else:
        print(f"  Warning: Failed to update thread state: {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        return False


def get_run_title(run) -> str:
    """Generate a title for the run based on first user message."""
    if run.inputs:
        messages = run.inputs.get("messages", [])
        for msg in messages:
            if isinstance(msg, dict):
                msg_type = msg.get("type", msg.get("role", ""))
                if msg_type in ("human", "user"):
                    content = msg.get("content", "")
                    if content:
                        # Truncate to 50 chars
                        return content[:50] + ("..." if len(content) > 50 else "")
    return f"Run {str(run.id)[:8]}"


def main():
    parser = argparse.ArgumentParser(description="Import LangSmith traces to LangGraph threads")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back")
    parser.add_argument("--limit", type=int, default=50, help="Maximum runs to import")
    parser.add_argument("--dry-run", action="store_true", help="Don't create threads, just show what would be imported")
    parser.add_argument("--project", default="roscoe-local", help="LangSmith project name")
    parser.add_argument("--run-id", help="Import a specific run by ID")
    args = parser.parse_args()

    # Check API key
    if not os.environ.get("LANGSMITH_API_KEY"):
        print("Error: LANGSMITH_API_KEY environment variable not set")
        sys.exit(1)

    print(f"Connecting to LangSmith project: {args.project}")
    print(f"LangGraph URL: {LANGGRAPH_URL}")
    print(f"Looking back: {args.days} days")
    print(f"Max runs: {args.limit}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Initialize clients
    ls_client = LangSmithClient()
    http_client = httpx.Client(timeout=30.0)

    try:
        # Calculate time range
        start_time = datetime.now() - timedelta(days=args.days)

        if args.run_id:
            # Fetch specific run
            print(f"Fetching run: {args.run_id}")
            try:
                run = ls_client.read_run(args.run_id)
                runs = [run] if run else []
            except Exception as e:
                print(f"Error fetching run: {e}")
                runs = []
        else:
            # List runs from project - only top-level runs (no parent)
            print(f"Fetching runs from {args.project} since {start_time.isoformat()}...")
            all_runs = list(ls_client.list_runs(
                project_name=args.project,
                start_time=start_time,
                run_type="chain",  # Top-level agent runs
                limit=args.limit * 3,  # Fetch extra since we'll filter
                is_root=True,  # Only root runs (no parent)
            ))

            # Dedupe by trace_id (keep most recent per conversation)
            seen_traces = set()
            runs = []
            for run in sorted(all_runs, key=lambda r: r.start_time or datetime.min, reverse=True):
                trace_id = str(run.trace_id) if run.trace_id else str(run.id)
                if trace_id not in seen_traces:
                    seen_traces.add(trace_id)
                    runs.append(run)
                    if len(runs) >= args.limit:
                        break

        print(f"Found {len(runs)} runs")
        print()

        imported = 0
        skipped = 0

        for run in runs:
            title = get_run_title(run)
            run_time = run.start_time.isoformat() if run.start_time else "unknown"
            run_id_str = str(run.id)

            print(f"Run: {run_id_str[:8]}... | {run_time[:19]} | {title}")

            # Extract messages
            messages = extract_messages_from_run(run)

            if not messages:
                print(f"  Skipping: No messages found")
                skipped += 1
                continue

            print(f"  Messages: {len(messages)}")

            # Show first message preview
            if messages:
                first_msg = messages[0]
                preview = first_msg.get("content", "")[:80]
                print(f"  First: [{first_msg.get('type')}] {preview}...")

            if args.dry_run:
                print(f"  [DRY RUN] Would create thread with {len(messages)} messages")
                imported += 1
                continue

            # Create thread and add messages
            try:
                thread_id = create_thread(http_client)
                print(f"  Created thread: {thread_id}")

                if add_messages_to_thread(http_client, thread_id, messages):
                    print(f"  Added {len(messages)} messages")
                    imported += 1
                else:
                    print(f"  Failed to add messages")
                    skipped += 1

            except Exception as e:
                print(f"  Error: {e}")
                skipped += 1

            print()

        print("=" * 60)
        print(f"Summary: {imported} imported, {skipped} skipped")

    finally:
        http_client.close()


if __name__ == "__main__":
    main()
