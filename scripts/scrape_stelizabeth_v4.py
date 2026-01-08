#!/usr/bin/env python3
"""
Scrape all St. Elizabeth Healthcare locations - Version 4.
Uses URL-based pagination for reliability.
"""

import json
import re
import time
from playwright.sync_api import sync_playwright

def extract_locations_from_page(page):
    """Extract all locations from current page using Python locators."""
    locations = []

    try:
        # Wait for location details links to appear
        page.wait_for_selector('a:text("Location Details")', timeout=10000)

        # Find all "Location Details" links
        detail_links = page.locator('a:text("Location Details")').all()

        print(f"    Found {len(detail_links)} location cards on page")

        for i, link in enumerate(detail_links):
            try:
                # Get the parent container (go up a few levels to get the card)
                # Try different levels to find the right container
                for level_up in [3, 4, 5]:
                    try:
                        container = link
                        for _ in range(level_up):
                            container = container.locator('..')

                        text = container.inner_text(timeout=2000)

                        # Check if this container has exactly one phone number
                        ph_count = text.count('PH:')
                        if ph_count == 1:
                            # Found the right level
                            lines = [l.strip() for l in text.split('\n') if l.strip()]

                            # Extract name (first line that's not metadata)
                            name = ""
                            for line in lines:
                                if (not line.startswith('PH:') and
                                    not line.startswith('FAX:') and
                                    'Location Details' not in line and
                                    'Get Directions' not in line and
                                    'Accepting' not in line and
                                    'Virtual' not in line and
                                    'Evening' not in line and
                                    'Online' not in line and
                                    not re.match(r'^\d+', line) and
                                    not re.search(r',\s*[A-Z]{2}\s+\d{5}', line) and
                                    len(line) > 5):
                                    name = line
                                    break

                            # Extract street
                            street = ""
                            for line in lines:
                                if re.match(r'^\d+', line) and 'miles' not in line.lower():
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

                            # Build address
                            if street and city_state_zip:
                                address = f"{street}, {city_state_zip}"
                            else:
                                address = city_state_zip or street

                            if name and address:
                                locations.append({
                                    "name": name,
                                    "address": address,
                                    "phone": phone
                                })
                                break  # Found the right level, move to next location

                    except:
                        continue  # Try next level

            except Exception as e:
                # Skip this location if we can't extract it
                pass

    except Exception as e:
        print(f"    Error finding locations on page: {str(e)[:100]}")

    return locations

def scrape_stelizabeth_locations():
    """Scrape all St. Elizabeth Healthcare locations."""
    all_locations = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Loop through pages by constructing URLs
        # The site uses hash-based pagination or AJAX, so we'll navigate and wait
        base_url = 'https://www.stelizabeth.com/care/find-a-location/results/'

        print("Loading first page...")
        page.goto(base_url, wait_until='domcontentloaded')
        time.sleep(6)

        total_pages = 42

        for page_num in range(1, total_pages + 1):
            print(f"\nPage {page_num}/{total_pages}:")

            # Extract locations from current page
            page_locations = extract_locations_from_page(page)

            print(f"    Extracted {len(page_locations)} locations")

            # Add to master list
            for loc in page_locations:
                key = f"{loc['name'].lower()}|{loc['address'].lower()}"
                if key not in seen:
                    seen.add(key)
                    all_locations.append(loc)

            # Navigate to next page if not last
            if page_num < total_pages:
                try:
                    # Find and click the next page number
                    next_num_str = str(page_num + 1)
                    next_link = page.locator(f'a:text("{next_num_str}")').first

                    next_link.click(timeout=3000, no_wait_after=True)
                    time.sleep(5)  # Wait for AJAX content to load

                except Exception as e:
                    print(f"    Navigation failed: {str(e)[:80]}")
                    # Try clicking the next arrow
                    try:
                        # The arrow is an image link
                        arrows = page.locator('nav a').all()
                        if len(arrows) > 0:
                            arrows[-1].click(timeout=3000, no_wait_after=True)
                            time.sleep(5)
                    except:
                        print(f"    Could not navigate to page {page_num + 1}")
                        break

        browser.close()

    return all_locations

if __name__ == "__main__":
    print("Starting St. Elizabeth Healthcare locations scrape (v4)...")
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
