#!/usr/bin/env python3
"""
Court Case & Legal Precedent Search Tool

Search millions of court opinions using the CourtListener API v4.
Essential for legal precedent research, case law citations, and jurisdiction-specific rulings.

Usage:
    python court_case_search.py "your search query" [--court COURT] [--after-date YYYY-MM-DD] [--max-results N]

Examples:
    python court_case_search.py "personal injury statute of limitations Kentucky"
    python court_case_search.py "whiplash motor vehicle accident" --court ca6 --max-results 20
    python court_case_search.py "traumatic brain injury damages" --after-date 2020-01-01

Output Format:
    JSON to stdout with case names, citations, courts, dates, and snippets

Court Codes:
    scotus - Supreme Court of the United States
    ca1, ca2, ..., ca11, cadc, cafc - Federal Circuit Courts
    ca6 - 6th Circuit (covers Kentucky, Michigan, Ohio, Tennessee)
    ky - Kentucky Supreme Court
    kyctapp - Kentucky Court of Appeals
    kyed, kywd, kyeb - Kentucky District Courts

API Notes:
    - API v4 with authentication
    - Requires COURTLISTENER_API_KEY environment variable
    - 5,000+ requests/hour with API key
    - Millions of federal and state court opinions
    - Updated daily

Environment Variables:
    COURTLISTENER_API_KEY: Required for API access
"""

import sys
import json
import argparse
from typing import Optional
import urllib.request
import urllib.parse
import urllib.error


def court_case_search(
    query: str,
    max_results: int = 10,
    court: Optional[str] = None,
    after_date: Optional[str] = None,
) -> dict:
    """
    Search CourtListener v4 API for court opinions and case law.

    Args:
        query: Search query string
        max_results: Maximum number of results (default: 10)
        court: Court identifier (e.g., 'scotus', 'ca6', 'ky')
        after_date: Filter cases after this date (YYYY-MM-DD format)

    Returns:
        Dictionary with search results including case names, citations, opinions
    """
    try:
        import os

        # Get API key (required for v4)
        api_key = os.environ.get("COURTLISTENER_API_KEY")
        if not api_key:
            return {
                "error": "COURTLISTENER_API_KEY environment variable not set",
                "query": query,
                "help": "Set COURTLISTENER_API_KEY in your environment to use this tool"
            }

        # Build API URL (v4)
        base_url = "https://www.courtlistener.com/api/rest/v4/search/"

        params = {
            "q": query,
            "type": "o",  # opinions
            "page_size": min(max_results, 20)  # API max per page is 20
        }

        # Add filters
        if court:
            params["court"] = court
        if after_date:
            params["filed_after"] = after_date

        # Encode parameters
        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"

        # Make request with authentication
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Roscoe-Paralegal-Agent/1.0")
        req.add_header("Authorization", f"Token {api_key}")

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        results_data = data.get("results", [])

        # Format results
        results = []
        for item in results_data:
            # Extract relevant fields
            case_name = item.get("caseName", "")
            citation = item.get("citation", [""])[0] if item.get("citation") else ""
            court_name = item.get("court", "")
            date_filed = item.get("dateFiled", "")
            snippet = item.get("snippet", "")

            # Clean snippet HTML
            if snippet:
                snippet = snippet.replace("<mark>", "").replace("</mark>", "")
                if len(snippet) > 400:
                    snippet = snippet[:400] + "..."

            results.append({
                "case_name": case_name,
                "citation": citation,
                "court": court_name,
                "date_filed": date_filed,
                "snippet": snippet,
                "url": f"https://www.courtlistener.com{item.get('absolute_url', '')}" if item.get('absolute_url') else ""
            })

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "total_found": data.get("count", 0),
            "results": results
        }

    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}: {e.reason}"
        if e.code == 429:
            error_msg += " (Rate limit exceeded - try again in a few minutes)"
        return {
            "error": error_msg,
            "query": query
        }
    except urllib.error.URLError as e:
        return {
            "error": f"Network error: {str(e.reason)}",
            "query": query
        }
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse API response: {str(e)}",
            "query": query
        }
    except Exception as e:
        return {
            "error": f"Court case search failed: {str(e)}",
            "query": query
        }


def main():
    """Command-line interface for court case search."""
    parser = argparse.ArgumentParser(
        description="Search court opinions and case law using CourtListener API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "personal injury statute of limitations"
  %(prog)s "motor vehicle accident whiplash injury" --court 6cir --max-results 20
  %(prog)s "traumatic brain injury damages Kentucky" --after-date 2020-01-01

Common Court Codes:
  scotus       - U.S. Supreme Court
  6cir         - 6th Circuit (KY, MI, OH, TN)
  ca1 - ca11   - Other Federal Circuits
  kyb, kye     - Kentucky District Courts

For full court list: https://www.courtlistener.com/api/rest/v3/courts/

Features:
  - FREE API with 5,000 requests/hour
  - Millions of federal and state opinions
  - Full-text search with relevance ranking
  - Updated daily

Output is JSON that can be piped to jq or parsed in Python.
        """
    )

    parser.add_argument(
        "query",
        help="Search query string"
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results to return (default: 10)"
    )

    parser.add_argument(
        "--court",
        help="Court identifier (e.g., 'scotus', '6cir', 'kyb')"
    )

    parser.add_argument(
        "--after-date",
        help="Filter cases filed after this date (YYYY-MM-DD)"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )

    args = parser.parse_args()

    # Perform search
    result = court_case_search(
        query=args.query,
        max_results=args.max_results,
        court=args.court,
        after_date=args.after_date
    )

    # Output JSON to stdout
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))

    # Exit with error code if search failed
    if "error" in result:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
