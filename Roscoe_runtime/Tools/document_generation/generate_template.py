#!/usr/bin/env python3
"""
Unified Template Generation Tool

Generates documents from templates using a simple interface:
- --project: The project/case name
- --template-id: Template ID from template_registry.json
- --context-id: ID of the entity to use (insurance ID, provider ID, lien ID, etc.)

Usage:
    # Generate a BI Letter of Rep (template ID 1) for insurance ID 42
    python generate_template.py --project "John-Doe-MVA-01-01-2025" --template-id 1 --context-id 42
    
    # List all templates
    python generate_template.py --list
    
    # Interactive mode (prompts for context)
    python generate_template.py --project "John-Doe-MVA-01-01-2025" --template-id 1 --interactive
"""

import argparse
import json
import os
import re
import subprocess
import sys
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from zipfile import ZipFile, ZIP_DEFLATED


# ============================================================
# Configuration
# ============================================================

# Base paths - adjust these to your environment
CLAUDE_DOCS = Path(os.environ.get("ROSCOE_ROOT", str(Path(__file__).resolve().parents[2])))
TEMPLATES_DIR = CLAUDE_DOCS / "templates"
TEMPLATE_REGISTRY_PATH = TEMPLATES_DIR / "template_registry.json"
DATABASE_DIR = CLAUDE_DOCS / "Database"
ID_TRACKER_PATH = DATABASE_DIR / "id_tracker.json"


# ============================================================
# Registry & Data Loading
# ============================================================

def load_template_registry() -> Dict:
    """Load the template registry."""
    with open(TEMPLATE_REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_id_tracker() -> Dict:
    """Load the ID tracker."""
    with open(ID_TRACKER_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_template_by_id(template_id: int, registry: Dict) -> Optional[Dict]:
    """Get a template definition by its numeric ID."""
    for template in registry.get("templates", []):
        if template.get("id") == template_id:
            return template
    return None


def get_project_path(project_name: str) -> Path:
    """Get the path to a project folder."""
    # Check in multiple locations
    possible_paths = [
        CLAUDE_DOCS / project_name,
        CLAUDE_DOCS / "projects" / project_name,
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Return default path even if it doesn't exist
    return CLAUDE_DOCS / project_name


def load_case_json(project_path: Path, json_name: str) -> Any:
    """Load a JSON file from the project's Case Information folder."""
    json_path = project_path / "Case Information" / json_name
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {} if json_name.endswith('.json') else []


def load_master_json(json_name: str) -> List[Dict]:
    """Load a JSON file from the master Database folder."""
    json_path = DATABASE_DIR / json_name
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    return []


# ============================================================
# Context Resolution
# ============================================================

def get_entity_by_id(
    project_name: str,
    project_path: Path,
    context_type: str,
    entity_id: int
) -> Optional[Dict]:
    """
    Get an entity (insurance, provider, lien, etc.) by its ID.
    
    First checks the project's Case Information folder, then falls back
    to the master Database folder.
    """
    # Map context type to JSON source
    context_map = {
        "insurance": ("insurance.json", "id"),
        "medical_provider": ("medical_providers.json", "id"),
        "lien": ("liens.json", "id"),
        "litigation_contact": ("contacts.json", "contact_id"),
    }
    
    if context_type not in context_map:
        return None
    
    json_name, id_field = context_map[context_type]
    
    # Try project-specific JSON first
    project_data = load_case_json(project_path, json_name)
    
    if isinstance(project_data, dict):
        # Single-entry JSON (like overview.json)
        if project_data.get(id_field) == entity_id:
            return project_data
        # Try nested entries
        for key, value in project_data.items():
            if isinstance(value, dict) and value.get(id_field) == entity_id:
                return value
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and item.get(id_field) == entity_id:
                        return item
    elif isinstance(project_data, list):
        # Array of entries
        for item in project_data:
            if isinstance(item, dict) and item.get(id_field) == entity_id:
                return item
    
    # Fall back to master Database
    master_data = load_master_json(json_name)
    for item in master_data:
        if item.get(id_field) == entity_id:
            # Verify it belongs to this project
            if item.get("project_name") == project_name:
                return item
    
    return None


def get_directory_entry(name: str) -> Optional[Dict]:
    """Look up a person/company in the master directory."""
    directory = load_master_json("directory.json")
    name_lower = name.lower().strip() if name else ""
    
    for entry in directory:
        full_name = entry.get("full_name", "").lower().strip()
        if full_name == name_lower or name_lower in full_name:
            return entry
    
    return None


def format_address_block(entry: Dict) -> str:
    """Format a directory entry as an address block."""
    if not entry:
        return ""
    
    lines = []
    if entry.get("full_name"):
        lines.append(entry["full_name"])
    if entry.get("address"):
        lines.append(entry["address"])
    
    return "\n".join(lines)


def build_context(
    project_name: str,
    project_path: Path,
    template: Dict,
    entity: Optional[Dict],
    registry: Dict
) -> Dict[str, Any]:
    """
    Build the full context dictionary for placeholder replacement.
    """
    context = {}
    
    # Load case overview
    overview = load_case_json(project_path, "overview.json")
    
    # ==================== Static/Computed Values ====================
    context["TODAY_LONG"] = datetime.now().strftime("%B %d, %Y")
    context["TODAY_SHORT"] = datetime.now().strftime("%m/%d/%Y")
    context["TODAY"] = context["TODAY_LONG"]
    
    # Primary attorney signature block
    static = registry.get("static_config", {})
    context["primary"] = static.get("primary_attorney", {}).get("signature_block", "")
    
    # ==================== Client/Case Data ====================
    client_name = overview.get("client_name", "")
    context["client.name"] = client_name
    context["client.firstname"] = client_name.split()[0] if client_name else ""
    context["client.addressBlock"] = overview.get("client_address", "")
    context["client.phone"] = overview.get("client_phone", "")
    context["client.email"] = overview.get("client_email", "")
    context["client.birthDate"] = overview.get("client_dob", "")
    context["client.ssn"] = overview.get("client_ssn", "")
    
    # Format accident date
    accident_date = overview.get("accident_date", "")
    if accident_date:
        try:
            parsed = datetime.strptime(accident_date, "%m-%d-%Y")
            context["incidentDate"] = parsed.strftime("%B %d, %Y")
        except:
            context["incidentDate"] = accident_date
    else:
        context["incidentDate"] = ""
    
    # Case type from project name
    if "MVA" in project_name:
        context["intake.incidenttype"] = "motor vehicle collision"
    elif "SF" in project_name or "S&F" in project_name:
        context["intake.incidenttype"] = "slip and fall incident"
    elif "WC" in project_name:
        context["intake.incidenttype"] = "workplace injury"
    else:
        context["intake.incidenttype"] = "incident"
    
    # ==================== Entity-Specific Context ====================
    if entity:
        context_type = template.get("context_type", "")
        
        if context_type == "insurance":
            # Insurance adjuster lookup
            adjuster_name = entity.get("insurance_adjuster_name", "")
            company_name = entity.get("insurance_company_name", "")
            
            context["insurance.insuranceAdjuster.name"] = adjuster_name
            context["insurance.claimNumber"] = entity.get("claim_number", "")
            context["insurance.insuranceCompany.name"] = company_name
            
            # Adjuster directory lookup
            if adjuster_name:
                adjuster = get_directory_entry(adjuster_name)
                if adjuster:
                    context["insurance.insuranceAdjuster.firstname"] = adjuster_name.split()[0] if adjuster_name else ""
                    context["insurance.insuranceAdjuster.email1"] = adjuster.get("email1", adjuster.get("email", ""))
                    context["insurance.insuranceCompany.addressBlock"] = format_address_block(adjuster)
            
            # Company directory lookup as fallback for address
            if not context.get("insurance.insuranceCompany.addressBlock") and company_name:
                company = get_directory_entry(company_name)
                if company:
                    context["insurance.insuranceCompany.addressBlock"] = format_address_block(company)
        
        elif context_type == "medical_provider":
            provider_name = entity.get("provider_full_name", "")
            context["medical.provider.name"] = provider_name
            context["medical.provider.phoneFax"] = entity.get("phone", "") + " / " + entity.get("fax", "")
            
            # Provider directory lookup
            if provider_name:
                provider = get_directory_entry(provider_name)
                if provider:
                    context["medical.provider.addressBlock"] = format_address_block(provider)
                    context["medical.provider.phone"] = provider.get("phone", "")
                    context["medical.provider.fax"] = provider.get("fax", "")
        
        elif context_type == "lien":
            holder_name = entity.get("lien_holder_name", "")
            context["liens.lienholder.name"] = holder_name
            context["liens.claimNumber"] = entity.get("claim_number", "")
            context["liens.datelorsent"] = entity.get("date_lien_notice_sent", "")
            
            # Lienholder directory lookup
            if holder_name:
                holder = get_directory_entry(holder_name)
                if holder:
                    context["liens.lienholder.addressBlock"] = format_address_block(holder)
                    context["liens.lienholder.phoneFax"] = holder.get("phone", "") + " / " + holder.get("fax", "")
        
        elif context_type == "litigation_contact":
            context["litigation.contact.name"] = entity.get("full_name", "")
            context["litigation.contact.addressBlock"] = entity.get("address", "")
    
    # ==================== Team Roles ====================
    team = static.get("team_roles", {})
    for role_key, role_data in team.items():
        context[f"team.role.{role_key}.fullName"] = role_data.get("fullName", "")
        context[f"team.role.{role_key}.email"] = role_data.get("email", "")
    
    return context


# ============================================================
# Template Filling
# ============================================================

def replace_placeholders_in_xml(xml_content: str, context: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
    """
    Replace all {{placeholder}} patterns in XML content.
    
    Handles cases where Word splits placeholders across multiple XML elements.
    """
    filled = []
    missing = []
    result = xml_content
    
    # Fix split placeholders where Word has put braces in separate elements
    complex_split = r'\{</w:t></w:r>(<w:r[^>]*><w:rPr>.*?</w:rPr>)?<w:t[^>]*>\{([a-zA-Z._]+)\}\}'
    result = re.sub(complex_split, r'{{\2}}', result, flags=re.DOTALL)
    
    simple_split = r'\{</w:t><w:t[^>]*>\{([a-zA-Z._]+)\}\}'
    result = re.sub(simple_split, r'{{\1}}', result)
    
    medium_split = r'\{</w:t></w:r><w:r[^>]*><w:t[^>]*>\{([a-zA-Z._]+)\}\}'
    result = re.sub(medium_split, r'{{\1}}', result)
    
    # Find and replace all clean placeholders
    clean_pattern = r'\{\{([a-zA-Z][a-zA-Z0-9._]*)\}\}'
    
    def replace_match(match):
        placeholder = match.group(1)
        
        # Try exact match
        value = context.get(placeholder, "")
        
        # Try with dots replaced by underscores
        if not value:
            underscore_key = placeholder.replace(".", "_")
            value = context.get(underscore_key, "")
        
        # Try nested lookup
        if not value and "." in placeholder:
            parts = placeholder.split(".")
            nested = context
            try:
                for part in parts:
                    if isinstance(nested, dict):
                        nested = nested.get(part, nested.get(part.replace("_", ""), ""))
                    else:
                        nested = ""
                        break
                if nested and not isinstance(nested, dict):
                    value = str(nested)
            except:
                pass
        
        if value:
            filled.append(placeholder)
            # Escape XML special chars
            value = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            return value
        else:
            missing.append(placeholder)
            return f"[{placeholder}]"
    
    result = re.sub(clean_pattern, replace_match, result)
    
    return result, list(set(filled)), list(set(missing))


def fill_docx_template(
    template_path: Path,
    output_path: Path,
    context: Dict[str, Any]
) -> Tuple[bool, List[str], List[str]]:
    """
    Fill a DOCX template with context data.
    """
    all_filled = []
    all_missing = []
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract DOCX
            with ZipFile(template_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            # Process document.xml
            document_xml_path = temp_path / "word" / "document.xml"
            if document_xml_path.exists():
                with open(document_xml_path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                modified_xml, filled, missing = replace_placeholders_in_xml(xml_content, context)
                all_filled.extend(filled)
                all_missing.extend(missing)
                
                with open(document_xml_path, 'w', encoding='utf-8') as f:
                    f.write(modified_xml)
            
            # Process header/footer files
            word_dir = temp_path / "word"
            for xml_file in list(word_dir.glob("header*.xml")) + list(word_dir.glob("footer*.xml")):
                with open(xml_file, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                modified_xml, filled, missing = replace_placeholders_in_xml(xml_content, context)
                all_filled.extend(filled)
                all_missing.extend(missing)
                
                with open(xml_file, 'w', encoding='utf-8') as f:
                    f.write(modified_xml)
            
            # Repack the DOCX
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with ZipFile(output_path, 'w', ZIP_DEFLATED) as zip_out:
                for file_path in temp_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_path)
                        zip_out.write(file_path, arcname)
            
            return True, list(set(all_filled)), list(set(all_missing))
    
    except Exception as e:
        return False, [], [str(e)]


def convert_to_pdf(docx_path: Path, pdf_path: Path) -> Tuple[bool, str]:
    """Convert DOCX to PDF using LibreOffice."""
    try:
        # Try soffice (LibreOffice)
        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            str(docx_path),
            "--outdir", str(pdf_path.parent)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # LibreOffice names output based on input filename
        expected_pdf = pdf_path.parent / (docx_path.stem + ".pdf")
        if expected_pdf.exists() and expected_pdf != pdf_path:
            shutil.move(expected_pdf, pdf_path)
        
        if pdf_path.exists():
            return True, ""
        else:
            return False, f"PDF conversion failed: {result.stderr}"
    
    except FileNotFoundError:
        return False, "LibreOffice not found. Install with: brew install --cask libreoffice"
    except subprocess.TimeoutExpired:
        return False, "PDF conversion timed out"
    except Exception as e:
        return False, str(e)


# ============================================================
# Main Entry Points
# ============================================================

def generate_document(
    project_name: str,
    template_id: int,
    context_id: int = None,
    output_path: str = None,
    include_pdf: bool = True,
    body_text: str = None,
    injuries_list: List[str] = None
) -> Dict[str, Any]:
    """
    Generate a document from a template.
    
    Args:
        project_name: Project/case name (e.g., "John-Doe-MVA-01-01-2025")
        template_id: Template ID from registry
        context_id: ID of the entity to use (insurance ID, provider ID, etc.)
        output_path: Custom output path (auto-generated if not specified)
        include_pdf: Whether to also generate PDF version
        body_text: Custom body text for blank letter templates
        injuries_list: List of injuries for lien letters
    
    Returns:
        Dict with status, paths, placeholders filled/missing, and errors
    """
    result = {
        "status": "error",
        "docx_path": None,
        "pdf_path": None,
        "placeholders_filled": [],
        "placeholders_missing": [],
        "errors": [],
        "warnings": []
    }
    
    try:
        # Load registry
        registry = load_template_registry()
        
        # Get template
        template = get_template_by_id(template_id, registry)
        if not template:
            result["errors"].append(f"Template ID {template_id} not found")
            return result
        
        # Check template file exists
        template_file = template.get("file", "")
        template_path = TEMPLATES_DIR / template_file
        if not template_path.exists():
            result["errors"].append(f"Template file not found: {template_path}")
            return result
        
        # Only DOCX templates can be filled programmatically
        if template.get("type") != "docx":
            result["errors"].append(f"Template type '{template.get('type')}' not supported for automatic filling. Use fillable PDF tool instead.")
            return result
        
        # Get project path
        project_path = get_project_path(project_name)
        if not project_path.exists():
            result["errors"].append(f"Project folder not found: {project_path}")
            return result
        
        # Resolve entity if context_id provided
        entity = None
        context_type = template.get("context_type", "client")
        
        if context_type != "client" and context_id:
            entity = get_entity_by_id(project_name, project_path, context_type, context_id)
            if not entity:
                result["errors"].append(f"Entity with ID {context_id} not found in {context_type}")
                return result
        
        # Build context
        context = build_context(project_name, project_path, template, entity, registry)
        
        # Add special inputs
        if body_text:
            context["body_text"] = body_text
        if injuries_list:
            context["injuries_list"] = "\n".join(f"• {inj}" for inj in injuries_list)
        
        # Determine output path
        if not output_path:
            today = datetime.now().strftime("%Y-%m-%d")
            client_name = context.get("client.name", "Client")
            last_name = client_name.split()[-1] if client_name else "Client"
            template_name = template.get("name", f"Template_{template_id}")
            
            # Build descriptive filename
            if entity:
                if context_type == "insurance":
                    entity_desc = entity.get("insurance_company_name", "")[:15]
                elif context_type == "medical_provider":
                    entity_desc = entity.get("provider_full_name", "")[:15]
                elif context_type == "lien":
                    entity_desc = entity.get("lien_holder_name", "")[:15]
                else:
                    entity_desc = ""
                filename = f"{today} - {last_name} - {template_name} - {entity_desc}.docx"
            else:
                filename = f"{today} - {last_name} - {template_name}.docx"
            
            # Clean filename
            filename = re.sub(r'[<>:"/\\|?*]', '', filename)
            
            # Determine output folder based on category
            category = template.get("category", "")
            if category == "insurance":
                output_folder = "Insurance"
            elif category == "medical":
                output_folder = "Medical Providers"
            elif category == "liens":
                output_folder = "Liens"
            elif category == "litigation":
                output_folder = "Litigation"
            else:
                output_folder = "Client"
            
            output_path = str(project_path / output_folder / filename)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Fill the template
        success, filled, missing = fill_docx_template(template_path, output_path, context)
        
        if not success:
            result["errors"].append("Failed to fill template")
            result["placeholders_missing"] = missing
            return result
        
        result["docx_path"] = str(output_path)
        result["placeholders_filled"] = filled
        result["placeholders_missing"] = missing
        
        if missing:
            result["warnings"].append(f"Some placeholders could not be filled: {missing}")
        
        # Convert to PDF
        if include_pdf:
            pdf_path = output_path.with_suffix(".pdf")
            pdf_success, pdf_error = convert_to_pdf(output_path, pdf_path)
            
            if pdf_success:
                result["pdf_path"] = str(pdf_path)
            else:
                result["warnings"].append(f"PDF conversion failed: {pdf_error}")
        
        result["status"] = "success"
        return result
    
    except Exception as e:
        result["errors"].append(str(e))
        import traceback
        result["errors"].append(traceback.format_exc())
        return result


def list_templates(category: str = None, context_type: str = None) -> List[Dict]:
    """List all available templates, optionally filtered."""
    registry = load_template_registry()
    templates = []
    
    for template in registry.get("templates", []):
        # Apply filters
        if category and template.get("category") != category:
            continue
        if context_type and template.get("context_type") != context_type:
            continue
        
        templates.append({
            "id": template.get("id"),
            "name": template.get("name"),
            "description": template.get("description"),
            "type": template.get("type"),
            "category": template.get("category"),
            "context_type": template.get("context_type"),
            "file": template.get("file")
        })
    
    return templates


def show_available_entities(project_name: str) -> Dict:
    """Show available entities (insurance, providers, liens) for a project."""
    project_path = get_project_path(project_name)
    
    result = {
        "project_name": project_name,
        "project_path": str(project_path),
        "insurance": [],
        "medical_providers": [],
        "liens": [],
        "contacts": []
    }
    
    # Load from project's Case Information folder
    insurance_data = load_case_json(project_path, "insurance.json")
    if isinstance(insurance_data, dict):
        for key, value in insurance_data.items():
            if isinstance(value, dict) and value.get("id"):
                result["insurance"].append({
                    "id": value.get("id"),
                    "company": value.get("insurance_company_name", ""),
                    "type": value.get("insurance_type", ""),
                    "adjuster": value.get("insurance_adjuster_name", "")
                })
    
    providers_data = load_case_json(project_path, "medical_providers.json")
    if isinstance(providers_data, dict):
        for key, value in providers_data.items():
            if isinstance(value, dict) and value.get("id"):
                result["medical_providers"].append({
                    "id": value.get("id"),
                    "name": value.get("provider_full_name", "")
                })
    
    liens_data = load_case_json(project_path, "liens.json")
    if isinstance(liens_data, dict):
        for key, value in liens_data.items():
            if isinstance(value, dict) and value.get("id"):
                result["liens"].append({
                    "id": value.get("id"),
                    "holder": value.get("lien_holder_name", "")
                })
    
    contacts_data = load_case_json(project_path, "contacts.json")
    if isinstance(contacts_data, dict):
        for key, value in contacts_data.items():
            if isinstance(value, dict) and value.get("contact_id"):
                result["contacts"].append({
                    "id": value.get("contact_id"),
                    "name": value.get("full_name", "")
                })
    
    return result


# ============================================================
# CLI Interface
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Unified Template Generation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a BI Letter of Rep (template ID 1) for insurance ID 42
  python generate_template.py --project "John-Doe-MVA-01-01-2025" --template-id 1 --context-id 42
  
  # List all templates
  python generate_template.py --list
  
  # List templates by category
  python generate_template.py --list --category insurance
  
  # Show available entities for a project
  python generate_template.py --project "John-Doe-MVA-01-01-2025" --show-entities
  
  # Interactive mode
  python generate_template.py --project "John-Doe-MVA-01-01-2025" --template-id 1 --interactive
        """
    )
    
    parser.add_argument("--project", "-p", help="Project/case name")
    parser.add_argument("--template-id", "-t", type=int, help="Template ID from registry")
    parser.add_argument("--context-id", "-c", type=int, help="Entity ID (insurance, provider, lien, etc.)")
    parser.add_argument("--output", "-o", help="Custom output path")
    parser.add_argument("--no-pdf", action="store_true", help="Don't generate PDF version")
    parser.add_argument("--body", "-b", help="Custom body text for blank letter templates")
    parser.add_argument("--injuries", help="Comma-separated list of injuries for lien letters")
    parser.add_argument("--list", "-l", action="store_true", help="List available templates")
    parser.add_argument("--category", help="Filter templates by category")
    parser.add_argument("--context-type", help="Filter templates by context type")
    parser.add_argument("--show-entities", action="store_true", help="Show available entities for project")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    
    args = parser.parse_args()
    
    # Handle --list
    if args.list:
        templates = list_templates(category=args.category, context_type=args.context_type)
        print(json.dumps(templates, indent=2 if args.pretty else None))
        return 0
    
    # Handle --show-entities
    if args.show_entities:
        if not args.project:
            print("Error: --project required with --show-entities", file=sys.stderr)
            return 1
        entities = show_available_entities(args.project)
        print(json.dumps(entities, indent=2 if args.pretty else None))
        return 0
    
    # Handle document generation
    if not args.project or args.template_id is None:
        parser.print_help()
        return 1
    
    # Interactive mode
    if args.interactive:
        registry = load_template_registry()
        template = get_template_by_id(args.template_id, registry)
        
        if not template:
            print(f"Error: Template ID {args.template_id} not found", file=sys.stderr)
            return 1
        
        context_type = template.get("context_type", "client")
        
        if context_type != "client" and not args.context_id:
            # Show available entities and prompt
            entities = show_available_entities(args.project)
            
            if context_type == "insurance":
                print("\nAvailable insurance entities:")
                for e in entities.get("insurance", []):
                    print(f"  ID {e['id']}: {e['company']} ({e['type']}) - {e['adjuster']}")
            elif context_type == "medical_provider":
                print("\nAvailable medical providers:")
                for e in entities.get("medical_providers", []):
                    print(f"  ID {e['id']}: {e['name']}")
            elif context_type == "lien":
                print("\nAvailable liens:")
                for e in entities.get("liens", []):
                    print(f"  ID {e['id']}: {e['holder']}")
            
            try:
                context_id_input = input(f"\nEnter {context_type} ID: ").strip()
                args.context_id = int(context_id_input)
            except (ValueError, EOFError):
                print("Error: Invalid ID", file=sys.stderr)
                return 1
    
    # Parse injuries
    injuries_list = None
    if args.injuries:
        injuries_list = [i.strip() for i in args.injuries.split(",")]
    
    # Generate document
    result = generate_document(
        project_name=args.project,
        template_id=args.template_id,
        context_id=args.context_id,
        output_path=args.output,
        include_pdf=not args.no_pdf,
        body_text=args.body,
        injuries_list=injuries_list
    )
    
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())

