#!/usr/bin/env python3
"""
Parse Baptist Health locations from PDF file.
Extracts name, address, and phone number for all 550 locations.
"""

import json
import re
import pdfplumber

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

            # Split into lines
            lines = [line.strip() for line in text.split('\n') if line.strip()]

            i = 0
            while i < len(lines):
                line = lines[i]

                # Look for patterns that indicate a location name
                # Names usually contain "Baptist Health" or end with specific facility types
                is_location_name = (
                    'Baptist Health' in line or
                    'Baptist Imaging' in line or
                    'Ray & Kay Eckstein' in line or
                    line.endswith('Hospital') or
                    line.endswith('Center') or
                    line.endswith('Clinic') or
                    line.endswith('Pharmacy') or
                    line.endswith('Services')
                )

                if is_location_name:
                    # Found a potential location name
                    name_parts = [line]

                    # Check next lines to see if they're part of the name
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j]

                        # If next line looks like an address (starts with number), stop
                        if re.match(r'^\d+', next_line):
                            break

                        # If next line is a phone number, stop
                        if re.match(r'^\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', next_line):
                            break

                        # If next line looks like city/state, stop
                        if re.search(r'[A-Z][a-z]+,\s*[A-Z]{2}\s+\d{5}', next_line):
                            break

                        # If next line is too short or looks like continuation
                        if len(next_line) < 50 and not next_line.startswith('CARE') and not next_line.startswith('PATIENTS'):
                            name_parts.append(next_line)
                            j += 1
                        else:
                            break

                    name = ' '.join(name_parts)

                    # Now look for address after the name
                    address_parts = []
                    phone = ""

                    k = j
                    while k < len(lines) and k < j + 10:  # Look within next 10 lines
                        addr_line = lines[k]

                        # Check if this is a phone number
                        if re.match(r'^\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', addr_line):
                            phone = addr_line
                            break

                        # Check if this looks like part of an address
                        if re.match(r'^\d+', addr_line) or re.search(r'[A-Z][a-z]+,\s*[A-Z]{2}\s+\d{5}', addr_line):
                            address_parts.append(addr_line)

                        k += 1

                    if address_parts:
                        address = ' '.join(address_parts)

                        # Clean up the data
                        name = re.sub(r'\s+', ' ', name).strip()
                        address = re.sub(r'\s+', ' ', address).strip()

                        if name and address:
                            locations.append({
                                "name": name,
                                "address": address,
                                "phone": phone
                            })

                    # Skip past the lines we've processed
                    i = max(k, j)
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
    print("Starting Baptist Health PDF parsing...")
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

    # Print first few examples
    if locations:
        print("\nFirst 5 locations:")
        for i, loc in enumerate(locations[:5], 1):
            print(f"\n{i}. {loc['name']}")
            print(f"   Address: {loc['address']}")
            print(f"   Phone: {loc['phone']}")

    # Print statistics
    locations_with_phone = sum(1 for loc in locations if loc['phone'])
    print(f"\nStatistics:")
    print(f"  Locations with names: {sum(1 for loc in locations if loc['name'])}")
    print(f"  Locations with addresses: {sum(1 for loc in locations if loc['address'])}")
    print(f"  Locations with phone numbers: {locations_with_phone}")
