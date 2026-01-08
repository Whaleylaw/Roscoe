#!/usr/bin/env python3
"""
Load Graph Structure from JSON Files

Loads entities and relationships into the Graphiti knowledge graph from JSON files.
Uses Cypher MERGE statements to create nodes and relationships, avoiding duplicates.

This script performs deterministic loading (not LLM-based extraction), ensuring
consistent, reproducible graph structure.

Usage:
    python -m roscoe.scripts.load_graph_from_json --json-dir /path/to/json-files/ [--merge-map /path/to/merge_map.json]
    
Phases:
    1. Load directory entries as base DirectoryEntry nodes
    2. Load cases from case-list.json
    3. Load clients and create HAS_CLIENT relationships
    4. Load insurance claims, insurers, adjusters with relationships
    5. Load medical providers and TREATING_AT relationships
    6. Load liens and lien holders
    7. Load litigation contacts (attorneys, defendants)
"""

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Any


def convert_excel_date(value: Any) -> Optional[str]:
    """Convert Excel serial date to ISO format."""
    if value is None:
        return None
    if isinstance(value, str):
        # Check if it looks like an Excel date (number as string)
        try:
            num = float(value)
            if num > 40000 and num < 50000:  # Likely Excel date range
                # Excel epoch is 1899-12-30
                from datetime import timedelta
                excel_epoch = datetime(1899, 12, 30)
                dt = excel_epoch + timedelta(days=int(num))
                return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
        # Already a date string
        return value
    if isinstance(value, (int, float)) and value > 40000 and value < 50000:
        from datetime import timedelta
        excel_epoch = datetime(1899, 12, 30)
        dt = excel_epoch + timedelta(days=int(value))
        return dt.strftime("%Y-%m-%d")
    return str(value) if value else None


def load_json_file(path: Path) -> list[dict]:
    """Load a JSON file, handling various PostgreSQL export formats."""
    with open(path) as f:
        content = f.read().strip()
    
    # Handle malformed exports with various issues
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Try several fixes for common malformations
        fixed = False
        
        # Fix 1: Missing opening bracket (starts with { but ends with ])
        if content.startswith('{') and content.endswith(']'):
            try:
                data = json.loads('[' + content)
                print(f"  Note: Added missing '[' to {path.name}")
                fixed = True
            except json.JSONDecodeError:
                pass
        
        # Fix 2: Trailing characters
        if not fixed:
            for trim in range(1, 10):
                try:
                    data = json.loads(content[:-trim].rstrip())
                    print(f"  Note: Trimmed {trim} chars from {path.name}")
                    fixed = True
                    break
                except json.JSONDecodeError:
                    continue
        
        if not fixed:
            raise ValueError(f"Could not parse {path}")
    
    # Handle jsonb_agg wrapper
    if isinstance(data, dict) and "jsonb_agg" in data:
        return data["jsonb_agg"]
    if isinstance(data, list):
        if len(data) >= 1 and isinstance(data[0], dict) and "jsonb_agg" in data[0]:
            return data[0]["jsonb_agg"]
        return data
    
    raise ValueError(f"Unexpected format in {path}")


def sanitize_for_cypher(value: Any) -> str:
    """Sanitize a value for safe inclusion in Cypher query."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    # String - escape quotes
    s = str(value)
    s = s.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
    return f"'{s}'"


def build_properties(props: dict) -> str:
    """Build Cypher properties string from dict."""
    parts = []
    for k, v in props.items():
        if v is not None:
            parts.append(f"{k}: {sanitize_for_cypher(v)}")
    return "{" + ", ".join(parts) + "}"


class GraphLoader:
    """Loads graph structure from JSON files."""
    
    def __init__(self, json_dir: Path, merge_map: Optional[dict] = None):
        self.json_dir = json_dir
        self.merge_map = merge_map or {}
        self.stats = {
            "directory_entries": 0,
            "cases": 0,
            "clients": 0,
            "insurers": 0,
            "adjusters": 0,
            "claims": 0,
            "providers": 0,
            "liens": 0,
            "lien_holders": 0,
            "attorneys": 0,
            "defendants": 0,
            "relationships": 0,
        }
        # Track created entities to avoid duplicates
        self.created_entities = set()
    
    def get_canonical_uuid(self, uuid: int) -> int:
        """Get canonical UUID if this one is merged, otherwise return as-is."""
        return self.merge_map.get(str(uuid), uuid)
    
    async def run_query(self, query: str, params: dict = None):
        """Execute a Cypher query."""
        from roscoe.core.graphiti_client import run_cypher_query
        try:
            return await run_cypher_query(query, params or {})
        except Exception as e:
            print(f"  Error executing query: {e}")
            print(f"  Query: {query[:200]}...")
            return []
    
    async def create_entity(self, entity_type: str, name: str, props: dict = None) -> bool:
        """Create or merge an entity node."""
        key = (entity_type, name)
        if key in self.created_entities:
            return False  # Already created
        
        props = props or {}
        props["entity_type"] = entity_type
        props["name"] = name
        
        # Use MERGE to avoid duplicates
        query = f"""
        MERGE (e:Entity {{name: $name, entity_type: $entity_type}})
        ON CREATE SET e += $props
        ON MATCH SET e += $props
        RETURN e.name as name
        """
        
        await self.run_query(query, {
            "name": name,
            "entity_type": entity_type,
            "props": props
        })
        
        self.created_entities.add(key)
        return True
    
    async def create_relationship(self, from_type: str, from_name: str, 
                                   rel_type: str, to_type: str, to_name: str,
                                   props: dict = None) -> bool:
        """Create a relationship between two entities."""
        props = props or {}
        
        query = f"""
        MATCH (from:Entity {{name: $from_name, entity_type: $from_type}})
        MATCH (to:Entity {{name: $to_name, entity_type: $to_type}})
        MERGE (from)-[r:{rel_type}]->(to)
        SET r += $props
        RETURN from.name, to.name
        """
        
        result = await self.run_query(query, {
            "from_name": from_name,
            "from_type": from_type,
            "to_name": to_name,
            "to_type": to_type,
            "props": props
        })
        
        if result:
            self.stats["relationships"] += 1
            return True
        return False
    
    async def load_directory(self):
        """Phase 1: Load directory entries as base entities."""
        print("\n=== Phase 1: Loading Directory Entries ===")
        
        # Try deduplicated file first, fall back to original
        dedup_path = self.json_dir / "dedup-output" / "directory_deduplicated.json"
        orig_path = self.json_dir / "directory.json"
        
        if dedup_path.exists():
            print(f"  Using deduplicated directory: {dedup_path}")
            entries = load_json_file(dedup_path)
        else:
            print(f"  Using original directory: {orig_path}")
            entries = load_json_file(orig_path)
        
        print(f"  Processing {len(entries)} directory entries...")
        
        for entry in entries:
            uuid = entry.get("uuid")
            if uuid is None:
                continue
            
            # Skip if this entry is merged into another
            canonical = self.get_canonical_uuid(uuid)
            if canonical != uuid:
                continue
            
            name = (entry.get("full_name") or "").strip()
            if not name:
                continue
            
            props = {
                "directory_uuid": uuid,
                "phone": entry.get("phone"),
                "email": entry.get("email"),
                "address": entry.get("address"),
                "phone_normalized": entry.get("phone_normalized"),
            }
            
            await self.create_entity("DirectoryEntry", name, props)
            self.stats["directory_entries"] += 1
        
        print(f"  Created {self.stats['directory_entries']} directory entries")
    
    async def load_cases(self):
        """Phase 2: Load cases from case-list.json."""
        print("\n=== Phase 2: Loading Cases ===")
        
        path = self.json_dir / "case-list.json"
        cases = load_json_file(path)
        
        print(f"  Processing {len(cases)} cases...")
        
        for case in cases:
            name = case.get("project_name")
            if not name:
                continue
            
            props = {
                "client_name": case.get("client_name"),
                "phase": case.get("phase"),
                "accident_date": case.get("accident_date"),
                "status": case.get("status"),
            }
            
            await self.create_entity("Case", name, props)
            self.stats["cases"] += 1
        
        print(f"  Created {self.stats['cases']} cases")
    
    async def load_clients(self):
        """Phase 3: Load clients and create HAS_CLIENT relationships."""
        print("\n=== Phase 3: Loading Clients ===")
        
        path = self.json_dir / "clients.json"
        clients = load_json_file(path)
        
        print(f"  Processing {len(clients)} clients...")
        
        for client in clients:
            name = (client.get("full_name") or "").strip()
            project_name = client.get("project_name")
            
            if not name or not project_name:
                continue
            
            uuid = client.get("uuid")
            canonical_uuid = self.get_canonical_uuid(uuid) if uuid else None
            
            props = {
                "directory_uuid": canonical_uuid,
                "date_of_birth": client.get("date_of_birth"),
                "social_security_number": client.get("social_security_number"),
                "phone": client.get("phone"),
                "email": client.get("email"),
                "address": client.get("address"),
            }
            
            await self.create_entity("Client", name, props)
            self.stats["clients"] += 1
            
            # Create HAS_CLIENT relationship
            await self.create_relationship("Case", project_name, "HAS_CLIENT", "Client", name)
            
            # Link to directory entry if exists
            if canonical_uuid:
                # Find directory entry name by UUID
                await self.create_relationship("Client", name, "IN_DIRECTORY", "DirectoryEntry", name)
        
        print(f"  Created {self.stats['clients']} clients")
    
    async def load_insurance(self):
        """Phase 4: Load insurance claims, insurers, and adjusters."""
        print("\n=== Phase 4: Loading Insurance Data ===")
        
        path = self.json_dir / "insurance.json"
        claims_data = load_json_file(path)
        
        print(f"  Processing {len(claims_data)} insurance records...")
        
        # Track unique insurers and adjusters for deduplication
        insurers_seen = set()
        adjusters_seen = set()
        
        for claim in claims_data:
            project_name = claim.get("project_name")
            insurer_name = (claim.get("insurance_company_name") or "").strip()
            adjuster_name = (claim.get("insurance_adjuster_name") or "").strip() or None
            claim_number = claim.get("claim_number")
            insurance_type = claim.get("insurance_type", "Unknown")
            
            if not project_name or not insurer_name:
                continue
            
            # Map insurance type to claim_type
            type_mapping = {
                "Personal Injury Protection (PIP)": "PIP",
                "Bodily Injury": "BI",
                "Uninsured Motorist": "UM",
                "Underinsured Motorist": "UIM",
                "Workers Compensation": "WC",
                "Medical Payments": "MedPay",
            }
            claim_type = type_mapping.get(insurance_type, insurance_type)
            
            # Create Insurer (deduplicated)
            if insurer_name not in insurers_seen:
                await self.create_entity("Insurer", insurer_name)
                self.stats["insurers"] += 1
                insurers_seen.add(insurer_name)
            
            # Create Adjuster (deduplicated)
            if adjuster_name and adjuster_name not in adjusters_seen:
                await self.create_entity("Adjuster", adjuster_name)
                self.stats["adjusters"] += 1
                adjusters_seen.add(adjuster_name)
            
            # Create InsuranceClaim
            claim_name = claim_number or f"{project_name}-{claim_type}"
            props = {
                "claim_number": claim_number,
                "claim_type": claim_type,
                "coverage_confirmation": claim.get("coverage_confirmation"),
                "demanded_amount": claim.get("demanded_amount"),
                "current_offer": claim.get("current_offer"),
                "settlement_amount": claim.get("settlement_amount"),
            }
            
            await self.create_entity("InsuranceClaim", claim_name, props)
            self.stats["claims"] += 1
            
            # Create relationships
            await self.create_relationship("Case", project_name, "HAS_CLAIM", "InsuranceClaim", claim_name)
            await self.create_relationship("InsuranceClaim", claim_name, "INSURED_BY", "Insurer", insurer_name)
            
            if adjuster_name:
                await self.create_relationship("InsuranceClaim", claim_name, "ASSIGNED_ADJUSTER", "Adjuster", adjuster_name)
        
        print(f"  Created {self.stats['insurers']} insurers, {self.stats['adjusters']} adjusters, {self.stats['claims']} claims")
    
    async def load_medical_providers(self):
        """Phase 5: Load medical providers and treatment relationships."""
        print("\n=== Phase 5: Loading Medical Providers ===")
        
        path = self.json_dir / "medical-providers.json"
        providers_data = load_json_file(path)
        
        print(f"  Processing {len(providers_data)} provider records...")
        
        providers_seen = set()
        
        for record in providers_data:
            project_name = record.get("project_name")
            provider_name = (record.get("provider_full_name") or "").strip()
            
            if not project_name or not provider_name:
                continue
            
            # Create provider (deduplicated)
            if provider_name not in providers_seen:
                props = {
                    "phone": record.get("phone"),
                    "fax": record.get("fax"),
                    "address": record.get("address"),
                }
                await self.create_entity("MedicalProvider", provider_name, props)
                self.stats["providers"] += 1
                providers_seen.add(provider_name)
            
            # Create TREATING_AT relationship with treatment details
            rel_props = {
                "billed_amount": record.get("billed_amount"),
                "settlement_payment": record.get("settlement_payment"),
                "treatment_started": convert_excel_date(record.get("date_treatment_started")),
                "treatment_completed": convert_excel_date(record.get("date_treatment_completed")),
                "records_received": convert_excel_date(record.get("date_medical_records_received")),
            }
            
            await self.create_relationship("Case", project_name, "TREATING_AT", "MedicalProvider", provider_name, rel_props)
        
        print(f"  Created {self.stats['providers']} medical providers")
    
    async def load_liens(self):
        """Phase 6: Load liens and lien holders."""
        print("\n=== Phase 6: Loading Liens ===")
        
        path = self.json_dir / "liens.json"
        liens_data = load_json_file(path)
        
        print(f"  Processing {len(liens_data)} lien records...")
        
        holders_seen = set()
        
        for lien in liens_data:
            project_name = lien.get("project_name")
            holder_name = (lien.get("lien_holder_name") or "").strip()
            lien_id = lien.get("id")
            
            if not project_name or not holder_name:
                continue
            
            # Create LienHolder (deduplicated)
            if holder_name not in holders_seen:
                await self.create_entity("LienHolder", holder_name)
                self.stats["lien_holders"] += 1
                holders_seen.add(holder_name)
            
            # Create Lien
            lien_name = f"{project_name}-lien-{lien_id}"
            props = {
                "lien_id": lien_id,
                "amount": lien.get("final_lien_amount"),
                "date_received": lien.get("date_notice_received"),
            }
            
            await self.create_entity("Lien", lien_name, props)
            self.stats["liens"] += 1
            
            # Create relationships
            await self.create_relationship("Case", project_name, "HAS_LIEN", "Lien", lien_name)
            await self.create_relationship("Lien", lien_name, "HELD_BY", "LienHolder", holder_name)
        
        print(f"  Created {self.stats['liens']} liens, {self.stats['lien_holders']} lien holders")
    
    async def load_litigation_contacts(self):
        """Phase 7: Load litigation contacts (attorneys, defendants)."""
        print("\n=== Phase 7: Loading Litigation Contacts ===")
        
        path = self.json_dir / "litigation_contacts.json"
        contacts_data = load_json_file(path)
        
        print(f"  Processing {len(contacts_data)} litigation contacts...")
        
        attorneys_seen = set()
        defendants_seen = set()
        
        for contact in contacts_data:
            project_name = contact.get("project_name")
            name = (contact.get("contact") or "").strip()
            role = (contact.get("role") or "").strip()
            
            if not project_name or not name:
                continue
            
            if "attorney" in role.lower():
                # Create Attorney
                if name not in attorneys_seen:
                    await self.create_entity("Attorney", name, {"role": role})
                    self.stats["attorneys"] += 1
                    attorneys_seen.add(name)
                
                # Determine relationship type based on role
                if "defense" in role.lower():
                    await self.create_relationship("Case", project_name, "DEFENSE_COUNSEL", "Attorney", name)
                elif "plaintiff" in role.lower():
                    await self.create_relationship("Case", project_name, "PLAINTIFF_COUNSEL", "Attorney", name)
                else:
                    await self.create_relationship("Case", project_name, "HAS_ATTORNEY", "Attorney", name)
            
            elif "defendant" in role.lower():
                # Create Defendant
                if name not in defendants_seen:
                    await self.create_entity("Defendant", name)
                    self.stats["defendants"] += 1
                    defendants_seen.add(name)
                
                await self.create_relationship("Case", project_name, "HAS_DEFENDANT", "Defendant", name)
        
        print(f"  Created {self.stats['attorneys']} attorneys, {self.stats['defendants']} defendants")
    
    async def classify_directory_entries(self):
        """Classify directory entries based on case_relationship.json roles."""
        print("\n=== Classifying Directory Entries by Role ===")
        
        path = self.json_dir / "case_relationship.json"
        relationships = load_json_file(path)
        
        # Group by directory ID and collect all roles
        roles_by_uuid = {}
        for rel in relationships:
            uuid = rel.get("id")
            roles = rel.get("roles", [])
            if uuid and roles:
                if uuid not in roles_by_uuid:
                    roles_by_uuid[uuid] = set()
                roles_by_uuid[uuid].update(roles)
        
        print(f"  Found roles for {len(roles_by_uuid)} directory entries")
        
        # Update entities with their roles
        for uuid, roles in roles_by_uuid.items():
            canonical_uuid = self.get_canonical_uuid(uuid)
            
            # Find the directory entry by UUID
            query = """
            MATCH (e:Entity {entity_type: 'DirectoryEntry', directory_uuid: $uuid})
            SET e.roles = $roles
            RETURN e.name as name
            """
            await self.run_query(query, {"uuid": canonical_uuid, "roles": list(roles)})
        
        print(f"  Classified directory entries")
    
    async def link_directory_entries(self):
        """Create IN_DIRECTORY relationships for entities that match directory entries."""
        print("\n=== Linking Entities to Directory ===")
        
        # Link entities to directory by name match
        entity_types = ["Insurer", "Adjuster", "MedicalProvider", "LienHolder", "Attorney"]
        
        for entity_type in entity_types:
            query = f"""
            MATCH (e:Entity {{entity_type: '{entity_type}'}})
            MATCH (d:Entity {{entity_type: 'DirectoryEntry'}})
            WHERE e.name = d.name
            MERGE (e)-[:IN_DIRECTORY]->(d)
            RETURN count(*) as linked
            """
            result = await self.run_query(query)
            if result:
                print(f"  Linked {result[0].get('linked', 0)} {entity_type} entities to directory")
    
    async def add_client_level_relationships(self):
        """
        Create client-level relationships that span across cases.
        
        This enables queries like "all providers a client has ever seen" 
        without having to traverse through Case entities.
        
        Creates:
        - Client -TREATED_BY-> MedicalProvider
        - Client -HAS_INSURANCE_WITH-> Insurer  
        - Client -HAS_LIEN_FROM-> LienHolder
        """
        print("\n=== Adding Client-Level Relationships ===")
        
        # 1. Client -TREATED_BY-> MedicalProvider
        # Traverse: Client <-HAS_CLIENT- Case -TREATING_AT-> Provider
        treated_by_query = """
        MATCH (client:Entity {entity_type: 'Client'})<-[:HAS_CLIENT]-(case:Entity {entity_type: 'Case'})-[:TREATING_AT]->(provider:Entity {entity_type: 'MedicalProvider'})
        MERGE (client)-[:TREATED_BY]->(provider)
        RETURN count(*) as created
        """
        result = await self.run_query(treated_by_query)
        treated_count = result[0].get('created', 0) if result else 0
        print(f"  Created {treated_count} Client -TREATED_BY-> MedicalProvider relationships")
        self.stats["relationships"] += treated_count
        
        # 2. Client -HAS_INSURANCE_WITH-> Insurer
        # Traverse: Client <-HAS_CLIENT- Case -HAS_CLAIM-> Claim -INSURED_BY-> Insurer
        insurance_query = """
        MATCH (client:Entity {entity_type: 'Client'})<-[:HAS_CLIENT]-(case:Entity {entity_type: 'Case'})-[:HAS_CLAIM]->(claim:Entity {entity_type: 'InsuranceClaim'})-[:INSURED_BY]->(insurer:Entity {entity_type: 'Insurer'})
        MERGE (client)-[:HAS_INSURANCE_WITH]->(insurer)
        RETURN count(*) as created
        """
        result = await self.run_query(insurance_query)
        insurance_count = result[0].get('created', 0) if result else 0
        print(f"  Created {insurance_count} Client -HAS_INSURANCE_WITH-> Insurer relationships")
        self.stats["relationships"] += insurance_count
        
        # 3. Client -HAS_LIEN_FROM-> LienHolder
        # Traverse: Client <-HAS_CLIENT- Case -HAS_LIEN-> Lien -HELD_BY-> LienHolder
        lien_query = """
        MATCH (client:Entity {entity_type: 'Client'})<-[:HAS_CLIENT]-(case:Entity {entity_type: 'Case'})-[:HAS_LIEN]->(lien:Entity {entity_type: 'Lien'})-[:HELD_BY]->(holder:Entity {entity_type: 'LienHolder'})
        MERGE (client)-[:HAS_LIEN_FROM]->(holder)
        RETURN count(*) as created
        """
        result = await self.run_query(lien_query)
        lien_count = result[0].get('created', 0) if result else 0
        print(f"  Created {lien_count} Client -HAS_LIEN_FROM-> LienHolder relationships")
        self.stats["relationships"] += lien_count
        
        total = treated_count + insurance_count + lien_count
        print(f"  Total client-level relationships: {total}")
    
    async def run(self):
        """Run all loading phases."""
        print("=" * 60)
        print("GRAPH LOADING FROM JSON FILES")
        print("=" * 60)
        print(f"JSON Directory: {self.json_dir}")
        print(f"Merge Map: {len(self.merge_map)} entries to merge")
        
        # Run phases in order
        await self.load_directory()
        await self.load_cases()
        await self.load_clients()
        await self.load_insurance()
        await self.load_medical_providers()
        await self.load_liens()
        await self.load_litigation_contacts()
        await self.classify_directory_entries()
        await self.link_directory_entries()
        await self.add_client_level_relationships()
        
        # Print summary
        print("\n" + "=" * 60)
        print("LOADING COMPLETE")
        print("=" * 60)
        print(f"Directory Entries: {self.stats['directory_entries']}")
        print(f"Cases:             {self.stats['cases']}")
        print(f"Clients:           {self.stats['clients']}")
        print(f"Insurers:          {self.stats['insurers']}")
        print(f"Adjusters:         {self.stats['adjusters']}")
        print(f"Claims:            {self.stats['claims']}")
        print(f"Medical Providers: {self.stats['providers']}")
        print(f"Liens:             {self.stats['liens']}")
        print(f"Lien Holders:      {self.stats['lien_holders']}")
        print(f"Attorneys:         {self.stats['attorneys']}")
        print(f"Defendants:        {self.stats['defendants']}")
        print(f"Relationships:     {self.stats['relationships']}")
        print("=" * 60)


async def main():
    parser = argparse.ArgumentParser(description="Load graph structure from JSON files")
    parser.add_argument(
        "--json-dir", "-j",
        type=Path,
        required=True,
        help="Directory containing JSON files"
    )
    parser.add_argument(
        "--merge-map", "-m",
        type=Path,
        help="Path to directory merge map (from deduplication)"
    )
    
    args = parser.parse_args()
    
    # Load merge map if provided
    merge_map = {}
    if args.merge_map and args.merge_map.exists():
        with open(args.merge_map) as f:
            merge_map = json.load(f)
        print(f"Loaded merge map with {len(merge_map)} entries")
    
    loader = GraphLoader(args.json_dir, merge_map)
    await loader.run()


if __name__ == "__main__":
    asyncio.run(main())
