#!/usr/bin/env python3
"""
Backfill name_embedding for all existing Entity nodes in the graph.

This script:
1. Queries all Entity nodes without name_embedding
2. Batch embeds their names using OpenAI text-embedding-3-small
3. Updates the graph with embeddings

Usage:
    python -m roscoe.scripts.backfill_entity_embeddings
    python -m roscoe.scripts.backfill_entity_embeddings --dry-run
    python -m roscoe.scripts.backfill_entity_embeddings --batch-size 50
"""

import asyncio
import argparse
from datetime import datetime
from falkordb import FalkorDB
from openai import AsyncOpenAI


# Configuration
FALKORDB_HOST = "roscoe-graphdb"
FALKORDB_PORT = 6379
GRAPH_NAME = "roscoe_graph"
BATCH_SIZE = 100  # Embed 100 entities at a time
EMBEDDING_MODEL = "text-embedding-3-small"


async def get_entities_without_embeddings(db: FalkorDB) -> list[dict]:
    """Get all Entity nodes that don't have name_embedding."""
    graph = db.select_graph(GRAPH_NAME)

    query = """
    MATCH (n:Entity)
    WHERE n.name_embedding IS NULL
    RETURN n.uuid as uuid, n.name as name, n.entity_type as entity_type
    ORDER BY n.entity_type, n.name
    """

    result = graph.query(query)

    entities = []
    if result.result_set:
        headers = [h[1] if isinstance(h, (list, tuple)) else str(h) for h in result.header]
        for row in result.result_set:
            entity = {headers[i]: row[i] for i in range(len(headers))}
            entities.append(entity)

    return entities


async def embed_batch(client: AsyncOpenAI, texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts using OpenAI."""
    # Clean texts (handle None, remove newlines, limit length)
    cleaned_texts = [(text or "unnamed").replace('\n', ' ')[:500] for text in texts]

    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=cleaned_texts,
    )

    return [item.embedding for item in response.data]


def update_embeddings_batch(db: FalkorDB, entities: list[dict], embeddings: list[list[float]]):
    """Update entity embeddings in the graph (sync)."""
    graph = db.select_graph(GRAPH_NAME)

    for entity, embedding in zip(entities, embeddings):
        # FalkorDB requires vecf32() wrapper for vector embeddings
        query = """
        MATCH (n:Entity {uuid: $uuid})
        SET n.name_embedding = vecf32($embedding)
        RETURN n.uuid
        """
        graph.query(query, {'uuid': entity['uuid'], 'embedding': embedding})


async def backfill_embeddings(dry_run: bool = False, batch_size: int = BATCH_SIZE):
    """Main backfill function."""
    import os

    print("=" * 70)
    print("BACKFILL ENTITY EMBEDDINGS")
    print("=" * 70)
    print(f"Graph: {GRAPH_NAME}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Batch Size: {batch_size}")
    print(f"Dry Run: {dry_run}")
    print()

    # Initialize clients
    db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Get entities without embeddings
    print("Querying entities without embeddings...")
    entities = await get_entities_without_embeddings(db)

    print(f"Found {len(entities)} entities without embeddings")
    print()

    if not entities:
        print("✅ All entities already have embeddings!")
        return

    # Show breakdown by entity type
    from collections import Counter
    type_counts = Counter(e['entity_type'] for e in entities)
    print("Entities by type:")
    for entity_type, count in sorted(type_counts.items()):
        print(f"  {entity_type}: {count}")
    print()

    if dry_run:
        print("[DRY RUN] Would embed and update these entities.")
        print(f"Estimated API calls: {len(entities) // batch_size + 1}")
        print(f"Estimated cost: ${(len(entities) / 1000) * 0.0001:.4f}")
        return

    # Process in batches
    total_batches = (len(entities) + batch_size - 1) // batch_size
    updated_count = 0

    print(f"Processing {len(entities)} entities in {total_batches} batches...")
    print()

    for i in range(0, len(entities), batch_size):
        batch_num = (i // batch_size) + 1
        batch = entities[i:i + batch_size]

        print(f"Batch {batch_num}/{total_batches}: Embedding {len(batch)} entities...")

        # Extract names for embedding
        names = [e['name'] for e in batch]

        # Embed batch
        try:
            embeddings = await embed_batch(openai_client, names)

            # Update graph
            update_embeddings_batch(db, batch, embeddings)

            updated_count += len(batch)
            print(f"  ✓ Updated {len(batch)} entities (total: {updated_count}/{len(entities)})")

        except Exception as e:
            print(f"  ✗ Error in batch {batch_num}: {str(e)}")
            continue

    print()
    print("=" * 70)
    print("✅ BACKFILL COMPLETE")
    print("=" * 70)
    print(f"Total entities updated: {updated_count}/{len(entities)}")
    print(f"Batches processed: {total_batches}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Backfill entity embeddings')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                       help=f'Batch size for embedding (default: {BATCH_SIZE})')
    args = parser.parse_args()

    asyncio.run(backfill_embeddings(args.dry_run, args.batch_size))


if __name__ == "__main__":
    main()
