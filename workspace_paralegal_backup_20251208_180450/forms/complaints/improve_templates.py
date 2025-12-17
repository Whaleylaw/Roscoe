#!/usr/bin/env python3
"""
Improve existing templates by replacing remaining specific names with placeholders.
"""

import re
from pathlib import Path

def improve_template(content):
    """Replace remaining specific names with placeholders."""
    
    # Replace names after PLAINTIFF/DEFENDANT in headers
    content = re.sub(
        r'(PLAINTIFF|DEFENDANT)\s*\n\s*>\s*\n\s*>\s*([A-Z][A-Z\s&\.\']+?)(?=\s+PLAINTIFF|\s+DEFENDANT|\s+v\.|$)',
        r'\1\n>\n> [\1_NAME]',
        content,
        flags=re.MULTILINE | re.IGNORECASE
    )
    
    # Replace names in "Comes the Plaintiff, NAME" patterns
    content = re.sub(
        r'(Comes (?:now|the)? (?:the )?(?:Plaintiff|Defendant|Plaintiffs|Defendants)),\s+([A-Z][A-Z\s&\.\']+?)(?=\s+by|\s+and|\s+for|\s+states|$)',
        r'\1, [PARTY_NAME]',
        content,
        flags=re.IGNORECASE
    )
    
    # Replace specific person names in various contexts
    # Pattern: "Plaintiff, NAME" or "Defendant, NAME"
    content = re.sub(
        r'(Plaintiff|Defendant|Plaintiffs|Defendants),?\s+([A-Z][A-Z\s&\.\']+?)(?=\s+was|\s+is|\s+are|\s+had|\s+operated|\s+failed|,|\s+by|\s+and|\.|$)',
        r'\1, [PARTY_NAME]',
        content,
        flags=re.IGNORECASE
    )
    
    # Replace company names (with INC, LLC, CORP, etc.)
    content = re.sub(
        r'\b([A-Z][A-Z\s&\.\']+?)\s+(?:INC\.?|LLC\.?|CORP\.?|CORPORATION|COMPANY|HOLDINGS|GROUP|LOGISTICS|EXPRESS|CARGO|TRUCKING|RETAIL|SERVICES)\b',
        '[COMPANY_NAME]',
        content
    )
    
    # Replace names in "v." patterns
    content = re.sub(
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+v\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:INC\.?|LLC\.?|CORP\.?))?)\b',
        r'[PLAINTIFF_NAME] v. [DEFENDANT_NAME]',
        content
    )
    
    # Replace all-caps names that appear standalone (likely proper names)
    # But preserve common legal terms
    legal_terms = {
        'PLAINTIFF', 'DEFENDANT', 'COURT', 'KENTUCKY', 'JEFFERSON', 'LOUISVILLE',
        'COMMONWEALTH', 'COUNTY', 'CIRCUIT', 'JUDGE', 'HON', 'ORDER', 'MOTION',
        'COMPLAINT', 'SUMMONS', 'CERTIFICATE', 'SERVICE', 'ESTATE', 'ADMINISTRATOR',
        'COMPLAINT', 'PERSONAL', 'INJURY', 'MOTOR', 'VEHICLE', 'ACCIDENT'
    }
    
    def replace_allcaps(match):
        text = match.group(0)
        # Skip if it's a legal term or very short
        if len(text) < 3 or text.upper() in legal_terms:
            return text
        # Skip if it contains common punctuation that suggests it's not a name
        if any(c in text for c in '.,;:!?'):
            return text
        return '[PARTY_NAME]'
    
    # Replace all-caps words (but be conservative)
    content = re.sub(r'\b([A-Z]{3,}(?:\s+[A-Z]{3,})*)\b', replace_allcaps, content)
    
    # Replace specific known names from the documents
    known_names = [
        'Patricia Harrison', 'Sa\'Nyah Harrison', 'Maria LeeAnn Robinson',
        'Edwinna Eley', 'Macy\'s Retail Holdings', 'ANTONIO KENNEDY',
        'ABDULKADIR MOHAMED', 'ANTONION KENNEDY'
    ]
    
    for name in known_names:
        content = re.sub(re.escape(name), '[PARTY_NAME]', content, flags=re.IGNORECASE)
    
    return content

def process_templates():
    """Process all template files."""
    current_dir = Path('/Volumes/X10 Pro/Roscoe/forms/complaints')
    template_files = list(current_dir.glob('*_Template.md'))
    
    print(f"Found {len(template_files)} template files to improve")
    
    for template_file in template_files:
        print(f"\nImproving: {template_file.name}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        improved_content = improve_template(content)
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(improved_content)
        
        print(f"  Updated: {template_file.name}")

if __name__ == '__main__':
    process_templates()

