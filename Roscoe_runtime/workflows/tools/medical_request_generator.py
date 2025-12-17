#!/usr/bin/env python3
"""
Medical Request Generator Tool

Generates medical records/bills requests using client's signed HIPAA authorization.
Can create:
- Just the HIPAA with provider info filled in
- HIPAA + Medical Records Request letter
- HIPAA + Medical Bills Request letter  
- All three combined (Records Request + Bills Request + HIPAA)

Usage:
    # Generate HIPAA only with provider filled in
    python medical_request_generator.py \
        --case "Smith-MVA-01-15-2024" \
        --provider "Baptist Health Louisville" \
        --hipaa-only \
        --output /path/to/output.pdf
    
    # Generate all three (records request + bills request + HIPAA)
    python medical_request_generator.py \
        --case "Smith-MVA-01-15-2024" \
        --provider "Baptist Health Louisville" \
        --records-request \
        --bills-request \
        --output /path/to/output.pdf
    
    # Generate records request + HIPAA only
    python medical_request_generator.py \
        --case "Smith-MVA-01-15-2024" \
        --provider "Baptist Health Louisville" \
        --records-request \
        --output /path/to/output.pdf
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from io import BytesIO

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Default paths (can be overridden)
ROSCOE_ROOT = Path(os.environ.get("ROSCOE_ROOT", Path(__file__).resolve().parents[2]))
WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", str(ROSCOE_ROOT)))
TEMPLATES_DIR = Path(os.environ.get("ROSCOE_FORMS_TEMPLATES_DIR", str(ROSCOE_ROOT / "workflows" / "templates" / "medical")))
DATABASE_DIR = Path(os.environ.get("ROSCOE_DATABASE_DIR", str(ROSCOE_ROOT / "Database")))
PROJECTS_DIR = Path(os.environ.get("ROSCOE_PROJECTS_DIR", str(ROSCOE_ROOT)))

# Template files
HIPAA_TEMPLATE = Path(os.environ.get(\"ROSCOE_HIPAA_TEMPLATE\", str(ROSCOE_ROOT / \"workflows\" / \"phase_0_onboarding\" / \"workflows\" / \"document_collection\" / \"templates\" / \"intake_forms\" / \"2021 Whaley Medical Authorization (HIPAA) (1).pdf\")))
RECORDS_REQUEST_TEMPLATE = TEMPLATES_DIR / "2023 Whaley Law Firm Medical Request Template (1).pdf"
BILLS_REQUEST_TEMPLATE = TEMPLATES_DIR / "2023 Whaley Initial Medical Billing Request to Provider (MBR) (1).pdf"


def load_case_data(case_name: str) -> Dict[str, Any]:
    """Load case data from database JSON files."""
    case_data = {
        "client_name": "",
        "dob": "",
        "ssn": "",
        "date_of_loss": "",
        "project_name": case_name
    }
    
    # Try to load from case_overview.json
    overview_path = DATABASE_DIR / "case_overview.json"
    if overview_path.exists():
        with open(overview_path) as f:
            overviews = json.load(f)
        
        for record in overviews:
            if record.get("project_name") == case_name:
                case_data["client_name"] = record.get("client_name", "")
                case_data["dob"] = record.get("dob", record.get("date_of_birth", ""))
                case_data["ssn"] = record.get("ssn", record.get("social_security", ""))
                case_data["date_of_loss"] = record.get("accident_date", record.get("date_of_loss", ""))
                break
    
    return case_data


def load_provider_data(case_name: str, provider_name: str) -> Dict[str, Any]:
    """Load provider data from medical_providers.json."""
    provider_data = {
        "name": provider_name,
        "address_line1": "",
        "address_line2": "",
        "city": "",
        "state": "KY",
        "zip": "",
        "fax": "",
        "phone": "",
        "attention": ""
    }
    
    providers_path = DATABASE_DIR / "medical_providers.json"
    if providers_path.exists():
        with open(providers_path) as f:
            providers = json.load(f)
        
        # Find matching provider for this case
        for record in providers:
            if record.get("project_name") == case_name:
                full_name = record.get("provider_full_name", "")
                if provider_name.lower() in full_name.lower() or full_name.lower() in provider_name.lower():
                    provider_data["name"] = full_name
                    provider_data["address_line1"] = record.get("address", record.get("address_line1", ""))
                    provider_data["city"] = record.get("city", "")
                    provider_data["state"] = record.get("state", "KY")
                    provider_data["zip"] = record.get("zip", record.get("postal_code", ""))
                    provider_data["fax"] = record.get("fax", record.get("fax_number", ""))
                    provider_data["phone"] = record.get("phone", record.get("phone_number", ""))
                    break
    
    return provider_data


def find_signed_hipaa(case_name: str) -> Optional[Path]:
    """Find the client's signed HIPAA authorization in the case folder."""
    case_dir = PROJECTS_DIR / case_name
    
    if not case_dir.exists():
        return None
    
    # Common locations for signed HIPAA
    search_paths = [
        case_dir / "Client",
        case_dir / "Client" / "Authorizations",
        case_dir / "Case Information",
        case_dir / "Case_Information",
        case_dir
    ]
    
    hipaa_patterns = ["*HIPAA*signed*", "*hipaa*signed*", "*HIPAA*.pdf", "*Medical*Auth*.pdf"]
    
    for search_dir in search_paths:
        if search_dir.exists():
            for pattern in hipaa_patterns:
                matches = list(search_dir.glob(pattern))
                if matches:
                    # Return the most recent one
                    return max(matches, key=lambda p: p.stat().st_mtime)
    
    return None


def create_provider_overlay(provider_data: Dict[str, Any], page_width: float, page_height: float) -> BytesIO:
    """Create a PDF overlay with provider info for the HIPAA 'To:' section."""
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    
    # Position for "To:" section (adjust based on template)
    # These coordinates are approximate - may need tuning
    x = 1.0 * inch
    y = page_height - 2.3 * inch  # Start below letterhead
    
    # Build provider address block
    c.setFont("Helvetica", 10)
    line_height = 12
    
    lines = [provider_data["name"]]
    if provider_data.get("attention"):
        lines.append(f"Attn: {provider_data['attention']}")
    if provider_data.get("address_line1"):
        lines.append(provider_data["address_line1"])
    if provider_data.get("address_line2"):
        lines.append(provider_data["address_line2"])
    
    city_state_zip = ""
    if provider_data.get("city"):
        city_state_zip = provider_data["city"]
        if provider_data.get("state"):
            city_state_zip += f", {provider_data['state']}"
        if provider_data.get("zip"):
            city_state_zip += f" {provider_data['zip']}"
    if city_state_zip:
        lines.append(city_state_zip)
    
    # Draw each line
    for i, line in enumerate(lines):
        c.drawString(x, y - (i * line_height), line)
    
    c.save()
    packet.seek(0)
    return packet


def create_date_overlay(date_str: str, page_width: float, page_height: float) -> BytesIO:
    """Create a PDF overlay with the current date for letters."""
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    
    # Position for date (top of letter, below letterhead)
    x = 1.0 * inch
    y = page_height - 1.5 * inch
    
    c.setFont("Helvetica", 10)
    c.drawString(x, y, date_str)
    
    c.save()
    packet.seek(0)
    return packet


def fill_hipaa_with_provider(
    hipaa_path: Path,
    provider_data: Dict[str, Any],
    case_data: Dict[str, Any]
) -> PdfWriter:
    """
    Fill the HIPAA with provider info in the 'To:' section.
    Returns a PdfWriter with the modified page.
    """
    reader = PdfReader(str(hipaa_path))
    writer = PdfWriter()
    
    page = reader.pages[0]
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
    
    # Create overlay with provider info
    overlay_packet = create_provider_overlay(provider_data, page_width, page_height)
    overlay_reader = PdfReader(overlay_packet)
    overlay_page = overlay_reader.pages[0]
    
    # Merge overlay onto HIPAA page
    page.merge_page(overlay_page)
    writer.add_page(page)
    
    return writer


def fill_request_letter(
    template_path: Path,
    provider_data: Dict[str, Any],
    case_data: Dict[str, Any],
    request_type: str = "records"  # "records" or "bills"
) -> PdfWriter:
    """
    Fill in a medical request letter template.
    Returns a PdfWriter with the filled page.
    """
    reader = PdfReader(str(template_path))
    writer = PdfWriter()
    
    # Clone the PDF properly to preserve form fields
    writer.append(reader)
    
    # Prepare field values
    today = datetime.now().strftime("%B %d, %Y")
    today_short = datetime.now().strftime("%m/%d/%Y")
    
    # Format client name
    client_name = case_data.get("client_name", "")
    
    # Format SSN with masking (XXX-XX-1234)
    ssn = case_data.get("ssn", "")
    if ssn and len(ssn) >= 4:
        ssn_masked = f"XXX-XX-{ssn[-4:]}"
    else:
        ssn_masked = ssn
    
    # Dates
    dob = case_data.get("dob", "")
    date_of_loss = case_data.get("date_of_loss", "")
    
    # Provider info
    provider_name = provider_data.get("name", "")
    fax = provider_data.get("fax", "")
    address = provider_data.get("address_line1", "")
    city_state_zip = f"{provider_data.get('city', '')}, {provider_data.get('state', 'KY')} {provider_data.get('zip', '')}"
    
    # Build field mapping (these field names may need adjustment based on actual template)
    # For medical records template (2023 Whaley Law Firm Medical Request Template)
    records_fields = {
        "Text46": today,                    # Date at top
        "Text53": fax,                      # Fax number
        "Text54": provider_name,            # Provider name line 1
        "Text55": address,                  # Address
        "Text56": city_state_zip,           # City, State ZIP
        "Text57": client_name,              # Client name
        "Text58": dob,                      # DOB
        "Text59": ssn_masked,               # SSN (masked)
        "Text60": date_of_loss,             # Date of loss
        "Text61": date_of_loss,             # Start date for records
        "Text62": "present",                # End date for records
        "Text63": "",                       # Additional text
        "Text64": "",                       # 
        "Text65": "records@whaleylawfirm.com",  # Email
        "Text66": "",
        "Text67": "",
    }
    
    # For medical bills template (2023 Whaley Initial Medical Billing Request)
    bills_fields = {
        "1": today,                         # Date
        "2": fax,                           # Fax
        "3": provider_name,                 # Provider
        "4": address,                       # Address
        "5": city_state_zip,                # City State ZIP
        "6": client_name,                   # Client name
        "7": dob,                           # DOB
        "8": ssn_masked,                    # SSN
        "9": date_of_loss,                  # Date of loss
        "10": date_of_loss,                 # Start date
        "11": "present",                    # End date
        "13": "",
        "14": "",
        "15": "billing@whaleylawfirm.com",  # Email
        "16": "",
    }
    
    field_values = records_fields if request_type == "records" else bills_fields
    
    # Update form fields using the proper method
    try:
        writer.update_page_form_field_values(writer.pages[0], field_values, auto_regenerate=True)
    except Exception as e:
        # If form filling fails, fields might have different names
        print(f"Warning: Could not fill some fields: {e}", file=sys.stderr)
    
    return writer


def generate_medical_request(
    case_name: str,
    provider_name: str,
    include_records_request: bool = False,
    include_bills_request: bool = False,
    hipaa_only: bool = False,
    output_path: Optional[str] = None,
    signed_hipaa_path: Optional[str] = None,
    provider_data: Optional[Dict] = None,
    case_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Generate a medical request package.
    
    Args:
        case_name: Project/case name (e.g., "Smith-MVA-01-15-2024")
        provider_name: Medical provider name
        include_records_request: Include medical records request letter
        include_bills_request: Include medical bills request letter
        hipaa_only: Only generate HIPAA with provider filled in
        output_path: Where to save the output PDF
        signed_hipaa_path: Path to client's signed HIPAA (auto-detected if not provided)
        provider_data: Override provider data (auto-loaded from DB if not provided)
        case_data: Override case data (auto-loaded from DB if not provided)
    
    Returns:
        Dict with status, output_path, pages, and any errors
    """
    result = {
        "status": "success",
        "output_path": None,
        "pages": [],
        "errors": []
    }
    
    # Load data if not provided
    if case_data is None:
        case_data = load_case_data(case_name)
    
    if provider_data is None:
        provider_data = load_provider_data(case_name, provider_name)
        if not provider_data.get("name"):
            provider_data["name"] = provider_name
    
    # Find signed HIPAA
    if signed_hipaa_path:
        hipaa_path = Path(signed_hipaa_path)
    else:
        hipaa_path = find_signed_hipaa(case_name)
        if not hipaa_path:
            # Fall back to blank template
            hipaa_path = HIPAA_TEMPLATE
            result["errors"].append("Signed HIPAA not found, using blank template")
    
    if not hipaa_path.exists():
        result["status"] = "error"
        result["errors"].append(f"HIPAA template not found: {hipaa_path}")
        return result
    
    # Collect PDFs to merge
    pdfs_to_merge = []
    
    try:
        # Add medical records request letter if requested
        if include_records_request and not hipaa_only:
            if RECORDS_REQUEST_TEMPLATE.exists():
                records_writer = fill_request_letter(
                    RECORDS_REQUEST_TEMPLATE,
                    provider_data,
                    case_data,
                    "records"
                )
                # Save to temp file for merging
                import tempfile
                temp_records = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                records_writer.write(temp_records)
                temp_records.close()
                pdfs_to_merge.append(temp_records.name)
                result["pages"].append("Medical Records Request")
            else:
                result["errors"].append("Records request template not found")
        
        # Add medical bills request letter if requested
        if include_bills_request and not hipaa_only:
            if BILLS_REQUEST_TEMPLATE.exists():
                bills_writer = fill_request_letter(
                    BILLS_REQUEST_TEMPLATE,
                    provider_data,
                    case_data,
                    "bills"
                )
                temp_bills = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                bills_writer.write(temp_bills)
                temp_bills.close()
                pdfs_to_merge.append(temp_bills.name)
                result["pages"].append("Medical Bills Request")
            else:
                result["errors"].append("Bills request template not found")
        
        # Add HIPAA with provider info
        hipaa_writer = fill_hipaa_with_provider(hipaa_path, provider_data, case_data)
        temp_hipaa = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        hipaa_writer.write(temp_hipaa)
        temp_hipaa.close()
        pdfs_to_merge.append(temp_hipaa.name)
        result["pages"].append("HIPAA Authorization")
        
        # Merge all PDFs
        final_writer = PdfWriter()
        for pdf_path in pdfs_to_merge:
            final_writer.append(pdf_path)
        
        # Clean up temp files
        for temp_path in pdfs_to_merge:
            try:
                os.unlink(temp_path)
            except:
                pass
        
        # Determine output path
        if not output_path:
            today = datetime.now().strftime("%Y-%m-%d")
            client_lastname = case_data.get("client_name", "Client").split()[-1]
            provider_short = provider_name.replace(" ", "_")[:30]
            
            request_types = []
            if include_records_request:
                request_types.append("Records")
            if include_bills_request:
                request_types.append("Bills")
            if hipaa_only or not request_types:
                request_types.append("HIPAA")
            
            filename = f"{today} - {client_lastname} - Medical {'+'.join(request_types)} - {provider_short}.pdf"
            
            # Save to case folder
            case_dir = PROJECTS_DIR / case_name / "Medical Records" / provider_name.replace("/", "-")
            case_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(case_dir / filename)
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write final PDF
        with open(output_path, 'wb') as f:
            final_writer.write(f)
        
        result["output_path"] = output_path
        
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Generate medical records/bills requests with HIPAA authorization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate HIPAA only with provider filled in
  python medical_request_generator.py --case "Smith-MVA" --provider "Baptist Health" --hipaa-only
  
  # Generate records request + HIPAA
  python medical_request_generator.py --case "Smith-MVA" --provider "Baptist Health" --records-request
  
  # Generate bills request + HIPAA
  python medical_request_generator.py --case "Smith-MVA" --provider "Baptist Health" --bills-request
  
  # Generate all three (records + bills + HIPAA)
  python medical_request_generator.py --case "Smith-MVA" --provider "Baptist Health" --records-request --bills-request
        """
    )
    
    parser.add_argument("--case", "-c", required=True, help="Case/project name")
    parser.add_argument("--provider", "-p", required=True, help="Medical provider name")
    parser.add_argument("--records-request", "-r", action="store_true",
                        help="Include medical records request letter")
    parser.add_argument("--bills-request", "-b", action="store_true",
                        help="Include medical bills request letter")
    parser.add_argument("--hipaa-only", action="store_true",
                        help="Generate only HIPAA with provider filled in")
    parser.add_argument("--output", "-o", help="Output PDF path (auto-generated if not specified)")
    parser.add_argument("--signed-hipaa", help="Path to client's signed HIPAA (auto-detected if not specified)")
    parser.add_argument("--provider-address", help="Provider address (if not in database)")
    parser.add_argument("--provider-fax", help="Provider fax number (if not in database)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    # If neither records nor bills requested, default to HIPAA only
    if not args.records_request and not args.bills_request and not args.hipaa_only:
        args.hipaa_only = True
    
    # Build provider data overrides
    provider_override = None
    if args.provider_address or args.provider_fax:
        provider_override = {"name": args.provider}
        if args.provider_address:
            # Simple address parsing
            parts = args.provider_address.split(",")
            provider_override["address_line1"] = parts[0].strip() if parts else ""
            if len(parts) > 1:
                city_state_zip = parts[1].strip()
                provider_override["city"] = city_state_zip
        if args.provider_fax:
            provider_override["fax"] = args.provider_fax
    
    result = generate_medical_request(
        case_name=args.case,
        provider_name=args.provider,
        include_records_request=args.records_request,
        include_bills_request=args.bills_request,
        hipaa_only=args.hipaa_only,
        output_path=args.output,
        signed_hipaa_path=args.signed_hipaa,
        provider_data=provider_override
    )
    
    print(json.dumps(result, indent=2 if args.pretty else None))
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()

