#!/usr/bin/env python3
"""
Parse Baptist Health locations from PDF - Improved version.
Better separation of name from address.
"""

import json
import re
import pdfplumber

def clean_name(name):
    """Clean up the location name."""
    # Remove common UI elements that leaked into names
    name = re.sub(r'\s*ALL LOCATION TYPES.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*QUICK SEARCH.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*Enter City or Zip.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*HOSPITAL$', '', name)

    # Remove address fragments that got captured in name
    # Remove patterns like "900 Hospital Drive" at end of name
    name = re.sub(r'\s+\d+\s+[\w\s]+(Drive|Street|Road|Avenue|Boulevard|Way|Lane|Circle|Court|Place|Parkway)\s*$', '', name, flags=re.IGNORECASE)

    name = re.sub(r'\s+', ' ', name).strip()
    return name

def parse_baptist_pdf(pdf_path):
    """Parse all Baptist Health locations from PDF."""
    locations = []

    print(f"Opening PDF: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}")

        for page_num, page in enumerate(pdf.pages, 1):
            if page_num % 25 == 0:
                print(f"  Processing page {page_num}/{total_pages}...")

            text = page.extract_text()
            if not text:
                continue

            lines = [line.strip() for line in text.split('\n') if line.strip()]

            i = 0
            while i < len(lines):
                line = lines[i]

                # Look for location names
                is_location_name = (
                    'Baptist Health' in line or
                    'Baptist Imaging' in line or
                    'Ray & Kay Eckstein' in line
                )

                if is_location_name:
                    name = line
                    i += 1

                    # Collect address lines
                    address_lines = []
                    phone = ""

                    # Look ahead for address components
                    while i < len(lines) and len(address_lines) < 3:
                        current_line = lines[i]

                        # Check for phone number
                        if re.match(r'^\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', current_line):
                            phone = current_line
                            break

                        # Check for street address (starts with number)
                        if re.match(r'^\d+', current_line):
                            address_lines.append(current_line)
                            i += 1
                            continue

                        # Check for city/state/zip line
                        if re.search(r'[A-Z][a-z]+,\s*[A-Z]{2}\s+\d{5}', current_line):
                            address_lines.append(current_line)
                            i += 1
                            continue

                        # Stop if we hit certain keywords
                        if any(kw in current_line for kw in ['CARE AND SERVICES', 'PATIENTS', 'Location details', 'HOURS:', 'NOTICE']):
                            break

                        i += 1

                    # Only add if we have a complete address (street + city)
                    if len(address_lines) >= 2 or (len(address_lines) == 1 and re.search(r'[A-Z]{2}\s+\d{5}', address_lines[0])):
                        address = ' '.join(address_lines)
                        name = clean_name(name)

                        # Skip if name is invalid
                        if len(name) > 5 and not name.isupper():
                            locations.append({
                                "name": name,
                                "address": address,
                                "phone": phone
                            })
                else:
                    i += 1

    print(f"\nExtracted {len(locations)} locations from PDF")

    # Remove duplicates
    seen = set()
    unique_locations = []
    for loc in locations:
        key = f"{loc['name']}|{loc['address']}"
        if key not in seen:
            seen.add(key)
            unique_locations.append(loc)

    print(f"After removing duplicates: {len(unique_locations)} locations")

    return unique_locations

if __name__ == "__main__":
    print("Starting Baptist Health PDF parsing (v2)...")
    print("=" * 60)

    pdf_path = "/Volumes/X10 Pro/Roscoe/Find a Location - Baptist Health.pdf"
    locations = parse_baptist_pdf(pdf_path)

    print("\n" + "=" * 60)
    print(f"Total locations extracted: {len(locations)}")

    # Save to JSON file
    output_file = "/Volumes/X10 Pro/Roscoe/json-files/baptist_health_locations.json"
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
    with_street = sum(1 for loc in locations if re.match(r'^\d+', loc['address']))
    print(f"\nStatistics:")
    print(f"  Total locations: {len(locations)}")
    print(f"  With phone numbers: {with_phone}")
    print(f"  With street addresses: {with_street}")
