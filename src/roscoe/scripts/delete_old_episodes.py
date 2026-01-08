#!/usr/bin/env python3
"""
Delete Old Episodic Nodes Without Embeddings

Removes episodic nodes created before indices were built, along with their
edges. This allows for clean re-ingestion with proper embeddings.

Usage:
    # Run inside roscoe-agents container
    python -m roscoe.scripts.delete_old_episodes

    # With custom cutoff time
    python -m roscoe.scripts.delete_old_episodes --before "2025-12-23T15:00:00"

    # Dry run (show what would be deleted)
    python -m roscoe.scripts.delete_old_episodes --dry-run
"""

import asyncio
import argparse
from datetime import datetime


async def delete_old_episodes(cutoff_time: str, dry_run: bool = False):
    """Delete episodic nodes created before the cutoff time."""
    from roscoe.core.graphiti_client import run_cypher_query

    print("=" * 70)
    print("DELETE OLD EPISODIC NODES")
    print("=" * 70)
    print(f"Cutoff time: {cutoff_time}")
    print(f"Dry run: {dry_run}")
    print()

    # Count episodic nodes to be deleted
    count_query = """
        MATCH (e:Episodic)
        WHERE e.created_at < $cutoff_time
        RETURN count(e) as count
    """

    result = await run_cypher_query(count_query, {"cutoff_time": cutoff_time})
    episodic_count = result[0]['count'] if result else 0

    print(f"📊 Found {episodic_count} episodic nodes to delete")

    if episodic_count == 0:
        print("   ✅ No old episodic nodes found. Nothing to delete.")
        return

    # Count edges to be deleted
    edge_count_query = """
        MATCH (e:Episodic)-[r]-()
        WHERE e.created_at < $cutoff_time
        RETURN count(r) as count
    """

    result = await run_cypher_query(edge_count_query, {"cutoff_time": cutoff_time})
    edge_count = result[0]['count'] if result else 0

    print(f"📊 Found {edge_count} edges connected to these episodic nodes")
    print()

    if dry_run:
        print("[DRY RUN] Would delete:")
        print(f"  - {episodic_count} Episodic nodes")
        print(f"  - {edge_count} associated edges")
        print()
        print("Run without --dry-run to actually delete.")
        return

    # Delete episodic nodes and their edges
    print("🗑️  Deleting old episodic nodes and edges...")

    delete_query = """
        MATCH (e:Episodic)
        WHERE e.created_at < $cutoff_time
        DETACH DELETE e
    """

    try:
        await run_cypher_query(delete_query, {"cutoff_time": cutoff_time})

        print()
        print("=" * 70)
        print("✅ DELETION COMPLETE")
        print("=" * 70)
        print(f"Deleted {episodic_count} episodic nodes")
        print(f"Deleted {edge_count} associated edges")
        print()
        print("Next steps:")
        print("  1. Verify deletion with: MATCH (e:Episodic) RETURN count(e)")
        print("  2. Re-run full parallel ingestion")
        print("  3. All new episodes will have proper embeddings")
        print("=" * 70)

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ DELETION FAILED")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  - Check FalkorDB connection")
        print("  - Verify query syntax")
        print("  - Check database permissions")
        print("=" * 70)
        raise


async def verify_deletion():
    """Verify that old episodes were deleted."""
    from roscoe.core.graphiti_client import run_cypher_query

    print()
    print("🔍 Verifying deletion...")

    count_query = "MATCH (e:Episodic) RETURN count(e) as remaining_count"
    result = await run_cypher_query(count_query, {})
    remaining = result[0]['remaining_count'] if result else 0

    print(f"   Remaining episodic nodes: {remaining}")

    if remaining == 0:
        print("   ✅ All episodic nodes deleted successfully")
    else:
        print(f"   ℹ️  {remaining} episodic nodes remain (likely from today)")

    return remaining


def main():
    parser = argparse.ArgumentParser(description='Delete old episodic nodes without embeddings')
    parser.add_argument('--before', '--cutoff-time',
                       dest='cutoff_time',
                       default='2025-12-23T15:00:00+00:00',
                       help='Delete episodes created before this timestamp (ISO format)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    args = parser.parse_args()

    print()
    asyncio.run(delete_old_episodes(args.cutoff_time, args.dry_run))

    if not args.dry_run:
        asyncio.run(verify_deletion())

    print()


if __name__ == "__main__":
    main()
