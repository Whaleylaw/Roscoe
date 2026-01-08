#!/usr/bin/env python3
"""
Stage 3: Note Summarization

Converts preprocessed notes to Episode Cards:
- Uses templates for integration notes (voicemail, call logs, etc.)
- Uses LLM (Gemini) for staff notes requiring summarization
- Extracts entities and relationships mentioned

Usage:
    python summarize_notes.py [--input path] [--output-dir path] [--batch-size N] [--max-notes N]
"""

import json
import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional
from collections import defaultdict

# For LLM calls
import google.generativeai as genai

from memory_card_schema import (
    EpisodeCard,
    EntityMention,
    EdgeMention,
    create_episode_card,
)


# =============================================================================
# Configuration
# =============================================================================

INPUT_PATH = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/notes_cleaned.json")
OUTPUT_DIR = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes")

# Load known entities for matching
ENTITIES_DIR = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")


# =============================================================================
# Entity Loading for Matching
# =============================================================================

def load_known_entities() -> dict:
    """
    Load known entities from generated entity cards.
    Returns a dict mapping entity names (lowercase) to their type.
    """
    entities = {}
    
    for file_name in [
        "cases.json",
        "clients.json",
        "insurers.json",
        "adjusters.json",
        "medical_providers.json",
        "lienholders.json",
    ]:
        path = ENTITIES_DIR / file_name
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for entity in data:
                    name = entity.get("name", "")
                    entity_type = entity.get("entity_type", "")
                    if name:
                        entities[name.lower()] = entity_type
    
    return entities


# Staff members for matching
STAFF_MEMBERS = {
    "aaron whaley": ("Attorney", "aaron_whaley"),
    "aaronw": ("Attorney", "aaron_whaley"),
    "justin chumley": ("Staff", "justin_chumley"),
    "justin chumbley": ("Staff", "justin_chumley"),
    "colleen hargan": ("Staff", "colleen_hargan"),
    "colleen": ("Staff", "colleen_hargan"),
    "bryce koon": ("Staff", "bryce_koon"),
    "jessa galosmo": ("Staff", "jessa_galosmo"),
    "faye gaither": ("Staff", "faye_gaither"),
    "sarena tuttle": ("Staff", "sarena_tuttle"),
    "jessica bottorff": ("Staff", "jessica_bottorff"),
    "aries": ("Staff", "aries"),
    "coleen thea madayag": ("Staff", "coleen_madayag"),
}


# =============================================================================
# Template-Based Summarization (for integration notes)
# =============================================================================

def extract_phone_info(note_text: str) -> dict:
    """Extract phone-related info from RingCentral notes."""
    info = {}
    
    # Extract caller/contact name
    name_match = re.search(r"Caller Name:\s*(.+?)(?:\n|$)", note_text)
    if name_match:
        info["contact_name"] = name_match.group(1).strip()
    
    # Extract phone number
    phone_match = re.search(r"Caller ID:\s*(.+?)(?:\n|$)", note_text)
    if phone_match:
        info["phone"] = phone_match.group(1).strip()
    
    # Extract staff member involved
    for staff_name in STAFF_MEMBERS:
        if staff_name in note_text.lower():
            info["staff_involved"] = staff_name.title()
            break
    
    return info


def summarize_voicemail(note: dict) -> str:
    """Generate summary for voicemail notes."""
    note_text = note.get("note", "")
    project_name = note.get("project_name", "")
    
    # Extract client name from project
    client_name = project_name.split("-")[0] + " " + project_name.split("-")[1] if "-" in project_name else project_name
    
    info = extract_phone_info(note_text)
    contact = info.get("contact_name", "caller")
    
    # Look for voicemail transcription
    transcription = ""
    trans_match = re.search(r'(?:Voicemail Preview:|Voicemail Transcription:)\s*["\']?(.+?)["\']?\s*(?:\n|$)', note_text, re.DOTALL | re.IGNORECASE)
    if trans_match:
        transcription = trans_match.group(1).strip()[:200]  # Limit length
        if len(trans_match.group(1).strip()) > 200:
            transcription += "..."
    
    if transcription:
        return f"Voicemail received from {contact}. Message: \"{transcription}\""
    else:
        return f"Voicemail received from {contact} regarding case {project_name}."


def summarize_missed_call(note: dict) -> str:
    """Generate summary for missed call notes."""
    note_text = note.get("note", "")
    project_name = note.get("project_name", "")
    
    info = extract_phone_info(note_text)
    contact = info.get("contact_name", "unknown caller")
    phone = info.get("phone", "")
    staff = info.get("staff_involved", "staff")
    
    return f"Missed call from {contact} ({phone}) to {staff}."


def summarize_outbound_call(note: dict) -> str:
    """Generate summary for outbound call notes."""
    note_text = note.get("note", "")
    project_name = note.get("project_name", "")
    
    info = extract_phone_info(note_text)
    contact = info.get("contact_name", "contact")
    
    # Extract staff from note
    staff_match = re.search(r"A call from\s+(\w+\s+\w+)", note_text)
    staff = staff_match.group(1) if staff_match else "Staff"
    
    return f"{staff} made outbound call to {contact} regarding case."


def summarize_inbound_call(note: dict) -> str:
    """Generate summary for inbound call notes."""
    note_text = note.get("note", "")
    
    info = extract_phone_info(note_text)
    contact = info.get("contact_name", "caller")
    
    return f"Inbound call received from {contact}."


def summarize_email(note: dict) -> str:
    """Generate summary for email notes."""
    note_text = note.get("note", "")
    
    # Extract subject
    subject_match = re.search(r"Subject:\s*(.+?)(?:\n|$)", note_text)
    subject = subject_match.group(1).strip() if subject_match else "No subject"
    
    # Extract from
    from_match = re.search(r"From:\s*(.+?)(?:\n|$)", note_text)
    sender = from_match.group(1).strip() if from_match else "unknown"
    
    # Clean up sender
    sender = re.sub(r'<[^>]+>', '', sender).strip()
    sender = sender[:50] if len(sender) > 50 else sender
    
    return f"Email from {sender}. Subject: {subject[:100]}"


def summarize_fax(note: dict) -> str:
    """Generate summary for fax notes."""
    note_text = note.get("note", "")
    
    if "sent" in note_text.lower():
        return "Fax sent regarding case."
    elif "received" in note_text.lower():
        return "Fax received regarding case."
    else:
        return "Fax communication regarding case."


def template_summarize(note: dict) -> Optional[str]:
    """
    Try to summarize using templates based on note_source.
    Returns None if template doesn't apply.
    """
    note_source = note.get("note_source")
    
    if note_source == "voicemail":
        return summarize_voicemail(note)
    elif note_source == "missed_call":
        return summarize_missed_call(note)
    elif note_source == "outbound_call":
        return summarize_outbound_call(note)
    elif note_source == "inbound_call":
        return summarize_inbound_call(note)
    elif note_source == "email":
        return summarize_email(note)
    elif note_source == "fax":
        return summarize_fax(note)
    
    return None


# =============================================================================
# LLM-Based Summarization
# =============================================================================

def setup_genai():
    """Configure the Gemini API."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        # Try to load from api-keys-backup.txt
        keys_file = Path("/Volumes/X10 Pro/Roscoe/api-keys-backup.txt")
        if keys_file.exists():
            with open(keys_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GOOGLE_API_KEY="):
                        api_key = line.split("=", 1)[1]
                        break
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash-exp')


def llm_summarize(note: dict, model, known_entities: dict) -> dict:
    """
    Use LLM to summarize a note and extract entities.
    Returns dict with 'summary', 'entities', 'edges'.
    """
    note_text = note.get("note", "")
    project_name = note.get("project_name", "")
    author = note.get("author_name", "")
    date = note.get("last_activity", "")
    
    # Extract client name from project
    parts = project_name.split("-") if project_name else []
    client_name = f"{parts[0]} {parts[1]}" if len(parts) >= 2 else ""
    
    prompt = f"""Summarize this legal case note concisely (1-2 sentences). Also extract any entities mentioned.

Case: {project_name}
Client: {client_name}
Author: {author}
Date: {date}

Note:
{note_text[:2000]}

Respond in this exact JSON format:
{{
  "summary": "Brief 1-2 sentence summary of what happened",
  "entities": [
    {{"type": "Client|Attorney|MedicalProvider|Insurer|Adjuster|Staff", "name": "Entity Name"}}
  ],
  "edges": [
    {{"type": "TreatingAt|HasClaim|ContactedBy", "from": "source entity", "to": "target entity"}}
  ]
}}

Only include entities and edges that are explicitly mentioned. Keep the summary factual and concise."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Extract JSON from response
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        result = json.loads(text)
        return {
            "summary": result.get("summary", "Note recorded."),
            "entities": result.get("entities", []),
            "edges": result.get("edges", []),
        }
    except Exception as e:
        # Fallback to simple summary
        return {
            "summary": note_text[:150] + "..." if len(note_text) > 150 else note_text,
            "entities": [],
            "edges": [],
        }


# =============================================================================
# Entity Extraction
# =============================================================================

def extract_entities_from_text(note_text: str, known_entities: dict) -> list[dict]:
    """
    Extract entities mentioned in note text by matching against known entities.
    """
    entities = []
    note_lower = note_text.lower()
    
    # Check for known entities
    for entity_name, entity_type in known_entities.items():
        if entity_name in note_lower:
            entities.append({
                "type": entity_type,
                "name": entity_name.title(),
            })
    
    # Check for staff members
    for staff_name, (staff_type, staff_id) in STAFF_MEMBERS.items():
        if staff_name in note_lower:
            entities.append({
                "type": staff_type,
                "name": staff_name.title(),
            })
    
    return entities


# =============================================================================
# Main Processing
# =============================================================================

def process_note(note: dict, model, known_entities: dict, use_llm: bool = True) -> Optional[EpisodeCard]:
    """
    Process a single note and return an EpisodeCard.
    """
    project_name = note.get("project_name")
    date = note.get("last_activity")
    note_text = note.get("note", "")
    
    if not project_name or not note_text.strip():
        return None
    
    # Try template summarization first
    summary = template_summarize(note)
    entities = []
    edges = []
    
    if summary is None and use_llm:
        # Use LLM for complex notes
        result = llm_summarize(note, model, known_entities)
        summary = result["summary"]
        entities = result.get("entities", [])
        edges = result.get("edges", [])
    elif summary is None:
        # Fallback without LLM
        summary = note_text[:200] + "..." if len(note_text) > 200 else note_text
    
    # Add entities found through text matching
    matched_entities = extract_entities_from_text(note_text, known_entities)
    for ent in matched_entities:
        if ent not in entities:
            entities.append(ent)
    
    return create_episode_card(
        case=project_name,
        date=date or datetime.now().strftime("%Y-%m-%d"),
        summary=summary,
        entities=entities,
        edges=edges,
        author=note.get("real_author") or note.get("author_name"),
        author_type=note.get("author_type"),
        note_source=note.get("note_source"),
        original_note_id=note.get("id"),
    )


def summarize_all_notes(
    input_path: Path,
    output_dir: Path,
    batch_size: int = 50,
    max_notes: Optional[int] = None,
    use_llm: bool = True,
) -> dict:
    """
    Process all notes and generate Episode Cards.
    """
    print(f"Loading notes from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        notes = json.load(f)
    
    if max_notes:
        notes = notes[:max_notes]
    
    print(f"Loaded {len(notes):,} notes to process")
    
    # Load known entities
    print("Loading known entities...")
    known_entities = load_known_entities()
    print(f"  Loaded {len(known_entities):,} known entities")
    
    # Setup LLM if needed
    model = None
    if use_llm:
        print("Setting up Gemini API...")
        model = setup_genai()
    
    # Process notes
    print(f"\nProcessing notes (batch_size={batch_size}, use_llm={use_llm})...")
    
    stats = {
        "total_input": len(notes),
        "total_output": 0,
        "by_source": defaultdict(int),
        "template_summarized": 0,
        "llm_summarized": 0,
        "errors": 0,
    }
    
    episodes_by_case = defaultdict(list)
    
    for i, note in enumerate(notes):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1:,}/{len(notes):,} notes...")
        
        try:
            episode = process_note(note, model, known_entities, use_llm)
            
            if episode:
                episodes_by_case[episode.case].append(episode)
                stats["total_output"] += 1
                
                if note.get("note_source"):
                    stats["by_source"][note["note_source"]] += 1
                    stats["template_summarized"] += 1
                else:
                    stats["llm_summarized"] += 1
        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] <= 5:
                print(f"  Error processing note {note.get('id')}: {e}")
    
    # Save episodes by case
    print(f"\nSaving episodes by case...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_episodes = []
    for case_name, episodes in episodes_by_case.items():
        # Save per-case file
        case_file = output_dir / "by_case" / f"{case_name}_episodes.json"
        case_file.parent.mkdir(parents=True, exist_ok=True)
        
        episode_dicts = [ep.model_dump(by_alias=True) for ep in episodes]
        with open(case_file, 'w', encoding='utf-8') as f:
            json.dump(episode_dicts, f, indent=2, ensure_ascii=False, default=str)
        
        all_episodes.extend(episode_dicts)
    
    # Save all episodes
    all_file = output_dir / "all_episodes.json"
    with open(all_file, 'w', encoding='utf-8') as f:
        json.dump(all_episodes, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"  Saved {len(all_episodes):,} episodes to {all_file.name}")
    print(f"  Saved {len(episodes_by_case):,} per-case files")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARIZATION SUMMARY")
    print("=" * 60)
    print(f"\nInput notes:       {stats['total_input']:,}")
    print(f"Output episodes:   {stats['total_output']:,}")
    print(f"Template-based:    {stats['template_summarized']:,}")
    print(f"LLM-based:         {stats['llm_summarized']:,}")
    print(f"Errors:            {stats['errors']:,}")
    print(f"\nCases with episodes: {len(episodes_by_case):,}")
    print("\nBy note source:")
    for source, count in sorted(stats["by_source"].items(), key=lambda x: -x[1]):
        print(f"  {source:15} {count:,}")
    
    # Save stats
    stats["by_source"] = dict(stats["by_source"])
    stats_path = output_dir / "summarization_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nStats saved to {stats_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Summarize notes into Episode Cards")
    parser.add_argument(
        "--input",
        type=Path,
        default=INPUT_PATH,
        help="Path to preprocessed notes_cleaned.json"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for output episode card files"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for processing"
    )
    parser.add_argument(
        "--max-notes",
        type=int,
        default=None,
        help="Maximum number of notes to process (for testing)"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM summarization (use templates only)"
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    summarize_all_notes(
        args.input,
        args.output_dir,
        batch_size=args.batch_size,
        max_notes=args.max_notes,
        use_llm=not args.no_llm,
    )
    return 0


if __name__ == "__main__":
    exit(main())
