#!/usr/bin/env python3
"""
Template Identifier for Document Generation

Identifies which template a document is based on by:
1. YAML frontmatter (for Markdown files)
2. Content markers (specific text patterns in the document)
3. Filename pattern matching
4. Registry lookup

Usage:
    from template_identifier import identify_template
    
    template_info = identify_template("/path/to/document.md")
    # Returns: {
    #     "template_id": "demand_letter",
    #     "template_type": "markdown",
    #     "identification_method": "yaml_frontmatter",
    #     "registry_entry": { ... full template registry entry ... }
    # }
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zipfile import ZipFile

import yaml


# Base paths
CLAUDE_DOCS = Path(os.environ.get("CLAUDE_DOCS", os.environ.get("ROSCOE_ROOT", str(Path(__file__).resolve().parents[2]))))
TEMPLATES_DIR = CLAUDE_DOCS / "templates"
REGISTRY_PATH = TEMPLATES_DIR / "template_registry.json"


def load_template_registry() -> Dict:
    """Load the template registry."""
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"templates": []}


def extract_yaml_frontmatter(content: str) -> Optional[Dict]:
    """
    Extract YAML frontmatter from markdown content.
    
    Args:
        content: File content as string
    
    Returns:
        Parsed YAML dict or None if no frontmatter
    """
    yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if yaml_match:
        try:
            return yaml.safe_load(yaml_match.group(1))
        except yaml.YAMLError:
            pass
    return None


def extract_docx_content(docx_path: Path) -> str:
    """
    Extract text content from a DOCX file for pattern matching.
    
    Args:
        docx_path: Path to the DOCX file
    
    Returns:
        Extracted text content (first 5000 chars for efficiency)
    """
    try:
        with ZipFile(docx_path, 'r') as zip_ref:
            if 'word/document.xml' in zip_ref.namelist():
                xml_content = zip_ref.read('word/document.xml').decode('utf-8')
                # Simple text extraction - remove XML tags
                text = re.sub(r'<[^>]+>', ' ', xml_content)
                text = re.sub(r'\s+', ' ', text)
                return text[:5000]  # First 5000 chars should be enough
    except Exception:
        pass
    return ""


def extract_docx_custom_properties(docx_path: Path) -> Dict[str, str]:
    """
    Extract custom document properties from DOCX.
    
    Some templates may have a TemplateID custom property.
    """
    properties = {}
    try:
        with ZipFile(docx_path, 'r') as zip_ref:
            if 'docProps/custom.xml' in zip_ref.namelist():
                xml_content = zip_ref.read('docProps/custom.xml').decode('utf-8')
                # Simple extraction of property names and values
                matches = re.findall(
                    r'<vt:lpwstr>([^<]+)</vt:lpwstr>.*?name="([^"]+)"',
                    xml_content,
                    re.DOTALL
                )
                for value, name in matches:
                    properties[name] = value
    except Exception:
        pass
    return properties


def match_content_markers(content: str, registry: Dict) -> Optional[Dict]:
    """
    Try to identify template by content markers defined in registry.
    
    Args:
        content: Document text content
        registry: Template registry
    
    Returns:
        Matching template entry or None
    """
    for template in registry.get("templates", []):
        identification = template.get("identification", {})
        if identification.get("method") == "content_marker":
            marker = identification.get("marker", "")
            if marker and marker.lower() in content.lower():
                return template
    return None


def match_filename(filename: str, registry: Dict) -> Optional[Dict]:
    """
    Try to identify template by filename pattern.
    
    Args:
        filename: Document filename
        registry: Template registry
    
    Returns:
        Matching template entry or None
    """
    filename_lower = filename.lower()
    
    for template in registry.get("templates", []):
        # Check source_file match
        source_file = template.get("source_file", "")
        if source_file and source_file.lower() in filename_lower:
            return template
        
        # Check filename patterns
        identification = template.get("identification", {})
        if identification.get("method") == "filename_pattern":
            pattern = identification.get("pattern", "")
            if pattern and re.search(pattern, filename, re.IGNORECASE):
                return template
    
    # Try fuzzy matching on template names
    for template in registry.get("templates", []):
        template_name = template.get("name", "").lower()
        template_id = template.get("id", "").lower()
        
        # Check if key words from template name appear in filename
        name_words = set(re.findall(r'\w+', template_name))
        filename_words = set(re.findall(r'\w+', filename_lower))
        
        # If significant overlap, consider it a match
        if len(name_words & filename_words) >= 2:
            return template
        
        # Check template ID in filename
        if template_id and template_id.replace('_', ' ') in filename_lower.replace('_', ' '):
            return template
    
    return None


def identify_template(file_path: str) -> Dict[str, Any]:
    """
    Identify which template a document is based on.
    
    Tries identification in order:
    1. YAML frontmatter (for .md files)
    2. Custom document properties (for .docx files)
    3. Content markers
    4. Filename pattern matching
    
    Args:
        file_path: Path to the document
    
    Returns:
        Dict with:
            - template_id: str - The template identifier
            - template_type: str - Type (markdown, docx, pdf_form)
            - identification_method: str - How it was identified
            - registry_entry: dict|None - Full registry entry if found
            - confidence: str - high, medium, low
    """
    path = Path(file_path)
    result = {
        "template_id": None,
        "template_type": None,
        "identification_method": None,
        "registry_entry": None,
        "confidence": "low",
        "file_extension": path.suffix.lower(),
    }
    
    registry = load_template_registry()
    
    # Determine base type from extension
    if path.suffix.lower() == '.md':
        result["template_type"] = "markdown"
    elif path.suffix.lower() == '.docx':
        result["template_type"] = "docx"
    elif path.suffix.lower() == '.pdf':
        result["template_type"] = "pdf_form"
    
    # Method 1: YAML frontmatter (Markdown files)
    if path.suffix.lower() == '.md' and path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = extract_yaml_frontmatter(content)
        if frontmatter and frontmatter.get("template_id"):
            result["template_id"] = frontmatter["template_id"]
            result["identification_method"] = "yaml_frontmatter"
            result["confidence"] = "high"
            
            # Find matching registry entry
            for template in registry.get("templates", []):
                if template.get("id") == result["template_id"]:
                    result["registry_entry"] = template
                    break
            
            return result
    
    # Method 2: Custom document properties (DOCX files)
    if path.suffix.lower() == '.docx' and path.exists():
        properties = extract_docx_custom_properties(path)
        if properties.get("TemplateID"):
            result["template_id"] = properties["TemplateID"]
            result["identification_method"] = "custom_property"
            result["confidence"] = "high"
            
            for template in registry.get("templates", []):
                if template.get("id") == result["template_id"]:
                    result["registry_entry"] = template
                    break
            
            return result
    
    # Method 3: Content markers
    content = ""
    if path.suffix.lower() == '.md' and path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()[:5000]
    elif path.suffix.lower() == '.docx' and path.exists():
        content = extract_docx_content(path)
    
    if content:
        template = match_content_markers(content, registry)
        if template:
            result["template_id"] = template.get("id")
            result["identification_method"] = "content_marker"
            result["registry_entry"] = template
            result["confidence"] = "medium"
            return result
    
    # Method 4: Filename pattern matching
    template = match_filename(path.name, registry)
    if template:
        result["template_id"] = template.get("id")
        result["identification_method"] = "filename_pattern"
        result["registry_entry"] = template
        result["confidence"] = "medium"
        return result
    
    # Method 5: Infer from file extension and path
    # If still no match, try to infer from common patterns
    filename_lower = path.name.lower()
    
    if 'lor' in filename_lower and 'pip' in filename_lower:
        result["template_id"] = "lor_pip"
        result["identification_method"] = "filename_inference"
        result["confidence"] = "low"
    elif 'lor' in filename_lower and 'bi' in filename_lower:
        result["template_id"] = "lor_bi"
        result["identification_method"] = "filename_inference"
        result["confidence"] = "low"
    elif 'demand' in filename_lower:
        result["template_id"] = "demand_letter"
        result["identification_method"] = "filename_inference"
        result["confidence"] = "low"
    elif 'complaint' in filename_lower:
        result["template_id"] = "complaint_mva"
        result["identification_method"] = "filename_inference"
        result["confidence"] = "low"
    elif 'lien' in filename_lower and 'request' in filename_lower:
        result["template_id"] = "lien_request"
        result["identification_method"] = "filename_inference"
        result["confidence"] = "low"
    elif 'medical' in filename_lower and 'record' in filename_lower:
        result["template_id"] = "medical_record_request"
        result["identification_method"] = "filename_inference"
        result["confidence"] = "low"
    
    # Try to find registry entry for inferred ID
    if result["template_id"]:
        for template in registry.get("templates", []):
            if template.get("id") == result["template_id"]:
                result["registry_entry"] = template
                break
    
    return result


def get_template_by_id(template_id: str) -> Optional[Dict]:
    """
    Get a template entry from the registry by ID.
    
    Args:
        template_id: The template identifier
    
    Returns:
        Template registry entry or None
    """
    registry = load_template_registry()
    for template in registry.get("templates", []):
        if template.get("id") == template_id:
            return template
    return None


def list_templates(template_type: str = None) -> List[Dict]:
    """
    List all templates, optionally filtered by type.
    
    Args:
        template_type: Filter by type (markdown, docx, pdf_form)
    
    Returns:
        List of template entries
    """
    registry = load_template_registry()
    templates = registry.get("templates", [])
    
    if template_type:
        templates = [t for t in templates if t.get("type") == template_type]
    
    return templates


# =============================================================================
# CLI for testing
# =============================================================================

def main():
    """Test template identification."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python template_identifier.py <file_path>")
        print("\nOr run with --list to see all templates")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        templates = list_templates()
        print(f"Found {len(templates)} templates:\n")
        for t in templates:
            print(f"  {t.get('id'):30} | {t.get('type'):10} | {t.get('name')}")
        return
    
    result = identify_template(sys.argv[1])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

