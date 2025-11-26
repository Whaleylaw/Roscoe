#!/usr/bin/env python3
"""
Expert Witness Publication & Credential Lookup Tool

Search for expert witness publications, citation metrics, and research credentials.
Uses Semantic Scholar Author Search API to verify publication quality and expertise.

Usage:
    python expert_witness_lookup.py "Expert Name" [--max-papers N] [--field-filter FIELD]

Examples:
    python expert_witness_lookup.py "John Smith neurology"
    python expert_witness_lookup.py "Dr. Jane Doe biomechanics" --max-papers 20
    python expert_witness_lookup.py "Robert Jones orthopedic" --field-filter "Medicine"

Output Format:
    JSON to stdout with author info, h-index, citation count, and top publications

API Notes:
    - Completely FREE with no API key required
    - Rate limit: 100 requests per 5 minutes
    - 230M+ papers, comprehensive author profiles
"""

import sys
import json
import argparse
from typing import Optional
import urllib.request
import urllib.parse
import urllib.error


def expert_witness_lookup(
    expert_name: str,
    max_papers: int = 10,
    field_filter: Optional[str] = None,
) -> dict:
    """
    Look up expert witness publication record and credentials.

    Args:
        expert_name: Name of the expert witness
        max_papers: Maximum number of papers to return (default: 10)
        field_filter: Filter by field of study (e.g., "Medicine", "Engineering")

    Returns:
        Dictionary with author profile, h-index, citations, and top papers
    """
    try:
        # Search for author
        base_url = "https://api.semanticscholar.org/graph/v1/author/search"

        params = {
            "query": expert_name,
            "limit": 5,  # Get top 5 author matches
            "fields": "authorId,name,affiliations,homepage,paperCount,citationCount,hIndex"
        }

        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"

        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Roscoe-Paralegal-Agent/1.0")

        with urllib.request.urlopen(req, timeout=30) as response:
            author_data = json.loads(response.read().decode())

        authors = author_data.get("data", [])

        if not authors:
            return {
                "success": True,
                "query": expert_name,
                "found": False,
                "message": "No matching authors found"
            }

        # Get the most likely match (first result)
        author = authors[0]
        author_id = author.get("authorId")

        # Get author's papers
        papers_url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers"

        paper_params = {
            "limit": max_papers,
            "fields": "paperId,title,year,citationCount,publicationTypes,venue"
        }

        if field_filter:
            paper_params["fieldsOfStudy"] = field_filter

        paper_query = urllib.parse.urlencode(paper_params)
        papers_full_url = f"{papers_url}?{paper_query}"

        papers_req = urllib.request.Request(papers_full_url)
        papers_req.add_header("User-Agent", "Roscoe-Paralegal-Agent/1.0")

        with urllib.request.urlopen(papers_req, timeout=30) as papers_response:
            papers_data = json.loads(papers_response.read().decode())

        papers = papers_data.get("data", [])

        # Format papers
        top_papers = []
        for paper in papers:
            top_papers.append({
                "title": paper.get("title", ""),
                "year": paper.get("year"),
                "citations": paper.get("citationCount", 0),
                "venue": paper.get("venue", ""),
                "publication_types": paper.get("publicationTypes", [])
            })

        # Sort papers by citations
        top_papers.sort(key=lambda x: x.get("citations", 0), reverse=True)

        # Return all matching authors for disambiguation
        all_matches = []
        for auth in authors:
            all_matches.append({
                "name": auth.get("name", ""),
                "affiliations": auth.get("affiliations", [])[:2],  # First 2
                "paper_count": auth.get("paperCount", 0),
                "citation_count": auth.get("citationCount", 0),
                "h_index": auth.get("hIndex", 0),
                "homepage": auth.get("homepage", "")
            })

        return {
            "success": True,
            "query": expert_name,
            "found": True,
            "primary_match": {
                "name": author.get("name", ""),
                "author_id": author_id,
                "affiliations": author.get("affiliations", []),
                "homepage": author.get("homepage", ""),
                "total_papers": author.get("paperCount", 0),
                "total_citations": author.get("citationCount", 0),
                "h_index": author.get("hIndex", 0),
                "semantic_scholar_url": f"https://www.semanticscholar.org/author/{author_id}"
            },
            "top_papers": top_papers[:max_papers],
            "all_matches": all_matches
        }

    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}: {e.reason}"
        return {
            "error": error_msg,
            "query": expert_name
        }
    except urllib.error.URLError as e:
        return {
            "error": f"Network error: {str(e.reason)}",
            "query": expert_name
        }
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse API response: {str(e)}",
            "query": expert_name
        }
    except Exception as e:
        return {
            "error": f"Expert witness lookup failed: {str(e)}",
            "query": expert_name
        }


def main():
    """Command-line interface for expert witness lookup."""
    parser = argparse.ArgumentParser(
        description="Look up expert witness publications and credentials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "John Smith neurology"
  %(prog)s "Dr. Jane Doe biomechanics" --max-papers 20
  %(prog)s "Robert Jones orthopedic surgery" --field-filter Medicine

Output includes:
  - Total publications and citation count
  - H-index (measure of research impact)
  - Affiliations and homepage
  - Top publications by citation count
  - Multiple author matches for disambiguation

Use Case:
  - Verify expert witness credentials
  - Check publication quality (citation counts)
  - Identify areas of actual expertise
  - Find contradictory published research
  - Assess credibility for cross-examination

Output is JSON that can be piped to jq or parsed in Python.
        """
    )

    parser.add_argument(
        "expert_name",
        help="Name of the expert witness to look up"
    )

    parser.add_argument(
        "--max-papers",
        type=int,
        default=10,
        help="Maximum number of papers to return (default: 10)"
    )

    parser.add_argument(
        "--field-filter",
        help="Filter by field of study (e.g., 'Medicine', 'Engineering')"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )

    args = parser.parse_args()

    # Perform lookup
    result = expert_witness_lookup(
        expert_name=args.expert_name,
        max_papers=args.max_papers,
        field_filter=args.field_filter
    )

    # Output JSON to stdout
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))

    # Exit with error code if lookup failed
    if "error" in result:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
