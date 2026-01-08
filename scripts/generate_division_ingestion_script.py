#!/usr/bin/env python3
"""
Generate shell script to ingest all court divisions on VM.

Creates a bash script that can be copied to the VM and executed directly,
which is much faster than making individual gcloud ssh calls.
"""

import json
from pathlib import Path


def escape_cypher(value):
    """Escape value for Cypher in shell script."""
    if value is None or value == "":
        return '""'
    value_str = str(value)
    # Escape for Cypher first
    value_str = value_str.replace('\\', '\\\\')
    value_str = value_str.replace('"', '\\"')
    # Then escape for shell
    value_str = value_str.replace('$', '\\$')
    value_str = value_str.replace('`', '\\`')
    return f'"{value_str}"'


def generate_script(entities_dir: Path, output_script: Path):
    """Generate ingestion shell script."""

    division_files = [
        ("CircuitDivision", "circuit_divisions.json"),
        ("DistrictDivision", "district_divisions.json"),
        ("AppellateDistrict", "appellate_districts.json"),
        ("SupremeCourtDistrict", "supreme_court_districts.json"),
    ]

    script_lines = [
        "#!/bin/bash",
        "# Court Divisions Ingestion Script",
        f"# Generated: {Path(__file__).name}",
        "# Execute on VM: bash /tmp/ingest_divisions.sh",
        "",
        "set -e",  # Exit on error
        "",
        'echo "======================================================================="',
        'echo "COURT DIVISIONS INGESTION - PHASE 1b"',
        'echo "======================================================================="',
        'echo ""',
        "",
        '# Verify graph connection',
        'echo "Verifying FalkorDB connection..."',
        'docker exec roscoe-graphdb redis-cli -p 6379 PING > /dev/null 2>&1 || { echo "❌ Cannot connect to FalkorDB"; exit 1; }',
        'echo "✓ Connected to FalkorDB"',
        'echo ""',
        "",
        '# Pre-ingestion count',
        'BEFORE=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MATCH (n) RETURN count(n)" --raw | grep -E "^[0-9]+$" | head -1)',
        'echo "Nodes before: $BEFORE"',
        'echo ""',
        "",
    ]

    total_divisions = 0

    for entity_type, filename in division_files:
        file_path = entities_dir / filename

        if not file_path.exists():
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            divisions = json.load(f)

        total_divisions += len(divisions)

        script_lines.append(f'echo "Ingesting {entity_type}: {len(divisions)} entities..."')
        script_lines.append(f'CREATED_COUNT=0')
        script_lines.append(f'MATCHED_COUNT=0')
        script_lines.append('')

        for idx, div in enumerate(divisions, 1):
            name = div['name']
            attrs = div.get('attributes', {})

            # Build property assignments
            props = []
            for key, value in attrs.items():
                if value is not None and value != "":
                    props.append(f'h.{key} = {escape_cypher(value)}')

            props.append('h.created_at = timestamp()')
            props_str = ', '.join(props)

            # Build Cypher
            query = f'MERGE (h:{entity_type} {{name: {escape_cypher(name)}, group_id: "roscoe_graph"}}) ON CREATE SET {props_str} ON MATCH SET h.updated_at = timestamp() RETURN h.name'

            # Add to script with error handling
            script_lines.append(f'# {idx}. {name}')
            script_lines.append(f'RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "{query}" --raw 2>&1)')
            script_lines.append(f'if echo "$RESULT" | grep -q "Nodes created: 1"; then')
            script_lines.append(f'  ((CREATED_COUNT++))')
            script_lines.append(f'  echo "  ✓ Created: {name}"')
            script_lines.append(f'elif echo "$RESULT" | grep -q "{name}"; then')
            script_lines.append(f'  ((MATCHED_COUNT++))')
            script_lines.append(f'  echo "  ⊙ Exists: {name}"')
            script_lines.append(f'else')
            script_lines.append(f'  echo "  ❌ Error: {name}"')
            script_lines.append(f'  echo "$RESULT" | head -3')
            script_lines.append(f'fi')
            script_lines.append('')

        script_lines.append(f'echo ""')
        script_lines.append(f'echo "{entity_type} Summary: Created=$CREATED_COUNT, Matched=$MATCHED_COUNT"')
        script_lines.append(f'echo ""')
        script_lines.append('')

    # Final summary
    script_lines.extend([
        '# Post-ingestion verification',
        'AFTER=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MATCH (n) RETURN count(n)" --raw | grep -E "^[0-9]+$" | head -1)',
        'ADDED=$((AFTER - BEFORE))',
        'echo "======================================================================="',
        'echo "INGESTION COMPLETE"',
        'echo "======================================================================="',
        'echo "Nodes before: $BEFORE"',
        'echo "Nodes after: $AFTER"',
        'echo "Nodes added: $ADDED"',
        f'echo "Expected: {total_divisions}"',
        'echo ""',
        '',
        '# Verify Abby Sitgraves case integrity (canary)',
        'ABBY_RELS=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MATCH (c:Case {name: \\\"Abby-Sitgraves-MVA-7-13-2024\\\"})-[r]-() RETURN count(r)" --raw | grep -E "^[0-9]+$" | head -1)',
        'echo "Abby Sitgraves relationships: $ABBY_RELS (should be 93)"',
        'echo ""',
        '',
        '# List all division types',
        'echo "Division types in graph:"',
        'docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MATCH (d) WHERE labels(d)[0] CONTAINS \\"Division\\" RETURN labels(d)[0], count(*) ORDER BY labels(d)[0]" --raw | grep -v "Cached"',
        'echo ""',
        'echo "✅ Phase 1b complete"',
    ])

    # Write script
    with open(output_script, 'w', encoding='utf-8') as f:
        f.write('\n'.join(script_lines))

    output_script.chmod(0o755)

    print(f"✓ Generated ingestion script: {output_script}")
    print(f"  Total divisions to ingest: {total_divisions}")
    print()
    print("To execute:")
    print(f"  1. Copy to VM:")
    print(f'     gcloud compute scp "{output_script}" aaronwhaley@roscoe-paralegal-vm:/tmp/ingest_divisions.sh --zone=us-central1-a')
    print()
    print(f"  2. Execute on VM:")
    print(f'     gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="bash /tmp/ingest_divisions.sh"')
    print()
    print(f"  Or in one command:")
    print(f'     gcloud compute scp "{output_script}" aaronwhaley@roscoe-paralegal-vm:/tmp/ingest_divisions.sh --zone=us-central1-a && \\')
    print(f'     gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="bash /tmp/ingest_divisions.sh"')


def main():
    entities_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")
    output_script = Path("/Volumes/X10 Pro/Roscoe/scripts/ingest_divisions.sh")

    if not entities_dir.exists():
        print(f"❌ Directory not found: {entities_dir}")
        return

    generate_script(entities_dir, output_script)


if __name__ == "__main__":
    main()
