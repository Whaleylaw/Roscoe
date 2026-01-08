#!/usr/bin/env python3
"""Convert Baptist Health PDF to Markdown."""

import pdfplumber

pdf_path = "/Volumes/X10 Pro/Roscoe/Find a Location - Baptist Health.pdf"
md_path = "/Volumes/X10 Pro/Roscoe/baptist_health_locations.md"

print(f"Converting PDF to Markdown...")
print(f"Input: {pdf_path}")
print(f"Output: {md_path}")

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages: {total_pages}")

    with open(md_path, 'w', encoding='utf-8') as md_file:
        md_file.write("# Baptist Health Locations\n\n")

        for page_num, page in enumerate(pdf.pages, 1):
            if page_num % 25 == 0:
                print(f"  Processing page {page_num}/{total_pages}...")

            text = page.extract_text()
            if text:
                md_file.write(f"## Page {page_num}\n\n")
                md_file.write(text)
                md_file.write("\n\n---\n\n")

print(f"\nConversion complete!")
print(f"Markdown file saved to: {md_path}")
