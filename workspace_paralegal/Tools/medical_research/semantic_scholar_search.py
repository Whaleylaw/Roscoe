#!/usr/bin/env python3
"""
Semantic Scholar Academic Research Search Tool

Search 230M+ academic papers with AI-powered relevance ranking and citation tracking.
Excellent for tracking expert witness publications, finding contradictory research,
and verifying testimony against research consensus.

Usage:
    python semantic_scholar_search.py "your search query" [--max-results N] [--min-citations N] [--year-from YYYY]

Examples:
    python semantic_scholar_search.py "biomechanics whiplash injury"
    python semantic_scholar_search.py "traumatic brain injury prognosis" --max-results 20 --min-citations 50
    python semantic_scholar_search.py "spinal cord injury recovery" --year-from 2020

Output Format:
    JSON to stdout with paper titles, authors, citations, abstracts, and paper IDs

API Notes:
    - Completely FREE with no API key required
    - Rate limit: 100 requests per 5 minutes
    - AI-powered relevance ranking
"""

import sys
import json
import argparse
from typing import Optional
import urllib.request
import urllib.parse
import urllib.error


def semantic_scholar_search(
    query: str,
    max_results: int = 10,
    min_citations: Optional[int] = None,
    year_from: Optional[int] = None,
    fields: str = "title,authors,year,citationCount,abstract,url,venue,publicationTypes"
) -> dict:
    """
    Search Semantic Scholar for academic papers.

    Args:
        query: Search query string
        max_results: Maximum number of results (default: 10, max: 100)
        min_citations: Minimum citation count filter
        year_from: Filter papers from this year onwards
        fields: Comma-separated fields to return

    Returns:
        Dictionary with search results including titles, authors, citations
    """
    try:
        # Build API URL
        base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

        params = {
            "query": query,
            "limit": min(max_results, 100),  # API max is 100
            "fields": fields
        }

        # Add filters
        if min_citations is not None:
            params["minCitationCount"] = min_citations
        if year_from is not None:
            params["year"] = f"{year_from}-"

        # Encode parameters
        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"

        # Make request
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Roscoe-Paralegal-Agent/1.0")

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        papers = data.get("data", [])

        # Format results
        results = []
        for paper in papers:
            # Extract authors
            authors = []
            for author in paper.get("authors", [])[:5]:  # Limit to first 5
                authors.append(author.get("name", "Unknown"))

            # Format abstract
            abstract = paper.get("abstract", "")
            if abstract and len(abstract) > 500:
                abstract = abstract[:500] + "..."

            results.append({
                "paper_id": paper.get("paperId", ""),
                "title": paper.get("title", ""),
                "authors": authors,
                "year": paper.get("year"),
                "citation_count": paper.get("citationCount", 0),
                "venue": paper.get("venue", ""),
                "publication_types": paper.get("publicationTypes", []),
                "abstract": abstract,
                "url": paper.get("url", "")
            })

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "total_found": data.get("total", 0),
            "results": results
        }

    except urllib.error.HTTPError as e:
        return {
            "error": f"HTTP {e.code}: {e.reason}",
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
            "error": f"Semantic Scholar search failed: {str(e)}",
            "query": query
        }


def main():
    """Command-line interface for Semantic Scholar search."""
    parser = argparse.ArgumentParser(
        description="Search Semantic Scholar for academic papers with citation tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "biomechanics cervical spine whiplash"
  %(prog)s "expert witness testimony standards" --max-results 20
  %(prog)s "traumatic brain injury outcomes" --min-citations 100 --year-from 2020

Features:
  - 230M+ papers across all scientific fields
  - AI-powered relevance ranking
  - Citation counts for credibility assessment
  - Free API with no key required
  - Rate limit: 100 requests per 5 minutes

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
        help="Maximum number of results to return (default: 10, max: 100)"
    )

    parser.add_argument(
        "--min-citations",
        type=int,
        help="Filter papers with at least this many citations"
    )

    parser.add_argument(
        "--year-from",
        type=int,
        help="Filter papers published from this year onwards (e.g., 2020)"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )

    args = parser.parse_args()

    # Perform search
    result = semantic_scholar_search(
        query=args.query,
        max_results=args.max_results,
        min_citations=args.min_citations,
        year_from=args.year_from
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
