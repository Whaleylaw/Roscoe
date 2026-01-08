#!/usr/bin/env python3
"""Test ingesting a single note to debug errors."""

import asyncio
import json
import sys
from datetime import datetime

sys.path.insert(0, "/deps/Roscoe/src")


async def test_single():
    from roscoe.core.graphiti_client import (
        get_graphiti, ENTITY_TYPES_DICT, EDGE_TYPES_DICT, EDGE_TYPE_MAP
    )
    from graphiti_core.nodes import EpisodeType
    
    print("Loading notes...")
    with open('/mnt/workspace/projects/Caryn-McCay-MVA-7-30-2023/Case Information/notes.json') as f:
        notes = json.load(f)
    
    # Get a meaningful note (skip phase changes)
    note = notes[2]
    print(f"Note ID: {note['id']}")
    print(f"Note text: {note['note'][:200]}...")
    print()
    
    g = await get_graphiti()
    
    body = f"""Case: Caryn-McCay-MVA-7-30-2023
Client: Caryn McCay
Date: {note.get('last_activity', '')}
Author: {note.get('author_name', 'Unknown')}

{note.get('note', '')}"""

    print("Adding episode...")
    try:
        result = await g.add_episode(
            name=f"Note {note['id']}",
            episode_body=body,
            source=EpisodeType.text,
            source_description="case_notes",
            reference_time=datetime.now(),
            group_id="roscoe_graph_v2",
            entity_types=ENTITY_TYPES_DICT,
            edge_types=EDGE_TYPES_DICT,
            edge_type_map=EDGE_TYPE_MAP,
        )
        print(f"SUCCESS: {len(result.nodes)} nodes, {len(result.edges)} edges")
        for node in result.nodes[:5]:
            print(f"  - {node.name}")
    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_single())
