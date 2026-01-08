#!/usr/bin/env python3
"""
Scrape Kentucky Medical License database using direct print page URLs.

URL Pattern: https://web1.ky.gov/GenSearch/PrintPage.aspx?AGY=5&FLD1=&FLD2=&FLD3={COUNTY}&FLD4=0&TYPE=
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
from datetime import datetime
import sys

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


def parse_doctor_table(html_content):
    """Parse the HTML table containing doctor information."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the main table (usually the first significant table)
    table = soup.find('table')
    if not table:
        return []

    records = []

    # The table structure seems to have multiple rows per doctor
    # Let's extract all table data and try to parse it
    rows = table.find_all('tr')

    current_doctor = None
    for row in rows:
        cells = row.find_all(['td', 'th'])

        # Skip empty rows
        if not cells:
            continue

        # Get cell texts
        cell_texts = [cell.get_text(strip=True) for cell in cells]

        # If we see a bold header or label, it might be a field name
        # This will require inspection of actual HTML to refine
        if len(cell_texts) >= 2:
            # Likely a key-value pair
            key = cell_texts[0]
            value = ' '.join(cell_texts[1:])

            # Initialize new doctor record if we see "License Number" or "Last Name"
            if 'License' in key or (current_doctor is None and key):
                if current_doctor:
                    records.append(current_doctor)
                current_doctor = {}

            if current_doctor is not None:
                current_doctor[key] = value

    # Add last doctor
    if current_doctor:
        records.append(current_doctor)

    return records


async def scrape_county(county_name, page):
    """Scrape all doctors for a single county."""
    print(f"Scraping {county_name} County...")

    url = f"https://web1.ky.gov/GenSearch/PrintPage.aspx?AGY=5&FLD1=&FLD2=&FLD3={county_name}&FLD4=0&TYPE="

    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)

        # Get the page content
        html = await page.content()

        # Parse the table
        doctors = parse_doctor_table(html)

        # Add county to each record
        for doctor in doctors:
            doctor['County'] = county_name

        print(f"  Found {len(doctors)} doctors in {county_name}")
        return doctors

    except Exception as e:
        print(f"  ERROR scraping {county_name}: {e}")
        return []


async def scrape_all_counties():
    """Scrape all Kentucky counties."""

    all_doctors = []

    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Scrape each county
            for i, county in enumerate(KENTUCKY_COUNTIES, 1):
                print(f"\n[{i}/{len(KENTUCKY_COUNTIES)}] {county} County")
                doctors = await scrape_county(county, page)
                all_doctors.extend(doctors)

                # Small delay to be respectful
                await asyncio.sleep(1)

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

    # Save metadata
    metadata = {
        "scrape_timestamp": datetime.now().isoformat(),
        "source_url_pattern": "https://web1.ky.gov/GenSearch/PrintPage.aspx?AGY=5&FLD1=&FLD2=&FLD3={COUNTY}&FLD4=0&TYPE=",
        "total_records": len(df),
        "total_counties": len(KENTUCKY_COUNTIES),
        "output_files": {
            "csv": CSV_PATH,
            "json": JSON_PATH
        },
        "columns": list(df.columns)
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
