#!/usr/bin/env python3
"""
Stage 0: Notes Preprocessing

Strips notes.json to essential fields, identifies authors, and flags integration-generated notes.
This is the first step in the Memory Card pipeline.

Usage:
    python preprocess_notes.py [--input path] [--output path] [--stats]
"""

import json
import re
import argparse
from pathlib import Path
from typing import Optional
from collections import defaultdict


# =============================================================================
# Configuration
# =============================================================================

# Fields to keep from each note
KEEP_FIELDS = ["note", "author_name", "project_name", "last_activity", "id"]

# Author mapping table
AUTHOR_MAPPING = {
    # Staff members
    "Aaron Whaley": {"author_type": "staff", "author_id": "aaron_whaley", "entity_type": "Attorney"},
    "AaronW": {"author_type": "staff", "author_id": "aaron_whaley", "entity_type": "Attorney"},
    "Justin Chumley": {"author_type": "staff", "author_id": "justin_chumley", "entity_type": "DirectoryEntry"},
    "Justin Chumbley": {"author_type": "staff", "author_id": "justin_chumley", "entity_type": "DirectoryEntry"},  # Typo variant
    "Colleen Hargan": {"author_type": "staff", "author_id": "colleen_hargan", "entity_type": "DirectoryEntry"},
    "Colleen": {"author_type": "staff", "author_id": "colleen_hargan", "entity_type": "DirectoryEntry"},
    "Coleen Thea Madayag": {"author_type": "staff", "author_id": "coleen_madayag", "entity_type": "DirectoryEntry"},
    "Bryce Koon": {"author_type": "staff", "author_id": "bryce_koon", "entity_type": "DirectoryEntry"},
    "Jessa Galosmo": {"author_type": "staff", "author_id": "jessa_galosmo", "entity_type": "DirectoryEntry"},
    "Faye Gaither": {"author_type": "staff", "author_id": "faye_gaither", "entity_type": "DirectoryEntry"},
    "Sarena Tuttle": {"author_type": "staff", "author_id": "sarena_tuttle", "entity_type": "DirectoryEntry"},
    "Jessica Bottorff": {"author_type": "staff", "author_id": "jessica_bottorff", "entity_type": "DirectoryEntry"},
    "Aries": {"author_type": "staff", "author_id": "aries", "entity_type": "DirectoryEntry"},
    "Cameron Smith": {"author_type": "staff", "author_id": "cameron_smith", "entity_type": "DirectoryEntry"},
    # AI
    "Roscoe (AI Paralegal)": {"author_type": "ai", "author_id": "roscoe", "entity_type": "AI"},
    # Integrations
    "Filevine System": {"author_type": "integration", "author_id": "filevine", "entity_type": "System"},
    "Filevine Integration": {"author_type": "integration", "author_id": "filevine_copy", "entity_type": "System"},
    "Fuel Digital RingCentral Integration Service Account": {"author_type": "integration", "author_id": "ringcentral", "entity_type": "System"},
    "RingCentral": {"author_type": "integration", "author_id": "ringcentral", "entity_type": "System"},
    "Migrations+Iteam": {"author_type": "integration", "author_id": "migrations", "entity_type": "System"},
    "Vinesign Integration": {"author_type": "integration", "author_id": "vinesign", "entity_type": "System"},
    "New Integration": {"author_type": "integration", "author_id": "new_integration", "entity_type": "System"},
}

# Staff names for extracting real author from Filevine Integration notes
STAFF_NAMES = [
    "Aaron Whaley", "AaronW", "Justin Chumley", "Justin Chumbley",
    "Colleen Hargan", "Colleen", "Coleen Thea Madayag",
    "Bryce Koon", "Jessa Galosmo", "Faye Gaither", "Sarena Tuttle",
    "Jessica Bottorff", "Aries", "Cameron Smith"
]

# Note source detection patterns
NOTE_SOURCE_PATTERNS = {
    "voicemail": [
        r"Voice Message",
        r"Voicemail",
        r"Voicemail Preview",
        r"VoicemailPreview",
    ],
    "missed_call": [
        r"#missedcall",
        r"missed call.*was logged",
    ],
    "outbound_call": [
        r"#outboundcall",
        r"outbound call",
        r"A call from.*was logged",
    ],
    "inbound_call": [
        r"#inboundcall",
        r"inbound call",
    ],
    "email": [
        r"^__FW:",
        r"^__RE:",
        r"^From:\s+\[",
        r"From:.*\nTo:.*\nDate:",
    ],
    "fax": [
        r"#fax",
        r"fax sent",
        r"fax received",
        r"eFax",
    ],
}

# Skip patterns - notes that are just system noise
SKIP_PATTERNS = [
    r"^Phase Change:",
    r"^Insurance Company Added$",
    r"^Medical Provider Added$",
    r"^New Medical Provider Added$",
    r"^Expense Added$",
    r"^Lien Added$",
    r"^[cC]ontact Added$",
    r"^[dD]ocument Added$",
    r"^__Phase Changed By:__",
    r"^Task Completed:",
    r"^Task Created:",
    r"^\s*$",  # Empty notes
    r"^Automatic reply:",
    r"^Out of Office:",
]


# =============================================================================
# Helper Functions
# =============================================================================

def extract_real_author(note_text: str) -> Optional[str]:
    """
    Extract the real author from a Filevine Integration note.
    These notes are auto-copied from other parts of the system,
    and the real author is often embedded in the note text.
    """
    if not note_text:
        return None
    
    # Check first 300 chars for staff names
    search_text = note_text[:300].lower()
    
    for name in STAFF_NAMES:
        if name.lower() in search_text:
            return name
    
    return None


def detect_note_source(note_text: str, author_id: str) -> Optional[str]:
    """
    Detect the source type of an integration-generated note.
    """
    if not note_text:
        return None
    
    for source_type, patterns in NOTE_SOURCE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, note_text, re.IGNORECASE | re.MULTILINE):
                return source_type
    
    # Default sources based on integration type
    if author_id == "filevine_copy":
        return "auto_copy"
    elif author_id == "filevine":
        return "system_event"
    
    return None


def should_skip_note(note_text: str) -> bool:
    """
    Check if a note should be skipped (system noise).
    """
    if not note_text:
        return True
    
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, note_text.strip(), re.IGNORECASE):
            return True
    
    return False


def get_author_info(author_name: str, note_text: str) -> dict:
    """
    Get author information including type, id, and entity_type.
    For Filevine Integration notes, tries to extract the real author.
    """
    # Default for unknown authors
    result = {
        "author_type": "unknown",
        "author_id": None,
        "entity_type": None,
        "real_author": None,
    }
    
    if not author_name:
        return result
    
    # Check exact match first
    if author_name in AUTHOR_MAPPING:
        result.update(AUTHOR_MAPPING[author_name])
    else:
        # Try partial matching for variations
        author_lower = author_name.lower()
        for known_name, info in AUTHOR_MAPPING.items():
            if known_name.lower() in author_lower or author_lower in known_name.lower():
                result.update(info)
                break
    
    # Special handling for Filevine Integration - try to find real author
    if author_name == "Filevine Integration" and note_text:
        real_author = extract_real_author(note_text)
        if real_author:
            result["real_author"] = real_author
            # Update author_type to staff since we found the real author
            if real_author in AUTHOR_MAPPING:
                result["author_type"] = AUTHOR_MAPPING[real_author]["author_type"]
                result["author_id"] = AUTHOR_MAPPING[real_author]["author_id"]
    
    return result


def clean_note_text(note_text: str) -> str:
    """
    Basic cleaning of note text - removes some obvious noise.
    Full cleaning happens in the summarization stage.
    """
    if not note_text:
        return ""
    
    # Remove common boilerplate patterns that add no value
    # RingCentral footer
    note_text = re.sub(
        r"Thank you for using RingCentral!.*$",
        "",
        note_text,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # RingCentral legal footer
    note_text = re.sub(
        r"By subscribing to and/or using RingCentral.*$",
        "",
        note_text,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Filevine links
    note_text = re.sub(
        r"https://louisvilleaccidentlawyer\.filevineapp\.com[^\s]*",
        "[filevine-link]",
        note_text
    )
    
    # Multiple consecutive newlines
    note_text = re.sub(r"\n{3,}", "\n\n", note_text)
    
    # Multiple consecutive spaces
    note_text = re.sub(r" {2,}", " ", note_text)
    
    return note_text.strip()


def process_note(note: dict) -> Optional[dict]:
    """
    Process a single note, extracting essential fields and adding metadata.
    Returns None if the note should be skipped.
    """
    note_text = note.get("note", "")
    
    # Check if this note should be skipped
    if should_skip_note(note_text):
        return None
    
    # Get author information
    author_name = note.get("author_name", "")
    author_info = get_author_info(author_name, note_text)
    
    # Detect note source for integration notes
    note_source = None
    if author_info["author_type"] == "integration":
        note_source = detect_note_source(note_text, author_info.get("author_id"))
    
    # Clean the note text (basic cleaning only)
    cleaned_text = clean_note_text(note_text)
    
    # Build the output record
    result = {
        "note": cleaned_text,
        "project_name": note.get("project_name"),
        "last_activity": note.get("last_activity"),
        "author_name": author_name,
        "author_type": author_info["author_type"],
        "author_id": author_info["author_id"],
        "note_source": note_source,
        "id": note.get("id"),
    }
    
    # Add real_author if detected
    if author_info.get("real_author"):
        result["real_author"] = author_info["real_author"]
    
    return result


# =============================================================================
# Main Processing
# =============================================================================

def preprocess_notes(input_path: Path, output_path: Path, show_stats: bool = True) -> dict:
    """
    Main preprocessing function.
    
    Args:
        input_path: Path to notes.json
        output_path: Path for cleaned output
        show_stats: Whether to print statistics
    
    Returns:
        Dictionary with processing statistics
    """
    print(f"Loading notes from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        notes = json.load(f)
    
    print(f"Loaded {len(notes):,} notes")
    
    # Statistics tracking
    stats = {
        "total_input": len(notes),
        "total_output": 0,
        "skipped": 0,
        "by_author_type": defaultdict(int),
        "by_note_source": defaultdict(int),
        "unknown_authors": defaultdict(int),
        "real_authors_found": 0,
    }
    
    # Process notes
    processed_notes = []
    for note in notes:
        result = process_note(note)
        
        if result is None:
            stats["skipped"] += 1
            continue
        
        processed_notes.append(result)
        stats["total_output"] += 1
        stats["by_author_type"][result["author_type"]] += 1
        
        if result["note_source"]:
            stats["by_note_source"][result["note_source"]] += 1
        
        if result["author_type"] == "unknown":
            stats["unknown_authors"][result["author_name"]] += 1
        
        if result.get("real_author"):
            stats["real_authors_found"] += 1
    
    # Sort by project_name and last_activity for easier browsing
    processed_notes.sort(key=lambda x: (x.get("project_name") or "", x.get("last_activity") or ""))
    
    # Save output
    print(f"Saving {len(processed_notes):,} cleaned notes to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_notes, f, indent=2, ensure_ascii=False)
    
    # Calculate file sizes
    input_size = input_path.stat().st_size / (1024 * 1024)  # MB
    output_size = output_path.stat().st_size / (1024 * 1024)  # MB
    reduction = (1 - output_size / input_size) * 100
    
    stats["input_size_mb"] = round(input_size, 2)
    stats["output_size_mb"] = round(output_size, 2)
    stats["size_reduction_pct"] = round(reduction, 1)
    
    if show_stats:
        print("\n" + "=" * 60)
        print("PREPROCESSING STATISTICS")
        print("=" * 60)
        print(f"Input notes:     {stats['total_input']:,}")
        print(f"Output notes:    {stats['total_output']:,}")
        print(f"Skipped:         {stats['skipped']:,}")
        print(f"Input size:      {stats['input_size_mb']:.2f} MB")
        print(f"Output size:     {stats['output_size_mb']:.2f} MB")
        print(f"Size reduction:  {stats['size_reduction_pct']:.1f}%")
        print()
        print("By Author Type:")
        for author_type, count in sorted(stats["by_author_type"].items(), key=lambda x: -x[1]):
            print(f"  {author_type:15} {count:,}")
        print()
        print("By Note Source (integration notes only):")
        for source, count in sorted(stats["by_note_source"].items(), key=lambda x: -x[1]):
            print(f"  {source:15} {count:,}")
        print()
        print(f"Real authors extracted from Filevine Integration: {stats['real_authors_found']:,}")
        
        if stats["unknown_authors"]:
            print()
            print("Top Unknown Authors (may need to add to mapping):")
            for author, count in sorted(stats["unknown_authors"].items(), key=lambda x: -x[1])[:10]:
                print(f"  {author[:40]:40} {count:,}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Preprocess notes.json for Memory Card pipeline")
    parser.add_argument(
        "--input", 
        type=Path, 
        default=Path("/Volumes/X10 Pro/Roscoe/json-files/notes.json"),
        help="Path to input notes.json"
    )
    parser.add_argument(
        "--output", 
        type=Path, 
        default=Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/notes_cleaned.json"),
        help="Path for output cleaned notes"
    )
    parser.add_argument(
        "--stats", 
        action="store_true", 
        default=True,
        help="Show processing statistics"
    )
    parser.add_argument(
        "--no-stats", 
        action="store_false", 
        dest="stats",
        help="Hide processing statistics"
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    stats = preprocess_notes(args.input, args.output, args.stats)
    
    # Save stats to a separate file
    stats_path = args.output.parent / "preprocessing_stats.json"
    with open(stats_path, 'w') as f:
        # Convert defaultdicts to regular dicts for JSON serialization
        stats_json = {
            k: dict(v) if isinstance(v, defaultdict) else v
            for k, v in stats.items()
        }
        json.dump(stats_json, f, indent=2)
    print(f"\nStats saved to {stats_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())
