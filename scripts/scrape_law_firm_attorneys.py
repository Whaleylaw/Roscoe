#!/usr/bin/env python3
"""
Scrape attorney information from 12 Kentucky law firm websites.
Extracts: name, email, phone, firm name, practice areas, and bio.
"""

import json
import re
import time
from playwright.sync_api import sync_playwright

# Law firm websites to scrape
LAW_FIRMS = {
    "Dilbeck & Myers": {
        "url": "https://www.dilbeckandmyers.com/#portfolio",
        "type": "portfolio"
    },
    "Smith & Hoskins": {
        "url": "https://www.smith-hoskins.com/practice",
        "type": "practice_page"
    },
    "Kopka Pinkus Dolin": {
        "url": "https://www.kopkalaw.com/all-attorneys/",
        "filter": "Kentucky"
    },
    "SBM Law": {
        "url": "https://www.sbmkylaw.com/attorneys/",
        "type": "attorney_list"
    },
    "BSG Law": {
        "url": "https://bsg-law.com/meet-our-attorneys/",
        "type": "attorney_list"
    },
    "Burke & Neal": {
        "urls": [
            "https://www.burkeneal.com/kevin-burke",
            "https://www.burkeneal.com/jamie-neal"
        ],
        "type": "individual_pages"
    },
    "SON Legal": {
        "url": "https://www.sonlegal.com/about/",
        "type": "about_page"
    },
    "CBM Law": {
        "url": "https://cbmlaw.net/",
        "type": "homepage"
    },
    "PPOA Law": {
        "url": "https://ppoalaw.com/attorneys/",
        "type": "attorney_list"
    },
    "BDB Law": {
        "url": "https://bdblawky.com/firm-overview/",
        "type": "firm_overview"
    },
    "WHT Law": {
        "url": "https://whtlaw.com/about/",
        "type": "about_page"
    },
    "Sturgill Turner": {
        "url": "https://www.sturgillturner.com/our-attorneys",
        "type": "attorney_list"
    }
}

def extract_email(text):
    """Extract email address from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ""

def extract_phone(text):
    """Extract phone number from text."""
    # Try various phone patterns
    patterns = [
        r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # (502) 555-1234 or 502-555-1234
        r'\d{3}\.\d{3}\.\d{4}',                   # 502.555.1234
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)

    return ""

def scrape_generic_attorney_list(page, firm_name):
    """Generic scraper for attorney list pages."""
    attorneys = []

    print(f"    Waiting for page to load...")
    time.sleep(3)

    # Try to find attorney cards/sections
    # Common patterns: links to attorney pages, attorney names in headings, etc.

    # Method 1: Find all links that might lead to attorney pages
    attorney_links = []

    # Look for common patterns in URLs
    page_content = page.content()

    # Extract attorney profile links
    link_patterns = [
        r'href="([^"]*(?:attorney|lawyer|team|people|staff)[^"]*)"',
        r'href="([^"]*\/(?:attorneys?|team|people|staff)\/[^"]*)"'
    ]

    for pattern in link_patterns:
        matches = re.findall(pattern, page_content, re.IGNORECASE)
        attorney_links.extend(matches)

    # Remove duplicates
    attorney_links = list(set(attorney_links))

    # Also try to extract attorney info directly from the current page
    text = page.inner_text('body')

    # Look for email addresses (attorneys usually have emails on pages)
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

    # Extract names near emails
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if '@' in line:
            # Look at surrounding lines for a name
            for offset in [-3, -2, -1, 0, 1]:
                if 0 <= i + offset < len(lines):
                    check_line = lines[i + offset].strip()
                    # Check if this looks like a name (2-4 words, capitalized)
                    name_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z.]+){1,3})$', check_line)
                    if name_match:
                        name = name_match.group(1)
                        email = extract_email(line)
                        phone = extract_phone(text[max(0, text.find(check_line)-200):text.find(check_line)+200])

                        attorneys.append({
                            "name": name,
                            "email": email,
                            "phone": phone,
                            "firm_name": firm_name,
                            "url": page.url
                        })
                        break

    return attorneys

def scrape_law_firm(browser, firm_name, firm_config):
    """Scrape attorneys from a single law firm."""
    attorneys = []

    print(f"\n{firm_name}:")

    try:
        page = browser.new_page()

        # Handle single URL or multiple URLs
        urls = firm_config.get('urls', [firm_config.get('url')])
        if not isinstance(urls, list):
            urls = [urls]

        for url in urls:
            print(f"  Loading {url}...")

            try:
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)

                # Use generic scraper
                firm_attorneys = scrape_generic_attorney_list(page, firm_name)

                print(f"    Found {len(firm_attorneys)} attorneys")
                attorneys.extend(firm_attorneys)

            except Exception as e:
                print(f"    Error loading page: {str(e)[:80]}")

        page.close()

    except Exception as e:
        print(f"  Error: {str(e)[:100]}")

    return attorneys

def main():
    all_attorneys = []

    print("Scraping attorneys from 12 Kentucky law firms...")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for firm_name, firm_config in LAW_FIRMS.items():
            firm_attorneys = scrape_law_firm(browser, firm_name, firm_config)
            all_attorneys.extend(firm_attorneys)

        browser.close()

    print("\n" + "=" * 60)
    print(f"Total attorneys scraped: {len(all_attorneys)}")

    # Remove duplicates based on email
    seen_emails = set()
    unique_attorneys = []

    for attorney in all_attorneys:
        email = attorney.get('email', '').lower()
        if email and email not in seen_emails:
            seen_emails.add(email)
            unique_attorneys.append(attorney)
        elif not email:
            # Include attorneys without emails
            unique_attorneys.append(attorney)

    print(f"Unique attorneys: {len(unique_attorneys)}")

    # Save raw scraped data
    output_file = "/Volumes/X10 Pro/Roscoe/json-files/scraped_attorneys_raw.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_attorneys, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to: {output_file}")

    # Show samples
    if unique_attorneys:
        print("\nFirst 10 attorneys:")
        for i, attorney in enumerate(unique_attorneys[:10], 1):
            print(f"\n{i}. {attorney['name']}")
            print(f"   Firm: {attorney['firm_name']}")
            print(f"   Email: {attorney.get('email', '(not found)')}")
            print(f"   Phone: {attorney.get('phone', '(not found)')}")

if __name__ == "__main__":
    main()
