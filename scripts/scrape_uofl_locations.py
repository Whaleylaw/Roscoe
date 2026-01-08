#!/usr/bin/env python3
"""
Scrape all UofL Health locations from https://uoflhealth.org/locations/
Extracts name, address, and phone number for all 345 locations.
"""

import json
import re
import time
from playwright.sync_api import sync_playwright

def extract_location_data(location_element):
    """Extract name, address, and phone from a location card."""
    try:
        # Get the full text content
        text = location_element.inner_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # First line is the name
        name = lines[0] if lines else ""

        # Find phone number (pattern: XXX-XXX-XXXX)
        phone = ""
        for line in lines:
            if re.match(r'\d{3}-\d{3}-\d{4}', line):
                phone = line
                break

        # Address is everything between name and phone
        # Filter out the location icon text and hours if present
        address_lines = []
        for line in lines[1:]:
            # Stop at phone number
            if line == phone:
                break
            # Skip empty lines and time info
            if line and not re.match(r'\d+\s*(a\.m\.|p\.m\.)', line.lower()):
                address_lines.append(line)

        address = ", ".join(address_lines)

        return {
            "name": name,
            "address": address,
            "phone": phone
        }
    except Exception as e:
        print(f"Error extracting location: {e}")
        return None

def scrape_uofl_locations():
    """Scrape all 345 UofL Health locations."""
    locations = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Loading initial page...")
        page.goto('https://uoflhealth.org/locations/', wait_until='networkidle')
        time.sleep(3)  # Wait for JavaScript to load locations

        # Get total number of pages from pagination
        # Look for the last page number before "next" button
        total_pages = 29  # We know from the site it's 29 pages

        for page_num in range(1, total_pages + 1):
            print(f"\nScraping page {page_num} of {total_pages}...")

            # Wait for locations to load
            page.wait_for_selector('a[href*="/locations/"]', timeout=10000)
            time.sleep(2)  # Extra wait for dynamic content

            # Find all location cards
            # They are links with href containing "/locations/" in the results section
            location_cards = page.locator('div.facetwp-template a[href*="/locations/"]').all()

            print(f"Found {len(location_cards)} locations on this page")

            for i, card in enumerate(location_cards, 1):
                try:
                    location_data = extract_location_data(card)
                    if location_data and location_data['name']:
                        locations.append(location_data)
                        print(f"  {i}. {location_data['name']}")
                except Exception as e:
                    print(f"  Error processing location {i}: {e}")

            # Navigate to next page if not on last page
            if page_num < total_pages:
                try:
                    # Click the "next" button
                    next_button = page.locator('a[aria-label*="next"]').first
                    if next_button.is_visible():
                        next_button.click()
                        time.sleep(3)  # Wait for next page to load
                    else:
                        # Alternative: click the next page number
                        next_page_link = page.locator(f'a:has-text("{page_num + 1}")').first
                        next_page_link.click()
                        time.sleep(3)
                except Exception as e:
                    print(f"Error navigating to next page: {e}")
                    break

        browser.close()

    return locations

if __name__ == "__main__":
    print("Starting UofL Health locations scrape...")
    print("=" * 60)

    locations = scrape_uofl_locations()

    print("\n" + "=" * 60)
    print(f"Total locations scraped: {len(locations)}")

    # Save to JSON file
    output_file = "/Volumes/X10 Pro/Roscoe/json-files/uofl_health_locations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to: {output_file}")

    # Print first few examples
    print("\nFirst 3 locations:")
    for i, loc in enumerate(locations[:3], 1):
        print(f"\n{i}. {loc['name']}")
        print(f"   Address: {loc['address']}")
        print(f"   Phone: {loc['phone']}")
