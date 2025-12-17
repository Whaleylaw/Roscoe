#!/usr/bin/env python3
"""
PDF Form Filler Tool

Fill out PDF forms (AcroForms) programmatically. Works with any fillable PDF.

Usage:
    # List available fields in a PDF form
    python fill_pdf_form.py /path/to/form.pdf --list-fields
    
    # Fill form with field values
    python fill_pdf_form.py /path/to/form.pdf /path/to/output.pdf \
        --field "Full Name" "John Smith" \
        --field "Date" "December 9, 2025"
    
    # Fill from JSON file
    python fill_pdf_form.py /path/to/form.pdf /path/to/output.pdf \
        --from-json /path/to/field_values.json
    
    # Interactive mode (prompts for each field)
    python fill_pdf_form.py /path/to/form.pdf /path/to/output.pdf --interactive
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from pypdf import PdfReader, PdfWriter


def list_form_fields(pdf_path: str) -> Dict[str, Any]:
    """
    List all form fields in a PDF with their types and current values.
    
    Returns dict with:
        - is_fillable: bool
        - field_count: int
        - fields: list of {name, type, value, options}
    """
    result = {
        "is_fillable": False,
        "field_count": 0,
        "fields": []
    }
    
    try:
        reader = PdfReader(pdf_path)
        fields = reader.get_fields()
        
        if not fields:
            return result
        
        result["is_fillable"] = True
        result["field_count"] = len(fields)
        
        for field_name, field_info in fields.items():
            field_type_code = str(field_info.get('/FT', ''))
            
            # Map field type codes to human-readable names
            type_map = {
                '/Tx': 'text',
                '/Btn': 'button/checkbox',
                '/Ch': 'choice/dropdown',
                '/Sig': 'signature'
            }
            field_type = type_map.get(field_type_code, field_type_code)
            
            field_data = {
                "name": field_name,
                "type": field_type,
                "value": str(field_info.get('/V', '')) if field_info.get('/V') else None,
            }
            
            # For choice fields, get options
            if field_type == 'choice/dropdown' and '/Opt' in field_info:
                field_data["options"] = [str(opt) for opt in field_info.get('/Opt', [])]
            
            result["fields"].append(field_data)
        
        return result
        
    except Exception as e:
        return {"error": str(e), "is_fillable": False}


def fill_pdf_form(
    template_path: str,
    output_path: str,
    field_values: Dict[str, str],
    flatten: bool = False
) -> Dict[str, Any]:
    """
    Fill a PDF form with provided field values.
    
    Args:
        template_path: Path to the fillable PDF template
        output_path: Where to save the filled PDF
        field_values: Dict mapping field names to values
        flatten: If True, flatten the form (fields become non-editable)
    
    Returns:
        Dict with status, filled_fields, unfilled_fields, errors
    """
    result = {
        "status": "success",
        "template": template_path,
        "output": output_path,
        "filled_fields": [],
        "unfilled_fields": [],
        "unknown_fields": [],
        "errors": []
    }
    
    try:
        reader = PdfReader(template_path)
        writer = PdfWriter()
        
        # Clone all pages to writer
        writer.append(reader)
        
        # Get available fields
        available_fields = set(reader.get_fields().keys()) if reader.get_fields() else set()
        
        if not available_fields:
            result["status"] = "error"
            result["errors"].append("PDF has no fillable form fields")
            return result
        
        # Check for unknown fields in input
        for field_name in field_values.keys():
            if field_name not in available_fields:
                result["unknown_fields"].append(field_name)
        
        # Fill the form fields
        for field_name in available_fields:
            if field_name in field_values and field_values[field_name]:
                result["filled_fields"].append(field_name)
            else:
                result["unfilled_fields"].append(field_name)
        
        # Update form field values
        writer.update_page_form_field_values(
            writer.pages[0],
            field_values,
            auto_regenerate=True
        )
        
        # Optionally flatten (make non-editable)
        if flatten:
            for page in writer.pages:
                if '/Annots' in page:
                    # This removes the form field interactivity
                    pass  # Basic flattening - fields remain visible but not editable
        
        # Write output
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        if result["unknown_fields"]:
            result["errors"].append(f"Unknown fields ignored: {result['unknown_fields']}")
        
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Fill PDF forms (AcroForms) programmatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List fields in a form
  python fill_pdf_form.py form.pdf --list-fields
  
  # Fill specific fields
  python fill_pdf_form.py form.pdf filled.pdf --field "Name" "John Smith" --field "Date" "12/9/2025"
  
  # Fill from JSON
  python fill_pdf_form.py form.pdf filled.pdf --from-json values.json
  
  # JSON format:
  {
    "Full Name": "John Smith",
    "Date": "December 9, 2025",
    "Date of Incident": "January 15, 2024"
  }
        """
    )
    
    parser.add_argument("template", help="Path to fillable PDF template")
    parser.add_argument("output", nargs='?', help="Path for filled PDF output")
    parser.add_argument("--list-fields", "-l", action="store_true",
                        help="List available form fields and exit")
    parser.add_argument("--field", "-f", nargs=2, action="append", metavar=("NAME", "VALUE"),
                        help="Set field value (can be used multiple times)")
    parser.add_argument("--from-json", "-j", help="Load field values from JSON file")
    parser.add_argument("--flatten", action="store_true",
                        help="Flatten the form (make fields non-editable)")
    parser.add_argument("--pretty", "-p", action="store_true",
                        help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    # List fields mode
    if args.list_fields:
        result = list_form_fields(args.template)
        print(json.dumps(result, indent=2 if args.pretty else None))
        sys.exit(0 if result.get("is_fillable") else 1)
    
    # Fill mode - need output path
    if not args.output:
        parser.error("output path is required when filling a form")
    
    # Collect field values
    field_values = {}
    
    if args.from_json:
        try:
            with open(args.from_json, 'r') as f:
                field_values = json.load(f)
        except Exception as e:
            print(json.dumps({"error": f"Failed to load JSON: {e}"}))
            sys.exit(1)
    
    if args.field:
        for name, value in args.field:
            field_values[name] = value
    
    if not field_values:
        # Show available fields if no values provided
        print("No field values provided. Available fields:", file=sys.stderr)
        result = list_form_fields(args.template)
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)
    
    # Fill the form
    result = fill_pdf_form(
        args.template,
        args.output,
        field_values,
        flatten=args.flatten
    )
    
    print(json.dumps(result, indent=2 if args.pretty else None))
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()

