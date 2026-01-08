#!/usr/bin/env python3
"""
Generate Facility and Location entity files from parsed hierarchy.

Creates:
- facilities.json (all Facility entities including independent)
- locations.json (all Location entities including independent)
- hierarchy_relationships.json (mapping file)
"""

import json
from pathlib import Path


def generate_entity_files():
    """Generate Facility and Location JSON files."""

    # Load parsed hierarchy (from health systems)
    with open("/Volumes/X10 Pro/Roscoe/parsed_hierarchy.json") as f:
        parsed_data = json.load(f)

    # Load master provider list to get independent providers
    with open("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities/medical_providers.json") as f:
        master_providers = json.load(f)

    print("="*70)
    print("GENERATING FACILITY AND LOCATION FILES")
    print("="*70)
    print()

    facilities = []
    locations = []
    facility_count = 0
    location_count = 0

    # Process health system facilities/locations
    print("Processing health system facilities...")

    for system_data in parsed_data:
        system_name = system_data['system']

        for facility_data in system_data['facilities']:
            facility_name = facility_data['name']
            facility_locations = facility_data['locations']

            # Create Facility entity
            facility = {
                'card_type': 'entity',
                'entity_type': 'Facility',
                'name': facility_name,
                'attributes': {
                    'parent_system': system_name,
                    'location_count': len(facility_locations),

                    # Records request fields (null for now)
                    'records_request_method': None,
                    'records_request_url': None,
                    'records_request_address': None,
                    'records_request_fax': None,
                    'records_request_phone': None,
                    'records_request_notes': None,

                    'billing_request_method': None,
                    'billing_request_address': None,
                    'billing_request_phone': None,

                    'facility_type': None,
                    'specialty': None,
                    'main_phone': None,
                    'website': None,

                    'source': 'health_system_roster',
                    'validation_state': 'unverified'
                },
                'source_id': f"facility_{facility_count}",
                'source_file': 'hierarchy_outline'
            }

            facilities.append(facility)
            facility_count += 1

            # Create Location entities for this facility
            for loc_data in facility_locations:
                location = {
                    'card_type': 'entity',
                    'entity_type': 'Location',
                    'name': loc_data['name'],
                    'attributes': {
                        'address': loc_data.get('address', ''),
                        'phone': loc_data.get('phone', ''),

                        # Parse city, state, zip from address if possible
                        'city': None,
                        'state': None,
                        'zip': None,

                        'location_type': None,
                        'specialty': None,

                        'parent_facility': facility_name,
                        'parent_system': system_name,

                        # Records request (location-level - rare)
                        'records_request_method': None,
                        'records_request_url': None,
                        'records_request_address': None,
                        'records_request_fax': None,
                        'records_request_phone': None,
                        'records_request_notes': None,

                        'source': 'health_system_roster',
                        'validation_state': 'unverified'
                    },
                    'source_id': f"location_{location_count}",
                    'source_file': 'hierarchy_outline'
                }

                locations.append(location)
                location_count += 1

    print(f"  Health system facilities: {facility_count}")
    print(f"  Health system locations: {location_count}")
    print()

    # Process independent providers
    print("Processing independent providers...")

    independent_providers = [p for p in master_providers
                           if not p.get('attributes', {}).get('parent_system')
                           or p.get('attributes', {}).get('parent_system') == 'Independent']

    print(f"  Independent providers: {len(independent_providers)}")

    independent_facility_count = 0
    independent_location_count = 0

    for provider in independent_providers:
        provider_name = provider['name']
        provider_attrs = provider.get('attributes', {})

        # Create Facility (conceptual entity)
        facility = {
            'card_type': 'entity',
            'entity_type': 'Facility',
            'name': provider_name,
            'attributes': {
                'parent_system': None,  # Independent
                'location_count': 1,  # Most independent have 1 location

                'records_request_method': None,
                'records_request_url': None,
                'records_request_address': None,
                'records_request_fax': None,
                'records_request_phone': None,
                'records_request_notes': None,

                'billing_request_method': None,
                'billing_request_address': None,
                'billing_request_phone': None,

                'facility_type': provider_attrs.get('provider_type'),
                'specialty': provider_attrs.get('specialty'),
                'main_phone': provider_attrs.get('phone'),
                'website': None,

                'source': provider.get('source_file', 'case_data'),
                'validation_state': 'unverified'
            },
            'source_id': f"facility_{facility_count + independent_facility_count}",
            'source_file': provider.get('source_file', 'case_data')
        }

        facilities.append(facility)
        independent_facility_count += 1

        # Create Location (physical location)
        # For standalone providers, location name = facility name + " - Main Office"
        location = {
            'card_type': 'entity',
            'entity_type': 'Location',
            'name': f"{provider_name} - Main Office",
            'attributes': {
                'address': provider_attrs.get('address', ''),
                'phone': provider_attrs.get('phone', ''),
                'email': provider_attrs.get('email'),
                'fax': provider_attrs.get('fax'),

                'city': None,
                'state': None,
                'zip': None,

                'location_type': 'main_office',
                'specialty': provider_attrs.get('specialty'),

                'parent_facility': provider_name,
                'parent_system': None,  # Independent

                'records_request_method': None,
                'records_request_url': None,
                'records_request_address': provider_attrs.get('address'),  # Default to location address
                'records_request_fax': provider_attrs.get('fax'),
                'records_request_phone': provider_attrs.get('phone'),
                'records_request_notes': None,

                'source': provider.get('source_file', 'case_data'),
                'validation_state': 'unverified'
            },
            'source_id': f"location_{location_count + independent_location_count}",
            'source_file': provider.get('source_file', 'case_data')
        }

        locations.append(location)
        independent_location_count += 1

    print(f"  Independent facilities: {independent_facility_count}")
    print(f"  Independent locations: {independent_location_count}")
    print()

    # Save files
    print("="*70)
    print("SAVING ENTITY FILES")
    print("="*70)
    print()

    facilities_file = Path("/Volumes/X10 Pro/Roscoe/json-files/hierarchy/facilities.json")
    facilities_file.parent.mkdir(parents=True, exist_ok=True)

    with open(facilities_file, 'w', encoding='utf-8') as f:
        json.dump(facilities, f, indent=2, ensure_ascii=False)

    print(f"✓ facilities.json: {len(facilities)} entities")
    print(f"    Health systems: {facility_count}")
    print(f"    Independent: {independent_facility_count}")

    locations_file = Path("/Volumes/X10 Pro/Roscoe/json-files/hierarchy/locations.json")

    with open(locations_file, 'w', encoding='utf-8') as f:
        json.dump(locations, f, indent=2, ensure_ascii=False)

    print(f"\n✓ locations.json: {len(locations)} entities")
    print(f"    Health systems: {location_count}")
    print(f"    Independent: {independent_location_count}")

    # Generate hierarchy relationships
    relationships = {
        'location_to_facility': [],
        'facility_to_health_system': []
    }

    # Location → Facility relationships
    for location in locations:
        parent_fac = location['attributes'].get('parent_facility')
        if parent_fac:
            relationships['location_to_facility'].append({
                'location': location['name'],
                'facility': parent_fac
            })

    # Facility → HealthSystem relationships
    for facility in facilities:
        parent_sys = facility['attributes'].get('parent_system')
        if parent_sys:
            relationships['facility_to_health_system'].append({
                'facility': facility['name'],
                'health_system': parent_sys
            })

    relationships_file = Path("/Volumes/X10 Pro/Roscoe/json-files/hierarchy/hierarchy_relationships.json")

    with open(relationships_file, 'w', encoding='utf-8') as f:
        json.dump(relationships, f, indent=2, ensure_ascii=False)

    print(f"\n✓ hierarchy_relationships.json")
    print(f"    Location → Facility: {len(relationships['location_to_facility'])}")
    print(f"    Facility → HealthSystem: {len(relationships['facility_to_health_system'])}")

    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTotal Facilities: {len(facilities)}")
    print(f"Total Locations: {len(locations)}")
    print()
    print("Files created:")
    print(f"  - {facilities_file}")
    print(f"  - {locations_file}")
    print(f"  - {relationships_file}")

    print()
    print("✅ Entity files generated!")


if __name__ == "__main__":
    generate_entity_files()
