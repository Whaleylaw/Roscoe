#!/usr/bin/env python3
"""
Create a human-readable markdown summary from merged episode file.
"""

import json
from pathlib import Path
from collections import defaultdict


def create_summary(merged_path: Path, output_path: Path):
    """Create markdown summary from merged JSON."""

    with open(merged_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    case_name = data.get('case_name', 'Unknown')
    total_episodes = data.get('total_episodes', 0)
    episodes = data.get('episodes', [])

    # Collect all unique entities
    entities_by_type = defaultdict(set)
    episode_summaries = []

    for episode in episodes:
        ep_name = episode.get('episode_name', 'Unnamed')
        valid_at = episode.get('valid_at', 'Unknown date')
        natural_lang = episode.get('natural_language', '')

        # Extract entities
        entities_in_episode = []
        rels = episode.get('proposed_relationships', {})
        for rel_type, entity_list in rels.items():
            if not isinstance(entity_list, list):
                continue
            for entity_ref in entity_list:
                if not isinstance(entity_ref, dict):
                    continue
                entity_type = entity_ref.get('entity_type', 'Unknown')
                entity_name = entity_ref.get('entity_name', 'Unknown')
                relevance = entity_ref.get('relevance', '')

                entities_by_type[entity_type].add(entity_name)
                entities_in_episode.append(f"**{entity_type}**: {entity_name}")

        # Store episode summary
        episode_summaries.append({
            'name': ep_name,
            'date': valid_at,
            'narrative': natural_lang[:200] + '...' if len(natural_lang) > 200 else natural_lang,
            'entities': entities_in_episode
        })

    # Write markdown
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Merged Episode Review: {case_name}\n\n")
        f.write(f"**Total Episodes:** {total_episodes}\n\n")
        f.write(f"**Generated from:** `merged_{case_name}.json`\n\n")
        f.write("---\n\n")

        # Entity summary
        f.write("## Entity Summary\n\n")
        f.write("All unique entities mentioned across episodes:\n\n")

        for entity_type in sorted(entities_by_type.keys()):
            entity_names = sorted(entities_by_type[entity_type])
            f.write(f"### {entity_type} ({len(entity_names)})\n\n")
            for name in entity_names:
                f.write(f"- {name}\n")
            f.write("\n")

        f.write("---\n\n")

        # Episode details (first 10 as examples)
        f.write("## Sample Episodes (First 10)\n\n")
        for i, ep in enumerate(episode_summaries[:10], 1):
            f.write(f"### {i}. {ep['name']}\n\n")
            f.write(f"**Date:** {ep['date']}\n\n")
            f.write(f"**Entities:**\n")
            if ep['entities']:
                for entity in ep['entities']:
                    f.write(f"- {entity}\n")
            else:
                f.write("- *(none)*\n")
            f.write(f"\n**Narrative:**\n\n")
            f.write(f"{ep['narrative']}\n\n")
            f.write("---\n\n")

        # Full episode list
        f.write(f"## All {total_episodes} Episodes\n\n")
        for i, ep in enumerate(episode_summaries, 1):
            entity_count = len(ep['entities'])
            f.write(f"{i}. **{ep['name']}** ({ep['date']}) - {entity_count} entities\n")
        f.write("\n")

        f.write("---\n\n")
        f.write("## Review Checklist\n\n")
        f.write("- [ ] Entity names are clean (no annotation text like '(WHALEY STAFF → ...')\n")
        f.write("- [ ] Entity types are correct (CaseManager vs Attorney)\n")
        f.write("- [ ] No duplicate entities with slight name variations\n")
        f.write("- [ ] Court divisions properly identified\n")
        f.write("- [ ] All relevant entities captured\n")
        f.write("- [ ] No ignored entities included\n")

    print(f"✓ Summary created: {output_path}")


def main():
    base_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes")
    case_name = "Abby-Sitgraves-MVA-7-13-2024"

    merged_path = base_dir / f"merged_{case_name}.json"
    output_path = Path("/Volumes/X10 Pro/Roscoe") / f"merged_{case_name}.md"

    create_summary(merged_path, output_path)


if __name__ == "__main__":
    main()
