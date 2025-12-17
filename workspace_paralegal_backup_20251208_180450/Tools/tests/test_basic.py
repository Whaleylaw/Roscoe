#!/usr/bin/env python3
"""
Test 1: Basic Execution
Verifies that simple script execution works and stdout is captured.
"""

import sys
import os

print("=" * 50)
print("Test: Basic Script Execution")
print("=" * 50)

print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Script path: {__file__}")

# Print environment context
if os.environ.get("EXECUTION_ID"):
    print(f"Execution ID: {os.environ['EXECUTION_ID']}")
if os.environ.get("CASE_NAME"):
    print(f"Case Name: {os.environ['CASE_NAME']}")

print("\n✓ Basic execution test passed!")

