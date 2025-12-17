#!/usr/bin/env python3
"""
KYeCourts Docket Lookup Tool

Automates login and case docket retrieval from Kentucky's eCourts system.
Uses Playwright for browser automation.

Usage:
    python kyecourts_docket.py --county "JEFFERSON" --case-number "25-CI-00133"
    python kyecourts_docket.py --county "FAYETTE" --case-number "24-CI-00456" --output /Reports/case.json

Environment Variables:
    KYECOURTS_USERNAME - KBA number or username
    KYECOURTS_PASSWORD - Account password

Output:
    JSON with case details including parties, documents, events, and images
    Optionally saves full page text to a file

Navigation Flow (discovered via browser exploration):
    1. Login at https://kcoj.kycourts.net/kyecourts/Login
    2. Land on Apps page → Click "Case Search (CourtNet)"
    3. Account Summary page → Click "Continue"
    4. Search page → Select "Search by Case" tab
    5. Select County dropdown, enter Case Number
    6. Click Search → Results list parties
    7. Click case number link → Opens "Case at a Glance" in new tab
    8. Extract all case information from the detail page
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout
except ImportError:
    print(json.dumps({
        "error": "Playwright not installed. Run with execute_python_script_with_browser()",
        "success": False
    }))
    sys.exit(1)


# Configuration - URLs discovered during browser exploration
KYECOURTS_LOGIN_URL = "https://kcoj.kycourts.net/kyecourts/Login"
KYECOURTS_APPS_URL = "https://kcoj.kycourts.net/kyecourts/Apps"
COURTNET_SEARCH_URL = "https://kcoj.kycourts.net/CourtNet/Search/Index"
DEFAULT_TIMEOUT = 30000  # 30 seconds


def get_credentials() -> tuple[str, str]:
    """Get KYeCourts credentials from environment variables."""
    username = os.environ.get("KYECOURTS_USERNAME")
    password = os.environ.get("KYECOURTS_PASSWORD")
    
    if not username or not password:
        raise ValueError(
            "Missing credentials. Set KYECOURTS_USERNAME and KYECOURTS_PASSWORD environment variables."
        )
    
    return username, password


def login(page: Page, username: str, password: str) -> bool:
    """
    Login to KYeCourts.
    
    Returns True if login successful, False otherwise.
    """
    print(f"Navigating to login page...", file=sys.stderr)
    page.goto(KYECOURTS_LOGIN_URL, wait_until="networkidle")
    
    # Check for and dismiss any modal popups (the "Having Trouble Logging In?" modal)
    try:
        modal_ok = page.locator("button:has-text('OK')").first
        if modal_ok.is_visible(timeout=2000):
            print("Dismissing login help modal...", file=sys.stderr)
            modal_ok.click()
            page.wait_for_timeout(500)
    except PlaywrightTimeout:
        pass  # No modal present
    
    # Fill in credentials using discovered selectors
    print("Entering credentials...", file=sys.stderr)
    
    # Username field: input[name='Username']
    page.locator("input[name='Username']").fill(username)
    
    # Password field: input[name='Password']
    page.locator("input[name='Password']").fill(password)
    
    # Click login button
    page.get_by_role("button", name=" Login").click()
    
    # Wait for navigation to Apps page after login
    print("Waiting for login to complete...", file=sys.stderr)
    try:
        page.wait_for_url("**/kyecourts/Apps**", timeout=DEFAULT_TIMEOUT)
        print("Login successful!", file=sys.stderr)
        return True
    except PlaywrightTimeout:
        # Check if we're still on login page (login failed)
        if "Login" in page.url:
            print("Login failed - still on login page", file=sys.stderr)
            return False
        return True


def navigate_to_case_search(page: Page) -> bool:
    """
    Navigate from Apps page to CourtNet case search.
    
    Flow: Apps → Case Search (CourtNet) → Account Summary → Continue → Search
    """
    print("Navigating to case search...", file=sys.stderr)
    
    # Step 1: Click "Case Search (CourtNet)" on Apps page
    try:
        page.get_by_role("link", name="Case Search (CourtNet)").click()
        page.wait_for_load_state("networkidle")
        print("  Clicked Case Search (CourtNet)", file=sys.stderr)
    except PlaywrightTimeout:
        print("Could not find Case Search link on Apps page", file=sys.stderr)
        return False
    
    # Step 2: On Account Summary page, click "Continue"
    try:
        page.get_by_role("link", name="Continue").click()
        page.wait_for_url("**/CourtNet/Search/Index**", timeout=DEFAULT_TIMEOUT)
        print("  Clicked Continue, now on Search page", file=sys.stderr)
        return True
    except PlaywrightTimeout:
        print("Could not navigate to search page", file=sys.stderr)
        return False


def search_case_by_number(
    page: Page,
    county: str,
    case_number: str,
) -> bool:
    """
    Search for a case by county and case number.
    
    Args:
        page: Playwright page object
        county: County name (e.g., "JEFFERSON", "FAYETTE")
        case_number: Case number (e.g., "25-CI-00133")
    
    Returns:
        True if search completed, False on error
    """
    print(f"Searching for case {case_number} in {county}...", file=sys.stderr)
    
    # Step 1: Click "Search by Case" tab to expand that section
    try:
        page.get_by_role("link", name="Search by Case").click()
        page.wait_for_timeout(500)  # Wait for form to appear
        print("  Expanded 'Search by Case' form", file=sys.stderr)
    except PlaywrightTimeout:
        print("Could not expand Search by Case form", file=sys.stderr)
        return False
    
    # Step 2: Select county from dropdown
    # The county dropdown is a select2 widget - click to open, then click option
    try:
        # Click on the county dropdown link to open it
        county_dropdown = page.locator("a:has-text('ADAIR')").first  # Default is ADAIR
        if not county_dropdown.is_visible():
            # Try alternative - might show current selection
            county_dropdown = page.locator("#s2id_SearchCriteria_County a").first
        county_dropdown.click()
        page.wait_for_timeout(300)
        
        # Select the county from the dropdown list
        page.get_by_role("option", name=county.upper()).click()
        print(f"  Selected county: {county}", file=sys.stderr)
    except PlaywrightTimeout:
        print(f"Could not select county: {county}", file=sys.stderr)
        return False
    
    # Step 3: Enter case number
    try:
        page.locator("#SearchCriteria_CaseNumber").fill(case_number)
        print(f"  Entered case number: {case_number}", file=sys.stderr)
    except PlaywrightTimeout:
        print("Could not enter case number", file=sys.stderr)
        return False
    
    # Step 4: Click Search button
    try:
        page.get_by_role("button", name=" Search").click()
        page.wait_for_load_state("networkidle")
        print("  Search submitted", file=sys.stderr)
        return True
    except PlaywrightTimeout:
        print("Search timed out", file=sys.stderr)
        return False


def click_first_case_result(page: Page, case_number: str) -> bool:
    """
    Click on the first case result link to open case details.
    
    The case opens in a new tab.
    """
    print("Clicking on case result...", file=sys.stderr)
    
    # Normalize case number format (25-ci-00133 -> 25-CI-000133)
    # The system adds leading zeros to make it 6 digits
    
    try:
        # Find and click the first case number link in results
        # Results show case number like "25-CI-000133"
        case_link = page.get_by_role("link", name=re.compile(r"\d{2}-CI-\d+")).first
        case_link.click()
        page.wait_for_timeout(1000)  # Wait for new tab to open
        print("  Clicked case link", file=sys.stderr)
        return True
    except PlaywrightTimeout:
        print("Could not find case link in results", file=sys.stderr)
        return False


def extract_case_details(page: Page) -> Dict[str, Any]:
    """
    Extract all case information from the "Case at a Glance" page.
    
    Returns structured dict with:
    - case_info: Basic case information (number, caption, court, judge, etc.)
    - parties: List of parties with roles and addresses
    - documents: List of filed documents with dates
    - events: List of scheduled events
    - images: List of available document images
    - raw_text: Full page text content
    """
    print("Extracting case details...", file=sys.stderr)
    
    # Get full page text
    raw_text = page.evaluate("() => document.body.innerText")
    
    # Extract case header info
    case_info = {}
    
    # Case number from page title or heading
    title = page.title()
    if title and title != "CourtNet 2.0":
        case_info["case_number"] = title
    
    # Try to extract structured info from the page
    try:
        # Caption is in a row by itself
        caption_cell = page.locator("td:has-text('VS.')").first
        if caption_cell.is_visible():
            case_info["caption"] = caption_cell.text_content().strip()
    except:
        pass
    
    # Extract court, filing date, judge from header area
    header_text = ""
    try:
        header_cell = page.locator("text=CIRCUIT COURT").first
        if header_cell.is_visible():
            header_text = header_cell.locator("..").text_content()
            
            # Parse: "JEFFERSON CIRCUIT COURT"
            if "CIRCUIT COURT" in header_text:
                court_match = re.search(r"(\w+)\s+CIRCUIT COURT", header_text)
                if court_match:
                    case_info["court"] = f"{court_match.group(1)} CIRCUIT COURT"
            
            # Parse: "Filed on 01/08/2025 as AUTOMOBILE"
            filed_match = re.search(r"Filed on (\d{2}/\d{2}/\d{4}) as (\w+)", raw_text)
            if filed_match:
                case_info["filed_date"] = filed_match.group(1)
                case_info["case_type"] = filed_match.group(2)
            
            # Parse: "with HON. ANNIE O'CONNELL"
            judge_match = re.search(r"with (HON\. [A-Z\s\.]+)", raw_text)
            if judge_match:
                case_info["judge"] = judge_match.group(1).strip()
    except:
        pass
    
    # Parse parties from raw text
    parties = []
    party_pattern = re.compile(
        r"•\s+([A-Z][A-Z\s,\.]+?)\s+as\s+([A-Z\s/]+?)(?:\s*\(Withdrawn[^)]+\))?\s*(?:Address|Memo|Summons|$)",
        re.MULTILINE
    )
    for match in party_pattern.finditer(raw_text):
        parties.append({
            "name": match.group(1).strip(),
            "role": match.group(2).strip()
        })
    
    # Parse documents from raw text
    documents = []
    doc_pattern = re.compile(
        r"•\s+([A-Z][A-Z\s\-&]+?)\s+(?:filed|entered)\s+on\s+(\d{2}/\d{2}/\d{4})",
        re.MULTILINE
    )
    for match in doc_pattern.finditer(raw_text):
        doc_type = match.group(1).strip()
        # Skip if this looks like a summons entry (those are under parties)
        if "SUMMONS" not in doc_type or "filed on" in raw_text[match.start()-50:match.start()]:
            documents.append({
                "type": doc_type,
                "date": match.group(2)
            })
    
    # Parse events from raw text
    events = []
    event_pattern = re.compile(
        r"•\s+([A-Z\s]+?)\s+scheduled for\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}\s+[AP]M)\s+in room\s+(\d+)\s+with\s+(HON\.[^•]+)",
        re.MULTILINE
    )
    for match in event_pattern.finditer(raw_text):
        events.append({
            "type": match.group(1).strip(),
            "date": match.group(2),
            "time": match.group(3),
            "room": match.group(4),
            "judge": match.group(5).strip()
        })
    
    # Parse images (documents with page counts)
    images = []
    image_pattern = re.compile(
        r"•\s+([A-Z][A-Z\s\-&]+?)\s+filed on\s+(\d{2}/\d{2}/\d{4})\s+Page\(s\):\s+(\d+)",
        re.MULTILINE
    )
    for match in image_pattern.finditer(raw_text):
        images.append({
            "type": match.group(1).strip(),
            "date": match.group(2),
            "pages": int(match.group(3))
        })
    
    return {
        "case_info": case_info,
        "parties": parties,
        "documents": documents,
        "events": events,
        "images": images,
        "raw_text": raw_text,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Search KYeCourts for case docket information"
    )
    parser.add_argument(
        "--county",
        required=True,
        help="County name (e.g., 'JEFFERSON', 'FAYETTE')"
    )
    parser.add_argument(
        "--case-number",
        required=True,
        help="Case number (e.g., '25-CI-00133')"
    )
    parser.add_argument(
        "--output",
        help="Output file path for JSON results (default: stdout)"
    )
    parser.add_argument(
        "--save-text",
        help="Save raw page text to this file path"
    )
    parser.add_argument(
        "--screenshot",
        help="Save screenshot of case details to this path"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in non-headless mode for debugging"
    )
    
    args = parser.parse_args()
    
    # Get credentials
    try:
        username, password = get_credentials()
    except ValueError as e:
        print(json.dumps({
            "error": str(e),
            "success": False
        }))
        sys.exit(1)
    
    result = {
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "search_params": {
            "county": args.county,
            "case_number": args.case_number,
        },
        "case_info": None,
        "parties": [],
        "documents": [],
        "events": [],
        "images": [],
        "error": None,
    }
    
    # Run browser automation
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=not args.debug)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT)
        
        try:
            # Step 1: Login
            if not login(page, username, password):
                result["error"] = "Login failed"
                print(json.dumps(result, indent=2))
                sys.exit(1)
            
            # Step 2: Navigate to case search
            if not navigate_to_case_search(page):
                result["error"] = "Could not navigate to case search"
                print(json.dumps(result, indent=2))
                sys.exit(1)
            
            # Step 3: Search for case
            if not search_case_by_number(page, args.county, args.case_number):
                result["error"] = "Case search failed"
                print(json.dumps(result, indent=2))
                sys.exit(1)
            
            # Step 4: Click on first case result (opens in new tab)
            if not click_first_case_result(page, args.case_number):
                result["error"] = "Could not find case in results"
                print(json.dumps(result, indent=2))
                sys.exit(1)
            
            # Step 5: Switch to the new tab with case details
            # Wait for new page to open
            page.wait_for_timeout(1000)
            pages = context.pages
            if len(pages) > 1:
                case_page = pages[-1]  # New tab is the last one
                case_page.wait_for_load_state("networkidle")
            else:
                case_page = page
            
            # Step 6: Extract case details
            details = extract_case_details(case_page)
            result["case_info"] = details["case_info"]
            result["parties"] = details["parties"]
            result["documents"] = details["documents"]
            result["events"] = details["events"]
            result["images"] = details["images"]
            
            # Take screenshot if requested
            if args.screenshot:
                screenshot_path = Path(args.screenshot)
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                case_page.screenshot(path=str(screenshot_path), full_page=True)
                result["screenshot"] = str(screenshot_path)
                print(f"Screenshot saved to {screenshot_path}", file=sys.stderr)
            
            # Save raw text if requested
            if args.save_text:
                text_path = Path(args.save_text)
                text_path.parent.mkdir(parents=True, exist_ok=True)
                text_path.write_text(details["raw_text"])
                result["text_file"] = str(text_path)
                print(f"Raw text saved to {text_path}", file=sys.stderr)
            
            result["success"] = True
            
        except PlaywrightTimeout as e:
            result["error"] = f"Timeout: {str(e)}"
        except Exception as e:
            result["error"] = f"Error: {str(e)}"
        finally:
            browser.close()
    
    # Remove raw_text from output (too large) - it's saved to file if requested
    if "raw_text" in result:
        del result["raw_text"]
    
    # Output result
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json)
        print(f"Results saved to {args.output}", file=sys.stderr)
    
    print(output_json)
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
