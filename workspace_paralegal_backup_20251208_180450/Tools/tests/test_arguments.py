#!/usr/bin/env python3
"""
Test 3: Script Arguments
Verifies that command-line arguments are passed correctly to scripts.
"""

import sys
import argparse

print("=" * 50)
print("Test: Script Arguments")
print("=" * 50)

# Parse arguments
parser = argparse.ArgumentParser(description="Test argument passing")
parser.add_argument("--format", choices=["json", "text", "markdown"], default="text",
                    help="Output format")
parser.add_argument("--output", type=str, help="Output file path")
parser.add_argument("--verbose", action="store_true", help="Verbose output")
parser.add_argument("positional", nargs="*", help="Positional arguments")

args = parser.parse_args()

print(f"Raw sys.argv: {sys.argv}")
print(f"\nParsed arguments:")
print(f"  --format: {args.format}")
print(f"  --output: {args.output}")
print(f"  --verbose: {args.verbose}")
print(f"  positional: {args.positional}")

# Verify expected arguments
if args.format and args.output:
    print("\n✓ Arguments test passed!")
else:
    print("\nNote: Run with arguments to fully test, e.g.:")
    print("  --format json --output /workspace/Reports/test.json --verbose arg1 arg2")
    print("\n✓ Basic argument parsing works!")

