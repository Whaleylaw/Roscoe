#!/usr/bin/env python3
"""
Letterhead Generator Tool

Takes markdown content and generates a professional document on firm letterhead,
then optionally converts to PDF.

Uses pandoc's --reference-doc feature for styles, then post-processes to
copy over header/footer files with the logo.

Usage:
    from letterhead_generator import generate_letterhead_document
    
    result = generate_letterhead_document(
        markdown_path="/path/to/content.md",
        output_path="/path/to/output.docx",
        convert_to_pdf=True
    )
"""

import os
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Default letterhead template location
DEFAULT_LETTERHEAD = Path(__file__).parent.parent.parent / "forms" / "2021 Whaley Letterhead (1).docx"


def generate_letterhead_document(
    markdown_path: Optional[str] = None,
    markdown_content: Optional[str] = None,
    output_path: str = None,
    convert_to_pdf: bool = True,
    letterhead_template: Optional[str] = None,
    replacements: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Generate a document on letterhead from markdown content.
    
    Uses pandoc with --reference-doc for styles, then copies header/footer files
    from the letterhead template to include the logo.
    
    Args:
        markdown_path: Path to markdown file (mutually exclusive with markdown_content)
        markdown_content: Markdown string content (mutually exclusive with markdown_path)
        output_path: Where to save the output .docx (required)
        convert_to_pdf: Whether to also generate a PDF version
        letterhead_template: Custom letterhead template path (uses default if not specified)
        replacements: Dictionary of placeholder replacements (e.g., {"{{CLIENT_NAME}}": "John Smith"})
    
    Returns:
        Dictionary with status, paths, and any errors
    """
    result = {
        "status": "success",
        "docx_path": None,
        "pdf_path": None,
        "errors": []
    }
    
    # Validate inputs
    if not markdown_path and not markdown_content:
        result["status"] = "error"
        result["errors"].append("Must provide either markdown_path or markdown_content")
        return result
    
    if markdown_path and markdown_content:
        result["status"] = "error"
        result["errors"].append("Provide only one of markdown_path or markdown_content, not both")
        return result
    
    if not output_path:
        result["status"] = "error"
        result["errors"].append("output_path is required")
        return result
    
    # Read markdown content
    if markdown_path:
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"Failed to read markdown file: {e}")
            return result
    
    # Resolve template path
    template_path = Path(letterhead_template) if letterhead_template else DEFAULT_LETTERHEAD
    if not template_path.exists():
        result["status"] = "error"
        result["errors"].append(f"Letterhead template not found: {template_path}")
        return result
    
    # Check pandoc is available
    if not shutil.which('pandoc'):
        result["status"] = "error"
        result["errors"].append("pandoc not found. Install with: brew install pandoc")
        return result
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Apply standard replacements to markdown
    today_long = datetime.now().strftime("%B %d, %Y")
    today_short = datetime.now().strftime("%m/%d/%Y")
    
    standard_replacements = {
        "{{TODAY_LONG}}": today_long,
        "{{TODAY_SHORT}}": today_short,
        "{{TODAY}}": today_long,
        "{{DATE}}": today_long,
    }
    if replacements:
        standard_replacements.update(replacements)
    
    for placeholder, value in standard_replacements.items():
        markdown_content = markdown_content.replace(placeholder, value)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write markdown to temp file
            md_file = temp_path / "content.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Temp output for pandoc
            pandoc_output = temp_path / "pandoc_output.docx"
            
            # Use pandoc with --reference-doc to inherit letterhead styles
            pandoc_cmd = [
                'pandoc',
                str(md_file),
                '-o', str(pandoc_output),
                '--from', 'markdown+pipe_tables+grid_tables+raw_html',
                '--to', 'docx',
                '--reference-doc', str(template_path),
            ]
            
            pandoc_result = subprocess.run(
                pandoc_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if pandoc_result.returncode != 0:
                result["errors"].append(f"Pandoc error: {pandoc_result.stderr}")
            
            if not pandoc_output.exists():
                result["status"] = "error"
                result["errors"].append(f"Pandoc failed to create output file. stderr: {pandoc_result.stderr}")
                return result
            
            # Post-process: Copy header/footer files from letterhead template
            final_docx = inject_header_footer(pandoc_output, template_path, temp_path)
            
            # Copy to final output
            shutil.copy(final_docx, output_path)
            result["docx_path"] = str(output_path)
            
            # Convert to PDF if requested
            if convert_to_pdf:
                pdf_path = output_path.with_suffix('.pdf')
                pdf_result = convert_docx_to_pdf(output_path, pdf_path)
                if pdf_result["success"]:
                    result["pdf_path"] = str(pdf_path)
                else:
                    result["errors"].append(f"PDF conversion warning: {pdf_result['error']}")
    
    except subprocess.TimeoutExpired:
        result["status"] = "error"
        result["errors"].append("Pandoc conversion timed out")
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"Document generation failed: {e}")
        import traceback
        result["errors"].append(traceback.format_exc())
    
    return result


def inject_header_footer(pandoc_docx: Path, letterhead_docx: Path, temp_dir: Path) -> Path:
    """
    Copy header/footer files from letterhead template into the pandoc-generated docx.
    
    Pandoc's --reference-doc copies styles but not the actual header/footer files.
    This function:
    1. Extracts both docx files
    2. Copies header*.xml, footer*.xml, and media/* from letterhead
    3. Updates relationships and content types
    4. Repacks into final docx
    """
    # Extract both docx files
    pandoc_dir = temp_dir / "pandoc"
    letterhead_dir = temp_dir / "letterhead"
    
    with zipfile.ZipFile(pandoc_docx, 'r') as z:
        z.extractall(pandoc_dir)
    
    with zipfile.ZipFile(letterhead_docx, 'r') as z:
        z.extractall(letterhead_dir)
    
    # Copy header files from letterhead
    letterhead_word = letterhead_dir / "word"
    pandoc_word = pandoc_dir / "word"
    
    # Copy header*.xml files
    for header_file in letterhead_word.glob("header*.xml"):
        shutil.copy(header_file, pandoc_word / header_file.name)
    
    # Copy footer*.xml files
    for footer_file in letterhead_word.glob("footer*.xml"):
        shutil.copy(footer_file, pandoc_word / footer_file.name)
    
    # Copy header relationships (for logo images)
    letterhead_rels = letterhead_word / "_rels"
    pandoc_rels = pandoc_word / "_rels"
    pandoc_rels.mkdir(exist_ok=True)
    
    for rels_file in letterhead_rels.glob("header*.xml.rels"):
        shutil.copy(rels_file, pandoc_rels / rels_file.name)
    
    # Copy media folder (contains logo images)
    letterhead_media = letterhead_word / "media"
    pandoc_media = pandoc_word / "media"
    
    if letterhead_media.exists():
        if pandoc_media.exists():
            # Copy files that don't exist
            for media_file in letterhead_media.iterdir():
                if not (pandoc_media / media_file.name).exists():
                    shutil.copy(media_file, pandoc_media / media_file.name)
        else:
            shutil.copytree(letterhead_media, pandoc_media)
    
    # Copy fonts folder (for embedded fonts)
    letterhead_fonts = letterhead_word / "fonts"
    pandoc_fonts = pandoc_word / "fonts"
    
    if letterhead_fonts.exists() and not pandoc_fonts.exists():
        shutil.copytree(letterhead_fonts, pandoc_fonts)
    
    # Update [Content_Types].xml to include header/footer/media types
    update_content_types(pandoc_dir, letterhead_dir)
    
    # Repack as docx
    output_docx = temp_dir / "final.docx"
    with zipfile.ZipFile(output_docx, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root_dir, dirs, files in os.walk(pandoc_dir):
            for file in files:
                file_path = Path(root_dir) / file
                arcname = file_path.relative_to(pandoc_dir)
                zipf.write(file_path, arcname)
    
    return output_docx


def update_content_types(pandoc_dir: Path, letterhead_dir: Path):
    """Update [Content_Types].xml to include any missing content types from letterhead."""
    pandoc_ct = pandoc_dir / "[Content_Types].xml"
    letterhead_ct = letterhead_dir / "[Content_Types].xml"
    
    if not pandoc_ct.exists() or not letterhead_ct.exists():
        return
    
    # Read both files as text (avoid ElementTree namespace issues)
    with open(pandoc_ct, 'r', encoding='utf-8') as f:
        pandoc_content = f.read()
    
    with open(letterhead_ct, 'r', encoding='utf-8') as f:
        letterhead_content = f.read()
    
    # Extract content type entries from letterhead
    import re
    
    # Find all Default and Override entries
    default_pattern = r'<Default[^>]+/>'
    override_pattern = r'<Override[^>]+/>'
    
    letterhead_defaults = set(re.findall(default_pattern, letterhead_content))
    letterhead_overrides = set(re.findall(override_pattern, letterhead_content))
    
    # Find insertion point (before </Types>)
    types_end = '</Types>'
    if types_end not in pandoc_content:
        return
    
    # Add missing entries
    entries_to_add = []
    
    for default in letterhead_defaults:
        # Check if this Extension is already in pandoc
        ext_match = re.search(r'Extension="([^"]+)"', default)
        if ext_match:
            ext = ext_match.group(1)
            if f'Extension="{ext}"' not in pandoc_content:
                entries_to_add.append(default)
    
    for override in letterhead_overrides:
        # Check if this PartName is already in pandoc
        part_match = re.search(r'PartName="([^"]+)"', override)
        if part_match:
            part = part_match.group(1)
            if f'PartName="{part}"' not in pandoc_content:
                entries_to_add.append(override)
    
    if entries_to_add:
        # Insert before </Types>
        insertion = '\n'.join(entries_to_add)
        pandoc_content = pandoc_content.replace(types_end, f'{insertion}\n{types_end}')
        
        with open(pandoc_ct, 'w', encoding='utf-8') as f:
            f.write(pandoc_content)


def convert_docx_to_pdf(docx_path: Path, pdf_path: Path) -> Dict[str, Any]:
    """Convert a DOCX file to PDF using LibreOffice."""
    result = {"success": False, "error": None}
    
    try:
        cmd = [
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', str(pdf_path.parent),
            str(docx_path)
        ]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # LibreOffice names the output based on input filename
        expected_pdf = pdf_path.parent / f"{docx_path.stem}.pdf"
        
        if expected_pdf.exists():
            if expected_pdf != pdf_path:
                shutil.move(expected_pdf, pdf_path)
            result["success"] = True
        else:
            result["error"] = f"LibreOffice did not produce PDF. stderr: {process.stderr}"
    
    except FileNotFoundError:
        result["error"] = "LibreOffice (soffice) not found. Install with: brew install --cask libreoffice"
    except subprocess.TimeoutExpired:
        result["error"] = "PDF conversion timed out"
    except Exception as e:
        result["error"] = str(e)
    
    return result


# Command-line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate document on letterhead from markdown")
    parser.add_argument("markdown_file", help="Path to markdown file")
    parser.add_argument("output_file", help="Output .docx path")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF conversion")
    parser.add_argument("--template", help="Custom letterhead template path")
    parser.add_argument("--replace", action="append", nargs=2, metavar=("KEY", "VALUE"),
                        help="Placeholder replacement (can be used multiple times)")
    
    args = parser.parse_args()
    
    replacements = {}
    if args.replace:
        for key, value in args.replace:
            replacements[key] = value
    
    result = generate_letterhead_document(
        markdown_path=args.markdown_file,
        output_path=args.output_file,
        convert_to_pdf=not args.no_pdf,
        letterhead_template=args.template,
        replacements=replacements
    )
    
    print(json.dumps(result, indent=2))
