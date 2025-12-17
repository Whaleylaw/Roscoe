#!/usr/bin/env python3
"""
Test 6: Playwright Browser Automation
Verifies that Playwright-enabled scripts can launch browser and interact with pages.

IMPORTANT: Run this with execute_python_script_with_browser() not execute_python_script()
"""

import sys
import os
from pathlib import Path

print("=" * 50)
print("Test: Playwright Browser Automation")
print("=" * 50)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("✗ Playwright not installed")
    print("This test requires the Playwright Docker image")
    sys.exit(1)

# Test browser launch and page navigation
print("Launching Chromium browser...")

with sync_playwright() as p:
    # Launch browser (headless)
    browser = p.chromium.launch(headless=True)
    print("✓ Browser launched")
    
    # Create page
    page = browser.new_page()
    print("✓ Page created")
    
    # Navigate to a test page
    print("Navigating to example.com...")
    page.goto("https://example.com")
    print(f"✓ Page loaded: {page.title()}")
    
    # Extract some content
    heading = page.locator("h1").first.text_content()
    print(f"✓ Page heading: {heading}")
    
    # Take a screenshot if output directory exists
    output_dir = Path("/workspace/Reports/test_outputs")
    if output_dir.exists():
        screenshot_path = output_dir / "playwright_test_screenshot.png"
        page.screenshot(path=str(screenshot_path))
        print(f"✓ Screenshot saved: {screenshot_path}")
    
    # Close browser
    browser.close()
    print("✓ Browser closed")

print("\n✓ Playwright test passed!")

