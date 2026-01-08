#!/usr/bin/env python3
"""Test insurance claim types."""

import asyncio
from datetime import datetime, date
import sys
from typing import Optional

sys.path.insert(0, "/deps/Roscoe/src")

from pydantic import BaseModel, Field


# Insurance claim types
class PIPClaim(BaseModel):
    """PIP insurance claim."""
    claim_number: Optional[str] = Field(default=None, description="Claim number")
    insurer_name: Optional[str] = Field(default=None, description="Insurance company")
    policy_limit: Optional[float] = Field(default=None, description="Policy limit")


class BIClaim(BaseModel):
    """BI insurance claim."""
    claim_number: Optional[str] = Field(default=None, description="Claim number")
    insurer_name: Optional[str] = Field(default=None, description="Insurance company")
    policy_limit: Optional[float] = Field(default=None, description="Policy limit")


class UMClaim(BaseModel):
    """UM insurance claim."""
    claim_number: Optional[str] = Field(default=None, description="Claim number")


class UIMClaim(BaseModel):
    """UIM insurance claim."""
    claim_number: Optional[str] = Field(default=None, description="Claim number")


class WCClaim(BaseModel):
    """WC insurance claim."""
    claim_number: Optional[str] = Field(default=None, description="Claim number")


class MedPayClaim(BaseModel):
    """MedPay insurance claim."""
    claim_number: Optional[str] = Field(default=None, description="Claim number")


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
            episode_body="The PIP claim with Allstate has number 12345. State Farm BI claim 67890 has policy limits of $100,000.",
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
        print(f"  FAILED: {str(e)[:100]}")
        return False


async def main():
    print("=" * 60)
    print("INSURANCE CLAIM TYPE TESTING")
    print("=" * 60)
    
    # Test claim types individually
    await test_type_set("PIPClaim", {"PIPClaim": PIPClaim})
    await test_type_set("BIClaim", {"BIClaim": BIClaim})
    await test_type_set("UMClaim", {"UMClaim": UMClaim})
    await test_type_set("UIMClaim", {"UIMClaim": UIMClaim})
    await test_type_set("WCClaim", {"WCClaim": WCClaim})
    await test_type_set("MedPayClaim", {"MedPayClaim": MedPayClaim})
    
    # Test all claim types together
    await test_type_set("All Claims", {
        "PIPClaim": PIPClaim,
        "BIClaim": BIClaim,
        "UMClaim": UMClaim,
        "UIMClaim": UIMClaim,
        "WCClaim": WCClaim,
        "MedPayClaim": MedPayClaim,
    })
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
