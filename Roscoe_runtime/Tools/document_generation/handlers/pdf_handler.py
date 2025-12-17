#!/usr/bin/env python3
"""
PDF Handler for Document Generation

Fills PDF form fields with data from the context.
Used for fillable PDF forms like the KACP PIP Application.

Usage:
    from handlers.pdf_handler import process_pdf_form
    
    result = process_pdf_form(
        pdf_path="/path/to/form.pdf",
        context={"client.name": "John Doe", "client.ssn": "123-45-6789"}
    )
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Try to import PDF libraries
try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import pdfrw
    from pdfrw import PdfReader as PdfrwReader, PdfWriter as PdfrwWriter
    PDFRW_AVAILABLE = True
except ImportError:
    PDFRW_AVAILABLE = False


def get_form_fields(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Get all form fields from a PDF.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        List of field info dicts with name, type, value
    """
    fields = []
    
    if PYPDF_AVAILABLE:
        try:
            reader = PdfReader(pdf_path)
            if reader.get_fields():
                for name, field in reader.get_fields().items():
                    fields.append({
                        "name": name,
                        "type": str(field.get("/FT", "Unknown")),
                        "value": field.get("/V", ""),
                    })
        except Exception:
            pass
    
    if not fields and PDFRW_AVAILABLE:
        try:
            reader = PdfrwReader(pdf_path)
            for page in reader.pages:
                annots = page.get('/Annots')
                if annots:
                    for annot in annots:
                        if annot.get('/Subtype') == '/Widget':
                            name = annot.get('/T')
                            if name:
                                # pdfrw returns names in parentheses
                                name_str = str(name).strip('()')
                                fields.append({
                                    "name": name_str,
                                    "type": str(annot.get('/FT', 'Unknown')),
                                    "value": str(annot.get('/V', '')).strip('()'),
                                })
        except Exception:
            pass
    
    return fields


def fill_pdf_form_pypdf(
    pdf_path: str,
    field_values: Dict[str, str],
    output_path: str
) -> Tuple[bool, List[str], List[str]]:
    """
    Fill PDF form using pypdf library.
    
    Returns:
        Tuple of (success, filled_fields, unfilled_fields)
    """
    filled = []
    unfilled = []
    
    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Get existing fields
        existing_fields = set()
        if reader.get_fields():
            existing_fields = set(reader.get_fields().keys())
        
        # Fill fields
        for field_name, value in field_values.items():
            if field_name in existing_fields:
                writer.update_page_form_field_values(
                    writer.pages[0],  # Assume single page form for now
                    {field_name: value}
                )
                filled.append(field_name)
            else:
                unfilled.append(field_name)
        
        # Write output
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return True, filled, unfilled
    
    except Exception as e:
        return False, filled, [str(e)]


def fill_pdf_form_pdfrw(
    pdf_path: str,
    field_values: Dict[str, str],
    output_path: str
) -> Tuple[bool, List[str], List[str]]:
    """
    Fill PDF form using pdfrw library.
    
    Returns:
        Tuple of (success, filled_fields, unfilled_fields)
    """
    filled = []
    unfilled = list(field_values.keys())
    
    try:
        reader = PdfrwReader(pdf_path)
        
        for page in reader.pages:
            annots = page.get('/Annots')
            if not annots:
                continue
            
            for annot in annots:
                if annot.get('/Subtype') != '/Widget':
                    continue
                
                field_name = annot.get('/T')
                if not field_name:
                    continue
                
                # Clean field name
                field_name_str = str(field_name).strip('()')
                
                if field_name_str in field_values:
                    value = field_values[field_name_str]
                    
                    # Set the value
                    annot.update(pdfrw.PdfDict(V=f'({value})', AP=''))
                    
                    filled.append(field_name_str)
                    if field_name_str in unfilled:
                        unfilled.remove(field_name_str)
        
        # Write output
        PdfrwWriter(output_path, trailer=reader).write()
        
        return True, filled, unfilled
    
    except Exception as e:
        return False, filled, [str(e)]


def map_context_to_fields(
    context: Dict[str, Any],
    field_mapping: Dict[str, str] = None
) -> Dict[str, str]:
    """
    Map context values to PDF field names.
    
    Args:
        context: The context dictionary with nested values
        field_mapping: Optional explicit mapping of context_key -> field_name
    
    Returns:
        Dict of field_name -> value
    """
    field_values = {}
    
    # Default mappings for common fields
    default_mapping = {
        "client.name": ["Name", "ClientName", "client_name", "Claimant Name"],
        "client.address": ["Address", "ClientAddress", "Street Address"],
        "client.ssn": ["SSN", "Social Security", "SS#"],
        "client.dob": ["DOB", "Date of Birth", "BirthDate"],
        "client.phone": ["Phone", "Telephone", "PhoneNumber"],
        "incidentDate": ["Date of Accident", "Accident Date", "DateOfLoss"],
    }
    
    def flatten_context(ctx, prefix=""):
        """Flatten nested context to dot-notation keys."""
        flat = {}
        for key, value in ctx.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flat.update(flatten_context(value, full_key))
            else:
                flat[full_key] = str(value) if value else ""
        return flat
    
    flat_context = flatten_context(context)
    
    # Apply field mapping
    if field_mapping:
        for context_key, field_name in field_mapping.items():
            if context_key in flat_context:
                field_values[field_name] = flat_context[context_key]
    
    # Apply default mappings
    for context_key, field_names in default_mapping.items():
        if context_key in flat_context:
            value = flat_context[context_key]
            for field_name in field_names:
                field_values[field_name] = value
    
    # Also include all flat context values as potential field names
    for key, value in flat_context.items():
        # Convert to common field name formats
        simple_key = key.split('.')[-1]
        field_values[simple_key] = value
        field_values[key] = value
        field_values[key.replace('.', '_')] = value
    
    return field_values


def process_pdf_form(
    pdf_path: str,
    context: Dict[str, Any],
    field_mapping: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Process a fillable PDF form.
    
    The filled PDF overwrites the input file.
    
    Args:
        pdf_path: Path to the PDF form (will be overwritten)
        context: Dictionary with values to fill
        field_mapping: Optional explicit mapping of context_key -> field_name
    
    Returns:
        Dict with:
            - status: "success" | "error"
            - pdf_path: Path to filled PDF
            - fields_filled: List of fields that were filled
            - fields_missing: List of context values that couldn't be mapped
            - available_fields: List of fields in the PDF
            - errors: List of error messages
    """
    result = {
        "status": "error",
        "pdf_path": None,
        "fields_filled": [],
        "fields_missing": [],
        "available_fields": [],
        "errors": [],
    }
    
    path = Path(pdf_path)
    
    if not path.exists():
        result["errors"].append(f"File not found: {pdf_path}")
        return result
    
    if path.suffix.lower() != '.pdf':
        result["errors"].append(f"Not a PDF file: {pdf_path}")
        return result
    
    if not PYPDF_AVAILABLE and not PDFRW_AVAILABLE:
        result["errors"].append("No PDF library available. Install pypdf or pdfrw.")
        return result
    
    try:
        # Get available fields
        available_fields = get_form_fields(pdf_path)
        result["available_fields"] = [f["name"] for f in available_fields]
        
        if not available_fields:
            result["errors"].append("No fillable form fields found in PDF")
            return result
        
        # Map context to field values
        field_values = map_context_to_fields(context, field_mapping)
        
        # Create temporary output path
        temp_output = path.with_suffix('.filled.pdf')
        
        # Try to fill the form
        success = False
        
        if PYPDF_AVAILABLE:
            success, filled, unfilled = fill_pdf_form_pypdf(
                str(path), field_values, str(temp_output)
            )
        
        if not success and PDFRW_AVAILABLE:
            success, filled, unfilled = fill_pdf_form_pdfrw(
                str(path), field_values, str(temp_output)
            )
        
        if success and temp_output.exists():
            # Replace original with filled version
            temp_output.replace(path)
            
            result["pdf_path"] = str(path)
            result["fields_filled"] = filled
            result["fields_missing"] = unfilled
            result["status"] = "success"
        else:
            result["errors"].append("Failed to fill PDF form")
            if unfilled:
                result["errors"].extend(unfilled)
        
    except Exception as e:
        result["errors"].append(str(e))
        import traceback
        result["errors"].append(traceback.format_exc())
    
    return result


# =============================================================================
# CLI for testing
# =============================================================================

def main():
    """Test PDF form processing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_handler.py <pdf_path> [--list-fields]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "--list-fields":
        fields = get_form_fields(pdf_path)
        print(f"Found {len(fields)} form fields:")
        for field in fields:
            print(f"  {field['name']}: {field['type']} = {field['value']}")
        return
    
    # Test with sample context
    context = {
        "client": {
            "name": "Test Client",
            "address": "123 Test St",
            "ssn": "123-45-6789",
            "dob": "01/01/1980",
        },
        "incidentDate": "01/01/2025",
    }
    
    result = process_pdf_form(pdf_path, context)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

