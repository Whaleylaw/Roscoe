#!/usr/bin/env python3
"""
Outstanding Medical Bills Report - Pending Billing Requests

Queries medical_providers.json for bills that have been requested but not yet received.
Identifies stale billing requests that may need follow-up.

Usage:
    python /workspace/Tools/reporting/outstanding_medical_bills_report.py [--format markdown|json] [--output path]

Examples:
    # Generate markdown report to stdout
    python /workspace/Tools/reporting/outstanding_medical_bills_report.py

    # Generate JSON format
    python /workspace/Tools/reporting/outstanding_medical_bills_report.py --format json

    # Save to file
    python /workspace/Tools/reporting/outstanding_medical_bills_report.py --output /Reports/operational/outstanding_bills.md
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path


def calculate_days_since(date_str):
    """Calculate days since a date string (handles various formats)."""
    if not date_str or date_str == "null" or date_str == "None":
        return None

    try:
        # Try parsing various date formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y.%m.%d"]:
            try:
                date_obj = datetime.strptime(str(date_str).strip(), fmt)
                delta = datetime.now() - date_obj
                return delta.days
            except ValueError:
                continue

        # Try parsing Excel serial date (e.g., "45966.0")
        try:
            excel_date = float(str(date_str))
            # Excel epoch is 1899-12-30
            from datetime import timedelta
            date_obj = datetime(1899, 12, 30) + timedelta(days=excel_date)
            delta = datetime.now() - date_obj
            return delta.days
        except:
            pass

        return None
    except:
        return None


def generate_report(database_path: str, format: str = "markdown"):
    """
    Core report generation logic.

    Args:
        database_path: Path to Database directory
        format: Output format (markdown or json)

    Returns:
        Formatted report string
    """
    try:
        # Load medical providers data
        providers_file = Path(database_path) / "master_lists" / "medical_providers.json"

        if not providers_file.exists():
            return {"error": f"Database file not found: {providers_file}"}

        with open(providers_file) as f:
            providers_data = json.load(f)

        # Load caselist for client names (optional)
        caselist_file = Path(database_path) / "caselist.json"
        client_names = {}
        if caselist_file.exists():
            with open(caselist_file) as f:
                caselist = json.load(f)
                client_names = {case["project_name"]: case["client_name"] for case in caselist}

        # Filter for outstanding bills (two categories):
        # 1. Requested but not received
        # 2. Done treating but no request sent (NEEDS REQUEST)
        outstanding = []

        for provider in providers_data:
            requested = provider.get("date_medical_bills_requested")
            received = provider.get("medical_bills_received_date")
            treatment_completed = provider.get("date_treatment_completed")

            # Category 1: Requested but not received
            if requested and requested not in ["null", "None", ""]:
                if not received or received in ["null", "None", ""]:
                    provider_copy = provider.copy()
                    provider_copy["bill_status"] = "Requested"
                    outstanding.append(provider_copy)

            # Category 2: Done treating but no request sent
            elif treatment_completed and treatment_completed not in ["null", "None", ""]:
                if not requested or requested in ["null", "None", ""]:
                    provider_copy = provider.copy()
                    provider_copy["bill_status"] = "Needs Request"
                    provider_copy["days_outstanding"] = None  # No days outstanding if not requested yet
                    outstanding.append(provider_copy)

        # Calculate days outstanding for each (only for "Requested" status)
        for provider in outstanding:
            if provider.get("bill_status") == "Requested":
                requested_date = provider.get("date_medical_bills_requested")
                days = calculate_days_since(requested_date)
                provider["days_outstanding"] = days
            provider["client_name"] = client_names.get(provider["project_name"], provider["project_name"])

        # Sort by status (Needs Request first), then by days outstanding (longest first)
        outstanding.sort(key=lambda x: (
            0 if x.get("bill_status") == "Needs Request" else 1,
            -(x.get("days_outstanding") or 0)
        ))

        # Format output
        if format == "markdown":
            return format_markdown(outstanding)
        else:
            return json.dumps({
                "report_type": "outstanding_medical_bills",
                "generated": datetime.now().isoformat(),
                "total_outstanding": len(outstanding),
                "providers": outstanding
            }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Report generation failed: {str(e)}"})


def format_markdown(data):
    """Format data as markdown table."""
    output = []
    output.append("# Outstanding Medical Bills Report")
    output.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append(f"**Total Outstanding:** {len(data)}\n")

    if not data:
        output.append("*No outstanding medical bills requests found.*")
        return "\n".join(output)

    # Summary statistics
    needs_request = len([p for p in data if p.get("bill_status") == "Needs Request"])
    requested_data = [p for p in data if p.get("bill_status") == "Requested"]
    over_90 = len([p for p in requested_data if p.get("days_outstanding", 0) > 90])
    over_60 = len([p for p in requested_data if 60 < p.get("days_outstanding", 0) <= 90])
    over_30 = len([p for p in requested_data if 30 < p.get("days_outstanding", 0) <= 60])
    under_30 = len(requested_data) - over_90 - over_60 - over_30

    output.append("## Summary")
    output.append(f"- **⚠️ Needs Request (done treating, no request sent):** {needs_request}")
    output.append(f"- **Requested but not received:**")
    output.append(f"  - Over 90 days: {over_90} {'⚠️' if over_90 > 0 else ''}")
    output.append(f"  - 60-90 days: {over_60}")
    output.append(f"  - 30-60 days: {over_30}")
    output.append(f"  - Under 30 days: {under_30}\n")

    # Table header
    output.append("| Client | Provider | Status | Date Requested | Days Outstanding | Follow-up Date |")
    output.append("|--------|----------|--------|----------------|-----------------|----------------|")

    # Table rows
    for provider in data:
        client = provider.get("client_name", provider.get("project_name", "N/A"))
        provider_name = provider.get("provider_full_name", "N/A")
        status = provider.get("bill_status", "N/A")
        requested = provider.get("date_medical_bills_requested", "N/A")

        days = provider.get("days_outstanding")
        if status == "Needs Request":
            days_str = "-"
        else:
            days_str = f"{days} days" if days is not None else "N/A"
            # Add warning emoji for old requests
            if days and days > 90:
                days_str = f"⚠️ {days_str}"

        follow_up = provider.get("medical_bills_follow_up_date", "N/A")

        output.append(f"| {client} | {provider_name} | {status} | {requested} | {days_str} | {follow_up} |")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Outstanding Medical Bills Report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --format json
  %(prog)s --output /Reports/operational/outstanding_bills.md
        """
    )
    parser.add_argument(
        "--database",
        default="/workspace/Database",
        help="Path to Database directory (default: /workspace/Database)"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (optional, prints to stdout if not specified)"
    )

    args = parser.parse_args()

    # Generate report
    report = generate_report(args.database, args.format)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}", file=sys.stderr)
        sys.exit(0)
    else:
        print(report)
        sys.exit(0)


if __name__ == "__main__":
    main()
