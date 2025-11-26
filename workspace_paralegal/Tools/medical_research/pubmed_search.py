#!/usr/bin/env python3
"""
PubMed Medical Research Search Tool

Search 39M+ peer-reviewed biomedical citations using NCBI E-utilities API.
Essential for medical causation research, expert witness verification, and
standards of care investigation.

Usage:
    python pubmed_search.py "your search query" [--max-results N] [--sort relevance|date] [--details]

Examples:
    python pubmed_search.py "whiplash cervical spine injury"
    python pubmed_search.py "traumatic brain injury long-term effects" --max-results 20
    python pubmed_search.py "lumbar disc herniation causation motor vehicle" --sort date --details

Output Format:
    JSON to stdout with article titles, authors, journals, abstracts, and PMIDs

Environment Variables:
    NCBI_API_KEY: (Optional) For higher rate limits (10 req/sec vs 3 req/sec)
    NCBI_EMAIL: (Required) Your email for NCBI tracking
"""

import os
import sys
import json
import argparse
import time
from typing import List, Dict, Literal


def pubmed_search(
    query: str,
    max_results: int = 10,
    sort: Literal["relevance", "date"] = "relevance",
    include_details: bool = False,
) -> dict:
    """
    Search PubMed for peer-reviewed medical research.

    Args:
        query: Search query (supports PubMed query syntax)
        max_results: Maximum number of results (default: 10)
        sort: Sort by relevance or publication date
        include_details: Include full abstracts and detailed metadata

    Returns:
        Dictionary with search results including PMIDs, titles, authors, journals
    """
    try:
        from Bio import Entrez
    except ImportError:
        return {
            "error": "biopython package not installed. Run: pip install biopython",
            "query": query
        }

    try:
        # Configure Entrez
        Entrez.email = os.environ.get("NCBI_EMAIL", "your_email@example.com")
        api_key = os.environ.get("NCBI_API_KEY")
        if api_key:
            Entrez.api_key = api_key

        # Search for PMIDs
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "sort": "relevance" if sort == "relevance" else "pub_date",
            "retmode": "json"
        }

        handle = Entrez.esearch(**search_params)
        search_results = Entrez.read(handle)
        handle.close()

        pmid_list = search_results.get("IdList", [])

        if not pmid_list:
            return {
                "success": True,
                "query": query,
                "count": 0,
                "results": []
            }

        # Fetch details for each PMID
        results = []

        if include_details:
            # Fetch detailed records (abstracts, full metadata)
            ids = ",".join(pmid_list)
            handle = Entrez.efetch(db="pubmed", id=ids, rettype="abstract", retmode="xml")
            records = Entrez.read(handle)
            handle.close()

            for article in records.get("PubmedArticle", []):
                medline = article.get("MedlineCitation", {})
                article_data = medline.get("Article", {})

                # Extract authors
                authors = []
                author_list = article_data.get("AuthorList", [])
                for author in author_list[:5]:  # Limit to first 5 authors
                    last_name = author.get("LastName", "")
                    initials = author.get("Initials", "")
                    if last_name:
                        authors.append(f"{last_name} {initials}".strip())

                # Extract abstract
                abstract_parts = article_data.get("Abstract", {}).get("AbstractText", [])
                abstract = " ".join([str(part) for part in abstract_parts]) if abstract_parts else ""

                # Extract journal and publication date
                journal = article_data.get("Journal", {})
                journal_title = journal.get("Title", "")
                pub_date = journal.get("JournalIssue", {}).get("PubDate", {})
                year = pub_date.get("Year", "")

                results.append({
                    "pmid": medline.get("PMID", ""),
                    "title": article_data.get("ArticleTitle", ""),
                    "authors": authors,
                    "journal": journal_title,
                    "year": year,
                    "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{medline.get('PMID', '')}/"
                })

            # Respect rate limits
            time.sleep(0.35)  # ~3 requests/sec without API key

        else:
            # Fetch summaries only (faster, less detailed)
            ids = ",".join(pmid_list)
            handle = Entrez.esummary(db="pubmed", id=ids, retmode="json")
            summaries = Entrez.read(handle)
            handle.close()

            for pmid in pmid_list:
                summary = summaries.get("result", {}).get(pmid, {})

                authors = summary.get("AuthorList", [])[:3]  # First 3 authors
                author_names = [f"{a.get('Name', '')}" for a in authors if isinstance(a, dict)]

                results.append({
                    "pmid": pmid,
                    "title": summary.get("Title", ""),
                    "authors": author_names,
                    "journal": summary.get("Source", ""),
                    "year": summary.get("PubDate", "").split()[0] if summary.get("PubDate") else "",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "total_found": int(search_results.get("Count", 0)),
            "results": results
        }

    except Exception as e:
        return {
            "error": f"PubMed search failed: {str(e)}",
            "query": query
        }


def main():
    """Command-line interface for PubMed search."""
    parser = argparse.ArgumentParser(
        description="Search PubMed for peer-reviewed medical research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "whiplash injury cervical spine"
  %(prog)s "traumatic brain injury long-term" --max-results 20 --sort date
  %(prog)s "lumbar disc herniation motor vehicle accident" --details

Environment Variables:
  NCBI_EMAIL: Your email (required for NCBI tracking)
  NCBI_API_KEY: (Optional) For 10 req/sec vs 3 req/sec

Output is JSON that can be piped to jq or parsed in Python.
        """
    )

    parser.add_argument(
        "query",
        help="PubMed search query"
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results to return (default: 10)"
    )

    parser.add_argument(
        "--sort",
        choices=["relevance", "date"],
        default="relevance",
        help="Sort by relevance or publication date (default: relevance)"
    )

    parser.add_argument(
        "--details",
        action="store_true",
        help="Include full abstracts and detailed metadata"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )

    args = parser.parse_args()

    # Perform search
    result = pubmed_search(
        query=args.query,
        max_results=args.max_results,
        sort=args.sort,
        include_details=args.details
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
