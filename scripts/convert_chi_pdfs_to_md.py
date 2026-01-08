#!/usr/bin/env python3
"""Convert all CHI PDFs to Markdown files."""

import pdfplumber
import os

base_dir = "/Volumes/X10 Pro/Roscoe"
pdf_files = [f"CHI-{i}.pdf" for i in range(1, 10)]

print("Converting CHI PDFs to Markdown...")
print("=" * 60)

for pdf_file in pdf_files:
    pdf_path = os.path.join(base_dir, pdf_file)
    md_file = pdf_file.replace('.pdf', '.md')
    md_path = os.path.join(base_dir, md_file)

    print(f"\nConverting {pdf_file}...")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"  Total pages: {total_pages}")

            with open(md_path, 'w', encoding='utf-8') as md:
                md.write(f"# {pdf_file} - Provider Locations\n\n")

                for page_num, page in enumerate(pdf.pages, 1):
                    if page_num % 25 == 0:
                        print(f"    Processing page {page_num}/{total_pages}...")

                    text = page.extract_text()
                    if text:
                        md.write(f"## Page {page_num}\n\n")
                        md.write(text)
                        md.write("\n\n---\n\n")

            print(f"  ✓ Saved to {md_file}")

    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")

print("\n" + "=" * 60)
print("Conversion complete!")
