#!/usr/bin/env python3
"""Test the new workflow management tools."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, '/deps/Roscoe/src')


def test_update_landmark():
    """Test the update_landmark tool."""
    from roscoe.agents.paralegal.tools import update_landmark
    
    print("=" * 60)
    print("TEST: update_landmark")
    print("=" * 60)
    
    # Test updating a landmark
    result = update_landmark(
        case_name="Caryn-McCay-MVA-7-30-2023",
        landmark_id="retainer_signed",
        status="complete",
        notes="Test - signed via DocuSign"
    )
    print(result)
    print()


def test_get_workflow_status():
    """Test the get_case_workflow_status tool."""
    from roscoe.agents.paralegal.tools import get_case_workflow_status
    
    print("=" * 60)
    print("TEST: get_case_workflow_status")
    print("=" * 60)
    
    result = get_case_workflow_status("Caryn-McCay-MVA-7-30-2023")
    print(result)
    print()


def test_advance_phase():
    """Test the advance_phase tool."""
    from roscoe.agents.paralegal.tools import advance_phase
    
    print("=" * 60)
    print("TEST: advance_phase")
    print("=" * 60)
    
    # First try without force (should show blockers if any remain)
    result = advance_phase("Caryn-McCay-MVA-7-30-2023")
    print(result)
    print()


def main():
    # Set environment
    os.environ["GRAPHITI_ENABLED"] = "true"
    
    print("\n" + "=" * 60)
    print("WORKFLOW TOOLS TEST SUITE")
    print("=" * 60 + "\n")
    
    # Run tests
    test_get_workflow_status()
    test_update_landmark()
    test_get_workflow_status()  # Show updated status
    test_advance_phase()


if __name__ == "__main__":
    main()
