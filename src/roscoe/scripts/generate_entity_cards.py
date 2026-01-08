#!/usr/bin/env python3
"""
Stage 1: Entity Card Generation

Generates Entity Cards from source JSON files:
- directory.json → DirectoryEntry
- overview.json → Case, Client
- insurance.json → PIPClaim, BIClaim, etc., Insurer, Adjuster
- medical-providers.json → MedicalProvider
- liens.json → Lien, LienHolder

Usage:
    python generate_entity_cards.py [--input-dir path] [--output-dir path]
"""

import json
import re
import argparse
from pathlib import Path
from typing import Optional
from collections import defaultdict

from memory_card_schema import (
    EntityCard, 
    create_entity_card,
    ALL_ENTITY_TYPES,
)


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
    "Property Damage (PD)": "PropertyDamageClaim",  # Not in our types, use generic
    "Collision": "CollisionClaim",  # Not in our types, use generic
    # Default fallback
    None: "InsuranceClaim",
}


# =============================================================================
# Entity Generators
# =============================================================================

def generate_directory_entries(input_dir: Path) -> list[EntityCard]:
    """
    Generate DirectoryEntry entities from directory.json.
    Uses deduplicated version if available.
    """
    # Prefer deduplicated version
    dedup_path = input_dir / "dedup-output" / "directory_deduplicated.json"
    if dedup_path.exists():
        path = dedup_path
        print(f"  Using deduplicated directory: {dedup_path}")
    else:
        path = input_dir / "directory.json"
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle nested jsonb_agg format
    if isinstance(data, list) and len(data) == 1 and "jsonb_agg" in data[0]:
        entries = data[0]["jsonb_agg"]
    elif isinstance(data, list):
        entries = data
    else:
        entries = [data]
    
    cards = []
    for entry in entries:
        if not entry.get("full_name"):
            continue
        
        card = create_entity_card(
            entity_type="DirectoryEntry",
            name=entry["full_name"],
            attributes={
                "phone": entry.get("phone"),
                "email": entry.get("email"),
                "address": entry.get("address"),
                "phone_normalized": entry.get("phone_normalized"),
            },
            source_id=str(entry.get("uuid")),
            source_file="directory.json",
        )
        cards.append(card)
    
    return cards


def safe_load_json(path: Path) -> list:
    """
    Safely load JSON that might have corruption at the end.
    Returns a list of entries.
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try normal parsing first
    try:
        data = json.loads(content)
        # Handle nested jsonb_agg format
        if isinstance(data, list) and len(data) >= 1 and isinstance(data[0], dict) and "jsonb_agg" in data[0]:
            return data[0]["jsonb_agg"]
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        pass
    
    # Handle file corruption - try to extract valid JSON
    # Look for the pattern [{ ... }] and extract properly
    content = content.strip()
    
    # If it doesn't start with [, wrap it
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
    # But handle nested structures properly
    bracket_stack = []
    for i, char in enumerate(content):
        if char == '[':
            bracket_stack.append(i)
        elif char == ']':
            if bracket_stack:
                start = bracket_stack.pop()
                if len(bracket_stack) == 0:
                    # Found the matching outer bracket
                    try:
                        data = json.loads(content[:i+1])
                        if isinstance(data, list) and len(data) >= 1:
                            if isinstance(data[0], dict) and "jsonb_agg" in data[0]:
                                return data[0]["jsonb_agg"]
                            return data
                    except:
                        pass
    
    return []


def generate_cases_and_clients(input_dir: Path) -> tuple[list[EntityCard], list[EntityCard]]:
    """
    Generate Case and Client entities from overview.json.
    """
    path = input_dir / "overview.json"
    entries = safe_load_json(path)
    
    cases = []
    clients = []
    seen_clients = set()
    
    for entry in entries:
        project_name = entry.get("project_name")
        if not project_name:
            continue
        
        # Extract accident date from project name if not in data
        accident_date = entry.get("accident_date")
        
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
        
        # Create Case entity
        case_card = create_entity_card(
            entity_type="Case",
            name=project_name,
            attributes={
                "case_type": case_type,
                "accident_date": accident_date,
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
        cases.append(case_card)
        
        # Create Client entity (deduplicated)
        client_name = entry.get("client_name")
        if client_name and client_name not in seen_clients:
            seen_clients.add(client_name)
            
            client_card = create_entity_card(
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
            clients.append(client_card)
    
    return cases, clients


def generate_insurance_entities(input_dir: Path) -> tuple[list[EntityCard], list[EntityCard], list[EntityCard]]:
    """
    Generate insurance-related entities from insurance.json:
    - Insurance Claims (PIPClaim, BIClaim, etc.)
    - Insurers
    - Adjusters
    """
    path = input_dir / "insurance.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    claims = []
    insurers = []
    adjusters = []
    
    seen_insurers = set()
    seen_adjusters = set()
    
    for entry in data:
        project_name = entry.get("project_name")
        if not project_name:
            continue
        
        # Determine claim type
        insurance_type = entry.get("insurance_type", "")
        entity_type = INSURANCE_TYPE_MAP.get(insurance_type, "InsuranceClaim")
        
        # Use a generic InsuranceClaim if type not in our model
        if entity_type not in ALL_ENTITY_TYPES:
            entity_type = "PIPClaim"  # Default to PIPClaim as fallback
        
        # Create claim name from project + type + claim number
        claim_number = entry.get("claim_number", "")
        claim_name = f"{project_name}-{insurance_type}-{claim_number}" if claim_number else f"{project_name}-{insurance_type}"
        
        claim_card = create_entity_card(
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
        claims.append(claim_card)
        
        # Create Insurer entity (deduplicated)
        insurer_name = entry.get("insurance_company_name")
        if insurer_name and insurer_name not in seen_insurers:
            seen_insurers.add(insurer_name)
            
            insurer_card = create_entity_card(
                entity_type="Insurer",
                name=insurer_name,
                attributes={},
                source_id=insurer_name,
                source_file="insurance.json",
            )
            insurers.append(insurer_card)
        
        # Create Adjuster entity (deduplicated)
        adjuster_name = entry.get("insurance_adjuster_name")
        if adjuster_name and adjuster_name.strip() and adjuster_name not in seen_adjusters:
            seen_adjusters.add(adjuster_name)
            
            adjuster_card = create_entity_card(
                entity_type="Adjuster",
                name=adjuster_name,
                attributes={
                    "insurer": insurer_name,
                },
                source_id=adjuster_name,
                source_file="insurance.json",
            )
            adjusters.append(adjuster_card)
    
    return claims, insurers, adjusters


def generate_medical_providers(input_dir: Path) -> list[EntityCard]:
    """
    Generate MedicalProvider entities from medical-providers.json.
    """
    path = input_dir / "medical-providers.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cards = []
    seen_providers = set()
    
    for entry in data:
        provider_name = entry.get("provider_full_name")
        if not provider_name or provider_name in seen_providers:
            continue
        
        seen_providers.add(provider_name)
        
        # Try to determine specialty from name
        specialty = None
        name_lower = provider_name.lower()
        if "chiro" in name_lower:
            specialty = "chiropractic"
        elif "physical therapy" in name_lower or "pt" in name_lower or "rehab" in name_lower:
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
        
        card = create_entity_card(
            entity_type="MedicalProvider",
            name=provider_name,
            attributes={
                "specialty": specialty,
            },
            source_id=str(entry.get("id")),
            source_file="medical-providers.json",
        )
        cards.append(card)
    
    return cards


def generate_liens_and_lienholders(input_dir: Path) -> tuple[list[EntityCard], list[EntityCard]]:
    """
    Generate Lien and LienHolder entities from liens.json.
    """
    path = input_dir / "liens.json"
    data = safe_load_json(path)
    
    liens = []
    lienholders = []
    seen_lienholders = set()
    
    for entry in data:
        project_name = entry.get("project_name")
        lienholder_name = entry.get("lien_holder_name")
        
        if not project_name or not lienholder_name:
            continue
        
        # Determine lien type from lienholder name
        lien_type = None
        name_lower = lienholder_name.lower()
        if "medicare" in name_lower:
            lien_type = "Medicare"
        elif "medicaid" in name_lower:
            lien_type = "Medicaid"
        elif "anthem" in name_lower or "humana" in name_lower or "aetna" in name_lower or "cigna" in name_lower:
            lien_type = "ERISA"
        elif "child support" in name_lower:
            lien_type = "child_support"
        else:
            lien_type = "medical"
        
        # Create lien name
        lien_name = f"{project_name}-{lienholder_name}"
        
        lien_card = create_entity_card(
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
        liens.append(lien_card)
        
        # Create LienHolder entity (deduplicated)
        if lienholder_name not in seen_lienholders:
            seen_lienholders.add(lienholder_name)
            
            lienholder_card = create_entity_card(
                entity_type="LienHolder",
                name=lienholder_name,
                attributes={
                    "lien_type": lien_type,
                },
                source_id=lienholder_name,
                source_file="liens.json",
            )
            lienholders.append(lienholder_card)
    
    return liens, lienholders


# =============================================================================
# Main Processing
# =============================================================================

def save_entity_cards(cards: list[EntityCard], output_path: Path, entity_type: str):
    """Save entity cards to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to list of dicts
    data = [card.model_dump() for card in cards]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"  Saved {len(cards):,} {entity_type} entities to {output_path.name}")


def generate_all_entities(input_dir: Path, output_dir: Path) -> dict:
    """
    Generate all entity cards from source files.
    
    Returns:
        Statistics dictionary
    """
    stats = {
        "total_entities": 0,
        "by_type": {},
    }
    
    print("Generating Entity Cards...")
    print("=" * 60)
    
    # 1. Directory entries
    print("\n1. Processing directory.json...")
    directory_entries = generate_directory_entries(input_dir)
    save_entity_cards(directory_entries, output_dir / "directory_entries.json", "DirectoryEntry")
    stats["by_type"]["DirectoryEntry"] = len(directory_entries)
    
    # 2. Cases and Clients
    print("\n2. Processing overview.json...")
    cases, clients = generate_cases_and_clients(input_dir)
    save_entity_cards(cases, output_dir / "cases.json", "Case")
    save_entity_cards(clients, output_dir / "clients.json", "Client")
    stats["by_type"]["Case"] = len(cases)
    stats["by_type"]["Client"] = len(clients)
    
    # 3. Insurance entities
    print("\n3. Processing insurance.json...")
    claims, insurers, adjusters = generate_insurance_entities(input_dir)
    save_entity_cards(claims, output_dir / "insurance_claims.json", "InsuranceClaim")
    save_entity_cards(insurers, output_dir / "insurers.json", "Insurer")
    save_entity_cards(adjusters, output_dir / "adjusters.json", "Adjuster")
    stats["by_type"]["InsuranceClaim"] = len(claims)
    stats["by_type"]["Insurer"] = len(insurers)
    stats["by_type"]["Adjuster"] = len(adjusters)
    
    # 4. Medical providers
    print("\n4. Processing medical-providers.json...")
    providers = generate_medical_providers(input_dir)
    save_entity_cards(providers, output_dir / "medical_providers.json", "MedicalProvider")
    stats["by_type"]["MedicalProvider"] = len(providers)
    
    # 5. Liens and lienholders
    print("\n5. Processing liens.json...")
    liens, lienholders = generate_liens_and_lienholders(input_dir)
    save_entity_cards(liens, output_dir / "liens.json", "Lien")
    save_entity_cards(lienholders, output_dir / "lienholders.json", "LienHolder")
    stats["by_type"]["Lien"] = len(liens)
    stats["by_type"]["LienHolder"] = len(lienholders)
    
    # Calculate totals
    stats["total_entities"] = sum(stats["by_type"].values())
    
    # Print summary
    print("\n" + "=" * 60)
    print("ENTITY GENERATION SUMMARY")
    print("=" * 60)
    print(f"\nTotal entities generated: {stats['total_entities']:,}")
    print("\nBy type:")
    for entity_type, count in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
        print(f"  {entity_type:20} {count:,}")
    
    # Save stats
    stats_path = output_dir / "entity_generation_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nStats saved to {stats_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Generate Entity Cards from source JSON files")
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
        help="Directory for output entity card files"
    )
    
    args = parser.parse_args()
    
    if not args.input_dir.exists():
        print(f"Error: Input directory not found: {args.input_dir}")
        return 1
    
    generate_all_entities(args.input_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    exit(main())
