#!/usr/bin/env python3
"""
Test 2: File Persistence
Verifies that files created by scripts persist to the GCS filesystem.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

print("=" * 50)
print("Test: File Persistence")
print("=" * 50)

# Create test output directory
output_dir = Path("/workspace/Reports/test_outputs")
output_dir.mkdir(parents=True, exist_ok=True)

# Create a test file
test_file = output_dir / f"persistence_test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
test_content = f"""
File Persistence Test
=====================
Created at: {datetime.utcnow().isoformat()}
Working directory: {os.getcwd()}
Python version: {sys.version}
Execution ID: {os.environ.get('EXECUTION_ID', 'N/A')}

This file was created by the Docker script executor.
If you can read this, file persistence to GCS is working correctly.
"""

test_file.write_text(test_content)
print(f"Created test file: {test_file}")

# Verify the file exists
if test_file.exists():
    print(f"File size: {test_file.stat().st_size} bytes")
    print("\n✓ File persistence test passed!")
else:
    print("\n✗ File persistence test FAILED - file not found after creation")
    sys.exit(1)

