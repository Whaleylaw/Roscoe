#!/usr/bin/env python3
"""
Clean medical_providers.json by removing entries marked with DELETE.
"""

import json
import re
from pathlib import Path


def clean_medical_providers():
    """Remove DELETE marked entries from medical_providers.json."""

    input_file = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/medical_providers.json")

    print("Reading medical_providers.json...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Original size: {len(content)} characters")

    # Find DELETE markers
    delete_count = len(re.findall(r'DELETE', content))
    print(f"Found {delete_count} DELETE markers\n")

    # Remove DELETE text inline first
    content_no_delete_text = re.sub(r',?\s*DELETE\s*', '', content)

    # Try to parse
    try:
        data = json.loads(content_no_delete_text)
        print(f"✓ Parsed successfully")
        print(f"Total providers: {len(data)}")

        # Now filter out any entries that might still be problematic
        # or that we want to exclude
        cleaned_data = []

        for provider in data:
            name = provider.get('name', '')

            # Skip if name contains indicators of bad data
            if not name or name.strip() == '':
                continue

            # Skip obvious bad entries
            if 'please delete' in name.lower():
                print(f"  Skipping: {name}")
                continue

            # Skip Baptist Health Blvd entries (addresses, not facilities)
            if '3000 Baptist Health Blvd' in name:
                print(f"  Skipping: {name}")
                continue

            cleaned_data.append(provider)

        print(f"\nAfter cleaning: {len(cleaned_data)} providers")
        print(f"Removed: {len(data) - len(cleaned_data)} entries")

        # Save
        output_file = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/medical_providers_FINAL.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved to: {output_file.name}")

        # Show summary
        with_parent = len([p for p in cleaned_data if p.get('attributes', {}).get('parent_system')])
        without_parent = len(cleaned_data) - with_parent

        print(f"\nBreakdown:")
        print(f"  With health system: {with_parent}")
        print(f"  Independent: {without_parent}")

        print(f"\n✅ Clean combined provider list created!")

    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"Error at position {e.pos}")
        print(f"Context: {content_no_delete_text[max(0, e.pos-100):e.pos+100]}")


if __name__ == "__main__":
    clean_medical_providers()
