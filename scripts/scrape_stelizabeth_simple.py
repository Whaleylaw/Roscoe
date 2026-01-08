#!/usr/bin/env python3
"""
Scrape all St. Elizabeth Healthcare locations - Simple version.
All locations appear to be loaded on the page at once.
"""

import json
import re
import time
from playwright.sync_api import sync_playwright

def scrape_stelizabeth_locations():
    """Scrape all St. Elizabeth Healthcare locations."""
    locations = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Loading St. Elizabeth locations page...")
        page.goto('https://www.stelizabeth.com/care/find-a-location/results/', wait_until='domcontentloaded')

        print("Waiting for all locations to load...")
        time.sleep(10)  # Give extra time for AJAX to load all locations

        # Wait for location details links
        page.wait_for_selector('a:text("Location Details")', timeout=15000)

        # Get all "Location Details" links
        detail_links = page.locator('a:text("Location Details")').all()
        total_links = len(detail_links)

        print(f"Found {total_links} location cards")
        print("Extracting data...\n")

        for i, link in enumerate(detail_links, 1):
            try:
                # Go up 2 levels to get the card container
                # Based on the sample, parent2 has the clean data
                card = link.locator('..').locator('..')

                text = card.inner_text(timeout=2000)
                lines = [l.strip() for l in text.split('\n') if l.strip()]

                # Extract name (first line)
                name = lines[0] if lines else ""

                # Extract street (starts with digit)
                street = ""
                for line in lines:
                    if re.match(r'^\d+', line):
                        street = line
                        break

                # Extract city/state/zip
                city_state_zip = ""
                for line in lines:
                    if re.search(r'^[A-Z][a-z]+,\s*[A-Z]{2}\s+\d{5}', line):
                        city_state_zip = line
                        break

                # Extract phone
                phone = ""
                for line in lines:
                    if line.startswith('PH:'):
                        match = re.search(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', line)
                        if match:
                            phone = match.group(0)
                        break

                # Construct address
                if street and city_state_zip:
                    address = f"{street}, {city_state_zip}"
                else:
                    address = city_state_zip or street

                # Add if valid
                if name and address:
                    key = f"{name.lower()}|{address.lower()}"
                    if key not in seen:
                        seen.add(key)
                        locations.append({
                            "name": name,
                            "address": address,
                            "phone": phone
                        })

                        if i % 50 == 0:
                            print(f"  Processed {i}/{total_links} locations...")

            except Exception as e:
                # Skip this location if extraction fails
                pass

        print(f"  Processed {total_links}/{total_links} locations")
        browser.close()

    return locations

if __name__ == "__main__":
    print("Starting St. Elizabeth Healthcare locations scrape...")
    print("=" * 60)

    locations = scrape_stelizabeth_locations()

    print("\n" + "=" * 60)
    print(f"Total unique locations: {len(locations)}")

    # Save to JSON
    output_file = "/Volumes/X10 Pro/Roscoe/json-files/stelizabeth_locations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to: {output_file}")

    # Show examples
    if locations:
        print("\nFirst 10 locations:")
        for i, loc in enumerate(locations[:10], 1):
            print(f"\n{i}. {loc['name']}")
            print(f"   Address: {loc['address']}")
            print(f"   Phone: {loc['phone']}")

    # Stats
    with_phone = sum(1 for loc in locations if loc['phone'])
    with_street = sum(1 for loc in locations if re.match(r'^\d+', loc['address']))

    print(f"\nStatistics:")
    print(f"  Total: {len(locations)}")
    print(f"  With phones: {with_phone}")
    print(f"  With street addresses: {with_street}")
