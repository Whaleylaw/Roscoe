#!/usr/bin/env python3
"""Check the format of the Baptist Health PDF."""

import pdfplumber

pdf_path = "/Volumes/X10 Pro/Roscoe/Find a Location - Baptist Health.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    print("\n" + "=" * 60)
    print("First page text sample:")
    print("=" * 60)

    # Get first page
    first_page = pdf.pages[0]
    text = first_page.extract_text()

    if text:
        # Print first 2000 characters
        print(text[:2000])
    else:
        print("No text extracted from first page")

    print("\n" + "=" * 60)
    print("Page 5 text sample:")
    print("=" * 60)

    # Get page 5
    if len(pdf.pages) >= 5:
        page5 = pdf.pages[4]
        text = page5.extract_text()

        if text:
            print(text[:2000])
        else:
            print("No text extracted from page 5")
