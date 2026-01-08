#!/usr/bin/env python3
"""
Regenerate all review documents with improved consolidation logic.

Reads existing review files, extracts proposed entities, applies
improved fuzzy matching and consolidation, then regenerates.
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from roscoe.scripts.generate_review_docs import (
    consolidate_proposed_entities,
    load_global_entities,
    fuzzy_match_entity,
    fuzzy_match_doctor,
    check_whaley_staff,
    normalize_name
)


def extract_entities_from_review(review_file: Path) -> tuple[dict, dict, dict]:
    """
    Extract case entities, proposed entities, and user annotations from existing review.

    Returns: (case_entities, proposed_entities, user_annotations)
    """
    with open(review_file) as f:
        content = f.read()

    case_entities = {
        'providers': [],
        'claims': [],
        'liens': [],
        'attorneys': [],
        'courts': [],
        'defendants': []
    }

    proposed_entities = defaultdict(set)
    user_annotations = {}  # entity_name -> annotation text

    # Extract case entities from Section 1
    # Medical Providers
    provider_section = re.search(r'### Medical Providers \((\d+)\)(.*?)(?=###|---|\Z)', content, re.DOTALL)
    if provider_section:
        for line in provider_section.group(2).strip().split('\n'):
            if line.startswith('- '):
                # Format: "- Name (specialty)" or "- Name"
                match = re.match(r'-\s+([^(]+)(?:\s*\(([^)]+)\))?', line)
                if match:
                    case_entities['providers'].append({
                        'name': match.group(1).strip(),
                        'specialty': match.group(2).strip() if match.group(2) else ''
                    })

    # Insurance Claims
    claims_section = re.search(r'### Insurance Claims \((\d+)\)(.*?)(?=###|---|\Z)', content, re.DOTALL)
    if claims_section:
        current_claim = None
        for line in claims_section.group(2).strip().split('\n'):
            if line.startswith('- **'):
                # Format: "- **ClaimType**: Insurer"
                match = re.match(r'-\s+\*\*([^*]+)\*\*:\s+(.+)', line)
                if match:
                    current_claim = {
                        'type': match.group(1).strip(),
                        'insurer': match.group(2).strip(),
                        'adjuster': ''
                    }
                    case_entities['claims'].append(current_claim)
            elif line.strip().startswith('- Adjuster:') and current_claim:
                adjuster = line.split(':', 1)[1].strip()
                current_claim['adjuster'] = adjuster

    # Liens
    liens_section = re.search(r'### Liens \((\d+)\)(.*?)(?=###|---|\Z)', content, re.DOTALL)
    if liens_section:
        for line in liens_section.group(2).strip().split('\n'):
            if line.startswith('- '):
                # Format: "- Holder ($amount)" or "- Holder"
                match = re.match(r'-\s+([^($]+)(?:\s*\(\$([0-9,.]+)\))?', line)
                if match:
                    amount_str = match.group(2)
                    amount = float(amount_str.replace(',', '')) if amount_str else 0.0
                    case_entities['liens'].append({
                        'holder': match.group(1).strip(),
                        'amount': amount
                    })

    # Extract proposed entities from Section 2
    # Pattern: ### EntityType (N unique) followed by entity lines
    sections = re.split(r'\n### ([A-Za-z]+) \((\d+) (?:unique|consolidated)\)', content)

    for i in range(1, len(sections), 3):
        entity_type = sections[i]
        section_content = sections[i+2] if i+2 < len(sections) else ""

        # Extract all entities (both NEW and EXISTS) with annotations
        # Pattern: - [ ] Name — *status* [optional user annotation]
        for line in section_content.split('\n'):
            if line.strip().startswith('- [ ]'):
                # Extract entity name and annotation
                # Pattern: - [ ] **Name** — *status* annotation or - [ ] Name — *status* annotation
                match = re.match(r'- \[ \] (?:\*\*)?([^*—]+?)(?:\*\*)? — \*(?:[^*]+)\*\s*(.*)', line)
                if match:
                    entity_name = match.group(1).strip()
                    annotation = match.group(2).strip()

                    if entity_name:
                        proposed_entities[entity_type].add(entity_name)
                        if annotation:
                            user_annotations[entity_name] = annotation

    return case_entities, proposed_entities, user_annotations


def find_entity_context(case_name: str, entity_name: str, episodes_dir: Path) -> list[dict]:
    """Find episode context where entity is mentioned."""
    processed_file = episodes_dir / f"processed_{case_name}.json"
    if not processed_file.exists():
        return []

    with open(processed_file) as f:
        data = json.load(f)

    contexts = []
    for ep in data.get('episodes', []):
        for rel in ep.get('proposed_relationships', {}).get('about', []):
            if rel.get('entity_name') == entity_name:
                contexts.append({
                    'episode_name': ep.get('episode_name', ''),
                    'natural_language': ep.get('natural_language', '')[:300],  # First 300 chars
                    'relevance': rel.get('relevance', '')
                })
                if len(contexts) >= 2:  # Max 2 examples
                    return contexts

    return contexts


def regenerate_review(review_file: Path, global_entities: dict, output_dir: Path, episodes_dir: Path):
    """Regenerate a single review file with improved logic."""
    # Extract data from existing review
    case_entities, proposed_entities_raw, user_annotations = extract_entities_from_review(review_file)

    # Consolidate duplicates
    consolidated = consolidate_proposed_entities(proposed_entities_raw)

    # Get case name from filename
    case_name = review_file.stem.replace('review_', '')

    # Count total episodes and relationships from original review
    with open(review_file) as f:
        content = f.read()

    total_episodes = 0
    total_relationships = 0

    ep_match = re.search(r'\*\*Total Episodes:\*\* (\d+)', content)
    if ep_match:
        total_episodes = int(ep_match.group(1))

    rel_match = re.search(r'\*\*Total Proposed Relationships:\*\* (\d+)', content)
    if rel_match:
        total_relationships = int(rel_match.group(1))

    # Build regenerated review
    lines = []
    lines.append(f"# Relationship Review: {case_name}\n")
    lines.append(f"**Total Episodes:** {total_episodes}\n")
    lines.append(f"**Total Proposed Relationships:** {total_relationships}\n")
    lines.append("\n---\n")

    # Section 1: Existing entities (same as before)
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

    # Section 2: Proposed entities with consolidation
    lines.append("\n---\n")
    lines.append("## 2. Proposed Entity Mentions (from LLM extraction)\n")
    lines.append("*(Consolidated duplicates, showing matches to existing entities)*\n")

    for entity_type in sorted(consolidated.keys()):
        type_groups = consolidated[entity_type]
        lines.append(f"\n### {entity_type} ({len(type_groups)} consolidated)")

        for canonical_name, variants in sorted(type_groups.items()):
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
            if not matched and global_entities.get('lienholders'):
                # Check if this entity is a lienholder (medical billing, subrogation companies)
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['lienholders'])
                if matched:
                    matched_name = f"{matched_name} (LienHolder, not {entity_type})"

            if not matched and global_entities.get('vendors'):
                # Check if this entity is a vendor (IME companies, court reporters, record services)
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['vendors'])
                if matched:
                    matched_name = f"{matched_name} (Vendor, not {entity_type})"

            # CROSS-CHECK ALL JSON FILES (original classification may be wrong)
            # PRIORITY ORDER: Case entities FIRST, then global databases
            # This prevents clients/existing providers from being mismatched to global entities

            # === PRIORITY 1: CASE-SPECIFIC ENTITIES (from Section 1) ===
            # These are already confirmed for this specific case - check them FIRST

            # Check case clients (from existing case data)
            if not matched and entity_type == "Client":
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['clients'], entity_type="Client")

            # Check case providers (from Section 1)
            if not matched:
                provider_names = [p['name'] for p in case_entities['providers']]
                matched, matched_name = fuzzy_match_entity(canonical_name, provider_names, entity_type="MedicalProvider")

            # Check case insurers (from Section 1 claims)
            if not matched:
                insurers = list(set(c['insurer'] for c in case_entities['claims'] if c['insurer']))
                matched, matched_name = fuzzy_match_entity(canonical_name, insurers)

            # Check case adjusters (from Section 1 claims)
            if not matched:
                adjusters = list(set(c['adjuster'] for c in case_entities['claims'] if c['adjuster']))
                matched, matched_name = fuzzy_match_entity(canonical_name, adjusters)

            # Check case attorneys (from Section 1)
            if not matched:
                attorney_names = [a['name'] for a in case_entities['attorneys']]
                matched, matched_name = fuzzy_match_entity(canonical_name, attorney_names, entity_type="Attorney")

            # Check case lienholders (from Section 1)
            if not matched and entity_type in ["Lien", "LienHolder"]:
                holders = [l['holder'] for l in case_entities['liens'] if l['holder']]
                matched, matched_name = fuzzy_match_entity(canonical_name, holders)

            # === PRIORITY 2: GLOBAL ENTITY DATABASES ===

            # === COURT ENTITIES ===
            if not matched and entity_type in ["Court", "CircuitDivision", "DistrictDivision"]:
                # Check circuit divisions first (most specific), then district divisions, then courts, then organizations
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['circuit_divisions'], entity_type="Court")
                if not matched:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['district_divisions'], entity_type="Court")
                if not matched:
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['courts'], entity_type="Court")
                if not matched:
                    # Check organizations (for entities like "Kentucky Court of Justice")
                    matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['organizations'])

            # === MEDICAL ENTITIES (Doctor or MedicalProvider) ===
            # Check doctors.json - but AFTER checking case providers above
            if not matched:
                # Check active doctors first (13K+)
                if global_entities.get('doctors'):
                    matched, matched_name = fuzzy_match_doctor(canonical_name, global_entities['doctors'])
                    if matched:
                        matched_name = f"{matched_name} (licensed KY doctor)"
                        if entity_type not in ["Doctor", "MedicalProvider"]:
                            matched_name = f"{matched_name}, not {entity_type}"

                # Check all doctors (including inactive) if not found
                if not matched and global_entities.get('doctors_all'):
                    matched, matched_name = fuzzy_match_doctor(canonical_name, global_entities['doctors_all'])
                    if matched:
                        matched_name = f"{matched_name} (licensed KY doctor, inactive)"
                        if entity_type not in ["Doctor", "MedicalProvider"]:
                            matched_name = f"{matched_name}, not {entity_type}"

            # Check global medical providers (after case providers and doctors)
            if not matched:
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['medical_providers'], entity_type="MedicalProvider")
                if matched and entity_type not in ["MedicalProvider", "Doctor", "Organization"]:
                    matched_name = f"{matched_name} (MedicalProvider, not {entity_type})"

            # === INSURANCE-RELATED ENTITIES ===
            # Check claim-specific insurers (for BIClaim, PIPClaim, etc.)
            if not matched and entity_type in ["BIClaim", "PIPClaim", "UMClaim", "UIMClaim", "WCClaim"]:
                insurers_for_type = [c['insurer'] for c in case_entities['claims']
                                    if c['type'] == entity_type and c['insurer']]
                matched, matched_name = fuzzy_match_entity(canonical_name, insurers_for_type)

            # Check global insurers (after case insurers checked above in Priority 1)
            if not matched and global_entities.get('insurers'):
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['insurers'])
                if matched and entity_type != "Insurer":
                    matched_name = f"{matched_name} (Insurer, not {entity_type})"

            # Check global adjusters (after case adjusters checked above in Priority 1)
            if not matched and global_entities.get('adjusters'):
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['adjusters'])
                if matched and entity_type != "Adjuster":
                    matched_name = f"{matched_name} (Adjuster, not {entity_type})"

            # === LEGAL ENTITIES ===
            # Check global attorneys (after case attorneys checked above in Priority 1)
            if not matched and global_entities.get('attorneys'):
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities['attorneys'], entity_type="Attorney")
                if matched and entity_type != "Attorney":
                    matched_name = f"{matched_name} (Attorney, not {entity_type})"

            # Check law firms (cross-check even if classified differently)
            if not matched and entity_type in ["LawFirm", "Organization", "Attorney"]:
                # First check aliases (exact or partial match for names with extra info)
                if 'law_firm_aliases' in global_entities:
                    # Try exact match first
                    if canonical_name in global_entities['law_firm_aliases']:
                        matched = True
                        matched_name = f"{global_entities['law_firm_aliases'][canonical_name]} (alias: {canonical_name})"
                    else:
                        # Try stripping parenthetical info (e.g., "BDB Law (bdblawky.com)" → "BDB Law")
                        base_name = re.sub(r'\s*\([^)]+\)\s*$', '', canonical_name).strip()
                        if base_name in global_entities['law_firm_aliases']:
                            matched = True
                            matched_name = f"{global_entities['law_firm_aliases'][base_name]} (alias: {base_name})"

                if not matched:
                    # Check if it's actually an attorney's name (already checked above, but re-check for law firm context)
                    is_staff, staff_name, _ = check_whaley_staff(canonical_name)
                    if is_staff:
                        matched = True
                        matched_name = f"{staff_name} (→ ATTORNEY, not law firm)"
                    else:
                        is_attorney, atty_name = fuzzy_match_entity(canonical_name, global_entities.get('attorneys', []), entity_type="Attorney")
                        if is_attorney:
                            matched = True
                            matched_name = f"{atty_name} (→ ATTORNEY, not law firm)"
                        else:
                            matched, matched_name = fuzzy_match_entity(canonical_name, global_entities.get('law_firms', []), entity_type="LawFirm")

            # === DEFENDANT ENTITIES ===
            if not matched:
                # Check defendants (cross-check even if classified differently)
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities.get('defendants', []))
                if matched:
                    matched_name = f"{matched_name} (Defendant, not {entity_type})" if entity_type != "Defendant" else matched_name

            # === PROFESSIONAL SERVICE ENTITIES ===
            # Check vendors (cross-check even if classified differently)
            if not matched:
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities.get('vendors', []))
                if matched:
                    matched_name = f"{matched_name} (Vendor, not {entity_type})" if entity_type != "Vendor" else matched_name

            # Check experts (cross-check even if classified differently)
            if not matched:
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities.get('experts', []))
                if matched:
                    matched_name = f"{matched_name} (Expert, not {entity_type})" if entity_type != "Expert" else matched_name

            # Check witnesses (cross-check even if classified differently)
            if not matched:
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities.get('witnesses', []))
                if matched:
                    matched_name = f"{matched_name} (Witness, not {entity_type})" if entity_type != "Witness" else matched_name

            # Check mediators (cross-check even if classified differently)
            if not matched:
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities.get('mediators', []))
                if matched:
                    matched_name = f"{matched_name} (Mediator, not {entity_type})" if entity_type != "Mediator" else matched_name

            # === ORGANIZATIONS ===
            # Check general organizations (cross-check even if classified differently)
            if not matched:
                matched, matched_name = fuzzy_match_entity(canonical_name, global_entities.get('organizations', []))
                if matched:
                    matched_name = f"{matched_name} (Organization, not {entity_type})" if entity_type != "Organization" else matched_name

            # Fallback: check directory for any unmatched entity
            if not matched and global_entities['directory_all']:
                dir_matched, dir_name = fuzzy_match_entity(canonical_name, global_entities['directory_all'])
                if dir_matched:
                    matched = True
                    matched_name = f"{dir_name} (from directory)"

            # Build status
            if matched and matched_name:
                status = f"✓ MATCHES: {matched_name}"
            elif matched:
                status = "✓ EXISTS"
            else:
                status = "? NEW"

            # Show canonical with variants (DO NOT preserve user annotations)
            if len(variants) > 1:
                entity_line = f"- [ ] **{canonical_name}** — *{status}*"
                lines.append(entity_line)
                for variant in variants:
                    if variant != canonical_name:
                        lines.append(f"      ↳ _{variant}_")
            else:
                entity_line = f"- [ ] {canonical_name} — *{status}*"
                lines.append(entity_line)

    # Section 3: Action items
    lines.append("\n---\n")
    lines.append("## 3. Review Actions\n")
    lines.append("\n**For each proposed entity marked '? NEW':**")
    lines.append("- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')")
    lines.append("- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)")
    lines.append("- [ ] **Create new** (valid entity not yet in graph)")
    lines.append("\n**After review:**")
    lines.append("- Run ingestion script to create Episode nodes and ABOUT relationships")

    # Write regenerated review
    output_file = output_dir / f"review_{case_name}.md"
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

    return output_file


def main():
    reviews_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews")
    entities_dir = reviews_dir.parent.parent / "entities"
    episodes_dir = reviews_dir.parent  # For processed_*.json files
    directory_file = reviews_dir.parent.parent.parent / "directory.json"

    print("=" * 80)
    print("REGENERATING ALL REVIEW DOCUMENTS")
    print("=" * 80)
    print()

    # Load approved reviews to skip
    approved_file = reviews_dir / "APPROVED_REVIEWS.txt"
    approved_reviews = set()
    if approved_file.exists():
        with open(approved_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    approved_reviews.add(line)
        print(f"⚠️  Skipping {len(approved_reviews)} approved reviews (will not regenerate)")
        for approved in sorted(approved_reviews):
            print(f"     - {approved}")
        print()

    # Load global entities
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

    # Find all review files
    review_files = sorted(reviews_dir.glob("review_*.md"))
    print(f"Found {len(review_files)} review files to regenerate")
    print()

    # Regenerate each review (skip approved)
    regenerated = 0
    skipped = 0
    for i, review_file in enumerate(review_files, 1):
        # Skip approved reviews
        if review_file.name in approved_reviews:
            skipped += 1
            continue

        output = regenerate_review(review_file, global_entities, reviews_dir, episodes_dir)
        regenerated += 1
        if regenerated % 10 == 0:
            print(f"  [{regenerated}/{len(review_files) - len(approved_reviews)}] {output.name}")

    print()
    print(f"✅ Regenerated {regenerated} review documents")
    print(f"   Skipped {skipped} approved reviews (protected from regeneration)")
    print(f"Location: {reviews_dir}")


if __name__ == "__main__":
    main()
