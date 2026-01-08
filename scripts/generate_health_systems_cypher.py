#!/usr/bin/env python3
"""
Generate Cypher queries for Health Systems ingestion.

Outputs Cypher that can be executed via redis-cli:
docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph '<query>'
"""

import json
from pathlib import Path
from datetime import datetime


def escape_string(s: str) -> str:
    """Escape string for Cypher."""
    if not s:
        return ""
    # Escape single quotes and backslashes
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace('"', '\\"')
    return s


def generate_health_system_cypher(json_file: Path, output_file: Path):
    """Generate Cypher queries for health systems."""

    with open(json_file, 'r', encoding='utf-8') as f:
        health_systems = json.load(f)

    queries = []

    # Header
    queries.append("// Health Systems Ingestion - Generated Cypher")
    queries.append(f"// Source: {json_file.name}")
    queries.append(f"// Generated: {datetime.now().isoformat()}")
    queries.append(f"// Total entities: {len(health_systems)}")
    queries.append("")

    for idx, hs in enumerate(health_systems, 1):
        name = escape_string(hs['name'])
        attrs = hs.get('attributes', {})

        # Extract attributes
        medical_records_endpoint = escape_string(attrs.get('medical_records_endpoint', ''))
        billing_endpoint = escape_string(attrs.get('billing_endpoint', ''))
        phone = escape_string(attrs.get('phone', ''))
        fax = escape_string(attrs.get('fax', ''))
        email = escape_string(attrs.get('email', ''))
        address = escape_string(attrs.get('address', ''))
        website = escape_string(attrs.get('website', ''))
        created_at = datetime.now().isoformat()

        # Build Cypher query
        query = f"""MERGE (h:HealthSystem {{name: "{name}", group_id: "roscoe_graph"}})
ON CREATE SET
  h.medical_records_endpoint = "{medical_records_endpoint}",
  h.billing_endpoint = "{billing_endpoint}",
  h.phone = "{phone}",
  h.fax = "{fax}",
  h.email = "{email}",
  h.address = "{address}",
  h.website = "{website}",
  h.created_at = "{created_at}"
ON MATCH SET
  h.updated_at = "{created_at}"
RETURN h.name, id(h)"""

        queries.append(f"// {idx}. {name}")
        queries.append(query)
        queries.append("")

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(queries))

    print(f"✓ Generated {len(health_systems)} Cypher queries")
    print(f"  Output: {output_file}")
    print()
    print("To execute on VM:")
    print('  gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command="')
    print(f'    docker exec roscoe-graphdb redis-cli -p 6379 < /path/to/{output_file.name}')
    print('  "')


def generate_execution_script(cypher_file: Path, shell_script: Path):
    """Generate shell script to execute all Cypher queries."""

    with open(cypher_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Extract non-comment, non-empty lines
    queries = []
    current_query = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('//'):
            if current_query:
                queries.append(' '.join(current_query))
                current_query = []
            continue
        current_query.append(line)

    if current_query:
        queries.append(' '.join(current_query))

    # Build shell script
    script_lines = [
        "#!/bin/bash",
        "# Execute Health Systems Cypher queries",
        f"# Generated: {datetime.now().isoformat()}",
        "",
        "set -e",  # Exit on error
        "",
        'echo "Ingesting Health Systems to FalkorDB..."',
        'echo ""',
        ""
    ]

    for idx, query in enumerate(queries, 1):
        # Escape for shell
        query_escaped = query.replace('"', '\\"').replace('$', '\\$')
        script_lines.append(f'echo "Executing query {idx}/{len(queries)}..."')
        script_lines.append(f'docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "{query_escaped}" --raw')
        script_lines.append('echo ""')
        script_lines.append('')

    script_lines.append('echo "✓ All queries executed"')

    with open(shell_script, 'w', encoding='utf-8') as f:
        f.write('\n'.join(script_lines))

    # Make executable
    shell_script.chmod(0o755)

    print(f"✓ Generated shell script: {shell_script}")
    print()
    print("To execute on VM:")
    print(f"  gcloud compute scp {shell_script} aaronwhaley@roscoe-paralegal-vm:/tmp/ingest_health_systems.sh --zone=us-central1-a")
    print(f"  gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a --command='bash /tmp/ingest_health_systems.sh'")


def main():
    base_dir = Path("/Volumes/X10 Pro/Roscoe")
    json_file = base_dir / "json-files/memory-cards/entities/health_systems.json"
    cypher_output = base_dir / "scripts/health_systems_ingestion.cypher"
    shell_output = base_dir / "scripts/ingest_health_systems.sh"

    if not json_file.exists():
        print(f"❌ File not found: {json_file}")
        return

    print("Generating Cypher queries...")
    print()
    generate_health_system_cypher(json_file, cypher_output)
    print()
    print("Generating shell script...")
    print()
    generate_execution_script(cypher_output, shell_output)


if __name__ == "__main__":
    main()
