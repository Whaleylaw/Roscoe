#!/usr/bin/env python3
"""
Ingest case notes from JSON file into Graphiti as episodes.

Reads from: notes_cleaned.json (17,101 notes)
Creates: Episode entities with automatic entity linking via Graphiti LLM

Uses Graphiti (unstructured layer) - notes are free-form text.
Enhances episode body with Case + Client context for reliable linking.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from roscoe.core.graphiti_client import add_case_episode


# =============================================================================
# Helper Functions
# =============================================================================

def extract_client_name(case_name: str) -> str:
    """
    Extract client name from case name.

    Example:
        "Abby-Sitgraves-MVA-7-13-2024" → "Abby Sitgraves"
        "Estate-of-Betty-Prince-Premise-7-14-2020" → "Estate of Betty Prince"

    Args:
        case_name: Case folder name (hyphenated)

    Returns:
        Client name with spaces
    """
    # Remove date suffix (last 3 components)
    # Format: Name-Name-Type-M-D-YYYY or Name-Name-Type-MM-DD-YYYY
    parts = case_name.split("-")

    # Find where the date starts (look for case type keywords)
    case_types = ["MVA", "WC", "Premise", "DB", "SF", "Med-Mal", "Dual"]

    # Find last occurrence of case type
    type_index = -1
    for i, part in enumerate(parts):
        if part in case_types:
            type_index = i

    if type_index > 0:
        # Everything before case type is the client name
        client_parts = parts[:type_index]
    else:
        # Fallback: assume last 3 components are date
        client_parts = parts[:-3]

    # Join with spaces and handle "Estate-of" pattern
    client_name = " ".join(client_parts)
    client_name = client_name.replace("Estate of", "Estate of")

    return client_name


def build_enhanced_episode_body(note: Dict) -> str:
    """
    Build episode body with Case + Client context header.

    Format:
        Case: Elizabeth-Lindsey-MVA-12-01-2024
        Client: Elizabeth Lindsey

        [Original note content]

    This gives Graphiti's LLM maximum context for entity linking.

    Args:
        note: Note dictionary from notes_cleaned.json

    Returns:
        Enhanced episode body with context header
    """
    case_name = note["project_name"]
    client_name = extract_client_name(case_name)
    note_text = note["note"]

    # Build enhanced body
    enhanced_body = f"""Case: {case_name}
Client: {client_name}

{note_text}""".strip()

    return enhanced_body


# =============================================================================
# Episode Creation
# =============================================================================

async def create_episode_from_note(note: Dict, case_exists_cache: set) -> bool:
    """
    Create a Graphiti episode from a case note.

    Args:
        note: Note dictionary with fields: note, project_name, last_activity, author_name, etc.
        case_exists_cache: Set of case names that exist in graph (for validation)

    Returns:
        True if created successfully, False if error
    """
    try:
        case_name = note["project_name"]

        # Skip if case doesn't exist in graph
        if case_name not in case_exists_cache:
            return False

        # Build enhanced episode body with Case + Client context
        episode_body = build_enhanced_episode_body(note)

        # Build episode name
        author = note.get("author_name", "Unknown")
        date_str = note.get("last_activity", "")
        episode_name = f"{author} - {date_str}" if author else f"Note - {date_str}"

        # Parse reference time
        reference_time = None
        if date_str:
            try:
                reference_time = datetime.fromisoformat(date_str)
            except:
                reference_time = datetime.now()

        # Determine source
        note_source = note.get("note_source", "migration")
        source_desc = f"migration:{note_source}" if note_source else "migration"

        # Create episode via Graphiti
        await add_case_episode(
            case_name=case_name,
            episode_name=episode_name,
            episode_body=episode_body,
            source=source_desc,
            reference_time=reference_time,
            use_custom_types=False  # Disable custom types for now
        )

        return True

    except Exception as e:
        print(f"  ❌ Error creating episode for note {note.get('id', 'unknown')}: {e}")
        return False


# =============================================================================
# Case Validation
# =============================================================================

async def get_existing_cases() -> set:
    """
    Query graph for all existing Case entities.

    Returns:
        Set of case names
    """
    from roscoe.core.graphiti_client import run_cypher_query

    try:
        result = await run_cypher_query('''
            MATCH (c:Entity {entity_type: 'Case'})
            RETURN c.name as name
        ''')

        return {row["name"] for row in result if row.get("name")}
    except Exception as e:
        print(f"⚠️  Warning: Could not fetch case list from graph: {e}")
        return set()


# =============================================================================
# Main Ingestion Function
# =============================================================================

async def ingest_notes(
    notes_file: str = "/Volumes/X10 Pro/Roscoe/json-files/memory-cards/notes_cleaned.json",
    checkpoint_file: str = "/tmp/notes_ingestion_checkpoint.txt",
    resume: bool = True
):
    """
    Ingest all case notes as Graphiti episodes.

    Args:
        notes_file: Path to notes_cleaned.json
        checkpoint_file: Path to checkpoint file for resuming
        resume: Whether to resume from checkpoint (default True)
    """
    start_time = datetime.now()

    print("\n" + "="*80)
    print("🚀 ROSCOE NOTES INGESTION TO GRAPHITI")
    print("="*80)
    print(f"Start time: {start_time.isoformat()}")
    print(f"Notes file: {notes_file}")
    print(f"Checkpoint: {checkpoint_file}")

    # Load notes
    print(f"\n📖 Loading notes from {notes_file}...")
    with open(notes_file, 'r') as f:
        all_notes = json.load(f)

    print(f"✅ Loaded {len(all_notes)} notes")

    # Get existing cases from graph
    print(f"\n🔍 Fetching existing cases from graph...")
    case_exists_cache = await get_existing_cases()
    print(f"✅ Found {len(case_exists_cache)} cases in graph")

    # Check for checkpoint
    start_index = 0
    if resume and Path(checkpoint_file).exists():
        with open(checkpoint_file, 'r') as f:
            start_index = int(f.read().strip())
        print(f"📍 Resuming from checkpoint: {start_index}/{len(all_notes)}")

    # Process notes
    print(f"\n📝 Creating episodes...")
    print("="*80)

    created = 0
    skipped = 0
    errors = 0

    for i, note in enumerate(all_notes[start_index:], start=start_index):
        success = await create_episode_from_note(note, case_exists_cache)

        if success:
            created += 1
        elif note["project_name"] not in case_exists_cache:
            skipped += 1  # Case doesn't exist
        else:
            errors += 1

        # Progress indicator every 100 notes
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i + 1}/{len(all_notes)} processed (✅ {created} created, ⏭️  {skipped} skipped, ❌ {errors} errors)")

            # Update checkpoint
            with open(checkpoint_file, 'w') as f:
                f.write(str(i + 1))

        # Brief pause to avoid overwhelming Graphiti
        if (i + 1) % 10 == 0:
            await asyncio.sleep(0.1)

    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "="*80)
    print("✅ NOTES INGESTION COMPLETE!")
    print("="*80)
    print(f"Total notes processed: {len(all_notes) - start_index}")
    print(f"  ✅ Created: {created}")
    print(f"  ⏭️  Skipped (no case): {skipped}")
    print(f"  ❌ Errors: {errors}")
    print(f"Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
    print(f"Rate: {created/duration:.1f} episodes/second")
    print("="*80 + "\n")

    # Clean up checkpoint on success
    if Path(checkpoint_file).exists():
        Path(checkpoint_file).unlink()
        print("✅ Checkpoint file removed")


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import sys

    # Allow custom paths via command line
    if len(sys.argv) > 1:
        notes_file = sys.argv[1]
        checkpoint_file = sys.argv[2] if len(sys.argv) > 2 else "/tmp/notes_ingestion_checkpoint.txt"
    else:
        notes_file = "/Volumes/X10 Pro/Roscoe/json-files/memory-cards/notes_cleaned.json"
        checkpoint_file = "/tmp/notes_ingestion_checkpoint.txt"

    asyncio.run(ingest_notes(notes_file, checkpoint_file))
