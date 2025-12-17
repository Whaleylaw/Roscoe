#!/usr/bin/env python3
"""
DOCX Handler for Document Generation

Processes DOCX templates by replacing placeholders with actual data.
Handles Word's tendency to split placeholders across multiple XML elements.

Usage:
    from handlers.docx_handler import process_docx_template
    
    result = process_docx_template(
        docx_path="/path/to/template.docx",
        context={"client.name": "John Doe", "incidentDate": "January 1, 2025"},
        output_pdf=True
    )
"""

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple
from zipfile import ZIP_DEFLATED, ZipFile


def get_placeholder_value(placeholder: str, context: Dict[str, Any]) -> Tuple[str, bool]:
    """Get value for a placeholder, return (value, found)."""
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
        except Exception:
            pass
    
    return str(value) if value else "", bool(value)


def replace_placeholders_in_xml(
    xml_content: str,
    context: Dict[str, Any]
) -> Tuple[str, List[str], List[str]]:
    """
    Replace all {{placeholder}} patterns in XML content.
    
    Handles cases where Word splits placeholders across multiple XML elements
    by processing each paragraph as a unit.
    
    Args:
        xml_content: The XML content from document.xml
        context: Dictionary of placeholder -> value mappings
    
    Returns:
        Tuple of (modified_xml, filled_placeholders, missing_placeholders)
    """
    filled = []
    missing = []
    
    def process_paragraph(para_xml: str) -> str:
        """Process a single paragraph, handling split placeholders."""
        # Extract all text content from this paragraph
        text_pattern = r'<w:t(?:[^>]*)>([^<]*)</w:t>'
        text_matches = list(re.finditer(text_pattern, para_xml))
        
        if not text_matches:
            return para_xml
        
        # Get combined text
        combined_text = ''.join(m.group(1) for m in text_matches)
        
        # Find placeholders in combined text
        placeholder_pattern = r'\{\{([a-zA-Z][a-zA-Z0-9._]*)\}\}'
        if not re.search(placeholder_pattern, combined_text):
            return para_xml
        
        # We have placeholders - need to rebuild this paragraph
        # Replace placeholders in the combined text
        new_text = combined_text
        for ph_match in re.finditer(placeholder_pattern, combined_text):
            ph_key = ph_match.group(1)
            value, found = get_placeholder_value(ph_key, context)
            
            if found:
                filled.append(ph_key)
                # Escape XML special chars
                value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            else:
                missing.append(ph_key)
                value = f"[{ph_key}]"
            
            new_text = new_text.replace(f"{{{{{ph_key}}}}}", value, 1)
        
        # Now redistribute text back into XML structure
        # Strategy: Put all text in the first <w:t>, clear subsequent ones
        result = para_xml
        for i, match in enumerate(text_matches):
            start, end = match.start(), match.end()
            
            # Adjust for any changes we've made
            # Find the actual position in current result
            original_text = match.group(1)
            
            if i == 0:
                # First text element gets all the new text
                replacement = match.group(0).replace(f'>{original_text}<', f'>{new_text}<')
            else:
                # Subsequent elements become empty
                replacement = match.group(0).replace(f'>{original_text}<', '><')
            
            # Find and replace this specific occurrence
            result = result.replace(match.group(0), replacement, 1)
        
        return result
    
    # Process each paragraph
    para_pattern = r'<w:p[^>]*>.*?</w:p>'
    result = re.sub(para_pattern, lambda m: process_paragraph(m.group(0)), 
                    xml_content, flags=re.DOTALL)
    
    return result, list(set(filled)), list(set(missing))


def process_docx_template(
    docx_path: str,
    context: Dict[str, Any],
    output_pdf: bool = True
) -> Dict[str, Any]:
    """
    Process a DOCX template by filling placeholders.
    
    The filled document overwrites the input file, and optionally
    generates a PDF alongside.
    
    Args:
        docx_path: Path to the DOCX file (will be overwritten with filled version)
        context: Dictionary of placeholder -> value mappings
        output_pdf: Whether to also generate a PDF
    
    Returns:
        Dict with:
            - status: "success" | "error"
            - docx_path: Path to filled DOCX
            - pdf_path: Path to PDF (if generated)
            - fields_filled: List of placeholders that were filled
            - fields_missing: List of placeholders that couldn't be filled
            - errors: List of error messages
    """
    result = {
        "status": "error",
        "docx_path": None,
        "pdf_path": None,
        "fields_filled": [],
        "fields_missing": [],
        "errors": [],
    }
    
    path = Path(docx_path)
    
    if not path.exists():
        result["errors"].append(f"File not found: {docx_path}")
        return result
    
    if path.suffix.lower() != '.docx':
        result["errors"].append(f"Not a DOCX file: {docx_path}")
        return result
    
    all_filled = []
    all_missing = []
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract DOCX
            with ZipFile(path, 'r') as zip_ref:
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
            
            # Repack the DOCX (overwrite original)
            with ZipFile(path, 'w', ZIP_DEFLATED) as zip_out:
                for file_path in temp_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_path)
                        zip_out.write(file_path, arcname)
        
        result["docx_path"] = str(path)
        result["fields_filled"] = list(set(all_filled))
        result["fields_missing"] = list(set(all_missing))
        
        # Convert to PDF if requested
        if output_pdf:
            pdf_path = path.with_suffix(".pdf")
            pdf_success, pdf_error = convert_docx_to_pdf(path, pdf_path)
            
            if pdf_success:
                result["pdf_path"] = str(pdf_path)
            else:
                result["errors"].append(f"PDF conversion failed: {pdf_error}")
        
        result["status"] = "success"
        
    except Exception as e:
        result["errors"].append(str(e))
        import traceback
        result["errors"].append(traceback.format_exc())
    
    return result


def convert_docx_to_pdf(docx_path: Path, pdf_path: Path) -> Tuple[bool, str]:
    """
    Convert DOCX to PDF using LibreOffice.
    
    Args:
        docx_path: Path to source DOCX
        pdf_path: Desired path for output PDF
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Try soffice (LibreOffice)
        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            str(docx_path),
            "--outdir", str(pdf_path.parent)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # LibreOffice names output based on input filename
        expected_pdf = pdf_path.parent / (docx_path.stem + ".pdf")
        if expected_pdf.exists() and expected_pdf != pdf_path:
            shutil.move(expected_pdf, pdf_path)
        
        if pdf_path.exists():
            return True, ""
        else:
            return False, f"PDF not created. stderr: {result.stderr}"
    
    except FileNotFoundError:
        return False, "LibreOffice not found. Install with: brew install --cask libreoffice"
    except subprocess.TimeoutExpired:
        return False, "PDF conversion timed out"
    except Exception as e:
        return False, str(e)


# =============================================================================
# CLI for testing
# =============================================================================

def main():
    """Test DOCX processing."""
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python docx_handler.py <docx_path> [--context '{...}']")
        sys.exit(1)
    
    docx_path = sys.argv[1]
    
    # Parse context from command line
    context = {}
    if len(sys.argv) > 3 and sys.argv[2] == "--context":
        context = json.loads(sys.argv[3])
    else:
        # Default test context
        context = {
            "client.name": "Test Client",
            "incidentDate": "January 1, 2025",
            "TODAY": "December 14, 2025",
        }
    
    result = process_docx_template(docx_path, context)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

