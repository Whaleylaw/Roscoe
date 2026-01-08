#!/usr/bin/env python3
"""
Clean graphiti_client.py by removing Graphiti library dependencies.

Keeps:
- Pydantic entity models
- ENTITY_TYPES list
- EDGE_TYPE_MAP
- Direct Cypher query helpers

Removes:
- Graphiti imports
- Graphiti client functions
- Graphiti-dependent code
"""

from pathlib import Path


def clean_file():
    """Remove Graphiti library code."""

    input_file = Path("/Volumes/X10 Pro/Roscoe/schema-final/source/graphiti_client.py")
    output_file = Path("/Volumes/X10 Pro/Roscoe/schema-final/source/graphiti_client_CLEAN.py")

    with open(input_file) as f:
        lines = f.readlines()

    print("Reading file...")
    print(f"  Total lines: {len(lines)}")
    print()

    # Find sections to remove
    remove_start = None
    remove_end = None

    for i, line in enumerate(lines):
        # Find start of Graphiti client section
        if "# Graphiti Client Factory" in line or "def get_graphiti" in line:
            if remove_start is None:
                remove_start = i
                print(f"  Found Graphiti section start: line {i+1}")

        # Find where Cypher helpers start (keep these)
        if "async def run_cypher_query_direct" in line:
            remove_end = i
            print(f"  Found Cypher helpers start (keep from here): line {i+1}")
            break

    # Remove Graphiti imports
    cleaned_lines = []
    skip_graphiti_imports = False

    for i, line in enumerate(lines):
        # Skip Graphiti imports (lines 15-18)
        if i >= 14 and i <= 20:
            if "from graphiti" in line or "import graphiti" in line:
                print(f"  Removing import: {line.strip()}")
                continue

        # Skip Graphiti client section (lines remove_start to remove_end)
        if remove_start and remove_end:
            if i >= remove_start and i < remove_end:
                continue

        cleaned_lines.append(line)

    # Write cleaned file
    with open(output_file, 'w') as f:
        f.writelines(cleaned_lines)

    print()
    print(f"✓ Created clean file")
    print(f"  Original: {len(lines)} lines")
    print(f"  Cleaned: {len(cleaned_lines)} lines")
    print(f"  Removed: {len(lines) - len(cleaned_lines)} lines")
    print()
    print(f"Output: {output_file}")
    print()
    print("Removed:")
    print("  - Graphiti imports (3 lines)")
    print(f"  - Graphiti client functions ({remove_end - remove_start} lines)")
    print()
    print("Kept:")
    print("  - All Pydantic entity models")
    print("  - ENTITY_TYPES list")
    print("  - EDGE_TYPE_MAP")
    print("  - Direct Cypher query helpers")
    print("  - Workflow query functions")


if __name__ == "__main__":
    clean_file()
