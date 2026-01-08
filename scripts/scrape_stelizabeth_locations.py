#!/usr/bin/env python3
"""
Scrape all St. Elizabeth Healthcare locations.
Extracts name, address, and phone number for all 414 locations.
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

        print("Waiting for locations to load...")
        time.sleep(8)

        total_pages = 42

        for page_num in range(1, total_pages + 1):
            print(f"\nProcessing page {page_num}/{total_pages}...")

            # Wait for content
            time.sleep(2)

            # Extract all location cards from the current page
            page_locations = page.evaluate('''() => {
                const results = [];
                const processed = new Set();

                // Find all links that say "Location Details"
                const allLinks = document.querySelectorAll('a');
                const detailLinks = Array.from(allLinks).filter(a => a.textContent.includes('Location Details'));

                detailLinks.forEach(detailLink => {
                    // Get parent container for this location
                    let card = detailLink.parentElement;
                    for (let i = 0; i < 6; i++) {
                        if (card.parentElement) card = card.parentElement;
                    }

                    const fullText = card.innerText;
                    const lines = fullText.split('\\n').map(l => l.trim()).filter(l => l && l.length > 0);

                    // Extract name (first meaningful line)
                    let name = '';
                    for (const line of lines) {
                        if (!line.startsWith('PH:') &&
                            !line.startsWith('FAX:') &&
                            !line.includes('Location Details') &&
                            !line.includes('Get Directions') &&
                            !line.includes('Accepting') &&
                            !line.includes('Virtual') &&
                            !line.includes('Evening') &&
                            !line.includes('Online') &&
                            !/^\\d+/.test(line) &&
                            !/,\\s*[A-Z]{2}\\s+\\d{5}/.test(line)) {
                            name = line;
                            break;
                        }
                    }

                    // Extract street address
                    let street = '';
                    for (const line of lines) {
                        if (/^\\d+/.test(line) && !line.includes('miles')) {
                            street = line;
                            break;
                        }
                    }

                    // Extract city, state, zip
                    let cityStateZip = '';
                    for (const line of lines) {
                        if (/[A-Z][a-z]+,\\s*[A-Z]{2}\\s+\\d{5}/.test(line)) {
                            cityStateZip = line;
                            break;
                        }
                    }

                    // Extract phone
                    let phone = '';
                    for (const line of lines) {
                        if (line.startsWith('PH:')) {
                            const match = line.match(/\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}/);
                            if (match) phone = match[0];
                            break;
                        }
                    }

                    // Construct address
                    const address = street && cityStateZip ? `${street}, ${cityStateZip}` : (cityStateZip || street);

                    // Only add if we have valid data and haven't seen it
                    const key = `${name}|${address}`;
                    if (name && address && name.length > 3 && !processed.has(key)) {
                        processed.add(key);
                        results.push({ name, address, phone });
                    }
                });

                return results;
            }''')

            print(f"  Found {len(page_locations)} locations")

            # Add to main list (check for global duplicates too)
            for loc in page_locations:
                key = f"{loc['name']}|{loc['address']}"
                if key not in seen:
                    seen.add(key)
                    locations.append(loc)

            # Navigate to next page
            if page_num < total_pages:
                try:
                    # Use JavaScript to click the pagination link
                    success = page.evaluate(f'''() => {{
                        const allLinks = document.querySelectorAll('a[href="#"]');
                        const pageLinks = Array.from(allLinks).filter(a => {{
                            const text = a.textContent.trim();
                            return text === "{page_num + 1}" && !a.querySelector('img');
                        }});

                        if (pageLinks.length > 0) {{
                            pageLinks[0].click();
                            return true;
                        }}
                        return false;
                    }}''')

                    if not success:
                        print(f"  Could not find link to page {page_num + 1}")
                        break

                    # Wait for new page to load
                    time.sleep(4)

                except Exception as e:
                    print(f"  Error navigating: {str(e)[:80]}")
                    break

        browser.close()

    return locations

if __name__ == "__main__":
    print("Starting St. Elizabeth Healthcare locations scrape...")
    print("=" * 60)

    locations = scrape_stelizabeth_locations()

    print("\n" + "=" * 60)
    print(f"Total unique locations scraped: {len(locations)}")

    # Save to JSON file
    output_file = "/Volumes/X10 Pro/Roscoe/json-files/stelizabeth_locations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to: {output_file}")

    # Print first 10 examples
    if locations:
        print("\nFirst 10 locations:")
        for i, loc in enumerate(locations[:10], 1):
            print(f"\n{i}. {loc['name']}")
            print(f"   Address: {loc['address']}")
            print(f"   Phone: {loc['phone']}")

    # Statistics
    with_phone = sum(1 for loc in locations if loc['phone'])
    print(f"\nStatistics:")
    print(f"  Total locations: {len(locations)}")
    print(f"  With phone numbers: {with_phone}")
