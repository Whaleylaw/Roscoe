#!/usr/bin/env python3
"""Test the refactored GraphWorkflowStateComputer."""

import asyncio


async def test():
    from roscoe.workflow_engine.orchestrator.graph_state_computer import (
        GraphWorkflowStateComputer,
        get_workflow_state_prompt,
        get_case_state_from_graph,
    )
    
    # Test on a couple cases
    cases = [
        "Caryn-McCay-MVA-7-30-2023",
        "Abigail-Whaley-MVA-10-24-2024",
        "Fidel-Antonio-Bueso-Sandoval-MVA-06-13-2",
    ]
    
    computer = GraphWorkflowStateComputer()
    
    for case in cases:
        print("=" * 70)
        print(f"CASE: {case}")
        print("=" * 70)
        
        # Get state
        state = await computer.compute_state(case)
        
        print(f"Client: {state.client_name}")
        print(f"Phase: {state.current_phase} ({state.phase_display_name})")
        print(f"Track: {state.phase_track}")
        print(f"Can Advance: {state.can_advance}")
        print(f"Next Phase: {state.next_phase}")
        print(f"Landmarks: {state.landmarks_complete}/{state.landmarks_total} complete")
        
        if state.blocking_landmarks:
            print(f"Blocking: {[b.get('landmark_id') for b in state.blocking_landmarks]}")
        
        if state.workflows_needed:
            print("Workflows Needed:")
            for wf in state.workflows_needed[:2]:
                print(f"  - {wf.get('landmark')}: {[w.get('workflow_name') for w in wf.get('workflows', [])]}")
        
        print(f"Insurance Claims: {len(state.insurance_claims)}")
        print(f"Medical Providers: {len(state.medical_providers)}")
        print(f"Liens: {len(state.liens)}")
        
        if state.statute_of_limitations.get("status") != "unknown":
            sol = state.statute_of_limitations
            print(f"SOL: {sol.get('deadline')} ({sol.get('days_remaining')} days, {sol.get('status')})")
        
        print()
    
    # Test the prompt format
    print("=" * 70)
    print("PROMPT FORMAT TEST")
    print("=" * 70)
    prompt = await get_workflow_state_prompt("Caryn-McCay-MVA-7-30-2023")
    print(prompt)
    
    # Test the dict format
    print("\n" + "=" * 70)
    print("DICT FORMAT TEST")
    print("=" * 70)
    state_dict = await get_case_state_from_graph("Caryn-McCay-MVA-7-30-2023")
    print(f"Keys: {list(state_dict.keys())}")
    print(f"Current Phase: {state_dict.get('current_phase')}")
    print(f"Landmarks Complete: {state_dict.get('landmarks', {}).get('complete')}")


def main():
    asyncio.run(test())


if __name__ == "__main__":
    main()
