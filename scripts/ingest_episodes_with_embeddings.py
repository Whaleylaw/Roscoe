#!/usr/bin/env python3
"""
Ingest episodes to FalkorDB with semantic embeddings.

This script:
1. Loads merged_*.json files (99 files with corrected entity names)
2. Generates embeddings using sentence-transformers (same as skill matching)
3. Creates Episode nodes with embeddings
4. Creates ABOUT relationships to entities (Facility, Location, Attorney, etc.)
5. Creates RELATES_TO relationships to Cases

Run inside roscoe-agents container:
  docker exec roscoe-agents python3 /deps/roscoe/src/roscoe/scripts/ingest_episodes_with_embeddings.py
"""

import json
import os
import uuid as uuid_lib
from pathlib import Path
from datetime import datetime
from falkordb import FalkorDB
from sentence_transformers import SentenceTransformer


def create_vector_index_if_needed(graph):
    """Create vector index for Episode embeddings if it doesn't exist."""

    try:
        # Check if vector index exists
        # FalkorDB may not support vector indices yet - this might fail
        # If it does, we'll just store embeddings as properties
        result = graph.query("""
            CALL db.idx.vector.createNodeIndex(
              'Episode',
              'embedding',
              384,
              'cosine'
            )
        """)
        print("✓ Created vector index for Episode.embedding")
        return True
    except Exception as e:
        print(f"⊙ Vector index creation not supported or already exists: {str(e)[:100]}")
        print("  Embeddings will be stored as properties (searchable via application layer)")
        return False


def generate_embedding(text: str, model) -> list:
    """Generate 384-dim embedding for text."""

    embedding = model.encode(text)
    return embedding.tolist()


def ingest_case_episodes(merged_file: Path, model, graph):
    """Ingest all episodes for one case."""

    with open(merged_file) as f:
        data = json.load(f)

    case_name = data.get('case_name', 'unknown')
    episodes = data.get('episodes', [])

    print(f"\n{case_name}: {len(episodes)} episodes")

    stats = {
        'episodes_created': 0,
        'relationships_created': 0,
        'errors': []
    }

    for episode in episodes:
        try:
            # Extract episode data
            episode_name = episode.get('episode_name', 'Unnamed')
            content = episode.get('natural_language', '')
            valid_at = episode.get('valid_at', datetime.now().isoformat())
            author = episode.get('author', 'imported')

            # Generate unique ID
            episode_uuid = str(uuid_lib.uuid4())

            # Generate embedding
            embedding = generate_embedding(content, model)

            # Create Episode node
            # Note: FalkorDB doesn't have datetime() function, use string for valid_at
            query = """
            CREATE (ep:Episode {
              uuid: $uuid,
              name: $name,
              content: $content,
              valid_at: $valid_at,
              author: $author,
              case_name: $case_name,
              episode_type: $episode_type,
              group_id: $group_id,
              created_at: timestamp(),
              embedding: $embedding
            })
            RETURN ep.uuid
            """

            params = {
                'uuid': episode_uuid,
                'name': episode_name,
                'content': content,
                'valid_at': valid_at,
                'author': author,
                'case_name': case_name,
                'episode_type': 'imported',
                'group_id': 'roscoe_graph',
                'embedding': embedding
            }

            result = graph.query(query, params)

            if result.nodes_created > 0:
                stats['episodes_created'] += 1

                # Create RELATES_TO relationship to Case
                case_rel_query = """
                MATCH (ep:Episode {uuid: $uuid})
                MATCH (c:Case {name: $case_name})
                CREATE (ep)-[:RELATES_TO]->(c)
                """

                graph.query(case_rel_query, {'uuid': episode_uuid, 'case_name': case_name})
                stats['relationships_created'] += 1

                # Create ABOUT relationships to entities
                for rel_type, entities in episode.get('proposed_relationships', {}).items():
                    if not isinstance(entities, list):
                        continue

                    for entity_ref in entities:
                        if not isinstance(entity_ref, dict):
                            continue

                        entity_type = entity_ref.get('entity_type')
                        entity_name = entity_ref.get('entity_name')

                        if not entity_type or not entity_name:
                            continue

                        # Create ABOUT relationship
                        about_query = f"""
                        MATCH (ep:Episode {{uuid: $uuid}})
                        MATCH (e:{entity_type} {{name: $entity_name}})
                        CREATE (ep)-[:ABOUT]->(e)
                        """

                        try:
                            result = graph.query(about_query, {
                                'uuid': episode_uuid,
                                'entity_name': entity_name
                            })

                            if result.relationships_created > 0:
                                stats['relationships_created'] += 1

                        except Exception as e:
                            # Entity might not exist or type mismatch
                            pass  # Continue with other entities

        except Exception as e:
            stats['errors'].append(f"{episode_name}: {str(e)[:50]}")

    return stats


def main():
    """Ingest all episodes with embeddings."""

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Preview without ingesting')
    parser.add_argument('--limit', type=int, help='Limit number of cases to process')
    args = parser.parse_args()

    print("="*70)
    print("EPISODE INGESTION WITH EMBEDDINGS")
    print("="*70)
    print()

    if args.dry_run:
        print("DRY RUN MODE - No ingestion\n")

    # Load embedding model
    print("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✓ Model loaded (384 dimensions)\n")

    # Connect to graph
    if not args.dry_run:
        host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
        port = int(os.getenv("FALKORDB_PORT", "6379"))

        print(f"Connecting to FalkorDB at {host}:{port}")
        db = FalkorDB(host=host, port=port)
        graph = db.select_graph("roscoe_graph")
        print("✓ Connected\n")

        # Create vector index if supported
        create_vector_index_if_needed(graph)
        print()

    # Find merged files
    episodes_dir = Path("/mnt/workspace/json-files/memory-cards/episodes")
    if not episodes_dir.exists():
        episodes_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes")

    merged_files = sorted(episodes_dir.glob("merged_*.json"))

    if args.limit:
        merged_files = merged_files[:args.limit]

    print(f"Found {len(merged_files)} merged files to process")
    print()

    # Pre-check
    if not args.dry_run:
        result = graph.query("MATCH (n) RETURN count(n)")
        nodes_before = result.result_set[0][0]
        result = graph.query("MATCH ()-[r]->() RETURN count(r)")
        rels_before = result.result_set[0][0]

        print(f"Nodes before: {nodes_before:,}")
        print(f"Relationships before: {rels_before:,}")

    # Process each merged file
    all_stats = {
        'cases_processed': 0,
        'episodes_created': 0,
        'relationships_created': 0,
        'errors': []
    }

    for merged_file in merged_files:
        if args.dry_run:
            with open(merged_file) as f:
                data = json.load(f)
            print(f"Would process: {data.get('case_name')} ({len(data.get('episodes', []))} episodes)")
        else:
            stats = ingest_case_episodes(merged_file, model, graph)

            all_stats['cases_processed'] += 1
            all_stats['episodes_created'] += stats['episodes_created']
            all_stats['relationships_created'] += stats['relationships_created']
            all_stats['errors'].extend(stats['errors'])

            print(f"  Episodes: {stats['episodes_created']}, Relationships: {stats['relationships_created']}")

    print()
    print("="*70)
    print("INGESTION COMPLETE")
    print("="*70)

    if args.dry_run:
        print("\nDRY RUN - No data ingested")
        print(f"Would process {len(merged_files)} cases")
    else:
        print(f"\nCases processed: {all_stats['cases_processed']}")
        print(f"Episodes created: {all_stats['episodes_created']:,}")
        print(f"Relationships created: {all_stats['relationships_created']:,}")
        print(f"Errors: {len(all_stats['errors'])}")

        if all_stats['errors']:
            print("\nSample errors (first 10):")
            for err in all_stats['errors'][:10]:
                print(f"  - {err}")

        # Post-check
        result = graph.query("MATCH (n) RETURN count(n)")
        nodes_after = result.result_set[0][0]
        result = graph.query("MATCH ()-[r]->() RETURN count(r)")
        rels_after = result.result_set[0][0]
        result = graph.query("MATCH (ep:Episode) RETURN count(ep)")
        total_episodes = result.result_set[0][0]

        print()
        print(f"Nodes after: {nodes_after:,} (+{nodes_after - nodes_before:,})")
        print(f"Relationships after: {rels_after:,} (+{rels_after - rels_before:,})")
        print(f"Total Episode nodes: {total_episodes:,}")

        print()
        print("✅ Episodes ingested with semantic embeddings!")


if __name__ == "__main__":
    main()
