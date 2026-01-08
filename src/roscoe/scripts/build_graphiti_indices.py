#!/usr/bin/env python3
"""
Build Graphiti Vector Indices

Creates vector indices and fulltext indices in FalkorDB for Graphiti.
This is a ONE-TIME operation that enables:
- Vector search on embeddings
- Hybrid search (vector + fulltext)
- Proper embedding storage on episodic nodes

Usage:
    # Run inside roscoe-agents container
    python -m roscoe.scripts.build_graphiti_indices

Note: This takes ~6 minutes to complete. Only needs to be run once.
"""

import asyncio
import time


async def build_indices():
    """Build Graphiti indices for vector and fulltext search."""
    from roscoe.core.graphiti_client import get_graphiti

    print("=" * 70)
    print("BUILDING GRAPHITI INDICES")
    print("=" * 70)
    print()
    print("⏱️  This will take approximately 6 minutes...")
    print("📊 Creating vector indices for embeddings")
    print("🔍 Creating fulltext indices for search")
    print()

    start_time = time.time()

    # Get Graphiti client
    print("📡 Connecting to Graphiti...")
    graphiti = await get_graphiti()
    print("   ✅ Connected to FalkorDB (roscoe_graph)")
    print()

    # Build indices
    print("🔨 Building indices...")
    print("   (This creates vector indices for Entity and Episodic nodes)")
    print("   (And fulltext indices for name/fact/content fields)")
    print()

    try:
        await graphiti.build_indices_and_constraints()
        elapsed = time.time() - start_time

        print()
        print("=" * 70)
        print("✅ INDICES BUILT SUCCESSFULLY")
        print("=" * 70)
        print(f"Time elapsed: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print()
        print("Vector indices created:")
        print("  - Entity.name_embedding (for semantic entity search)")
        print("  - Entity.summary_embedding (for semantic entity summaries)")
        print("  - Episodic.embedding (for semantic episode search)")
        print()
        print("Fulltext indices created:")
        print("  - Entity.name (for keyword entity search)")
        print("  - Edge.fact (for keyword relationship search)")
        print("  - Episodic.content (for keyword episode search)")
        print()
        print("Next steps:")
        print("  1. Re-run episode ingestion to populate embeddings")
        print("  2. Use query_case_graph() for semantic search")
        print("  3. Vector search will now work properly")
        print("=" * 70)

    except Exception as e:
        elapsed = time.time() - start_time
        print()
        print("=" * 70)
        print("❌ INDEX BUILD FAILED")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print(f"Time elapsed: {elapsed:.1f} seconds")
        print()
        print("Troubleshooting:")
        print("  - Check FalkorDB is running: docker ps | grep graphdb")
        print("  - Check connection: redis-cli -p 6379 PING")
        print("  - Check existing indices: GRAPH.QUERY roscoe_graph 'CALL db.indexes()'")
        print("=" * 70)
        raise


async def verify_indices():
    """Verify that indices were created successfully."""
    from roscoe.core.graphiti_client import run_cypher_query

    print()
    print("🔍 Verifying indices...")

    try:
        # Try to query indices (this might timeout if indices don't exist)
        result = await run_cypher_query("CALL db.indexes()", {})
        print(f"   ✅ Found {len(result)} indices")
        return True
    except Exception as e:
        print(f"   ⚠️  Could not verify indices: {str(e)[:100]}")
        return False


def main():
    print()
    print("Starting Graphiti index build...")
    print()

    asyncio.run(build_indices())

    # Optionally verify (may timeout, don't fail on this)
    try:
        asyncio.run(verify_indices())
    except:
        pass

    print()


if __name__ == "__main__":
    main()
