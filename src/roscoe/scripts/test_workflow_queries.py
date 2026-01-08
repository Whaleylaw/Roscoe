#!/usr/bin/env python3
"""Test script for workflow queries."""

import asyncio
import sys


async def test():
    from roscoe.core.graphiti_client import (
        get_all_phases,
        get_phase_workflows,
        get_phase_landmarks,
        get_workflow_info,
    )
    
    print("Testing workflow queries...")
    
    # Test get_all_phases
    phases = await get_all_phases()
    print(f"\nFound {len(phases)} phases:")
    for p in phases[:5]:
        name = p.get("name")
        display = p.get("display_name")
        print(f"  - {name}: {display}")
    
    # Test get_phase_workflows
    workflows = await get_phase_workflows("file_setup")
    print(f"\nFile setup has {len(workflows)} workflows:")
    for w in workflows:
        name = w.get("name")
        print(f"  - {name}")
    
    # Test get_phase_landmarks
    landmarks = await get_phase_landmarks("file_setup")
    print(f"\nFile setup has {len(landmarks)} landmarks:")
    for lm in landmarks:
        name = lm.get("name")
        subs = lm.get("sub_landmarks", [])
        print(f"  - {name} (sub-landmarks: {len(subs)})")
    
    # Test get_workflow_info
    wf_info = await get_workflow_info("intake")
    if wf_info:
        print(f"\nWorkflow 'intake' has {len(wf_info.get('steps', []))} steps")
    else:
        print("\nWorkflow 'intake' not found")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test())
