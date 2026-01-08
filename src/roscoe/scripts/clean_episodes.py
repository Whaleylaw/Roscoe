#!/usr/bin/env python3
"""
Clean and Filter Episodes for Ingestion

Removes vague/generic episodes that don't add meaningful narrative.

Examples of episodes to REMOVE:
- "New Lien added" (no details)
- "Database Updated" (just metadata)
- "Case Notes Updated" (generic)
- Episodes with <10 words
- Episodes that are just field updates

Examples to KEEP:
- "Called State Farm to confirm coverage - adjuster unavailable"
- "Sent medical records request to UK Hospital via fax with signed HIPAA"
- "Client reported increased pain in lower back, referred to Dr. Smith"

Usage:
    python -m roscoe.scripts.clean_episodes --analyze  # Show what would be removed
    python -m roscoe.scripts.clean_episodes --clean    # Create cleaned file
"""

import json
import re
from pathlib import Path
from collections import Counter


# Patterns for vague/generic episodes to remove
VAGUE_PATTERNS = [
    r"^New \w+ added$",  # "New Lien added", "New Provider added"
    r"^Database [Uu]pdated",
    r"^Case [Nn]otes [Uu]pdated",
    r"^\w+ [Uu]pdated$",  # "Insurance Updated", "Provider Updated"
    r"^Activity recorded",
    r"^Medical providers database updated",
    r"^Updated [\w\s]+ database",
    # Standard welcome/onboarding templates (auto-generated for every case)
    r"Contact .+ and do Welcome Call and send Welcome Email",
    r".*Welcome Call.*Welcome Email.*Confirm treatment providers",
    r"^Enter New Client Information & Assign Case Manager$",
    r"^Time to check in with client again$",
    r"^Send Medical Record and Bill Requests for .+$",
    r"^Draft & File Complaint & Disc Req PP Def$",
    r"Two Week follow up with client initiated",
    r"Phase Changed",
]

# Minimum content length (excluding case header)
MIN_CONTENT_LENGTH = 20


def is_vague_episode(episode: dict) -> tuple[bool, str]:
    """
    Check if episode is too vague to be useful.

    Returns: (is_vague: bool, reason: str)
    """
    episode_body = episode.get('episode_body', '')
    source_desc = episode.get('source_description', '')

    # Filter out ONLY "integration: Filevine System" (exact match)
    # Keep "integration: Filevine Integration" and other variations
    if source_desc == "integration: Filevine System":
        return True, "Filevine System integration (exact match)"

    # Remove case header to get actual content
    lines = episode_body.split('\n')
    content_lines = []
    for line in lines:
        if line.startswith('Case:') or line.startswith('Client:') or not line.strip():
            continue
        content_lines.append(line)

    actual_content = '\n'.join(content_lines).strip()

    # Check if empty after removing headers
    if not actual_content:
        return True, "Empty content (only case/client header)"

    # Check minimum length
    if len(actual_content) < MIN_CONTENT_LENGTH:
        return True, f"Too short ({len(actual_content)} chars)"

    # Check vague patterns
    for pattern in VAGUE_PATTERNS:
        if re.match(pattern, actual_content, re.IGNORECASE):
            return True, f"Matches vague pattern: {pattern}"

    # Check if it's just field update notation (contains only __FIELD__: value)
    if re.match(r'^(__\w+__:\s*.+\s*)+$', actual_content):
        return True, "Just field updates (no narrative)"

    return False, ""


def analyze_episodes(episodes_path: Path):
    """Analyze episodes and show what would be removed."""
    with open(episodes_path) as f:
        all_episodes = json.load(f)

    print(f"Total episodes: {len(all_episodes)}")
    print()

    vague_episodes = []
    vague_reasons = Counter()

    for ep in all_episodes:
        is_vague, reason = is_vague_episode(ep)

        if is_vague:
            vague_episodes.append({
                'case': ep.get('case_name', 'Unknown'),
                'name': ep.get('episode_name', 'Unknown'),
                'body': ep.get('episode_body', '')[:200],
                'reason': reason
            })
            vague_reasons[reason] += 1

    print(f"Vague episodes to remove: {len(vague_episodes)}")
    print(f"Episodes to keep: {len(all_episodes) - len(vague_episodes)}")
    print()

    print("Removal reasons:")
    for reason, count in vague_reasons.most_common():
        print(f"  - {reason}: {count}")
    print()

    print("Sample vague episodes (first 10):")
    for i, ep in enumerate(vague_episodes[:10], 1):
        print(f"\n{i}. {ep['case']} - {ep['name']}")
        print(f"   Reason: {ep['reason']}")
        print(f"   Body: {ep['body'][:150]}...")


def clean_episodes(episodes_path: Path, output_path: Path):
    """Remove vague episodes and create cleaned file."""
    with open(episodes_path) as f:
        all_episodes = json.load(f)

    print(f"Loading {len(all_episodes)} episodes...")

    cleaned = []
    removed = []

    for ep in all_episodes:
        is_vague, reason = is_vague_episode(ep)

        if is_vague:
            removed.append(ep)
        else:
            cleaned.append(ep)

    print(f"Kept: {len(cleaned)}")
    print(f"Removed: {len(removed)}")
    print()

    # Save cleaned version
    with open(output_path, 'w') as f:
        json.dump(cleaned, f, indent=2)

    print(f"✅ Saved cleaned episodes to: {output_path}")

    # Save removed for review
    removed_path = output_path.parent / "removed_episodes.json"
    with open(removed_path, 'w') as f:
        json.dump(removed, f, indent=2)

    print(f"📋 Saved removed episodes to: {removed_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Clean vague episodes')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze and show what would be removed')
    parser.add_argument('--clean', action='store_true',
                       help='Create cleaned file')
    parser.add_argument('--input', type=str,
                       default="/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/notes_as_episodes.json",
                       help='Input file path')
    parser.add_argument('--output', type=str,
                       default="/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/cleaned_episodes.json",
                       help='Output file path')
    args = parser.parse_args()

    episodes_path = Path(args.input)
    output_path = Path(args.output)

    if not episodes_path.exists():
        print(f"❌ Input file not found: {episodes_path}")
        return

    print("=" * 70)
    print("EPISODE CLEANING")
    print("=" * 70)
    print(f"Input: {episodes_path}")
    print()

    if args.analyze:
        analyze_episodes(episodes_path)
    elif args.clean:
        clean_episodes(episodes_path, output_path)
    else:
        print("Specify --analyze or --clean")


if __name__ == "__main__":
    main()
