#!/usr/bin/env python3
"""
Add Semantic Embeddings to Existing Graph Entities

Embeds all entities with enriched context (entity + first-hop relationships).
This enables semantic search across the entire knowledge graph.

Entity types embedded:
- Cases (with client name, case type)
- Clients (with case count)
- Medical Providers (with specialty, case count)
- Insurance entities (claims, insurers, adjusters)
- Liens, Attorneys, Courts, etc.

Embedding strategy: Option C (enriched context)
- Include entity details + key relationships
- Example: "Baptist Health Neurology (Neurology) - Treating 3 cases: Abby Sitgraves, Muhammad Alif, James Sadler"

Usage:
    python -m roscoe.scripts.add_graph_embeddings
    python -m roscoe.scripts.add_graph_embeddings --dry-run
    python -m roscoe.scripts.add_graph_embeddings --entity-type MedicalProvider
"""

import asyncio
import argparse
import os
from typing import Optional
from falkordb import FalkorDB
from openai import AsyncOpenAI


# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100
FALKORDB_HOST = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", "6379"))


async def build_enriched_text_for_entity(graph, entity_type: str, entity_name: str) -> str:
    """
    Build enriched text for entity embedding.

    Includes entity details + first-hop relationships for richer context.
    """
    if entity_type == "Case":
        # Case: Include case type + client name
        query = """
        MATCH (c:Case {name: $name})
        OPTIONAL MATCH (c)-[:HAS_CLIENT]->(client:Client)
        RETURN c.name, c.case_type, client.name as client_name
        """
        result = graph.query(query, {'name': entity_name})
        if result.result_set:
            row = result.result_set[0]
            case_type = row[1] or "Unknown"
            client = row[2] or "Unknown Client"
            return f"{entity_name} - {case_type} case - Client: {client}"

    elif entity_type == "Client":
        # Client: Include case count
        query = """
        MATCH (client:Client {name: $name})<-[:HAS_CLIENT]-(c:Case)
        RETURN client.name, count(c) as case_count
        """
        result = graph.query(query, {'name': entity_name})
        if result.result_set:
            count = result.result_set[0][1]
            return f"{entity_name} - Client in {count} case{'s' if count != 1 else ''}"

    elif entity_type == "MedicalProvider":
        # Provider: Include specialty + cases treated
        query = """
        MATCH (p:MedicalProvider {name: $name})<-[:TREATING_AT]-(c:Case)
        RETURN p.name, p.specialty, collect(c.name) as cases
        LIMIT 1
        """
        result = graph.query(query, {'name': entity_name})
        if result.result_set:
            row = result.result_set[0]
            specialty = row[1] or "Medical"
            cases = row[2][:3] if len(row) > 2 and row[2] else []
            case_list = ", ".join([c.split('-')[0] for c in cases]) if cases else "no cases"
            return f"{entity_name} ({specialty}) - Treating {len(cases)} cases: {case_list}"

    elif entity_type in ["BIClaim", "PIPClaim", "UMClaim", "UIMClaim", "WCClaim", "MedPayClaim"]:
        # Insurance Claim: Include insurer + adjuster
        query = f"""
        MATCH (claim:{entity_type} {{name: $name}})
        OPTIONAL MATCH (claim)-[:INSURED_BY]->(insurer:Insurer)
        OPTIONAL MATCH (claim)-[:ASSIGNED_ADJUSTER]->(adjuster:Adjuster)
        RETURN claim.name, insurer.name, adjuster.name
        """
        result = graph.query(query, {'name': entity_name})
        if result.result_set:
            row = result.result_set[0]
            insurer = row[1] or "Unknown Insurer"
            adjuster = row[2] or "No adjuster assigned"
            return f"{entity_type} - {insurer} - Adjuster: {adjuster}"

    # Default: Just return entity type + name
    return f"{entity_type}: {entity_name}"


async def embed_entities_by_type(
    graph,
    openai_client: AsyncOpenAI,
    entity_type: str,
    dry_run: bool = False
) -> int:
    """Embed all entities of a specific type."""
    # Get all entities of this type
    query = f"""
    MATCH (n:{entity_type})
    RETURN n.name as name
    ORDER BY n.name
    """
    result = graph.query(query)

    if not result.result_set:
        print(f"  - {entity_type}: 0 entities (skipped)")
        return 0

    entities = [row[0] for row in result.result_set if row[0]]
    total = len(entities)

    print(f"  {entity_type}: {total} entities to embed...")

    if dry_run:
        print(f"    [DRY RUN] Would embed {total} {entity_type} entities")
        return total

    # Process in batches
    embedded_count = 0

    for i in range(0, total, BATCH_SIZE):
        batch = entities[i:i + BATCH_SIZE]

        # Build enriched texts
        texts = []
        for name in batch:
            text = await build_enriched_text_for_entity(graph, entity_type, name)
            texts.append(text)

        # Get embeddings from OpenAI
        try:
            response = await openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts
            )

            # Update graph with embeddings
            for j, embedding_data in enumerate(response.data):
                entity_name = batch[j]
                embedding = embedding_data.embedding

                update_query = f"""
                MATCH (n:{entity_type} {{name: $name}})
                SET n.embedding = vecf32($embedding)
                """
                graph.query(update_query, {
                    'name': entity_name,
                    'embedding': embedding
                })

                embedded_count += 1

            if (i + BATCH_SIZE) % 500 == 0:
                print(f"    Progress: {embedded_count}/{total} embedded...")

        except Exception as e:
            print(f"    Error in batch starting at {i}: {e}")
            continue

    print(f"    ✓ Embedded {embedded_count}/{total} {entity_type} entities")
    return embedded_count


async def main(dry_run: bool = False, entity_type: Optional[str] = None):
    """Main embedding function."""
    print("=" * 70)
    print("ADD SEMANTIC EMBEDDINGS TO GRAPH")
    print("=" * 70)
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Batch size: {BATCH_SIZE}")
    if entity_type:
        print(f"Entity type filter: {entity_type}")
    print(f"Dry run: {dry_run}")
    print()

    # Connect to FalkorDB
    db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
    graph = db.select_graph("roscoe_graph")

    # Connect to OpenAI
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Entity types to embed (in priority order)
    entity_types = [
        "Case",
        "Client",
        "MedicalProvider",
        "BIClaim",
        "PIPClaim",
        "UMClaim",
        "UIMClaim",
        "WCClaim",
        "Insurer",
        "Adjuster",
        "Lien",
        "LienHolder",
        "Attorney",
        "Court",
        "Defendant",
        "Organization",
        "Vendor",
    ]

    # Filter if specific type requested
    if entity_type:
        if entity_type in entity_types:
            entity_types = [entity_type]
        else:
            print(f"❌ Unknown entity type: {entity_type}")
            return

    total_embedded = 0

    print("Embedding entities...\n")

    for etype in entity_types:
        count = await embed_entities_by_type(graph, openai_client, etype, dry_run)
        total_embedded += count

    print()
    print("=" * 70)
    print("✅ COMPLETE")
    print("=" * 70)
    print(f"Total entities embedded: {total_embedded}")
    print()


def run():
    parser = argparse.ArgumentParser(description='Add embeddings to graph entities')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without embedding')
    parser.add_argument('--entity-type', type=str, default=None,
                       help='Embed only specific entity type (e.g., MedicalProvider)')
    args = parser.parse_args()

    asyncio.run(main(dry_run=args.dry_run, entity_type=args.entity_type))


if __name__ == "__main__":
    run()
