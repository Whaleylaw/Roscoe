#!/usr/bin/env python3
"""Parse CHI (CommonSpirit Health) locations from markdown files."""

import json
import re
import os

def parse_chi_markdown(md_path):
    """Parse locations from a CHI markdown file."""
    locations = []

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by page markers
    pages = content.split('---')

    for page in pages:
        lines = [line.strip() for line in page.split('\n') if line.strip()]

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for CHI location names
            if line.startswith('CHI Saint Joseph'):
                # Remove type suffixes that often get concatenated
                name = re.sub(r'\s+(Therapy\s*Services|Specialty\s*Center|Medical\s*Group\s*Clinic|Hospital|Emergency\s*Room)Open.*$', '', line)
                name = re.sub(r'\s+ServicesOpen.*$', '', name)
                name = re.sub(r'\s+CenterOpen.*$', '', name)
                name = re.sub(r'\s+ClinicOpen.*$', '', name)
                name = re.sub(r'\s+HospitalOpen.*$', '', name)
                name = re.sub(r'\s+RoomOpen.*$', '', name)
                name = name.strip()

                # Sometimes name continues on next line (before the type)
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # Check if next line is a type indicator (contains "Open" or common types)
                    if any(keyword in next_line for keyword in ['ServicesOpen', 'CenterOpen', 'ClinicOpen', 'HospitalOpen', 'RoomOpen']):
                        # Name is complete, address should be after this
                        i += 1
                    else:
                        # Next line might be continuation of name
                        if (not re.search(r'\d+.*(?:Street|Drive|Road|Avenue|Boulevard|Way)', next_line) and
                            not re.search(r'[A-Z][a-z]+,\s*[A-Z]{2}\s+\d{5}', next_line) and
                            'Call' not in next_line and
                            'Get Directions' not in next_line and
                            'Open' not in next_line and
                            len(next_line) < 80):
                            name += ' ' + next_line
                            i += 1

                i += 1

                # Now look for address (next line that looks like an address)
                address = ""
                for j in range(i, min(i + 5, len(lines))):
                    check_line = lines[j]

                    # Check if this is an address line
                    # Address pattern: number + street, city, state zip
                    if re.search(r'\d+.*,.*[A-Z]{2}\s+\d{5}', check_line):
                        # Remove distance info like "62 mi away"
                        address = re.sub(r'\d+(\.\d+)?\s*mi\s+away.*$', '', check_line).strip()
                        break

                    # Stop at certain markers
                    if 'Call' in check_line or 'Get Directions' in check_line or 'https://' in check_line:
                        break

                # Clean up name
                name = re.sub(r'\s+', ' ', name).strip()

                if name and address:
                    locations.append({
                        "name": name,
                        "address": address,
                        "phone": ""  # Not available in markdown
                    })

            i += 1

    return locations

def main():
    base_dir = "/Volumes/X10 Pro/Roscoe"
    md_files = [f"CHI-{i}.md" for i in range(1, 10)]

    all_locations = []
    seen = set()

    print("Parsing CHI location markdown files...")
    print("=" * 60)

    for md_file in md_files:
        md_path = os.path.join(base_dir, md_file)

        if not os.path.exists(md_path):
            print(f"\nSkipping {md_file} - file not found")
            continue

        print(f"\nParsing {md_file}...")

        try:
            locations = parse_chi_markdown(md_path)
            print(f"  Found {len(locations)} locations")

            # Add to master list (avoid duplicates)
            for loc in locations:
                key = f"{loc['name'].lower()}|{loc['address'].lower()}"
                if key not in seen:
                    seen.add(key)
                    all_locations.append(loc)

        except Exception as e:
            print(f"  Error: {str(e)[:100]}")

    print("\n" + "=" * 60)
    print(f"Total unique locations: {len(all_locations)}")

    # Save to JSON
    output_file = os.path.join(base_dir, "json-files", "chi_saint_joseph_locations.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_locations, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to: {output_file}")

    # Show samples
    if all_locations:
        print("\nFirst 10 locations:")
        for i, loc in enumerate(all_locations[:10], 1):
            print(f"\n{i}. {loc['name']}")
            print(f"   Address: {loc['address']}")
            print(f"   Phone: {loc['phone']}")

    # Statistics
    with_address = sum(1 for loc in all_locations if loc['address'])
    print(f"\nStatistics:")
    print(f"  Total: {len(all_locations)}")
    print(f"  With addresses: {with_address}")
    print(f"  Note: Phone numbers not available in source data")

if __name__ == "__main__":
    main()
