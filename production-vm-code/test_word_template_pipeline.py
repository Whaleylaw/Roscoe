#!/usr/bin/env python3
"""
Smoke Test for Word Template Pipeline

This script tests the template filling and PDF export capabilities
using actual templates from the forms directory.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the source directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from roscoe.agents.paralegal.word_template_pipeline import (
    check_dependencies,
    list_template_placeholders,
    fill_and_export_template,
    convert_docx_to_pdf,
)


def test_dependencies():
    """Test that all dependencies are available."""
    print("=" * 60)
    print("DEPENDENCY CHECK")
    print("=" * 60)
    
    deps = check_dependencies()
    
    print(f"  docxtpl:     {'✅ Available' if deps['docxtpl_available'] else '❌ Missing'}")
    print(f"  python-docx: {'✅ Available' if deps['python_docx_available'] else '❌ Missing'}")
    print(f"  LibreOffice: {'✅ Available' if deps['libreoffice_available'] else '❌ Missing'}")
    
    if deps['libreoffice_path']:
        print(f"               Path: {deps['libreoffice_path']}")
    
    if not deps['all_available']:
        print(f"\n⚠️  Missing: {', '.join(deps['missing'])}")
    else:
        print("\n✅ All dependencies available!")
    
    return deps['all_available']


def test_template_inspection(template_path: Path):
    """Test that we can read placeholders from a template."""
    print(f"\n{'=' * 60}")
    print(f"TEMPLATE INSPECTION: {template_path.name}")
    print("=" * 60)
    
    try:
        placeholders = list_template_placeholders(template_path)
        
        if placeholders:
            print(f"Found {len(placeholders)} placeholder(s):")
            for p in placeholders[:15]:
                print(f"  • {p}")
            if len(placeholders) > 15:
                print(f"  ... and {len(placeholders) - 15} more")
        else:
            print("No Jinja2 placeholders found.")
            print("(Template may use a different placeholder format)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_fill_template(template_path: Path, output_dir: Path):
    """Test template filling with sample data."""
    print(f"\n{'=' * 60}")
    print(f"TEMPLATE FILLING TEST: {template_path.name}")
    print("=" * 60)
    
    # Sample context - adjust based on template
    context = {
        # Client info
        "client_name": "Test Client",
        "client_address": "123 Test Street, Louisville, KY 40202",
        "client_dob": "January 1, 1980",
        "client_ssn": "XXX-XX-1234",
        
        # Case info
        "date_of_accident": "December 1, 2024",
        "case_number": "24-CI-001234",
        "our_file_number": "2024-TEST-001",
        
        # Defendants
        "defendant_name": "Defendant LLC",
        "defendant_address": "456 Defendant Ave, Louisville, KY 40203",
        
        # Insurance
        "insurance_company": "Test Insurance Co.",
        "claim_number": "CLM-2024-12345",
        "policy_number": "POL-987654",
        
        # Court info
        "court_name": "Jefferson Circuit Court",
        "court_division": "Division 1",
        
        # Attorney info
        "attorney_name": "Aaron Whaley",
        "firm_name": "Whaley Law PLLC",
        "firm_address": "100 W Main St, Ste 100, Louisville, KY 40202",
        "firm_phone": "(502) 555-0123",
        
        # Dates
        "date_today": "December 12, 2024",
        "response_deadline": "30 days",
    }
    
    output_path = output_dir / f"FILLED_{template_path.stem}.docx"
    
    try:
        result = fill_and_export_template(
            template_path=template_path,
            output_path=output_path,
            context=context,
            export_pdf=True,
        )
        
        if result.get("success"):
            print(f"✅ DOCX created: {result.get('docx_path')}")
            
            if result.get("pdf_path"):
                print(f"✅ PDF created:  {result.get('pdf_path')}")
            elif result.get("pdf_error"):
                print(f"⚠️  PDF failed:  {result.get('pdf_error')}")
            
            filled = result.get("placeholders_filled", [])
            unfilled = result.get("placeholders_unfilled", [])
            
            if filled:
                print(f"\nFilled {len(filled)} placeholder(s)")
            if unfilled:
                print(f"⚠️  {len(unfilled)} placeholder(s) not filled:")
                for p in unfilled[:5]:
                    print(f"    • {p}")
            
            return True
        else:
            print(f"❌ Failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_pdf_only_export(docx_path: Path, output_dir: Path):
    """Test PDF-only export from an existing DOCX."""
    print(f"\n{'=' * 60}")
    print(f"PDF EXPORT TEST: {docx_path.name}")
    print("=" * 60)
    
    try:
        result = convert_docx_to_pdf(docx_path, output_dir)
        
        if result.get("success"):
            print(f"✅ PDF created: {result.get('output_path')}")
            return True
        else:
            print(f"❌ Failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print(" WORD TEMPLATE PIPELINE - SMOKE TEST")
    print("=" * 60 + "\n")
    
    # Find templates directory
    forms_base = Path("/Volumes/X10 Pro/Roscoe/workspace_paralegal_backup_20251208_180450/forms")
    
    if not forms_base.exists():
        print(f"❌ Forms directory not found: {forms_base}")
        return 1
    
    # Test templates
    test_templates = [
        forms_base / "complaints" / "2022 Whaley MVA Complaint - Standard.docx",
        forms_base / "liens" / "Ltr with HIPPA (BW).docx",
        forms_base / "mediation" / "2022 Whaley Mediation Notice to Client.docx",
    ]
    
    # Filter to existing templates
    test_templates = [t for t in test_templates if t.exists()]
    
    if not test_templates:
        print("❌ No test templates found!")
        return 1
    
    print(f"Found {len(test_templates)} template(s) for testing")
    
    # 1. Check dependencies
    deps_ok = test_dependencies()
    
    # 2. Create temp directory for outputs
    with tempfile.TemporaryDirectory(prefix="word_pipeline_test_") as temp_dir:
        output_dir = Path(temp_dir)
        print(f"\nOutput directory: {output_dir}")
        
        all_passed = True
        
        # 3. Test each template
        for template in test_templates:
            # Test inspection
            if not test_template_inspection(template):
                all_passed = False
            
            # Test filling
            if deps_ok:
                if not test_fill_template(template, output_dir):
                    all_passed = False
        
        # 4. Summary
        print("\n" + "=" * 60)
        print(" SMOKE TEST SUMMARY")
        print("=" * 60)
        
        if all_passed and deps_ok:
            print("\n✅ All tests passed!")
            print("\nThe word template pipeline is ready to use.")
            return 0
        elif not deps_ok:
            print("\n⚠️  Some dependencies missing.")
            print("Template inspection works, but filling/PDF export may fail.")
            print("See LIBREOFFICE_SETUP.md for installation instructions.")
            return 1
        else:
            print("\n❌ Some tests failed.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
