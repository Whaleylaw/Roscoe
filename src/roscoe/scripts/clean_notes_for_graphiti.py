#!/usr/bin/env python3
"""
Clean notes.json for Graphiti episode ingestion.

This script:
1. Filters out useless system notes
2. Extracts real authors from Filevine Integration notes
3. Cleans HTML artifacts and encoding issues
4. Simplifies fax/email confirmations
5. Outputs clean notes ready for Graphiti

Usage:
    python clean_notes_for_graphiti.py /path/to/notes.json [--output /path/to/clean_notes.json]
"""

import json
import re
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime


# Patterns to SKIP entirely (no useful information)
SKIP_PATTERNS = [
    r'^Insurance Company Added$',
    r'^New Medical Provider Added$',
    r'^Phase Change:',
    r'^Medical Provider Updated$',
    r'^Insurance Updated$',
    r'^Lien (Added|Updated)$',
    r'^Expense (Added|Updated)$',
    r'^Contact (Added|Updated)$',
]

# Authors that indicate system-generated notes (need special handling)
SYSTEM_AUTHORS = [
    'Filevine Integration',
    'Filevine System',
    'Fuel Digital RingCentral Integration Service Account',
    '',
]

# Patterns to extract real author from note content
AUTHOR_EXTRACTION_PATTERNS = [
    r'__Written by:__\s*([A-Za-z\s]+)',
    r'From:\s*([A-Za-z\s]+)\s*\[',
    r'Caller Info:.*\nCaller Name:\s*([A-Za-z\s]+)',
]

# HTML/encoding artifacts to clean
HTML_CLEANUP = [
    (r'\?+', ''),  # Remove ? sequences (encoding artifacts)
    (r'\s{3,}', ' '),  # Collapse multiple spaces
    (r'\n{3,}', '\n\n'),  # Collapse multiple newlines
    (r'\[image:.*?\]', ''),  # Remove image placeholders
    (r'Copyright \d{4}.*$', '', re.MULTILINE),  # Remove copyright footers
    (r'This email was sent to you at.*$', '', re.MULTILINE),  # Remove email footers
    (r'By subscribing to and/or using RingCentral.*$', '', re.MULTILINE | re.DOTALL),
]

# Email signature patterns to trim
SIGNATURE_PATTERNS = [
    r'\n\nRespectfully,\n.*$',
    r'\n\nThank you.*\n\n.*@whaleylawfirm\.com$',
    r'\n\n-{5,}.*$',  # Divider lines
]

# Hashtags to preserve as categories
CATEGORY_TAGS = {
    '#Inotes': 'insurance_note',
    '#status': 'status_change',
    '#missedcall': 'missed_call',
    '#outboundcall': 'outbound_call',
    '#cc': 'client_contact',
    '#MRnotes': 'medical_records',
}


def should_skip(note: dict) -> tuple[bool, str]:
    """Check if note should be skipped entirely."""
    text = note.get('note', '').strip()
    
    # Skip empty notes
    if not text:
        return True, "empty"
    
    # Skip very short system notes
    if len(text) < 30:
        for pattern in SKIP_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True, f"system_pattern: {pattern}"
    
    # Skip pure phase changes (we track these differently)
    if text.startswith('Phase Change:'):
        return True, "phase_change"
    
    # Skip notes that are just "X Added" or "X Updated"
    if re.match(r'^[A-Za-z\s]+ (Added|Updated)$', text):
        return True, "generic_added_updated"
    
    return False, ""


def extract_real_author(note: dict) -> str:
    """Extract real author from note content if system-generated."""
    author = note.get('author_name', '').strip()
    text = note.get('note', '')
    
    # If author is a real person, keep it
    if author and author not in SYSTEM_AUTHORS:
        return author
    
    # Try to extract from note content
    for pattern in AUTHOR_EXTRACTION_PATTERNS:
        match = re.search(pattern, text)
        if match:
            extracted = match.group(1).strip()
            # Validate it looks like a name
            if extracted and len(extracted) > 2 and not extracted.startswith('mailto'):
                return extracted
    
    # Check for "logged at" pattern (RingCentral)
    match = re.search(r'call (?:from|for)\s+([a-z]+\s+[a-z]+)\s+was logged', text, re.IGNORECASE)
    if match:
        return match.group(1).title()
    
    return author or "System"


def clean_note_text(text: str) -> str:
    """Clean HTML artifacts and normalize text."""
    cleaned = text
    
    # Apply HTML cleanup patterns
    for pattern_tuple in HTML_CLEANUP:
        if len(pattern_tuple) == 2:
            pattern, replacement = pattern_tuple
            flags = 0
        else:
            pattern, replacement, flags = pattern_tuple
        cleaned = re.sub(pattern, replacement, cleaned, flags=flags)
    
    # Trim email signatures
    for pattern in SIGNATURE_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL)
    
    # Clean up markdown-style formatting that's not useful
    cleaned = re.sub(r'__([^_]+)__', r'\1', cleaned)  # __bold__ -> bold
    
    # Clean up email formatting
    cleaned = re.sub(r'\[([^\]]+)\]\(mailto:[^\)]+\)', r'\1', cleaned)  # [email](mailto:x) -> email
    
    # Normalize whitespace
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned


def extract_categories(text: str) -> list[str]:
    """Extract category tags from note text."""
    categories = []
    for tag, category in CATEGORY_TAGS.items():
        if tag in text:
            categories.append(category)
    return categories


def simplify_fax_confirmation(text: str) -> Optional[str]:
    """Simplify RingCentral fax confirmations."""
    if 'Fax Message Transmission Result' not in text and 'Fax Transmission Result' not in text:
        return None
    
    # Extract recipient and result
    recipient_match = re.search(r'to \+?1?\s*\(?(\d{3})\)?\s*(\d{3})[\s-]?(\d{4})', text)
    result_match = re.search(r'(Sent|Failed|Pending)', text)
    file_match = re.search(r'File Name.*?Result\s*\n([^\n]+\.pdf)\s+(Success|Failed)', text)
    
    if recipient_match and result_match:
        phone = f"({recipient_match.group(1)}) {recipient_match.group(2)}-{recipient_match.group(3)}"
        result = result_match.group(1)
        
        if file_match:
            return f"Fax sent to {phone}: {file_match.group(1)} - {file_match.group(2)}"
        return f"Fax sent to {phone} - {result}"
    
    return None


def simplify_email_confirmation(text: str) -> Optional[str]:
    """Simplify email auto-reply confirmations."""
    if "We've Received Your Email" not in text and "Email received" not in text:
        return None
    
    # Extract claim number if present
    claim_match = re.search(r'Claim[:\s#]*(\w+)', text)
    company_match = re.search(r'From:\s*([A-Za-z\s]+)\s*<', text) or re.search(r'\[image:\s*([A-Za-z]+)\]', text)
    
    claim = claim_match.group(1) if claim_match else "unknown"
    company = company_match.group(1).strip() if company_match else "Insurance Company"
    
    return f"{company} confirmed receipt of email for claim {claim}"


def process_note(note: dict) -> Optional[dict]:
    """Process a single note, returning cleaned version or None if should skip."""
    # Check if should skip
    skip, reason = should_skip(note)
    if skip:
        return None
    
    text = note.get('note', '')
    
    # Try to simplify fax confirmations
    simplified = simplify_fax_confirmation(text)
    if simplified:
        text = simplified
    else:
        # Try to simplify email confirmations
        simplified = simplify_email_confirmation(text)
        if simplified:
            text = simplified
        else:
            # Regular cleanup
            text = clean_note_text(text)
    
    # Skip if cleaned text is too short
    if len(text) < 20:
        return None
    
    # Extract real author
    author = extract_real_author(note)
    
    # Extract categories
    categories = extract_categories(note.get('note', ''))
    
    # Build cleaned note
    cleaned = {
        'id': note.get('id'),
        'date': note.get('last_activity'),
        'time': note.get('time'),
        'author': author,
        'note': text,
        'categories': categories,
        'project_name': note.get('project_name'),
    }
    
    # Preserve related UUIDs if present
    for key in ['related_insurance_uuid', 'related_medical_provider_id', 'related_lien_uuid', 'related_expense_uuid']:
        if note.get(key):
            cleaned[key] = note[key]
    
    return cleaned


def process_notes_file(input_path: str, output_path: Optional[str] = None) -> dict:
    """Process entire notes file and return statistics."""
    with open(input_path) as f:
        notes = json.load(f)
    
    stats = {
        'total': len(notes),
        'kept': 0,
        'skipped': 0,
        'skip_reasons': {},
    }
    
    cleaned_notes = []
    
    for note in notes:
        skip, reason = should_skip(note)
        if skip:
            stats['skipped'] += 1
            stats['skip_reasons'][reason] = stats['skip_reasons'].get(reason, 0) + 1
            continue
        
        cleaned = process_note(note)
        if cleaned:
            cleaned_notes.append(cleaned)
            stats['kept'] += 1
        else:
            stats['skipped'] += 1
            stats['skip_reasons']['too_short_after_clean'] = stats['skip_reasons'].get('too_short_after_clean', 0) + 1
    
    stats['cleaned_notes'] = cleaned_notes
    
    # Write output if path provided
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(cleaned_notes, f, indent=2)
        print(f"Wrote {len(cleaned_notes)} cleaned notes to {output_path}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(description='Clean notes.json for Graphiti ingestion')
    parser.add_argument('input', help='Path to notes.json')
    parser.add_argument('--output', '-o', help='Output path for cleaned notes')
    parser.add_argument('--stats-only', action='store_true', help='Only show statistics, no output')
    parser.add_argument('--sample', type=int, default=0, help='Show N sample cleaned notes')
    
    args = parser.parse_args()
    
    stats = process_notes_file(args.input, None if args.stats_only else args.output)
    
    print(f"\n=== CLEANUP STATISTICS ===")
    print(f"Total notes:   {stats['total']}")
    print(f"Kept:          {stats['kept']} ({stats['kept']/stats['total']*100:.1f}%)")
    print(f"Skipped:       {stats['skipped']} ({stats['skipped']/stats['total']*100:.1f}%)")
    
    print(f"\n=== SKIP REASONS ===")
    for reason, count in sorted(stats['skip_reasons'].items(), key=lambda x: -x[1]):
        print(f"  {count:3d}x  {reason}")
    
    if args.sample > 0:
        print(f"\n=== SAMPLE CLEANED NOTES ===")
        for note in stats['cleaned_notes'][:args.sample]:
            print(f"\n--- ID {note['id']} ({note['date']}) by {note['author']} ---")
            print(f"Categories: {note['categories']}")
            print(note['note'][:500])
            if len(note['note']) > 500:
                print("...")


if __name__ == '__main__':
    main()
