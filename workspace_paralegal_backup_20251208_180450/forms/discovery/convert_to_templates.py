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

def convert_doc_to_markdown(doc_path):
    """Convert a .doc file to Markdown using pandoc."""
    try:
        result = subprocess.run(
            ['pandoc', str(doc_path), '-t', 'markdown', '--wrap=none'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error converting {doc_path}: {e}")
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
        
        # Common law firm names
        (r'Whaley Law Firm', '[LAW_FIRM_NAME]'),
        (r'The Whaley Law Firm', '[LAW_FIRM_NAME]'),
        
        # Common attorney names
        (r'Aaron G\.?\s*Whaley', '[ATTORNEY_NAME]'),
        (r'Aaron Whaley', '[ATTORNEY_NAME]'),
        
        # Addresses - street addresses
        (r'\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Boulevard|Blvd|Drive|Dr|Court|Ct|Circle|Cir|Way|Parkway|Pkwy)[\s,]*', '[STREET_ADDRESS]'),
        
        # City names (common Kentucky cities)
        (r'\b(Louisville|Lexington|Frankfort|Bowling Green|Owensboro|Covington|Hopkinsville|Richmond|Florence|Georgetown|Henderson|Elizabethtown|Paducah|Madisonville|Ashland|Nicholasville|Jeffersontown|Frankfort|Murray|Fort Thomas|Shively|Newport|St\.?\s*Matthews|Fort Campbell|Danville|Glasgow|Bardstown|Middlesborough|Mayfield|Princeton|Somerset|Fort Wright|Campbellsville|La Grange|Lebanon|Pikeville|Radcliff|Mount Washington|Harrodsburg|Corbin|London|Maysville|Morehead|Paris|Prestonsburg|Russellville|Shelbyville|Villa Hills|Williamsburg|Winchester)\b,?\s*KY', '[CITY], Kentucky'),
        
        # Specific case names
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
    
    # Replace names in "Comes the Plaintiff, NAME" patterns
    content = re.sub(
        r'(Comes (?:now|the)? (?:the )?(?:Plaintiff|Defendant|Plaintiffs|Defendants)),\s+([A-Z][A-Z\s&\.\']+?)(?=\s+by|\s+and|\s+for|\s+states|$)',
        r'\1, [PARTY_NAME]',
        content,
        flags=re.IGNORECASE
    )
    
    # Replace specific person names in various contexts
    content = re.sub(
        r'(Plaintiff|Defendant|Plaintiffs|Defendants),?\s+([A-Z][A-Z\s&\.\']+?)(?=\s+was|\s+is|\s+are|\s+had|\s+operated|\s+failed|,|\s+by|\s+and|\.|$)',
        r'\1, [PARTY_NAME]',
        content,
        flags=re.IGNORECASE
    )
    
    # Replace company names (with INC, LLC, CORP, etc.)
    content = re.sub(
        r'\b([A-Z][A-Z\s&\.\']+?)\s+(?:INC\.?|LLC\.?|CORP\.?|CORPORATION|COMPANY|HOLDINGS|GROUP|LOGISTICS|EXPRESS|CARGO|TRUCKING|RETAIL|SERVICES|INSURANCE)\b',
        '[COMPANY_NAME]',
        content
    )
    
    # Replace names in "v." patterns
    content = re.sub(
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:INC\.?|LLC\.?|CORP\.?))?)\b',
        r'[PLAINTIFF_NAME] v. [DEFENDANT_NAME]',
        content
    )
    
    return content

def process_all_word_files():
    """Process all .docx and .doc files in the current directory."""
    current_dir = Path('/Volumes/X10 Pro/Roscoe/forms/discovery')
    docx_files = list(current_dir.glob('*.docx'))
    doc_files = list(current_dir.glob('*.doc'))
    all_files = docx_files + doc_files
    
    print(f"Found {len(all_files)} Word files to process ({len(docx_files)} .docx, {len(doc_files)} .doc)")
    
    for word_file in all_files:
        print(f"\nProcessing: {word_file.name}")
        
        # Convert to Markdown
        if word_file.suffix == '.docx':
            markdown_content = convert_docx_to_markdown(word_file)
        else:
            markdown_content = convert_doc_to_markdown(word_file)
        
        if not markdown_content:
            print(f"  Failed to convert {word_file.name}")
            continue
        
        # Create template
        template_content = create_template(markdown_content, word_file.name)
        
        if not template_content:
            print(f"  Failed to create template for {word_file.name}")
            continue
        
        # Save template
        template_filename = word_file.stem + '_Template.md'
        template_path = current_dir / template_filename
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"  Created template: {template_filename}")

if __name__ == '__main__':
    process_all_word_files()

