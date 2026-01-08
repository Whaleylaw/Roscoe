#!/usr/bin/env python3
"""Test the new graphiti_client helper functions."""

import asyncio


async def test():
    from roscoe.core.graphiti_client import (
        get_case_phase, 
        get_case_landmark_statuses, 
        check_phase_can_advance, 
        get_case_workflow_state
    )
    
    # Test on a specific case
    case = "Caryn-McCay-MVA-7-30-2023"
    
    print("=" * 60)
    print(f"Testing helper functions for: {case}")
    print("=" * 60)
    
    # Get current phase
    phase = await get_case_phase(case)
    print(f"\nCurrent Phase: {phase}")
    
    # Get landmark statuses
    landmarks = await get_case_landmark_statuses(case)
    print(f"\nLandmarks ({len(landmarks)} total):")
    for lm in landmarks[:5]:
        lid = lm.get("landmark_id")
        status = lm.get("status")
        print(f"  {lid}: {status}")
    
    # Check if can advance
    check = await check_phase_can_advance(case)
    can_adv = check.get("can_advance")
    print(f"\nCan Advance: {can_adv}")
    blockers = check.get("blocking_landmarks", [])
    if blockers:
        ids = [b.get("landmark_id") for b in blockers]
        print(f"Blocking: {ids}")
    
    # Get full workflow state
    state = await get_case_workflow_state(case)
    print("\nFull Workflow State:")
    cp = state.get("current_phase", {})
    cpl = state.get("current_phase_landmarks", {})
    print(f"  Phase: {cp.get('name')}")
    print(f"  Can Advance: {state.get('can_advance')}")
    print(f"  Landmarks: {cpl.get('total')} total, {cpl.get('complete')} complete")
    
    # Test on another case with different status
    case2 = "Abigail-Whaley-MVA-10-24-2024"
    print(f"\n{'=' * 60}")
    print(f"Testing: {case2}")
    print("=" * 60)
    
    phase2 = await get_case_phase(case2)
    print(f"Phase: {phase2}")
    
    check2 = await check_phase_can_advance(case2)
    print(f"Can Advance: {check2.get('can_advance')}")


def main():
    asyncio.run(test())


if __name__ == "__main__":
    main()
