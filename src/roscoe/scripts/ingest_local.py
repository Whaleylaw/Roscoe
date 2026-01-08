#!/usr/bin/env python3
"""
Local ingestion script for Caryn McCay case.
Connects to FalkorDB via SSH tunnel on localhost:6379.

Usage:
    # First start the SSH tunnel:
    gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a -- -L 6379:localhost:6379 -N &
    
    # Then run this script:
    python src/roscoe/scripts/ingest_local.py --dry-run
    python src/roscoe/scripts/ingest_local.py --start 0 --batch-size 10
"""

import asyncio
import json
import argparse
import re
import os
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Set environment variables for local connection
os.environ["FALKORDB_HOST"] = "localhost"
os.environ["FALKORDB_PORT"] = "6380"  # FalkorDB is on 6380, Redis is on 6379

# Load API keys from backup file
api_keys_file = Path(__file__).parent.parent.parent.parent / "api-keys-backup.txt"
if api_keys_file.exists():
    with open(api_keys_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key not in os.environ:  # Don't override existing
                    os.environ[key] = value

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
    r"^\s*$",
    r"^Automatic reply:",
    r"^Out of Office:",
]

SKIP_REGEXES = [re.compile(p, re.IGNORECASE) for p in SKIP_PATTERNS]


def should_skip_note(note_text: str) -> bool:
    if not note_text or len(note_text.strip()) < 10:
        return True
    for regex in SKIP_REGEXES:
        if regex.search(note_text):
            return True
    return False


def clean_note_text(note_text: str) -> str:
    if not note_text:
        return ""
    text = note_text.replace("&nbsp;", " ")
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def format_note_as_episode(note: dict) -> tuple[str, str, datetime]:
    note_text = clean_note_text(note.get("note", ""))
    author = note.get("author_name", "Unknown")
    date_str = note.get("last_activity", "")
    time_str = note.get("time", "")
    note_id = note.get("id", 0)
    
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
    
    name = f"Note {note_id}: {date_str}"
    if author and author != "Filevine Integration":
        name += f" by {author}"
    
    body = f"Case: Caryn-McCay-MVA-7-30-2023\n"
    body += f"Client: Caryn McCay\n"
    body += f"Date: {date_str}\n"
    if author:
        body += f"Author: {author}\n"
    body += f"\n{note_text}"
    
    return name, body, dt


async def ingest_batch(notes: list, start_idx: int, batch_size: int, use_types: bool = True) -> int:
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
            print(f"  [{global_idx}] SKIP")
            continue
        
        name, body, dt = format_note_as_episode(note)
        
        try:
            kwargs = {
                "name": name,
                "episode_body": body,
                "source": EpisodeType.text,
                "source_description": "case_notes",
                "reference_time": dt,
                "group_id": GROUP_ID,
            }
            
            if use_types:
                kwargs["entity_types"] = ENTITY_TYPES_DICT
                kwargs["edge_types"] = EDGE_TYPES_DICT
                kwargs["edge_type_map"] = EDGE_TYPE_MAP
            
            result = await g.add_episode(**kwargs)
            nodes = len(result.nodes) if result.nodes else 0
            edges = len(result.edges) if result.edges else 0
            print(f"  [{global_idx}] OK: {nodes} nodes, {edges} edges - {name[:40]}")
            success_count += 1
        except Exception as e:
            print(f"  [{global_idx}] ERROR: {str(e)[:60]}")
    
    return success_count


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0, help="Start index")
    parser.add_argument("--batch-size", type=int, default=10, help="Notes per batch")
    parser.add_argument("--dry-run", action="store_true", help="Just count, don't ingest")
    parser.add_argument("--no-types", action="store_true", help="Skip custom entity types")
    args = parser.parse_args()
    
    # Load notes from GCS path on VM - we need local copy
    # For now, check if we have a local copy
    local_notes = Path("/Volumes/X10 Pro/Roscoe/json-files/caryn_mccay_notes.json")
    
    if not local_notes.exists():
        print("Notes file not found locally. Downloading from VM...")
        import subprocess
        result = subprocess.run([
            "gcloud", "compute", "scp",
            "aaronwhaley@roscoe-paralegal-vm:/mnt/workspace/projects/Caryn-McCay-MVA-7-30-2023/Case Information/notes.json",
            str(local_notes),
            "--zone=us-central1-a"
        ], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error downloading: {result.stderr}")
            return
        print("Downloaded!")
    
    print(f"Loading notes from {local_notes}...")
    with open(local_notes) as f:
        all_notes = json.load(f)
    
    print(f"Total notes: {len(all_notes)}")
    
    useful_notes = [n for n in all_notes if not should_skip_note(n.get("note", ""))]
    print(f"Useful notes (after filtering): {len(useful_notes)}")
    
    if args.dry_run:
        print("\n--- DRY RUN: First 5 useful notes ---")
        for i, note in enumerate(useful_notes[:5]):
            name, body, dt = format_note_as_episode(note)
            print(f"\n[{i}] {name}")
            print(f"    {body[:150]}...")
        return
    
    print(f"\n{'='*60}")
    print(f"Ingesting notes {args.start} to {args.start + args.batch_size - 1}")
    print(f"Custom types: {'OFF' if args.no_types else 'ON'}")
    print(f"{'='*60}\n")
    
    success = await ingest_batch(useful_notes, args.start, args.batch_size, not args.no_types)
    
    print(f"\n{'='*60}")
    print(f"Batch complete: {success} notes ingested")
    print(f"Next batch: --start {args.start + args.batch_size}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
