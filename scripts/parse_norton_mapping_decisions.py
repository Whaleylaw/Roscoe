#!/usr/bin/env python3
"""
Parse Norton mapping decisions from marked NORTON_MAPPING.md file.

Extracts all [x] REPLACE decisions and creates replacement mapping.
"""

import re
from pathlib import Path


def parse_mapping_file(mapping_file: Path):
    """Parse marked mapping file to extract replacement decisions."""

    with open(mapping_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by provider sections (## N. OLD: ...)
    sections = re.split(r'## (\d+)\. OLD: (.+?)$', content, flags=re.MULTILINE)

    replacements = []

    # Process sections in groups of 3 (number, old_name, section_content)
    for i in range(1, len(sections), 3):
        if i + 2 >= len(sections):
            break

        section_num = sections[i]
        old_name = sections[i + 1].strip()
        section_content = sections[i + 2]

        # Check if marked for replacement
        if '[ x]' in section_content or '[x ]' in section_content or '[x]' in section_content:
            # Extract the match number
            match_num_pattern = r'\[ x\] REPLACE with match #([_\d]+)'
            match_num_search = re.search(match_num_pattern, section_content)

            if not match_num_search:
                # Try alternate pattern
                match_num_pattern = r'\[x \] REPLACE with match #([_\d]+)'
                match_num_search = re.search(match_num_pattern, section_content)

            if not match_num_search:
                # Try pattern with custom provider name in notes
                custom_pattern = r'\[ x\] REPLACE.*?(?:Update with|connect this to|specify which one above)\s+([^\n]+)'
                custom_search = re.search(custom_pattern, section_content)

                if custom_search:
                    custom_name = custom_search.group(1).strip().rstrip('.')
                    replacements.append({
                        'old_name': old_name,
                        'new_name': custom_name,
                        'match_type': 'custom'
                    })
                    continue

            # Extract the top N matches
            matches_section = re.search(r'\*\*Top 5 Matches from New Roster:\*\*(.*?)\*\*DECISION:\*\*', section_content, re.DOTALL)

            if matches_section:
                matches_text = matches_section.group(1)

                # Parse each match
                match_lines = re.findall(r'(\d+)\. \*\*(.+?)\*\* \((\d+)% match\)', matches_text)

                if match_num_search:
                    match_num_str = match_num_search.group(1).strip('_')

                    if match_num_str.isdigit():
                        match_num = int(match_num_str)

                        # Find the corresponding new provider name
                        for m_num, m_name, m_score in match_lines:
                            if int(m_num) == match_num:
                                replacements.append({
                                    'old_name': old_name,
                                    'new_name': m_name.strip(),
                                    'match_num': match_num,
                                    'match_score': int(m_score),
                                    'match_type': 'numbered'
                                })
                                break

    return replacements


def main():
    """Parse Norton mapping file."""

    mapping_file = Path("/Volumes/X10 Pro/Roscoe/provider-mappings/NORTON_MAPPING.md")

    print("="*70)
    print("PARSING NORTON MAPPING DECISIONS")
    print("="*70)
    print()

    replacements = parse_mapping_file(mapping_file)

    print(f"Found {len(replacements)} replacement decisions:\n")

    for idx, repl in enumerate(replacements, 1):
        print(f"{idx}. OLD: {repl['old_name']}")
        print(f"   NEW: {repl['new_name']}")
        if repl.get('match_type') == 'numbered':
            print(f"   Match: #{repl['match_num']} ({repl['match_score']}% similarity)")
        else:
            print(f"   Type: {repl['match_type']}")
        print()

    # Save to JSON for script execution
    output_file = Path("/Volumes/X10 Pro/Roscoe/norton_replacements.json")
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(replacements, f, indent=2)

    print(f"✓ Saved to: {output_file}")
    print(f"\n✅ Parsed {len(replacements)} Norton provider replacements")


if __name__ == "__main__":
    main()
