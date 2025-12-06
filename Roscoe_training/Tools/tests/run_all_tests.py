#!/usr/bin/env python3
"""
Script Execution Test Runner

Run all tests for the Docker-based script execution system.
This script is meant to be run from the VM after Docker images are built.

Usage:
    python /workspace/Tools/tests/run_all_tests.py [--skip-playwright] [--skip-error]
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Tests directory
TESTS_DIR = Path(__file__).parent

# Test definitions: (script_name, description, requires_playwright, expects_failure)
TESTS = [
    ("test_basic.py", "Basic script execution", False, False),
    ("test_dependencies.py", "Dependencies check", False, False),
    ("test_file_persistence.py", "File persistence to GCS", False, False),
    ("test_arguments.py", "Argument passing", False, False),
    ("test_internet.py", "Internet access", False, False),
    ("test_error_handling.py", "Error handling (expects failure)", False, True),
    ("test_playwright.py", "Playwright browser automation", True, False),
]


def run_test_direct(script_path: Path, expects_failure: bool = False) -> tuple[bool, str]:
    """Run a test script directly (for local testing without Docker)."""
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(script_path.parent),
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n\nSTDERR:\n{result.stderr}"
        
        # For error handling test, non-zero exit is expected
        if expects_failure:
            success = result.returncode != 0
        else:
            success = result.returncode == 0
            
        return success, output
        
    except subprocess.TimeoutExpired:
        return False, "Test timed out after 60 seconds"
    except Exception as e:
        return False, f"Failed to run test: {e}"


def main():
    parser = argparse.ArgumentParser(description="Run script execution tests")
    parser.add_argument("--skip-playwright", action="store_true",
                        help="Skip Playwright tests (requires special image)")
    parser.add_argument("--skip-error", action="store_true",
                        help="Skip error handling test")
    parser.add_argument("--direct", action="store_true",
                        help="Run tests directly (not via Docker executor)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Script Execution Test Suite")
    print(f"Started: {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    results = []
    
    for script_name, description, requires_playwright, expects_failure in TESTS:
        # Skip conditions
        if requires_playwright and args.skip_playwright:
            print(f"\n⏭️  SKIP: {description} (--skip-playwright)")
            results.append(("SKIP", description))
            continue
            
        if expects_failure and args.skip_error:
            print(f"\n⏭️  SKIP: {description} (--skip-error)")
            results.append(("SKIP", description))
            continue
        
        print(f"\n{'='*60}")
        print(f"TEST: {description}")
        print(f"Script: {script_name}")
        print("=" * 60)
        
        script_path = TESTS_DIR / script_name
        
        if args.direct:
            success, output = run_test_direct(script_path, expects_failure)
        else:
            # When running via Docker executor, import and use the executor
            try:
                from roscoe.agents.paralegal.script_executor import (
                    execute_python_script,
                    format_execution_result,
                )
                
                result = execute_python_script(
                    script_path=f"/Tools/tests/{script_name}",
                    enable_playwright=requires_playwright,
                    timeout=120 if requires_playwright else 60,
                )
                
                output = format_execution_result(result)
                
                if expects_failure:
                    success = not result['success']
                else:
                    success = result['success']
                    
            except ImportError:
                # Fall back to direct execution
                print("Note: Docker executor not available, running directly")
                success, output = run_test_direct(script_path, expects_failure)
        
        print(output)
        
        if success:
            status = "PASS"
            print(f"\n✅ {description}: PASSED")
        else:
            status = "FAIL"
            print(f"\n❌ {description}: FAILED")
            
        results.append((status, description))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for s, _ in results if s == "PASS")
    failed = sum(1 for s, _ in results if s == "FAIL")
    skipped = sum(1 for s, _ in results if s == "SKIP")
    
    for status, description in results:
        emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}[status]
        print(f"  {emoji} {description}: {status}")
    
    print()
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    
    if failed > 0:
        print("\n⚠️  Some tests failed!")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

