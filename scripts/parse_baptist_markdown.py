#!/usr/bin/env python3
"""Parse Baptist Health locations from markdown file."""

import json
import re

md_path = "/Volumes/X10 Pro/Roscoe/baptist_health_locations.md"

print(f"Reading markdown file: {md_path}")

with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Split by page markers
pages = content.split('---')

print(f"Found {len(pages)} pages")

locations = []
seen = set()

for page in pages:
    lines = [line.strip() for line in page.split('\n') if line.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # Look for location names
        if 'Baptist Health' in line or 'Baptist Imaging' in line or 'Ray & Kay Eckstein' in line:
            name = line

            # Sometimes name continues on next line
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # Check if next line is a continuation (not an address, not a phone)
                if (not re.match(r'^\d+', next_line) and
                    not re.match(r'^\(?\d{3}\)?', next_line) and
                    not re.search(r'[A-Z]{2}\s+\d{5}', next_line) and
                    len(next_line) < 50 and
                    not any(kw in next_line for kw in ['CARE AND SERVICES', 'PATIENTS', 'Location details', 'HOURS', 'NOTICE', 'HOSPITAL', 'ER &'])):
                    name += ' ' + next_line
                    i += 1

            i += 1

            # Now look for address components
            street = ""
            city_state_zip = ""
            phone = ""

            # Look ahead up to 10 lines for address and phone
            for j in range(i, min(i + 10, len(lines))):
                check_line = lines[j]

                # Phone number
                if re.match(r'^\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', check_line):
                    phone = check_line
                    break

                # Street address (starts with number)
                if re.match(r'^\d+', check_line) and not street:
                    street = check_line
                    continue

                # City, State ZIP
                if re.search(r'[A-Z][a-z]+,\s*[A-Z]{2}\s+\d{5}', check_line):
                    city_state_zip = check_line
                    continue

                # Stop at certain keywords
                if any(kw in check_line for kw in ['Location details', 'HOURS:', 'NOTICE', 'Baptist Health']):
                    break

            # Construct full address
            address_parts = []
            if street:
                address_parts.append(street)
            if city_state_zip:
                address_parts.append(city_state_zip)

            address = ', '.join(address_parts) if address_parts else city_state_zip

            # Clean up name
            name = re.sub(r'\s+', ' ', name).strip()

            # Only add if we have name and at least city/state
            if name and city_state_zip:
                # Create unique key
                key = f"{name}|{address}"

                if key not in seen:
                    seen.add(key)
                    locations.append({
                        "name": name,
                        "address": address,
                        "phone": phone
                    })

        i += 1

print(f"\nExtracted {len(locations)} unique locations")

# Save to JSON
output_file = "/Volumes/X10 Pro/Roscoe/json-files/baptist_health_locations.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(locations, f, indent=2, ensure_ascii=False)

print(f"Data saved to: {output_file}")

# Show first 10
print("\nFirst 10 locations:")
for i, loc in enumerate(locations[:10], 1):
    print(f"\n{i}. {loc['name']}")
    print(f"   Address: {loc['address']}")
    print(f"   Phone: {loc['phone']}")

# Statistics
with_phone = sum(1 for loc in locations if loc['phone'])
with_street = sum(1 for loc in locations if ',' in loc['address'] and re.match(r'^\d+', loc['address']))

print(f"\nStatistics:")
print(f"  Total locations: {len(locations)}")
print(f"  With phone numbers: {with_phone}")
print(f"  With complete addresses (street + city): {with_street}")
