#!/usr/bin/env python3
"""
Scrape all Baptist Health locations from their website.
Extracts name, address, and phone number for all 550 locations.
"""

import json
import re
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

def extract_location_from_card(card):
    """Extract name, address, and phone from a location card."""
    try:
        # Get the location name from the link
        try:
            name_link = card.locator('a[href*="/locations/"], a[href*="baptisthealthdeaconess.com"]').first
            name = name_link.inner_text(timeout=1000).strip()
        except:
            name = ""

        # Get the address (look for the link with "maps/dir" in href)
        try:
            address_link = card.locator('a[href*="maps/dir"]').first
            address_text = address_link.inner_text(timeout=1000).strip()
            # Remove newlines and extra spaces
            address = ' '.join(address_text.split())
        except:
            address = ""

        # Get the phone number (look for tel: link)
        try:
            phone_link = card.locator('a[href^="tel:"]').first
            phone = phone_link.inner_text(timeout=1000).strip()
        except:
            phone = ""

        return {
            "name": name,
            "address": address,
            "phone": phone
        }
    except Exception as e:
        return None

def scrape_baptist_locations():
    """Scrape all Baptist Health locations."""
    locations = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("Loading Baptist Health locations page...")
        page.goto('https://www.baptisthealth.com/locations?activeTab=list', wait_until='networkidle', timeout=30000)

        print("Waiting for locations to load...")
        time.sleep(3)

        # Click "View More" button repeatedly to load all locations
        print("Loading all 550 locations by clicking 'View More'...")
        max_clicks = 60  # Increased to load more locations
        clicks = 0
        consecutive_failures = 0

        while clicks < max_clicks and consecutive_failures < 3:
            try:
                view_more_button = page.locator('button:has-text("View More")').first

                if view_more_button.is_visible(timeout=2000):
                    view_more_button.click(timeout=3000)
                    clicks += 1
                    consecutive_failures = 0
                    if clicks % 5 == 0:
                        print(f"  Clicked 'View More' {clicks} times...")
                    time.sleep(1)  # Reduced wait time
                else:
                    consecutive_failures += 1
                    print(f"  Button not visible (attempt {consecutive_failures}/3)")
                    time.sleep(0.5)
            except Exception as e:
                consecutive_failures += 1
                print(f"  Error clicking (attempt {consecutive_failures}/3): {str(e)[:50]}")
                time.sleep(0.5)

        print(f"  Finished loading locations (clicked {clicks} times)")
        print("Extracting location data...")
        time.sleep(1)

        # Get all location list items
        location_items = page.locator('div[role="tabpanel"] ul li').all()

        print(f"Found {len(location_items)} location cards")

        seen_names = set()
        for i, item in enumerate(location_items, 1):
            try:
                location_data = extract_location_from_card(item)

                if location_data and location_data['name'] and location_data['address']:
                    # Skip if we've seen this name+address combo before
                    identifier = f"{location_data['name']}|{location_data['address']}"
                    if identifier not in seen_names:
                        locations.append(location_data)
                        seen_names.add(identifier)

                        if len(locations) % 50 == 0:
                            print(f"  Extracted {len(locations)} locations...")
            except Exception as e:
                pass  # Skip items that can't be parsed

        print(f"  Extracted {len(locations)} total locations")
        browser.close()

    return locations

if __name__ == "__main__":
    print("Starting Baptist Health locations scrape...")
    print("=" * 60)

    locations = scrape_baptist_locations()

    print("\n" + "=" * 60)
    print(f"Total locations scraped: {len(locations)}")

    # Save to JSON file
    output_file = "/Volumes/X10 Pro/Roscoe/json-files/baptist_health_locations.json"
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
