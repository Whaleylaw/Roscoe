#!/usr/bin/env python3
"""
Reclassify Directory Entries

This script:
1. Reads all directory entries
2. Classifies them into specific entity types
3. Moves classified entries to their appropriate JSON files
4. Keeps truly unknown entries in directory_entries.json
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Base paths
JSON_FILES = Path("/Volumes/X10 Pro/Roscoe/json-files")
ENTITIES_DIR = JSON_FILES / "memory-cards" / "entities"


# ============================================================================
# Classification Patterns
# ============================================================================

# Medical provider patterns - comprehensive list
MEDICAL_PATTERNS = [
    # Core medical terms
    'chiropractic', 'chiropractor', 'hospital', 'medical center', 'medical group',
    'clinic', 'physical therapy', ' pt ', 'orthopedic', 'orthopaedic', 'neurology',
    'neurological', 'pain management', 'spine', 'imaging', 'radiology', 'radiologist',
    'mri', 'ct scan', 'x-ray', 'xray', 'ems', 'ambulance', 'urgent care', 'emergency',
    'surgery center', 'surgical', 'physician', 'md,', 'md ', ', md', 'd.o.', ', do ',
    'dpt', 'pharma', 'diagnostic', 'pathology', 'anesthesia', 'cardiology', 'cardio',
    'pulmonology', 'pulmon', 'gastro', 'dermatology', 'dermat', 'psychiatr', 'psych',
    'oncology', 'oncol', 'urology', 'urol', 'ophthalmolog', 'optometr', 'dentist',
    'dental', 'oral surgery', 'podiatr', 'wound care', 'infusion', 'dialysis',
    'hospice', 'nursing home', 'skilled nursing', 'acute care', 'wellness center',
    'recovery center', 'treatment center', 'rehab', 'rehabilitation', 'therapeut',
    
    # Hospital/health system names
    'baptist health', 'norton', 'uofl health', 'jewish hospital', 'st. ', 'saint ',
    'ascension', 'bon secours', 'kindred', 'select specialty', 'chi ', 'arh ',
    'deaconess', 'king\'s daughters', 'mercy health', 'uk health', 'va hospital',
    'veterans hospital', 'community hospital', 'regional hospital', 'regional medical',
    'ephraim mcdowell', 'harlan arh', 'hazard arh', 'clark memorial', 'floyd memorial',
    'jennie stuart', 'methodist', 'memorial hospital', 'general hospital',
    
    # Specific medical specialties/types
    'primary care', 'family medicine', 'internal medicine', 'pediatric', 'ob/gyn',
    'obgyn', 'gynecolog', 'ear, nose', 'ent ', 'allergy', 'immunology', 'endocrin',
    'rheumatolog', 'nephrol', 'hematolog', 'infectious', 'vascular', 'plastic surgery',
    'hand surgery', 'foot ', 'ankle ', 'knee ', 'shoulder ', 'sports medicine',
    'occupational therapy', 'speech therapy', 'home health', 'home care',
    
    # Chiropractic variations
    'chiro ', ' chiro', 'back & spine', 'back and spine', 'spinal', 'adjustment',
    
    # Pain/injury centers
    'pain center', 'pain institute', 'pain clinic', 'injury center', 'injury care',
    'accident care', 'accident & injury', 'accident and injury', 'trauma',
    
    # Diagnostic facilities
    'lab ', 'laboratory', 'bloodwork', 'testing center', 'screening',
    
    # Therapy types
    'physiotherapy', 'athletic train', 'biomechan', 'kinesio',
    
    # Healthcare companies/brands
    'athletico', 'kort ', 'benchmark', 'concentra', 'fast pace', 'med express',
    'patient first', 'carespot', 'minit clinic', 'minute clinic',
    
    # Additional patterns
    'healthcare', 'health care', 'medical practice', 'medical associates',
    'physicians group', 'doctors ', 'specialties', 'specialists',
    
    # Second pass patterns (to catch more)
    'health center', 'health system', 'neuro', ' rx', 'pharmacy', 
    'women\'s health', 'air evac', 'air ambulance', 'medical response', 'amr ',
    'family health', 'eye dr', 'eye institute', 'oral-maxillo', 'neuroscience',
    'health and wellness', 'express care', 'direct care', 'directcare',
    'family services', '1st response', 'first response', 'aptiva health',
    'bracing', 'prosthetic', 'orthotics', 'massage', 'pain relief',
    'adult & child', 'child health', 'behavioral health', 'mental health',
    
    # Third pass - more health/medical
    'biokinetics', 'discovery health', 'integrated health', 'holzer',
    'lifestance', 'teamhealth', 'uc health', 'us health', 'owensboro health',
    'pearl medical', 'southern medical', 'ophtalmology', 'ophthalmology',
    'health first', 'medical services', 'family care', 'optimal living',
    'multicare', 'medical partners', 'health group',
    
    # Fourth pass - specific names
    ' md', 'r t md', 'kort', 'ky one health', 'ambulatory', 'sharecare',
]

# Doctor name patterns (Dr. prefix)
DOCTOR_PATTERNS = [
    r'^dr\.\s',
    r'^dr\s',
]

# Insurance company patterns
INSURANCE_PATTERNS = [
    'insurance', 'mutual insurance', 'indemnity', 'casualty', 'underwriter',
    'assurance', 'allstate', 'state farm', 'geico', 'progressive', 'farmers insurance',
    'liberty mutual', 'nationwide', 'usaa', 'travelers', 'hartford', 'safeco',
    'amica', 'erie insurance', 'auto-owners', 'american family', 'mercury insurance',
    'esurance', 'the general', 'direct auto', 'shelter insurance', 'root insurance',
    'metlife auto', 'kemper', 'bristol west', 'national general', 'dairyland',
    'safe auto', 'great west', 'old republic', 'ocean harbor', 'falcon insurance',
    'founders insurance', 'canal insurance', 'cherokee insurance', 'acuity',
    'westfield', 'selective insurance', 'encova', 'federated mutual', 'emc insurance',
    'iat insurance', 'intact insurance', 'mohave', 'repwest', 'gainsco',
    'wayne insurance', 'central insurance', 'standard fire', 'country way',
    'diversified insurance', 'hagerty', 'lincoln heritage', 'bankers life',
    'americo life', 'monumental life', 'reserve national', 'sonnenberg mutual',
    'accident fund', 'klc insurance', 'charles taylor',
]

# Health insurance / Lien holders (subrogation)
LIEN_HOLDER_PATTERNS = [
    'aetna', 'anthem', 'bcbs', 'blue cross', 'blue shield', 'bluecross', 'blueshield',
    'cigna', 'humana', 'united health', 'unitedhealthcare', 'molina', 'centene', 
    'wellcare', 'ambetter', 'oscar', 'caresource', 'passport', 'medicaid', 'medicare',
    'tricare', 'champva', 'premera', 'subrogation', 'collection', 'zipliens', 'carelon',
    'healthy horizons', 'community plan', 'health plan', 'erisa', 'credit agency',
]

# Law firm / Attorney patterns
ATTORNEY_PATTERNS = [
    'law firm', 'law group', 'law office', 'attorney', 'lawyers', ', esq', 'esq.',
    'pllc', 'legal', 'litigation', 'trial lawyer', 'law, psc', ', psc',
    # Known defense firms and law firm name patterns
    'boehl, stopher', 'cowles & thompson', 'ellis & badenhausen', 'lewis, brisbois',
    'reminger', 'sitlinger law', 'soergel, abell', 'tyson, schwab', ', llp', 'lpa',
    'phillips, parker', 'mcintyre, gilligan', 'merk & gile', 'dettman and associates',
    'migliore & associates', 'belanger & associates', 'dsj & associates',
]

# Court patterns
COURT_PATTERNS = [
    'circuit court', 'district court', 'court of ', 'superior court', 'county court',
    'family court', 'probate court', 'bankruptcy court', 'court of justice',
]

# Government/EMS patterns (will map to MedicalProvider for EMS, Organization for others)
GOVERNMENT_PATTERNS = [
    'county', 'city of ', 'state of ', 'department of', 'sheriff', 'police',
    'commonwealth', 'federal', 'detention', 'public school', 'fire department',
    'workers\' claims', 'motor vehicles', 'transit authority', 'lmpd', 'jcps',
]

# Trucking/Transportation (potential defendants)
TRUCKING_PATTERNS = [
    'trucking', 'truck group', 'express trucking', 'transport', 'logistics',
    'freight', 'hauling', 'carrier', 'fleet',
]

# EMS patterns (subset of government, but should be MedicalProvider)
EMS_PATTERNS = [
    ' ems', 'ems ', 'ambulance', 'fire/ems', 'fire ems', 'paramedic',
]

# Vendor patterns
VENDOR_PATTERNS = {
    'towing': ['towing', 'tow ', 'wrecker', 'roadside'],
    'court_reporting': ['reporting', 'court reporter', 'deposition', 'stenograph', 'ccr,'],
    'investigation': ['investigation', 'investigator', 'investigative', 'collision investigation'],
    'moving': ['moving', 'movers', 'relocation'],
    'records_retrieval': ['medicopy', 'verisma', 'mro', 'ciox', 'healthport', 'vital chart', 'vrc companies',
                          'chartswap', 'datavant', 'cardone record', 'healthmark', 'scanstat'],
    'process_server': ['process server', 'service of process'],
    'claims_services': ['gallagher bassett', 'dynamic claims', 'rental claim', 'spectrum damage', 
                        'claims department', 'claims service'],
    'litigation_funding': ['barrister capital', 'kentuckiana capital', 'litigation fund'],
    'mediation': ['mediation', 'mediator', 'distinguished neutrals', 'arbitrat'],
    'legal_software': ['evenup', 'casepacer', 'litify'],
    'medical_equipment': ['medequip', 'orthofix', 'prosthetic', 'bracing'],
}


# ============================================================================
# Classification Functions
# ============================================================================

def classify_entry(name: str) -> Tuple[str, str]:
    """
    Classify a directory entry by name.
    Returns (entity_type, subtype/vendor_type or None)
    """
    name_lower = name.lower()
    
    # --- Priority 1: Vendor types (check first to avoid false positives) ---
    for vendor_type, patterns in VENDOR_PATTERNS.items():
        for p in patterns:
            if p in name_lower:
                return ('Vendor', vendor_type)
    
    # --- Priority 2: Courts (specific pattern) ---
    for p in COURT_PATTERNS:
        if p in name_lower:
            return ('Court', None)
    
    # --- Priority 3: EMS (medical provider, not government) ---
    for p in EMS_PATTERNS:
        if p in name_lower:
            return ('MedicalProvider', 'ems')
    
    # --- Priority 4: Medical Providers ---
    # Check Dr. prefix first
    for pattern in DOCTOR_PATTERNS:
        if re.match(pattern, name_lower):
            return ('MedicalProvider', None)
    
    # Check medical patterns
    for p in MEDICAL_PATTERNS:
        if p in name_lower:
            return ('MedicalProvider', None)
    
    # --- Priority 5: Lien Holders (health insurance, subrogation) ---
    for p in LIEN_HOLDER_PATTERNS:
        if p in name_lower:
            return ('LienHolder', None)
    
    # --- Priority 6: Auto Insurers ---
    for p in INSURANCE_PATTERNS:
        if p in name_lower:
            return ('Insurer', None)
    
    # --- Priority 7: Attorneys/Law Firms ---
    for p in ATTORNEY_PATTERNS:
        if p in name_lower:
            return ('Attorney', None)
    
    # --- Priority 8: Government (non-EMS) ---
    for p in GOVERNMENT_PATTERNS:
        if p in name_lower:
            return ('Organization', 'government')
    
    # --- Priority 9: Trucking/Transportation (potential defendants) ---
    for p in TRUCKING_PATTERNS:
        if p in name_lower:
            return ('Organization', 'trucking')
    
    # --- Default: Unknown (stays as DirectoryEntry) ---
    return ('DirectoryEntry', None)


def load_json(path: Path) -> List[dict]:
    """Load JSON file, return empty list if not found."""
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return []


def save_json(path: Path, data: List[dict]):
    """Save data to JSON file with pretty formatting."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved {len(data)} entries to {path.name}")


# ============================================================================
# Main Processing
# ============================================================================

def main():
    print("=" * 60)
    print("RECLASSIFYING DIRECTORY ENTRIES")
    print("=" * 60)
    
    # Load directory entries
    dir_entries_path = ENTITIES_DIR / "directory_entries.json"
    dir_entries = load_json(dir_entries_path)
    print(f"\nLoaded {len(dir_entries)} directory entries")
    
    # Load existing entity files
    existing_files = {
        'MedicalProvider': load_json(ENTITIES_DIR / "medical_providers.json"),
        'Insurer': load_json(ENTITIES_DIR / "insurers.json"),
        'LienHolder': load_json(ENTITIES_DIR / "lienholders.json"),
        'Attorney': load_json(ENTITIES_DIR / "attorneys.json"),
        'Court': [],  # New file
        'Vendor': [],  # New file
        'Organization': [],  # New file for government entities
    }
    
    # Track existing names to avoid duplicates
    existing_names = {}
    for entity_type, entries in existing_files.items():
        existing_names[entity_type] = {e['name'].lower() for e in entries}
    
    # Classify directory entries
    classified = {
        'MedicalProvider': [],
        'Insurer': [],
        'LienHolder': [],
        'Attorney': [],
        'Court': [],
        'Vendor': [],
        'Organization': [],
        'DirectoryEntry': [],  # Remains unknown
    }
    
    stats = {k: 0 for k in classified.keys()}
    
    for entry in dir_entries:
        name = entry.get('name', '')
        entity_type, subtype = classify_entry(name)
        
        # Skip if already exists in target entity file
        name_lower = name.lower()
        if entity_type in existing_names and name_lower in existing_names[entity_type]:
            # Already exists, keep as DirectoryEntry to not create duplicate
            classified['DirectoryEntry'].append(entry)
            stats['DirectoryEntry'] += 1
            continue
        
        # Create new entry for target type
        new_entry = {
            'card_type': 'entity',
            'entity_type': entity_type,
            'name': name,
            'attributes': entry.get('attributes', {}).copy(),
            'source_id': entry.get('source_id'),
            'source_file': 'directory.json',
        }
        
        # Add subtype info
        if entity_type == 'Vendor' and subtype:
            new_entry['attributes']['vendor_type'] = subtype
        elif entity_type == 'MedicalProvider' and subtype == 'ems':
            new_entry['attributes']['specialty'] = 'ems'
        elif entity_type == 'Organization' and subtype == 'government':
            new_entry['attributes']['org_type'] = 'government'
        
        classified[entity_type].append(new_entry)
        stats[entity_type] += 1
    
    # Print classification summary
    print("\n" + "=" * 60)
    print("CLASSIFICATION SUMMARY")
    print("=" * 60)
    for entity_type, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {entity_type}: {count}")
    
    # Merge and save files
    print("\n" + "=" * 60)
    print("SAVING ENTITY FILES")
    print("=" * 60)
    
    # Medical Providers - merge new with existing
    medical_providers = existing_files['MedicalProvider'] + classified['MedicalProvider']
    save_json(ENTITIES_DIR / "medical_providers.json", medical_providers)
    
    # Insurers
    insurers = existing_files['Insurer'] + classified['Insurer']
    save_json(ENTITIES_DIR / "insurers.json", insurers)
    
    # Lien Holders
    lienholders = existing_files['LienHolder'] + classified['LienHolder']
    save_json(ENTITIES_DIR / "lienholders.json", lienholders)
    
    # Attorneys
    attorneys = existing_files['Attorney'] + classified['Attorney']
    save_json(ENTITIES_DIR / "attorneys.json", attorneys)
    
    # Courts (new file)
    save_json(ENTITIES_DIR / "courts.json", classified['Court'])
    
    # Vendors (new file)
    save_json(ENTITIES_DIR / "vendors.json", classified['Vendor'])
    
    # Organizations (new file)
    save_json(ENTITIES_DIR / "organizations.json", classified['Organization'])
    
    # Directory Entries (remaining unknowns)
    save_json(ENTITIES_DIR / "directory_entries.json", classified['DirectoryEntry'])
    
    # Print detailed breakdown of what was classified
    print("\n" + "=" * 60)
    print("NEWLY CLASSIFIED ENTRIES BY TYPE")
    print("=" * 60)
    
    for entity_type in ['MedicalProvider', 'Insurer', 'LienHolder', 'Attorney', 'Court', 'Vendor', 'Organization']:
        if classified[entity_type]:
            print(f"\n=== {entity_type} ({len(classified[entity_type])}) ===")
            for entry in sorted(classified[entity_type], key=lambda x: x['name'])[:30]:
                subtype = ""
                if 'vendor_type' in entry.get('attributes', {}):
                    subtype = f" [{entry['attributes']['vendor_type']}]"
                elif 'specialty' in entry.get('attributes', {}):
                    subtype = f" [{entry['attributes']['specialty']}]"
                elif 'org_type' in entry.get('attributes', {}):
                    subtype = f" [{entry['attributes']['org_type']}]"
                print(f"  - {entry['name']}{subtype}")
            if len(classified[entity_type]) > 30:
                print(f"  ... and {len(classified[entity_type]) - 30} more")
    
    # Show sample of remaining unknowns
    print("\n" + "=" * 60)
    print(f"REMAINING UNKNOWNS ({len(classified['DirectoryEntry'])})")
    print("=" * 60)
    unknowns = classified['DirectoryEntry']
    for entry in sorted(unknowns, key=lambda x: x['name'])[:50]:
        print(f"  - {entry['name']}")
    if len(unknowns) > 50:
        print(f"  ... and {len(unknowns) - 50} more")


if __name__ == "__main__":
    main()
