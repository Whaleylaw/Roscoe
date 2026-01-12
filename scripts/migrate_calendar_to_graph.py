#!/usr/bin/env python3
"""
One-time migration of calendar.json events to knowledge graph.

Run once, then the JSON file can be archived/removed.

Usage:
    python scripts/migrate_calendar_to_graph.py

On VM:
    cd /home/aaronwhaley/roscoe
    python scripts/migrate_calendar_to_graph.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from roscoe.core.graph_manager import create_calendar_event


async def migrate():
    """Migrate calendar events from JSON to graph."""

    # Determine workspace path
    workspace = os.environ.get("GCS_WORKSPACE", "/mnt/workspace")
    calendar_path = Path(workspace) / "Database" / "calendar.json"

    if not calendar_path.exists():
        print(f"Calendar file not found at: {calendar_path}")
        print("Nothing to migrate.")
        return

    print(f"Reading calendar from: {calendar_path}")

    with open(calendar_path) as f:
        data = json.load(f)

    events = data.get("events", [])

    if not events:
        print("No events found in calendar.json")
        return

    print(f"Found {len(events)} events to migrate")

    migrated = 0
    failed = 0

    for i, event in enumerate(events, 1):
        title = event.get("title", "Untitled")
        date = event.get("date")

        if not date:
            print(f"  [{i}] SKIPPED - no date: {title}")
            failed += 1
            continue

        try:
            # Map JSON fields to graph entity fields
            result = await create_calendar_event(
                title=title,
                event_date=date,
                event_type=event.get("type", "task"),  # JSON might have "type"
                case_name=event.get("project_name"),   # JSON uses "project_name"
                priority=event.get("priority", "medium"),
                event_time=event.get("time"),
                notes=event.get("notes"),
                source="migration"
            )

            if result:
                status = "completed" if event.get("completed") else "pending"
                print(f"  [{i}] OK: {title} ({date}) -> {status}")
                migrated += 1
            else:
                print(f"  [{i}] FAILED: {title}")
                failed += 1

        except Exception as e:
            print(f"  [{i}] ERROR: {title} - {str(e)}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Migration complete!")
    print(f"  Migrated: {migrated}")
    print(f"  Failed:   {failed}")
    print(f"  Total:    {len(events)}")

    if migrated > 0 and failed == 0:
        # Rename the old file as backup
        backup_path = calendar_path.with_suffix(".json.bak")
        calendar_path.rename(backup_path)
        print(f"\nOriginal file backed up to: {backup_path}")
        print("The graph is now the source of truth for calendar events.")
    else:
        print(f"\nOriginal file preserved at: {calendar_path}")
        print("Review errors and re-run if needed.")


if __name__ == "__main__":
    print("Calendar Migration: JSON -> Knowledge Graph")
    print("=" * 50)
    asyncio.run(migrate())
