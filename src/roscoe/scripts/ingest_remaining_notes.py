#!/usr/bin/env python3
"""Ingest remaining notes (14-20) to Graphiti."""

import json
import asyncio
from datetime import datetime
import sys
sys.path.insert(0, "/deps/Roscoe/src")

async def main():
    from roscoe.core.graphiti_client import add_case_episode, get_graphiti
    
    with open("/app/workspace_paralegal/caryn_mccay_clean_notes.json") as f:
        notes = json.load(f)
    
    # Start from note 13 (index 13) to 19 (7 remaining)
    notes_to_process = notes[13:20]
    
    print(f"Continuing ingestion: {len(notes_to_process)} remaining notes")
    
    await get_graphiti()
    
    success_count = 0
    for i, note in enumerate(notes_to_process):
        case_name = note.get("project_name", "Unknown")
        date = note.get("date", "Unknown date")
        author = note.get("author", "Unknown")
        text = note.get("note", "")
        categories = note.get("categories", [])
        note_id = note.get("id", "unknown")
        
        category_str = categories[0] if categories else "note"
        episode_name = f"Case note ({category_str}): {case_name} - {date}"
        
        episode_body = f"Case: {case_name}\nDate: {date}\nAuthor: {author}\n\n{text}"
        
        try:
            ref_time = datetime.strptime(date, "%Y-%m-%d")
        except:
            ref_time = datetime.now()
        
        print(f"[{i+14}/20] Note {note_id} ({date})")
        
        try:
            await add_case_episode(
                case_name=case_name,
                episode_name=episode_name,
                episode_body=episode_body,
                source="migration",
                reference_time=ref_time,
            )
            print(f"    OK")
            success_count += 1
        except Exception as e:
            print(f"    ERROR: {e}")
        
        await asyncio.sleep(0.3)
    
    print(f"\nDone: {success_count}/{len(notes_to_process)} ingested")

if __name__ == "__main__":
    asyncio.run(main())
