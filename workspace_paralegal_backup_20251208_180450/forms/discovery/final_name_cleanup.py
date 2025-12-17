#!/usr/bin/env python3
"""
Final cleanup to replace remaining specific names with placeholders.
"""

import re
from pathlib import Path

def final_name_cleanup(content):
    """Replace remaining specific names."""
    
    # Replace specific names that appear in documents
    specific_names = [
        'Patricia Harrison', "Sa'nyah Harrison", 'Sa\'Nyah Harrison',
        'Maria Robinson', 'Maria LeeAnn Robinson',
        'Abeba Negussie',
        'Dinsmore & Shohl'
    ]
    
    for name in specific_names:
        # Replace with appropriate placeholder based on context
        if 'Harrison' in name:
            content = re.sub(re.escape(name), '[PLAINTIFF_NAME]', content, flags=re.IGNORECASE)
        elif 'Robinson' in name or 'Maria' in name:
            content = re.sub(re.escape(name), '[DEFENDANT_NAME]', content, flags=re.IGNORECASE)
        elif 'Abeba' in name or 'Negussie' in name:
            content = re.sub(re.escape(name), '[CLIENT_NAME]', content, flags=re.IGNORECASE)
        elif 'Dinsmore' in name:
            content = re.sub(re.escape(name), '[LAW_FIRM_NAME]', content, flags=re.IGNORECASE)
        else:
            content = re.sub(re.escape(name), '[PARTY_NAME]', content, flags=re.IGNORECASE)
    
    # Fix "You/Your" definitions that reference specific names
    content = re.sub(
        r'The terms "you" and "your," as used throughout these interrogatories and requests for production, mean [A-Z][a-z]+ [A-Z][a-z]+,',
        'The terms "you" and "your," as used throughout these interrogatories and requests for production, mean [DEFENDANT_NAME],',
        content
    )
    
    # Fix "Dear [Name]" patterns
    content = re.sub(r'Dear [A-Z][a-z]+,', 'Dear [CLIENT_NAME],', content)
    
    # Fix addresses that got partially replaced
    content = re.sub(r'\[ZIP_CODE\]\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+Drive', '[STREET_ADDRESS]', content)
    
    return content

def process_templates():
    """Process all template files."""
    current_dir = Path('/Volumes/X10 Pro/Roscoe/forms/discovery')
    template_files = list(current_dir.glob('*_Template.md'))
    
    print(f"Found {len(template_files)} template files to clean up")
    
    for template_file in template_files:
        print(f"\nCleaning names in: {template_file.name}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned_content = final_name_cleanup(content)
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"  Cleaned: {template_file.name}")

if __name__ == '__main__':
    process_templates()

