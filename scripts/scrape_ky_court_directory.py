#!/usr/bin/env python3
"""
Scrape Kentucky Court Directory using Playwright browser automation.

This script navigates to https://kcoj.kycourts.net/ContactList/Search and extracts
all 993+ contact records into a CSV file.
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import json
from datetime import datetime
import sys

# Output paths
OUTPUT_DIR = "/Volumes/X10 Pro/Roscoe/scripts/output"
CSV_PATH = f"{OUTPUT_DIR}/ky_court_directory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
METADATA_PATH = f"{OUTPUT_DIR}/ky_court_directory_metadata.json"

async def scrape_court_directory():
    """Main scraping function."""

    all_records = []

    async with async_playwright() as p:
        # Launch browser
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Navigate to the search page
            print("Navigating to Kentucky Court Directory...")
            await page.goto("https://kcoj.kycourts.net/ContactList/Search", wait_until="networkidle")

            # Wait for the page to load
            await page.wait_for_selector("#addressList", timeout=10000)
            print("Page loaded successfully")

            # Change page size to 100 entries (maximum)
            print("Setting page size to 100 entries...")
            await page.select_option('select[name="addressList_length"]', value="100")

            # Wait for table to update
            await page.wait_for_timeout(2000)

            # Get total number of entries
            pagination_text = await page.locator('.dataTables_info').inner_text()
            print(f"Pagination info: {pagination_text}")

            # Extract total entries (e.g., "Showing 1 to 100 of 993 entries")
            import re
            match = re.search(r'of (\d+) entries', pagination_text)
            total_entries = int(match.group(1)) if match else 0
            total_pages = (total_entries + 99) // 100  # Round up

            print(f"Total entries: {total_entries}")
            print(f"Total pages: {total_pages}")

            # Loop through all pages
            for page_num in range(1, total_pages + 1):
                print(f"\nScraping page {page_num}/{total_pages}...")

                # Wait for table to be visible
                await page.wait_for_selector("#addressList tbody tr", timeout=5000)

                # Extract table data
                rows = await page.locator("#addressList tbody tr").all()

                for row in rows:
                    cells = await row.locator("td").all()
                    if len(cells) >= 6:
                        record = {
                            "Name": await cells[0].inner_text(),
                            "Address": await cells[1].inner_text(),
                            "County": await cells[2].inner_text(),
                            "Phone_Number": await cells[3].inner_text(),
                            "Area": await cells[4].inner_text(),
                            "Category": await cells[5].inner_text()
                        }
                        all_records.append(record)

                print(f"  Extracted {len(rows)} records from page {page_num}")

                # Click "Next" button if not on last page
                if page_num < total_pages:
                    next_button = page.locator('.paginate_button.next:not(.disabled)')
                    if await next_button.count() > 0:
                        await next_button.click()
                        await page.wait_for_timeout(2000)  # Wait for page to load
                    else:
                        print("  No more pages (Next button disabled)")
                        break

            print(f"\n✅ Total records collected: {len(all_records)}")

        finally:
            await browser.close()

    return all_records


def save_to_csv(records):
    """Save records to CSV."""
    import os

    # Create output directory if needed
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Create DataFrame
    df = pd.DataFrame(records)

    # Clean up the data
    print("\nCleaning data...")

    # Remove duplicates
    original_count = len(df)
    df = df.drop_duplicates()
    print(f"  Removed {original_count - len(df)} duplicate records")

    # Save to CSV
    print(f"\nSaving to CSV: {CSV_PATH}")
    df.to_csv(CSV_PATH, index=False, encoding='utf-8')
    print(f"✅ Saved {len(df)} records to CSV")

    # Save metadata
    metadata = {
        "scrape_timestamp": datetime.now().isoformat(),
        "source_url": "https://kcoj.kycourts.net/ContactList/Search",
        "total_records": len(df),
        "output_file": CSV_PATH,
        "columns": list(df.columns),
        "categories": df['Category'].unique().tolist() if 'Category' in df.columns else [],
        "counties": df['County'].unique().tolist() if 'County' in df.columns else []
    }

    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Saved metadata to {METADATA_PATH}")

    # Print summary
    print("\n" + "=" * 80)
    print("SCRAPING SUMMARY")
    print("=" * 80)
    print(f"Total records: {len(df)}")
    print(f"Columns: {', '.join(df.columns)}")
    print(f"\nCategories ({len(metadata['categories'])}):")
    for cat in sorted(metadata['categories']):
        print(f"  - {cat}")
    print(f"\nCounties ({len(metadata['counties'])}):")
    for county in sorted(metadata['counties']):
        count = len(df[df['County'] == county])
        print(f"  - {county}: {count} records")

    return df


async def main():
    """Main entry point."""
    print("Kentucky Court Directory Scraper")
    print("=" * 80)

    try:
        # Scrape the data
        records = await scrape_court_directory()

        if not records:
            print("❌ No records collected!")
            sys.exit(1)

        # Save to CSV
        df = save_to_csv(records)

        print("\n✅ Scraping complete!")
        print(f"Output: {CSV_PATH}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
