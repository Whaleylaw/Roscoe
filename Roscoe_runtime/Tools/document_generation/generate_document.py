#!/usr/bin/env python3
"""
Unified Document Generation Tool

Single entry point for all document generation. The agent:
1. Copies a template to its destination folder
2. (For agent-filled templates) Fills in the content
3. Passes the path to this tool

The tool then:
1. Identifies the template from the file content
2. Extracts context from the file path (project, insurance company, etc.)
3. Loads relevant case data from JSON files
4. Fills placeholders and generates output

Usage:
    python generate_document.py "/Project/Insurance/State Farm/LOR to PIP.docx"
    python generate_document.py "/Project/Documents/Demand/Demand Letter.md"

The path provides everything needed:
- The template file itself (to identify what type)
- The location context (to know what data to pull)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from path_parser import parse_path_context, get_case_json_path, get_context_entity_id
from template_identifier import identify_template, get_template_by_id
from handlers.docx_handler import process_docx_template
from handlers.markdown_handler import process_markdown_template
from handlers.pdf_handler import process_pdf_form


# Base paths
CLAUDE_DOCS = Path(os.environ.get("CLAUDE_DOCS", os.environ.get("ROSCOE_ROOT", str(Path(__file__).resolve().parents[2]))))
TEMPLATES_DIR = CLAUDE_DOCS / "templates"


def unwrap_nested_data(data: Any) -> Any:
    """
    Unwrap nested data structures like jsonb_agg from database exports.
    
    Handles structures like:
    - [{"jsonb_agg": [{"field": "value"}]}] -> {"field": "value"}
    - [{"field": "value"}] -> {"field": "value"} (for single-item lists that should be dicts)
    
    Args:
        data: Raw JSON data that may have nested structure
    
    Returns:
        Unwrapped data
    """
    if isinstance(data, list) and len(data) == 1:
        item = data[0]
        if isinstance(item, dict):
            # Check for jsonb_agg wrapper
            if "jsonb_agg" in item and len(item) == 1:
                inner = item["jsonb_agg"]
                if isinstance(inner, list) and len(inner) == 1:
                    return inner[0]
                elif isinstance(inner, list) and len(inner) > 1:
                    return inner
                return inner
            # Single-item list with dict - return the dict
            return item
    return data


def load_case_data(case_info_path: Path) -> Dict[str, Any]:
    """
    Load all relevant case JSON files.
    
    Args:
        case_info_path: Path to Case Information folder
    
    Returns:
        Dict with overview, insurance, medical_providers, liens, contacts data
    """
    case_data = {}
    
    json_files = [
        "overview.json",
        "insurance.json",
        "medical_providers.json",
        "liens.json",
        "contacts.json",
        "litigation.json",
        "notes.json",
    ]
    
    for json_file in json_files:
        json_path = case_info_path / json_file
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                    
                    # Unwrap nested structures (especially for overview.json with jsonb_agg)
                    key = json_file.replace('.json', '')
                    if key == "overview":
                        # Overview should be a single dict, not a list
                        case_data[key] = unwrap_nested_data(raw_data)
                    else:
                        case_data[key] = raw_data
            except json.JSONDecodeError:
                pass
    
    return case_data


def load_client_from_database(project_name: str) -> Dict[str, Any]:
    """
    Load client data from the master Database/clients.json.
    
    Args:
        project_name: The project name to match (e.g., "Henrietta-Jenkins-MVA-5-20-2025")
    
    Returns:
        Client data dict or empty dict if not found
    """
    clients_path = CLAUDE_DOCS / "Database" / "clients.json"
    
    if not clients_path.exists():
        return {}
    
    try:
        with open(clients_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Handle nested jsonb_agg structure
        clients_list = []
        if isinstance(raw_data, list) and len(raw_data) > 0:
            first_item = raw_data[0]
            if isinstance(first_item, dict) and "jsonb_agg" in first_item:
                clients_list = first_item.get("jsonb_agg", [])
            else:
                clients_list = raw_data
        
        # Find client by project_name
        for client in clients_list:
            if isinstance(client, dict):
                if client.get("project_name") == project_name:
                    return client
        
        return {}
    except Exception:
        return {}


def load_firm_config() -> Dict[str, Any]:
    """Load firm configuration."""
    config_paths = [
        CLAUDE_DOCS / "Tools" / "document_generation" / "firm_config.json",
        TEMPLATES_DIR / "firm_config.json",
    ]
    
    for path in config_paths:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    return {
        "firm_name": "The Whaley Law Firm",
        "attorney_name": "Aaron G. Whaley, Esq.",
        "address": "712 Lyndon Lane",
        "city_state_zip": "Louisville, KY 40222",
        "phone": "(502) 583-4022",
        "fax": "(502) 364-9363",
    }


def find_entity_by_name(
    entities: Any,
    name: str,
    name_fields: List[str]
) -> Optional[Dict]:
    """
    Find an entity by matching name against various fields.
    
    Args:
        entities: Dict or list of entities
        name: Name to search for
        name_fields: List of field names to check
    
    Returns:
        Matching entity dict or None
    """
    if not name:
        return None
    
    name_lower = name.lower().strip()
    
    def check_entity(entity: Dict) -> bool:
        for field in name_fields:
            value = entity.get(field, "")
            if isinstance(value, str) and name_lower in value.lower():
                return True
        return False
    
    if isinstance(entities, dict):
        # Could be keyed by company name or other identifier
        for key, value in entities.items():
            if isinstance(value, dict):
                if check_entity(value):
                    return value
            elif isinstance(key, str) and name_lower in key.lower():
                return value if isinstance(value, dict) else {"name": key, "data": value}
    elif isinstance(entities, list):
        for entity in entities:
            if isinstance(entity, dict) and check_entity(entity):
                return entity
    
    return None


def build_context(
    path_context: Dict[str, Any],
    case_data: Dict[str, Any],
    template_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build the full context dictionary for placeholder replacement.
    
    Args:
        path_context: Result from parse_path_context
        case_data: Loaded case JSON data
        template_info: Template identification info
    
    Returns:
        Context dictionary with all placeholder values
    """
    context = {}
    
    # Load firm config
    firm_config = load_firm_config()
    
    # === Static/Computed Values ===
    context["TODAY"] = datetime.now().strftime("%B %d, %Y")
    context["TODAY_LONG"] = context["TODAY"]
    context["TODAY_SHORT"] = datetime.now().strftime("%m/%d/%Y")
    
    # Firm info - handle both nested and flat structure
    firm_data = firm_config.get("firm", {})
    attorney_data = firm_config.get("attorney", {})
    
    firm_name = firm_data.get("full_name", firm_data.get("name", firm_config.get("firm_name", "")))
    attorney_name = attorney_data.get("name", firm_config.get("attorney_name", ""))
    
    context["firm"] = firm_config
    context["primary"] = f"{attorney_name}\n{firm_name}"
    context["firm.name"] = firm_name
    context["firm.attorney"] = attorney_name
    context["firm.signature"] = context["primary"]
    
    # Team roles from firm config
    team_config = firm_config.get("team", {})
    for role_name, role_data in team_config.items():
        if isinstance(role_data, dict):
            for field, value in role_data.items():
                context[f"team.role.{role_name}.{field}"] = value
    
    # === Client/Case Data ===
    overview = case_data.get("overview", {})
    
    # Load client from master database for DOB and SSN
    project_name = path_context.get("project", "")
    client_db_data = load_client_from_database(project_name)
    
    client_name = overview.get("client_name", "")
    context["client.name"] = client_name
    context["client.firstname"] = client_name.split()[0] if client_name else ""
    context["client.address"] = overview.get("client_address", "")
    context["client.addressBlock"] = overview.get("client_address", "")
    context["client.phone"] = overview.get("client_phone", "")
    context["client.email"] = overview.get("client_email", "")
    
    # Legacy placeholder mappings for older templates
    context["intake.clientInformation.name"] = client_name
    
    # DOB from database - format nicely
    dob_raw = client_db_data.get("date_of_birth", "")
    if dob_raw:
        try:
            from dateutil.parser import parse as date_parse
            parsed_dob = date_parse(dob_raw)
            context["client.dob"] = parsed_dob.strftime("%m/%d/%Y")
            context["client.birthDate"] = parsed_dob.strftime("%m/%d/%Y")
        except Exception:
            context["client.dob"] = dob_raw
            context["client.birthDate"] = dob_raw
    else:
        context["client.dob"] = ""
        context["client.birthDate"] = ""
    
    # SSN from database
    ssn = client_db_data.get("social_security_number", "")
    context["client.ssn"] = ssn
    context["client.custom.ssn"] = ssn
    
    # Format accident date
    accident_date = overview.get("accident_date", "")
    if accident_date:
        try:
            # Try to parse and reformat
            from dateutil.parser import parse as date_parse
            parsed = date_parse(accident_date)
            context["incidentDate"] = parsed.strftime("%B %d, %Y")
        except Exception:
            context["incidentDate"] = accident_date
    else:
        context["incidentDate"] = ""
    
    # Case type
    project_name = path_context.get("project", "")
    if "MVA" in project_name:
        context["intake.incidenttype"] = "motor vehicle collision"
        context["casesummary.caseType"] = "Motor Vehicle Accident"
    elif "SF" in project_name or "S&F" in project_name:
        context["intake.incidenttype"] = "slip and fall incident"
        context["casesummary.caseType"] = "Slip and Fall"
    elif "WC" in project_name:
        context["intake.incidenttype"] = "workplace injury"
        context["casesummary.caseType"] = "Workers' Compensation"
    else:
        context["intake.incidenttype"] = "incident"
        context["casesummary.caseType"] = "Personal Injury"
    
    # === Context-Specific Data ===
    context_type = path_context.get("context_type")
    context_name = path_context.get("context_name")
    
    # Get contacts for cross-referencing
    contacts = case_data.get("contacts", [])
    
    if context_type == "insurance" and context_name:
        insurance_data = case_data.get("insurance", {})
        entity = find_entity_by_name(
            insurance_data,
            context_name,
            ["insurance_company_name", "company_name", "name"]
        )
        
        if entity:
            adjuster_name = entity.get("insurance_adjuster_name", "")
            company_name = entity.get("insurance_company_name", "")
            
            context["insurance.insuranceCompany.name"] = company_name
            context["insurance.insuranceAdjuster.name"] = adjuster_name
            context["insurance.insuranceAdjuster.firstname"] = (
                adjuster_name.split()[0] if adjuster_name else ""
            )
            context["insurance.claimNumber"] = entity.get("claim_number", "")
            
            # Cross-reference contacts.json for adjuster details
            adjuster_contact = find_entity_by_name(contacts, adjuster_name, ["full_name"])
            
            if adjuster_contact:
                # Get adjuster email from contacts
                adjuster_email = adjuster_contact.get("email", "")
                if adjuster_email:
                    context["insurance.insuranceAdjuster.email1"] = adjuster_email
                
                # Get adjuster phone from contacts
                adjuster_phone = adjuster_contact.get("phone", "")
                if adjuster_phone:
                    context["insurance.insuranceAdjuster.phone"] = adjuster_phone
                
                # Get adjuster address from contacts (preferred)
                adjuster_address = adjuster_contact.get("address")
                if adjuster_address:
                    context["insurance.insuranceAdjuster.addressBlock"] = adjuster_address
                    context["insurance.insuranceAdjuster.address1Block"] = adjuster_address
                    context["insurance.insuranceCompany.addressBlock"] = adjuster_address
            
            # Fallback: If no adjuster address, get company address from contacts
            if not context.get("insurance.insuranceCompany.addressBlock"):
                company_contact = find_entity_by_name(contacts, company_name, ["full_name"])
                if company_contact and company_contact.get("address"):
                    company_addr = company_contact.get("address")
                    context["insurance.insuranceCompany.addressBlock"] = company_addr
                    # Also set adjuster address variants to company address as fallback
                    if not context.get("insurance.insuranceAdjuster.addressBlock"):
                        context["insurance.insuranceAdjuster.addressBlock"] = company_addr
                        context["insurance.insuranceAdjuster.address1Block"] = company_addr
    
    elif context_type == "medical_provider" and context_name:
        providers = case_data.get("medical_providers", {})
        entity = find_entity_by_name(
            providers,
            context_name,
            ["provider_full_name", "name", "provider_name"]
        )
        
        provider_name = ""
        if entity:
            provider_name = entity.get("provider_full_name", "")
            context["medical.provider.name"] = provider_name
        
        # Cross-reference contacts.json for provider details
        provider_contact = find_entity_by_name(contacts, context_name, ["full_name"])
        
        if provider_contact:
            # Get address, phone, fax, email from contacts
            if provider_contact.get("address"):
                context["medical.provider.addressBlock"] = provider_contact.get("address")
                context["medical.provider.address1Block"] = provider_contact.get("address")
            if provider_contact.get("phone"):
                context["medical.provider.phone"] = provider_contact.get("phone")
                # Combine phone/fax for phoneFax field
                fax = provider_contact.get("fax", "")
                phone = provider_contact.get("phone", "")
                if fax:
                    context["medical.provider.phoneFax"] = f"Ph: {phone} | Fax: {fax}"
                else:
                    context["medical.provider.phoneFax"] = f"Ph: {phone}"
            if provider_contact.get("fax"):
                context["medical.provider.fax"] = provider_contact.get("fax")
            if provider_contact.get("email"):
                context["medical.provider.email"] = provider_contact.get("email")
    
    elif context_type == "lien" and context_name:
        liens = case_data.get("liens", {})
        entity = find_entity_by_name(
            liens,
            context_name,
            ["lien_holder_name", "name", "holder_name"]
        )
        
        lien_holder_name = ""
        if entity:
            lien_holder_name = entity.get("lien_holder_name", "")
            context["liens.lienholder.name"] = lien_holder_name
            context["liens.claimNumber"] = entity.get("claim_number", "")
        
        # Cross-reference contacts.json for lien holder details
        lien_contact = find_entity_by_name(contacts, context_name, ["full_name"])
        
        if lien_contact:
            # Get address, phone, fax, email from contacts
            if lien_contact.get("address"):
                context["liens.lienholder.addressBlock"] = lien_contact.get("address")
                context["liens.lienholder.address1Block"] = lien_contact.get("address")
            if lien_contact.get("phone"):
                context["liens.lienholder.phone"] = lien_contact.get("phone")
                # Combine phone/fax for phoneFax field
                fax = lien_contact.get("fax", "")
                phone = lien_contact.get("phone", "")
                if fax:
                    context["liens.lienholder.phoneFax"] = f"Ph: {phone} | Fax: {fax}"
                else:
                    context["liens.lienholder.phoneFax"] = f"Ph: {phone}"
            if lien_contact.get("email"):
                context["liens.lienholder.email"] = lien_contact.get("email")
    
    elif context_type == "litigation":
        litigation = case_data.get("litigation", {})
        contacts = case_data.get("contacts", [])
        
        # Search contacts for defendant/liable party by role
        defendant_found = False
        if isinstance(contacts, list):
            for contact in contacts:
                if isinstance(contact, dict):
                    roles = contact.get("roles", [])
                    if isinstance(roles, str):
                        roles = [roles]
                    # Check if any role matches defendant-like roles
                    if any(r in ["defendant", "liable_party", "adverse", "at_fault"] for r in roles):
                        context["defendant.name"] = contact.get("full_name", "")
                        context["defendant.address"] = contact.get("address", "")
                        defendant_found = True
                        break
        elif isinstance(contacts, dict):
            for key, contact in contacts.items():
                if isinstance(contact, dict):
                    roles = contact.get("roles", contact.get("role", []))
                    if isinstance(roles, str):
                        roles = [roles]
                    if any(r in ["defendant", "liable_party", "adverse", "at_fault"] for r in roles):
                        context["defendant.name"] = contact.get("full_name", "")
                        context["defendant.address"] = contact.get("address", "")
                        defendant_found = True
                        break
        
        # Pull from litigation.json directly if defendant fields exist there
        if not defendant_found and litigation:
            if litigation.get("defendant_name"):
                context["defendant.name"] = litigation.get("defendant_name", "")
            if litigation.get("defendant_address"):
                context["defendant.address"] = litigation.get("defendant_address", "")
        
        # Litigation-specific fields from litigation.json
        context["litigation.case_number"] = litigation.get("case_number", "")
        context["litigation.caseNumber"] = litigation.get("case_number", "")
        context["litigation.court"] = litigation.get("court", "")
        context["litigation.judge"] = litigation.get("judge", "")
        context["litigation.opposing_counsel"] = litigation.get("opposing_counsel", "")
        context["litigation.opposingCounsel"] = litigation.get("opposing_counsel", "")
        context["litigation.opposing_counsel_email"] = litigation.get("opposing_counsel_email", "")
        context["litigation.opposing_counsel_phone"] = litigation.get("opposing_counsel_phone", "")
        context["litigation.clientDepositionDate"] = litigation.get("plaintiff_deposition_date", litigation.get("client_deposition_date", ""))
        context["litigation.clientDepositionTime"] = litigation.get("client_deposition_time", "")
        context["litigation.discovery_cutoff_date"] = litigation.get("discovery_cutoff_date", "")
        context["litigation.trial_date"] = litigation.get("trial_date", "")
        context["litigation.mediation_date"] = litigation.get("mediation_date", "")
    
    return context


# Category mapping for naming convention
CATEGORY_MAP = {
    "insurance": "Insurance",
    "medical_provider": "Medical Records",
    "lien": "Liens",
    "litigation": "Litigation",
    "client": "Client",
    "demand": "Negotiation Settlement",
    "correspondence": "Correspondence",
    "discovery": "Litigation",
}


def generate_proper_filename(
    path_context: Dict[str, Any],
    case_data: Dict[str, Any],
    template_info: Dict[str, Any],
    original_filename: str
) -> str:
    """
    Generate a properly formatted filename following the naming convention.
    
    Format: YYYY-MM-DD - {Client Name} - {Category} - {Originator} - {Description}.ext
    
    Args:
        path_context: Result from parse_path_context
        case_data: Loaded case JSON data
        template_info: Template identification info
        original_filename: Original filename for the description
    
    Returns:
        Properly formatted filename
    """
    # Get today's date
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Get client name from overview
    overview = case_data.get("overview", {})
    client_name = overview.get("client_name", "Unknown Client")
    
    # Get category from context type
    context_type = path_context.get("context_type", "")
    category = CATEGORY_MAP.get(context_type, "Documents")
    
    # Get originator (WLF to [recipient])
    context_name = path_context.get("context_name", "")
    if context_name:
        # Shorten long names (e.g., "Progressive Insurance Company" -> "Progressive")
        short_name = context_name.split()[0] if context_name else ""
        originator = f"WLF to {short_name}"
    else:
        originator = "WLF"
    
    # Get description from original filename or template
    # Remove extension and clean up
    original_stem = Path(original_filename).stem
    # Remove common prefixes like "2022 Whaley" etc.
    description = original_stem
    for prefix in ["2021 Whaley", "2022 Whaley", "2023 Whaley"]:
        if description.startswith(prefix):
            description = description[len(prefix):].strip()
    # Remove duplicate spaces and clean
    description = " ".join(description.split())
    
    # Get extension
    ext = Path(original_filename).suffix
    
    # Build filename
    filename = f"{date_str} - {client_name} - {category} - {originator} - {description}{ext}"
    
    # Clean any double spaces
    filename = " ".join(filename.split())
    
    return filename


def generate_document(path: str) -> Dict[str, Any]:
    """
    Process a document template at the given path.
    
    This is the main entry point. The agent:
    1. Copies a template to the destination folder
    2. (For agent-filled templates) Fills in the content
    3. Calls this function with the path
    
    The path provides:
    - The template file itself (to identify what it is)
    - The location context (to know what data to pull)
    
    Args:
        path: Full path to the template in its destination location
              e.g., "/Project/Insurance/State Farm/LOR.docx"
    
    Returns:
        Dict with:
            - status: "success" | "error"
            - docx_path: Path to DOCX output
            - pdf_path: Path to PDF output
            - fields_filled: List of placeholders filled
            - fields_missing: List of placeholders that couldn't be filled
            - template_id: Identified template ID
            - context_info: Info about the context extracted from path
            - errors: List of error messages
    """
    result = {
        "status": "error",
        "docx_path": None,
        "pdf_path": None,
        "fields_filled": [],
        "fields_missing": [],
        "template_id": None,
        "context_info": {},
        "errors": [],
        "warnings": [],
    }
    
    file_path = Path(path)
    
    # Validate file exists
    if not file_path.exists():
        result["errors"].append(f"File not found: {path}")
        return result
    
    # Step 1: Parse path for context
    path_context = parse_path_context(path)
    result["context_info"] = path_context
    
    if not path_context.get("project"):
        result["warnings"].append("Could not determine project from path")
    
    # Step 2: Identify template
    template_info = identify_template(path)
    result["template_id"] = template_info.get("template_id")
    
    if not template_info.get("template_id"):
        result["warnings"].append(
            f"Could not identify template. Processing as generic {template_info.get('template_type', 'unknown')} file."
        )
    
    # Step 3: Load case data
    case_data = {}
    if path_context.get("case_info_path"):
        case_info_path = Path(path_context["case_info_path"])
        if case_info_path.exists():
            case_data = load_case_data(case_info_path)
        else:
            result["warnings"].append(f"Case Information folder not found: {case_info_path}")
    
    # Step 4: Build context
    context = build_context(path_context, case_data, template_info)
    
    # Step 5: Route to appropriate handler based on file type
    file_ext = file_path.suffix.lower()
    
    try:
        if file_ext == '.docx':
            handler_result = process_docx_template(
                str(file_path),
                context,
                output_pdf=True
            )
        elif file_ext == '.md':
            handler_result = process_markdown_template(
                str(file_path),
                context,
                output_pdf=True,
                output_docx=True
            )
        elif file_ext == '.pdf':
            handler_result = process_pdf_form(
                str(file_path),
                context
            )
        else:
            result["errors"].append(f"Unsupported file type: {file_ext}")
            return result
        
        # Merge handler result
        result["status"] = handler_result.get("status", "error")
        result["docx_path"] = handler_result.get("docx_path")
        result["pdf_path"] = handler_result.get("pdf_path")
        result["fields_filled"] = handler_result.get("fields_filled", [])
        result["fields_missing"] = handler_result.get("fields_missing", [])
        
        if handler_result.get("errors"):
            result["errors"].extend(handler_result["errors"])
        
        # Step 6: Rename output files to follow naming convention
        if result["status"] == "success":
            try:
                # Generate proper filename
                proper_docx_name = generate_proper_filename(
                    path_context, case_data, template_info, file_path.name
                )
                
                # Get the directory
                output_dir = file_path.parent
                
                # Rename DOCX if it exists
                if result["docx_path"]:
                    old_docx = Path(result["docx_path"])
                    if old_docx.exists():
                        new_docx = output_dir / proper_docx_name.replace(file_path.suffix, ".docx")
                        if old_docx != new_docx:
                            old_docx.rename(new_docx)
                            result["docx_path"] = str(new_docx)
                
                # Rename PDF if it exists
                if result["pdf_path"]:
                    old_pdf = Path(result["pdf_path"])
                    if old_pdf.exists():
                        new_pdf = output_dir / proper_docx_name.replace(file_path.suffix, ".pdf")
                        if old_pdf != new_pdf:
                            old_pdf.rename(new_pdf)
                            result["pdf_path"] = str(new_pdf)
                
                # Rename the original source file (DOCX/MD) to match
                if file_path.exists():
                    new_source = output_dir / proper_docx_name
                    if file_path != new_source:
                        file_path.rename(new_source)
                        result["source_path"] = str(new_source)
                
            except Exception as rename_error:
                result["warnings"].append(f"Could not rename output files: {rename_error}")
        
    except Exception as e:
        result["errors"].append(str(e))
        import traceback
        result["errors"].append(traceback.format_exc())
    
    return result


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Unified Document Generation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a filled LOR from template in Insurance folder
  python generate_document.py "/John-Doe-MVA-01-01-2025/Insurance/State Farm/LOR to PIP.docx"
  
  # Generate demand letter from filled markdown
  python generate_document.py "/John-Doe-MVA-01-01-2025/Documents/Demand/Demand Letter.md"
  
  # Fill a PDF form
  python generate_document.py "/John-Doe-MVA-01-01-2025/Insurance/State Farm/PIP Application.pdf"

The path provides everything:
  - The template file (to identify what it is)
  - The location context (to know what data to pull)
        """
    )
    
    parser.add_argument(
        "path",
        help="Path to the document template in its destination location"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug information"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        print(f"Processing: {args.path}", file=sys.stderr)
    
    result = generate_document(args.path)
    
    print(json.dumps(result, indent=2 if args.pretty else None, default=str))
    
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())

