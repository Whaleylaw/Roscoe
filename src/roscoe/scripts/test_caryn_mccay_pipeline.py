#!/usr/bin/env python3
"""
Test the full Memory Card pipeline with Caryn McCay's case.

This script:
1. Preprocesses Caryn McCay's notes
2. Generates entity cards (filtered to her case)
3. Generates relationship cards (filtered to her case)  
4. Summarizes notes into episode cards
5. Shows what would be ingested into Graphiti
"""

import json
import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from preprocess_notes import process_note, KEEP_FIELDS
from memory_card_schema import create_entity_card, create_relationship_card, create_episode_card


CASE_NAME = "Caryn-McCay-MVA-7-30-2023"
INPUT_FILE = Path("/Volumes/X10 Pro/Roscoe/json-files/caryn_mccay_notes.json")
OUTPUT_DIR = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/test_caryn_mccay")


def preprocess_caryn_notes():
    """Stage 0: Preprocess notes."""
    print("\n--- Stage 0: Preprocessing Notes ---")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        notes = json.load(f)
    
    print(f"  Loaded {len(notes)} notes from {INPUT_FILE.name}")
    
    processed = []
    skipped = 0
    
    for note in notes:
        result = process_note(note)
        if result:
            processed.append(result)
        else:
            skipped += 1
    
    # Save processed notes
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "notes_cleaned.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed, f, indent=2, ensure_ascii=False)
    
    print(f"  Processed: {len(processed)}")
    print(f"  Skipped: {skipped}")
    print(f"  Saved to: {output_path}")
    
    return processed


def generate_caryn_entities():
    """Stage 1: Generate entity cards for this case."""
    print("\n--- Stage 1: Generating Entity Cards ---")
    
    entities = []
    
    # Create Case entity
    case = create_entity_card(
        entity_type="Case",
        name=CASE_NAME,
        attributes={
            "case_type": "MVA",
            "accident_date": "2023-07-30",
        },
        source_id=CASE_NAME,
        source_file="test",
    )
    entities.append(case)
    print(f"  Created Case: {CASE_NAME}")
    
    # Create Client entity
    client = create_entity_card(
        entity_type="Client",
        name="Caryn McCay",
        attributes={},
        source_id="Caryn McCay",
        source_file="test",
    )
    entities.append(client)
    print(f"  Created Client: Caryn McCay")
    
    # Save entities
    output_path = OUTPUT_DIR / "entities.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([e.model_dump() for e in entities], f, indent=2, default=str)
    
    print(f"  Total entities: {len(entities)}")
    print(f"  Saved to: {output_path}")
    
    return entities


def generate_caryn_relationships():
    """Stage 2: Generate relationship cards for this case."""
    print("\n--- Stage 2: Generating Relationship Cards ---")
    
    relationships = []
    
    # Case HasClient Client
    rel = create_relationship_card(
        edge_type="HasClient",
        source_type="Case",
        source_name=CASE_NAME,
        target_type="Client",
        target_name="Caryn McCay",
        attributes={},
        context=CASE_NAME,
    )
    relationships.append(rel)
    
    # Client PlaintiffIn Case
    rel2 = create_relationship_card(
        edge_type="PlaintiffIn",
        source_type="Client",
        source_name="Caryn McCay",
        target_type="Case",
        target_name=CASE_NAME,
        attributes={},
        context=CASE_NAME,
    )
    relationships.append(rel2)
    
    # Save relationships
    output_path = OUTPUT_DIR / "relationships.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([r.model_dump() for r in relationships], f, indent=2, default=str)
    
    print(f"  Total relationships: {len(relationships)}")
    print(f"  Saved to: {output_path}")
    
    return relationships


def summarize_caryn_notes(processed_notes: list):
    """Stage 3: Summarize notes into episode cards."""
    print("\n--- Stage 3: Summarizing Notes ---")
    
    from summarize_notes import template_summarize, extract_entities_from_text, load_known_entities
    
    known_entities = {}  # Load would go here if needed
    
    episodes = []
    template_count = 0
    fallback_count = 0
    
    for note in processed_notes:
        # Try template summarization
        summary = template_summarize(note)
        
        if summary:
            template_count += 1
        else:
            # Fallback
            note_text = note.get("note", "")
            summary = note_text[:150] + "..." if len(note_text) > 150 else note_text
            fallback_count += 1
        
        # Extract entities from text
        entities = extract_entities_from_text(note.get("note", ""), known_entities)
        
        episode = create_episode_card(
            case=note.get("project_name", CASE_NAME),
            date=note.get("last_activity", ""),
            summary=summary,
            entities=entities,
            edges=[],
            author=note.get("real_author") or note.get("author_name"),
            author_type=note.get("author_type"),
            note_source=note.get("note_source"),
            original_note_id=note.get("id"),
        )
        episodes.append(episode)
    
    # Save episodes
    output_path = OUTPUT_DIR / "episodes.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump([e.model_dump(by_alias=True) for e in episodes], f, indent=2, default=str, ensure_ascii=False)
    
    print(f"  Template-based: {template_count}")
    print(f"  Fallback: {fallback_count}")
    print(f"  Total episodes: {len(episodes)}")
    print(f"  Saved to: {output_path}")
    
    return episodes


def show_sample_output(entities, relationships, episodes):
    """Show sample of what would be ingested."""
    print("\n" + "=" * 60)
    print("SAMPLE OUTPUT")
    print("=" * 60)
    
    print("\n--- Sample Entity Card ---")
    print(json.dumps(entities[0].model_dump(), indent=2, default=str))
    
    print("\n--- Sample Relationship Card ---")
    print(json.dumps(relationships[0].model_dump(), indent=2, default=str))
    
    print("\n--- Sample Episode Cards (first 3) ---")
    for ep in episodes[:3]:
        print(json.dumps(ep.model_dump(by_alias=True), indent=2, default=str, ensure_ascii=False))
        print()


def main():
    print("=" * 60)
    print("TESTING MEMORY CARD PIPELINE - CARYN MCCAY")
    print("=" * 60)
    
    if not INPUT_FILE.exists():
        print(f"Error: Input file not found: {INPUT_FILE}")
        return 1
    
    # Run pipeline stages
    processed_notes = preprocess_caryn_notes()
    entities = generate_caryn_entities()
    relationships = generate_caryn_relationships()
    episodes = summarize_caryn_notes(processed_notes)
    
    # Show sample output
    show_sample_output(entities, relationships, episodes)
    
    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"  - notes_cleaned.json: {len(processed_notes)} notes")
    print(f"  - entities.json: {len(entities)} entities")
    print(f"  - relationships.json: {len(relationships)} relationships")
    print(f"  - episodes.json: {len(episodes)} episodes")
    print("\nTo ingest into Graphiti:")
    print(f"  python ingest_memory_cards.py --cards-dir {OUTPUT_DIR}")
    
    return 0


if __name__ == "__main__":
    exit(main())
