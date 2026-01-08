#!/usr/bin/env python3
"""Test episode with minimal custom types to isolate the Cypher error."""

import asyncio
from datetime import datetime
import sys
from typing import Optional

sys.path.insert(0, "/deps/Roscoe/src")

from pydantic import BaseModel, Field


# Minimal entity types (no 'name' field - it's protected)
class Person(BaseModel):
    """A person entity."""
    occupation: Optional[str] = Field(default=None, description="Job or role")


class Location(BaseModel):
    """A location entity."""
    location_type: Optional[str] = Field(default=None, description="Type of location")


# Minimal edge type
class LocatedAt(BaseModel):
    """Located at relationship."""
    pass


async def test():
    from roscoe.core.graphiti_client import get_graphiti
    from graphiti_core.nodes import EpisodeType
    
    g = await get_graphiti()
    
    # Minimal entity types dict
    entity_types = {
        "Person": Person,
        "Location": Location,
    }
    
    edge_types = {
        "LocatedAt": LocatedAt,
    }
    
    edge_type_map = {
        ("Person", "Location"): ["LocatedAt"],
        ("Entity", "Entity"): ["RelatesTo"],
    }
    
    print("Test: Add episode with MINIMAL custom types")
    print("=" * 50)
    print(f"Entity types: {list(entity_types.keys())}")
    print(f"Edge types: {list(edge_types.keys())}")
    print()
    
    try:
        result = await g.add_episode(
            name="Test: Minimal Types",
            episode_body="John Smith works as a lawyer in Louisville, Kentucky.",
            source=EpisodeType.text,
            source_description="test",
            reference_time=datetime.now(),
            group_id="roscoe_graph_v2",
            entity_types=entity_types,
            edge_types=edge_types,
            edge_type_map=edge_type_map,
        )
        print(f"SUCCESS! Nodes: {len(result.nodes)}, Edges: {len(result.edges)}")
        for node in result.nodes:
            etype = getattr(node, 'entity_type', 'unknown')
            print(f"  - {node.name} (type: {etype})")
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
