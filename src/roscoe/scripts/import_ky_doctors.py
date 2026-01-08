#!/usr/bin/env python3
"""
Import Kentucky Licensed Doctors from state directory.

Creates Doctor entity cards from KY medical board data.
Imports 20,000+ doctors with license numbers, specialties, etc.
"""

import json
import re
from pathlib import Path
from collections import defaultdict


def normalize_doctor_name(name: str) -> str:
    """
    Normalize doctor name to standard format.

    Examples:
    - "Tracy L  Courtney M.D." → "Dr. Tracy L. Courtney"
    - "John Smith D.O." → "Dr. John Smith"
    """
    # Remove credentials suffix
    name = re.sub(r'\s*(M\.?D\.?|D\.?O\.?|D\.?C\.?)$', '', name, flags=re.IGNORECASE)

    # Clean up extra spaces
    name = re.sub(r'\s+', ' ', name).strip()

    # Add "Dr." prefix if not present
    if not name.startswith("Dr."):
        name = f"Dr. {name}"

    return name


def extract_credentials(original_name: str) -> str:
    """Extract credentials from name (M.D., D.O., etc.)"""
    match = re.search(r'(M\.?D\.?|D\.?O\.?|D\.?C\.?)$', original_name, re.IGNORECASE)
    if match:
        cred = match.group(1).upper()
        # Normalize to standard format
        if 'MD' in cred:
            return 'MD'
        elif 'DO' in cred:
            return 'DO'
        elif 'DC' in cred:
            return 'DC'
    return ''


def normalize_specialty(specialty: str) -> str:
    """Normalize specialty names to standard terms."""
    if not specialty or specialty == "None":
        return ""

    specialty_lower = specialty.lower()

    # Map to standard specialties
    mappings = {
        'orthopedic': ['orthopedic', 'orthopaedic', 'orthopedics'],
        'neurology': ['neurology', 'neurological'],
        'pain management': ['pain management', 'pain medicine'],
        'radiology': ['diagnostic radiology', 'radiology'],
        'emergency medicine': ['emergency medicine', 'emergency'],
        'family medicine': ['family medicine', 'family practice'],
        'internal medicine': ['internal medicine'],
        'physical therapy': ['physical therapy', 'rehabilitation'],
        'chiropractic': ['chiropractic'],
        'psychiatry': ['psychiatry', 'psychiatric'],
        'surgery': ['surgery', 'surgical'],
    }

    for standard, variants in mappings.items():
        if any(v in specialty_lower for v in variants):
            return standard

    return specialty.strip()


def safe_str(value) -> str:
    """Safely convert any value to string, handling NaN and None."""
    if value is None or str(value) == 'nan':
        return ""
    return str(value).strip()


def convert_doctor_to_entity(entry: dict) -> dict:
    """Convert doctor directory entry to entity card."""
    original_name = safe_str(entry.get("Name", ""))
    if not original_name:
        return None

    # Normalize name
    name = normalize_doctor_name(original_name)
    credentials = extract_credentials(original_name)

    # Extract specialty
    specialty = normalize_specialty(safe_str(entry.get("*Area of Practice", "")))

    # Build address
    address_parts = []
    addr1 = safe_str(entry.get("Address", ""))
    if addr1:
        address_parts.append(addr1)
    addr2 = safe_str(entry.get("City, State, Zip", ""))
    if addr2:
        address_parts.append(addr2)
    address = ", ".join(address_parts) if address_parts else ""

    # Extract phone
    phone = safe_str(entry.get("Phone", ""))

    return {
        "card_type": "entity",
        "entity_type": "Doctor",
        "name": name,
        "attributes": {
            "specialty": specialty,
            "credentials": credentials,
            "license_number": safe_str(entry.get("License", "")),
            "license_status": safe_str(entry.get("Status", "")),
            "practice_county": safe_str(entry.get("Practice County", "")),
            "practice_type": safe_str(entry.get("Type of Practice", "")),
            "phone": phone,
            "email": "",
            "address": address,
            "npi": "",
            "medical_school": safe_str(entry.get("Medical School", "")),
            "year_graduated": safe_str(entry.get("Year Graduated", ""))
        },
        "source_id": "ky_medical_board",
        "source_file": "ky_doctors_20251228_172247.json"
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--status', type=str, default='all',
                       choices=['all', 'active', 'inactive'],
                       help='Which doctors to import (default: all)')
    args = parser.parse_args()

    input_file = Path("/Volumes/X10 Pro/Roscoe/scripts/output/ky_doctors_20251228_172247.json")
    output_file = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/doctors.json")

    print("=" * 80)
    print("IMPORTING KENTUCKY LICENSED DOCTORS")
    print("=" * 80)
    print()

    with open(input_file) as f:
        entries = json.load(f)

    print(f"Total entries in directory: {len(entries)}")
    print()

    # Convert to entity cards
    doctors = []
    skipped = 0

    status_counts = defaultdict(int)

    for entry in entries:
        status = entry.get("Status", "")
        status_counts[status] += 1

        # Filter by status if requested
        if args.status == 'active' and 'Active' not in status:
            skipped += 1
            continue
        elif args.status == 'inactive' and 'Inactive' not in status:
            skipped += 1
            continue

        card = convert_doctor_to_entity(entry)
        if card:
            doctors.append(card)
        else:
            skipped += 1

    print("Status breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print()

    print(f"Converted {len(doctors)} doctors to entity cards")
    if skipped:
        print(f"Skipped: {skipped} (based on filter: {args.status})")
    print()

    # Sample specialty distribution
    specialty_counts = defaultdict(int)
    for doc in doctors:
        spec = doc["attributes"].get("specialty", "")
        if spec:
            specialty_counts[spec] += 1

    print("Top specialties:")
    for spec, count in sorted(specialty_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {spec}: {count}")
    print()

    # Save (REPLACE existing doctors.json)
    with open(output_file, 'w') as f:
        json.dump(doctors, f, indent=2)

    print(f"✅ Replaced {output_file}")
    print(f"   Total doctors: {len(doctors)}")
    print()

    if args.status == 'all':
        print("💡 Note: Imported ALL doctors (active and inactive)")
        print("   Inactive doctors may be relevant for old medical records")


if __name__ == "__main__":
    main()
