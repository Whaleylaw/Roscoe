#!/usr/bin/env python3
"""Test with many types to find the threshold."""

import asyncio
from datetime import datetime, date
import sys
from typing import Optional

sys.path.insert(0, "/deps/Roscoe/src")

from pydantic import BaseModel, Field


# Define all types
class Case(BaseModel):
    case_type: Optional[str] = None

class Client(BaseModel):
    phone: Optional[str] = None

class Insurer(BaseModel):
    phone: Optional[str] = None

class Adjuster(BaseModel):
    phone: Optional[str] = None

class PIPClaim(BaseModel):
    claim_number: Optional[str] = None

class BIClaim(BaseModel):
    claim_number: Optional[str] = None

class UMClaim(BaseModel):
    claim_number: Optional[str] = None

class UIMClaim(BaseModel):
    claim_number: Optional[str] = None

class WCClaim(BaseModel):
    claim_number: Optional[str] = None

class MedPayClaim(BaseModel):
    claim_number: Optional[str] = None

class MedicalProvider(BaseModel):
    specialty: Optional[str] = None

class Lien(BaseModel):
    amount: Optional[float] = None

class Document(BaseModel):
    path: Optional[str] = None

class LawFirm(BaseModel):
    phone: Optional[str] = None

class Attorney(BaseModel):
    role: Optional[str] = None

class Court(BaseModel):
    county: Optional[str] = None

class Pleading(BaseModel):
    pleading_type: Optional[str] = None

class Expense(BaseModel):
    amount: Optional[float] = None

class Settlement(BaseModel):
    gross_amount: Optional[float] = None

class Phase(BaseModel):
    display_name: Optional[str] = None

class Landmark(BaseModel):
    landmark_id: Optional[str] = None

class WorkflowDef(BaseModel):
    display_name: Optional[str] = None

class WorkflowStep(BaseModel):
    step_id: Optional[str] = None

class WorkflowChecklist(BaseModel):
    path: Optional[str] = None

class WorkflowSkill(BaseModel):
    path: Optional[str] = None

class WorkflowTemplate(BaseModel):
    path: Optional[str] = None

class WorkflowTool(BaseModel):
    path: Optional[str] = None


ALL_TYPES = {
    "Case": Case,
    "Client": Client,
    "Insurer": Insurer,
    "Adjuster": Adjuster,
    "PIPClaim": PIPClaim,
    "BIClaim": BIClaim,
    "UMClaim": UMClaim,
    "UIMClaim": UIMClaim,
    "WCClaim": WCClaim,
    "MedPayClaim": MedPayClaim,
    "MedicalProvider": MedicalProvider,
    "Lien": Lien,
    "Document": Document,
    "LawFirm": LawFirm,
    "Attorney": Attorney,
    "Court": Court,
    "Pleading": Pleading,
    "Expense": Expense,
    "Settlement": Settlement,
    "Phase": Phase,
    "Landmark": Landmark,
    "WorkflowDef": WorkflowDef,
    "WorkflowStep": WorkflowStep,
    "WorkflowChecklist": WorkflowChecklist,
    "WorkflowSkill": WorkflowSkill,
    "WorkflowTemplate": WorkflowTemplate,
    "WorkflowTool": WorkflowTool,
}


async def test_type_set(name, entity_types):
    from roscoe.core.graphiti_client import get_graphiti
    from graphiti_core.nodes import EpisodeType
    
    g = await get_graphiti()
    
    print(f"\nTest: {name} ({len(entity_types)} types)")
    
    try:
        result = await g.add_episode(
            name=f"Test: {name}",
            episode_body="Case involves client John. He treats at Baptist Health. State Farm has the BI claim.",
            source=EpisodeType.text,
            source_description="test",
            reference_time=datetime.now(),
            group_id="roscoe_graph_v2",
            entity_types=entity_types,
            edge_types={},
            edge_type_map={("Entity", "Entity"): ["RelatesTo"]},
        )
        print(f"  SUCCESS! Nodes: {len(result.nodes)}")
        return True
    except Exception as e:
        print(f"  FAILED: {str(e)[:100]}")
        return False


async def main():
    print("=" * 60)
    print("LARGE TYPE SET TESTING")
    print("=" * 60)
    
    type_names = list(ALL_TYPES.keys())
    
    # Test incrementally: 5, 10, 15, 20, 25, 27
    for count in [5, 10, 15, 20, 25, 27]:
        subset = {k: ALL_TYPES[k] for k in type_names[:count]}
        success = await test_type_set(f"First {count} types", subset)
        if not success:
            print(f"\n!!! FAILURE at {count} types !!!")
            # Test which specific type caused it
            for i in range(count-1, count):
                test_subset = {k: ALL_TYPES[k] for k in type_names[:i+1]}
                print(f"\nTrying with types: {list(test_subset.keys())}")
                await test_type_set(f"Narrowing: {i+1} types", test_subset)
            break
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
