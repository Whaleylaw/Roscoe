#!/usr/bin/env python3
"""
Graphiti Memory Card Ingestion

Loads Memory Cards into Graphiti in the correct order:
1. Entity Cards - Create nodes with proper labels
2. Relationship Cards - Create edges between nodes
3. Episode Cards - Add temporal facts via add_episode()

Usage:
    python ingest_memory_cards.py [--cards-dir path] [--graph-name name] [--dry-run]
"""

import json
import asyncio
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Graphiti imports
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.nodes import EpisodeType


# =============================================================================
# Configuration
# =============================================================================

CARDS_DIR = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards")
DEFAULT_GRAPH = "roscoe_graph_v2"  # Use v2 for testing

# Load API keys from backup file
def load_api_keys() -> dict:
    keys = {}
    keys_file = Path("/Volumes/X10 Pro/Roscoe/api-keys-backup.txt")
    if keys_file.exists():
        with open(keys_file) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    keys[key] = value
    return keys


# =============================================================================
# Graphiti Client Setup
# =============================================================================

async def create_graphiti_client(graph_name: str) -> Graphiti:
    """Create a Graphiti client for the specified graph using Gemini."""
    keys = load_api_keys()
    api_key = keys.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found")
    
    # Configure Gemini
    llm_config = LLMConfig(
        api_key=api_key,
        model="gemini-2.0-flash-exp",
    )
    
    llm_client = GeminiClient(config=llm_config)
    
    embedder_config = GeminiEmbedderConfig(
        api_key=api_key,
        embedding_model="text-embedding-004",
    )
    embedder = GeminiEmbedder(config=embedder_config)
    
    reranker = GeminiRerankerClient(config=llm_config)
    
    # FalkorDB connection
    falkor_host = os.environ.get("FALKORDB_HOST", "localhost")
    falkor_port = int(os.environ.get("FALKORDB_PORT", "6380"))
    
    falkor_driver = FalkorDriver(
        host=falkor_host,
        port=falkor_port,
        database=graph_name,
    )
    
    graphiti = Graphiti(
        graph_driver=falkor_driver,
        llm_client=llm_client,
        embedder=embedder,
        cross_encoder=reranker,
    )
    
    await graphiti.build_indices_and_constraints()
    
    return graphiti


# =============================================================================
# Entity Card Ingestion
# =============================================================================

async def ingest_entity_cards(
    graphiti: Graphiti,
    cards_dir: Path,
    group_id: str,
    dry_run: bool = False,
) -> dict:
    """
    Ingest Entity Cards into Graphiti.
    
    For each entity, we create an episode that describes the entity,
    allowing Graphiti's LLM to create the node with proper type.
    """
    import asyncio
    
    entities_dir = cards_dir / "entities"
    stats = {"total": 0, "by_type": {}, "errors": 0}
    
    if not entities_dir.exists():
        print(f"  No entities directory found at {entities_dir}")
        return stats
    
    # Process each entity file
    entity_files = list(entities_dir.glob("*.json"))
    print(f"  Found {len(entity_files)} entity files")
    
    for entity_file in entity_files:
        if entity_file.name == "entity_generation_stats.json":
            continue
        
        with open(entity_file, 'r', encoding='utf-8') as f:
            entities = json.load(f)
        
        entity_type = entities[0]["entity_type"] if entities else "Unknown"
        print(f"  Processing {len(entities)} {entity_type} entities from {entity_file.name}...")
        
        for entity in entities:
            stats["total"] += 1
            stats["by_type"][entity["entity_type"]] = stats["by_type"].get(entity["entity_type"], 0) + 1
            
            if dry_run:
                continue
            
            # Create an episode describing this entity
            entity_name = entity["name"]
            entity_type = entity["entity_type"]
            attributes = entity.get("attributes", {})
            
            # Build a description
            attr_str = ", ".join(f"{k}={v}" for k, v in attributes.items() if v)
            episode_body = f"Entity definition: {entity_name} is a {entity_type}. {attr_str}"
            
            try:
                await graphiti.add_episode(
                    name=f"Entity: {entity_name}",
                    episode_body=episode_body,
                    source=EpisodeType.text,
                    source_description="memory_card_import",
                    reference_time=datetime.now(),
                    group_id=group_id,
                )
                # Add small delay to avoid rate limits
                await asyncio.sleep(0.5)
            except Exception as e:
                stats["errors"] += 1
                if stats["errors"] <= 5:
                    print(f"    Error ingesting entity {entity_name}: {e}")
    
    return stats


# =============================================================================
# Relationship Card Ingestion
# =============================================================================

async def ingest_relationship_cards(
    graphiti: Graphiti,
    cards_dir: Path,
    group_id: str,
    dry_run: bool = False,
) -> dict:
    """
    Ingest Relationship Cards into Graphiti.
    
    For each relationship, we create an episode that describes the connection,
    allowing Graphiti's LLM to extract and create the edge.
    """
    import asyncio
    
    relationships_dir = cards_dir / "relationships"
    stats = {"total": 0, "by_type": {}, "errors": 0}
    
    if not relationships_dir.exists():
        print(f"  No relationships directory found at {relationships_dir}")
        return stats
    
    # Load the main relationships file
    all_rel_file = relationships_dir / "all_relationships.json"
    if not all_rel_file.exists():
        print(f"  No all_relationships.json found")
        return stats
    
    with open(all_rel_file, 'r', encoding='utf-8') as f:
        relationships = json.load(f)
    
    print(f"  Processing {len(relationships)} relationships...")
    
    for rel in relationships:
        stats["total"] += 1
        edge_type = rel["edge_type"]
        stats["by_type"][edge_type] = stats["by_type"].get(edge_type, 0) + 1
        
        if dry_run:
            continue
        
        # Create an episode describing this relationship in natural language
        source = rel["source"]
        target = rel["target"]
        context = rel.get("context", "")
        
        episode_body = (
            f"Relationship: {source['name']} ({source['entity_type']}) "
            f"{edge_type} {target['name']} ({target['entity_type']})"
        )
        if context:
            episode_body += f" in context of {context}"
        
        try:
            await graphiti.add_episode(
                name=f"Relationship: {source['name']} -> {target['name']}",
                episode_body=episode_body,
                source=EpisodeType.text,
                source_description="memory_card_import",
                reference_time=datetime.now(),
                group_id=group_id,
            )
            # Add delay to avoid rate limits
            await asyncio.sleep(0.5)
        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] <= 5:
                print(f"    Error ingesting relationship: {e}")
    
    return stats


# =============================================================================
# Episode Card Ingestion
# =============================================================================

async def ingest_episode_cards(
    graphiti: Graphiti,
    cards_dir: Path,
    group_id: str,
    dry_run: bool = False,
    max_episodes: Optional[int] = None,
    skip_episodes: int = 0,
) -> dict:
    """
    Ingest Episode Cards into Graphiti.
    
    Episodes represent temporal facts about cases. Each episode is sent
    to Graphiti's LLM for entity extraction and relationship inference.
    """
    import asyncio
    
    episodes_dir = cards_dir / "episodes"
    stats = {"total": 0, "by_case": {}, "errors": 0}
    
    if not episodes_dir.exists():
        print(f"  No episodes directory found at {episodes_dir}")
        return stats
    
    # Load all episodes
    all_episodes_file = episodes_dir / "all_episodes.json"
    if not all_episodes_file.exists():
        print(f"  No all_episodes.json found")
        return stats
    
    with open(all_episodes_file, 'r', encoding='utf-8') as f:
        episodes = json.load(f)
    
    total_episodes = len(episodes)
    
    # Skip already-processed episodes (for resuming)
    if skip_episodes > 0:
        episodes = episodes[skip_episodes:]
        print(f"  Skipping first {skip_episodes} episodes (already ingested)")
    
    if max_episodes:
        episodes = episodes[:max_episodes]
    
    print(f"  Processing {len(episodes)} episodes (of {total_episodes} total)...")
    
    for i, ep in enumerate(episodes):
        if (i + 1) % 10 == 0:
            print(f"    Processed {i + 1}/{len(episodes)} episodes...")
        
        stats["total"] += 1
        case_name = ep["case"]
        stats["by_case"][case_name] = stats["by_case"].get(case_name, 0) + 1
        
        if dry_run:
            continue
        
        # Parse date
        date_str = ep.get("date", "")
        try:
            ref_time = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
        except:
            ref_time = datetime.now()
        
        # Build episode body with context
        summary = ep.get("summary", "")
        episode_body = f"Case {case_name}: {summary}"
        
        # Add entity mentions if available
        entities = ep.get("entities", [])
        if entities:
            entity_names = [f"{e.get('name')} ({e.get('type')})" for e in entities if e.get('name')]
            if entity_names:
                episode_body += f" Mentions: {', '.join(entity_names)}"
        
        # Retry logic for rate limits
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await graphiti.add_episode(
                    name=f"Note: {case_name} - {date_str}",
                    episode_body=episode_body,
                    source=EpisodeType.text,
                    source_description=ep.get("note_source") or ep.get("author_type") or "note",
                    reference_time=ref_time,
                    group_id=group_id,
                )
                # Add delay to avoid rate limits
                # OpenAI has higher limits - use 2s delay
                await asyncio.sleep(2.0)
                break  # Success, exit retry loop
            except Exception as e:
                error_str = str(e).lower()
                if "rate limit" in error_str:
                    wait_time = 60  # Fixed 60s wait for rate limits
                    if attempt < max_retries - 1:
                        print(f"    Rate limited, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                        await asyncio.sleep(wait_time)
                    else:
                        stats["errors"] += 1
                        if stats["errors"] <= 10:
                            print(f"    Failed after {max_retries} attempts: {e}")
                else:
                    stats["errors"] += 1
                    if stats["errors"] <= 10:
                        print(f"    Error ingesting episode: {e}")
                    break  # Non-rate-limit error, don't retry
    
    return stats


# =============================================================================
# Main Ingestion
# =============================================================================

async def ingest_all(
    cards_dir: Path,
    graph_name: str,
    dry_run: bool = False,
    skip_entities: bool = False,
    skip_relationships: bool = False,
    skip_episodes: bool = False,
    max_episodes: Optional[int] = None,
    skip_first_episodes: int = 0,
) -> dict:
    """
    Run the full ingestion pipeline.
    """
    print("=" * 60)
    print("MEMORY CARD INGESTION")
    print("=" * 60)
    print(f"\nCards directory: {cards_dir}")
    print(f"Graph name: {graph_name}")
    print(f"Dry run: {dry_run}")
    print()
    
    stats = {
        "entities": {},
        "relationships": {},
        "episodes": {},
    }
    
    # Create Graphiti client
    if not dry_run:
        print("Creating Graphiti client...")
        graphiti = await create_graphiti_client(graph_name)
    else:
        graphiti = None
        print("DRY RUN - no actual ingestion will occur")
    
    group_id = graph_name
    
    # 1. Ingest entities
    if not skip_entities:
        print("\n--- Stage 1: Entity Cards ---")
        stats["entities"] = await ingest_entity_cards(
            graphiti, cards_dir, group_id, dry_run
        )
        print(f"  Total: {stats['entities'].get('total', 0):,}")
        print(f"  Errors: {stats['entities'].get('errors', 0):,}")
    
    # 2. Ingest relationships
    if not skip_relationships:
        print("\n--- Stage 2: Relationship Cards ---")
        stats["relationships"] = await ingest_relationship_cards(
            graphiti, cards_dir, group_id, dry_run
        )
        print(f"  Total: {stats['relationships'].get('total', 0):,}")
        print(f"  Errors: {stats['relationships'].get('errors', 0):,}")
    
    # 3. Ingest episodes
    if not skip_episodes:
        print("\n--- Stage 3: Episode Cards ---")
        stats["episodes"] = await ingest_episode_cards(
            graphiti, cards_dir, group_id, dry_run, max_episodes, skip_first_episodes
        )
        print(f"  Total: {stats['episodes'].get('total', 0):,}")
        print(f"  Errors: {stats['episodes'].get('errors', 0):,}")
    
    # Close connection
    if graphiti:
        await graphiti.close()
    
    # Print summary
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"\nEntities:      {stats['entities'].get('total', 0):,} (errors: {stats['entities'].get('errors', 0)})")
    print(f"Relationships: {stats['relationships'].get('total', 0):,} (errors: {stats['relationships'].get('errors', 0)})")
    print(f"Episodes:      {stats['episodes'].get('total', 0):,} (errors: {stats['episodes'].get('errors', 0)})")
    
    # Save stats
    stats_path = cards_dir / "ingestion_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nStats saved to {stats_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Ingest Memory Cards into Graphiti")
    parser.add_argument(
        "--cards-dir",
        type=Path,
        default=CARDS_DIR,
        help="Directory containing memory card files"
    )
    parser.add_argument(
        "--graph-name",
        type=str,
        default=DEFAULT_GRAPH,
        help="Graphiti graph/database name"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count cards but don't actually ingest"
    )
    parser.add_argument(
        "--skip-entities",
        action="store_true",
        help="Skip entity ingestion"
    )
    parser.add_argument(
        "--skip-relationships",
        action="store_true",
        help="Skip relationship ingestion"
    )
    parser.add_argument(
        "--skip-episodes",
        action="store_true",
        help="Skip episode ingestion"
    )
    parser.add_argument(
        "--max-episodes",
        type=int,
        default=None,
        help="Maximum episodes to ingest (for testing)"
    )
    parser.add_argument(
        "--resume-from",
        type=int,
        default=0,
        help="Episode index to resume from (skip first N episodes)"
    )
    
    args = parser.parse_args()
    
    if not args.cards_dir.exists():
        print(f"Error: Cards directory not found: {args.cards_dir}")
        return 1
    
    asyncio.run(ingest_all(
        cards_dir=args.cards_dir,
        graph_name=args.graph_name,
        dry_run=args.dry_run,
        skip_entities=args.skip_entities,
        skip_relationships=args.skip_relationships,
        skip_episodes=args.skip_episodes,
        max_episodes=args.max_episodes,
        skip_first_episodes=args.resume_from,
    ))
    return 0


if __name__ == "__main__":
    exit(main())
