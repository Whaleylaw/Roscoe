#!/usr/bin/env python3
"""
Convert Word documents to Markdown templates by replacing specific information with placeholders.
"""

import os
import re
import subprocess
from pathlib import Path

def convert_docx_to_markdown(docx_path):
    """Convert a .docx file to Markdown using pandoc."""
    try:
        result = subprocess.run(
            ['pandoc', str(docx_path), '-t', 'markdown', '--wrap=none'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error converting {docx_path}: {e}")
        return None

def create_template(markdown_content, original_filename):
    """Replace specific information with placeholders to create a template."""
    if not markdown_content:
        return None
    
    content = markdown_content
    
    # Common patterns to replace with placeholders
    replacements = [
        # Dates - various formats
        (r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '[DATE]'),
        (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', '[DATE]'),
        (r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', '[DATE]'),
        
        # Case numbers - various formats
        (r'\b\d{2}-CI-\d{5}\b', '[CASE_NUMBER]'),
        (r'\b\d{2}-CV-\d{5}\b', '[CASE_NUMBER]'),
        (r'Case No\.?\s*[:\-]?\s*\d{2}-CI-\d{5}', '[CASE_NUMBER]'),
        (r'Civil Action No\.?\s*[:\-]?\s*\d{2}-CI-\d{5}', '[CASE_NUMBER]'),
        
        # Phone numbers
        (r'\(?\d{3}\)?\s*-?\s*\d{3}\s*-?\s*\d{4}\b', '[PHONE]'),
        (r'\d{3}\.\d{3}\.\d{4}\b', '[PHONE]'),
        
        # Email addresses
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
        
        # Zip codes
        (r'\b\d{5}(-\d{4})?\b', '[ZIP_CODE]'),
        
        # Common law firm names (keep structure but make generic)
        (r'Whaley Law Firm', '[LAW_FIRM_NAME]'),
        (r'The Whaley Law Firm', '[LAW_FIRM_NAME]'),
        
        # Common attorney names
        (r'Aaron G\.?\s*Whaley', '[ATTORNEY_NAME]'),
        (r'Aaron Whaley', '[ATTORNEY_NAME]'),
        
        # Addresses - street addresses
        (r'\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Boulevard|Blvd|Drive|Dr|Court|Ct|Circle|Cir|Way|Parkway|Pkwy)[\s,]*', '[STREET_ADDRESS]'),
        
        # City names (common Kentucky cities)
        (r'\b(Louisville|Lexington|Frankfort|Bowling Green|Owensboro|Covington|Hopkinsville|Richmond|Florence|Georgetown|Henderson|Elizabethtown|Paducah|Madisonville|Ashland|Nicholasville|Jeffersontown|Frankfort|Murray|Fort Thomas|Shively|Newport|St\.?\s*Matthews|Fort Campbell|Danville|Glasgow|Bardstown|Middlesborough|Mayfield|Princeton|Somerset|Fort Wright|Campbellsville|La Grange|Lebanon|Pikeville|Radcliff|Mount Washington|Harrodsburg|Corbin|London|Maysville|Morehead|Paris|Prestonsburg|Russellville|Shelbyville|Villa Hills|Williamsburg|Winchester)\b,?\s*KY', '[CITY], Kentucky'),
        
        # Specific case names - replace with placeholders
        # This is tricky - we'll look for common patterns like "Estate of", "v.", etc.
        (r'Estate of [A-Z]\.[A-Z]\.', 'Estate of [DECEDENT_NAME]'),
        (r'Estate of [A-Z][a-z]+\s+[A-Z][a-z]+', 'Estate of [DECEDENT_NAME]'),
        
        # Bar numbers
        (r'\(\d{5}\)', '([BAR_NUMBER])'),
        
        # Specific years (2022, 2023, 2024, 2025)
        (r'\b(202[2-5])\b', '[YEAR]'),
    ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # Replace names that appear after PLAINTIFF/DEFENDANT labels
    # Pattern: PLAINTIFF\n> [NAME] or DEFENDANT\n> [NAME]
    content = re.sub(r'(PLAINTIFF|DEFENDANT)\s*\n\s*>\s*\n\s*>\s*([A-Z][A-Z\s&\.\']+?)(?=\s+PLAINTIFF|\s+DEFENDANT|\s+v\.|$)', 
                     r'\1\n>\n> [\1_NAME]', content, flags=re.MULTILINE | re.IGNORECASE)
    
    # Replace names in "Comes the Plaintiff, [NAME]" patterns
    content = re.sub(r'(Comes (?:now|the)? (?:the )?(?:Plaintiff|Defendant|Plaintiffs|Defendants)),\s+([A-Z][A-Z\s&\.\']+?)(?=\s+by|\s+and|\s+for|\s+states|$)', 
                     r'\1, [PARTY_NAME]', content, flags=re.IGNORECASE)
    
    # Replace names after "Plaintiff, [NAME]" or "Defendant, [NAME]" in paragraphs
    content = re.sub(r'(Plaintiff|Defendant|Plaintiffs|Defendants),?\s+([A-Z][A-Z\s&\.\']+?)(?=\s+was|\s+is|\s+are|\s+had|\s+operated|\s+failed|,|\s+by|\s+and|\.|$)', 
                     r'\1, [PARTY_NAME]', content, flags=re.IGNORECASE)
    
    # Replace company/corporation names (all caps with INC, LLC, etc.)
    content = re.sub(r'\b([A-Z][A-Z\s&\.\']+?)\s+(?:INC\.?|LLC\.?|CORP\.?|CORPORATION|COMPANY|HOLDINGS|GROUP|LOGISTICS|EXPRESS|CARGO|TRUCKING|RETAIL)\b', 
                     '[COMPANY_NAME]', content)
    
    # Replace specific person names (capitalized first and last names)
    # Be careful not to replace common words
    common_words = {'Plaintiff', 'Defendant', 'Court', 'Kentucky', 'Jefferson', 'Louisville', 
                    'Commonwealth', 'County', 'Circuit', 'Judge', 'Hon', 'Order', 'Motion',
                    'Complaint', 'Summons', 'Certificate', 'Service', 'Estate', 'Administrator'}
    
    # Replace names in "v." patterns more carefully
    content = re.sub(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:INC\.?|LLC\.?|CORP\.?))?)\b',
                     r'[PLAINTIFF_NAME] v. [DEFENDANT_NAME]', content)
    
    # Replace remaining all-caps names (likely proper names)
    # But skip if it's a common legal term
    def replace_name(match):
        name = match.group(0)
        if name.upper() not in [w.upper() for w in common_words]:
            return '[PARTY_NAME]'
        return name
    
    # Replace all-caps words that might be names (but be conservative)
    content = re.sub(r'\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)\b', replace_name, content)
    
    return content

def process_all_docx_files():
    """Process all .docx files in the current directory."""
    current_dir = Path('/Volumes/X10 Pro/Roscoe/forms/complaints')
    docx_files = list(current_dir.glob('*.docx'))
    
    print(f"Found {len(docx_files)} .docx files to process")
    
    for docx_file in docx_files:
        print(f"\nProcessing: {docx_file.name}")
        
        # Convert to Markdown
        markdown_content = convert_docx_to_markdown(docx_file)
        
        if not markdown_content:
            print(f"  Failed to convert {docx_file.name}")
            continue
        
        # Create template
        template_content = create_template(markdown_content, docx_file.name)
        
        if not template_content:
            print(f"  Failed to create template for {docx_file.name}")
            continue
        
        # Save template
        template_filename = docx_file.stem + '_Template.md'
        template_path = current_dir / template_filename
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"  Created template: {template_filename}")

if __name__ == '__main__':
    process_all_docx_files()

