#!/usr/bin/env python3
"""
Scrape Norton Children's locations using Playwright.

Scrapes https://nortonchildrens.com/location/ with full JavaScript rendering.
"""

import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def scrape_norton_childrens():
    """Scrape Norton Children's locations."""

    url = "https://nortonchildrens.com/location/"
    locations = []

    print(f"Launching browser and navigating to {url}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until='networkidle', timeout=60000)
            print("✓ Page loaded")

            # Wait for content to load
            await page.wait_for_timeout(3000)

            # Scroll to bottom to trigger lazy loading
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)

            # Try to find all location links or elements
            # Look for links that go to individual location pages
            location_links = await page.query_selector_all('a[href*="/location/"]')

            print(f"Found {len(location_links)} location links")

            # Extract unique location URLs
            location_urls = set()

            for link in location_links:
                href = await link.get_attribute('href')
                if href and '/location/' in href and href != '/location/':
                    # Make absolute URL
                    if href.startswith('/'):
                        href = f"https://nortonchildrens.com{href}"
                    location_urls.add(href)

            print(f"Found {len(location_urls)} unique location pages")

            # Visit each location page to extract details
            for idx, loc_url in enumerate(sorted(location_urls)[:100], 1):  # Limit to 100 for safety
                print(f"Scraping {idx}/{min(len(location_urls), 100)}: {loc_url.split('/')[-2]}...", end=' ')

                try:
                    await page.goto(loc_url, wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(1000)

                    # Extract location details
                    location = {'url': loc_url}

                    # Try to find name (usually in h1 or title)
                    name_elem = await page.query_selector('h1')
                    if name_elem:
                        location['name'] = await name_elem.text_content()
                        location['name'] = location['name'].strip()

                    # Try to find address
                    address_selectors = [
                        '[class*="address"]',
                        'address',
                        '[itemprop="address"]',
                        '.location-address'
                    ]

                    for selector in address_selectors:
                        addr_elem = await page.query_selector(selector)
                        if addr_elem:
                            location['address'] = await addr_elem.text_content()
                            location['address'] = location['address'].strip()
                            break

                    # Try to find phone
                    phone_elem = await page.query_selector('a[href^="tel:"]')
                    if phone_elem:
                        phone_text = await phone_elem.text_content()
                        location['phone'] = phone_text.strip()

                    if location.get('name'):
                        locations.append(location)
                        print(f"✓ {location['name'][:50]}")
                    else:
                        print("⊙ No name found")

                except Exception as e:
                    print(f"❌ Error: {str(e)[:50]}")

        finally:
            await browser.close()

    return locations


def format_for_json(locations: list) -> list:
    """Format locations to match our entity card structure."""

    formatted = []

    for idx, loc in enumerate(locations, 1):
        formatted_loc = {
            'card_type': 'entity',
            'entity_type': 'MedicalProvider',
            'name': loc.get('name', ''),
            'attributes': {
                'address': loc.get('address', ''),
                'phone': loc.get('phone', ''),
                'parent_system': 'Norton Children\'s Hospital',
                'specialty': 'pediatric'
            },
            'source_id': str(idx),
            'source_file': 'norton_childrens_website',
            'source_url': loc.get('url', '')
        }
        formatted.append(formatted_loc)

    return formatted


async def main():
    """Main scraping function."""

    print("="*70)
    print("NORTON CHILDREN'S LOCATION SCRAPER - PLAYWRIGHT")
    print("="*70)
    print()

    locations = await scrape_norton_childrens()

    print(f"\n✓ Scraped {len(locations)} locations")

    if not locations:
        print("\n❌ No locations found")
        return

    # Format for our JSON structure
    formatted = format_for_json(locations)

    # Save to file
    output_file = Path("/Volumes/X10 Pro/Roscoe/json-files/norton_childrens_locations.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved to: {output_file}")
    print(f"\nTotal locations: {len(formatted)}")

    # Show sample
    print("\nSample locations:")
    for loc in formatted[:5]:
        print(f"  - {loc['name']}")

    print("\n✅ Scraping complete")


if __name__ == "__main__":
    asyncio.run(main())
