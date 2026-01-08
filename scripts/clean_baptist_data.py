#!/usr/bin/env python3
"""Clean up the Baptist Health locations data."""

import json
import re

# Load the data
with open("/Volumes/X10 Pro/Roscoe/json-files/baptist_health_locations.json", 'r') as f:
    locations = json.load(f)

print(f"Loaded {len(locations)} locations")

cleaned_locations = []

for loc in locations:
    name = loc['name']
    address = loc['address']
    phone = loc['phone']

    # Clean name - remove unwanted fragments
    name = re.sub(r'\s+ALL LOCATION TYPES.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+QUICK SEARCH.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+Enter City or Zip.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+Type of Location.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+HOSPITAL.*900 Hospital Drive$', '', name)
    name = re.sub(r'\s*\d{3,4} Hospital Drive$', '', name)
    name = re.sub(r'\s+\d+\s+[A-Z][a-z]+.*$', '', name)  # Remove address fragments at end

    # Clean name - normalize spaces
    name = re.sub(r'\s+', ' ', name).strip()

    # Clean address - ensure proper spacing between street and city
    # Pattern: "123 Street Cityname, KY 12345" -> "123 Street, Cityname, KY 12345"
    address = re.sub(r'([A-Za-z]+)\s+([A-Z][a-z]+,\s*[A-Z]{2}\s+\d{5})', r'\1, \2', address)

    # Clean phone
    phone = phone.strip()

    # Skip if name is too short or looks invalid
    if len(name) < 5 or name.isupper() or name.isdigit():
        continue

    # Skip if address is missing city/state
    if not re.search(r'[A-Z]{2}\s+\d{5}', address):
        continue

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

# Show first 5
print("\nFirst 5 cleaned locations:")
for i, loc in enumerate(cleaned_locations[:5], 1):
    print(f"\n{i}. {loc['name']}")
    print(f"   Address: {loc['address']}")
    print(f"   Phone: {loc['phone']}")

# Statistics
with_phone = sum(1 for loc in cleaned_locations if loc['phone'])
print(f"\nFinal statistics:")
print(f"  Total locations: {len(cleaned_locations)}")
print(f"  With phone numbers: {with_phone}")
