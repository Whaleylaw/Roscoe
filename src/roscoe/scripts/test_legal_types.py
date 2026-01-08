#!/usr/bin/env python3
"""Test episode with core legal entity types."""

import asyncio
from datetime import datetime, date
import sys
from typing import Optional

sys.path.insert(0, "/deps/Roscoe/src")

from pydantic import BaseModel, Field


# Core legal entity types (no 'name' field)
class Case(BaseModel):
    """A personal injury case."""
    case_type: Optional[str] = Field(default=None, description="Type: MVA, Premise, WC")
    accident_date: Optional[date] = Field(default=None, description="Date of accident")
    phase: Optional[str] = Field(default=None, description="Current phase")


class Client(BaseModel):
    """A client/plaintiff."""
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email")


class MedicalProvider(BaseModel):
    """A medical provider."""
    specialty: Optional[str] = Field(default=None, description="Specialty")
    phone: Optional[str] = Field(default=None, description="Phone")


class Insurer(BaseModel):
    """An insurance company."""
    phone: Optional[str] = Field(default=None, description="Phone")


class Attorney(BaseModel):
    """An attorney."""
    role: Optional[str] = Field(default=None, description="Role: plaintiff, defense")
    firm_name: Optional[str] = Field(default=None, description="Law firm")


# Edge types
class TreatingAt(BaseModel):
    """Treatment relationship."""
    start_date: Optional[date] = Field(default=None, description="First visit")


class HasClaim(BaseModel):
    """Insurance claim relationship."""
    claim_number: Optional[str] = Field(default=None, description="Claim number")


async def test():
    from roscoe.core.graphiti_client import get_graphiti
    from graphiti_core.nodes import EpisodeType
    
    g = await get_graphiti()
    
    entity_types = {
        "Case": Case,
        "Client": Client,
        "MedicalProvider": MedicalProvider,
        "Insurer": Insurer,
        "Attorney": Attorney,
    }
    
    edge_types = {
        "TreatingAt": TreatingAt,
        "HasClaim": HasClaim,
    }
    
    edge_type_map = {
        ("Client", "Case"): ["PlaintiffIn"],
        ("Client", "MedicalProvider"): ["TreatingAt"],
        ("Case", "Insurer"): ["HasClaim"],
        ("Attorney", "Case"): ["RepresentsClient"],
        ("Entity", "Entity"): ["RelatesTo"],
    }
    
    print("Test: Add episode with CORE LEGAL types")
    print("=" * 50)
    print(f"Entity types: {list(entity_types.keys())}")
    print()
    
    episode_body = """
    Case: Caryn-McCay-MVA-7-30-2023
    Client Caryn McCay was injured in a motor vehicle accident on July 30, 2023.
    Attorney Aaron Whaley of Whaley Law Firm is representing Caryn McCay.
    Caryn is treating at Baptist Health Emergency Department for neck and back injuries.
    The at-fault driver has State Farm Insurance with a BI claim.
    Allstate Insurance is handling the PIP claim.
    """
    
    try:
        result = await g.add_episode(
            name="Test: Legal Types",
            episode_body=episode_body,
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
