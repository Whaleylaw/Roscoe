#!/usr/bin/env python3
"""
Create Clean Entity Files

Generates clean, complete entity JSON files by merging data from all source files.
Contact info from directory.json is merged into specialized entity types.

Usage:
    python create_clean_entity_files.py [--input-dir path] [--output-dir path]
"""

import json
import re
import argparse
from pathlib import Path
from typing import Optional
from collections import defaultdict
from datetime import datetime

# Try to import rapidfuzz for fuzzy matching, fall back to basic matching
try:
    from rapidfuzz import fuzz
    HAS_FUZZY = True
except ImportError:
    HAS_FUZZY = False
    print("Warning: rapidfuzz not installed. Using exact name matching only.")


# =============================================================================
# Configuration
# =============================================================================

INPUT_DIR = Path("/Volumes/X10 Pro/Roscoe/json-files")
OUTPUT_DIR = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/entities")

# Insurance type mapping
INSURANCE_TYPE_MAP = {
    "Personal Injury Protection (PIP)": "PIPClaim",
    "Bodily Injury (BI)": "BIClaim",
    "Uninsured Motorist (UM)": "UMClaim",
    "Underinsured Motorist (UIM)": "UIMClaim",
    "Workers' Compensation (WC)": "WCClaim",
    "Medical Payments (MedPay)": "MedPayClaim",
}


# =============================================================================
# Utility Functions
# =============================================================================

def normalize_name(name: str) -> str:
    """Normalize name for matching: lowercase, strip, remove punctuation."""
    if not name:
        return ""
    # Lowercase and strip
    normalized = name.lower().strip()
    # Remove common suffixes/prefixes that vary
    normalized = re.sub(r'\s+(inc|llc|llp|pllc|pc|pa|md|do|dc|pt|dpt)\.?$', '', normalized, flags=re.IGNORECASE)
    # Remove punctuation except spaces
    normalized = re.sub(r'[^\w\s]', '', normalized)
    # Collapse multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def safe_load_json(path: Path) -> list:
    """Safely load JSON that might have corruption or nested format."""
    if not path.exists():
        print(f"  Warning: File not found: {path}")
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Handle empty file
    content = content.strip()
    if not content:
        return []
    
    # Try normal parsing first
    try:
        data = json.loads(content)
        # Handle nested jsonb_agg format
        if isinstance(data, list) and len(data) >= 1 and isinstance(data[0], dict) and "jsonb_agg" in data[0]:
            return data[0]["jsonb_agg"]
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        pass
    
    # Handle file corruption - extract valid JSON
    if not content.startswith('['):
        # Find all complete JSON objects
        objects = []
        depth = 0
        start = None
        for i, char in enumerate(content):
            if char == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0 and start is not None:
                    try:
                        obj = json.loads(content[start:i+1])
                        objects.append(obj)
                    except:
                        pass
                    start = None
        return objects
    
    # For array format, find matching bracket
    bracket_stack = []
    for i, char in enumerate(content):
        if char == '[':
            bracket_stack.append(i)
        elif char == ']':
            if bracket_stack:
                start = bracket_stack.pop()
                if len(bracket_stack) == 0:
                    try:
                        data = json.loads(content[:i+1])
                        if isinstance(data, list) and len(data) >= 1:
                            if isinstance(data[0], dict) and "jsonb_agg" in data[0]:
                                return data[0]["jsonb_agg"]
                            return data
                    except:
                        pass
    
    return []


def create_entity_card(
    entity_type: str,
    name: str,
    attributes: dict,
    source_id: str = None,
    source_file: str = None,
) -> dict:
    """Create an entity card dictionary."""
    # Filter out None values from attributes
    clean_attrs = {k: v for k, v in attributes.items() if v is not None}
    
    return {
        "card_type": "entity",
        "entity_type": entity_type,
        "name": name,
        "attributes": clean_attrs,
        "source_id": source_id,
        "source_file": source_file,
    }


def save_entities(entities: list, output_path: Path, entity_type: str):
    """Save entity cards to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(entities, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"  Saved {len(entities):,} {entity_type} entities to {output_path.name}")


# =============================================================================
# Directory Lookup
# =============================================================================

class DirectoryLookup:
    """Lookup table for contact info from directory.json."""
    
    def __init__(self, input_dir: Path):
        self.lookup = {}  # normalized_name -> contact dict
        self.original_names = {}  # normalized_name -> original name
        self.used_names = set()  # Track names used by specialized entities
        
        self._load_directory(input_dir)
    
    def _load_directory(self, input_dir: Path):
        """Load directory.json into lookup table."""
        # Prefer deduplicated version
        dedup_path = input_dir / "dedup-output" / "directory_deduplicated.json"
        if dedup_path.exists():
            path = dedup_path
            print(f"  Using deduplicated directory: {dedup_path.name}")
        else:
            path = input_dir / "directory.json"
        
        entries = safe_load_json(path)
        
        for entry in entries:
            name = entry.get("full_name")
            if not name:
                continue
            
            normalized = normalize_name(name)
            if not normalized:
                continue
            
            contact = {
                "phone": entry.get("phone"),
                "email": entry.get("email"),
                "address": entry.get("address"),
                "fax": self._extract_fax(entry.get("phone")),
                "uuid": entry.get("uuid"),
            }
            
            self.lookup[normalized] = contact
            self.original_names[normalized] = name
        
        print(f"  Loaded {len(self.lookup):,} directory entries into lookup")
    
    def _extract_fax(self, phone: str) -> Optional[str]:
        """Extract fax number if phone field contains 'fax'."""
        if phone and "fax" in phone.lower():
            return phone
        return None
    
    def find(self, name: str, threshold: int = 85) -> dict:
        """
        Find contact info for a name.
        Returns empty dict if not found.
        """
        if not name:
            return {}
        
        normalized = normalize_name(name)
        
        # Exact match
        if normalized in self.lookup:
            self.used_names.add(normalized)
            return self.lookup[normalized]
        
        # Fuzzy match if available
        if HAS_FUZZY and threshold < 100:
            best_match = None
            best_score = 0
            
            for key in self.lookup:
                score = fuzz.ratio(normalized, key)
                if score > best_score and score >= threshold:
                    best_match = key
                    best_score = score
            
            if best_match:
                self.used_names.add(best_match)
                return self.lookup[best_match]
        
        return {}
    
    def mark_used(self, name: str):
        """Mark a name as used by a specialized entity."""
        normalized = normalize_name(name)
        if normalized:
            self.used_names.add(normalized)
    
    def get_unused_entries(self) -> list:
        """Get directory entries that weren't used by specialized entities."""
        unused = []
        for normalized, contact in self.lookup.items():
            if normalized not in self.used_names:
                unused.append({
                    "name": self.original_names[normalized],
                    "contact": contact,
                })
        return unused


# =============================================================================
# Entity Generators
# =============================================================================

def create_cases(input_dir: Path) -> list:
    """Generate Case entities from overview.json."""
    path = input_dir / "overview.json"
    entries = safe_load_json(path)
    
    entities = []
    
    for entry in entries:
        project_name = entry.get("project_name")
        if not project_name:
            continue
        
        # Determine case type from project name
        case_type = None
        if "-MVA-" in project_name:
            case_type = "MVA"
        elif "-Premise-" in project_name or "-S&F-" in project_name:
            case_type = "Premises"
        elif "-WC-" in project_name:
            case_type = "Workers Compensation"
        elif "-Med-Mal-" in project_name:
            case_type = "Medical Malpractice"
        
        entity = create_entity_card(
            entity_type="Case",
            name=project_name,
            attributes={
                "case_type": case_type,
                "accident_date": entry.get("accident_date"),
                "phase": entry.get("phase"),
                "total_medical_bills": entry.get("total_medical_bills"),
                "total_expenses": entry.get("total_expenses"),
                "total_liens": entry.get("total_liens"),
                "case_role": entry.get("case_role"),
                "case_summary": entry.get("case_summary"),
                "current_status": entry.get("current_status"),
            },
            source_id=project_name,
            source_file="overview.json",
        )
        entities.append(entity)
    
    return entities


def create_clients(input_dir: Path) -> list:
    """Generate Client entities from overview.json."""
    path = input_dir / "overview.json"
    entries = safe_load_json(path)
    
    entities = []
    seen_clients = set()
    
    for entry in entries:
        client_name = entry.get("client_name")
        if not client_name or client_name in seen_clients:
            continue
        
        seen_clients.add(client_name)
        
        entity = create_entity_card(
            entity_type="Client",
            name=client_name,
            attributes={
                "phone": entry.get("client_phone"),
                "email": entry.get("client_email"),
                "address": entry.get("client_address"),
            },
            source_id=client_name,
            source_file="overview.json",
        )
        entities.append(entity)
    
    return entities


def create_medical_providers(input_dir: Path, directory: DirectoryLookup) -> list:
    """Generate MedicalProvider entities by merging medical-providers.json + directory."""
    path = input_dir / "medical-providers.json"
    entries = safe_load_json(path)
    
    entities = []
    seen_providers = set()
    
    for entry in entries:
        provider_name = entry.get("provider_full_name")
        if not provider_name or provider_name in seen_providers:
            continue
        
        seen_providers.add(provider_name)
        
        # Get contact info from directory
        contact = directory.find(provider_name)
        
        # Determine specialty from name
        specialty = None
        name_lower = provider_name.lower()
        if "chiro" in name_lower:
            specialty = "chiropractic"
        elif "physical therapy" in name_lower or "rehab" in name_lower:
            specialty = "physical therapy"
        elif "orthop" in name_lower or "ortho" in name_lower:
            specialty = "orthopedic"
        elif "neurol" in name_lower:
            specialty = "neurology"
        elif "ems" in name_lower or "ambulance" in name_lower:
            specialty = "emergency medical services"
        elif "hospital" in name_lower or "medical center" in name_lower:
            specialty = "hospital"
        elif "pain" in name_lower:
            specialty = "pain management"
        elif "imaging" in name_lower or "radiol" in name_lower:
            specialty = "radiology"
        
        entity = create_entity_card(
            entity_type="MedicalProvider",
            name=provider_name,
            attributes={
                "specialty": specialty,
                "phone": contact.get("phone"),
                "fax": contact.get("fax"),
                "address": contact.get("address"),
            },
            source_id=str(entry.get("id")),
            source_file="medical-providers.json",
        )
        entities.append(entity)
        
        # Mark as used in directory
        directory.mark_used(provider_name)
    
    return entities


def create_insurers(input_dir: Path, directory: DirectoryLookup) -> list:
    """Generate Insurer entities from insurance.json + directory."""
    path = input_dir / "insurance.json"
    entries = safe_load_json(path)
    
    entities = []
    seen_insurers = set()
    
    for entry in entries:
        insurer_name = entry.get("insurance_company_name")
        if not insurer_name or insurer_name in seen_insurers:
            continue
        
        seen_insurers.add(insurer_name)
        
        # Get contact info from directory
        contact = directory.find(insurer_name)
        
        entity = create_entity_card(
            entity_type="Insurer",
            name=insurer_name,
            attributes={
                "phone": contact.get("phone"),
                "fax": contact.get("fax"),
                "address": contact.get("address"),
            },
            source_id=insurer_name,
            source_file="insurance.json",
        )
        entities.append(entity)
        
        directory.mark_used(insurer_name)
    
    return entities


def create_adjusters(input_dir: Path, directory: DirectoryLookup) -> list:
    """Generate Adjuster entities from insurance.json + directory."""
    path = input_dir / "insurance.json"
    entries = safe_load_json(path)
    
    entities = []
    seen_adjusters = set()
    
    for entry in entries:
        adjuster_name = entry.get("insurance_adjuster_name")
        insurer_name = entry.get("insurance_company_name")
        
        if not adjuster_name or not adjuster_name.strip() or adjuster_name in seen_adjusters:
            continue
        
        seen_adjusters.add(adjuster_name)
        
        # Get contact info from directory
        contact = directory.find(adjuster_name)
        
        entity = create_entity_card(
            entity_type="Adjuster",
            name=adjuster_name,
            attributes={
                "phone": contact.get("phone"),
                "email": contact.get("email"),
                "fax": contact.get("fax"),
            },
            source_id=adjuster_name,
            source_file="insurance.json",
        )
        entities.append(entity)
        
        directory.mark_used(adjuster_name)
    
    return entities


def create_insurance_claims(input_dir: Path) -> dict:
    """Generate insurance claim entities by type from insurance.json."""
    path = input_dir / "insurance.json"
    entries = safe_load_json(path)
    
    # Group by claim type
    claims_by_type = defaultdict(list)
    
    for entry in entries:
        project_name = entry.get("project_name")
        if not project_name:
            continue
        
        insurance_type = entry.get("insurance_type", "")
        entity_type = INSURANCE_TYPE_MAP.get(insurance_type)
        
        if not entity_type:
            continue  # Skip unknown types
        
        # Create claim name
        claim_number = entry.get("claim_number", "")
        claim_name = f"{project_name}-{insurance_type}"
        if claim_number:
            claim_name = f"{claim_name}-{claim_number}"
        
        entity = create_entity_card(
            entity_type=entity_type,
            name=claim_name,
            attributes={
                "claim_number": claim_number,
                "insurer_name": entry.get("insurance_company_name"),
                "adjuster_name": entry.get("insurance_adjuster_name"),
                "coverage_confirmation": entry.get("coverage_confirmation"),
                "demand_amount": entry.get("demanded_amount"),
                "current_offer": entry.get("current_offer"),
                "settlement_amount": entry.get("settlement_amount"),
                "settlement_date": entry.get("settlement_date"),
                "date_demand_sent": entry.get("date_demand_sent"),
                "is_active_negotiation": entry.get("is_active_negotiation"),
                "insurance_notes": entry.get("insurance_notes"),
                "project_name": project_name,
            },
            source_id=str(entry.get("id")),
            source_file="insurance.json",
        )
        
        claims_by_type[entity_type].append(entity)
    
    return dict(claims_by_type)


def create_liens(input_dir: Path) -> list:
    """Generate Lien entities from liens.json."""
    path = input_dir / "liens.json"
    entries = safe_load_json(path)
    
    entities = []
    
    for entry in entries:
        project_name = entry.get("project_name")
        lienholder_name = entry.get("lien_holder_name")
        
        if not project_name or not lienholder_name:
            continue
        
        # Determine lien type
        lien_type = "medical"
        name_lower = lienholder_name.lower()
        if "medicare" in name_lower:
            lien_type = "Medicare"
        elif "medicaid" in name_lower:
            lien_type = "Medicaid"
        elif any(term in name_lower for term in ["anthem", "humana", "aetna", "cigna", "bcbs", "blue cross"]):
            lien_type = "ERISA"
        elif "child support" in name_lower:
            lien_type = "child_support"
        
        lien_name = f"{project_name}-{lienholder_name}"
        
        entity = create_entity_card(
            entity_type="Lien",
            name=lien_name,
            attributes={
                "amount": entry.get("final_lien_amount") or entry.get("amount_owed_from_settlement"),
                "lien_type": lien_type,
                "lienholder_name": lienholder_name,
                "project_name": project_name,
                "date_notice_received": entry.get("date_notice_received"),
                "date_lien_paid": entry.get("date_lien_paid"),
                "reduction_amount": entry.get("reduction_amount"),
            },
            source_id=str(entry.get("id")),
            source_file="liens.json",
        )
        entities.append(entity)
    
    return entities


def create_lienholders(input_dir: Path, directory: DirectoryLookup) -> list:
    """Generate LienHolder entities from liens.json + directory."""
    path = input_dir / "liens.json"
    entries = safe_load_json(path)
    
    entities = []
    seen_lienholders = set()
    
    for entry in entries:
        lienholder_name = entry.get("lien_holder_name")
        
        if not lienholder_name or lienholder_name in seen_lienholders:
            continue
        
        seen_lienholders.add(lienholder_name)
        
        # Get contact info from directory
        contact = directory.find(lienholder_name)
        
        # Determine lien type
        lien_type = "medical"
        name_lower = lienholder_name.lower()
        if "medicare" in name_lower:
            lien_type = "Medicare"
        elif "medicaid" in name_lower:
            lien_type = "Medicaid"
        elif any(term in name_lower for term in ["anthem", "humana", "aetna", "cigna", "bcbs", "blue cross"]):
            lien_type = "ERISA"
        elif "child support" in name_lower:
            lien_type = "child_support"
        
        entity = create_entity_card(
            entity_type="LienHolder",
            name=lienholder_name,
            attributes={
                "lien_type": lien_type,
                "phone": contact.get("phone"),
                "fax": contact.get("fax"),
                "address": contact.get("address"),
            },
            source_id=lienholder_name,
            source_file="liens.json",
        )
        entities.append(entity)
        
        directory.mark_used(lienholder_name)
    
    return entities


def create_attorneys(input_dir: Path, directory: DirectoryLookup) -> list:
    """Generate Attorney entities from litigation_contacts.json + directory."""
    path = input_dir / "litigation_contacts.json"
    entries = safe_load_json(path)
    
    entities = []
    seen_attorneys = set()
    
    for entry in entries:
        role = entry.get("role", "")
        contact_name = entry.get("contact")
        
        if not contact_name or "attorney" not in role.lower():
            continue
        
        if contact_name in seen_attorneys:
            continue
        
        seen_attorneys.add(contact_name)
        
        # Get contact info from directory
        contact = directory.find(contact_name)
        
        # Determine role type
        attorney_role = "defense_counsel" if "defense" in role.lower() else "plaintiff_counsel"
        
        entity = create_entity_card(
            entity_type="Attorney",
            name=contact_name,
            attributes={
                "role": attorney_role,
                "phone": contact.get("phone"),
                "email": contact.get("email"),
            },
            source_id=str(entry.get("id")),
            source_file="litigation_contacts.json",
        )
        entities.append(entity)
        
        directory.mark_used(contact_name)
    
    return entities


def create_defendants(input_dir: Path) -> list:
    """Generate Defendant entities from litigation_contacts.json."""
    path = input_dir / "litigation_contacts.json"
    entries = safe_load_json(path)
    
    entities = []
    seen_defendants = set()
    
    for entry in entries:
        role = entry.get("role", "")
        contact_name = entry.get("contact")
        project_name = entry.get("project_name")
        
        if not contact_name or "defendant" not in role.lower():
            continue
        
        # Use project_name + contact as key for uniqueness
        key = f"{project_name}-{contact_name}"
        if key in seen_defendants:
            continue
        
        seen_defendants.add(key)
        
        entity = create_entity_card(
            entity_type="Defendant",
            name=contact_name,
            attributes={
                "project_name": project_name,
            },
            source_id=str(entry.get("id")),
            source_file="litigation_contacts.json",
        )
        entities.append(entity)
    
    return entities


def create_pleadings(input_dir: Path) -> list:
    """Generate Pleading entities from pleadings.json."""
    path = input_dir / "pleadings.json"
    entries = safe_load_json(path)
    
    entities = []
    
    for entry in entries:
        project_name = entry.get("project_name")
        pleading_type = entry.get("pleading_type")
        
        if not project_name or not pleading_type:
            continue
        
        # Create pleading name
        filing_date = entry.get("certificate_of_service", "")
        pleading_name = f"{project_name}-{pleading_type}"
        if filing_date:
            pleading_name = f"{pleading_name}-{filing_date}"
        
        entity = create_entity_card(
            entity_type="Pleading",
            name=pleading_name,
            attributes={
                "pleading_type": pleading_type,
                "filed_date": entry.get("certificate_of_service"),
                "filed_by": entry.get("filing_party_name"),
                "project_name": project_name,
                "notes": entry.get("pleadings_notes"),
                "hearing_date": entry.get("motion_hour_or_hearing_date"),
                "hearing_type": entry.get("telephonic_or_zoom_or_in_person"),
            },
            source_id=str(entry.get("id")),
            source_file="pleadings.json",
        )
        entities.append(entity)
    
    return entities


def create_directory_entries(directory: DirectoryLookup) -> list:
    """Generate DirectoryEntry entities for unused directory entries."""
    unused = directory.get_unused_entries()
    
    entities = []
    
    for item in unused:
        name = item["name"]
        contact = item["contact"]
        
        entity = create_entity_card(
            entity_type="DirectoryEntry",
            name=name,
            attributes={
                "phone": contact.get("phone"),
                "email": contact.get("email"),
                "address": contact.get("address"),
                "fax": contact.get("fax"),
            },
            source_id=str(contact.get("uuid")),
            source_file="directory.json",
        )
        entities.append(entity)
    
    return entities


# =============================================================================
# Main Processing
# =============================================================================

def create_all_entity_files(input_dir: Path, output_dir: Path) -> dict:
    """Create all entity files."""
    stats = {
        "total_entities": 0,
        "by_type": {},
        "directory_match_rate": 0,
    }
    
    print("=" * 60)
    print("CREATE CLEAN ENTITY FILES")
    print("=" * 60)
    print(f"\nInput directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # Step 1: Load directory lookup
    print("\n--- Loading Directory Lookup ---")
    directory = DirectoryLookup(input_dir)
    
    # Step 2: Generate each entity type
    print("\n--- Generating Entity Files ---")
    
    # Cases
    print("\n1. Cases...")
    cases = create_cases(input_dir)
    save_entities(cases, output_dir / "cases.json", "Case")
    stats["by_type"]["Case"] = len(cases)
    
    # Clients
    print("\n2. Clients...")
    clients = create_clients(input_dir)
    save_entities(clients, output_dir / "clients.json", "Client")
    stats["by_type"]["Client"] = len(clients)
    
    # Medical Providers (with directory merge)
    print("\n3. Medical Providers (merging with directory)...")
    providers = create_medical_providers(input_dir, directory)
    save_entities(providers, output_dir / "medical_providers.json", "MedicalProvider")
    stats["by_type"]["MedicalProvider"] = len(providers)
    
    # Insurers (with directory merge)
    print("\n4. Insurers (merging with directory)...")
    insurers = create_insurers(input_dir, directory)
    save_entities(insurers, output_dir / "insurers.json", "Insurer")
    stats["by_type"]["Insurer"] = len(insurers)
    
    # Adjusters (with directory merge)
    print("\n5. Adjusters (merging with directory)...")
    adjusters = create_adjusters(input_dir, directory)
    save_entities(adjusters, output_dir / "adjusters.json", "Adjuster")
    stats["by_type"]["Adjuster"] = len(adjusters)
    
    # Insurance Claims by type
    print("\n6. Insurance Claims (by type)...")
    claims_by_type = create_insurance_claims(input_dir)
    for claim_type, claims in claims_by_type.items():
        filename = f"{claim_type.lower()}_claims.json"
        save_entities(claims, output_dir / filename, claim_type)
        stats["by_type"][claim_type] = len(claims)
    
    # Liens
    print("\n7. Liens...")
    liens = create_liens(input_dir)
    save_entities(liens, output_dir / "liens.json", "Lien")
    stats["by_type"]["Lien"] = len(liens)
    
    # LienHolders (with directory merge)
    print("\n8. LienHolders (merging with directory)...")
    lienholders = create_lienholders(input_dir, directory)
    save_entities(lienholders, output_dir / "lienholders.json", "LienHolder")
    stats["by_type"]["LienHolder"] = len(lienholders)
    
    # Attorneys (with directory merge)
    print("\n9. Attorneys (merging with directory)...")
    attorneys = create_attorneys(input_dir, directory)
    save_entities(attorneys, output_dir / "attorneys.json", "Attorney")
    stats["by_type"]["Attorney"] = len(attorneys)
    
    # Defendants
    print("\n10. Defendants...")
    defendants = create_defendants(input_dir)
    save_entities(defendants, output_dir / "defendants.json", "Defendant")
    stats["by_type"]["Defendant"] = len(defendants)
    
    # Pleadings
    print("\n11. Pleadings...")
    pleadings = create_pleadings(input_dir)
    save_entities(pleadings, output_dir / "pleadings.json", "Pleading")
    stats["by_type"]["Pleading"] = len(pleadings)
    
    # DirectoryEntry (only unused)
    print("\n12. Directory Entries (unused only)...")
    directory_entries = create_directory_entries(directory)
    save_entities(directory_entries, output_dir / "directory_entries.json", "DirectoryEntry")
    stats["by_type"]["DirectoryEntry"] = len(directory_entries)
    
    # Calculate totals
    stats["total_entities"] = sum(stats["by_type"].values())
    stats["directory_used"] = len(directory.used_names)
    stats["directory_total"] = len(directory.lookup)
    stats["directory_match_rate"] = round(
        len(directory.used_names) / len(directory.lookup) * 100, 1
    ) if directory.lookup else 0
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nTotal entities generated: {stats['total_entities']:,}")
    print(f"\nDirectory lookup utilization:")
    print(f"  - Total entries: {stats['directory_total']:,}")
    print(f"  - Matched to specialized types: {stats['directory_used']:,}")
    print(f"  - Match rate: {stats['directory_match_rate']}%")
    print(f"\nBy type:")
    for entity_type, count in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
        print(f"  {entity_type:20} {count:,}")
    
    # Save stats
    stats["generated_at"] = datetime.now().isoformat()
    stats_path = output_dir / "entity_generation_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nStats saved to {stats_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Create clean entity JSON files")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=INPUT_DIR,
        help="Directory containing source JSON files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory for output entity files"
    )
    
    args = parser.parse_args()
    
    if not args.input_dir.exists():
        print(f"Error: Input directory not found: {args.input_dir}")
        return 1
    
    create_all_entity_files(args.input_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    exit(main())
