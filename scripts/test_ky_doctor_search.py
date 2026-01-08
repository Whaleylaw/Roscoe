#!/usr/bin/env python3
"""
Test script to explore the Kentucky Medical License database.
Test searching by county and understand the results format.
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_county_search():
    """Test searching for doctors in one county."""

    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=False)  # Keep visible for debugging
        page = await browser.new_page()

        try:
            # Navigate to search page
            print("Navigating to Kentucky Medical License search...")
            await page.goto("https://web1.ky.gov/GenSearch/LicenseSearch.aspx?AGY=5")
            await page.wait_for_load_state("networkidle")

            # Save initial page HTML to find field names
            initial_html = await page.content()
            with open("/Volumes/X10 Pro/Roscoe/scripts/output/ky_doctor_search_form.html", 'w') as f:
                f.write(initial_html)
            print("Saved initial form HTML for inspection")

            # Get all select elements
            selects = await page.locator('select').all()
            print(f"\nFound {len(selects)} select elements:")
            for i, select in enumerate(selects):
                name = await select.get_attribute('name')
                id = await select.get_attribute('id')
                print(f"  {i+1}. name='{name}' id='{id}'")

            # Select a county (Fayette - Lexington, should have many doctors)
            print("\nSelecting Fayette County...")
            await page.select_option('select[name="usLicenseSearch$ddlField3"]', value="Fayette")
            print("Selected Fayette")

            # Click search button
            print("Clicking Search...")
            await page.click('input[type="submit"][value="Search"]')

            # Wait for results
            await page.wait_for_load_state("networkidle")
            time.sleep(2)  # Extra wait for page to fully load

            # Take a screenshot to see what we got
            screenshot_path = "/Volumes/X10 Pro/Roscoe/scripts/output/ky_doctor_search_results.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved: {screenshot_path}")

            # Get the page content
            content = await page.content()

            # Save HTML for inspection
            html_path = "/Volumes/X10 Pro/Roscoe/scripts/output/ky_doctor_search_results.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"HTML saved: {html_path}")

            # Look for "format for printing" or print link
            print("\nLooking for print/format options...")
            print_links = await page.locator('a:has-text("print")').count()
            format_links = await page.locator('a:has-text("format")').count()

            print(f"Found {print_links} links with 'print'")
            print(f"Found {format_links} links with 'format'")

            # Get all links on the page
            all_links = await page.locator('a').all()
            print(f"\nAll links on results page ({len(all_links)} total):")
            for i, link in enumerate(all_links[:20]):  # First 20 links
                text = await link.inner_text()
                href = await link.get_attribute('href')
                if text.strip():
                    print(f"  {i+1}. {text.strip()[:50]} -> {href[:80] if href else 'No href'}")

            # Check if there's a table or grid of results
            tables = await page.locator('table').count()
            print(f"\nFound {tables} tables on the page")

            if tables > 0:
                # Get first table data
                print("\nExtracting data from first table...")
                first_table = page.locator('table').first
                rows = await first_table.locator('tr').count()
                print(f"Table has {rows} rows")

                # Get first few rows
                for i in range(min(5, rows)):
                    row = first_table.locator('tr').nth(i)
                    cells = await row.locator('td, th').all()
                    row_data = []
                    for cell in cells:
                        text = await cell.inner_text()
                        row_data.append(text.strip()[:40])
                    print(f"  Row {i}: {' | '.join(row_data)}")

            # Keep browser open for manual inspection
            print("\nBrowser will stay open for 10 seconds for manual inspection...")
            await asyncio.sleep(10)

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_county_search())
