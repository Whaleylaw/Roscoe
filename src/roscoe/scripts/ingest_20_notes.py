#!/usr/bin/env python3
"""Ingest 20 cleaned notes to Graphiti."""

import json
import asyncio
from datetime import datetime
import sys
import traceback

sys.path.insert(0, "/deps/Roscoe/src")

async def ingest_note(add_episode_func, note, index, total):
    """Ingest a single note as an episode."""
    case_name = note.get("project_name", "Unknown")
    date = note.get("date", "Unknown date")
    time_str = note.get("time", "")
    author = note.get("author", "Unknown")
    text = note.get("note", "")
    categories = note.get("categories", [])
    note_id = note.get("id", "unknown")
    
    category_str = categories[0] if categories else "note"
    episode_name = f"Case note ({category_str}): {case_name} - {date}"
    
    episode_body = f"""Case: {case_name}
Date: {date} {time_str or ""}
Author: {author}
Categories: {", ".join(categories) if categories else "general"}

{text}"""

    try:
        ref_time = datetime.strptime(date, "%Y-%m-%d") if date and date != "Unknown date" else datetime.now()
    except:
        ref_time = datetime.now()
    
    print(f"[{index+1}/{total}] Note {note_id} ({date}) by {author}")
    preview = text[:60].replace("\n", " ")
    print(f"    {preview}...")
    
    try:
        await add_episode_func(
            case_name=case_name,
            episode_name=episode_name,
            episode_body=episode_body,
            source="migration",
            reference_time=ref_time,
        )
        print(f"    OK")
        return True
    except Exception as e:
        print(f"    ERROR: {e}")
        traceback.print_exc()
        return False


async def main():
    print("Starting ingestion...")
    
    try:
        from roscoe.core.graphiti_client import add_case_episode, get_graphiti, CASE_DATA_GROUP_ID
        
        print(f"CASE_DATA_GROUP_ID: {CASE_DATA_GROUP_ID}")
        
        # Load notes
        with open("/app/workspace_paralegal/caryn_mccay_clean_notes.json") as f:
            notes = json.load(f)
        
        notes_to_process = notes[:20]
        
        print(f"=== GRAPHITI EPISODE INGESTION ===")
        print(f"Processing: {len(notes_to_process)} notes")
        print()
        
        print("Initializing Graphiti...")
        await get_graphiti()
        print("Connected!")
        print()
        
        success_count = 0
        start_time = datetime.now()
        
        for i, note in enumerate(notes_to_process):
            success = await ingest_note(add_case_episode, note, i, len(notes_to_process))
            if success:
                success_count += 1
            await asyncio.sleep(0.3)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print()
        print(f"=== COMPLETE ===")
        print(f"Success: {success_count}/{len(notes_to_process)}")
        print(f"Time: {elapsed:.1f}s ({elapsed/len(notes_to_process):.1f}s per note)")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
