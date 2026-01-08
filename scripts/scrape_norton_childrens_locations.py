#!/usr/bin/env python3
"""
Scrape Norton Children's locations from their website.

This script will scrape https://nortonchildrens.com/location/
and create a norton_childrens_locations.json file.

Usage:
    python3 scrape_norton_childrens_locations.py
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path


def scrape_norton_childrens_locations():
    """Scrape Norton Children's locations."""

    url = "https://nortonchildrens.com/location/"

    print(f"Fetching {url}...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch page: {response.status_code}")
        return []

    print("✓ Page loaded")
    print("Parsing HTML...")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for location listings (this will need adjustment based on actual page structure)
    locations = []

    # Try to find all location cards/listings
    # Common patterns: article tags, divs with class containing "location", "card", etc.

    location_elements = soup.find_all(['article', 'div'], class_=lambda x: x and ('location' in x.lower() or 'card' in x.lower()))

    print(f"Found {len(location_elements)} potential location elements")

    for element in location_elements:
        # Extract name
        name_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'])
        if not name_elem:
            continue

        name = name_elem.get_text(strip=True)

        # Extract address
        address_elem = element.find(class_=lambda x: x and 'address' in x.lower())
        address = address_elem.get_text(strip=True) if address_elem else None

        # Extract phone
        phone_elem = element.find('a', href=lambda x: x and x.startswith('tel:'))
        phone = phone_elem.get_text(strip=True) if phone_elem else None

        if name and len(name) > 5:
            location = {
                'name': name,
                'address': address,
                'phone': phone
            }
            locations.append(location)

    # If no locations found, try alternative structure
    if len(locations) == 0:
        print("⚠️  No locations found with standard structure")
        print("Trying alternative extraction...")

        # Look for all links that might be location pages
        links = soup.find_all('a', href=lambda x: x and '/location/' in x)

        print(f"Found {len(links)} location links")

        for link in links[:10]:  # Sample first 10
            text = link.get_text(strip=True)
            href = link.get('href')
            print(f"  - {text}: {href}")

    return locations


def save_locations_json(locations: list, output_file: Path):
    """Save locations to JSON file in the same format as other health systems."""

    # Convert to same format as other location files
    formatted_locations = []

    for idx, loc in enumerate(locations, 1):
        formatted_loc = {
            'card_type': 'entity',
            'entity_type': 'MedicalProvider',
            'name': loc['name'],
            'attributes': {
                'address': loc.get('address', ''),
                'phone': loc.get('phone', ''),
                'parent_system': 'Norton Children\'s Hospital'
            },
            'source_id': str(idx),
            'source_file': 'norton_childrens_website'
        }
        formatted_locations.append(formatted_loc)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_locations, f, indent=2)

    print(f"\n✓ Saved {len(formatted_locations)} locations to {output_file}")


def main():
    """Main scraping function."""

    print("="*70)
    print("NORTON CHILDREN'S LOCATION SCRAPER")
    print("="*70)
    print()

    locations = scrape_norton_childrens_locations()

    if not locations:
        print("\n⚠️  No locations extracted")
        print("\nNOTE: Norton Children's website may use dynamic JavaScript loading.")
        print("Recommendation: Use Playwright/Selenium for full scraping or")
        print("manually compile locations from the website.")
        return

    output_file = Path("/Volumes/X10 Pro/Roscoe/json-files/norton_childrens_locations.json")
    save_locations_json(locations, output_file)

    print("\n✅ Scraping complete")


if __name__ == "__main__":
    main()
