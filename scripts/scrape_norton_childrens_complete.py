#!/usr/bin/env python3
"""
Scrape all Norton Children's locations from their website.

The site organizes locations by type:
- Pediatrician Practice
- Specialist Practice
- Outpatient Center
- Hospital
- Pharmacy

We'll scrape each category separately.
"""

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import re


def scrape_location_type(location_type: str) -> list:
    """Scrape one type of location."""

    url = f"https://nortonchildrens.com/location/?type={location_type.replace(' ', '+')}"

    print(f"\nFetching {location_type}...")
    print(f"  URL: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"  ❌ Failed: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for individual location links (URLs like /location/some-location-name/)
        all_links = soup.find_all('a', href=True)
        location_links = []

        for link in all_links:
            href = link.get('href', '')
            # Match pattern: /location/[something]/ but not /location/?type=...
            if '/location/' in href and '?type=' not in href and href != '/location/':
                if not href.startswith('http'):
                    href = f"https://nortonchildrens.com{href}"
                location_links.append(href)

        # Deduplicate
        location_urls = list(set(location_links))

        print(f"  ✓ Found {len(location_urls)} location pages")

        # Scrape each location page
        locations = []

        for idx, loc_url in enumerate(location_urls, 1):
            loc_name = loc_url.split('/')[-2].replace('-', ' ').title()
            print(f"    {idx}/{len(location_urls)}: {loc_name[:40]}...", end=' ')

            try:
                loc_response = requests.get(loc_url, headers=headers, timeout=20)

                if loc_response.status_code != 200:
                    print("❌ Failed")
                    continue

                loc_soup = BeautifulSoup(loc_response.text, 'html.parser')

                location = {'url': loc_url}

                # Extract name (h1)
                h1 = loc_soup.find('h1')
                if h1:
                    location['name'] = h1.get_text(strip=True)

                # Extract address (look for common patterns)
                address_elem = (
                    loc_soup.find(class_=re.compile(r'address', re.I)) or
                    loc_soup.find('address') or
                    loc_soup.find(itemprop='address')
                )

                if address_elem:
                    # Clean up address text
                    address_text = address_elem.get_text(separator=' ', strip=True)
                    # Remove excessive whitespace
                    address_text = re.sub(r'\s+', ' ', address_text)
                    location['address'] = address_text

                # Extract phone
                phone_link = loc_soup.find('a', href=re.compile(r'^tel:'))
                if phone_link:
                    phone_text = phone_link.get_text(strip=True)
                    location['phone'] = phone_text

                # Extract specialty/department if available
                # Look for breadcrumbs, categories, or department info
                specialty_elem = loc_soup.find(class_=re.compile(r'specialty|department|category', re.I))
                if specialty_elem:
                    location['specialty'] = specialty_elem.get_text(strip=True)

                if location.get('name'):
                    locations.append(location)
                    print("✓")
                else:
                    print("⊙ No data")

                time.sleep(0.5)  # Be polite to the server

            except Exception as e:
                print(f"❌ {str(e)[:30]}")

        return locations

    except Exception as e:
        print(f"  ❌ Error fetching category: {str(e)}")
        return []


def main():
    """Scrape all Norton Children's location types."""

    print("="*70)
    print("NORTON CHILDREN'S LOCATION SCRAPER")
    print("="*70)

    location_types = [
        "Pediatrician Practice",
        "Specialist Practice",
        "Outpatient Center",
        "Hospital",
        "Pharmacy"
    ]

    all_locations = []

    for loc_type in location_types:
        locations = scrape_location_type(loc_type)
        all_locations.extend(locations)
        print(f"  Total for {loc_type}: {len(locations)}")

    print(f"\n" + "="*70)
    print(f"SCRAPING COMPLETE")
    print("="*70)
    print(f"\nTotal locations scraped: {len(all_locations)}")

    if not all_locations:
        print("\n❌ No locations found")
        return

    # Format for our entity structure
    formatted_locations = []

    for idx, loc in enumerate(all_locations, 1):
        formatted_loc = {
            'card_type': 'entity',
            'entity_type': 'MedicalProvider',
            'name': loc.get('name', ''),
            'attributes': {
                'address': loc.get('address', ''),
                'phone': loc.get('phone', ''),
                'parent_system': 'Norton Children\'s Hospital',
                'specialty': loc.get('specialty', 'pediatric'),
                'provider_type': 'pediatric'
            },
            'source_id': str(idx),
            'source_file': 'norton_childrens_website',
            'source_url': loc.get('url', '')
        }
        formatted_locations.append(formatted_loc)

    # Save to file
    output_file = Path("/Volumes/X10 Pro/Roscoe/json-files/norton_childrens_locations.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_locations, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to: {output_file}")

    # Show summary
    print("\nSample locations:")
    for loc in formatted_locations[:10]:
        name = loc['name'][:60]
        address = loc['attributes'].get('address', 'No address')[:40]
        print(f"  - {name}")
        print(f"    {address}")

    print(f"\n✅ Created norton_childrens_locations.json with {len(formatted_locations)} locations")


if __name__ == "__main__":
    main()
