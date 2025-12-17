#!/usr/bin/env python3
"""
Exhibit Compiler Tool

Takes a demand letter and a manifest of exhibits, then compiles them into a single PDF.

The manifest can be:
- A YAML file with exhibit metadata and paths
- A JSON file with the same structure

Example manifest (YAML):
```yaml
demand_letter: /path/to/demand.pdf
output: /path/to/combined_demand_with_exhibits.pdf
exhibits:
  - letter: A
    description: "Aiken Family Dentistry - Medical Records and Billing"
    path: /path/to/exhibit_a.pdf
  - letter: B
    description: "Baptist Health Medical Group - Medical Records"  
    path: /path/to/exhibit_b.pdf
```

Usage:
    python exhibit_compiler.py manifest.yaml
    python exhibit_compiler.py manifest.json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black


def create_exhibit_cover_page(exhibit_letter: str, description: str, output_path: Path) -> Path:
    """Create a cover page for an exhibit."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    
    # Center the exhibit letter
    c.setFont("Times-Bold", 72)
    c.drawCentredString(width / 2, height / 2 + 50, f"EXHIBIT {exhibit_letter}")
    
    # Add description below
    c.setFont("Times-Roman", 14)
    
    # Word wrap the description if needed
    max_width = width - 2 * inch
    words = description.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if c.stringWidth(test_line, "Times-Roman", 14) < max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    y_pos = height / 2 - 30
    for line in lines:
        c.drawCentredString(width / 2, y_pos, line)
        y_pos -= 20
    
    c.save()
    return output_path


def compile_exhibits(
    demand_letter_path: str,
    exhibits: List[Dict[str, str]],
    output_path: str,
    add_cover_pages: bool = True
) -> Dict[str, Any]:
    """
    Compile demand letter and exhibits into a single PDF.
    
    Args:
        demand_letter_path: Path to the demand letter PDF
        exhibits: List of exhibit dictionaries with keys: letter, description, path
        output_path: Where to save the combined PDF
        add_cover_pages: Whether to add cover pages before each exhibit
    
    Returns:
        Dictionary with status and metadata
    """
    result = {
        "status": "success",
        "output_path": None,
        "page_count": 0,
        "exhibits_included": [],
        "errors": []
    }
    
    writer = PdfWriter()
    
    # Add demand letter
    demand_path = Path(demand_letter_path)
    if not demand_path.exists():
        result["status"] = "error"
        result["errors"].append(f"Demand letter not found: {demand_path}")
        return result
    
    try:
        demand_reader = PdfReader(str(demand_path))
        for page in demand_reader.pages:
            writer.add_page(page)
        result["page_count"] += len(demand_reader.pages)
    except Exception as e:
        result["errors"].append(f"Error reading demand letter: {e}")
    
    # Add each exhibit
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    
    for exhibit in exhibits:
        exhibit_letter = exhibit.get("letter", "?")
        description = exhibit.get("description", "")
        exhibit_path = Path(exhibit.get("path", ""))
        
        if not exhibit_path.exists():
            result["errors"].append(f"Exhibit {exhibit_letter} not found: {exhibit_path}")
            continue
        
        # Add cover page if requested
        if add_cover_pages:
            cover_path = temp_dir / f"cover_{exhibit_letter}.pdf"
            create_exhibit_cover_page(exhibit_letter, description, cover_path)
            
            try:
                cover_reader = PdfReader(str(cover_path))
                for page in cover_reader.pages:
                    writer.add_page(page)
                result["page_count"] += len(cover_reader.pages)
            except Exception as e:
                result["errors"].append(f"Error adding cover for Exhibit {exhibit_letter}: {e}")
        
        # Add exhibit pages
        try:
            exhibit_reader = PdfReader(str(exhibit_path))
            for page in exhibit_reader.pages:
                writer.add_page(page)
            result["page_count"] += len(exhibit_reader.pages)
            result["exhibits_included"].append({
                "letter": exhibit_letter,
                "description": description,
                "pages": len(exhibit_reader.pages)
            })
        except Exception as e:
            result["errors"].append(f"Error reading Exhibit {exhibit_letter}: {e}")
    
    # Write output
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "wb") as f:
            writer.write(f)
        
        result["output_path"] = str(output_file)
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"Error writing output: {e}")
    
    # Clean up temp files
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return result


def load_manifest(manifest_path: str) -> Dict[str, Any]:
    """Load a YAML or JSON manifest file."""
    path = Path(manifest_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if path.suffix.lower() in ['.yaml', '.yml']:
        if not HAS_YAML:
            raise ImportError("PyYAML required for YAML manifests. Install with: pip install pyyaml")
        return yaml.safe_load(content)
    else:
        return json.loads(content)


def main():
    parser = argparse.ArgumentParser(description="Compile demand letter with exhibits into single PDF")
    parser.add_argument("manifest", help="Path to YAML or JSON manifest file")
    parser.add_argument("--no-covers", action="store_true", help="Skip exhibit cover pages")
    parser.add_argument("--output", "-o", help="Override output path from manifest")
    
    args = parser.parse_args()
    
    try:
        manifest = load_manifest(args.manifest)
    except Exception as e:
        print(f"Error loading manifest: {e}", file=sys.stderr)
        sys.exit(1)
    
    demand_letter = manifest.get("demand_letter")
    exhibits = manifest.get("exhibits", [])
    output_path = args.output or manifest.get("output", "combined_demand.pdf")
    
    if not demand_letter:
        print("Error: manifest must specify 'demand_letter' path", file=sys.stderr)
        sys.exit(1)
    
    result = compile_exhibits(
        demand_letter_path=demand_letter,
        exhibits=exhibits,
        output_path=output_path,
        add_cover_pages=not args.no_covers
    )
    
    print(json.dumps(result, indent=2))
    
    if result["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()

