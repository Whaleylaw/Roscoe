#!/usr/bin/env python3
"""
Scrape Kentucky Medical License database by:
1. Searching for each county
2. Finding the 'format for printing' link
3. Extracting doctor data from the print page
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import sys
import re

# Output paths
OUTPUT_DIR = "/Volumes/X10 Pro/Roscoe/scripts/output"
CSV_PATH = f"{OUTPUT_DIR}/ky_doctors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
JSON_PATH = f"{OUTPUT_DIR}/ky_doctors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
METADATA_PATH = f"{OUTPUT_DIR}/ky_doctors_metadata.json"

# All Kentucky counties
KENTUCKY_COUNTIES = [
    "Adair", "Allen", "Anderson", "Ballard", "Barren", "Bath", "Bell", "Boone",
    "Bourbon", "Boyd", "Boyle", "Bracken", "Breathitt", "Breckinridge", "Bullitt",
    "Butler", "Caldwell", "Calloway", "Campbell", "Carlisle", "Carroll", "Carter",
    "Casey", "Christian", "Clark", "Clay", "Clinton", "Crittenden", "Cumberland",
    "Daviess", "Edmonson", "Elliott", "Estill", "Fayette", "Fleming", "Floyd",
    "Franklin", "Fulton", "Gallatin", "Garrard", "Grant", "Graves", "Grayson",
    "Green", "Greenup", "Hancock", "Hardin", "Harlan", "Harrison", "Hart",
    "Henderson", "Henry", "Hickman", "Hopkins", "Jackson", "Jefferson", "Jessamine",
    "Johnson", "Kenton", "Knott", "Knox", "Larue", "Laurel", "Lawrence", "Lee",
    "Leslie", "Letcher", "Lewis", "Lincoln", "Livingston", "Logan", "Lyon",
    "Madison", "Magoffin", "Marion", "Marshall", "Martin", "Mason", "McCracken",
    "McCreary", "McLean", "Meade", "Menifee", "Mercer", "Metcalfe", "Monroe",
    "Montgomery", "Morgan", "Muhlenberg", "Nelson", "Nicholas", "Ohio", "Oldham",
    "Owen", "Owsley", "Pendleton", "Perry", "Pike", "Powell", "Pulaski",
    "Robertson", "Rockcastle", "Rowan", "Russell", "Scott", "Shelby", "Simpson",
    "Spencer", "Taylor", "Todd", "Trigg", "Trimble", "Union", "Warren",
    "Washington", "Wayne", "Webster", "Whitley", "Wolfe", "Woodford"
]


def parse_results_table(html_content, county_name):
    """Parse the results table from the search results or print page."""
    soup = BeautifulSoup(html_content, 'html.parser')

    doctors = []

    # Look for all tables
    tables = soup.find_all('table')

    for table in tables:
        # Try to find doctor records in the table
        rows = table.find_all('tr')

        for row in rows:
            cells = row.find_all(['td', 'th'])

            if len(cells) >= 3:  # Expect multiple columns of data
                cell_texts = [cell.get_text(strip=True) for cell in cells]

                # Skip header rows
                if 'License' in cell_texts[0] or 'Name' in cell_texts[0]:
                    continue

                # Create doctor record (structure will depend on actual HTML)
                # This is a placeholder that will need adjustment based on actual data
                doctor = {
                    'County': county_name,
                    'Raw_Data': ' | '.join(cell_texts)
                }
                doctors.append(doctor)

    return doctors


async def scrape_county_via_search(county_name, page):
    """Scrape doctors for a county by searching and using print page."""
    print(f"Scraping {county_name} County...")

    try:
        # Navigate to search page
        await page.goto("https://web1.ky.gov/GenSearch/LicenseSearch.aspx?AGY=5",
                        wait_until="networkidle")

        # Select county
        await page.select_option('select[name="usLicenseSearch$ddlField3"]', value=county_name)

        # Click search
        await page.click('input[type="submit"][value="Search"]')

        # Wait for results
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        # Look for print/format link
        print_link = None

        # Try to find a link with "print" or "format" in the text
        links = await page.locator('a').all()
        for link in links:
            text = await link.inner_text()
            if 'print' in text.lower() or 'format' in text.lower():
                print_link = link
                print(f"  Found print link: {text}")
                break

        if print_link:
            # Click the print link
            await print_link.click()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)

        # Get the page content (either results page or print page)
        html = await page.content()

        # Save for debugging
        debug_path = f"{OUTPUT_DIR}/debug_{county_name}.html"
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # Parse the results
        doctors = parse_results_table(html, county_name)

        print(f"  Found {len(doctors)} records in {county_name}")
        return doctors

    except Exception as e:
        print(f"  ERROR scraping {county_name}: {e}")
        import traceback
        traceback.print_exc()
        return []


async def scrape_all_counties():
    """Scrape all Kentucky counties."""

    all_doctors = []

    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Test with first few counties
            test_counties = KENTUCKY_COUNTIES[:3]

            for i, county in enumerate(test_counties, 1):
                print(f"\n[{i}/{len(test_counties)}] {county} County")
                doctors = await scrape_county_via_search(county, page)
                all_doctors.extend(doctors)

                # Delay between requests
                await asyncio.sleep(2)

            print(f"\n✅ Total records collected: {len(all_doctors)}")

        finally:
            await browser.close()

    return all_doctors


def save_to_files(doctors):
    """Save doctors to CSV and JSON."""
    import os

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Create DataFrame
    df = pd.DataFrame(doctors)

    if len(df) == 0:
        print("No data to save!")
        return df

    print("\nCleaning data...")

    # Remove duplicates
    original_count = len(df)
    df = df.drop_duplicates()
    print(f"  Removed {original_count - len(df)} duplicate records")

    # Save to CSV
    print(f"\nSaving to CSV: {CSV_PATH}")
    df.to_csv(CSV_PATH, index=False, encoding='utf-8')
    print(f"✅ Saved {len(df)} records to CSV")

    # Save to JSON
    print(f"\nSaving to JSON: {JSON_PATH}")
    records_list = df.to_dict(orient='records')
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(records_list, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(records_list)} records to JSON")

    return df


async def main():
    """Main entry point."""
    print("Kentucky Medical License Database Scraper")
    print("=" * 80)

    try:
        # Scrape counties
        doctors = await scrape_all_counties()

        if not doctors:
            print("❌ No doctors collected!")
            sys.exit(1)

        # Save to files
        df = save_to_files(doctors)

        print("\n✅ Scraping complete!")
        print(f"Output CSV: {CSV_PATH}")
        print(f"Output JSON: {JSON_PATH}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
