#!/usr/bin/env python3
"""
Consolidate all scraped attorney data and merge with existing attorneys.json.
Deduplicates, normalizes, and updates incomplete records.
"""

import json
import os
import re

def normalize_name(name):
    """Normalize attorney name for matching."""
    # Remove titles and suffixes for comparison
    name = re.sub(r',?\s+(Esq\.|Jr\.|Sr\.|III|II)\.?', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip()
    return name.lower()

def normalize_phone(phone):
    """Normalize phone number."""
    if not phone:
        return ""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone

def main():
    base_dir = "/Volumes/X10 Pro/Roscoe/json-files"

    print("Merging attorney data from all sources...")
    print("=" * 60)

    # Load all batch files
    batch_files = [f"attorneys_batch_{i}.json" for i in range(1, 5)]

    scraped_attorneys = []

    for batch_file in batch_files:
        filepath = os.path.join(base_dir, batch_file)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                scraped_attorneys.extend(data)
                print(f"Loaded {len(data)} attorneys from {batch_file}")
        else:
            print(f"⚠️  {batch_file} not found")

    print(f"\nTotal scraped: {len(scraped_attorneys)} attorneys")

    # Deduplicate scraped data
    seen = {}
    unique_scraped = []

    for att in scraped_attorneys:
        name = att.get('name', '')
        norm_name = normalize_name(name)

        if norm_name not in seen:
            seen[norm_name] = att
            unique_scraped.append(att)
        else:
            # If we've seen this name, update with any missing info
            existing = seen[norm_name]
            if att.get('email') and not existing.get('email'):
                existing['email'] = att['email']
            if att.get('phone') and not existing.get('phone'):
                existing['phone'] = att['phone']

    print(f"After deduplication: {len(unique_scraped)} unique attorneys")

    # Load existing attorneys.json
    existing_file = os.path.join(base_dir, "memory-cards/entities/attorneys.json")

    existing_attorneys = []
    if os.path.exists(existing_file):
        with open(existing_file, 'r') as f:
            existing_attorneys = json.load(f)
        print(f"\nLoaded {len(existing_attorneys)} existing attorneys from database")

    # Create lookup for existing attorneys by name
    existing_by_name = {}
    for att in existing_attorneys:
        name = att.get('name', '')
        norm_name = normalize_name(name)
        existing_by_name[norm_name] = att

    # Merge: Update existing records and add new ones
    updated_count = 0
    added_count = 0

    for scraped_att in unique_scraped:
        name = scraped_att.get('name', '')
        norm_name = normalize_name(name)

        if norm_name in existing_by_name:
            # Update existing record
            existing = existing_by_name[norm_name]
            updated = False

            # Update email if missing
            if scraped_att.get('email') and not existing['attributes'].get('email'):
                existing['attributes']['email'] = scraped_att['email']
                updated = True

            # Update phone if missing
            if scraped_att.get('phone') and not existing['attributes'].get('phone'):
                existing['attributes']['phone'] = normalize_phone(scraped_att['phone'])
                updated = True

            # Update firm name if missing
            if scraped_att.get('firm_name') and not existing['attributes'].get('firm_name'):
                existing['attributes']['firm_name'] = scraped_att['firm_name']
                updated = True

            if updated:
                updated_count += 1

        else:
            # Add new attorney
            new_attorney = {
                "card_type": "entity",
                "entity_type": "Attorney",
                "name": name,
                "attributes": {
                    "role": "defense_counsel",  # Default for these firms
                    "firm_name": scraped_att.get('firm_name', ''),
                    "phone": normalize_phone(scraped_att.get('phone', '')),
                    "email": scraped_att.get('email', ''),
                },
                "source_id": "law_firm_scrape_2025",
                "source_file": "attorney_deep_research"
            }

            # Add additional info if available
            if scraped_att.get('additional_info'):
                new_attorney['notes'] = scraped_att['additional_info']

            existing_attorneys.append(new_attorney)
            added_count += 1

    print(f"\n{'=' * 60}")
    print(f"Merge Results:")
    print(f"  Updated existing records: {updated_count}")
    print(f"  Added new attorneys: {added_count}")
    print(f"  Total in database: {len(existing_attorneys)}")

    # Save updated attorneys.json
    output_file = os.path.join(base_dir, "memory-cards/entities/attorneys.json")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(existing_attorneys, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated attorneys.json saved to: {output_file}")

    # Also save a backup
    backup_file = os.path.join(base_dir, "memory-cards/entities/attorneys_backup_pre_merge.json")
    if os.path.exists(existing_file) and not os.path.exists(backup_file):
        import shutil
        shutil.copy(existing_file, backup_file)
        print(f"Backup created: {backup_file}")

    # Print statistics
    print(f"\n{'=' * 60}")
    print("Statistics:")
    print(f"  Total attorneys in database: {len(existing_attorneys)}")

    with_email = sum(1 for a in existing_attorneys if a['attributes'].get('email'))
    with_phone = sum(1 for a in existing_attorneys if a['attributes'].get('phone'))
    with_firm = sum(1 for a in existing_attorneys if a['attributes'].get('firm_name'))

    print(f"  With email addresses: {with_email}")
    print(f"  With phone numbers: {with_phone}")
    print(f"  With firm names: {with_firm}")

    # Show sample of newly added attorneys
    if added_count > 0:
        print(f"\n{'=' * 60}")
        print("Sample of newly added attorneys (first 10):")

        # Get last N added (they're at the end)
        new_attorneys = existing_attorneys[-added_count:]

        for i, att in enumerate(new_attorneys[:10], 1):
            print(f"\n{i}. {att['name']}")
            print(f"   Firm: {att['attributes'].get('firm_name', '(not specified)')}")
            print(f"   Email: {att['attributes'].get('email', '(not available)')}")
            print(f"   Phone: {att['attributes'].get('phone', '(not available)')}")

if __name__ == "__main__":
    main()
