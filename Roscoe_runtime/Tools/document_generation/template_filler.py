#!/usr/bin/env python3
"""
Template Filler Tool

Fills DOCX templates with case data by resolving placeholders from JSON databases.
Supports automatic context detection for insurance, liens, and medical providers.

Usage:
    # Fill LOR to PIP adjuster (auto-detects if only one PIP policy)
    python template_filler.py --case "Smith-MVA-01-15-2024" --template lor_pip
    
    # Fill with specific insurance type
    python template_filler.py --case "Smith-MVA-01-15-2024" --template lor_bi --insurance-type bi
    
    # Fill lien request for specific holder
    python template_filler.py --case "Smith-MVA-01-15-2024" --template initial_lien_request \
        --lien-holder "Humana" --injuries "cervical strain,lumbar sprain"
    
    # List available templates
    python template_filler.py --list-templates
    
    # Show context options for a case
    python template_filler.py --case "Smith-MVA-01-15-2024" --show-context
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import tempfile

# Import sibling module
from context_resolver import ContextResolver


# Default paths
WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", os.environ.get("ROSCOE_ROOT", str(Path(__file__).resolve().parents[2]))))
TOOLS_DIR = WORKSPACE_ROOT / "Tools" / "document_generation"
TEMPLATES_DIR = WORKSPACE_ROOT / "forms" / "templates"
PROJECTS_DIR = WORKSPACE_ROOT / "projects"


def load_template_registry() -> Dict:
    """Load the template registry configuration."""
    registry_path = TOOLS_DIR / "template_registry.json"
    with open(registry_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_placeholder_mapping() -> Dict:
    """Load the placeholder mapping configuration."""
    mapping_path = TOOLS_DIR / "placeholder_mapping.json"
    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_template_by_id(template_id: str, registry: Dict) -> Optional[Dict]:
    """Get a template definition by its ID."""
    for template in registry.get("templates", []):
        if template.get("id") == template_id:
            return template
    return None


def format_date(date_str: str, format_type: str = "date_long") -> str:
    """
    Format a date string.
    
    Args:
        date_str: Date string in various formats
        format_type: "date_long" or "date_short"
    
    Returns:
        Formatted date string
    """
    if not date_str:
        return ""
    
    # Try to parse the date
    date_formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
    ]
    
    parsed_date = None
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(str(date_str), fmt)
            break
        except ValueError:
            continue
    
    if not parsed_date:
        # Return as-is if we can't parse it
        return str(date_str)
    
    # Format according to type
    if format_type == "date_long":
        return parsed_date.strftime("%B %d, %Y")
    elif format_type == "date_short":
        return parsed_date.strftime("%m/%d/%Y")
    else:
        return str(date_str)


def resolve_placeholder_value(
    placeholder: str,
    context: Dict[str, Any],
    registry: Dict,
    mapping: Dict
) -> Tuple[str, bool]:
    """
    Resolve a placeholder to its value.
    
    Args:
        placeholder: The placeholder name (without braces)
        context: The resolved context data
        registry: Template registry config
        mapping: Placeholder mapping config
    
    Returns:
        Tuple of (resolved_value, was_found)
    """
    # First, check if placeholder exists directly in context
    if placeholder in context:
        value = context[placeholder]
        if value:
            return str(value), True
    
    # Check with dot-to-underscore conversion
    underscore_key = placeholder.replace(".", "_")
    if underscore_key in context:
        value = context[underscore_key]
        if value:
            return str(value), True
    
    # Check nested context (e.g., insurance.claimNumber -> context['insurance']['claimNumber'])
    if "." in placeholder:
        parts = placeholder.split(".")
        value = context
        try:
            for part in parts:
                if isinstance(value, dict):
                    # Try exact key first
                    if part in value:
                        value = value[part]
                    # Try underscore version
                    elif part.replace(".", "_") in value:
                        value = value[part.replace(".", "_")]
                    else:
                        value = None
                        break
                else:
                    value = None
                    break
            if value and not isinstance(value, dict):
                return str(value), True
        except:
            pass
    
    mapping_def = mapping.get("mappings", {}).get(placeholder)
    
    if not mapping_def:
        # Unknown placeholder
        return f"[UNKNOWN: {placeholder}]", False
    
    mapping_type = mapping_def.get("type", "")
    
    # Handle computed values
    if mapping_type == "computed":
        format_type = mapping_def.get("format", "")
        transform = mapping_def.get("transform", "")
        
        if format_type == "date_long":
            return datetime.now().strftime("%B %d, %Y"), True
        elif format_type == "date_short":
            return datetime.now().strftime("%m/%d/%Y"), True
        
        # Handle transforms on database fields
        if transform and mapping_def.get("source"):
            source = mapping_def["source"]
            field = mapping_def.get("field", "")
            value = context.get(field, "") or context.get(f"{source}_{field}", "")
            
            if transform == "first_name" and value:
                return value.split()[0] if " " in value else value, True
            elif transform == "incident_type":
                project_name = context.get("project_name", "")
                if "MVA" in project_name:
                    return "motor vehicle collision", True
                elif "S&F" in project_name:
                    return "slip and fall incident", True
                elif "WC" in project_name:
                    return "workplace injury", True
                return "incident", True
    
    # Handle static values
    elif mapping_type == "static":
        path = mapping_def.get("path", "")
        static_config = registry.get("static_config", {})
        
        # Navigate the path
        parts = path.replace("static_config.", "").split(".")
        value = static_config
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, "")
            else:
                value = ""
                break
        
        return str(value), bool(value)
    
    # Handle database values
    elif mapping_type == "database":
        source = mapping_def.get("source", "")
        field = mapping_def.get("field", "")
        format_type = mapping_def.get("format", "")
        
        # Map source to context key
        source_map = {
            "case_overview": "",  # Base context
            "clients": "",
            "litigation": "",
        }
        
        # Try to find the value
        value = context.get(field, "")
        if not value:
            # Try with underscore variations
            alt_field = field.replace("_", "")
            value = context.get(alt_field, "")
        if not value:
            # Try camelCase
            camel_field = "".join(w.title() if i > 0 else w for i, w in enumerate(field.split("_")))
            value = context.get(camel_field, "")
        
        # Apply format
        if value and format_type:
            if "date" in format_type:
                value = format_date(str(value), format_type)
            elif format_type == "ssn_masked":
                if len(str(value)) >= 4:
                    value = f"XXX-XX-{str(value)[-4:]}"
        
        return str(value), bool(value)
    
    # Handle context values (insurance, lien, provider)
    elif mapping_type in ("context", "context_lookup", "context_directory_lookup"):
        source = mapping_def.get("source", "")
        field = mapping_def.get("field", "")
        context_key = mapping_def.get("context_key", "")
        format_type = mapping_def.get("format", "")
        
        # Get from context sub-dictionary
        sub_context = context.get(source, {})
        if isinstance(sub_context, dict):
            value = sub_context.get(field, "")
            
            # For directory lookups, we need the address_block or formatted version
            if mapping_type == "context_directory_lookup":
                lookup_field = mapping_def.get("lookup_field", "")
                if field == "address":
                    value = sub_context.get(f"{lookup_field.replace('_name', '')}_address_block", value)
                elif field == "phone":
                    value = sub_context.get(f"{lookup_field.replace('_name', '')}_phone", value)
                elif field == "email":
                    value = sub_context.get(f"{lookup_field.replace('_name', '')}_email", value)
            
            # Apply format
            if value and format_type and "date" in format_type:
                value = format_date(str(value), format_type)
            
            return str(value), bool(value)
    
    # Handle agent input placeholders
    elif mapping_type == "agent_input":
        # These should be provided via overrides
        return f"[INPUT REQUIRED: {placeholder}]", False
    
    return f"[MISSING: {placeholder}]", False


def replace_placeholders_in_xml(
    xml_content: str,
    context: Dict[str, Any],
    registry: Dict,
    mapping: Dict
) -> Tuple[str, List[str], List[str]]:
    """
    Replace all {{placeholder}} patterns in XML content.
    
    Handles cases where Word splits placeholders across multiple XML elements,
    e.g., {</w:t><w:t>{incidentDate}}</w:t> instead of {{incidentDate}}
    
    Args:
        xml_content: The XML content from document.xml
        context: Resolved context data
        registry: Template registry
        mapping: Placeholder mapping
    
    Returns:
        Tuple of (modified_xml, filled_placeholders, missing_placeholders)
    """
    filled = []
    missing = []
    result = xml_content
    
    # Step 1: Fix split placeholders where Word has put braces in separate elements
    # Pattern: {</w:t>...<w:t>{placeholder}} needs to become {{placeholder}}
    # The regex captures: lone { in one element, followed by {placeholder}} in next element
    
    # Handle: {</w:t></w:r><w:r ...><w:t>{placeholder}}
    # This pattern handles cases where Word may have additional XML between the braces
    complex_split = r'\{</w:t></w:r>(<w:r[^>]*><w:rPr>.*?</w:rPr>)?<w:t[^>]*>\{([a-zA-Z._]+)\}\}'
    result = re.sub(complex_split, r'{{\2}}', result, flags=re.DOTALL)
    
    # Handle simpler: {</w:t><w:t>{placeholder}}
    simple_split = r'\{</w:t><w:t[^>]*>\{([a-zA-Z._]+)\}\}'
    result = re.sub(simple_split, r'{{\1}}', result)
    
    # Handle: {</w:t></w:r><w:r><w:t>{placeholder}}
    medium_split = r'\{</w:t></w:r><w:r[^>]*><w:t[^>]*>\{([a-zA-Z._]+)\}\}'
    result = re.sub(medium_split, r'{{\1}}', result)
    
    # Step 2: Find and replace all clean placeholders
    clean_pattern = r'\{\{([a-zA-Z][a-zA-Z0-9._]*)\}\}'
    
    def replace_match(match):
        placeholder = match.group(1)
        value, found = resolve_placeholder_value(placeholder, context, registry, mapping)
        
        if found:
            filled.append(placeholder)
        else:
            missing.append(placeholder)
        
        # Escape XML special chars
        value = value.replace("&", "&amp;")
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")
        
        return value
    
    result = re.sub(clean_pattern, replace_match, result)
    
    # Step 3: Clean up any orphaned braces that might remain
    # Remove lone { that's immediately followed by </w:t> (orphan opening brace)
    result = re.sub(r'(?<![{])\{(?!</w:t>)(?=[^{]</w:t>)', '', result)
    
    return result, list(set(filled)), list(set(missing))


def fill_docx_template(
    template_path: Path,
    output_path: Path,
    context: Dict[str, Any],
    registry: Dict,
    mapping: Dict
) -> Tuple[bool, List[str], List[str]]:
    """
    Fill a DOCX template with resolved context data.
    
    Args:
        template_path: Path to the template DOCX
        output_path: Path for the output DOCX
        context: Resolved context data
        registry: Template registry
        mapping: Placeholder mapping
    
    Returns:
        Tuple of (success, filled_placeholders, missing_placeholders)
    """
    all_filled = []
    all_missing = []
    
    try:
        # Create temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract DOCX (it's a ZIP file)
            with ZipFile(template_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            
            # Process document.xml (main content)
            document_xml_path = temp_path / "word" / "document.xml"
            if document_xml_path.exists():
                with open(document_xml_path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                modified_xml, filled, missing = replace_placeholders_in_xml(
                    xml_content, context, registry, mapping
                )
                all_filled.extend(filled)
                all_missing.extend(missing)
                
                with open(document_xml_path, 'w', encoding='utf-8') as f:
                    f.write(modified_xml)
            
            # Also process header files if they exist
            word_dir = temp_path / "word"
            for header_file in word_dir.glob("header*.xml"):
                with open(header_file, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                modified_xml, filled, missing = replace_placeholders_in_xml(
                    xml_content, context, registry, mapping
                )
                all_filled.extend(filled)
                all_missing.extend(missing)
                
                with open(header_file, 'w', encoding='utf-8') as f:
                    f.write(modified_xml)
            
            # Process footer files if they exist
            for footer_file in word_dir.glob("footer*.xml"):
                with open(footer_file, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                modified_xml, filled, missing = replace_placeholders_in_xml(
                    xml_content, context, registry, mapping
                )
                all_filled.extend(filled)
                all_missing.extend(missing)
                
                with open(footer_file, 'w', encoding='utf-8') as f:
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
        print(f"Error filling template: {e}", file=sys.stderr)
        return False, [], [str(e)]


def convert_to_pdf(docx_path: Path, pdf_path: Path) -> Tuple[bool, str]:
    """
    Convert DOCX to PDF using LibreOffice.
    
    Args:
        docx_path: Path to input DOCX
        pdf_path: Path for output PDF
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            str(docx_path),
            "--outdir", str(pdf_path.parent)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # LibreOffice names the output based on input filename
        expected_pdf = pdf_path.parent / (docx_path.stem + ".pdf")
        if expected_pdf.exists() and expected_pdf != pdf_path:
            shutil.move(expected_pdf, pdf_path)
        
        if pdf_path.exists():
            return True, ""
        else:
            return False, f"PDF conversion failed: {result.stderr}"
    
    except FileNotFoundError:
        return False, "LibreOffice not found. Install with: brew install --cask libreoffice"
    except Exception as e:
        return False, str(e)


def fill_template(
    case_name: str,
    template_id: str,
    insurance_type: str = None,
    lien_holder: str = None,
    provider_name: str = None,
    body_text: str = None,
    injuries_list: List[str] = None,
    output_path: str = None,
    include_pdf: bool = True,
    **overrides
) -> Dict[str, Any]:
    """
    Fill a DOCX template with case data.
    
    This is the main entry point for the template filling system.
    
    Args:
        case_name: Project/case name (e.g., "Smith-MVA-01-15-2024")
        template_id: Template ID from registry (e.g., "lor_pip")
        insurance_type: Insurance type if template requires it ("pip", "bi", "um")
        lien_holder: Lien holder name if template requires it
        provider_name: Medical provider name if template requires it
        body_text: Custom body text for blank letter templates
        injuries_list: List of injuries for lien letters
        output_path: Custom output path (auto-generated if not specified)
        include_pdf: Whether to also generate PDF version
        **overrides: Direct placeholder value overrides
    
    Returns:
        Dict with status, paths, filled/missing placeholders, and errors
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
        # Load configurations
        registry = load_template_registry()
        mapping = load_placeholder_mapping()
        
        # Get template definition
        template = get_template_by_id(template_id, registry)
        if not template:
            result["errors"].append(f"Template '{template_id}' not found in registry")
            return result
        
        # Build template path
        template_file = template.get("file", "")
        template_path = TEMPLATES_DIR / template_file
        if not template_path.exists():
            result["errors"].append(f"Template file not found: {template_path}")
            return result
        
        # Initialize context resolver
        resolver = ContextResolver(case_name, WORKSPACE_ROOT)
        
        # Resolve full context
        required_context = template.get("required_context", [])
        context, context_errors = resolver.resolve_full_context(
            required_context,
            insurance_type=insurance_type,
            lien_holder=lien_holder,
            provider_name=provider_name
        )
        
        if context_errors:
            result["errors"].extend(context_errors)
            return result
        
        # Add any overrides to context
        for key, value in overrides.items():
            context[key] = value
        
        # Add special inputs
        if body_text:
            context["body_text"] = body_text
        if injuries_list:
            # Format injuries as bullet list
            injuries_formatted = "\n".join(f"• {inj}" for inj in injuries_list)
            context["injuries_list"] = injuries_formatted
        
        # Determine output path
        if not output_path:
            today = datetime.now().strftime("%Y-%m-%d")
            client_name = context.get("client_name", "Client")
            last_name = client_name.split()[-1] if client_name else "Client"
            
            # Get output folder from template or default
            output_folder = template.get("output_folder", "Letters")
            
            # Build descriptive filename
            template_name = template.get("name", template_id)
            # Get relevant context for filename
            if insurance_type or "insurance" in template.get("category", ""):
                ins_ctx = context.get("insurance", {})
                company = ins_ctx.get("insurance_company_name", "")
                if company:
                    company_short = company.split()[0][:15]
                    filename = f"{today} - {last_name} - {template_name} - {company_short}.docx"
                else:
                    filename = f"{today} - {last_name} - {template_name}.docx"
            elif lien_holder or "liens" in template.get("category", ""):
                lien_ctx = context.get("lien", {})
                holder = lien_ctx.get("lien_holder_name", lien_holder or "")
                holder_short = holder[:15] if holder else ""
                filename = f"{today} - {last_name} - {template_name} - {holder_short}.docx"
            elif provider_name or "medical" in template.get("category", ""):
                provider_ctx = context.get("medical_provider", {})
                provider = provider_ctx.get("provider_name", provider_name or "")
                provider_short = provider[:15] if provider else ""
                filename = f"{today} - {last_name} - {template_name} - {provider_short}.docx"
            else:
                filename = f"{today} - {last_name} - {template_name}.docx"
            
            # Clean filename
            filename = re.sub(r'[<>:"/\\|?*]', '', filename)
            
            output_dir = PROJECTS_DIR / case_name / output_folder
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(output_dir / filename)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Fill the template
        success, filled, missing = fill_docx_template(
            template_path,
            output_path,
            context,
            registry,
            mapping
        )
        
        if not success:
            result["errors"].append("Failed to fill template")
            result["placeholders_missing"] = missing
            return result
        
        result["docx_path"] = str(output_path)
        result["placeholders_filled"] = filled
        result["placeholders_missing"] = missing
        
        if missing:
            result["warnings"].append(f"Some placeholders could not be filled: {missing}")
        
        # Convert to PDF if requested
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
        return result


def list_templates() -> List[Dict]:
    """List all available templates."""
    registry = load_template_registry()
    templates = []
    
    for template in registry.get("templates", []):
        templates.append({
            "id": template.get("id"),
            "name": template.get("name"),
            "category": template.get("category"),
            "description": template.get("description"),
            "required_context": template.get("required_context", []),
            "agent_input": template.get("agent_input", [])
        })
    
    return templates


def show_case_context(case_name: str) -> Dict:
    """Show available context options for a case."""
    resolver = ContextResolver(case_name, WORKSPACE_ROOT)
    
    return {
        "case_name": case_name,
        "base_data": resolver.get_case_base_data(),
        "insurance_types": resolver.get_available_insurance_types(),
        "lien_holders": resolver.get_available_lien_holders(),
        "medical_providers": resolver.get_available_medical_providers()
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fill DOCX templates with case data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fill LOR to PIP adjuster
  python template_filler.py --case "Smith-MVA-01-15-2024" --template lor_pip
  
  # Fill LOR to BI adjuster
  python template_filler.py --case "Smith-MVA-01-15-2024" --template lor_bi --insurance-type bi
  
  # Fill initial lien request
  python template_filler.py --case "Smith-MVA-01-15-2024" --template initial_lien_request \\
      --lien-holder "Humana" --injuries "cervical strain,lumbar sprain"
  
  # List available templates
  python template_filler.py --list-templates
  
  # Show context options for case
  python template_filler.py --case "Smith-MVA-01-15-2024" --show-context
        """
    )
    
    parser.add_argument("--case", "-c", help="Case/project name")
    parser.add_argument("--template", "-t", help="Template ID to fill")
    parser.add_argument("--insurance-type", "-i", choices=["pip", "bi", "um"],
                        help="Insurance type for insurance templates")
    parser.add_argument("--lien-holder", "-l", help="Lien holder name for lien templates")
    parser.add_argument("--provider", "-p", help="Medical provider name for medical templates")
    parser.add_argument("--body", "-b", help="Custom body text for blank letter templates")
    parser.add_argument("--injuries", help="Comma-separated list of injuries for lien letters")
    parser.add_argument("--output", "-o", help="Custom output path")
    parser.add_argument("--no-pdf", action="store_true", help="Don't generate PDF version")
    parser.add_argument("--list-templates", action="store_true", help="List available templates")
    parser.add_argument("--show-context", action="store_true", help="Show context options for case")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    
    args = parser.parse_args()
    
    # Handle list-templates
    if args.list_templates:
        templates = list_templates()
        print(json.dumps(templates, indent=2 if args.pretty else None))
        return 0
    
    # Handle show-context
    if args.show_context:
        if not args.case:
            print("Error: --case required with --show-context", file=sys.stderr)
            return 1
        context = show_case_context(args.case)
        print(json.dumps(context, indent=2 if args.pretty else None, default=str))
        return 0
    
    # Handle template filling
    if not args.case or not args.template:
        parser.print_help()
        return 1
    
    injuries_list = None
    if args.injuries:
        injuries_list = [i.strip() for i in args.injuries.split(",")]
    
    result = fill_template(
        case_name=args.case,
        template_id=args.template,
        insurance_type=args.insurance_type,
        lien_holder=args.lien_holder,
        provider_name=args.provider,
        body_text=args.body,
        injuries_list=injuries_list,
        output_path=args.output,
        include_pdf=not args.no_pdf
    )
    
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())

