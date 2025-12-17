#!/usr/bin/env python3
"""
Test script for context chunk injection.

Tests the CaseContextMiddleware's chunk detection functionality with various query types.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from roscoe.core.case_context_middleware import CaseContextMiddleware


def test_chunk_detection():
    """Test chunk detection with various query types."""
    
    # Initialize middleware with workspace path
    workspace_dir = "/Volumes/X10 Pro/Roscoe/workspace_paralegal"
    
    try:
        middleware = CaseContextMiddleware(workspace_dir=workspace_dir)
    except Exception as e:
        print(f"❌ Failed to initialize middleware: {e}")
        return False
    
    # Test cases: (query, expected_chunks)
    # Note: A test passes if ALL expected chunks are found (may have extras)
    test_cases = [
        # Slack communication - exact trigger
        ("[SLACK CONVERSATION] What's the status of the Wilson case?", ["slack_communication"]),
        
        # Calendar management - explicit calendar/deadline keywords
        ("What's on the calendar for next week?", ["calendar_management"]),
        ("Add a deadline for discovery responses", ["calendar_management"]),
        ("Schedule a reminder for the deposition date", ["calendar_management"]),
        
        # Notes recording - explicit note/log keywords
        ("Record a note about the client meeting", ["notes_recording"]),
        ("Log activity for the case", ["notes_recording"]),
        ("Add a case note about what we discussed", ["notes_recording"]),
        
        # Directory organization - explicit folder/organize keywords
        ("Where should I save this file in the folder?", ["directory_organization"]),
        ("Organize files in the case folder structure", ["directory_organization"]),
        ("What's the 8-bucket system?", ["directory_organization"]),
        
        # Memory management - explicit remember/preference keywords
        ("Remember this preference for me", ["memory_management"]),
        ("Save this as my preference please", ["memory_management"]),
        ("Always do this workflow", ["memory_management"]),
        
        # UI dashboard rules - explicit dashboard/card keywords
        ("Show me a dashboard for the case", ["ui_dashboard_rules"]),
        ("Display the case card", ["ui_dashboard_rules"]),
        ("Render the UI for this case", ["ui_dashboard_rules"]),
        
        # No chunks expected (generic queries)
        ("What's the weather today?", []),
        ("Hello, how are you?", []),
    ]
    
    print("=" * 80)
    print("CONTEXT CHUNK INJECTION TEST")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for query, expected in test_cases:
        detected = middleware._detect_context_chunks(query)
        detected_names = [c['name'] for c in detected]
        
        # Check if expected chunks are in detected (order doesn't matter, may have extras)
        all_expected_found = all(exp in detected_names for exp in expected)
        
        if all_expected_found and (len(expected) == 0 or len(detected) > 0):
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{status}: \"{query[:50]}...\"" if len(query) > 50 else f"{status}: \"{query}\"")
        print(f"   Expected: {expected}")
        print(f"   Detected: {detected_names}")
        if detected:
            for chunk in detected:
                print(f"      - {chunk['name']}: {chunk['match_type']} (score: {chunk['match_score']:.2f})")
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


def test_chunk_content_loading():
    """Test that chunk content is properly loaded."""
    
    workspace_dir = "/Volumes/X10 Pro/Roscoe/workspace_paralegal"
    
    try:
        middleware = CaseContextMiddleware(workspace_dir=workspace_dir)
    except Exception as e:
        print(f"❌ Failed to initialize middleware: {e}")
        return False
    
    print()
    print("=" * 80)
    print("CHUNK CONTENT LOADING TEST")
    print("=" * 80)
    print()
    
    chunks = middleware.chunks_manifest.get('chunks', [])
    all_loaded = True
    
    for chunk in chunks:
        content = middleware._load_chunk_content(chunk['file'])
        if content:
            print(f"✅ {chunk['name']}: Loaded {len(content)} chars from {chunk['file']}")
        else:
            print(f"❌ {chunk['name']}: Failed to load {chunk['file']}")
            all_loaded = False
    
    print()
    return all_loaded


def test_formatted_injection():
    """Test the formatted output for injection."""
    
    workspace_dir = "/Volumes/X10 Pro/Roscoe/workspace_paralegal"
    
    try:
        middleware = CaseContextMiddleware(workspace_dir=workspace_dir)
    except Exception as e:
        print(f"❌ Failed to initialize middleware: {e}")
        return False
    
    print()
    print("=" * 80)
    print("FORMATTED INJECTION TEST")
    print("=" * 80)
    print()
    
    # Test with a query that should match calendar
    query = "What deadlines are coming up on the calendar?"
    chunks = middleware._detect_context_chunks(query)
    formatted = middleware._format_chunks_for_injection(chunks)
    
    print(f"Query: \"{query}\"")
    print(f"Matched chunks: {[c['name'] for c in chunks]}")
    print()
    print("Formatted output preview (first 500 chars):")
    print("-" * 40)
    print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
    print("-" * 40)
    
    return len(formatted) > 0


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING CONTEXT CHUNK INJECTION TESTS")
    print("=" * 80 + "\n")
    
    results = []
    
    results.append(("Chunk Detection", test_chunk_detection()))
    results.append(("Content Loading", test_chunk_content_loading()))
    results.append(("Formatted Injection", test_formatted_injection()))
    
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    sys.exit(0 if all_passed else 1)

