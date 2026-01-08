#!/usr/bin/env python3
"""
Scrape all St. Elizabeth Healthcare locations - Version 3.
More precise extraction targeting individual location cards.
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

            # Extract locations using more targeted approach
            page_locations = page.evaluate('''() => {
                const results = [];
                const processed = new Set();

                // Find phone links that are actually part of location cards
                const phoneLinks = document.querySelectorAll('a[href^="tel:"]');

                phoneLinks.forEach(phoneLink => {
                    // Only process if it's a PH: phone link (not FAX:)
                    const phoneText = phoneLink.parentElement ? phoneLink.parentElement.innerText : '';
                    if (!phoneText.startsWith('PH:')) {
                        return;
                    }

                    // Find the immediate card container (not too far up)
                    // Location cards are typically 3-4 levels up from the phone link
                    let card = phoneLink.parentElement;
                    for (let i = 0; i < 4; i++) {
                        if (card.parentElement) card = card.parentElement;
                    }

                    const fullText = card.innerText;

                    // Skip if this looks like it contains multiple locations
                    if ((fullText.match(/PH:/g) || []).length > 2) {
                        // Too many phone numbers - went too high
                        card = phoneLink.parentElement.parentElement.parentElement;
                    }

                    const lines = fullText.split('\\n').map(l => l.trim()).filter(l => l);

                    // Extract name - should be one of the first few lines
                    let name = '';
                    for (let i = 0; i < Math.min(5, lines.length); i++) {
                        const line = lines[i];
                        if (!line.startsWith('PH:') &&
                            !line.startsWith('FAX:') &&
                            !line.startsWith('NEW SEARCH') &&
                            !line.includes('locations found') &&
                            !line.includes('Distance from') &&
                            !line.includes('Filter Results') &&
                            !line.includes('Location Details') &&
                            !line.includes('Get Directions') &&
                            !line.includes('Accepting') &&
                            !line.includes('Virtual') &&
                            !line.includes('Evening') &&
                            !line.includes('Online') &&
                            !/^\\d+\\s+(miles|locations)/.test(line) &&
                            !/^\\d+\\s*$/.test(line) &&
                            !/,\\s*[A-Z]{2}\\s+\\d{5}/.test(line) &&
                            line.length > 5) {
                            name = line;
                            break;
                        }
                    }

                    // Extract street address
                    let street = '';
                    for (const line of lines) {
                        if (/^\\d+\\s+[A-Z]/.test(line) && !line.includes('miles') && !line.includes('locations')) {
                            street = line;
                            break;
                        }
                    }

                    // Extract city, state, zip
                    let cityStateZip = '';
                    for (const line of lines) {
                        if (/^[A-Z][a-z]+,\\s*[A-Z]{2}\\s+\\d{5}/.test(line)) {
                            cityStateZip = line;
                            break;
                        }
                    }

                    // Extract phone from PH: line
                    const phoneMatch = fullText.match(/PH:\\s*\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}/);
                    const phone = phoneMatch ? phoneMatch[0].replace('PH:', '').trim() : '';

                    // Construct address
                    const address = street && cityStateZip ? `${street}, ${cityStateZip}` : (cityStateZip || street);

                    // Only add if we have valid data
                    const key = `${name}|${address}`;
                    if (name && address && !processed.has(key)) {
                        processed.add(key);
                        results.push({ name, address, phone });
                    }
                });

                return results;
            }''')

            print(f"  Found {len(page_locations)} locations")

            # Add to main list
            for loc in page_locations:
                key = f"{loc['name']}|{loc['address']}"
                if key not in seen:
                    seen.add(key)
                    locations.append(loc)

            # Navigate to next page
            if page_num < total_pages:
                try:
                    # Click next page using the next arrow or page number
                    clicked = page.evaluate(f'''() => {{
                        // Try to find the next page number link
                        const allLinks = Array.from(document.querySelectorAll('a[href="#"]'));

                        // Filter for the next page number
                        const nextPageLink = allLinks.find(a => {{
                            const txt = a.textContent.trim();
                            return txt === "{page_num + 1}";
                        }});

                        if (nextPageLink) {{
                            nextPageLink.click();
                            return true;
                        }}

                        // Try the next arrow
                        const navLinks = allLinks.filter(a => a.querySelector('img'));
                        if (navLinks.length > 0) {{
                            // Last one should be "next"
                            navLinks[navLinks.length - 1].click();
                            return true;
                        }}

                        return false;
                    }}''')

                    if not clicked:
                        print(f"  Could not navigate to page {page_num + 1}, stopping")
                        break

                    # Wait for page to update
                    time.sleep(4)

                except Exception as e:
                    print(f"  Navigation error: {str(e)[:100]}")
                    break

        browser.close()

    return locations

if __name__ == "__main__":
    print("Starting St. Elizabeth Healthcare locations scrape (v3)...")
    print("=" * 60)

    locations = scrape_stelizabeth_locations()

    print("\n" + "=" * 60)
    print(f"Total unique locations scraped: {len(locations)}")

    # Save to JSON file
    output_file = "/Volumes/X10 Pro/Roscoe/json-files/stelizabeth_locations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to: {output_file}")

    # Print examples
    if locations:
        print("\nFirst 10 locations:")
        for i, loc in enumerate(locations[:10], 1):
            print(f"\n{i}. {loc['name']}")
            print(f"   Address: {loc['address']}")
            print(f"   Phone: {loc['phone']}")

    # Statistics
    with_phone = sum(1 for loc in locations if loc['phone'])
    with_street = sum(1 for loc in locations if re.match(r'^\d+', loc['address']))

    print(f"\nStatistics:")
    print(f"  Total locations: {len(locations)}")
    print(f"  With phone numbers: {with_phone}")
    print(f"  With complete street addresses: {with_street}")
