#!/usr/bin/env python3
"""Test with ONLY Case type to isolate the issue."""

import asyncio
from datetime import datetime, date
import sys
from typing import Optional

sys.path.insert(0, "/deps/Roscoe/src")

from pydantic import BaseModel, Field


class Case(BaseModel):
    """A personal injury case."""
    case_type: Optional[str] = Field(default=None, description="Type: MVA, Premise")


async def test():
    from roscoe.core.graphiti_client import get_graphiti
    from graphiti_core.nodes import EpisodeType
    
    g = await get_graphiti()
    
    entity_types = {"Case": Case}
    edge_types = {}
    edge_type_map = {("Entity", "Entity"): ["RelatesTo"]}
    
    print("Test: ONLY Case type")
    print("=" * 50)
    
    try:
        result = await g.add_episode(
            name="Test: Case Only",
            episode_body="Case Caryn-McCay-MVA-7-30-2023 is a motor vehicle accident case from July 2023.",
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
            print(f"  - {node.name}")
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
