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
    legal_replacements = {
        '[PARTY_NAME] NO.': 'CASE NO.',
        '[PARTY_NAME]:': 'DIVISION:',
        '[PARTY_NAME] Certified Mail': 'USPS Certified Mail',
        '[PARTY_NAME] 304.39-062(b)': 'KRS 304.39-062(b)',
        '[PARTY_NAME], Plaintiff demand': 'WHEREFORE, Plaintiff demand',
        '[[PARTY_NAME]]': '[DATE]',  # Dates that got replaced
        '[[PARTY_NAME]], Kentucky': '[CITY], Kentucky',
        'T: [[PARTY_NAME]]': 'T: [PHONE]',
        'F: [[PARTY_NAME]]': 'F: [PHONE]',
        '[PARTY_NAME], [PARTY_NAME].': '[COMPANY_NAME].',
        '[PARTY_NAME] I:': 'COUNT I:',
        '[PARTY_NAME] OF': 'NEGLIGENCE OF',
        '[PARTY_NAME] TO': 'FACTUAL AND JURISDICTIONAL AVERMENTS TO',
        '[PARTY_NAME]': '[PLAINTIFF_NAME]',  # In header contexts
    }
    
    # But we need to be smarter - only replace in specific contexts
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
    
    # Fix COUNT I pattern
    content = re.sub(r'\[PARTY_NAME\]\s+I:\s*\[PARTY_NAME\]', 'COUNT I: NEGLIGENCE', content, flags=re.IGNORECASE)
    
    # Fix section headers
    content = re.sub(r'\[PARTY_NAME\]\s+TO\s+\[PARTY_NAME\]', 'FACTUAL AND JURISDICTIONAL AVERMENTS TO ALL COUNTS', content, flags=re.IGNORECASE)
    
    # Fix company names that got split
    content = re.sub(r'\[COMPANY_NAME\]\s+\[PARTY_NAME\],\s+\[PARTY_NAME\]\.', '[COMPANY_NAME].', content)
    
    # In header sections, replace [PARTY_NAME] with more specific placeholders
    # Pattern: lines that are just [PARTY_NAME] and likely represent plaintiff/defendant names
    lines = content.split('\n')
    result_lines = []
    in_header = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detect header section
        if 'CASE NO' in stripped.upper() or 'DIVISION' in stripped.upper():
            in_header = True
        
        if in_header and stripped == '[PARTY_NAME]' and i < len(lines) - 1:
            # Check if next line is "v." or "DEFENDANT" or "PLAINTIFF"
            next_stripped = lines[i+1].strip() if i+1 < len(lines) else ''
            prev_stripped = lines[i-1].strip() if i > 0 else ''
            
            if 'PLAINTIFF' in prev_stripped.upper() or 'v.' in next_stripped.lower():
                result_lines.append(line.replace('[PARTY_NAME]', '[PLAINTIFF_NAME]'))
            elif 'DEFENDANT' in prev_stripped.upper() or 'DEFENDANT' in next_stripped.upper():
                result_lines.append(line.replace('[PARTY_NAME]', '[DEFENDANT_NAME]'))
            else:
                result_lines.append(line)
        else:
            result_lines.append(line)
        
        # Exit header section
        if 'COMPLAINT' in stripped.upper() and '**' in stripped:
            in_header = False
    
    content = '\n'.join(result_lines)
    
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
    current_dir = Path('/Volumes/X10 Pro/Roscoe/forms/complaints')
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

