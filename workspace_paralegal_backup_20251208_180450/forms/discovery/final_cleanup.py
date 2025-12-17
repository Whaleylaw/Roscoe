#!/usr/bin/env python3
"""
Final cleanup of templates - more conservative approach.
Only replace names in specific contexts, preserve legal terminology.
"""

import re
from pathlib import Path

def final_cleanup(content):
    """Final cleanup with conservative replacements."""
    
    # Restore common legal terms that were incorrectly replaced
    # Restore case numbers pattern
    content = re.sub(r'\[PARTY_NAME\] NO\.', 'CASE NO.', content, flags=re.IGNORECASE)
    content = re.sub(r'\[PARTY_NAME\]:\s*\_', 'DIVISION: _____', content, flags=re.IGNORECASE)
    
    # Restore KRS citations
    content = re.sub(r'\[PARTY_NAME\]\s+304\.39', 'KRS 304.39', content)
    
    # Restore WHEREFORE
    content = re.sub(r'\[PARTY_NAME\],\s+Plaintiff demand', 'WHEREFORE, Plaintiff demand', content, flags=re.IGNORECASE)
    
    # Restore USPS
    content = re.sub(r'Serve via \[PARTY_NAME\] Certified Mail', 'Serve via USPS Certified Mail', content, flags=re.IGNORECASE)
    
    # Fix date placeholders that got double-bracketed
    content = re.sub(r'\[\[PARTY_NAME\]\]', '[DATE]', content)
    
    # Fix phone placeholders
    content = re.sub(r'T:\s*\[\[PARTY_NAME\]\]', 'T: [PHONE]', content)
    content = re.sub(r'F:\s*\[\[PARTY_NAME\]\]', 'F: [PHONE]', content)
    
    # Fix city placeholders
    content = re.sub(r'\[\[PARTY_NAME\]\],\s+Kentucky', '[CITY], Kentucky', content)
    
    # Replace [PARTY_NAME] in "Plaintiff, [PARTY_NAME]" contexts with [PLAINTIFF_NAME]
    content = re.sub(r'Plaintiffs?,?\s+\[PARTY_NAME\]', r'Plaintiff, [PLAINTIFF_NAME]', content, flags=re.IGNORECASE)
    
    # Replace [PARTY_NAME] in "Defendant, [PARTY_NAME]" contexts with [DEFENDANT_NAME]
    content = re.sub(r'Defendants?,?\s+\[PARTY_NAME\]', r'Defendant, [DEFENDANT_NAME]', content, flags=re.IGNORECASE)
    
    # Fix "Comes the Plaintiff, [PARTY_NAME]"
    content = re.sub(r'Comes (?:now|the)? (?:the )?Plaintiffs?,?\s+\[PARTY_NAME\]', r'Comes the Plaintiff, [PLAINTIFF_NAME]', content, flags=re.IGNORECASE)
    
    # Fix "against the Defendant, [PARTY_NAME]"
    content = re.sub(r'against (?:the )?Defendants?,?\s+\[PARTY_NAME\]', r'against the Defendant, [DEFENDANT_NAME]', content, flags=re.IGNORECASE)
    
    return content

def process_templates():
    """Process all template files."""
    current_dir = Path('/Volumes/X10 Pro/Roscoe/forms/discovery')
    template_files = list(current_dir.glob('*_Template.md'))
    
    print(f"Found {len(template_files)} template files to clean up")
    
    for template_file in template_files:
        print(f"\nCleaning: {template_file.name}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned_content = final_cleanup(content)
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"  Cleaned: {template_file.name}")

if __name__ == '__main__':
    process_templates()

