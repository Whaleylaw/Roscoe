#!/usr/bin/env python3
"""
Comprehensive attorney scraper for 12 Kentucky law firms.
Site-specific extraction logic for each firm.
"""

import json
import re
import time
from playwright.sync_api import sync_playwright

def extract_email(text):
    """Extract email from text."""
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return match.group(0) if match else ""

def extract_phone(text):
    """Extract phone from text."""
    match = re.search(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
    return match.group(0) if match else ""

def scrape_firm(page, firm_name, url, scraper_func):
    """Generic wrapper for firm scraping."""
    print(f"\n{firm_name}:")
    print(f"  URL: {url}")

    try:
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(4)

        attorneys = scraper_func(page, firm_name)
        print(f"  ✓ Found {len(attorneys)} attorneys")
        return attorneys

    except Exception as e:
        print(f"  ✗ Error: {str(e)[:100]}")
        return []

# Site-specific scrapers

def scrape_dilbeck_myers(page, firm_name):
    """Dilbeck & Myers scraper."""
    attorneys = []
    text = page.inner_text('body')
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # Find attorney names and contact info
    for i, line in enumerate(lines):
        # Look for attorney names (usually followed by credentials)
        if re.match(r'^[A-Z][a-z]+\s+(?:[A-Z]\.?\s+)?[A-Z][a-z]+(?:,?\s+Esq\.)?$', line):
            name = line.replace(', Esq.', '').strip()

            # Look ahead for email/phone
            email = ""
            phone = ""
            for j in range(i+1, min(i+10, len(lines))):
                if '@' in lines[j]:
                    email = extract_email(lines[j])
                if re.search(r'\d{3}', lines[j]):
                    phone = extract_phone(lines[j])

            attorneys.append({
                "name": name,
                "firm_name": firm_name,
                "email": email,
                "phone": phone
            })

    return attorneys

def scrape_attorney_list_generic(page, firm_name):
    """Generic scraper for sites with attorney listings."""
    attorneys = []

    # Get all text content
    text = page.inner_text('body')

    # Find all emails on the page
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

    # For each email, try to find associated name
    for email in emails:
        # Find the position of this email in the text
        email_pos = text.find(email)

        # Look backwards up to 500 chars for a name
        search_text = text[max(0, email_pos-500):email_pos]
        lines = search_text.split('\n')

        # Look for a name in recent lines
        name = ""
        for line in reversed(lines[-10:]):
            line = line.strip()
            # Match typical name patterns
            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z]+){1,2}(?:,?\s+(?:Jr\.|Sr\.|III|Esq\.))?$', line):
                name = re.sub(r',?\s+Esq\.', '', line).strip()
                break

        # Look for phone near email
        search_area = text[max(0, email_pos-300):min(len(text), email_pos+300)]
        phone = extract_phone(search_area)

        if name:
            attorneys.append({
                "name": name,
                "firm_name": firm_name,
                "email": email,
                "phone": phone
            })

    return attorneys

def scrape_kopka_law(page, firm_name):
    """Kopka Law - filter by Kentucky."""
    # The page has a state filter - need to interact with it
    attorneys = []

    try:
        # Try to find and click Kentucky filter if it exists
        page.wait_for_selector('body', timeout=5000)

        # Use generic scraper but look for "Kentucky" in text near names
        text = page.inner_text('body')

        # Find all emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

        # Check if "Kentucky" or "KY" appears on the page
        for email in emails:
            email_pos = text.find(email)
            context = text[max(0, email_pos-600):min(len(text), email_pos+300)]

            # Only include if Kentucky is mentioned in context
            if 'Kentucky' in context or ' KY ' in context or ', KY' in context:
                # Find name
                search_before = text[max(0, email_pos-400):email_pos]
                lines = search_before.split('\n')

                name = ""
                for line in reversed(lines[-8:]):
                    line = line.strip()
                    if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z]+){1,2}', line):
                        name = line
                        break

                phone = extract_phone(context)

                if name:
                    attorneys.append({
                        "name": name,
                        "firm_name": firm_name,
                        "email": email,
                        "phone": phone
                    })

    except Exception as e:
        pass

    return attorneys

def main():
    all_attorneys = []

    print("Scraping attorneys from 12 Kentucky law firms...")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Scrape each firm
        all_attorneys.extend(scrape_firm(browser, "Dilbeck & Myers",
                                         "https://www.dilbeckandmyers.com/#portfolio",
                                         scrape_dilbeck_myers))

        all_attorneys.extend(scrape_firm(browser, "Smith & Hoskins",
                                         "https://www.smith-hoskins.com/practice",
                                         scrape_attorney_list_generic))

        all_attorneys.extend(scrape_firm(browser, "Kopka Pinkus Dolin",
                                         "https://www.kopkalaw.com/all-attorneys/",
                                         scrape_kopka_law))

        all_attorneys.extend(scrape_firm(browser, "SBM Law",
                                         "https://www.sbmkylaw.com/attorneys/",
                                         scrape_attorney_list_generic))

        all_attorneys.extend(scrape_firm(browser, "BSG Law",
                                         "https://bsg-law.com/meet-our-attorneys/",
                                         scrape_attorney_list_generic))

        # Burke & Neal - individual pages
        page = browser.new_page()
        for url in ["https://www.burkeneal.com/kevin-burke", "https://www.burkeneal.com/jamie-neal"]:
            all_attorneys.extend(scrape_firm(page, "Burke & Neal", url, scrape_attorney_list_generic))
        page.close()

        all_attorneys.extend(scrape_firm(browser, "SON Legal",
                                         "https://www.sonlegal.com/about/",
                                         scrape_attorney_list_generic))

        all_attorneys.extend(scrape_firm(browser, "CBM Law",
                                         "https://cbmlaw.net/",
                                         scrape_attorney_list_generic))

        all_attorneys.extend(scrape_firm(browser, "PPOA Law",
                                         "https://ppoalaw.com/attorneys/",
                                         scrape_attorney_list_generic))

        all_attorneys.extend(scrape_firm(browser, "BDB Law",
                                         "https://bdblawky.com/firm-overview/",
                                         scrape_attorney_list_generic))

        all_attorneys.extend(scrape_firm(browser, "WHT Law",
                                         "https://whtlaw.com/about/",
                                         scrape_attorney_list_generic))

        all_attorneys.extend(scrape_firm(browser, "Sturgill Turner",
                                         "https://www.sturgillturner.com/our-attorneys",
                                         scrape_attorney_list_generic))

        browser.close()

    print("\n" + "=" * 60)
    print(f"Total attorneys scraped: {len(all_attorneys)}")

    # Remove duplicates
    seen = set()
    unique_attorneys = []

    for att in all_attorneys:
        key = f"{att['name'].lower()}|{att.get('email', '').lower()}"
        if key not in seen:
            seen.add(key)
            unique_attorneys.append(att)

    print(f"Unique attorneys: {len(unique_attorneys)}")

    # Save
    output_file = "/Volumes/X10 Pro/Roscoe/json-files/scraped_attorneys_raw.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_attorneys, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to: {output_file}")

    # Show sample
    print("\nFirst 15 attorneys:")
    for i, att in enumerate(unique_attorneys[:15], 1):
        print(f"\n{i}. {att['name']}")
        print(f"   Firm: {att['firm_name']}")
        print(f"   Email: {att.get('email', '(not found)')}")
        print(f"   Phone: {att.get('phone', '(not found)')}")

if __name__ == "__main__":
    main()
