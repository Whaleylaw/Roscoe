#!/usr/bin/env python3
"""
Test 4: Error Handling
Verifies that script errors are captured in stderr and exit code.
"""

import sys
import os

print("=" * 50)
print("Test: Error Handling")
print("=" * 50)

# Print some output first
print("Starting error test...")
print("This line should appear in stdout")

# Check if we should actually raise the error
# (allows running in "safe" mode for testing)
if "--safe" in sys.argv:
    print("\n--safe flag detected, skipping intentional error")
    print("✓ Safe mode test passed!")
    sys.exit(0)

# Intentionally raise an error
print("\nAbout to raise intentional ValueError...", file=sys.stderr)
raise ValueError("This is an intentional test error to verify error handling")

