#!/usr/bin/env python3
"""
Rebuild Graphiti Vector Indices for OpenAI Embeddings

Deletes existing indices and rebuilds them for the new embedding dimensions.
This is needed when switching embedding providers (e.g., Gemini 768d → OpenAI 1024d).

Usage:
    python -m roscoe.scripts.rebuild_graphiti_indices
"""

import asyncio
import time


async def rebuild_indices():
    """Rebuild Graphiti indices with delete_existing=True."""
    from roscoe.core.graphiti_client import get_graphiti

    print("=" * 70)
    print("REBUILDING GRAPHITI INDICES FOR OPENAI")
    print("=" * 70)
    print()
    print("⚠️  This will DELETE existing indices and rebuild them")
    print("📊 Old indices: 768 dimensions (Gemini text-embedding-004)")
    print("📊 New indices: 1024 dimensions (OpenAI text-embedding-3-small)")
    print()
    print("⏱️  This will take approximately 2-3 minutes...")
    print()

    start_time = time.time()

    # Get Graphiti client
    print("📡 Connecting to Graphiti with OpenAI...")
    graphiti = await get_graphiti()
    print("   ✅ Connected to FalkorDB (roscoe_graph)")
    print()

    # Rebuild indices (delete old ones first)
    print("🔨 Deleting old indices and building new ones...")
    print()

    try:
        await graphiti.build_indices_and_constraints(delete_existing=True)
        elapsed = time.time() - start_time

        print()
        print("=" * 70)
        print("✅ INDICES REBUILT SUCCESSFULLY")
        print("=" * 70)
        print(f"Time elapsed: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print()
        print("New vector indices created for:")
        print("  - Entity.name_embedding (1024 dimensions)")
        print("  - Entity.summary_embedding (1024 dimensions)")
        print("  - Edge.fact_embedding (1024 dimensions)")
        print()
        print("Fulltext indices recreated for:")
        print("  - Entity.name")
        print("  - Edge.fact")
        print("  - Episodic.content")
        print()
        print("Ready to start ingestion with OpenAI embeddings!")
        print("=" * 70)

    except Exception as e:
        elapsed = time.time() - start_time
        print()
        print("=" * 70)
        print("❌ INDEX REBUILD FAILED")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print(f"Time elapsed: {elapsed:.1f} seconds")
        print("=" * 70)
        raise


def main():
    print()
    asyncio.run(rebuild_indices())
    print()


if __name__ == "__main__":
    main()
