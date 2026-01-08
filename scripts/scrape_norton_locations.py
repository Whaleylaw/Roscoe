#!/usr/bin/env python3
"""
Scrape all Norton Healthcare locations from https://nortonhealthcare.com/locations/
Extracts name, address, and phone number for all 368+ locations.
"""

import json
import re
import time
from playwright.sync_api import sync_playwright

def extract_location_data(location_card):
    """Extract name, address, and phone from a location card."""
    try:
        # Get the full text content
        text = location_card.inner_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Parse the structure:
        # Line 0: Name
        # Line 1: Type (e.g., "Specialist Practice", "Hospital")
        # Line 2: Address
        # Line 3: Phone
        # Lines 4+: "Show on Map", "Directions", "Details"

        name = lines[0] if len(lines) > 0 else ""
        address = lines[2] if len(lines) > 2 else ""
        phone = lines[3] if len(lines) > 3 else ""

        # Clean up phone number if it doesn't match expected format
        if not re.match(r'\(\d{3}\)\s*\d{3}-\d{4}', phone):
            phone = ""

        return {
            "name": name,
            "address": address,
            "phone": phone
        }
    except Exception as e:
        print(f"Error extracting location: {e}")
        return None

def scrape_norton_locations():
    """Scrape all Norton Healthcare locations."""
    locations = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Loading Norton Healthcare locations page...")
        page.goto('https://nortonhealthcare.com/locations/', wait_until='networkidle')

        print("Waiting for locations to load...")
        time.sleep(8)  # Wait for JavaScript to load all locations

        print("Finding all location cards...")

        # Wait for location cards to be present
        page.wait_for_selector('.location-card', timeout=15000)

        # Get all location cards
        location_cards = page.locator('.location-card').all()
        total_cards = len(location_cards)

        print(f"Found {total_cards} location cards")
        print("Extracting data...")

        # Extract data from each card
        seen_names = set()  # To avoid duplicates
        for i, card in enumerate(location_cards, 1):
            try:
                location_data = extract_location_data(card)
                if location_data and location_data['name']:
                    # Skip if we've seen this name+address combo before
                    identifier = f"{location_data['name']}|{location_data['address']}"
                    if identifier not in seen_names:
                        locations.append(location_data)
                        seen_names.add(identifier)

                        if i % 25 == 0:
                            print(f"  Processed {i}/{total_cards} locations...")
            except Exception as e:
                print(f"  Error processing location {i}: {e}")

        print(f"  Processed {total_cards}/{total_cards} locations...")
        browser.close()

    return locations

if __name__ == "__main__":
    print("Starting Norton Healthcare locations scrape...")
    print("=" * 60)

    locations = scrape_norton_locations()

    print("\n" + "=" * 60)
    print(f"Total locations scraped: {len(locations)}")

    # Save to JSON file
    output_file = "/Volumes/X10 Pro/Roscoe/json-files/norton_healthcare_locations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to: {output_file}")

    # Print first few examples
    if locations:
        print("\nFirst 5 locations:")
        for i, loc in enumerate(locations[:5], 1):
            print(f"\n{i}. {loc['name']}")
            print(f"   Address: {loc['address']}")
            print(f"   Phone: {loc['phone']}")
