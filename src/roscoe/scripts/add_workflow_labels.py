#!/usr/bin/env python3
"""
Add type-specific labels to workflow entities

Workflow entities currently have only :Entity label.
This script adds the type-specific label based on entity_type property:
- entity_type='Phase' → Add :Phase label
- entity_type='Landmark' → Add :Landmark label
- etc.

Usage:
    python -m roscoe.scripts.add_workflow_labels
"""

import os
from falkordb import FalkorDB


def add_labels():
    """Add type-specific labels to ALL entities (not just workflow)."""
    db = FalkorDB(
        host=os.getenv("FALKORDB_HOST", "roscoe-graphdb"),
        port=int(os.getenv("FALKORDB_PORT", "6379"))
    )
    graph = db.select_graph("roscoe_graph")

    print("=" * 70)
    print("ADDING TYPE-SPECIFIC LABELS TO ALL ENTITIES")
    print("=" * 70)

    # Map entity_type to label (both workflow and case entities)
    type_to_label = {
        # Workflow entities
        "Phase": "Phase",
        "SubPhase": "SubPhase",
        "Landmark": "Landmark",
        "WorkflowDef": "WorkflowDef",
        "WorkflowStep": "WorkflowStep",
        "WorkflowChecklist": "WorkflowChecklist",
        "WorkflowSkill": "WorkflowSkill",
        "WorkflowTemplate": "WorkflowTemplate",
        "WorkflowTool": "WorkflowTool",
        "LandmarkStatus": "LandmarkStatus",
        # Case entities (skip Case and Client - already have labels)
        "MedicalProvider": "MedicalProvider",
        "Insurer": "Insurer",
        "Adjuster": "Adjuster",
        "PIPClaim": "PIPClaim",
        "BIClaim": "BIClaim",
        "UMClaim": "UMClaim",
        "UIMClaim": "UIMClaim",
        "WCClaim": "WCClaim",
        "MedPayClaim": "MedPayClaim",
        "Lien": "Lien",
        "LienHolder": "LienHolder",
        "Attorney": "Attorney",
        "Court": "Court",
        "Defendant": "Defendant",
        "Organization": "Organization",
        "Pleading": "Pleading",
        "Vendor": "Vendor",
    }

    total_updated = 0

    for entity_type, label in type_to_label.items():
        # Find entities of this type (any group_id)
        find_query = f"""
        MATCH (n:Entity)
        WHERE n.entity_type = '{entity_type}'
        RETURN count(n) as count
        """
        result = graph.query(find_query)
        count = result.result_set[0][0] if result.result_set else 0

        if count == 0:
            continue  # Skip silently

        # Add the label
        update_query = f"""
        MATCH (n:Entity)
        WHERE n.entity_type = '{entity_type}'
        SET n:{label}
        RETURN count(n) as updated
        """

        result = graph.query(update_query)
        updated = result.result_set[0][0] if result.result_set else 0

        total_updated += updated
        print(f"  ✓ {entity_type}: Added :{label} to {updated} entities")

    print()
    print("=" * 70)
    print(f"✅ COMPLETE - Updated {total_updated} entities")
    print("=" * 70)


if __name__ == "__main__":
    add_labels()
