#!/usr/bin/env python3
"""
Migrate existing JSON case data to Graphiti knowledge graph.

This script:
1. Reads all case folders from /mnt/workspace/projects/
2. For each case, loads JSON files (overview, insurance, medical_providers, notes, etc.)
3. Creates Graphiti episodes that describe the case data in natural language
4. Scans the file system for documents and creates document episodes
5. Graphiti's LLM extracts entities and relationships automatically

Usage:
    python -m roscoe.scripts.migrate_to_graphiti [--dry-run] [--case CASE_NAME] [--limit N]

Options:
    --dry-run       Print what would be migrated without actually doing it
    --case NAME     Migrate only a specific case
    --limit N       Migrate only the first N cases (for testing)
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Workspace path
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/mnt/workspace")
PROJECTS_DIR = Path(WORKSPACE_DIR) / "projects"


def excel_date_to_datetime(excel_date: Any) -> Optional[datetime]:
    """
    Convert Excel serial date to Python datetime.
    
    Excel dates are days since 1899-12-30.
    Some fields may be strings like "45968.0" or actual dates like "2025-08-07".
    """
    if excel_date is None:
        return None
    
    # Already a date string?
    if isinstance(excel_date, str):
        # Try parsing as date string first
        if "-" in excel_date and len(excel_date) >= 10:
            try:
                return datetime.fromisoformat(excel_date.replace("Z", "+00:00").split("T")[0])
            except ValueError:
                pass
        
        # Try parsing as Excel number string
        try:
            excel_date = float(excel_date)
        except ValueError:
            return None
    
    if isinstance(excel_date, (int, float)):
        # Excel epoch is 1899-12-30
        try:
            return datetime(1899, 12, 30) + timedelta(days=int(excel_date))
        except (ValueError, OverflowError):
            return None
    
    return None


def format_date(dt: Optional[datetime]) -> str:
    """Format datetime for episode text."""
    if dt is None:
        return "unknown date"
    return dt.strftime("%B %d, %Y")


def load_json_safe(path: Path) -> list:
    """Load JSON file, returning empty list if not found or invalid."""
    if not path.exists():
        return []
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        # Handle nested structure like overview.json
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict) and "jsonb_agg" in data[0]:
                return data[0]["jsonb_agg"]
        return data if isinstance(data, list) else [data]
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to load {path}: {e}")
        return []


async def create_case_overview_episode(graphiti, case_name: str, overview: dict, dry_run: bool = False) -> None:
    """Create episode for case overview information."""
    
    client_name = overview.get("client_name", "Unknown")
    accident_date = excel_date_to_datetime(overview.get("accident_date"))
    phase = overview.get("phase", "Unknown")
    case_summary = overview.get("case_summary", "")
    current_status = overview.get("current_status", "")
    total_bills = overview.get("total_medical_bills", 0) or 0
    
    # Build episode text
    episode_body = f"""
Case {case_name} was created for client {client_name}.
The accident occurred on {format_date(accident_date)}.
The case is currently in the {phase} phase.

Case Summary: {case_summary}

Current Status: {current_status}

Total medical bills to date: ${total_bills:,.2f}
"""
    
    # Add address/contact info if available
    if overview.get("client_address"):
        episode_body += f"\nClient address: {overview['client_address']}"
    if overview.get("client_phone"):
        episode_body += f"\nClient phone: {overview['client_phone']}"
    if overview.get("client_email") and overview["client_email"] != "unknown@unknown":
        episode_body += f"\nClient email: {overview['client_email']}"
    
    # Add parent case info if this is a related case
    if overview.get("parent_project_name"):
        episode_body += f"\n\nThis case is related to parent case: {overview['parent_project_name']}"
    
    logger.info(f"  [OVERVIEW] {client_name} - {phase} phase")
    
    if not dry_run:
        from roscoe.core.graphiti_client import add_case_episode
        await add_case_episode(
            case_name=case_name,
            episode_name=f"Case overview for {client_name}",
            episode_body=episode_body.strip(),
            source="migration",
            reference_time=excel_date_to_datetime(overview.get("case_create_date")) or datetime.now(),
        )


async def create_insurance_episodes(graphiti, case_name: str, insurance_claims: list, dry_run: bool = False) -> None:
    """Create episodes for each insurance claim with specific claim type identification."""
    
    # Map insurance types to our entity type names
    CLAIM_TYPE_MAP = {
        "bodily": ("BIClaim", "Bodily Injury (BI) claim", "third-party liability claim against the at-fault driver"),
        "bi": ("BIClaim", "Bodily Injury (BI) claim", "third-party liability claim against the at-fault driver"),
        "pip": ("PIPClaim", "Personal Injury Protection (PIP) claim", "first-party no-fault coverage"),
        "personal injury protection": ("PIPClaim", "Personal Injury Protection (PIP) claim", "first-party no-fault coverage"),
        "um": ("UMClaim", "Uninsured Motorist (UM) claim", "coverage when at-fault driver has no insurance"),
        "uninsured": ("UMClaim", "Uninsured Motorist (UM) claim", "coverage when at-fault driver has no insurance"),
        "uim": ("UIMClaim", "Underinsured Motorist (UIM) claim", "coverage when at-fault driver's limits are insufficient"),
        "underinsured": ("UIMClaim", "Underinsured Motorist (UIM) claim", "coverage when at-fault driver's limits are insufficient"),
        "wc": ("WCClaim", "Workers Compensation (WC) claim", "workplace injury coverage"),
        "workers": ("WCClaim", "Workers Compensation (WC) claim", "workplace injury coverage"),
        "medpay": ("MedPayClaim", "Medical Payments (MedPay) claim", "first-party medical expense coverage"),
    }
    
    for claim in insurance_claims:
        claim_type_raw = claim.get("insurance_type", "Unknown").lower()
        insurer = claim.get("insurance_company_name", "Unknown")
        claim_number = claim.get("claim_number", "Not assigned")
        adjuster = claim.get("insurance_adjuster_name")
        
        # Determine claim type and description
        entity_type, full_name, description = ("BIClaim", "Insurance claim", "")
        for key, value in CLAIM_TYPE_MAP.items():
            if key in claim_type_raw:
                entity_type, full_name, description = value
                break
        
        # Build episode with explicit entity type language
        episode_body = f"""
{full_name} opened with {insurer}.
This is a {description}.
Insurance company: {insurer}
Claim number: {claim_number}
"""
        
        if adjuster:
            episode_body += f"Insurance adjuster: {adjuster} (works for {insurer})\n"
        
        if claim.get("coverage_confirmation"):
            episode_body += f"Coverage status: {claim['coverage_confirmation']}\n"
        
        # Policy limits
        if claim.get("policy_limit"):
            episode_body += f"Policy limit: ${claim['policy_limit']:,.2f}\n"
        
        lor_sent = excel_date_to_datetime(claim.get("date_coots_letter_sent"))
        if lor_sent:
            episode_body += f"Letter of representation sent on {format_date(lor_sent)}\n"
        
        demand_sent = excel_date_to_datetime(claim.get("date_demand_sent"))
        if demand_sent:
            episode_body += f"Demand sent on {format_date(demand_sent)}\n"
            if claim.get("demanded_amount"):
                episode_body += f"Demand amount: ${claim['demanded_amount']:,.2f}\n"
        
        if claim.get("current_offer"):
            episode_body += f"Current settlement offer: ${claim['current_offer']:,.2f}\n"
        
        if claim.get("settlement_amount"):
            settlement_date = excel_date_to_datetime(claim.get("settlement_date"))
            episode_body += f"Settled for ${claim['settlement_amount']:,.2f} on {format_date(settlement_date)}\n"
        
        if claim.get("insurance_notes"):
            episode_body += f"\nNotes: {claim['insurance_notes']}"
        
        type_abbrev = entity_type.replace("Claim", "")  # BIClaim -> BI
        logger.info(f"  [{type_abbrev}] {insurer} - #{claim_number}")
        
        if not dry_run:
            from roscoe.core.graphiti_client import add_case_episode
            await add_case_episode(
                case_name=case_name,
                episode_name=f"{full_name} with {insurer}",
                episode_body=episode_body.strip(),
                source="migration",
                reference_time=lor_sent or datetime.now(),
            )


async def create_provider_episodes(graphiti, case_name: str, providers: list, dry_run: bool = False) -> None:
    """Create episodes for each medical provider."""
    
    for provider in providers:
        provider_name = provider.get("provider_full_name", "Unknown Provider")
        billed_amount = provider.get("billed_amount", 0) or 0
        visits = provider.get("number_of_visits", 0) or 0
        
        treatment_start = excel_date_to_datetime(provider.get("date_treatment_started"))
        treatment_end = excel_date_to_datetime(provider.get("date_treatment_completed"))
        
        records_requested = excel_date_to_datetime(provider.get("date_medical_records_requested"))
        records_received = excel_date_to_datetime(provider.get("date_medical_records_received"))
        bills_requested = excel_date_to_datetime(provider.get("date_medical_bills_requested"))
        bills_received = excel_date_to_datetime(provider.get("medical_bills_received_date"))
        
        episode_body = f"""
Client is treating at {provider_name}.
"""
        
        if treatment_start:
            episode_body += f"Treatment started on {format_date(treatment_start)}.\n"
        
        if treatment_end:
            episode_body += f"Treatment completed on {format_date(treatment_end)}.\n"
        else:
            episode_body += "Treatment is ongoing.\n"
        
        if visits:
            episode_body += f"Total visits: {visits}.\n"
        
        if billed_amount:
            episode_body += f"Total billed: ${billed_amount:,.2f}.\n"
        
        # Records status
        if records_requested:
            episode_body += f"Medical records requested on {format_date(records_requested)}.\n"
        if records_received:
            episode_body += f"Medical records received on {format_date(records_received)}.\n"
        elif records_requested:
            episode_body += "Medical records not yet received.\n"
        
        # Bills status
        if bills_requested:
            episode_body += f"Medical bills requested on {format_date(bills_requested)}.\n"
        if bills_received:
            episode_body += f"Medical bills received on {format_date(bills_received)}.\n"
        elif bills_requested:
            episode_body += "Medical bills not yet received.\n"
        
        if provider.get("medical_provider_notes"):
            episode_body += f"\nNotes: {provider['medical_provider_notes']}"
        
        logger.info(f"  [PROVIDER] {provider_name} - ${billed_amount:,.2f}")
        
        if not dry_run:
            from roscoe.core.graphiti_client import add_case_episode
            await add_case_episode(
                case_name=case_name,
                episode_name=f"Treatment at {provider_name}",
                episode_body=episode_body.strip(),
                source="migration",
                reference_time=treatment_start or datetime.now(),
            )


async def create_notes_episodes(graphiti, case_name: str, notes: list, dry_run: bool = False, max_notes: int = 50) -> None:
    """Create episodes for case notes."""
    
    # Sort by date and take most recent
    sorted_notes = sorted(
        notes,
        key=lambda n: n.get("last_activity", "") or "",
        reverse=True
    )[:max_notes]
    
    for note in sorted_notes:
        note_text = note.get("note", "")
        if not note_text or len(note_text) < 10:
            continue
        
        author = note.get("author_name", "Unknown")
        note_date = note.get("last_activity", "")
        note_type = note.get("note_type", "General")
        
        episode_body = f"""
Case note by {author}:
{note_text}
"""
        
        # Parse date
        try:
            ref_time = datetime.fromisoformat(note_date) if note_date else datetime.now()
        except ValueError:
            ref_time = datetime.now()
        
        logger.info(f"  [NOTE] {note_date} - {author} - {note_text[:50]}...")
        
        if not dry_run:
            from roscoe.core.graphiti_client import add_case_episode
            await add_case_episode(
                case_name=case_name,
                episode_name=f"Case note: {note_type or 'General'}",
                episode_body=episode_body.strip(),
                source="migration",
                reference_time=ref_time,
            )


async def create_document_episodes(graphiti, case_name: str, case_path: Path, dry_run: bool = False) -> None:
    """Scan file system and create episodes for documents."""
    
    # Document type inference patterns
    DOC_PATTERNS = {
        "fee agreement": "retainer",
        "retainer": "retainer",
        "hipaa": "hipaa_authorization",
        "auth": "hipaa_authorization",
        "intake": "intake_form",
        "demand": "demand_package",
        "letter of rep": "letter_of_rep",
        "lor": "letter_of_rep",
        "records request": "records_request",
        "medical records": "medical_records",
        "bills": "medical_bills",
        "ledger": "medical_bills",
        "complaint": "pleading",
        "answer": "pleading",
        "motion": "pleading",
        "discovery": "discovery",
        "subpoena": "subpoena",
        "settlement": "settlement_document",
        "check": "settlement_check",
    }
    
    def infer_doc_type(filename: str, folder: str) -> str:
        """Infer document type from filename and folder."""
        name_lower = filename.lower()
        folder_lower = folder.lower()
        
        for pattern, doc_type in DOC_PATTERNS.items():
            if pattern in name_lower:
                return doc_type
        
        # Infer from folder
        if "medical" in folder_lower:
            return "medical_records"
        elif "insurance" in folder_lower:
            return "insurance_correspondence"
        elif "litigation" in folder_lower or "pleading" in folder_lower:
            return "pleading"
        elif "negotiation" in folder_lower:
            return "negotiation_correspondence"
        elif "client" in folder_lower:
            return "client_document"
        elif "lien" in folder_lower:
            return "lien_document"
        
        return "other"
    
    # Find all documents
    doc_extensions = {".pdf", ".docx", ".doc", ".xlsx", ".jpg", ".jpeg", ".png", ".tiff"}
    document_count = 0
    
    for doc_path in case_path.rglob("*"):
        if doc_path.is_file() and doc_path.suffix.lower() in doc_extensions:
            relative_path = doc_path.relative_to(case_path)
            folder = str(relative_path.parent)
            filename = doc_path.name
            doc_type = infer_doc_type(filename, folder)
            
            # Determine related entity from folder structure
            related_to = ""
            if "/" in folder:
                parts = folder.split("/")
                if len(parts) >= 2:
                    related_to = parts[1]  # e.g., "Medical Records/Allstar Chiropractic" -> "Allstar Chiropractic"
            
            episode_body = f"""
Document in case file: {filename}
Location: {folder}/
Document type: {doc_type}
File path: {relative_path}
"""
            
            if related_to and related_to not in ["archive", "[archive]"]:
                episode_body += f"Related to: {related_to}\n"
            
            document_count += 1
            
            if not dry_run:
                from roscoe.core.graphiti_client import add_case_episode
                await add_case_episode(
                    case_name=case_name,
                    episode_name=f"Document: {filename}",
                    episode_body=episode_body.strip(),
                    source="migration",
                )
    
    logger.info(f"  [DOCUMENTS] Found {document_count} documents")


async def migrate_case(case_path: Path, dry_run: bool = False, skip_documents: bool = False) -> bool:
    """Migrate a single case to Graphiti."""
    
    case_name = case_path.name
    case_info_path = case_path / "Case Information"
    
    # Check if Case Information folder exists
    if not case_info_path.exists():
        logger.warning(f"  No 'Case Information' folder found, skipping")
        return False
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Migrating: {case_name}")
    logger.info(f"{'='*60}")
    
    # Load JSON files
    overview_data = load_json_safe(case_info_path / "overview.json")
    insurance_data = load_json_safe(case_info_path / "insurance.json")
    providers_data = load_json_safe(case_info_path / "medical_providers.json")
    notes_data = load_json_safe(case_info_path / "notes.json")
    
    # Get graphiti client (only if not dry run)
    graphiti = None
    if not dry_run:
        from roscoe.core.graphiti_client import get_graphiti
        graphiti = await get_graphiti()
    
    # Create episodes
    if overview_data:
        await create_case_overview_episode(graphiti, case_name, overview_data[0], dry_run)
    
    if insurance_data:
        await create_insurance_episodes(graphiti, case_name, insurance_data, dry_run)
    
    if providers_data:
        await create_provider_episodes(graphiti, case_name, providers_data, dry_run)
    
    if notes_data:
        await create_notes_episodes(graphiti, case_name, notes_data, dry_run, max_notes=20)
    
    # Scan for documents (unless skipped)
    if not skip_documents:
        await create_document_episodes(graphiti, case_name, case_path, dry_run)
    else:
        logger.info(f"  [DOCUMENTS] Skipped (--skip-documents flag)")
    
    return True


async def main():
    parser = argparse.ArgumentParser(description="Migrate case data to Graphiti knowledge graph")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be migrated without doing it")
    parser.add_argument("--case", type=str, help="Migrate only a specific case")
    parser.add_argument("--limit", type=int, help="Migrate only the first N cases")
    parser.add_argument("--skip-cases", type=int, default=0, help="Skip the first N cases (for resuming)")
    parser.add_argument("--skip-documents", action="store_true", help="Skip document scanning")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Graphiti Migration Script")
    logger.info("=" * 60)
    logger.info(f"Projects directory: {PROJECTS_DIR}")
    logger.info(f"Dry run: {args.dry_run}")
    
    if not PROJECTS_DIR.exists():
        logger.error(f"Projects directory not found: {PROJECTS_DIR}")
        sys.exit(1)
    
    # Get list of cases
    if args.case:
        case_paths = [PROJECTS_DIR / args.case]
        if not case_paths[0].exists():
            logger.error(f"Case not found: {args.case}")
            sys.exit(1)
    else:
        case_paths = sorted([p for p in PROJECTS_DIR.iterdir() if p.is_dir()])
    
    if args.skip_cases:
        logger.info(f"Skipping first {args.skip_cases} cases (already processed)")
        case_paths = case_paths[args.skip_cases:]
    
    if args.limit:
        case_paths = case_paths[:args.limit]
    
    logger.info(f"Cases to migrate: {len(case_paths)}")
    
    # Initialize Graphiti (if not dry run)
    if not args.dry_run:
        logger.info("\nInitializing Graphiti client...")
        from roscoe.core.graphiti_client import get_graphiti
        await get_graphiti()
        logger.info("Graphiti client initialized")
    
    # Migrate each case
    success_count = 0
    fail_count = 0
    
    if args.skip_documents:
        logger.info("Document scanning DISABLED (--skip-documents)")
    
    for case_path in case_paths:
        try:
            success = await migrate_case(case_path, args.dry_run, args.skip_documents)
            if success:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            logger.error(f"Failed to migrate {case_path.name}: {e}")
            fail_count += 1
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Migration Complete")
    logger.info("=" * 60)
    logger.info(f"Successfully migrated: {success_count}")
    logger.info(f"Failed/skipped: {fail_count}")
    
    if not args.dry_run:
        from roscoe.core.graphiti_client import close_graphiti
        await close_graphiti()


if __name__ == "__main__":
    asyncio.run(main())
