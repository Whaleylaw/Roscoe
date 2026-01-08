#!/usr/bin/env python3
"""
Process Episodes for Single Case - Extract Relationships for Review

For a given case:
1. Load all existing entities and relationships from graph
2. For each episode:
   - Convert to natural language
   - Propose relationships to existing entities
   - Propose FOLLOWS links to other episodes
3. Output JSON for manual review (does NOT create relationships)

Usage:
    python -m roscoe.scripts.process_episodes_for_case "Abby-Sitgraves-MVA-7-13-2024"
    python -m roscoe.scripts.process_episodes_for_case "Abby-Sitgraves-MVA-7-13-2024" --limit 10
"""

import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from openai import AsyncOpenAI
from falkordb import FalkorDB


async def load_case_entities(graph, case_name: str) -> Dict[str, List[Dict]]:
    """Load all entities for a case from the graph."""
    entities = {
        "providers": [],
        "insurers": [],
        "adjusters": [],
        "claims": [],
        "liens": [],
        "attorneys": [],
        "courts": [],
        "defendants": [],
    }

    # Medical Providers
    result = graph.query("""
        MATCH (c:Case {name: $case_name})-[:TREATING_AT]->(p:MedicalProvider)
        RETURN p.name, p.specialty
    """, {'case_name': case_name})

    if result.result_set:
        for row in result.result_set:
            entities["providers"].append({"name": row[0], "specialty": row[1]})

    # Insurance Claims + Insurers + Adjusters
    result = graph.query("""
        MATCH (c:Case {name: $case_name})-[:HAS_CLAIM]->(claim)
        WHERE claim:BIClaim OR claim:PIPClaim OR claim:UMClaim OR claim:UIMClaim
        OPTIONAL MATCH (claim)-[:INSURED_BY]->(insurer:Insurer)
        OPTIONAL MATCH (claim)-[:ASSIGNED_ADJUSTER]->(adj:Adjuster)
        RETURN labels(claim), claim.name, insurer.name, adj.name
    """, {'case_name': case_name})

    if result.result_set:
        for row in result.result_set:
            claim_type = [l for l in row[0] if l != 'Entity'][0] if row[0] else 'Claim'
            entities["claims"].append({
                "type": claim_type,
                "name": row[1],
                "insurer": row[2],
                "adjuster": row[3]
            })
            if row[2] and row[2] not in [i["name"] for i in entities["insurers"]]:
                entities["insurers"].append({"name": row[2]})
            if row[3] and row[3] not in [a["name"] for a in entities["adjusters"]]:
                entities["adjusters"].append({"name": row[3]})

    # Liens
    result = graph.query("""
        MATCH (c:Case {name: $case_name})-[:HAS_LIEN]->(lien:Lien)
        OPTIONAL MATCH (lien)-[:HELD_BY]->(holder:LienHolder)
        RETURN lien.name, holder.name, lien.amount
    """, {'case_name': case_name})

    if result.result_set:
        for row in result.result_set:
            entities["liens"].append({"name": row[0], "holder": row[1], "amount": row[2]})

    # Attorneys
    result = graph.query("""
        MATCH (c:Case {name: $case_name})-[r]-(atty:Attorney)
        RETURN atty.name, type(r)
    """, {'case_name': case_name})

    if result.result_set:
        for row in result.result_set:
            entities["attorneys"].append({"name": row[0], "role": row[1]})

    return entities


async def convert_to_natural_language(client: AsyncOpenAI, raw_text: str, case_name: str) -> str:
    """Convert structured text to natural language using GPT-5 Nano."""
    prompt = f"""Convert this structured case note into flowing natural language while preserving ALL facts and details.

Structured note:
{raw_text}

Write as narrative paragraphs. Be concise but complete. Example:
"Initial client contact on November 17, 2025 with Antonio Lopez regarding motor vehicle accident..."

Natural language version:"""

    response = await client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}],
        # GPT-5 models only support temperature=1 (default)
    )

    return response.choices[0].message.content


async def extract_proposed_relationships(
    client: AsyncOpenAI,
    episode_content: str,
    case_entities: Dict[str, List[Dict]],
    case_name: str
) -> Dict[str, Any]:
    """
    Use LLM to propose relationships for this episode.

    Returns JSON with proposed ABOUT and FOLLOWS links.
    """
    # Build entity list for prompt
    entity_choices = []

    if case_entities["providers"]:
        entity_choices.append("Medical Providers:")
        for p in case_entities["providers"]:
            entity_choices.append(f"  - {p['name']} ({p['specialty']})")

    if case_entities["claims"]:
        entity_choices.append("\nInsurance Claims:")
        for c in case_entities["claims"]:
            entity_choices.append(f"  - {c['type']}: {c['insurer']} (Adjuster: {c['adjuster']})")

    if case_entities["liens"]:
        entity_choices.append("\nLiens:")
        for l in case_entities["liens"]:
            entity_choices.append(f"  - {l['holder']}: ${l['amount']}")

    if case_entities["attorneys"]:
        entity_choices.append("\nAttorneys:")
        for a in case_entities["attorneys"]:
            entity_choices.append(f"  - {a['name']} ({a['role']})")

    entities_str = "\n".join(entity_choices) if entity_choices else "No entities found for this case"

    # Define valid entity types
    valid_types = [
        "Client", "HealthSystem", "MedicalProvider", "Doctor", "Insurer", "Adjuster",
        "BIClaim", "PIPClaim", "UMClaim", "UIMClaim", "WCClaim", "MedPayClaim",
        "Lien", "LienHolder",
        "Attorney", "CaseManager", "LawFirm",
        "Court", "CircuitDivision", "DistrictDivision", "AppellateDistrict", "SupremeCourtDistrict",
        "CircuitJudge", "DistrictJudge", "AppellateJudge", "SupremeCourtJustice",
        "CourtClerk", "MasterCommissioner", "CourtAdministrator",
        "Defendant", "Organization",
        "Expert", "Mediator", "Witness", "Vendor"
    ]

    prompt = f"""You are analyzing a case timeline episode to determine which entities it discusses.

IMPORTANT: You may ONLY use these entity types:
{', '.join(valid_types)}

If an entity doesn't match these types, DO NOT include it.

EPISODE:
{episode_content}

AVAILABLE ENTITIES FOR CASE {case_name}:
{entities_str}

TASK: Determine which entities this episode is ABOUT. Return JSON only.

EXAMPLES:

Example 1 (Multiple entities):
Episode: "Called State Farm adjuster John Smith about PIP claim #12345. He confirmed coverage is active and approved $10,000 for medical treatment at Baptist Health."
Response: {{
  "about": [
    {{"entity_type": "Insurer", "entity_name": "State Farm", "relevance": "subject of call"}},
    {{"entity_type": "Adjuster", "entity_name": "John Smith", "relevance": "person contacted"}},
    {{"entity_type": "PIPClaim", "entity_name": "PIP #12345", "relevance": "claim discussed"}},
    {{"entity_type": "MedicalProvider", "entity_name": "Baptist Health", "relevance": "treatment destination"}}
  ]
}}

Example 2 (Single entity):
Episode: "Faxed medical records request to UK Hospital with signed HIPAA authorization."
Response: {{
  "about": [
    {{"entity_type": "MedicalProvider", "entity_name": "UK Hospital", "relevance": "recipient of records request"}}
  ]
}}

Example 3 (No specific entities):
Episode: "Client called to say they're feeling better and treatment is going well."
Response: {{
  "about": []
}}

YOUR RESPONSE (JSON only):"""

    response = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        # GPT-5 models only support temperature=1 (default)
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


async def process_case_episodes(
    case_name: str,
    limit: int = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Process all episodes for a single case."""

    # Try by_case file first, then fall back to cleaned_episodes.json
    # Try multiple paths (local dev vs VM)
    possible_paths = [
        Path(f"/home/aaronwhaley/json-files/memory-cards/episodes/by_case/{case_name}.json"),
        Path(f"/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/by_case/{case_name}.json"),
    ]

    cleaned_paths = [
        Path("/mnt/workspace/json-files/memory-cards/episodes/cleaned_episodes.json"),
        Path("/home/aaronwhaley/json-files/memory-cards/episodes/cleaned_episodes.json"),
        Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/cleaned_episodes.json"),
    ]

    by_case_path = None
    for p in possible_paths:
        if p.exists():
            by_case_path = p
            break

    cleaned_path = None
    for p in cleaned_paths:
        if p.exists():
            cleaned_path = p
            break

    if by_case_path and by_case_path.exists():
        print(f"Loading episodes from: {by_case_path.name}")
        with open(by_case_path) as f:
            case_episodes = json.load(f)
    elif cleaned_path and cleaned_path.exists():
        print(f"Loading episodes from: {cleaned_path.name}")
        with open(cleaned_path) as f:
            all_episodes = json.load(f)
        case_episodes = [ep for ep in all_episodes if ep.get('case_name') == case_name]
    else:
        print(f"❌ No episode file found for {case_name}")
        return {}

    if limit:
        case_episodes = case_episodes[:limit]

    print(f"Processing {len(case_episodes)} episodes for {case_name}")
    print()

    if dry_run:
        print("[DRY RUN] Would process episodes")
        return {}

    # Connect to graph and OpenAI
    import os
    db = FalkorDB(
        host=os.getenv("FALKORDB_HOST", "roscoe-graphdb"),
        port=int(os.getenv("FALKORDB_PORT", "6379"))
    )
    graph = db.select_graph("roscoe_graph")

    openai_client = AsyncOpenAI()

    # Load existing entities for this case
    print("Loading existing entities from graph...")
    case_entities = await load_case_entities(graph, case_name)

    print(f"  Providers: {len(case_entities['providers'])}")
    print(f"  Claims: {len(case_entities['claims'])}")
    print(f"  Liens: {len(case_entities['liens'])}")
    print()

    # Process each episode
    processed = []
    errors = []

    for i, ep in enumerate(case_episodes, 1):
        print(f"\n[{i}/{len(case_episodes)}] {ep['episode_name'][:60]}...")
        print(f"  Date: {ep.get('reference_time', 'Unknown')[:10]}")
        print(f"  Author: {ep.get('author', 'Unknown')}")

        try:
            # Step 1: Convert to natural language
            print(f"  Converting to natural language...")
            natural = await convert_to_natural_language(
                openai_client,
                ep['episode_body'],
                case_name
            )
            print(f"  ✓ Converted ({len(natural)} chars)")

            # Step 2: Extract proposed relationships
            print(f"  Extracting entity relationships...")
            proposed = await extract_proposed_relationships(
                openai_client,
                natural,
                case_entities,
                case_name
            )

            num_about = len(proposed.get('about', []))
            print(f"  ✓ Proposed {num_about} ABOUT relationship{'s' if num_about != 1 else ''}")

            if num_about > 0:
                for rel in proposed.get('about', []):
                    print(f"    - {rel['entity_type']}: {rel['entity_name']}")

            processed.append({
                "episode_name": ep['episode_name'],
                "original_body": ep['episode_body'],
                "natural_language": natural,
                "valid_at": ep['reference_time'],
                "author": ep.get('author', 'Unknown'),
                "proposed_relationships": proposed,
            })

        except Exception as e:
            print(f"  ✗ ERROR: {str(e)[:100]}")
            errors.append({
                "episode_name": ep['episode_name'],
                "error": str(e)
            })
            continue

        # Save progress every 10 episodes
        if i % 10 == 0:
            print(f"\n--- Progress checkpoint: {i}/{len(case_episodes)} episodes processed ---")

    # Save results (workspace first, then home, then local)
    output_paths = [
        Path(f"/mnt/workspace/json-files/memory-cards/episodes/processed_{case_name}.json"),
        Path(f"/home/aaronwhaley/json-files/memory-cards/episodes/processed_{case_name}.json"),
        Path(f"/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/processed_{case_name}.json"),
    ]

    output_path = None
    for p in output_paths:
        if p.parent.exists():
            output_path = p
            break

    if not output_path:
        output_path = output_paths[0]
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump({
            "case_name": case_name,
            "total_episodes": len(processed),
            "total_errors": len(errors),
            "case_entities": case_entities,
            "episodes": processed,
            "errors": errors
        }, f, indent=2)

    print()
    print(f"✅ Saved to: {output_path}")
    print()
    print("Review the proposed relationships before ingesting to graph!")

    return processed


def main():
    parser = argparse.ArgumentParser(description='Process episodes for a case')
    parser.add_argument('case_name', help='Case name (e.g., Abby-Sitgraves-MVA-7-13-2024)')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of episodes')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = parser.parse_args()

    asyncio.run(process_case_episodes(
        args.case_name,
        limit=args.limit,
        dry_run=args.dry_run
    ))


if __name__ == "__main__":
    main()
