#!/usr/bin/env python3
"""Clean up CHI Saint Joseph locations data."""

import json
import re

# Load the data
input_file = "/Volumes/X10 Pro/Roscoe/json-files/chi_saint_joseph_locations.json"

with open(input_file, 'r') as f:
    locations = json.load(f)

print(f"Loaded {len(locations)} locations")

cleaned_locations = []

for loc in locations:
    name = loc['name']
    address = loc['address']
    phone = loc['phone']

    # Clean name - remove type suffixes that got included
    # Match patterns with or without space before "Open"
    name = re.sub(r'\s+Therapy\s*ServicesOpen\s*', '', name)
    name = re.sub(r'\s+Specialty\s*CenterOpen\s*', '', name)
    name = re.sub(r'\s+Medical\s+Group\s+ClinicOpen\s*', '', name)
    name = re.sub(r'\s+HospitalOpen\s*', '', name)
    name = re.sub(r'\s+Emergency\s+RoomOpen\s*', '', name)
    name = re.sub(r'\s+ClinicOpen\s*', '', name)
    name = re.sub(r'\s+CenterOpen\s*', '', name)
    name = re.sub(r'\s+ServicesOpen\s*', '', name)
    name = re.sub(r'\s+RoomOpen\s*', '', name)

    # Also remove if they're at the end without "Open"
    name = re.sub(r'\s+(Therapy Services|Specialty Center|Medical Group Clinic|Emergency Room)$', '', name)

    # Remove trailing "Open" if it somehow remains
    name = re.sub(r'\s+Open\s*$', '', name)

    # Normalize whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    address = re.sub(r'\s+', ' ', address).strip()

    # Only add if we have valid data
    if name and address and len(name) > 5:
        cleaned_locations.append({
            "name": name,
            "address": address,
            "phone": phone
        })

print(f"After cleaning: {len(cleaned_locations)} locations")

# Save cleaned data
output_file = "/Volumes/X10 Pro/Roscoe/json-files/chi_saint_joseph_locations.json"
with open(output_file, 'w') as f:
    json.dump(cleaned_locations, f, indent=2, ensure_ascii=False)

print(f"Cleaned data saved to: {output_file}")

# Show samples
print("\nFirst 10 cleaned locations:")
for i, loc in enumerate(cleaned_locations[:10], 1):
    print(f"\n{i}. {loc['name']}")
    print(f"   Address: {loc['address']}")

print(f"\nTotal: {len(cleaned_locations)} CHI Saint Joseph locations")
