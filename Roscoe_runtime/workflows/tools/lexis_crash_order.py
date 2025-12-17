#!/usr/bin/env python3
"""
LexisNexis Crash Report Ordering Tool

Automates ordering police/crash reports from LexisNexis BuyCrash using Playwright.

Prerequisites:
    pip install playwright
    playwright install chromium

Usage:
    # Interactive mode (visible browser, for first-time setup/debugging)
    python lexis_crash_order.py --report-number "12345" --interactive
    
    # Headless mode (after credentials are saved)
    python lexis_crash_order.py --report-number "12345" --output /case/reports/
    
    # With all search criteria
    python lexis_crash_order.py --report-number "12345" --last-name "Smith" --date "2024-01-15"

Environment Variables:
    LEXIS_USERNAME - LexisNexis username/email
    LEXIS_PASSWORD - LexisNexis password
    
    Or use --username and --password flags (not recommended for security)

Notes:
    - First run should use --interactive to verify the login flow works
    - The tool will save cookies to speed up subsequent logins
    - Downloaded PDFs are saved to the specified output directory
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("ERROR: Playwright not installed. Run: pip install playwright && playwright install chromium", file=sys.stderr)
    sys.exit(1)


# Configuration
DEFAULT_TIMEOUT = 30000  # 30 seconds
COOKIE_FILE = Path(__file__).parent / "config" / "lexis_cookies.json"
CONFIG_DIR = Path(__file__).parent / "config"

# LexisNexis URLs (may need adjustment based on your specific portal)
LEXIS_LOGIN_URL = "https://signin.lexisnexis.com/lnaccess/app/signin"
BUYCRASH_URL = "https://buycrash.lexisnexisrisk.com"


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def save_cookies(context, filepath: Path):
    """Save browser cookies for future sessions."""
    cookies = context.cookies()
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(cookies, f)
    print(f"Cookies saved to {filepath}", file=sys.stderr)


def load_cookies(context, filepath: Path) -> bool:
    """Load saved cookies if they exist."""
    if filepath.exists():
        try:
            with open(filepath) as f:
                cookies = json.load(f)
            context.add_cookies(cookies)
            print(f"Loaded saved cookies from {filepath}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"Warning: Could not load cookies: {e}", file=sys.stderr)
    return False


def login_to_lexis(page, username: str, password: str, interactive: bool = False) -> bool:
    """
    Log into LexisNexis.
    
    Args:
        page: Playwright page object
        username: LexisNexis username
        password: LexisNexis password
        interactive: If True, wait for manual intervention if needed
        
    Returns:
        True if login successful, False otherwise
    """
    print("Navigating to LexisNexis login...", file=sys.stderr)
    
    try:
        page.goto(LEXIS_LOGIN_URL, timeout=DEFAULT_TIMEOUT)
        
        # Wait for login form
        page.wait_for_selector('input[type="email"], input[name="userid"], input[id="userid"]', 
                               timeout=DEFAULT_TIMEOUT)
        
        # Fill username - try different possible selectors
        username_selectors = [
            'input[type="email"]',
            'input[name="userid"]',
            'input[id="userid"]',
            'input[name="username"]',
            '#username'
        ]
        
        for selector in username_selectors:
            try:
                elem = page.locator(selector).first
                if elem.is_visible():
                    elem.fill(username)
                    print(f"Filled username using selector: {selector}", file=sys.stderr)
                    break
            except:
                continue
        
        # Fill password
        password_selectors = [
            'input[type="password"]',
            'input[name="password"]',
            'input[id="password"]',
            '#password'
        ]
        
        for selector in password_selectors:
            try:
                elem = page.locator(selector).first
                if elem.is_visible():
                    elem.fill(password)
                    print(f"Filled password using selector: {selector}", file=sys.stderr)
                    break
            except:
                continue
        
        # Click login button
        login_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            '#SignIn',
            'button:has-text("Sign In")',
            'button:has-text("Log In")'
        ]
        
        for selector in login_selectors:
            try:
                elem = page.locator(selector).first
                if elem.is_visible():
                    elem.click()
                    print(f"Clicked login using selector: {selector}", file=sys.stderr)
                    break
            except:
                continue
        
        # Wait for redirect or dashboard
        time.sleep(3)  # Brief wait for redirect
        
        # Check if we're logged in (look for dashboard elements or URL change)
        current_url = page.url
        if "signin" not in current_url.lower() or "dashboard" in current_url.lower():
            print("Login appears successful!", file=sys.stderr)
            return True
        
        if interactive:
            print("\n" + "="*50, file=sys.stderr)
            print("MANUAL INTERVENTION NEEDED", file=sys.stderr)
            print("Please complete login in the browser window.", file=sys.stderr)
            print("Press Enter here when done...", file=sys.stderr)
            print("="*50, file=sys.stderr)
            input()
            return True
        
        return False
        
    except PlaywrightTimeout:
        print("ERROR: Timeout waiting for login page", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR during login: {e}", file=sys.stderr)
        return False


def navigate_to_buycrash(page) -> bool:
    """Navigate to the BuyCrash/crash reports section."""
    print("Navigating to BuyCrash...", file=sys.stderr)
    
    try:
        page.goto(BUYCRASH_URL, timeout=DEFAULT_TIMEOUT)
        time.sleep(2)  # Wait for page load
        
        # Check if we need to re-authenticate
        if "signin" in page.url.lower():
            print("Session expired, need to re-login", file=sys.stderr)
            return False
        
        print(f"Navigated to: {page.url}", file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"ERROR navigating to BuyCrash: {e}", file=sys.stderr)
        return False


def search_report(page, report_number: str, last_name: Optional[str] = None, 
                  report_date: Optional[str] = None, interactive: bool = False) -> bool:
    """
    Search for a crash report.
    
    Args:
        page: Playwright page object
        report_number: The crash report number
        last_name: Driver's last name (optional)
        report_date: Date of the report (optional)
        interactive: If True, allow manual intervention
        
    Returns:
        True if report found, False otherwise
    """
    print(f"Searching for report: {report_number}", file=sys.stderr)
    
    try:
        # Wait for search form to load
        time.sleep(2)
        
        # Try to find and fill report number field
        report_selectors = [
            'input[name="reportNumber"]',
            'input[name="caseNumber"]',
            'input[id="reportNumber"]',
            'input[id="caseNumber"]',
            'input[placeholder*="report"]',
            'input[placeholder*="case"]'
        ]
        
        filled = False
        for selector in report_selectors:
            try:
                elem = page.locator(selector).first
                if elem.is_visible():
                    elem.fill(report_number)
                    print(f"Filled report number using: {selector}", file=sys.stderr)
                    filled = True
                    break
            except:
                continue
        
        if not filled and interactive:
            print("\n" + "="*50, file=sys.stderr)
            print("MANUAL INTERVENTION NEEDED", file=sys.stderr)
            print(f"Please enter report number: {report_number}", file=sys.stderr)
            print("Press Enter here when done...", file=sys.stderr)
            print("="*50, file=sys.stderr)
            input()
        
        # Fill last name if provided
        if last_name:
            name_selectors = [
                'input[name="lastName"]',
                'input[id="lastName"]',
                'input[placeholder*="name"]'
            ]
            for selector in name_selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible():
                        elem.fill(last_name)
                        break
                except:
                    continue
        
        # Fill date if provided
        if report_date:
            date_selectors = [
                'input[name="reportDate"]',
                'input[type="date"]',
                'input[id="reportDate"]'
            ]
            for selector in date_selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible():
                        elem.fill(report_date)
                        break
                except:
                    continue
        
        # Click search button
        search_selectors = [
            'button[type="submit"]',
            'button:has-text("Search")',
            'input[type="submit"]',
            '#searchButton'
        ]
        
        for selector in search_selectors:
            try:
                elem = page.locator(selector).first
                if elem.is_visible():
                    elem.click()
                    print("Clicked search button", file=sys.stderr)
                    break
            except:
                continue
        
        # Wait for results
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"ERROR during search: {e}", file=sys.stderr)
        return False


def download_report(page, output_dir: Path, report_number: str, interactive: bool = False) -> Optional[Path]:
    """
    Download the crash report PDF.
    
    Args:
        page: Playwright page object
        output_dir: Directory to save the PDF
        report_number: Report number (used for filename)
        interactive: If True, allow manual intervention
        
    Returns:
        Path to downloaded file, or None if failed
    """
    print("Attempting to download report...", file=sys.stderr)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"crash_report_{report_number}_{timestamp}.pdf"
    output_path = output_dir / filename
    
    try:
        # Look for download/purchase button
        download_selectors = [
            'button:has-text("Download")',
            'button:has-text("Purchase")',
            'button:has-text("Buy")',
            'a:has-text("Download")',
            'a:has-text("PDF")',
            '.download-button',
            '#downloadButton'
        ]
        
        # Set up download handler
        with page.expect_download(timeout=60000) as download_info:
            clicked = False
            for selector in download_selectors:
                try:
                    elem = page.locator(selector).first
                    if elem.is_visible():
                        elem.click()
                        clicked = True
                        print(f"Clicked download using: {selector}", file=sys.stderr)
                        break
                except:
                    continue
            
            if not clicked and interactive:
                print("\n" + "="*50, file=sys.stderr)
                print("MANUAL INTERVENTION NEEDED", file=sys.stderr)
                print("Please click the download/purchase button.", file=sys.stderr)
                print("Press Enter here when download starts...", file=sys.stderr)
                print("="*50, file=sys.stderr)
                input()
        
        download = download_info.value
        download.save_as(output_path)
        print(f"Report downloaded to: {output_path}", file=sys.stderr)
        return output_path
        
    except PlaywrightTimeout:
        print("ERROR: Timeout waiting for download", file=sys.stderr)
        
        if interactive:
            # Maybe the download happened outside our handler
            print("Check if file was downloaded to browser's default location", file=sys.stderr)
        
        return None
        
    except Exception as e:
        print(f"ERROR during download: {e}", file=sys.stderr)
        return None


def order_crash_report(
    report_number: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    last_name: Optional[str] = None,
    report_date: Optional[str] = None,
    output_dir: str = ".",
    interactive: bool = False,
    headless: bool = True
) -> dict:
    """
    Main function to order a crash report from LexisNexis.
    
    Args:
        report_number: The crash report number to order
        username: LexisNexis username (or use LEXIS_USERNAME env var)
        password: LexisNexis password (or use LEXIS_PASSWORD env var)
        last_name: Driver's last name for search
        report_date: Date of report for search
        output_dir: Directory to save downloaded PDF
        interactive: If True, run with visible browser for manual intervention
        headless: If False, show browser window
        
    Returns:
        dict with success status and file path or error message
    """
    ensure_config_dir()
    
    # Get credentials
    username = username or os.environ.get("LEXIS_USERNAME")
    password = password or os.environ.get("LEXIS_PASSWORD")
    
    if not username or not password:
        return {
            "success": False,
            "error": "Missing credentials. Set LEXIS_USERNAME and LEXIS_PASSWORD environment variables.",
            "report_number": report_number
        }
    
    # If interactive, force visible browser
    if interactive:
        headless = False
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            accept_downloads=True,
            viewport={"width": 1280, "height": 800}
        )
        
        # Try to load saved cookies
        load_cookies(context, COOKIE_FILE)
        
        page = context.new_page()
        
        try:
            # Try navigating directly to BuyCrash first (if cookies are valid)
            if not navigate_to_buycrash(page) or "signin" in page.url.lower():
                # Need to login
                if not login_to_lexis(page, username, password, interactive):
                    return {
                        "success": False,
                        "error": "Login failed",
                        "report_number": report_number
                    }
                
                # Save cookies after successful login
                save_cookies(context, COOKIE_FILE)
                
                # Navigate to BuyCrash after login
                if not navigate_to_buycrash(page):
                    return {
                        "success": False,
                        "error": "Could not navigate to BuyCrash after login",
                        "report_number": report_number
                    }
            
            # Search for the report
            if not search_report(page, report_number, last_name, report_date, interactive):
                return {
                    "success": False,
                    "error": "Search failed",
                    "report_number": report_number
                }
            
            # Download the report
            output_path = download_report(page, Path(output_dir), report_number, interactive)
            
            if output_path and output_path.exists():
                # Save cookies after successful operation
                save_cookies(context, COOKIE_FILE)
                
                return {
                    "success": True,
                    "report_number": report_number,
                    "file_path": str(output_path),
                    "message": f"Report downloaded successfully to {output_path}"
                }
            else:
                return {
                    "success": False,
                    "error": "Download failed or file not found",
                    "report_number": report_number
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "report_number": report_number
            }
            
        finally:
            if interactive:
                print("\nPress Enter to close browser...", file=sys.stderr)
                input()
            browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Order crash reports from LexisNexis BuyCrash",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Required
    parser.add_argument("--report-number", "-r", required=True,
                        help="Crash report number to order")
    
    # Search criteria
    parser.add_argument("--last-name", "-n",
                        help="Driver's last name")
    parser.add_argument("--date", "-d",
                        help="Report date (YYYY-MM-DD)")
    
    # Credentials
    parser.add_argument("--username", "-u",
                        help="LexisNexis username (or use LEXIS_USERNAME env var)")
    parser.add_argument("--password", "-p",
                        help="LexisNexis password (or use LEXIS_PASSWORD env var)")
    
    # Output
    parser.add_argument("--output", "-o", default=".",
                        help="Output directory for downloaded PDF")
    
    # Browser options
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run with visible browser, pause for manual intervention")
    parser.add_argument("--show-browser", action="store_true",
                        help="Show browser window (but don't pause)")
    
    # Output format
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty print JSON output")
    
    args = parser.parse_args()
    
    result = order_crash_report(
        report_number=args.report_number,
        username=args.username,
        password=args.password,
        last_name=args.last_name,
        report_date=args.date,
        output_dir=args.output,
        interactive=args.interactive,
        headless=not (args.interactive or args.show_browser)
    )
    
    # Output result
    print(json.dumps(result, indent=2 if args.pretty else None))
    
    # Exit code
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

