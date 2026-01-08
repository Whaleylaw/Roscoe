#!/usr/bin/env python3
"""
Stage 2: Relationship Card Generation

Generates Relationship Cards from source JSON files:
- Case HasClient Client (from overview.json)
- Case HasClaim Claims (from insurance.json)
- Claim InsuredBy Insurer (from insurance.json)
- Claim AssignedAdjuster Adjuster (from insurance.json)
- Case TreatingAt MedicalProvider (from medical-providers.json)
- Case HasLien Lien (from liens.json)
- Lien HeldBy LienHolder (from liens.json)

Usage:
    python generate_relationship_cards.py [--input-dir path] [--output-dir path]
"""

import json
import argparse
from pathlib import Path
from collections import defaultdict

from memory_card_schema import (
    RelationshipCard,
    create_relationship_card,
)
from generate_entity_cards import safe_load_json, INPUT_DIR, INSURANCE_TYPE_MAP

OUTPUT_DIR = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/relationships")


# =============================================================================
# Relationship Generators
# =============================================================================

def generate_case_client_relationships(input_dir: Path) -> list[RelationshipCard]:
    """
    Generate Case-Client relationships from overview.json.
    """
    path = input_dir / "overview.json"
    entries = safe_load_json(path)
    
    cards = []
    for entry in entries:
        project_name = entry.get("project_name")
        client_name = entry.get("client_name")
        
        if not project_name or not client_name:
            continue
        
        # Case HasClient Client
        card = create_relationship_card(
            edge_type="HasClient",
            source_type="Case",
            source_name=project_name,
            target_type="Client",
            target_name=client_name,
            attributes={
                "case_create_date": entry.get("case_create_date"),
            },
            context=project_name,
        )
        cards.append(card)
        
        # Also create Client PlaintiffIn Case (reverse relationship)
        card2 = create_relationship_card(
            edge_type="PlaintiffIn",
            source_type="Client",
            source_name=client_name,
            target_type="Case",
            target_name=project_name,
            attributes={},
            context=project_name,
        )
        cards.append(card2)
    
    return cards


def generate_insurance_relationships(input_dir: Path) -> list[RelationshipCard]:
    """
    Generate insurance-related relationships from insurance.json:
    - Case HasClaim Claim
    - Claim InsuredBy Insurer
    - Claim AssignedAdjuster Adjuster
    """
    path = input_dir / "insurance.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cards = []
    
    for entry in data:
        project_name = entry.get("project_name")
        if not project_name:
            continue
        
        # Determine claim type and name
        insurance_type = entry.get("insurance_type", "")
        entity_type = INSURANCE_TYPE_MAP.get(insurance_type, "InsuranceClaim")
        if entity_type not in ["PIPClaim", "BIClaim", "UMClaim", "UIMClaim", "WCClaim", "MedPayClaim"]:
            entity_type = "PIPClaim"  # Default fallback
        
        claim_number = entry.get("claim_number", "")
        claim_name = f"{project_name}-{insurance_type}-{claim_number}" if claim_number else f"{project_name}-{insurance_type}"
        
        # Case HasClaim Claim
        card = create_relationship_card(
            edge_type="HasClaim",
            source_type="Case",
            source_name=project_name,
            target_type=entity_type,
            target_name=claim_name,
            attributes={
                "claim_type": insurance_type,
            },
            context=project_name,
        )
        cards.append(card)
        
        # Claim InsuredBy Insurer
        insurer_name = entry.get("insurance_company_name")
        if insurer_name:
            card = create_relationship_card(
                edge_type="InsuredBy",
                source_type=entity_type,
                source_name=claim_name,
                target_type="Insurer",
                target_name=insurer_name,
                attributes={
                    "policy_number": entry.get("claim_number"),
                },
                context=project_name,
            )
            cards.append(card)
        
        # Claim AssignedAdjuster Adjuster
        adjuster_name = entry.get("insurance_adjuster_name")
        if adjuster_name and adjuster_name.strip():
            card = create_relationship_card(
                edge_type="AssignedAdjuster",
                source_type=entity_type,
                source_name=claim_name,
                target_type="Adjuster",
                target_name=adjuster_name,
                attributes={},
                context=project_name,
            )
            cards.append(card)
            
            # Also Adjuster HandlesInsuranceClaim Claim
            card2 = create_relationship_card(
                edge_type="HandlesInsuranceClaim",
                source_type="Adjuster",
                source_name=adjuster_name,
                target_type=entity_type,
                target_name=claim_name,
                attributes={},
                context=project_name,
            )
            cards.append(card2)
            
            # Adjuster WorksAt Insurer
            if insurer_name:
                card3 = create_relationship_card(
                    edge_type="WorksAt",
                    source_type="Adjuster",
                    source_name=adjuster_name,
                    target_type="Insurer",
                    target_name=insurer_name,
                    attributes={},
                    context=project_name,
                )
                cards.append(card3)
    
    return cards


def generate_medical_provider_relationships(input_dir: Path) -> list[RelationshipCard]:
    """
    Generate Case-MedicalProvider relationships from medical-providers.json.
    """
    path = input_dir / "medical-providers.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cards = []
    
    for entry in data:
        project_name = entry.get("project_name")
        provider_name = entry.get("provider_full_name")
        
        if not project_name or not provider_name:
            continue
        
        # Case TreatingAt MedicalProvider
        card = create_relationship_card(
            edge_type="TreatingAt",
            source_type="Case",
            source_name=project_name,
            target_type="MedicalProvider",
            target_name=provider_name,
            attributes={
                "start_date": entry.get("date_treatment_started"),
                "end_date": entry.get("date_treatment_completed"),
                "billed_amount": entry.get("billed_amount"),
                "number_of_visits": entry.get("number_of_visits"),
            },
            context=project_name,
        )
        cards.append(card)
        
        # MedicalProvider TreatedBy Case (reverse)
        card2 = create_relationship_card(
            edge_type="TreatedBy",
            source_type="MedicalProvider",
            source_name=provider_name,
            target_type="Case",
            target_name=project_name,
            attributes={
                "billed_amount": entry.get("billed_amount"),
            },
            context=project_name,
        )
        cards.append(card2)
    
    return cards


def generate_lien_relationships(input_dir: Path) -> list[RelationshipCard]:
    """
    Generate lien-related relationships from liens.json:
    - Case HasLien Lien
    - Lien HeldBy LienHolder
    """
    path = input_dir / "liens.json"
    data = safe_load_json(path)
    
    cards = []
    
    for entry in data:
        project_name = entry.get("project_name")
        lienholder_name = entry.get("lien_holder_name")
        
        if not project_name or not lienholder_name:
            continue
        
        lien_name = f"{project_name}-{lienholder_name}"
        
        # Case HasLien Lien
        card = create_relationship_card(
            edge_type="HasLien",
            source_type="Case",
            source_name=project_name,
            target_type="Lien",
            target_name=lien_name,
            attributes={
                "amount": entry.get("final_lien_amount") or entry.get("amount_owed_from_settlement"),
            },
            context=project_name,
        )
        cards.append(card)
        
        # Case HasLienFrom LienHolder
        card2 = create_relationship_card(
            edge_type="HasLienFrom",
            source_type="Case",
            source_name=project_name,
            target_type="LienHolder",
            target_name=lienholder_name,
            attributes={
                "amount": entry.get("final_lien_amount") or entry.get("amount_owed_from_settlement"),
            },
            context=project_name,
        )
        cards.append(card2)
        
        # Lien HeldBy LienHolder
        card3 = create_relationship_card(
            edge_type="HeldBy",
            source_type="Lien",
            source_name=lien_name,
            target_type="LienHolder",
            target_name=lienholder_name,
            attributes={},
            context=project_name,
        )
        cards.append(card3)
        
        # LienHolder Holds Lien (reverse)
        card4 = create_relationship_card(
            edge_type="Holds",
            source_type="LienHolder",
            source_name=lienholder_name,
            target_type="Lien",
            target_name=lien_name,
            attributes={},
            context=project_name,
        )
        cards.append(card4)
    
    return cards


# =============================================================================
# Main Processing
# =============================================================================

def save_relationship_cards(cards: list[RelationshipCard], output_path: Path, description: str):
    """Save relationship cards to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to list of dicts
    data = [card.model_dump() for card in cards]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"  Saved {len(cards):,} {description} relationships to {output_path.name}")


def generate_all_relationships(input_dir: Path, output_dir: Path) -> dict:
    """
    Generate all relationship cards from source files.
    """
    stats = {
        "total_relationships": 0,
        "by_type": defaultdict(int),
    }
    
    print("Generating Relationship Cards...")
    print("=" * 60)
    
    all_cards = []
    
    # 1. Case-Client relationships
    print("\n1. Generating Case-Client relationships...")
    case_client_cards = generate_case_client_relationships(input_dir)
    all_cards.extend(case_client_cards)
    for card in case_client_cards:
        stats["by_type"][card.edge_type] += 1
    
    # 2. Insurance relationships
    print("\n2. Generating Insurance relationships...")
    insurance_cards = generate_insurance_relationships(input_dir)
    all_cards.extend(insurance_cards)
    for card in insurance_cards:
        stats["by_type"][card.edge_type] += 1
    
    # 3. Medical provider relationships
    print("\n3. Generating Medical Provider relationships...")
    provider_cards = generate_medical_provider_relationships(input_dir)
    all_cards.extend(provider_cards)
    for card in provider_cards:
        stats["by_type"][card.edge_type] += 1
    
    # 4. Lien relationships
    print("\n4. Generating Lien relationships...")
    lien_cards = generate_lien_relationships(input_dir)
    all_cards.extend(lien_cards)
    for card in lien_cards:
        stats["by_type"][card.edge_type] += 1
    
    # Save all relationships
    save_relationship_cards(all_cards, output_dir / "all_relationships.json", "all")
    
    # Also save by type for easier debugging
    by_type = defaultdict(list)
    for card in all_cards:
        by_type[card.edge_type].append(card)
    
    for edge_type, cards in by_type.items():
        save_relationship_cards(cards, output_dir / f"{edge_type.lower()}_relationships.json", edge_type)
    
    stats["total_relationships"] = len(all_cards)
    
    # Print summary
    print("\n" + "=" * 60)
    print("RELATIONSHIP GENERATION SUMMARY")
    print("=" * 60)
    print(f"\nTotal relationships generated: {stats['total_relationships']:,}")
    print("\nBy type:")
    for edge_type, count in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
        print(f"  {edge_type:25} {count:,}")
    
    # Save stats
    stats_path = output_dir / "relationship_generation_stats.json"
    stats["by_type"] = dict(stats["by_type"])
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\nStats saved to {stats_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Generate Relationship Cards from source JSON files")
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
        help="Directory for output relationship card files"
    )
    
    args = parser.parse_args()
    
    if not args.input_dir.exists():
        print(f"Error: Input directory not found: {args.input_dir}")
        return 1
    
    generate_all_relationships(args.input_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    exit(main())
