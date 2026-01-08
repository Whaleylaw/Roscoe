#!/usr/bin/env python3
"""
Ingest Caryn McCay case data into roscoe_graph_v2.

This script:
1. Loads and cleans notes (filters out system noise)
2. Ingests notes as episodes with custom entity types
3. Runs in batches with progress tracking

Usage:
    python ingest_caryn_mccay.py [--start N] [--batch-size M]
"""

import asyncio
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, "/deps/Roscoe/src")


# Notes to skip (system-generated noise)
SKIP_PATTERNS = [
    r"^Phase Change:",
    r"^Insurance Company Added$",
    r"^Medical Provider Added$",
    r"^New Medical Provider Added$",
    r"^Expense Added$",
    r"^Lien Added$",
    r"^Contact Added$",
    r"^Document Added$",
    r"^__Phase Changed By:__",
    r"^Task Completed:",
    r"^Task Created:",
    r"^\s*$",  # Empty notes
    r"^Automatic reply:",  # Auto-replies
    r"^Out of Office:",  # OOO messages
]

# Compile patterns
SKIP_REGEXES = [re.compile(p, re.IGNORECASE) for p in SKIP_PATTERNS]


def should_skip_note(note_text: str) -> bool:
    """Check if note should be skipped."""
    if not note_text or len(note_text.strip()) < 10:
        return True
    for regex in SKIP_REGEXES:
        if regex.search(note_text):
            return True
    return False


def clean_note_text(note_text: str) -> str:
    """Clean up note text for better LLM processing."""
    if not note_text:
        return ""
    
    # Remove excessive HTML-like entities
    text = note_text.replace("&nbsp;", " ")
    text = re.sub(r"&[a-z]+;", " ", text)
    
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    
    return text


def format_note_as_episode(note: dict) -> tuple[str, str, datetime]:
    """Format a note as an episode (name, body, timestamp)."""
    note_text = clean_note_text(note.get("note", ""))
    author = note.get("author_name", "Unknown")
    date_str = note.get("last_activity", "")
    time_str = note.get("time", "")
    note_id = note.get("id", 0)
    
    # Parse timestamp
    try:
        if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if time_str:
                try:
                    t = datetime.strptime(time_str, "%H:%M:%S").time()
                    dt = dt.replace(hour=t.hour, minute=t.minute, second=t.second)
                except:
                    pass
        else:
            dt = datetime.now()
    except:
        dt = datetime.now()
    
    # Create episode name
    name = f"Note {note_id}: {date_str}"
    if author and author != "Filevine Integration":
        name += f" by {author}"
    
    # Create episode body with context
    body = f"Case: Caryn-McCay-MVA-7-30-2023\n"
    body += f"Client: Caryn McCay\n"
    body += f"Date: {date_str}\n"
    if author:
        body += f"Author: {author}\n"
    body += f"\n{note_text}"
    
    return name, body, dt


async def ingest_batch(notes: list, start_idx: int, batch_size: int) -> int:
    """Ingest a batch of notes. Returns count of successfully ingested."""
    from roscoe.core.graphiti_client import (
        get_graphiti, ENTITY_TYPES_DICT, EDGE_TYPES_DICT, EDGE_TYPE_MAP
    )
    from graphiti_core.nodes import EpisodeType
    
    g = await get_graphiti()
    GROUP_ID = "roscoe_graph_v2"
    
    end_idx = min(start_idx + batch_size, len(notes))
    batch = notes[start_idx:end_idx]
    
    success_count = 0
    
    for i, note in enumerate(batch):
        global_idx = start_idx + i
        note_text = note.get("note", "")
        
        if should_skip_note(note_text):
            print(f"  [{global_idx}] SKIP: {note_text[:50]}...")
            continue
        
        name, body, dt = format_note_as_episode(note)
        
        try:
            result = await g.add_episode(
                name=name,
                episode_body=body,
                source=EpisodeType.text,
                source_description="case_notes",
                reference_time=dt,
                group_id=GROUP_ID,
                entity_types=ENTITY_TYPES_DICT,
                edge_types=EDGE_TYPES_DICT,
                edge_type_map=EDGE_TYPE_MAP,
            )
            nodes = len(result.nodes) if result.nodes else 0
            edges = len(result.edges) if result.edges else 0
            print(f"  [{global_idx}] OK: {nodes} nodes, {edges} edges - {name[:50]}")
            success_count += 1
        except Exception as e:
            print(f"  [{global_idx}] ERROR: {str(e)[:80]}")
    
    return success_count


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0, help="Start index")
    parser.add_argument("--batch-size", type=int, default=20, help="Notes per batch")
    parser.add_argument("--dry-run", action="store_true", help="Just count, don't ingest")
    args = parser.parse_args()
    
    # Load notes
    notes_path = "/mnt/workspace/projects/Caryn-McCay-MVA-7-30-2023/Case Information/notes.json"
    print(f"Loading notes from {notes_path}...")
    
    with open(notes_path) as f:
        all_notes = json.load(f)
    
    print(f"Total notes: {len(all_notes)}")
    
    # Filter notes
    useful_notes = [n for n in all_notes if not should_skip_note(n.get("note", ""))]
    print(f"Useful notes (after filtering): {len(useful_notes)}")
    
    if args.dry_run:
        print("\n--- DRY RUN: First 10 useful notes ---")
        for i, note in enumerate(useful_notes[:10]):
            name, body, dt = format_note_as_episode(note)
            print(f"\n[{i}] {name}")
            print(f"    {body[:200]}...")
        return
    
    # Ingest batch
    print(f"\n{'='*60}")
    print(f"Ingesting notes {args.start} to {args.start + args.batch_size - 1}")
    print(f"{'='*60}\n")
    
    success = await ingest_batch(useful_notes, args.start, args.batch_size)
    
    print(f"\n{'='*60}")
    print(f"Batch complete: {success} notes ingested")
    print(f"Next batch: --start {args.start + args.batch_size}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
