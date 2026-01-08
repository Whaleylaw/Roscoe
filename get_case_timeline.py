#!/usr/bin/env python3
"""
Get chronological timeline for a case from knowledge graph.

DEPLOYMENT PATH: /Tools/queries/get_case_timeline.py (in GCS bucket whaley_law_firm)

This script queries Episodes for a case and returns them in chronological order.
Provides case history timeline with all events.

Usage:
    python get_case_timeline.py "Christopher-Lanier-MVA-6-28-2025"
    python get_case_timeline.py "Christopher-Lanier-MVA-6-28-2025" --pretty
    python get_case_timeline.py "Christopher-Lanier-MVA-6-28-2025" --limit 50
"""

import argparse
import json
import sys
import os
from falkordb import FalkorDB


def get_case_timeline(case_name: str, limit: int = 100) -> dict:
    """
    Query knowledge graph for episode timeline.

    Args:
        case_name: Case folder name
        limit: Maximum number of episodes to return (default: 100)

    Returns:
        Dict with chronological list of episodes
    """
    # Connect to graph
    host = os.getenv("FALKORDB_HOST", "localhost")
    port = int(os.getenv("FALKORDB_PORT", "6379"))

    db = FalkorDB(host=host, port=port)
    graph = db.select_graph("roscoe_graph")

    # Query for episodes in chronological order
    query = """
        MATCH (episode:Episode)-[:RELATES_TO]->(case:Case {name: $case_name})
        OPTIONAL MATCH (episode)-[:ABOUT]->(entity)
        RETURN episode.uuid as uuid,
               episode.name as name,
               episode.content as content,
               episode.valid_at as valid_at,
               episode.author as author,
               episode.episode_type as episode_type,
               episode.created_at as created_at,
               collect(DISTINCT {
                   entity_name: entity.name,
                   entity_type: labels(entity)[0]
               }) as related_entities
        ORDER BY episode.valid_at DESC
        LIMIT $limit
    """

    result = graph.query(query, {"case_name": case_name, "limit": limit})

    episodes = []
    for record in result.result_set:
        episode_data = {
            "uuid": record[0],
            "name": record[1],
            "content": record[2],
            "valid_at": record[3],
            "author": record[4],
            "episode_type": record[5],
            "created_at": record[6],
            "related_entities": [
                e for e in record[7]
                if e.get("entity_name")  # Filter out empty entities
            ] if record[7] else [],
        }

        episodes.append(episode_data)

    return {
        "success": True,
        "case_name": case_name,
        "episodes": episodes,
        "total_episodes": len(episodes),
        "limit_applied": limit,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Get episode timeline from knowledge graph"
    )
    parser.add_argument("case_name", help="Case folder name")
    parser.add_argument("--limit", type=int, default=100, help="Max episodes to return")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    args = parser.parse_args()

    try:
        result = get_case_timeline(args.case_name, limit=args.limit)
        print(json.dumps(result, indent=2 if args.pretty else None))
        sys.exit(0)
    except Exception as e:
        error = {
            "success": False,
            "error": str(e),
            "case_name": args.case_name
        }
        print(json.dumps(error, indent=2 if args.pretty else None))
        sys.exit(1)


if __name__ == "__main__":
    main()
