#!/usr/bin/env python3
"""Incrementally test types to find which causes the Cypher error."""

import asyncio
from datetime import datetime, date
import sys
from typing import Optional

sys.path.insert(0, "/deps/Roscoe/src")

from pydantic import BaseModel, Field


# Define types one by one
class Case(BaseModel):
    """A personal injury case."""
    case_type: Optional[str] = Field(default=None, description="Type: MVA, Premise")

class Client(BaseModel):
    """A client."""
    phone: Optional[str] = Field(default=None, description="Phone")

class MedicalProvider(BaseModel):
    """A medical provider."""
    specialty: Optional[str] = Field(default=None, description="Specialty")

class Insurer(BaseModel):
    """An insurance company."""
    phone: Optional[str] = Field(default=None, description="Phone")

class Attorney(BaseModel):
    """An attorney."""
    role: Optional[str] = Field(default=None, description="Role")

# Types with 'date' fields
class CaseWithDate(BaseModel):
    """A case with date field."""
    accident_date: Optional[date] = Field(default=None, description="Date")


async def test_type_set(name, entity_types):
    from roscoe.core.graphiti_client import get_graphiti
    from graphiti_core.nodes import EpisodeType
    
    g = await get_graphiti()
    
    edge_types = {}
    edge_type_map = {("Entity", "Entity"): ["RelatesTo"]}
    
    print(f"\nTest: {name}")
    print(f"Types: {list(entity_types.keys())}")
    
    try:
        result = await g.add_episode(
            name=f"Test: {name}",
            episode_body="Case Caryn-McCay involves client Caryn McCay. She treats at Baptist Health. State Farm Insurance has the BI claim. Attorney Aaron Whaley represents her.",
            source=EpisodeType.text,
            source_description="test",
            reference_time=datetime.now(),
            group_id="roscoe_graph_v2",
            entity_types=entity_types,
            edge_types=edge_types,
            edge_type_map=edge_type_map,
        )
        print(f"  SUCCESS! Nodes: {len(result.nodes)}")
        return True
    except Exception as e:
        print(f"  FAILED: {str(e)[:80]}")
        return False


async def main():
    print("=" * 60)
    print("INCREMENTAL TYPE TESTING")
    print("=" * 60)
    
    # Test 1: Just Case
    await test_type_set("Case only", {"Case": Case})
    
    # Test 2: Case + Client
    await test_type_set("Case + Client", {"Case": Case, "Client": Client})
    
    # Test 3: Case + Client + MedicalProvider
    await test_type_set("+ MedicalProvider", {"Case": Case, "Client": Client, "MedicalProvider": MedicalProvider})
    
    # Test 4: Add Insurer
    await test_type_set("+ Insurer", {"Case": Case, "Client": Client, "MedicalProvider": MedicalProvider, "Insurer": Insurer})
    
    # Test 5: Add Attorney
    await test_type_set("+ Attorney", {"Case": Case, "Client": Client, "MedicalProvider": MedicalProvider, "Insurer": Insurer, "Attorney": Attorney})
    
    # Test 6: Case with date field
    await test_type_set("CaseWithDate", {"CaseWithDate": CaseWithDate})
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
