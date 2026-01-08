#!/usr/bin/env python3
"""
Scrape Kentucky Medical License database.

The scraper:
1. Searches for each county
2. Clicks "Format for Print" button
3. Extracts doctor data from the print page
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
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
CSV_PATH = f"{OUTPUT_DIR}/ky_doctors_{timestamp}.csv"
JSON_PATH = f"{OUTPUT_DIR}/ky_doctors_{timestamp}.json"
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


def parse_doctor_records(html_content, county_name):
    """Parse doctor records from the HTML page."""
    soup = BeautifulSoup(html_content, 'html.parser')

    doctors = []
    current_doctor = {}

    # Find all rows with the pattern: <div class="row">
    rows = soup.find_all('div', class_='row')

    for row in rows:
        # Get the label and value columns
        label_div = row.find('div', class_='cols2-col1')
        value_div = row.find('div', class_='cols2-col2')

        if not label_div or not value_div:
            continue

        label = label_div.get_text(strip=True).replace(':', '').replace('\xa0', '').strip()
        value = value_div.get_text(separator=' ', strip=True).replace('\xa0', ' ').strip()

        # Skip empty rows (separator between doctors)
        if not label or label == '':
            if current_doctor:
                # Add county
                current_doctor['County'] = county_name
                doctors.append(current_doctor)
                current_doctor = {}
            continue

        # Add field to current doctor
        current_doctor[label] = value

    # Add last doctor
    if current_doctor:
        current_doctor['County'] = county_name
        doctors.append(current_doctor)

    return doctors


async def scrape_county(county_name, page):
    """Scrape all doctors for a single county."""
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

        # Click "Format for Print" button
        try:
            await page.click('input[name="usLicenseList$btnPrint"]')
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)
            print(f"  Clicked 'Format for Print'")
        except:
            print(f"  Could not find 'Format for Print' button, using results page")

        # Get the page content
        html = await page.content()

        # Parse doctors
        doctors = parse_doctor_records(html, county_name)

        print(f"  Found {len(doctors)} doctors in {county_name}")
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
            for i, county in enumerate(KENTUCKY_COUNTIES, 1):
                print(f"\n[{i}/{len(KENTUCKY_COUNTIES)}] {county} County")
                doctors = await scrape_county(county, page)
                all_doctors.extend(doctors)

                # Delay between requests
                await asyncio.sleep(2)

            print(f"\n✅ Total doctors collected: {len(all_doctors)}")

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

    # Remove duplicates based on License number
    if 'License' in df.columns:
        original_count = len(df)
        df = df.drop_duplicates(subset=['License'])
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

    # Save metadata
    metadata = {
        "scrape_timestamp": datetime.now().isoformat(),
        "source_url": "https://web1.ky.gov/GenSearch/LicenseSearch.aspx?AGY=5",
        "total_records": len(df),
        "total_counties": len(KENTUCKY_COUNTIES),
        "output_files": {
            "csv": CSV_PATH,
            "json": JSON_PATH
        },
        "columns": list(df.columns),
        "counties_scraped": KENTUCKY_COUNTIES
    }

    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Saved metadata to {METADATA_PATH}")

    # Print summary
    print("\n" + "=" * 80)
    print("SCRAPING SUMMARY")
    print("=" * 80)
    print(f"Total doctors: {len(df)}")
    print(f"Columns: {', '.join(df.columns)}")
    print(f"Counties scraped: {len(KENTUCKY_COUNTIES)}")

    # Show sample record
    if len(df) > 0:
        print("\nSample record:")
        print(df.iloc[0].to_dict())

    return df


async def main():
    """Main entry point."""
    print("Kentucky Medical License Database Scraper")
    print("=" * 80)

    try:
        # Scrape all counties
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
