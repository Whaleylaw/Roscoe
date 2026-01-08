#!/usr/bin/env python3
"""
Generate Review Documents for Episode Relationship Proposals

For each processed case, creates a review document showing:
1. Existing entities in graph (the schema for this case)
2. All proposed entity mentions from episodes
3. Side-by-side for easy mapping/review

Output: One review_{case_name}.md per case

Usage:
    python -m roscoe.scripts.generate_review_docs
"""

import json
import re
from pathlib import Path
from collections import defaultdict


def normalize_name(name: str) -> str:
    """Normalize name for fuzzy matching."""
    # Remove titles and suffixes
    name = re.sub(r',?\s*(Esq\.?|Esquire|Jr\.?|Sr\.?|III|II|P\.?C\.?|PLLC|PSC|LLC|Inc\.?)$', '', name, flags=re.IGNORECASE)
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name)
    # Remove punctuation except hyphens
    name = re.sub(r'[,\.]', '', name)
    return name.strip().lower()


def normalize_attorney_name(name: str) -> str:
    """
    Normalize attorney name, handling last-name-first format and middle names.

    Examples:
    - "Whaley, Aaron Gregory" → "aaron whaley" (remove middle, handle last-first)
    - "Derek A. Harvey Jr." → "derek harvey"  (remove middle initial + suffix)
    - "Derek Anthony Harvey" → "derek harvey" (remove middle name)
    - "Sam Leffert" vs "Samuel Robert Leffert" → both become "samuel leffert"
    - "W. Bryce Koon, Esq." → "bryce koon"
    - "Dr. Wallace Huff" → "wallace huff" (remove Dr. prefix)
    """
    original = name

    # Remove "Dr." or "Dr" prefix first (before other processing)
    name = re.sub(r'^Dr\.?\s+', '', name, flags=re.IGNORECASE)

    # Handle last-name-first format BEFORE other normalization
    # But NOT if it's a suffix like "Esq", "Jr", "Sr"
    if ',' in name:
        parts = [p.strip() for p in name.split(',', 1)]  # Split only on first comma
        if len(parts) == 2:
            # Check if second part is a suffix (not a first name)
            second_part_lower = parts[1].lower().strip()
            is_suffix = any(suffix in second_part_lower for suffix in ['esq', 'jr', 'sr', 'iii', 'ii', 'iv'])

            if not is_suffix:
                # Reverse: "last, first middle" → "first middle last"
                name = f"{parts[1]} {parts[0]}"
            # else: keep as-is, let normalize_name handle suffix removal

    # Now apply standard normalization (removes suffixes, punctuation)
    name = normalize_name(name)

    # Expand common nicknames
    nickname_map = {
        'sam': 'samuel',
        'mike': 'michael',
        'bob': 'robert',
        'jim': 'james',
        'bill': 'william',
        'tom': 'thomas',
        'dave': 'david',
        'joe': 'joseph',
        'tony': 'anthony'
    }

    parts = name.split()
    if len(parts) > 0 and parts[0] in nickname_map:
        parts[0] = nickname_map[parts[0]]
        name = ' '.join(parts)

    # Remove leading initials and middle names (keep only first + last)
    # Pattern: "W. Bryce Koon" → "bryce koon"
    # Pattern: "first middle last" → "first last"
    parts = name.split()

    # Remove leading initial if present (e.g., "w bryce koon" → "bryce koon")
    if len(parts) >= 2 and len(parts[0]) == 1:
        parts = parts[1:]  # Drop the leading initial

    # Now remove middle names if we have 3+ parts
    if len(parts) == 3:
        # "first middle last" → "first last"
        name = f"{parts[0]} {parts[2]}"
    elif len(parts) > 3:
        # More than 3 parts - keep first and last
        name = f"{parts[0]} {parts[-1]}"
    else:
        # 2 or fewer parts - keep as is
        name = ' '.join(parts)

    # Final cleanup - remove any trailing punctuation
    name = name.strip().rstrip('.,;:')

    return name


def normalize_court_name(name: str) -> str:
    """
    Normalize court name, removing case numbers and variations.

    Examples:
    - "Jefferson County (25-CI-00133)" → "jefferson county"
    - "Jefferson Circuit Court" → "jefferson county circuit court"
    - "Jefferson 25-CI-00133" → "jefferson"
    """
    # Remove case numbers (pattern: digits-letters-digits)
    name = re.sub(r'\(\d+-\w+-\d+\)', '', name)
    name = re.sub(r'\d+-\w+-\d+', '', name)

    # Apply standard normalization
    name = normalize_name(name)

    return name.strip()


def normalize_hospital_name(name: str) -> str:
    """
    Normalize hospital name, handling common variations.

    Examples:
    - "UofL Health - Mary & Elizabeth Hospital" → "mary elizabeth hospital"
    - "St. Mary's Medical Center" → "mary medical center"
    - "Jewish Hospital" → "jewish hospital"
    """
    name = normalize_name(name)

    # Remove common prefixes
    name = re.sub(r'^(uofl|university of louisville|st|saint)\s+', '', name)
    name = re.sub(r'\s+(health|healthcare|medical group)\s*-?\s*', ' ', name)

    # Remove "&" and "and"
    name = re.sub(r'\s+(&|and)\s+', ' ', name)

    # Remove apostrophes
    name = re.sub(r"'s?\b", '', name)

    return name.strip()


def fuzzy_match_doctor(proposed_name: str, existing_doctors: list) -> tuple[bool, str]:
    """
    Stricter matching for doctors - requires first name match.

    Returns: (matched: bool, matched_name: str)
    """
    from rapidfuzz import fuzz

    # Normalize proposed name
    proposed_norm = normalize_attorney_name(proposed_name)
    proposed_parts = proposed_norm.split()

    if len(proposed_parts) < 2:
        # Need at least first + last name
        return False, ""

    proposed_first = proposed_parts[0]
    proposed_last = proposed_parts[-1]

    best_match = None
    best_score = 0

    for existing in existing_doctors:
        existing_norm = normalize_attorney_name(existing)
        existing_parts = existing_norm.split()

        if len(existing_parts) < 2:
            continue

        existing_first = existing_parts[0]
        existing_last = existing_parts[-1]

        # REQUIRE exact or very close first name match
        first_name_score = fuzz.ratio(proposed_first, existing_first)
        if first_name_score < 95:  # Very strict threshold for first name
            continue

        # Check last name
        last_name_score = fuzz.ratio(proposed_last, existing_last)
        if last_name_score < 90:  # Also strict for last name
            continue

        # Both names match - calculate overall score
        overall_score = (first_name_score + last_name_score) / 2

        if overall_score > best_score:
            best_score = overall_score
            best_match = existing

    if best_match and best_score >= 92:  # High threshold for final match
        return True, best_match

    return False, ""


def fuzzy_match_entity(proposed_name: str, existing_entities: list, threshold: int = 85, entity_type: str = None) -> tuple[bool, str]:
    """
    Check if proposed entity matches an existing one using fuzzy matching.

    Returns: (matched: bool, matched_name: str)
    """
    from rapidfuzz import fuzz

    # Use specialized normalization based on entity type
    if entity_type == "Court":
        proposed_norm = normalize_court_name(proposed_name)
    elif entity_type == "MedicalProvider":
        proposed_norm = normalize_hospital_name(proposed_name)
    elif entity_type == "Attorney":
        proposed_norm = normalize_attorney_name(proposed_name)
    else:
        proposed_norm = normalize_name(proposed_name)

    for existing in existing_entities:
        if entity_type == "Court":
            existing_norm = normalize_court_name(existing)
        elif entity_type == "MedicalProvider":
            existing_norm = normalize_hospital_name(existing)
        elif entity_type == "Attorney":
            existing_norm = normalize_attorney_name(existing)
        else:
            existing_norm = normalize_name(existing)

        # Exact match after normalization
        if proposed_norm == existing_norm:
            return True, existing

        # Fuzzy match
        score = fuzz.ratio(proposed_norm, existing_norm)
        if score >= threshold:
            return True, existing

        # Check if one is substring of other (for claims with IDs, hospitals)
        if len(proposed_norm) > 5 and len(existing_norm) > 5:
            if proposed_norm in existing_norm or existing_norm in proposed_norm:
                return True, existing

    return False, ""


# Known Whaley Law Firm staff (global list for matching)
WHALEY_STAFF = {
    "Aaron G. Whaley": ("Attorney", "plaintiff_counsel"),
    "Aaron Whaley": ("Attorney", "plaintiff_counsel"),
    "Aaron Gregory Whaley": ("Attorney", "plaintiff_counsel"),
    "Bryce Koon": ("Attorney", "plaintiff_counsel"),
    "W. Bryce Koon": ("Attorney", "plaintiff_counsel"),
    "Sarena Tuttle": ("CaseManager", "paralegal"),
    "Sarena M. Tuttle": ("CaseManager", "paralegal"),
    "Justin Chumbley": ("CaseManager", "case_manager"),
    "Coleen Madayag": ("CaseManager", "case_manager"),
    "Coleen Thea Madayag": ("CaseManager", "case_manager"),
    "Coleen Thea Ferry Madayag": ("CaseManager", "case_manager"),
    "Faye Gaither": ("CaseManager", "case_manager"),
    "Jessa Galosmo": ("CaseManager", "case_manager"),
    "Jessa": ("CaseManager", "case_manager"),
    "Aries Penaflor": ("CaseManager", "case_manager"),
    "Jessica Bottorff": ("CaseManager", "case_manager"),
}


def check_whaley_staff(name: str) -> tuple[bool, str, str]:
    """
    Check if name is Whaley Law Firm staff.

    Returns: (is_staff: bool, canonical_name: str, correct_type: str)
    """
    from rapidfuzz import fuzz

    name_norm = normalize_attorney_name(name)  # Use attorney normalization

    for staff_name, (entity_type, role) in WHALEY_STAFF.items():
        staff_norm = normalize_attorney_name(staff_name)

        # Exact match after normalization
        if name_norm == staff_norm:
            return True, staff_name, entity_type

        # Fuzzy match (high threshold)
        if fuzz.ratio(name_norm, staff_norm) >= 90:
            return True, staff_name, entity_type

        # Check if input is first name only and matches staff first name
        # E.g., "Sarena" matches "Sarena Tuttle"
        name_parts = name_norm.split()
        staff_parts = staff_norm.split()
        if len(name_parts) == 1 and len(staff_parts) >= 2:
            if name_parts[0] == staff_parts[0] and len(name_parts[0]) > 4:
                # First name match (require >4 chars to avoid false positives like "Amy")
                return True, staff_name, entity_type

    return False, "", ""


def load_directory_names(directory_file: Path) -> list[str]:
    """Extract all full_name entries from directory.json."""
    names = []
    with open(directory_file) as f:
        content = f.read()
        # Extract all "full_name": "..." patterns
        matches = re.findall(r'"full_name":\s*"([^"]+)"', content)
        names = [m.strip() for m in matches if m.strip()]
    return sorted(set(names))


def load_global_entities(entities_dir: Path, directory_file: Path = None) -> dict:
    """Load all entities from JSON files and directory for cross-case matching."""
    global_entities = {
        'clients': [],
        'courts': [],
        'defendants': [],
        'attorneys': [],
        'law_firms': [],
        'medical_providers': [],
        'insurers': [],
        'adjusters': [],
        'liens': [],
        'vendors': [],
        'experts': [],
        'witnesses': [],
        'mediators': [],
        'organizations': [],
        'circuit_divisions': [],
        'district_divisions': [],
        'directory_all': []  # All names from directory.json
    }

    # Load directory.json if provided
    if directory_file and directory_file.exists():
        global_entities['directory_all'] = load_directory_names(directory_file)

    # Load clients
    clients_file = entities_dir / "clients.json"
    if clients_file.exists():
        with open(clients_file) as f:
            data = json.load(f)
            global_entities['clients'] = [c['name'] for c in data]

    # Load courts
    courts_file = entities_dir / "courts.json"
    if courts_file.exists():
        with open(courts_file) as f:
            data = json.load(f)
            global_entities['courts'] = [c['name'] for c in data]

    # Load attorneys
    attorneys_file = entities_dir / "attorneys.json"
    if attorneys_file.exists():
        with open(attorneys_file) as f:
            data = json.load(f)
            global_entities['attorneys'] = [a['name'] for a in data]

    # Load law firms (including aliases)
    lawfirms_file = entities_dir / "lawfirms.json"
    if lawfirms_file.exists():
        with open(lawfirms_file) as f:
            data = json.load(f)
            # Store both names and aliases
            law_firm_names = []
            law_firm_aliases = {}  # alias -> canonical_name
            for lf in data:
                law_firm_names.append(lf['name'])
                if 'aliases' in lf:
                    for alias in lf['aliases']:
                        law_firm_aliases[alias] = lf['name']
            global_entities['law_firms'] = law_firm_names
            global_entities['law_firm_aliases'] = law_firm_aliases

    # Load medical providers
    providers_file = entities_dir / "medical_providers.json"
    if providers_file.exists():
        with open(providers_file) as f:
            data = json.load(f)
            global_entities['medical_providers'] = [p['name'] for p in data]

    # Load insurers
    insurers_file = entities_dir / "insurers.json"
    if insurers_file.exists():
        with open(insurers_file) as f:
            data = json.load(f)
            global_entities['insurers'] = [ins['name'] for ins in data]

    # Load adjusters
    adjusters_file = entities_dir / "adjusters.json"
    if adjusters_file.exists():
        with open(adjusters_file) as f:
            data = json.load(f)
            global_entities['adjusters'] = [adj['name'] for adj in data]

    # Load lienholders
    lienholders_file = entities_dir / "lienholders.json"
    if lienholders_file.exists():
        with open(lienholders_file) as f:
            data = json.load(f)
            global_entities['liens'] = [lh['name'] for lh in data]

    # Load defendants
    defendants_file = entities_dir / "defendants.json"
    if defendants_file.exists():
        with open(defendants_file) as f:
            data = json.load(f)
            global_entities['defendants'] = [d['name'] for d in data]

    # Load doctors (may be large - 20K+ entries)
    doctors_file = entities_dir / "doctors.json"
    if doctors_file.exists():
        with open(doctors_file) as f:
            data = json.load(f)
            # Only load active doctors for matching (reduce search space)
            global_entities['doctors'] = [d['name'] for d in data if 'Active' in d['attributes'].get('license_status', '')]
            global_entities['doctors_all'] = [d['name'] for d in data]  # All for fallback

    # Load mediators
    mediators_file = entities_dir / "mediators.json"
    if mediators_file.exists():
        with open(mediators_file) as f:
            data = json.load(f)
            global_entities['mediators'] = [m['name'] for m in data]

    # Load vendors
    vendors_file = entities_dir / "vendors.json"
    if vendors_file.exists():
        with open(vendors_file) as f:
            data = json.load(f)
            global_entities['vendors'] = [v['name'] for v in data]

    # Load experts
    experts_file = entities_dir / "experts.json"
    if experts_file.exists():
        with open(experts_file) as f:
            data = json.load(f)
            global_entities['experts'] = [e['name'] for e in data]

    # Load witnesses
    witnesses_file = entities_dir / "witnesses.json"
    if witnesses_file.exists():
        with open(witnesses_file) as f:
            data = json.load(f)
            global_entities['witnesses'] = [w['name'] for w in data]

    # Load organizations
    organizations_file = entities_dir / "organizations.json"
    if organizations_file.exists():
        with open(organizations_file) as f:
            data = json.load(f)
            global_entities['organizations'] = [o['name'] for o in data]

    # Load circuit divisions
    circuit_divisions_file = entities_dir / "circuit_divisions.json"
    if circuit_divisions_file.exists():
        with open(circuit_divisions_file) as f:
            data = json.load(f)
            global_entities['circuit_divisions'] = [d['name'] for d in data]

    # Load district divisions
    district_divisions_file = entities_dir / "district_divisions.json"
    if district_divisions_file.exists():
        with open(district_divisions_file) as f:
            data = json.load(f)
            global_entities['district_divisions'] = [d['name'] for d in data]

    return global_entities


# Additional manual mappings for known variants
KNOWN_MAPPINGS = {
    # Aaron Whaley variants
    "A. G. Whaley": "Aaron G. Whaley",
    "AW": "Aaron G. Whaley",
    "Aaron": "Aaron G. Whaley",
    "Greg Whaley": "Aaron G. Whaley",
    "Aaron Gregory Whaley": "Aaron G. Whaley",  # Abby Sitgraves
    "Whaley, Aaron Gregory": "Aaron G. Whaley",

    # Betsy Catron variants
    "BK": "Betsy R. Catron",
    "Betsy": "Betsy R. Catron",
    "Mrs. Catron": "Betsy R. Catron",

    # Bryce Koon variants
    "Bryce Whaley": "Bryce Koon",
    "W. Bryce Koon": "Bryce Koon",  # Abby Sitgraves
    "W. Bryce Koon, Esq.": "Bryce Koon",

    # Gregg E. Thornton
    "G. Thornton": "Gregg E. Thornton",

    # Thomas Knopf (Mediator)
    "Hon. Thomas J. Knopf": "Hon. Thomas J. Knopf (Ret.)",
    "Hon. Thomas Knopf": "Hon. Thomas J. Knopf (Ret.)",
    "Hon. Judge Thomas Knopf": "Hon. Thomas J. Knopf (Ret.)",
    "Judge Knopf": "Hon. Thomas J. Knopf (Ret.)",
    "Knopf": "Hon. Thomas J. Knopf (Ret.)",
    "Thomas Knopf": "Hon. Thomas J. Knopf (Ret.)",

    # Doctor variants
    "Dr. Huff": "Dr. Wallace Huff",
    "Wallace L. Huff": "Dr. Wallace Huff",
    "Dr. Nazar": "Dr. Gregory Nazar",
    "Nazar": "Dr. Gregory Nazar",
    "Dr. Khalily": "Dr. Cyna Khalily",
    "Dr. Magone": "Dr. Kevin Magone, MD",
    "Dr. Manderino": "Dr. Lisa Manderino",
    "Dr. Orlando": "Marc Orlando",

    # Knox Court variants
    "Knox": "Knox Circuit Court",
    "Knox Cir II": "Knox Circuit Court, Division II",
    "Knox Circuit Court (Kentucky)": "Knox Circuit Court",
    "Knox Circuit Court (Knox County, Kentucky)": "Knox Circuit Court",
    "Knox Circuit II": "Knox Circuit Court, Division II",
    "Knox County": "Knox Circuit Court",
    "Knox County Circuit Court": "Knox Circuit Court",
    "Knox Division 2": "Knox Circuit Court, Division II",

    # Law firm variants - WHT Law
    "WHT Law": "Ward, Hocker & Thornton, PLLC",
    "WHT Law (Vine Center)": "Ward, Hocker & Thornton, PLLC",
    "WHT Law (www.whtlaw.com)": "Ward, Hocker & Thornton, PLLC",
    "WHT Law (www.whtlaw.com / Vine Center)": "Ward, Hocker & Thornton, PLLC",
    "WHT Law Center": "Ward, Hocker & Thornton, PLLC",
    "WHT Law Firm": "Ward, Hocker & Thornton, PLLC",
    "www.whtlaw.com": "Ward, Hocker & Thornton, PLLC",
    "Whitt, Catron & Henderson (WHTLaw)": "Ward, Hocker & Thornton, PLLC",
    "www.whtlaw.com": "Whaley Harrison & Thorne, PLLC",

    # Law firm variants - Ward Hocker
    "Ward Hawker at Thornton": "Ward, Hocker & Thornton, PLLC",

    # Law firm variants - The Whaley Law Firm
    "Whaley Law Firm (whaleylawfirm.com)": "The Whaley Law Firm",
    "Whaley Law Office": "The Whaley Law Firm",
    "WhaleyLawFirm": "The Whaley Law Firm",
    "The Whaley Law Firm, PSC": "The Whaley Law Firm",
    "Whaley Law Firm": "The Whaley Law Firm",  # Abby Sitgraves

    # Law firm aliases
    "Kopka Law": "Kopka Pinkus Dolin, PC",

    # Derek Harvey variants (Abby Sitgraves)
    "Derek A. Harvey Jr.": "Derek Anthony Harvey",
    "Derek A. Harvey": "Derek Anthony Harvey",

    # Sam Leffert variants (Abby Sitgraves)
    "Sam Leffert": "Samuel Robert Leffert",

    # CAAL Worldwide defendant variants (Abby Sitgraves)
    "CAAL Worldwide, Inc.": "CAAL WORLDWIDE, INC.",
    "CAAL Worldwide": "CAAL WORLDWIDE, INC.",
    "Caal Worldwide, Inc.": "CAAL WORLDWIDE, INC.",
    "Caal Worldwide": "CAAL WORLDWIDE, INC.",

    # PIPClaim variants for National Indemnity (Abby Sitgraves)
    "PIP - National Indemnity Company": "National Indemnity Company",
    "PIPClaim: National Indemnity Company": "National Indemnity Company",

    # Client name variants
    "Alma Cristobal": "Alma Socorro Cristobal Avendao",
    "Alma Socorro Cristobal Avenda o": "Alma Socorro Cristobal Avendao",  # typo variant

    # Misclassified entities
    "Sarena Whaley Law Firm": "Sarena Tuttle",  # Person, not law firm
    "Louisville LMEMS": "Louisville Metro EMS",

    # Vendor aliases
    "KY Court Reporters": "Kentucky Court Reporters",
    "Kentuckiana Reporters": "Kentuckiana Court Reporters",
    # NADN variants
    "NADA": "National Academy of Distinguished Neutrals",
    "NADN": "National Academy of Distinguished Neutrals",
    "NADN (America's Premier Mediators & Arbitrators)": "National Academy of Distinguished Neutrals",
    "National Arbitration and Dispute Association": "National Academy of Distinguished Neutrals",

    # Sarena variants
    "Sarena (Whaley Law Firm)": "Sarena Tuttle",
    "Sarena Whaley": "Sarena Tuttle",
    # Additional doctors from Amy Mills case
    "Dr. Alsorogi": "Dr. Mohammad S. Alsorogi",
    "Dr. Kevin Magone, MD": "Dr. Kevin Magone",
    "Alexander Landfield PLLC": "Dr. Alexander David Landfield",
    # Psychologists (PsyD, not in physician database)
    "Dr. Shannon Voor": "Dr. Shannon Voor (psychologist)",
    "Dr. Lisa Manderino": "Dr. Lisa Manderino (neuropsychologist)",
    "Dr. Richard Edelson": "Dr. Richard Edelson (neuropsychologist)",
    
    # Additional doctors from research
    "Dr. Barefoot": "Dr. Julius J. Barefoot III",
    "Dr. Hunt": "Dr. Travis Hunt",

    # Consolidations from Ashlee-Williams review
    "Atty. Whaley": "Aaron G. Whaley",
    "L. Graham": "Lexi Graham",
    "Scott Stoutheukelaw": "Scott Stout",
    "Skofirm": "Stoll Keenon Ogden PLLC",
    "Stout & Heuke": "Stout & Heuke Law Office",

    # Consolidations from Brenda-Lang review
    "Winton and Hiestand": "Winton & Hiestand Law Group",
    "Whaley & Whaley Law Firm": "The Whaley Law Firm",
    "Kentuckiana Reporters Scheduling Department": "Kentuckiana Court Reporters",
    "Kentuckiana Reporters": "Kentuckiana Court Reporters",
    "Reif": "Allison L. Rief",
    "Scott Gowen": "Gregory Scott Gowen",
    "Lou Metro Gov": "Louisville Metro Government",
    "Louisville Metro (Metro Government)": "Louisville Metro Government",
    "Louisville Metropolitan Government": "Louisville Metro Government",
    "Louisville/Jefferson County government": "Louisville Metro Government",
    "Metro Government": "Louisville Metro Government",
    "City of Louisville (Scott Gowen)": "Jefferson County Attorney's Office",
    "Louisville City Attorney's Office": "Jefferson County Attorney's Office",
    "M Hamlet": "Marcus Hamlet",
    "FMD Legal": "Fulton, Maddox, Dickens & Stewart PLLC",
    "Isaacs & Isaacs": "Isaacs and Isaacs Law Firm",

    # Consolidations from Brooklyn-Ballard through Christopher-Wilkerson batch
    "Brooklyn (minor child)": "Brooklyn Ballard",
    "Whaley": "Aaron G. Whaley",
    "Auto-Owners Insurance Company": "Auto Owners Insurance",
    "Mr. Whaley": "Aaron G. Whaley",
    "Lowe": "Robert Lowe",
    "Adj Smith": "Debbie Smith",
    "Adjuster Smith": "Debbie Smith",
    "Debbie": "Debbie Smith",
    "Mrs. Smith": "Debbie Smith",
    "Hartford Mutual adjuster": "Debbie Smith",
    "Megan (KFB PIP adjuster)": "Megan Bates",
    "Megan Bates (RS)": "Megan Bates",
    "CLEARPATH SPECIALTY INSURANCE": "Clearpath Mutual Insurance Company",
    "ClearPath": "Clearpath Mutual Insurance Company",
    "ClearPath / ClearPath Mutual": "Clearpath Mutual Insurance Company",
    "ClearPath Mutual": "Clearpath Mutual Insurance Company",
    "Harford Mutual Insurance Group (formerly ClearPath Mutual)": "Hartford Mutual Insurance",
    "Hartford Mutual (Clearpath)": "Hartford Mutual Insurance",
    "Farm Bureau Insurance Company (Kentucky Farm Bureau)": "Kentucky Farm Bureau",
    "KFB": "Kentucky Farm Bureau",
    "Terrence Donahue": "Dr. Terrence P. Donohue",

    # Consolidations from Daniel-W-Volk through Destiny-Adkins batch
    "jchumbley": "Justin Chumbley",
    "Jessica (Whaley Law Firm)": "Jessica Bottorff",
    "Whaley Law Firm (Whaley Law Office)": "The Whaley Law Firm",
    "Whaley Law": "The Whaley Law Firm",
    "Whaley Lawfirm": "The Whaley Law Firm",
    "Whaley & Whaley": "The Whaley Law Firm",

    # Patrick Ross variants (Debra Marshall / Destiny Adkins cases)
    "Mr. Ross": "Patrick A. Ross",
    "Pat (Hensley & Ross)": "Patrick A. Ross",
    "Pat (Patrick) Hensley": "Patrick A. Ross",
    "Patrick Hensley": "Patrick A. Ross",
    "Ross": "Patrick A. Ross",

    # Campbell Ewen variants
    "A. Ewen": "A. Campbell Ewen",
    "Ewen, Allen Campbell": "A. Campbell Ewen",
    "Campbell Ewen": "A. Campbell Ewen",

    # Client variants
    "Downs": "Juanita Nicole Downs",
    "Juanita Downs": "Juanita Nicole Downs",

    # Court variants
    "Jeff Cir Crt": "Jefferson County Circuit Court, Division I",
    "Jefferson County Court": "Jefferson County Circuit Court, Division I",

    # Defendant - Stephanie Nail variants
    "DC Nail": "Stephanie Nail",
    "Def Nail": "Stephanie Nail",
    "Nail": "Stephanie Nail",
    "Nail, Stephanie M.": "Stephanie Nail",

    # Defendant - Demetrius Turner variants
    "Def Turner": "Demetrius E. Turner",
    "Defendant Turner": "Demetrius E. Turner",
    "Mr. Turner": "Demetrius E. Turner",

    # Organization variants
    "LMPD": "Louisville Metro Police Department",

    # Consolidations from Dewayne-Ward through Elizabeth-Lindsey batch
    "Bryce (BK)": "Bryce Koon",
    "Livers, Douglas": "Douglas G. Livers",
    "Floyd Circuit Court": "Floyd County Circuit Court, Division I",
    "Floyd County Court": "Floyd County Circuit Court, Division I",
    "Allstate Property and Casualty Insurance": "Allstate Insurance",
    "TRAVIS, HERBERT & STEMPIEN ATTORNEYS": "Travis Herbert & Stempien, PLLC",
    "TRAVIS, HERBERT & STEMPIEN, PLLC": "Travis Herbert & Stempien, PLLC",
    "Kentucky Department for Income Support, Child Support Enforcement (CSE)": "Kentucky Child Support Enforcement",
    "Kentucky Department for Income Support (CHFS) Administrative Enforcement Section": "Kentucky Child Support Enforcement",
    "Kentucky Department for Income Support, Child Support Enforcement (CHFS)": "Kentucky Child Support Enforcement",
    "Evenup": "EvenUP",
    "Liberty Mutual Claim #054658453-07": "Liberty Mutual Insurance Company",
    "PIP claim (Liberty Mutual)": "Liberty Mutual Insurance Company",
    "Allstate claim #0700228547": "Allstate Insurance",
    "Allstate Claim 0700228547": "Allstate Insurance",

    # Consolidations from Estate-of-Betty-Prince and Estate-of-Evangeline-Young
    "Bryce (Whaley Law Firm)": "Bryce Koon",
    "Stuttle": "Sarena Tuttle",
    "agwhaley": "Aaron G. Whaley",
    "Mr. Effinger": "Joseph M. Effinger",
    "Mr. Nafziger": "Ryan Nafziger",
    "Mr. Nafziger (rnafziger@ppoalaw.com)": "Ryan Nafziger",
    "Estate of Betty Prince": "Betty Prince",
    "Estate of Betty Prince - client": "Betty Prince",
    "Betty Prince (Estate of Betty Prince)": "Betty Prince",
    "Robert Finance": "Robert Prince",
    "Judge Haner": "Hon. Eric Haner",
    "PPOA": "Phillips, Parker, Orberson & Arnett, PLC",
    "PPOA Law": "Phillips, Parker, Orberson & Arnett, PLC",
    "PPOA law offices": "Phillips, Parker, Orberson & Arnett, PLC",
    "Philip, Parker & Orberson": "Phillips, Parker, Orberson & Arnett, PLC",
    "Norton": "Norton Hospital Downtown",
    "Norton Healthcare": "Norton Hospital Downtown",
    "NORTON HOSPITALS, INC.": "Norton Hospital Downtown",
    "Katie Watts, Esq.": "Katherine T. Watts",
    "S. Gowen": "Gregory Scott Gowen",
    "Scott Gowen, Esq.": "Gregory Scott Gowen",
    "Jacob Ray et al": "Jacob Ray",
    "RAY, JACOB ET AL": "Jacob Ray",
    "Ray, Jacob": "Jacob Ray",
    "Derby City Gaming (DCG)": "Derby City Gaming",
    "Probate Court": "Jefferson County District Court, Division 12",
    "GDonnell@thattorneys.com": "Ginny Donnell",
    "vherbert@thattorneys.com": "Valerie A Herbert",
    "TeamCare – A Central States Health Fund": "TeamCare",

    # Consolidations from Frances-Whitis and Greg-Neltner batch
    "Justin (Whaley Law Firm)": "Justin Chumbley",
    "Mr. Burch": "Stewart Burch",
    "Sarena@whaleylawfirm.com": "Sarena Tuttle",
    "burch@lbfattorneys.com": "Stewart Burch",
    "Blue Gross Taxi": "Bluegrass Taxi",
    "Bluegrass Taxi": "Bluegrass Taxi",
    "Frankfort City Police": "Frankfort Police Department",
    "Kentucky Department of Workers Claims (KY DWC)": "Kentucky Department Of Workers' Claims",
    "Kentucky Uninsured Employer Fund (UEF)": "Uninsured Employers Fund",
    "Kentucky Workers' Claims LMS (kyworkersclaims.lms.ky.gov / no-reply@ky.gov)": "Kentucky Department Of Workers' Claims",
    "Kentucky Workers' Claims LMS (no-reply@ky.gov)": "Kentucky Department Of Workers' Claims",
    "Kentucky Workers' Compensation LMS (kyworkersclaims.lms.ky.gov)": "Kentucky Department Of Workers' Claims",
    "Uninsured Employer Fund (UEF)": "Uninsured Employers Fund",
    "Uninsured Employer Fund": "Uninsured Employers Fund",
    "PIPClaim (Progressive Insurance)": "Progressive Insurance Company",
    "Progressive claim 24-727042794": "Progressive Insurance Company",
    "AG Whaley": "Aaron G. Whaley",
    "Justin Whaley": "Justin Chumbley",
    "Katherine (Katie) Nelson": "Katherine Nelson",
    "Kathleen Nelson": "Katherine Nelson",
    "Katie Nelson Dunn": "Katherine Nelson",
    "Boone Cir Crt 24-CI-00452": "Boone County Circuit Court, Division I",
    "Boone Circuit": "Boone County Circuit Court, Division I",
    "Boone Circuit Court": "Boone County Circuit Court, Division I",
    "Boone Circuit Court (Boone County)": "Boone County Circuit Court, Division I",
    "Boone Circuit Court (Kentucky)": "Boone County Circuit Court, Division I",
    "Boone County (Boone 24-CI-00452)": "Boone County Circuit Court, Division I",
    "Boone County (docket 24-CI-00452)": "Boone County Circuit Court, Division I",
    "COHARA, TRINITY": "Trinity Cohara",
    "Cohara": "Trinity Cohara",
    "Mrs. Cohara": "Trinity Cohara",
    "Progressive (The Progressive Group of Insurance Companies)": "Progressive Insurance Company",
    "Progressive BI claim #236275504": "Progressive Insurance Company",
    "PIPClaim 17-47Q4-74T (State Farm)": "State Farm Insurance Company",
    "State Farm PIP Claim": "State Farm Insurance Company",
    "Kentuckiana Reporters (Transcript Department)": "Kentuckiana Court Reporters",
    "kentuckianareporters.com Scheduling Department": "Kentuckiana Court Reporters",

    # Consolidations from Henrietta-Jenkins through James-Sadler batch
    "Salena Kelly": "Selena Kelly",
    "Emma Catherine Schumaker": "Emma Schumaker",
    "Emma Schamaker": "Emma Schumaker",
    "Emma Shumake": "Emma Schumaker",
    "Bemoore": "Brad E. Moore",
    "Kiper, James": "James Kiper",
    "AMANI, MUSIMBI": "Musimbi Amani",
    "Amani": "Musimbi Amani",
    "Misimbi": "Musimbi Amani",
    "Kopka & Kopka": "Kopka Pinkus Dolin, PC",
    "Travelers claim IZX7996": "Travelers Insurance",
    "Willie Law Firm": "The Whaley Law Firm",
    "law firm": "The Whaley Law Firm",
    "Attorney Whaley": "Aaron G. Whaley",
    "Churchill": "Churchill Downs",
    "State Farm Auto Medical Claims": "State Farm Insurance Company",
    "State Farm claim 17756H": "State Farm Insurance Company",
    "Eyob Tafesse": "Eyob Tafesse",
    "Tafesse": "Eyob Tafesse",

    # Consolidations from Jasmine-Wilson through Jeremy-Lindsey batch
    "Starlite Chiropractic": "Starlight Chiropractic",  # Fixed - Starlight is correct spelling
    "Starlite": "Starlight Chiropractic",
    "Progressive Group of Insurance Companies": "Progressive Insurance Company",
    "Blue Cross and Blue Shield": "Blue Cross Blue Shield",
    "Auto Owners Insurance (UIM)": "Auto Owners Insurance",
    "Progressive Claim #24-902741838": "Progressive Insurance Company",

    # Consolidations from Jerome-Hedinger through Jonah-Price batch
    "Serena": "Sarena Tuttle",
    "Sarena (The Whaley Law Firm)": "Sarena Tuttle",
    "Jessica Poalini": "Jessica L. Paolini",
    "David Ryan, LVM": "David Ryan",
    "State Farm - BK": "State Farm Insurance Company",
    "State Farm Fire & Casualty Company": "State Farm Insurance Company",
    "State Farm Fire Claims": "State Farm Insurance Company",
    "Dr Jeff Stidam": "Dr. Jeffrey M. Stidam",
    "Dr Lazlo Maak": "Dr. Lazlo T. Maak",
    "Dr. Haney": "Dr. William H. Haney",
    "Dr. Haney Office": "Dr. William H. Haney",
    "Dr. William H. Haney, M.D.": "Dr. William H. Haney",
    "William H. Haney, M.D. (Dr. Haney's Office)": "Dr. William H. Haney",
    "Personal Injury Protection (PIP) - Progressive Insurance Company": "Progressive Insurance Company",
    "No UIM coverage - Progressive Insurance Company": "Progressive Insurance Company",
    "No UM coverage - Progressive Insurance Company": "Progressive Insurance Company",
}

# Entities to ignore (generic terms, software, etc.)
IGNORE_ENTITIES = {
    # Generic legal terms
    "Amy Mills", "Bryce", "DC", "Defendant", "Defendants", "Defense Counsel (DC)",
    "Defense attorney", "Defense counsel", "CoC Esq", "Dinsmore",
    "KP Attorneys", "KPATT", "Multiple attorneys", "PD adjuster",
    "court", "individual defendant", "Courts", "Courtroom HJ301",
    "Court (CourtNet)", "CourtNet",

    # Generic insurance terms to ignore
    "Uninsured motorist demand(s)", "uninsured motorist claim",
    "UIM coverage", "UIM for Claim", "Underinsured motorist",
    "limousine company",
    "Kentucky One Health",  # Abby Sitgraves - wrong match (insurer, not medical provider)
    "Kentucky Court of Justice eFiling system",  # System, not entity

    # Software/tools
    "ChartSwap", "Conduent", "Dropbox", "Fax Legal", "Filevine",
    "NextRequest", "RCFax", "VineSign", "DocuSign", "FileVine",
    "Box", "FreshBooks", "RingCentral", "Vocecon", "Zoom",
    "Adobe Systems Incorporated", "Google LLC", "Mandrillapp",
    "bellabeautyinstitute@gmail.com", "emwnlaw.com",

    # Generic organizations
    "Johnson Health and Safety", "Hometown Bank", "Hometown Bank of Corbin",
    "IRS", "DC Mediation",

    # Service companies (non-legal)
    "Tony's Wrecker Service", "Transclaims",

    # Medical/provider generic terms
    "Medical providers (unspecified)", "PCP", "Orthopedic specialist (unspecified)",

    # People who are just names in wrong context
    "Cordle, Charles", "Jason", "Vine Center", "Walter, Casey",
    "Andrew M. Yocum", "Catie Coldiron Joseph", "Clay E. Thornton",
    "Tori S. Wells", "Jeremy Leitner", "Jones", "Kate Smith",
    "Brian Dietsche", "Jared Larkin",

    # Organizations to ignore
    "Bella Beauty", "Bella Beauty Institute", "Trillium Center",
    "Vine Center / WHT Law", "EMWN Law",

    "Bob Hammonds",
    "Defense Attorney for Forcht Bank",
    "lfarah@whtlaw.com",

    # BIClaim generic terms
    "Amy Mills - personal injury claim",
    "Amy Mills Premise 04/26/2019",
    "Amy-Mills-Premise-04-26-2019",
    "Bodily Injury (TBI, surgeries, lost income)",
    "Bodily Injury claim",
    "Impairment of future earning capacity claim",
    "Personal Injury Claim",
    "Personal injury claim (Premise 04-26-2019)",

    # From Anella-Noble/Antonio-Lopez/Ashlee-Williams reviews
    "BI Claim #054658453-01 (Liberty Mutual)",
    "Liberty Mutual PIP log",
    "Underinsured motorist coverage for Claim #054658453-01",
    "Naomi Richardson's attorney",
    "Louisville Accident Law Firm",
    "Kentucky PLLC",
    "University of Louisville",
    "UofL Health, Inc.",
    "UofL Health Inc.",

    # From Azaire-Lopez/Brenda-Lang reviews
    "CourtNet (envelope 6555977)", "CourtNet Envelope 6650387",
    "DC (defense counsel)", "DC Lou Metro",
    "AF Driver, Jeff", "AW & BK",
    "mother (unnamed)", "Wendy Cotton",
    "GoAnywhere", "Paubox", "20 Second Scheduler",
    "OMB Medical Records Requests", "AdaptHealth", "Ventra Health",
    "Microsoft Corporation",
    "sgowen@fmdlegal.com (S. Gowen)",  # Email address, not entity

    # From Brooklyn-Ballard through Christopher-Wilkerson batch
    "Greg Gant", "Deena Gilliam", "Elizabeth Ballard",
    "Brooklyn Ballard-Lien Request", "Health lien",
    "Tymon Brown", "Vinesign",
    "@jchumbley", "Mary [last name]", "final lien",
    "OMB Medical Records Requests (Louisville office)", "OMBMRR@Louisvilleky.gov",
    "Court Net", "Charles Johnson v. Robert Lowe (24-CI-002475)",
    "BI #250525568", "Louisville Accident Lawyer / Filevine",
    "Adjuster (unspecified)", "Arlene", "Christina",
    "Hartford Mutual Insurance adjuster", "Hartford Mutual adjuster (unnamed)", "unnamed adjuster",
    "Mutual of Omaha", "FORK MD",
    "Communication Project (Filevine integration)", "Generic Customer Service",
    "H&O Transport, Inc.", "M&W Transport",
    "LexisNexis Risk Solutions", "LexisNexis Risk Solutions (BuyCrash)", "LexisNexis BuyCrash",
    "PIP Claim 04943051", "Claim 04943051",
    "04943051", "238042CS (WC-MVA-02-15-2024)", "WC #238042",
    "Christopher-Wilkerson-WC-MVA-02-15-2024", "Christopher-Wilkerson-WC-MVA-02-15-2024 (file 238042)",
    "WC-MVA-02-15-2024", "WCClaim #238042CS",
    "Workers' Compensation (WC-MVA) claim", "Workers' Compensation Claim 238042",
    "Client",  # Generic "Client" reference

    # From Daniel-W-Volk through Destiny-Adkins batch
    "SafeCo adjuster", "Aaron Wy", "ZPA003356461", "Cressman Physical Therapy",
    "Dr Gilbert", "Dr. Cassenele", "PIPClaim #047060829", "EpicLink",
    "SafeCo UIM claim", "Under Insured Motorist (UIM) claim", "UM claim",
    "LBF", "Tasia Key", "Leiby Sanchez Luis", "Philip McDonald, MD",
    "Medicare questionnaire (2020)", "HCA Healthcare", "KFBMIC (A/S/O Edie Renick)",
    "BCM LLP", "LHP Law Group, PLLC", "911billing.net (Faith Gibbons)",
    "Express Notary Service", "Scheduling Department", "TSICO", "ZixCorp",
    "Jasmine Reed", "Robert", "Bankruptcy Court", "unspecified court",
    "Defendant driver", "defense attorney", "defense counsel",
    "John D. Bertram, Esq.", "Aaron Wy",
    "CourtNet Envelope 7240362", "District Court Administration",
    "Jefferson County OCCC Video Department", "Jennifer Miles (KY Courts)",
    "Kentucky Courts", "Kentucky Courts (CourtNet)",
    "Kentucky State Office of the Administrative Office of the Courts",
    "Kentucky courts (Mary Stephenson)", "Motion Hour (judge's order)",
    "Motion hearing (Sept 6, 2022)", "judge (unnamed)",
    "Defendant (hearing April 15, 2021)", "Defendants (DCs)",
    "NAIL, STEPHANIE M. ET AL", "Nail, et al.", "Unk Driver",
    "defense (unnamed)", "Defendant's insurance company",
    "AW & Assoc Franklin", "Adkins & Downs", "DC Rice Office",
    "Jefferson County OCC Video Department", "Paul Klapheke",
    "Beth Alexander",

    # From Dewayne-Ward through Elizabeth-Lindsey batch
    "defendants' attorney", "Dannin Turner", "Frank Adkins", "EHI",
    "Axon / Evidence.com", "Brandon French", "Floyd Co. Indiana Circuit Court",
    "Allstate adjuster", "Harold Dorman", "Harold Robert Dorman",
    "GDonnell@thattorneys.com", "vherbert@thattorneys.com", "Mory",
    "Wende Raderer", "former attorney", "QMJF78KY",
    "Court orders", "District of Columbia", "Family Court", "Hall of Justice",
    "Daetoia Lewis", "Defendant Lewis", "Mrs. Lewis",
    "UMClaim 0700228547", "Workers' Compensation",
    "Workers' Compensation (Uninsured Special Fund)",
    "Medical providers (wrist and knee surgeries)",
    "Lien from Allstate Insurance (dated Feb 15, 2023)",
    "None", "8593414845@rcfax.com",
    "Tasia Key", "Leiby Sanchez Luis", "defendants",

    # From Estate-of-Betty-Prince and Estate-of-Evangeline-Young batch
    "Celia Hibben", "Chibben", "Donna Jones", "jeffinger@ppoalaw.com",
    "unspecified lawyer", "21-CI-003798", "Bodily injury claim",
    "Estate-of-Betty-Prince-Premise-7-14-2020", "LVM", "Court",
    "Docket 21-CI-003798", "Trimble District Court", "Unspecified court",
    "motion hour on the MTC", "AGW", "Arriva Medical", "Kidney Care Consultants",
    "Donna Jones, RN", "Nurse Donna Jones", "Ruby Mail", "Vonage Business",
    "Ruby Receptionist", "Sonya (USAA)", "Sonya (ext 44766)", "Taneesha Jackson",
    "Debbie Allen", "Kwatts@ppoalaw.com", "jparker@ppoalaw.com", "Plaintiff counsel",
    "ESTATE OF: YOUNG, EVANGELINE LEE", "Estate of Evangeline Lee Young",
    "Estate-of-Evangeline-Young-MVA-8-12-2023", "Susie Tran", "YOUNG, DWIGHT ET AL",
    "Jefferson Circuit Court (DISTRICT)", "Ascension Point Recovery Services",
    "Central States Funds", "OMB MEDICAL RECORDS REQUESTS",
    "911 Billing Services & Consultant, Inc.", "911billing.net",
    "Unspecified lien (processed)",

    # From Frances-Whitis and Greg-Neltner batch
    "adjuster", "Defense counsel (DC)", "Rose Mauser",
    "Motor vehicle accident claim", "KY DWC", "KY DWC 2024-01285",
    "Kentucky DWC", "Kentucky Division of Workers' Compensation",
    "Employer", "Mrs. Mauser", "UEF", "defendant employer",
    "Mrs. Mauser's Auto Insurance", "United Financial Casualty Company",
    "Workers' Compensation Carrier", "LBF Attorneys",
    "lbfattorneys.com (opposing counsel)", "PIP claim 24-727042794",
    "CHC EMS Attorney Requests (Optum)", "LMS (Kentucky Workers' Claims)",
    "kyworkersclaims.lms.ky.gov", "202401285", "Frances Whitis WC claim",
    "Frances Whitis workers' compensation claim", "Frances-Whitis-WC-MVA-9-6-2024",
    "INJURY CLAIM (Document Id: 6910189)", "KY DWC 2024-01285",
    "LMS Claim Filing for Uninsured Employee Fund Coverage / Application for Resolution",
    "WC #202401285", "WC Claim #202401285", "WC with UEF",
    "WCClaim (24-727042794)", "Workers' Compensation Claim (Frances-Whitis)",
    "Workers' Compensation claim (FROI)", "Workers' compensation claim (UEF involvement)",
    "Megan E. Renfro", "Joe Mordino", "Maeve Richardson",
    "knelson@richardsonlawgrp.com", "Neltner v. Cohara (24-CI-00452)",
    "DC Office", "Unnamed defendant", "defendant (unnamed)",
    "None: $4980", "City of Florence", "City of Florence, Kentucky",
    "florence-ky.gov",

    # From Henrietta-Jenkins through James-Sadler batch
    "TANK", "BI #17-88T6-48L", "Claim 17-88T6-48L",
    "Defense Attorney", "defense counsel for Travelers",
    "23-CI-005758", "Defense", "defendant driver",
    "Bodily Injury", "Other Party BI limits", "driver behind / other driver",
    "insurers", "17-48B2-02X", "BI #1754B", "BI #1754K417G",
    "BI Claim 1727W365XI (State Farm)", "BI Claim 1742B",
    "BIClaim 17-48B2-02X (State Farm)", "Claim 1754B / 1754F (State Farm)",
    "Unspecified lien request", "RCFax (5025377709@rcfax.com)",

    # From Jasmine-Wilson through Jeremy-Lindsey batch
    "Jessica Giesel", "PIP - Progressive", "PIP claim",
    "assigned adjuster", "CSAA", "At-fault insurer (Claim #250-068-9702)",
    "at-fault party's insurance", "Uninsured motorist coverage",
    "unnamed defendants", "property-damage adjuster",

    # From Jerome-Hedinger through Jonah-Price batch
    "Adjuster", "BI adjuster", "Jerome's adjuster", "Jerry's adjuster",
    "State Farm adjuster", "State Farm adjuster supervisor", "at-fault adjuster",
    "unspecified adjuster", "Opposing counsel", "Plaintiff's counsel",
    "17N8360G8", "Bodily Injury (BI)", "Bodily Injury claim (State Farm)",
    "Premise Liability (Dog Bite) Complaint", "Criminal Court", "District Court",
    "432 Atwood, LLC", "432 Atwood, et al.", "Atwood LLC", "Brown",
    "Brown, Dahlyn", "Brown, Dahlyn (et al)", "Brown/Burden", "Burden",
    "DC Atwood", "Dahlyn Brown", "Draylen Round", "Jessica Burden",
    "Mr. Brown", "defendant (neighbor with pitbull)", "homeowner",
    "Homeowners insurance company", "homeowner's insurer",
    "432 Atwood LLC", "client's physicians", "psychiatrist",
    "therapist (PTSD specialist)", "jessica@whaleylawfirm.com",
    "Jimmy-Ferguson-MVA-5-30-2024", "Progressive adjuster",
    "Elmwood Staffing", "UM coverage",
}


def consolidate_proposed_entities(proposed_entities: dict) -> dict:
    """
    Consolidate duplicate entity mentions within each type.

    Returns: dict mapping canonical_name -> [variants]
    """
    from rapidfuzz import fuzz

    # First, apply known manual mappings and track original variants
    # Also filter out ignored entities
    mapped_entities = defaultdict(set)
    mapping_tracker = defaultdict(lambda: defaultdict(list))  # entity_type -> canonical -> [original_variants]

    for entity_type, entity_names in proposed_entities.items():
        for name in entity_names:
            # Skip ignored entities
            if name in IGNORE_ENTITIES:
                continue

            # Skip generic claim patterns
            if any(name.startswith(pattern) for pattern in ['BI claim', 'BIClaim #', 'Claim #', 'PIP #', 'UIM ']):
                continue

            # Check if this name has a known mapping
            if name in KNOWN_MAPPINGS:
                canonical = KNOWN_MAPPINGS[name]
                mapped_entities[entity_type].add(canonical)
                mapping_tracker[entity_type][canonical].append(name)
            else:
                mapped_entities[entity_type].add(name)

    consolidated = {}

    for entity_type, entity_names in mapped_entities.items():
        entity_list = sorted(entity_names)
        processed = set()
        type_consolidated = {}

        for i, name1 in enumerate(entity_list):
            if name1 in processed:
                continue

            # Normalize based on entity type
            if entity_type == "Attorney":
                norm1 = normalize_attorney_name(name1)
            elif entity_type == "Court":
                norm1 = normalize_court_name(name1)
            elif entity_type == "MedicalProvider":
                norm1 = normalize_hospital_name(name1)
            else:
                norm1 = normalize_name(name1)

            # Start with manual mapping variants if they exist
            variants = mapping_tracker[entity_type].get(name1, []) + [name1]

            for name2 in entity_list[i+1:]:
                if name2 in processed:
                    continue

                if entity_type == "Attorney":
                    norm2 = normalize_attorney_name(name2)
                elif entity_type == "Court":
                    norm2 = normalize_court_name(name2)
                elif entity_type == "MedicalProvider":
                    norm2 = normalize_hospital_name(name2)
                else:
                    norm2 = normalize_name(name2)

                # Check for match
                if norm1 == norm2:
                    # Add both name2 and any manual mappings that led to name2
                    variants.append(name2)
                    variants.extend(mapping_tracker[entity_type].get(name2, []))
                    processed.add(name2)
                elif fuzz.ratio(norm1, norm2) >= 85:
                    variants.append(name2)
                    variants.extend(mapping_tracker[entity_type].get(name2, []))
                    processed.add(name2)

            # Deduplicate variants
            variants = sorted(set(variants))

            if len(variants) > 1:
                # IMPORTANT: If name1 came from KNOWN_MAPPINGS, it should be canonical
                # (name1 is the mapped-to value, variants include the original)
                # Otherwise, use longest name as canonical
                if name1 in mapping_tracker[entity_type]:
                    # name1 is a KNOWN_MAPPINGS target - use it as canonical
                    canonical = name1
                else:
                    # No mapping involved - use longest name
                    canonical = max(variants, key=len)
                type_consolidated[canonical] = variants
            else:
                type_consolidated[name1] = [name1]

            processed.add(name1)

        consolidated[entity_type] = type_consolidated

    return consolidated


def generate_review_doc(processed_file: Path, output_dir: Path, global_entities: dict):
    """Generate review document for one case."""
    with open(processed_file) as f:
        data = json.load(f)

    case_name = data['case_name']
    case_entities = data['case_entities']
    episodes = data['episodes']

    # Collect all proposed entities
    proposed_entities = defaultdict(set)

    for ep in episodes:
        for rel in ep.get('proposed_relationships', {}).get('about', []):
            entity_type = rel.get('entity_type')
            entity_name = rel.get('entity_name')
            if entity_type and entity_name:
                proposed_entities[entity_type].add(entity_name)

    # Consolidate duplicate proposed entities
    consolidated = consolidate_proposed_entities(proposed_entities)

    # Build markdown review document
    lines = []
    lines.append(f"# Relationship Review: {case_name}\n")
    lines.append(f"**Total Episodes:** {data['total_episodes']}\n")
    lines.append(f"**Total Proposed Relationships:** {sum(len(eps.get('proposed_relationships', {}).get('about', [])) for eps in episodes)}\n")
    lines.append("\n---\n")

    # Section 1: Existing Graph Entities
    lines.append("## 1. Existing Entities in Graph\n")
    lines.append("*(These are already in the graph for this case)*\n")

    if case_entities['providers']:
        lines.append(f"\n### Medical Providers ({len(case_entities['providers'])})")
        for p in case_entities['providers']:
            specialty = f" ({p['specialty']})" if p['specialty'] else ""
            lines.append(f"- {p['name']}{specialty}")

    if case_entities['claims']:
        lines.append(f"\n### Insurance Claims ({len(case_entities['claims'])})")
        for c in case_entities['claims']:
            lines.append(f"- **{c['type']}**: {c['insurer']}")
            if c['adjuster']:
                lines.append(f"  - Adjuster: {c['adjuster']}")

    if case_entities['liens']:
        lines.append(f"\n### Liens ({len(case_entities['liens'])})")
        for l in case_entities['liens']:
            amount = f" (${l['amount']:,.2f})" if l['amount'] else ""
            lines.append(f"- {l['holder']}{amount}")

    if case_entities['attorneys']:
        lines.append(f"\n### Attorneys ({len(case_entities['attorneys'])})")
        for a in case_entities['attorneys']:
            lines.append(f"- {a['name']} ({a['role']})")

    # Section 2: Proposed Entities from Episodes
    lines.append("\n---\n")
    lines.append("## 2. Proposed Entity Mentions (from LLM extraction)\n")
    lines.append("*(Consolidated duplicates, showing matches to existing entities)*\n")

    for entity_type in sorted(consolidated.keys()):
        type_groups = consolidated[entity_type]
        lines.append(f"\n### {entity_type} ({len(type_groups)} consolidated)")

        for canonical_name, variants in sorted(type_groups.items()):
            # Check if this matches an existing entity (fuzzy matching)
            matched = False
            matched_name = ""

            # ALWAYS check Whaley staff FIRST, regardless of entity_type
            # Staff can be misclassified as Attorney, Adjuster, Client, etc.
            is_staff, staff_name, correct_type = check_whaley_staff(canonical_name)
            if is_staff:
                matched = True
                if correct_type == "CaseManager":
                    matched_name = f"{staff_name} (WHALEY STAFF → should be CaseManager, not {entity_type})"
                else:
                    matched_name = f"{staff_name} (WHALEY ATTORNEY, not {entity_type})"

            # PRIORITY CHECK: Check specialist categories BEFORE entity-specific matching
            # These should ALWAYS match to their specialist category, regardless of LLM extraction
            if not matched and global_entities.get('liens'):
                # Check if this entity is a lienholder (medical billing, subrogation companies)
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['liens'])
                if matched:
                    matched_name = f"{matched_name} (LienHolder, not {entity_type})"

            if not matched and global_entities.get('vendors'):
                # Check if this entity is a vendor (IME companies, court reporters, record services)
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['vendors'])
                if matched:
                    matched_name = f"{matched_name} (Vendor, not {entity_type})"

            # If not Whaley staff or specialist category, apply entity-specific matching
            if not matched and entity_type in ["BIClaim", "PIPClaim", "UMClaim", "UIMClaim", "WCClaim"]:
                # Match by insurer name, not full claim name
                insurers_for_type = [c['insurer'] for c in case_entities['claims']
                                    if c['type'] == entity_type and c['insurer']]
                matched, matched_name = fuzzy_match_entity(canonical_name, insurers_for_type)

            if not matched and entity_type == "MedicalProvider":
                # Check if this is actually a doctor (starts with "Dr." or has M.D./D.O.)
                is_doctor = (
                    canonical_name.startswith("Dr.") or
                    canonical_name.startswith("Dr ") or
                    "M.D." in canonical_name or
                    "D.O." in canonical_name or
                    ", MD" in canonical_name or
                    ", DO" in canonical_name
                )

                if is_doctor and global_entities.get('doctors'):
                    # Check doctors database first (use strict matching)
                    # NOTE: All doctors ARE medical providers (doctors provide medical care)
                    matched, matched_name = fuzzy_match_doctor(canonical_name, global_entities['doctors'])
                    if matched:
                        matched_name = f"{matched_name} (licensed KY doctor, valid MedicalProvider)"
                    elif global_entities.get('doctors_all'):
                        # Try all doctors (inactive)
                        matched, matched_name = fuzzy_match_doctor(canonical_name, global_entities['doctors_all'])
                        if matched:
                            matched_name = f"{matched_name} (licensed KY doctor, inactive, valid MedicalProvider)"

                if not matched:
                    # Check medical provider organizations
                    provider_names = [p['name'] for p in case_entities['providers']]
                    matched, matched_name = fuzzy_match_entity(canonical_name, provider_names, entity_type="MedicalProvider")
                    if not matched:
                        matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['medical_providers'], entity_type="MedicalProvider")

            if not matched and entity_type == "Doctor":
                # Check against active doctors first, then all doctors
                # Doctors are a subset of MedicalProvider (all doctors ARE medical providers)
                if global_entities.get('doctors'):
                    matched, matched_name = fuzzy_match_doctor(canonical_name, global_entities['doctors'])
                    if matched:
                        matched_name = f"{matched_name} (licensed in KY)"
                if not matched and global_entities.get('doctors_all'):
                    # Fallback to all doctors (includes inactive)
                    matched, matched_name = fuzzy_match_doctor(canonical_name, global_entities['doctors_all'])
                    if matched:
                        matched_name = f"{matched_name} (licensed in KY - may be inactive)"

            if not matched and entity_type == "Insurer":
                # Check case insurers first, then global insurers, then directory
                insurers = list(set(c['insurer'] for c in case_entities['claims'] if c['insurer']))
                matched, matched_name = fuzzy_match_entity(canonical_name, insurers)
                if not matched and global_entities['insurers']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['insurers'])
                if not matched and global_entities['directory_all']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                    if matched:
                        matched_name = f"{matched_name} (from directory)"

            if not matched and entity_type == "Adjuster":
                # Check case adjusters first, then global adjusters, then directory
                adjusters = list(set(c['adjuster'] for c in case_entities['claims'] if c['adjuster']))
                matched, matched_name = fuzzy_match_entity(canonical_name, adjusters)
                if not matched and global_entities['adjusters']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['adjusters'])
                if not matched and global_entities['directory_all']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                    if matched:
                        matched_name = f"{matched_name} (from directory)"

            if not matched and (entity_type == "Lien" or entity_type == "LienHolder"):
                holders = [l['holder'] for l in case_entities['liens'] if l['holder']]
                matched, matched_name = fuzzy_match_entity(canonical_name, holders)
                if not matched and global_entities['directory_all']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                    if matched:
                        matched_name = f"{matched_name} (from directory)"

            if not matched and entity_type == "Attorney":
                # Already checked Whaley staff globally above
                # Check against case attorneys, then global, then directory
                attorney_names = [a['name'] for a in case_entities['attorneys']]
                matched, matched_name = fuzzy_match_entity(canonical_name, attorney_names, entity_type="Attorney")
                if not matched:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['attorneys'], entity_type="Attorney")
                if not matched and global_entities['directory_all']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'], entity_type="Attorney")
                    if matched:
                        matched_name = f"{matched_name} (from directory)"

            if not matched and entity_type == "Defendant":
                # Check global defendants, then directory
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['defendants'])
                if not matched and global_entities['directory_all']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                    if matched:
                        matched_name = f"{matched_name} (from directory)"

            if not matched and entity_type == "LawFirm":
                # First check aliases (exact or partial match for names with extra info)
                alias_matched = False
                if 'law_firm_aliases' in global_entities:
                    # Try exact match first
                    if canonical_name in global_entities['law_firm_aliases']:
                        matched = True
                        matched_name = f"{global_entities['law_firm_aliases'][canonical_name]} (alias: {canonical_name})"
                        alias_matched = True
                    else:
                        # Try stripping parenthetical info (e.g., "BDB Law (bdblawky.com)" → "BDB Law")
                        base_name = re.sub(r'\s*\([^)]+\)\s*$', '', canonical_name).strip()
                        if base_name in global_entities['law_firm_aliases']:
                            matched = True
                            matched_name = f"{global_entities['law_firm_aliases'][base_name]} (alias: {base_name})"
                            alias_matched = True

                if not alias_matched:
                    # Check if it's actually an attorney's name
                    is_staff, staff_name, _ = check_whaley_staff(canonical_name)
                    if is_staff:
                        matched = True
                        matched_name = f"{staff_name} (→ ATTORNEY, not law firm)"
                    else:
                        # Check against global attorneys (wrong type)
                        is_attorney, atty_name = fuzzy_match_entity(canonical_name, global_entities['attorneys'], entity_type="Attorney")
                        if is_attorney:
                            matched = True
                            matched_name = f"{atty_name} (→ ATTORNEY, not law firm)"
                        else:
                            # Match law firms, then directory
                            matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['law_firms'], entity_type="LawFirm")
                            if not matched and global_entities['directory_all']:
                                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'], entity_type="LawFirm")
                                if matched:
                                    matched_name = f"{matched_name} (from directory)"

            if not matched and entity_type == "Client":
                # Check global clients
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['clients'])

            if not matched and entity_type == "Court":
                # Check circuit divisions first (most specific), then district divisions, then courts, then organizations
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['circuit_divisions'], entity_type="Court")
                if not matched:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['district_divisions'], entity_type="Court")
                if not matched:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['courts'], entity_type="Court")
                if not matched:
                    # Check organizations (for entities like "Kentucky Court of Justice")
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['organizations'])

            elif not matched and entity_type == "Vendor":
                # Check vendors, then directory
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['vendors'])
                if not matched and global_entities['directory_all']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                    if matched:
                        matched_name = f"{matched_name} (from directory)"

            elif not matched and entity_type == "Expert":
                # Check experts, then directory
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['experts'])
                if not matched and global_entities['directory_all']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                    if matched:
                        matched_name = f"{matched_name} (from directory)"

            elif not matched and entity_type == "Witness":
                # Check witnesses, then directory
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['witnesses'])
                if not matched and global_entities['directory_all']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                    if matched:
                        matched_name = f"{matched_name} (from directory)"

            elif not matched and entity_type == "Mediator":
                # Check mediators, then directory
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['mediators'])
                if not matched and global_entities['directory_all']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                    if matched:
                        matched_name = f"{matched_name} (from directory)"

            elif not matched and entity_type == "Organization":
                # Check organizations, then directory
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['organizations'])
                if not matched and global_entities['directory_all']:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                    if matched:
                        matched_name = f"{matched_name} (from directory)"

            # Fallback: check directory for any unmatched entity
            if not matched and global_entities['directory_all']:
                dir_matched, dir_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                if dir_matched:
                    matched = True
                    matched_name = f"{dir_name} (from directory)"

            # Build status with matched name if found
            if matched and matched_name:
                status = f"✓ MATCHES: {matched_name}"
            elif matched:
                status = "✓ EXISTS"
            else:
                status = "? NEW"

            # Show canonical with variants if duplicates were found
            if len(variants) > 1:
                lines.append(f"- [ ] **{canonical_name}** — *{status}*")
                for variant in variants:
                    if variant != canonical_name:
                        lines.append(f"      ↳ _{variant}_")
            else:
                lines.append(f"- [ ] {canonical_name} — *{status}*")

    # Section 3: Action Items
    lines.append("\n---\n")
    lines.append("## 3. Review Actions\n")
    lines.append("\n**For each proposed entity marked '? NEW':**")
    lines.append("- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')")
    lines.append("- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)")
    lines.append("- [ ] **Create new** (valid entity not yet in graph)")
    lines.append("\n**After review:**")
    lines.append("- Run ingestion script to create Episode nodes and ABOUT relationships")

    # Save review doc
    output_file = output_dir / f"review_{case_name}.md"
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

    return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate review documents')
    parser.add_argument('--processed-dir', type=str, default=None,
                       help='Directory containing processed_*.json files')
    args = parser.parse_args()

    # Paths (try multiple locations)
    if args.processed_dir:
        processed_dir = Path(args.processed_dir)
    else:
        possible_dirs = [
            Path("/mnt/workspace/json-files/memory-cards/episodes"),
            Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes"),
        ]
        processed_dir = None
        for d in possible_dirs:
            if d.exists():
                processed_dir = d
                break

        if not processed_dir:
            print("❌ Could not find processed episodes directory")
            return

    # Find entities directory
    entities_dir = processed_dir.parent / "entities"
    if not entities_dir.exists():
        print(f"❌ Could not find entities directory: {entities_dir}")
        return

    # Find directory.json
    directory_file = processed_dir.parent.parent / "directory.json"
    if not directory_file.exists():
        print(f"⚠️  Warning: directory.json not found at {directory_file}")
        directory_file = None

    review_dir = processed_dir / "reviews"
    review_dir.mkdir(exist_ok=True)

    # Load global entities for matching
    print("Loading global entities...")
    global_entities = load_global_entities(entities_dir, directory_file)
    print(f"  - {len(global_entities['clients'])} clients")
    print(f"  - {len(global_entities['courts'])} courts")
    print(f"  - {len(global_entities['circuit_divisions'])} circuit divisions")
    print(f"  - {len(global_entities['district_divisions'])} district divisions")
    print(f"  - {len(global_entities['attorneys'])} attorneys")
    print(f"  - {len(global_entities['law_firms'])} law firms")
    print(f"  - {len(global_entities['medical_providers'])} medical providers")
    print(f"  - {len(global_entities.get('doctors', []))} doctors (active)")
    print(f"  - {len(global_entities.get('doctors_all', []))} doctors (all)")
    print(f"  - {len(global_entities.get('mediators', []))} mediators")
    print(f"  - {len(global_entities.get('vendors', []))} vendors")
    print(f"  - {len(global_entities.get('experts', []))} experts")
    print(f"  - {len(global_entities.get('witnesses', []))} witnesses")
    print(f"  - {len(global_entities.get('organizations', []))} organizations")
    print(f"  - {len(global_entities['insurers'])} insurers")
    print(f"  - {len(global_entities['defendants'])} defendants")
    print(f"  - {len(global_entities['directory_all'])} directory entries")
    print()

    # Find all processed files
    processed_files = sorted(processed_dir.glob("processed_*.json"))

    print(f"Generating review documents for {len(processed_files)} cases...")
    print()

    for pf in processed_files:
        output = generate_review_doc(pf, review_dir, global_entities)
        print(f"✓ {output.name}")

    print()
    print(f"✅ Generated {len(processed_files)} review documents")
    print(f"Location: {review_dir}")


if __name__ == "__main__":
    main()
