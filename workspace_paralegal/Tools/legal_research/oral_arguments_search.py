#!/usr/bin/env python3
"""
Oral Arguments Search with Auto-Transcription

Search appellate court oral arguments with automatic speech-to-text transcription.
Essential for analyzing attorney performance, reviewing appellate strategy, and
understanding judicial questioning patterns.

Usage:
    python oral_arguments_search.py "your search query" [--court COURT] [--after-date YYYY-MM-DD] [--max-results N]

Examples:
    python oral_arguments_search.py "personal injury damages"
    python oral_arguments_search.py "whiplash causation" --court ca6 --max-results 10
    python oral_arguments_search.py "expert witness testimony" --after-date 2020-01-01

Output Format:
    JSON to stdout with case names, courts, dates, duration, judges, full transcript, and MP3 URLs

Court Codes:
    scotus - Supreme Court of the United States
    ca1, ca2, ..., ca11, cadc, cafc - Federal Circuit Courts
    ca6 - 6th Circuit (covers Kentucky, Michigan, Ohio, Tennessee)
    State appellate courts also available (check /api/rest/v4/courts/)

API Notes:
    - Requires COURTLISTENER_API_KEY environment variable
    - Automatic speech-to-text transcription included
    - Audio files available for download (MP3)
    - Transcripts searchable and exportable

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


def oral_arguments_search(
    query: str,
    max_results: int = 10,
    court: Optional[str] = None,
    after_date: Optional[str] = None,
) -> dict:
    """
    Search CourtListener v4 API for oral arguments with transcripts.

    Args:
        query: Search query string
        max_results: Maximum number of results (default: 10)
        court: Court identifier (e.g., 'scotus', 'ca6')
        after_date: Filter arguments after this date (YYYY-MM-DD format)

    Returns:
        Dictionary with search results including case names, transcripts, audio URLs
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
        base_url = "https://www.courtlistener.com/api/rest/v4/audio/"

        params = {
            "case_name": query,
            "page_size": min(max_results, 20)  # API max per page is 20
        }

        # Add filters
        if court:
            params["court"] = court
        if after_date:
            params["date_created__gte"] = after_date

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
            # Get basic info
            case_name = item.get("case_name", "")
            court_info = item.get("docket", "")
            date_created = item.get("date_created", "")
            duration = item.get("duration", 0)

            # Panel judges
            judges = item.get("judges", "")

            # Audio download
            download_url = item.get("download_url", "")
            local_path = item.get("local_path_mp3", "")

            # Transcript (the gold mine!)
            transcript = item.get("stt_transcript", "")
            transcript_status = item.get("stt_status", 0)  # 1 = complete, 0 = pending

            # Format duration (seconds to MM:SS)
            duration_formatted = f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"

            # Truncate transcript for preview (full version available in transcript field)
            transcript_preview = transcript[:500] + "..." if len(transcript) > 500 else transcript

            results.append({
                "case_name": case_name,
                "court": court if court else "Unknown",
                "date_created": date_created.split("T")[0] if "T" in date_created else date_created,
                "duration": duration_formatted,
                "duration_seconds": duration,
                "judges": judges,
                "transcript_status": "Complete" if transcript_status == 1 else "Pending",
                "transcript_preview": transcript_preview,
                "transcript_full": transcript,  # Full transcript available
                "audio_url": download_url,
                "audio_path": local_path,
                "url": f"https://www.courtlistener.com{item.get('absolute_url', '')}" if item.get('absolute_url') else ""
            })

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "total_found": data.get("count", 0) if isinstance(data.get("count"), int) else "Unknown",
            "results": results
        }

    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}: {e.reason}"
        if e.code == 401:
            error_msg += " (Invalid API key)"
        elif e.code == 429:
            error_msg += " (Rate limit exceeded - try again later)"
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
            "error": f"Oral arguments search failed: {str(e)}",
            "query": query
        }


def main():
    """Command-line interface for oral arguments search."""
    parser = argparse.ArgumentParser(
        description="Search oral arguments with automatic transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "personal injury damages"
  %(prog)s "whiplash causation medical evidence" --court ca6 --max-results 10
  %(prog)s "expert witness Daubert" --after-date 2020-01-01

Features:
  - Automatic speech-to-text transcription of oral arguments
  - Search by case name, court, date
  - Audio files available for download (MP3)
  - Panel judges and argument duration
  - Full searchable transcripts

Output includes:
  - Case name and court
  - Argument date and duration
  - Panel judges
  - Full transcript (auto-generated)
  - MP3 download URL
  - CourtListener page URL

Use Cases:
  - Analyze attorney performance and argumentation
  - Review successful appellate strategies
  - Understand judicial questioning patterns
  - Prepare for oral arguments
  - Find precedent on specific legal arguments

Output is JSON that can be piped to jq or parsed in Python.
        """
    )

    parser.add_argument(
        "query",
        help="Search query string (searches case names)"
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results to return (default: 10)"
    )

    parser.add_argument(
        "--court",
        help="Court identifier (e.g., 'scotus', 'ca6', 'ca9')"
    )

    parser.add_argument(
        "--after-date",
        help="Filter arguments after this date (YYYY-MM-DD)"
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )

    args = parser.parse_args()

    # Perform search
    result = oral_arguments_search(
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
