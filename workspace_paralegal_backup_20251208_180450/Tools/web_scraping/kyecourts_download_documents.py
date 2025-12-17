#!/usr/bin/env python3
"""
KYeCourts Document Download Tool

Downloads court documents (images/PDFs) from a Kentucky eCourts case.
Uses Playwright for browser automation.

Usage:
    # Download ALL documents from a case
    python kyecourts_download_documents.py --county JEFFERSON --case-number 25-CI-00133 \
        --output-dir /projects/Case-Name/Litigation/

    # Download only specific document types (partial match)
    python kyecourts_download_documents.py --county JEFFERSON --case-number 25-CI-00133 \
        --document-types "COMPLAINT,ANSWER,ORDER" \
        --output-dir /projects/Case-Name/Litigation/

    # Download documents from a specific date
    python kyecourts_download_documents.py --county JEFFERSON --case-number 25-CI-00133 \
        --date "12/04/2025" \
        --output-dir /projects/Case-Name/Litigation/

    # Download a specific document by exact name
    python kyecourts_download_documents.py --county JEFFERSON --case-number 25-CI-00133 \
        --exact-name "MOTION TO FILE INTERVENING COMPLAINT" \
        --output-dir /projects/Case-Name/Litigation/

    # Combine filters: specific type on specific date
    python kyecourts_download_documents.py --county JEFFERSON --case-number 25-CI-00133 \
        --date "12/04/2025" --document-types "EXHIBIT" \
        --output-dir /projects/Case-Name/Litigation/

    # List available documents without downloading
    python kyecourts_download_documents.py --county JEFFERSON --case-number 25-CI-00133 --list-only

Environment Variables:
    KYECOURTS_USERNAME - KBA number or username
    KYECOURTS_PASSWORD - Account password

Output:
    Downloads PDFs to specified directory with filenames like:
    2025-01-08_COMPLAINT_PETITION.pdf
    2025-02-17_ANSWER.pdf
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
    from playwright.sync_api import sync_playwright, Page, Browser, Download, TimeoutError as PlaywrightTimeout
except ImportError:
    print(json.dumps({
        "error": "Playwright not installed. Run with execute_python_script_with_browser()",
        "success": False
    }))
    sys.exit(1)


# Configuration
KYECOURTS_LOGIN_URL = "https://kcoj.kycourts.net/kyecourts/Login"
DEFAULT_TIMEOUT = 30000  # 30 seconds
DOWNLOAD_TIMEOUT = 60000  # 60 seconds for downloads


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
    """Login to KYeCourts."""
    print(f"Navigating to login page...", file=sys.stderr)
    page.goto(KYECOURTS_LOGIN_URL, wait_until="networkidle")
    
    # Dismiss modal if present
    try:
        modal_ok = page.locator("button:has-text('OK')").first
        if modal_ok.is_visible(timeout=2000):
            modal_ok.click()
            page.wait_for_timeout(500)
    except PlaywrightTimeout:
        pass
    
    # Fill credentials
    print("Entering credentials...", file=sys.stderr)
    page.locator("input[name='Username']").fill(username)
    page.locator("input[name='Password']").fill(password)
    page.get_by_role("button", name=" Login").click()
    
    try:
        page.wait_for_url("**/kyecourts/Apps**", timeout=DEFAULT_TIMEOUT)
        print("Login successful!", file=sys.stderr)
        return True
    except PlaywrightTimeout:
        if "Login" in page.url:
            print("Login failed", file=sys.stderr)
            return False
        return True


def navigate_to_case_search(page: Page) -> bool:
    """Navigate from Apps to CourtNet case search."""
    print("Navigating to case search...", file=sys.stderr)
    
    try:
        page.get_by_role("link", name="Case Search (CourtNet)").click()
        page.wait_for_load_state("networkidle")
        
        page.get_by_role("link", name="Continue").click()
        page.wait_for_url("**/CourtNet/Search/Index**", timeout=DEFAULT_TIMEOUT)
        return True
    except PlaywrightTimeout:
        print("Could not navigate to search page", file=sys.stderr)
        return False


def search_and_open_case(page: Page, county: str, case_number: str) -> Optional[Page]:
    """Search for case and open it in new tab. Returns the case page."""
    print(f"Searching for case {case_number} in {county}...", file=sys.stderr)
    
    try:
        # Click Search by Case tab
        page.get_by_role("link", name="Search by Case").click()
        page.wait_for_timeout(500)
        
        # Select county
        county_dropdown = page.locator("a:has-text('ADAIR')").first
        if not county_dropdown.is_visible():
            county_dropdown = page.locator("#s2id_SearchCriteria_County a").first
        county_dropdown.click()
        page.wait_for_timeout(300)
        page.get_by_role("option", name=county.upper()).click()
        
        # Enter case number
        page.locator("#SearchCriteria_CaseNumber").fill(case_number)
        
        # Search
        page.get_by_role("button", name=" Search").click()
        page.wait_for_load_state("networkidle")
        
        # Click first case result (opens new tab)
        case_link = page.get_by_role("link", name=re.compile(r"\d{2}-CI-\d+")).first
        case_link.click()
        page.wait_for_timeout(1500)
        
        # Get the new tab
        context = page.context
        pages = context.pages
        if len(pages) > 1:
            case_page = pages[-1]
            case_page.wait_for_load_state("networkidle")
            print(f"Opened case page: {case_page.title()}", file=sys.stderr)
            return case_page
        
        return page
        
    except PlaywrightTimeout as e:
        print(f"Error searching for case: {e}", file=sys.stderr)
        return None


def get_document_list(page: Page) -> List[Dict[str, Any]]:
    """Extract list of available documents from the Images section."""
    documents = []
    
    # Find the Images section - it contains links to downloadable documents
    # Each document link is in a table row with format:
    # "• DOCUMENT TYPE filed on MM/DD/YYYY Page(s): N"
    
    # Get all links in the Images section
    images_section = page.locator("text=Images").first
    
    # Find all document links - they're links that contain document type text
    # and have href="#" (they trigger JavaScript downloads)
    doc_links = page.locator("table:below(:text('Images')) a[href='#']").all()
    
    for link in doc_links:
        try:
            doc_type = link.text_content().strip()
            if not doc_type or doc_type in ['(-) Hide', '']:
                continue
            
            # Get the parent row to extract date
            parent = link.locator("..").first  # Get parent cell
            row_text = parent.text_content()
            
            # Extract date from "filed on MM/DD/YYYY"
            date_match = re.search(r'filed on (\d{2}/\d{2}/\d{4})', row_text)
            date = date_match.group(1) if date_match else "unknown"
            
            # Extract page count
            pages_match = re.search(r'Page\(s\):\s*(\d+)', row_text)
            pages = int(pages_match.group(1)) if pages_match else 0
            
            documents.append({
                "type": doc_type,
                "date": date,
                "pages": pages,
                "element": link,
            })
        except Exception as e:
            print(f"Error parsing document link: {e}", file=sys.stderr)
            continue
    
    return documents


def sanitize_filename(name: str) -> str:
    """Convert document type to safe filename."""
    # Replace special characters with underscores
    safe = re.sub(r'[^\w\s-]', '', name)
    safe = re.sub(r'[\s]+', '_', safe)
    return safe.upper()


def download_document(page: Page, doc: Dict[str, Any], output_dir: Path) -> Optional[str]:
    """Download a single document and save to output directory."""
    doc_type = doc["type"]
    date = doc["date"]
    element = doc["element"]
    
    # Create filename: YYYY-MM-DD_DOCUMENT_TYPE.pdf
    try:
        date_obj = datetime.strptime(date, "%m/%d/%Y")
        date_str = date_obj.strftime("%Y-%m-%d")
    except:
        date_str = date.replace("/", "-")
    
    safe_type = sanitize_filename(doc_type)
    filename = f"{date_str}_{safe_type}.pdf"
    filepath = output_dir / filename
    
    # Handle duplicate filenames by adding a counter
    counter = 1
    while filepath.exists():
        filename = f"{date_str}_{safe_type}_{counter}.pdf"
        filepath = output_dir / filename
        counter += 1
    
    print(f"  Downloading: {doc_type} ({date})...", file=sys.stderr)
    
    try:
        # Set up download handler
        with page.expect_download(timeout=DOWNLOAD_TIMEOUT) as download_info:
            element.click()
        
        download = download_info.value
        
        # Save the file
        download.save_as(str(filepath))
        print(f"    Saved: {filename}", file=sys.stderr)
        
        return str(filepath)
        
    except PlaywrightTimeout:
        print(f"    Timeout downloading {doc_type}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"    Error downloading {doc_type}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Download court documents from KYeCourts case"
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
        "--output-dir",
        required=False,
        default="/Reports/downloads",
        help="Directory to save downloaded documents"
    )
    parser.add_argument(
        "--document-types",
        help="Comma-separated list of document types to download - partial match (default: all)"
    )
    parser.add_argument(
        "--date",
        help="Download only documents from this date (format: MM/DD/YYYY)"
    )
    parser.add_argument(
        "--exact-name",
        help="Download document with this exact name (can be combined with --date)"
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="List available documents without downloading"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in non-headless mode for debugging"
    )
    
    args = parser.parse_args()
    
    # Parse filters
    type_filter = None
    if args.document_types:
        type_filter = [t.strip().upper() for t in args.document_types.split(",")]
    
    date_filter = args.date  # e.g., "12/04/2025"
    exact_name_filter = args.exact_name.upper().strip() if args.exact_name else None
    
    # Get credentials
    try:
        username, password = get_credentials()
    except ValueError as e:
        print(json.dumps({"error": str(e), "success": False}))
        sys.exit(1)
    
    # Resolve output directory
    workspace = Path(os.environ.get("WORKSPACE_DIR", "/mnt/workspace"))
    if args.output_dir.startswith("/"):
        output_dir = workspace / args.output_dir.lstrip("/")
    else:
        output_dir = workspace / args.output_dir
    
    result = {
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "case": {
            "county": args.county,
            "case_number": args.case_number,
        },
        "documents_found": [],
        "documents_downloaded": [],
        "output_dir": str(output_dir),
        "error": None,
    }
    
    # Run browser automation
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.debug)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(DEFAULT_TIMEOUT)
        
        try:
            # Login
            if not login(page, username, password):
                result["error"] = "Login failed"
                print(json.dumps(result, indent=2))
                sys.exit(1)
            
            # Navigate to search
            if not navigate_to_case_search(page):
                result["error"] = "Could not navigate to case search"
                print(json.dumps(result, indent=2))
                sys.exit(1)
            
            # Search and open case
            case_page = search_and_open_case(page, args.county, args.case_number)
            if not case_page:
                result["error"] = "Could not find case"
                print(json.dumps(result, indent=2))
                sys.exit(1)
            
            # Get document list
            print("Finding available documents...", file=sys.stderr)
            documents = get_document_list(case_page)
            
            result["documents_found"] = [
                {"type": d["type"], "date": d["date"], "pages": d["pages"]}
                for d in documents
            ]
            
            print(f"Found {len(documents)} documents", file=sys.stderr)
            
            # If list-only, just output the list
            if args.list_only:
                result["success"] = True
                print(json.dumps(result, indent=2))
                sys.exit(0)
            
            # Apply filters
            original_count = len(documents)
            
            # Filter by exact name
            if exact_name_filter:
                documents = [
                    d for d in documents
                    if d["type"].upper().strip() == exact_name_filter
                ]
                print(f"Filtered by exact name '{exact_name_filter}': {len(documents)} matches", file=sys.stderr)
            
            # Filter by document type (partial match)
            if type_filter:
                documents = [
                    d for d in documents
                    if any(t in d["type"].upper() for t in type_filter)
                ]
                print(f"Filtered by type {type_filter}: {len(documents)} matches", file=sys.stderr)
            
            # Filter by date
            if date_filter:
                documents = [
                    d for d in documents
                    if d["date"] == date_filter
                ]
                print(f"Filtered by date '{date_filter}': {len(documents)} matches", file=sys.stderr)
            
            if original_count != len(documents):
                print(f"Filtered from {original_count} to {len(documents)} documents", file=sys.stderr)
            
            if not documents:
                result["error"] = "No documents to download"
                result["success"] = True  # Not really an error, just nothing to do
                print(json.dumps(result, indent=2))
                sys.exit(0)
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Download each document
            print(f"Downloading {len(documents)} documents to {output_dir}...", file=sys.stderr)
            
            for doc in documents:
                filepath = download_document(case_page, doc, output_dir)
                if filepath:
                    result["documents_downloaded"].append({
                        "type": doc["type"],
                        "date": doc["date"],
                        "filepath": filepath,
                    })
            
            result["success"] = True
            print(f"\nDownloaded {len(result['documents_downloaded'])} of {len(documents)} documents", file=sys.stderr)
            
        except PlaywrightTimeout as e:
            result["error"] = f"Timeout: {str(e)}"
        except Exception as e:
            result["error"] = f"Error: {str(e)}"
        finally:
            browser.close()
    
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

