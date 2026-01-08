#!/usr/bin/env python3
"""
Add Embeddings to Existing Episodic Nodes

The graph has 625 Episodic nodes from a previous ingestion, but they lack
embeddings. This prevents semantic search from working.

This script:
1. Reads all Episodic nodes
2. Generates embeddings for their content using Gemini
3. Stores embeddings back on the nodes

Usage:
    python add_embeddings_to_episodic_nodes.py
    python add_embeddings_to_episodic_nodes.py --batch-size 50
    python add_embeddings_to_episodic_nodes.py --dry-run
"""

import asyncio
import os
from typing import List
import argparse


async def add_embeddings_to_episodic_nodes(batch_size: int = 50, dry_run: bool = False):
    """Add embeddings to Episodic nodes that lack them."""
    from roscoe.core.graphiti_client import run_cypher_query, get_graphiti

    print("=" * 70)
    print("ADDING EMBEDDINGS TO EPISODIC NODES")
    print("=" * 70)
    print(f"Batch size: {batch_size}")
    print(f"Dry run: {dry_run}")
    print()

    # Get Graphiti client (has embedder configured)
    graphiti = await get_graphiti()
    embedder = graphiti.embedder

    print(f"✅ Graphiti client initialized")
    print(f"   Embedder: {embedder.__class__.__name__}")
    print()

    # Get all Episodic nodes without embeddings
    query = """
    MATCH (e:Episodic)
    WHERE e.embedding IS NULL
    RETURN e.uuid as uuid, e.name as name, e.content as content
    """

    print("📊 Querying for Episodic nodes without embeddings...")
    episodic_nodes = await run_cypher_query(query, {})

    total_nodes = len(episodic_nodes)
    print(f"   Found {total_nodes} Episodic nodes needing embeddings")
    print()

    if total_nodes == 0:
        print("✅ All Episodic nodes already have embeddings!")
        return

    if dry_run:
        print(f"[DRY RUN] Would process {total_nodes} nodes in batches of {batch_size}")
        print(f"[DRY RUN] Sample node:")
        if episodic_nodes:
            sample = episodic_nodes[0]
            print(f"   UUID: {sample.get('uuid')}")
            print(f"   Name: {sample.get('name')}")
            print(f"   Content: {str(sample.get('content', ''))[:100]}...")
        return

    # Process in batches
    embedded_count = 0
    error_count = 0

    for i in range(0, total_nodes, batch_size):
        batch = episodic_nodes[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_nodes + batch_size - 1) // batch_size

        print(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} nodes)...")

        for node in batch:
            uuid = node.get("uuid")
            name = node.get("name", "")
            content = node.get("content", "")

            if not content:
                print(f"   ⚠️  Skipping {name} - no content")
                continue

            try:
                # Generate embedding for content
                embedding = await embedder.create(content)

                # Convert embedding to list if needed
                if hasattr(embedding, 'tolist'):
                    embedding = embedding.tolist()
                elif not isinstance(embedding, list):
                    embedding = list(embedding)

                # Store embedding on the node
                update_query = """
                MATCH (e:Episodic {uuid: $uuid})
                SET e.embedding = $embedding
                RETURN e.uuid
                """

                await run_cypher_query(update_query, {
                    "uuid": uuid,
                    "embedding": embedding
                })

                embedded_count += 1

                if embedded_count % 10 == 0:
                    print(f"   Progress: {embedded_count}/{total_nodes} embedded...")

            except Exception as e:
                print(f"   ❌ Error embedding {name}: {e}")
                error_count += 1

        # Progress update after each batch
        print(f"   ✅ Batch {batch_num} complete: {embedded_count} embedded, {error_count} errors")
        print()

    # Summary
    print("=" * 70)
    print("✅ EMBEDDING GENERATION COMPLETE")
    print("=" * 70)
    print(f"Total processed: {total_nodes}")
    print(f"Successfully embedded: {embedded_count}")
    print(f"Errors: {error_count}")
    print()
    print("Next steps:")
    print("  1. Test semantic search with query_case_graph()")
    print("  2. Verify embeddings were saved correctly")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Add embeddings to Episodic nodes')
    parser.add_argument('--batch-size', type=int, default=50, help='Nodes to process per batch')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    args = parser.parse_args()

    asyncio.run(add_embeddings_to_episodic_nodes(
        batch_size=args.batch_size,
        dry_run=args.dry_run
    ))


if __name__ == "__main__":
    main()
