#!/usr/bin/env python3
"""Final cleanup of Baptist Health locations data."""

import json
import re

# Load the data
with open("/Volumes/X10 Pro/Roscoe/json-files/baptist_health_locations.json", 'r') as f:
    locations = json.load(f)

print(f"Loaded {len(locations)} locations")

cleaned_locations = []
seen = set()

for loc in locations:
    name = loc['name']
    address = loc['address']
    phone = loc['phone']

    # Clean name - remove UI elements that leaked in
    name = re.sub(r'\s+ALL LOCATION TYPES.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+QUICK SEARCH.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+SHOW MORE.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+TYPE OF LOCATION.*$', '', name, flags=re.IGNORECASE)

    # Clean name - fix truncated names
    # If name ends with "& " or " -", it's likely truncated - try to fix common patterns
    if name.endswith('&'):
        name = name + ' Urgent Care'  # Most common pattern
    elif name.endswith(' -'):
        name = name.rstrip(' -')  # Remove trailing dash

    # Clean name - normalize whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    # Clean address - remove corrupted text
    address = re.sub(r'CARE AND SRERVICES', '', address, flags=re.IGNORECASE)
    address = re.sub(r'CARE AND SRERicVhICmESond', 'Richmond', address)
    address = re.sub(r'BLOG\s+', '', address)
    address = re.sub(r'PATIENTS.*$', '', address)
    address = re.sub(r'CONNHOESCPTIT.*$', '', address)

    # Clean address - normalize whitespace and commas
    address = re.sub(r'\s+', ' ', address).strip()
    address = re.sub(r',\s*,', ',', address)  # Remove duplicate commas

    # Clean phone
    phone = phone.strip()

    # Skip if name is too short or invalid
    if len(name) < 8:
        continue

    # Skip if address doesn't have proper state/zip
    if not re.search(r'[A-Z]{2}\s+\d{5}', address):
        continue

    # Skip if address has obvious corruption
    if any(bad in address.upper() for bad in ['CONNHOESCPTIT', 'ABOUFT', 'SRERVICES']):
        continue

    # Create unique key and check for duplicates
    key = f"{name.lower()}|{address.lower()}"
    if key not in seen:
        seen.add(key)
        cleaned_locations.append({
            "name": name,
            "address": address,
            "phone": phone
        })

print(f"After cleaning: {len(cleaned_locations)} locations")

# Save cleaned data
with open("/Volumes/X10 Pro/Roscoe/json-files/baptist_health_locations.json", 'w') as f:
    json.dump(cleaned_locations, f, indent=2, ensure_ascii=False)

print("Cleaned data saved!")

# Show first 10
print("\nFirst 10 cleaned locations:")
for i, loc in enumerate(cleaned_locations[:10], 1):
    print(f"\n{i}. {loc['name']}")
    print(f"   Address: {loc['address']}")
    print(f"   Phone: {loc['phone']}")

# Statistics
with_phone = sum(1 for loc in cleaned_locations if loc['phone'])
with_complete_address = sum(1 for loc in cleaned_locations if ',' in loc['address'])

print(f"\nFinal statistics:")
print(f"  Total locations: {len(cleaned_locations)}")
print(f"  With phone numbers: {with_phone}")
print(f"  With complete addresses: {with_complete_address}")
