"""
Medical Chronology Tools

Python utilities for generating professional medical chronologies with:
- Research cache for medical term definitions with citations
- PDF generation with formatted tables
- Clickable page references
- Treatment gap identification
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_CACHE_PATH = "Resources/medical_research_cache.json"


# ============================================================================
# RESEARCH CACHE FUNCTIONS
# ============================================================================

def load_research_cache(cache_path: str = DEFAULT_CACHE_PATH) -> dict:
    """Load the medical research cache."""
    default_cache = {
        "terms": {},
        "medications": {},
        "procedures": {},
        "anatomy": {}
    }
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default_cache
    
    return default_cache


def save_research_cache(cache: dict, cache_path: str = DEFAULT_CACHE_PATH) -> str:
    """Save the medical research cache."""
    cache_dir = os.path.dirname(cache_path)
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
    
    with open(cache_path, 'w') as f:
        json.dump(cache, f, indent=2)
    
    return cache_path


def add_researched_term(
    term: str,
    definition: str,
    source_name: str,
    source_url: str,
    category: str = "terms",
    cache_path: str = DEFAULT_CACHE_PATH
) -> dict:
    """
    Add a researched term to the cache with citation.
    
    Args:
        term: The medical term
        definition: Researched definition
        source_name: Name of source (e.g., "Mayo Clinic")
        source_url: URL where definition was found
        category: One of "terms", "medications", "procedures", "anatomy"
        cache_path: Path to cache file
        
    Returns:
        dict: The term entry that was added
    """
    cache = load_research_cache(cache_path)
    
    term_key = term.lower().replace(" ", "_")
    
    entry = {
        "term": term,
        "definition": definition,
        "source": source_name,
        "url": source_url,
        "researched_date": datetime.now().strftime("%Y-%m-%d"),
    }
    
    if category not in cache:
        cache[category] = {}
    
    cache[category][term_key] = entry
    save_research_cache(cache, cache_path)
    
    return entry


def get_cached_definition(
    term: str,
    category: str = None,
    max_age_days: int = 30,
    cache_path: str = DEFAULT_CACHE_PATH
) -> Optional[dict]:
    """
    Get a cached definition if available and not stale.
    
    Args:
        term: Term to look up
        category: Specific category to search, or None for all
        max_age_days: Maximum age of cached entry in days
        cache_path: Path to cache file
        
    Returns:
        dict or None: Cached entry with definition and citation
    """
    cache = load_research_cache(cache_path)
    term_key = term.lower().replace(" ", "_")
    
    categories = [category] if category else ["terms", "medications", "procedures", "anatomy"]
    
    for cat in categories:
        if cat in cache and term_key in cache[cat]:
            entry = cache[cat][term_key]
            
            if "researched_date" in entry:
                researched = datetime.strptime(entry["researched_date"], "%Y-%m-%d")
                age = (datetime.now() - researched).days
                
                if age <= max_age_days:
                    return entry
    
    return None


# ============================================================================
# STANDARD ABBREVIATIONS (No research needed)
# ============================================================================

STANDARD_ABBREVIATIONS = {
    "ROM": "Range of Motion",
    "DVA": "Distance Visual Acuity",
    "CT": "Computed Tomography",
    "MRI": "Magnetic Resonance Imaging",
    "ER": "Emergency Room",
    "ED": "Emergency Department",
    "PCP": "Primary Care Provider",
    "PT": "Physical Therapy",
    "OT": "Occupational Therapy",
    "Rx": "Prescription",
    "Dx": "Diagnosis",
    "Hx": "History",
    "WNL": "Within Normal Limits",
    "PRN": "As Needed",
    "BID": "Twice Daily",
    "TID": "Three Times Daily",
    "QID": "Four Times Daily",
    "HPI": "History of Present Illness",
    "ROS": "Review of Systems",
    "PE": "Physical Examination",
    "MMI": "Maximum Medical Improvement",
    "IME": "Independent Medical Evaluation",
    "FCE": "Functional Capacity Evaluation",
    "EMG": "Electromyography",
    "NCV": "Nerve Conduction Velocity",
}


def is_standard_abbreviation(term: str) -> bool:
    """Check if term is a standard abbreviation."""
    return term.upper() in STANDARD_ABBREVIATIONS


def get_abbreviation_expansion(abbrev: str) -> Optional[str]:
    """Get expansion for standard abbreviation."""
    return STANDARD_ABBREVIATIONS.get(abbrev.upper())


# ============================================================================
# CHRONOLOGY ENTRY FUNCTIONS
# ============================================================================

def create_chronology_entry(
    date: str,
    provider: str,
    medical_facts: str,
    page_number: str,
    source_file: str = None,
    comments: List[dict] = None
) -> dict:
    """
    Create a structured chronology entry.
    
    Args:
        date: Date of service (MM.DD.YYYY format)
        provider: Provider name with specialty/facility
        medical_facts: Detailed medical facts text
        page_number: Bates number or page reference
        source_file: Path to source document
        comments: List of comment dicts
        
    Returns:
        dict: Structured chronology entry
    """
    return {
        "date": date,
        "provider": provider,
        "medical_facts": medical_facts,
        "page_number": page_number,
        "source_file": source_file,
        "comments": comments or []
    }


def create_comment(
    comment_type: str,
    text: str,
    term: str = None,
    source: str = None,
    url: str = None
) -> dict:
    """
    Create a comment dict for chronology entry.
    
    Args:
        comment_type: One of "definition", "red_flag", "causation", "author_note"
        text: The comment text
        term: Medical term (for definitions)
        source: Source name (for definitions)
        url: Source URL (for definitions)
        
    Returns:
        dict: Comment structure
    """
    comment = {
        "type": comment_type,
        "text": text
    }
    
    if term:
        comment["term"] = term
    if source:
        comment["source"] = source
    if url:
        comment["url"] = url
    
    return comment


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def suggest_definitions(
    medical_facts: str,
    cache_path: str = DEFAULT_CACHE_PATH
) -> dict:
    """
    Analyze medical text to identify terms needing definition.
    
    Returns:
        dict: {
            'cached': [(term, definition_dict), ...],
            'needs_research': [term, ...],
            'abbreviations': [(abbrev, expansion), ...]
        }
    """
    import re
    
    result = {
        'cached': [],
        'needs_research': [],
        'abbreviations': []
    }
    
    # Find potential medical terms
    potential_terms = set()
    
    # Capitalized terms
    capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', medical_facts)
    potential_terms.update(capitalized)
    
    # Medical suffixes
    suffix_terms = re.findall(
        r'\b\w+(?:itis|osis|ectomy|plasty|otomy|opathy|algia|emia|penia|trophy)\b',
        medical_facts,
        re.IGNORECASE
    )
    potential_terms.update(suffix_terms)
    
    # Abbreviations
    abbreviations = re.findall(r'\b[A-Z]{2,6}\b', medical_facts)
    
    # Check abbreviations
    for abbrev in abbreviations:
        if abbrev in STANDARD_ABBREVIATIONS:
            result['abbreviations'].append((abbrev, STANDARD_ABBREVIATIONS[abbrev]))
    
    # Check terms
    for term in potential_terms:
        if term.upper() in STANDARD_ABBREVIATIONS:
            continue
        
        cached = get_cached_definition(term, cache_path=cache_path)
        if cached:
            result['cached'].append((term, cached))
        else:
            result['needs_research'].append(term)
    
    return result


def identify_treatment_gaps(
    entries: List[dict],
    gap_threshold_days: int = 30
) -> List[dict]:
    """
    Identify gaps in treatment timeline.
    
    Args:
        entries: Sorted list of chronology entries
        gap_threshold_days: Minimum days to flag as gap
        
    Returns:
        list: List of gap info dicts
    """
    gaps = []
    date_format = "%m.%d.%Y"
    
    for i in range(1, len(entries)):
        try:
            prev_date = datetime.strptime(entries[i-1]['date'], date_format)
            curr_date = datetime.strptime(entries[i]['date'], date_format)
            
            delta = (curr_date - prev_date).days
            
            if delta >= gap_threshold_days:
                gaps.append({
                    "start_date": entries[i-1]['date'],
                    "end_date": entries[i]['date'],
                    "days": delta,
                    "after_entry_index": i - 1
                })
        except (ValueError, KeyError):
            continue
    
    return gaps


def sort_entries_by_date(entries: List[dict]) -> List[dict]:
    """Sort chronology entries by date."""
    def parse_date(entry):
        try:
            return datetime.strptime(entry.get('date', ''), "%m.%d.%Y")
        except (ValueError, KeyError):
            return datetime.max
    
    return sorted(entries, key=parse_date)


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def save_chronology_data(
    entries: List[dict],
    client_info: dict,
    output_path: str
) -> str:
    """
    Save chronology data as JSON.
    
    Args:
        entries: List of chronology entries
        client_info: Client information dict
        output_path: Where to save JSON file
        
    Returns:
        str: Path to saved file
    """
    data = {
        "client_info": client_info,
        "entries": entries,
        "generated_at": datetime.now().isoformat(),
        "entry_count": len(entries)
    }
    
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return output_path


def load_chronology_data(json_path: str) -> dict:
    """Load previously saved chronology data."""
    with open(json_path, 'r') as f:
        return json.load(f)


# ============================================================================
# PDF GENERATION (requires reportlab)
# ============================================================================

def generate_chronology_pdf(
    output_path: str,
    client_info: dict,
    entries: List[dict],
    firm_name: str = "Law Firm",
    source_records_pdf: str = None
) -> str:
    """
    Generate a formatted medical chronology PDF.
    
    Note: Requires reportlab library. Install with: pip install reportlab
    
    Args:
        output_path: Where to save PDF
        client_info: {name, dob, date_of_injury}
        entries: List of chronology entries
        firm_name: For disclaimer
        source_records_pdf: Path to source records (for page references)
        
    Returns:
        str: Path to generated PDF
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
    except ImportError:
        raise ImportError("reportlab required. Install with: pip install reportlab")
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Header
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    elements.append(Paragraph(f"<b>Name:</b> {client_info.get('name', '')}", header_style))
    elements.append(Paragraph(f"<b>Date of Birth:</b> {client_info.get('dob', '')}", header_style))
    elements.append(Paragraph(f"<b>Date of Injury:</b> {client_info.get('date_of_injury', '')}", header_style))
    elements.append(Spacer(1, 12))
    
    # Disclaimer
    disclaimer = f"This chronology is for attorney use only and is work product of {firm_name}."
    elements.append(Paragraph(f"<i>{disclaimer}</i>", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Table headers
    headers = ['Date', 'Provider', 'Medical Facts', 'Comments', 'Page #']
    
    # Build table data
    table_data = [headers]
    
    for entry in entries:
        # Format comments
        comments_text = ""
        for comment in entry.get('comments', []):
            if comment.get('type') == 'definition':
                term = comment.get('term', '')
                text = comment.get('text', '')
                source = comment.get('source', '')
                comments_text += f"<b>{term}</b>: {text}\n<i>Source: {source}</i>\n\n"
            else:
                comments_text += f"{comment.get('text', '')}\n\n"
        
        row = [
            entry.get('date', ''),
            entry.get('provider', ''),
            entry.get('medical_facts', '')[:500] + "..." if len(entry.get('medical_facts', '')) > 500 else entry.get('medical_facts', ''),
            comments_text.strip(),
            entry.get('page_number', '')
        ]
        table_data.append(row)
    
    # Create table
    col_widths = [0.8*inch, 1.2*inch, 2.5*inch, 2*inch, 0.7*inch]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
    ]))
    
    elements.append(table)
    
    doc.build(elements)
    return output_path


def merge_chronology_with_records(
    chronology_pdf: str,
    records_pdf: str,
    output_path: str
) -> str:
    """
    Merge chronology PDF with source records.
    
    Note: Requires PyPDF2 library. Install with: pip install PyPDF2
    
    Args:
        chronology_pdf: Path to generated chronology
        records_pdf: Path to source medical records
        output_path: Where to save combined PDF
        
    Returns:
        str: Path to combined PDF
    """
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        raise ImportError("PyPDF2 required. Install with: pip install PyPDF2")
    
    merger = PdfMerger()
    merger.append(chronology_pdf)
    merger.append(records_pdf)
    
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    merger.write(output_path)
    merger.close()
    
    return output_path


# ============================================================================
# MAIN WORKFLOW FUNCTION
# ============================================================================

def create_medical_chronology(
    client_info: dict,
    entries: List[dict],
    output_dir: str,
    firm_name: str = "Law Firm",
    source_records_pdf: str = None,
    cache_path: str = DEFAULT_CACHE_PATH
) -> dict:
    """
    Complete workflow to create medical chronology.
    
    IMPORTANT: Before calling, ensure all medical terms have been researched
    and added to the cache using add_researched_term().
    
    Args:
        client_info: {name, dob, date_of_injury}
        entries: List of chronology entries
        output_dir: Directory to save outputs
        firm_name: Name for disclaimer
        source_records_pdf: Optional path to source records PDF
        cache_path: Path to research cache
        
    Returns:
        dict: Paths to all generated files
    """
    os.makedirs(output_dir, exist_ok=True)
    
    safe_name = client_info.get('name', 'Unknown').replace(' ', '_').replace(',', '')
    sorted_entries = sort_entries_by_date(entries)
    
    # Track terms needing research
    all_needs_research = []
    for entry in sorted_entries:
        analysis = suggest_definitions(entry.get('medical_facts', ''), cache_path=cache_path)
        all_needs_research.extend(analysis.get('needs_research', []))
    
    unique_needs_research = list(set(all_needs_research))
    
    # Identify treatment gaps
    gaps = identify_treatment_gaps(sorted_entries)
    
    # Generate outputs
    outputs = {}
    
    # Save JSON data
    json_path = os.path.join(output_dir, f"{safe_name}_chronology_data.json")
    save_chronology_data(sorted_entries, client_info, json_path)
    outputs['json'] = json_path
    
    # Generate PDF
    pdf_path = os.path.join(output_dir, f"{safe_name}_Medical_Chronology.pdf")
    try:
        generate_chronology_pdf(pdf_path, client_info, sorted_entries, firm_name, source_records_pdf)
        outputs['pdf'] = pdf_path
    except ImportError as e:
        outputs['pdf_error'] = str(e)
    
    # Merge with records if provided
    if source_records_pdf and os.path.exists(source_records_pdf) and 'pdf' in outputs:
        combined_path = os.path.join(output_dir, f"{safe_name}_Chronology_and_Records.pdf")
        try:
            merge_chronology_with_records(outputs['pdf'], source_records_pdf, combined_path)
            outputs['combined'] = combined_path
        except ImportError as e:
            outputs['combined_error'] = str(e)
    
    outputs['treatment_gaps'] = gaps
    outputs['terms_needing_research'] = unique_needs_research
    
    if unique_needs_research:
        outputs['warning'] = (
            f"ATTENTION: {len(unique_needs_research)} terms need research. "
            f"Use internet_search and add_researched_term() before finalizing."
        )
    
    return outputs

