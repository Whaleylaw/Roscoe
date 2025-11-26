#!/usr/bin/env python3
"""
Standalone Internet Search Tool using Tavily API

This tool can be executed directly from the command line by agents.
Results are output to stdout for easy processing with grep, awk, etc.

Usage:
    python internet_search.py "your search query" [--max-results N] [--topic general|news|finance] [--include-content]

Examples:
    python internet_search.py "Kentucky statute of limitations personal injury"
    python internet_search.py "latest medical research whiplash" --max-results 10 --topic news
    python internet_search.py "expert witness neurology testimony" --include-content

Output Format:
    JSON to stdout (can be processed with jq, grep, or parsed in code)
"""

import os
import sys
import json
import argparse
from typing import Literal


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> dict:
    """
    Perform internet search using Tavily API.

    Args:
        query: The search query
        max_results: Maximum number of results (default: 5)
        topic: Search category - 'general', 'news', or 'finance'
        include_raw_content: Include full page content in results

    Returns:
        Dictionary with search results
    """
    try:
        from tavily import TavilyClient

        # Get API key from environment
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return {
                "error": "TAVILY_API_KEY environment variable not set",
                "query": query
            }

        # Initialize client and perform search
        client = TavilyClient(api_key=api_key)
        results = client.search(
            query=query,
            max_results=max_results,
            topic=topic,
            include_raw_content=include_raw_content,
        )

        return {
            "success": True,
            "query": query,
            "results": results
        }

    except ImportError:
        return {
            "error": "tavily-python package not installed. Run: pip install tavily-python",
            "query": query
        }
    except Exception as e:
        return {
            "error": f"Search failed: {str(e)}",
            "query": query
        }


def main():
    """Command-line interface for internet search."""
    parser = argparse.ArgumentParser(
        description="Internet search using Tavily API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Kentucky personal injury statute of limitations"
  %(prog)s "whiplash medical research 2025" --max-results 10 --topic news
  %(prog)s "expert witness testimony standards" --include-content

Output is JSON that can be piped to jq, grep, or parsed in Python.
        """
    )

    parser.add_argument(
        "query",
        help="Search query string"
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of results to return (default: 5)"
    )

    parser.add_argument(
        "--topic",
        choices=["general", "news", "finance"],
        default="general",
        help="Search topic category (default: general)"
    )

    parser.add_argument(
        "--include-content",
        action="store_true",
        help="Include full page content in results"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )

    args = parser.parse_args()

    # Perform search
    result = internet_search(
        query=args.query,
        max_results=args.max_results,
        topic=args.topic,
        include_raw_content=args.include_content
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
