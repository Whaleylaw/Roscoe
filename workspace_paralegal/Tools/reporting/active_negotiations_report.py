#!/usr/bin/env python3
"""
Active Negotiations Report - Comprehensive Case Status and Cross-References

Queries insurance.json for cases with is_active_negotiation = true and generates
a comprehensive attorney-ready report with full cross-references to:
- Client contact information (caselist.json, project_contacts.json)
- Outstanding liens (liens.json)
- Recent case activity (notes.json)
- Medical treatment status (medical_providers.json)
- Case folder and medical chronology availability

Usage:
    python /workspace/Tools/reporting/active_negotiations_report.py [--format markdown|json] [--output path]

Examples:
    # Generate markdown report to stdout
    python /workspace/Tools/reporting/active_negotiations_report.py

    # Generate JSON format
    python /workspace/Tools/reporting/active_negotiations_report.py --format json

    # Save to file
    python /workspace/Tools/reporting/active_negotiations_report.py --output /Reports/operational/active_negotiations.md
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


def calculate_days_since(date_str: Optional[str]) -> Optional[int]:
    """Calculate days since a date string (handles various formats)."""
    if not date_str or date_str == "null" or date_str == "None":
        return None

    try:
        # Try parsing various date formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y.%m.%d", "%Y-%m-%d %H:%M:%S"]:
            try:
                date_obj = datetime.strptime(str(date_str), fmt)
                delta = datetime.now() - date_obj
                return delta.days
            except ValueError:
                continue
        return None
    except Exception:
        return None


def parse_date(date_str: Optional[str]) -> Optional[str]:
    """Parse and format date string to YYYY-MM-DD."""
    if not date_str or date_str == "null" or date_str == "None":
        return None

    try:
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y.%m.%d"]:
            try:
                date_obj = datetime.strptime(str(date_str), fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return str(date_str)  # Return as-is if can't parse
    except Exception:
        return None


def load_database_files(database_path: Path) -> Dict[str, Any]:
    """Load all relevant database files for cross-referencing."""
    db = {}

    # Required file
    insurance_file = database_path / "master_lists" / "insurance.json"
    if not insurance_file.exists():
        raise FileNotFoundError(f"Required file not found: {insurance_file}")

    with open(insurance_file) as f:
        db["insurance"] = json.load(f)

    # Optional cross-reference files
    optional_files = {
        "caselist": database_path / "caselist.json",
        "project_contacts": database_path / "master_lists" / "project_contacts.json",
        "liens": database_path / "master_lists" / "liens.json",
        "notes": database_path / "master_lists" / "notes.json",
        "medical_providers": database_path / "master_lists" / "medical_providers.json",
        "litigation_contacts": database_path / "master_lists" / "litigation_contacts.json",
        "expenses": database_path / "master_lists" / "expenses.json"
    }

    for key, filepath in optional_files.items():
        if filepath.exists():
            with open(filepath) as f:
                db[key] = json.load(f)
        else:
            db[key] = []

    return db


def build_cross_references(project_name: str, db: Dict[str, Any]) -> Dict[str, Any]:
    """Build comprehensive cross-references for a project."""
    refs = {
        "client_name": None,
        "client_contact": None,
        "liens": [],
        "total_lien_amount": 0,
        "recent_notes": [],
        "medical_providers": [],
        "defense_counsel": None,
        "total_expenses": 0
    }

    # Client name from caselist
    if db["caselist"]:
        for case in db["caselist"]:
            if case.get("project_name") == project_name:
                refs["client_name"] = case.get("client_name")
                break

    # Client contact info from project_contacts
    if db["project_contacts"]:
        for contact in db["project_contacts"]:
            if (contact.get("project_name") == project_name and
                "client" in contact.get("roles", [])):
                refs["client_contact"] = {
                    "name": contact.get("full_name"),
                    "phone": contact.get("phone"),
                    "email": contact.get("email")
                }
                break

    # Outstanding liens
    if db["liens"]:
        for lien in db["liens"]:
            if (lien.get("project_name") == project_name and
                not lien.get("date_lien_paid")):  # Only unpaid liens
                amount = lien.get("final_lien_amount") or lien.get("amount_owed_from_settlement") or 0
                refs["liens"].append({
                    "holder": lien.get("lien_holder_name"),
                    "amount": amount,
                    "status": "Final" if lien.get("date_of_final_lien_received") else "Pending"
                })
                refs["total_lien_amount"] += amount

    # Recent notes (last 30 days)
    if db["notes"]:
        recent_notes = []
        for note in db["notes"]:
            if note.get("project_name") == project_name:
                days = calculate_days_since(note.get("last_activity"))
                if days is not None and days <= 30:
                    recent_notes.append({
                        "date": note.get("last_activity"),
                        "author": note.get("author_name"),
                        "summary": (note.get("note") or "")[:100]  # First 100 chars
                    })
        # Sort by date descending, limit to 3 most recent
        recent_notes.sort(key=lambda x: x["date"] or "", reverse=True)
        refs["recent_notes"] = recent_notes[:3]

    # Medical providers
    if db["medical_providers"]:
        providers = set()
        for provider in db["medical_providers"]:
            if provider.get("project_name") == project_name:
                providers.add(provider.get("provider_name"))
        refs["medical_providers"] = sorted(list(providers))

    # Defense counsel from litigation contacts
    if db["litigation_contacts"]:
        for contact in db["litigation_contacts"]:
            if (contact.get("project_name") == project_name and
                "defense_attorney" in contact.get("roles", [])):
                refs["defense_counsel"] = {
                    "name": contact.get("full_name"),
                    "firm": contact.get("firm_name"),
                    "phone": contact.get("phone")
                }
                break

    # Total expenses from expenses.json
    if db["expenses"]:
        for expense in db["expenses"]:
            if expense.get("project_name") == project_name:
                amount = expense.get("amount") or 0
                refs["total_expenses"] += amount

    return refs


def check_case_folder(project_name: str, workspace_path: Path) -> Dict[str, Any]:
    """Check case folder existence and medical chronology availability."""
    info = {
        "folder_exists": False,
        "chronology_exists": False,
        "chronology_path": None
    }

    # Check if case folder exists in workspace
    case_folder = workspace_path / project_name
    if case_folder.exists() and case_folder.is_dir():
        info["folder_exists"] = True

        # Check for medical chronology in Reports
        chronology_path = workspace_path / "Reports" / f"chronology_{project_name}.md"
        if chronology_path.exists():
            info["chronology_exists"] = True
            info["chronology_path"] = f"/Reports/chronology_{project_name}.md"

    return info


def generate_report(database_path: str, workspace_path: str, format: str = "markdown"):
    """
    Core report generation logic with comprehensive cross-references.

    Args:
        database_path: Path to Database directory
        workspace_path: Path to workspace root
        format: Output format (markdown or json)

    Returns:
        Formatted report string or dict
    """
    try:
        db_path = Path(database_path)
        ws_path = Path(workspace_path)

        # Load all database files
        db = load_database_files(db_path)

        # Filter for active negotiations
        active_cases = [case for case in db["insurance"] if case.get("is_active_negotiation")]

        # Enrich each case with cross-references
        enriched_cases = []
        for case in active_cases:
            project_name = case.get("project_name")

            # Build cross-references
            refs = build_cross_references(project_name, db)

            # Check case folder and chronology
            folder_info = check_case_folder(project_name, ws_path)

            # Calculate days since last activity
            dates_to_check = [
                case.get("date_demand_acknowledged"),
                case.get("date_demand_sent"),
                case.get("settlement_date")
            ]
            days_list = [calculate_days_since(d) for d in dates_to_check if d]
            days_since_activity = min(days_list) if days_list else None

            # Extract last insurance note date (parse insurance_notes for dates)
            last_note_date = None
            insurance_notes = case.get("insurance_notes") or ""
            if insurance_notes:
                # Extract dates from notes (format: YYYY.MM.DD)
                import re
                dates = re.findall(r'(\d{4}\.\d{2}\.\d{2})', insurance_notes)
                if dates:
                    last_note_date = dates[-1].replace('.', '-')  # Convert to YYYY-MM-DD
                    note_days = calculate_days_since(last_note_date)
                    if note_days is not None:
                        if days_since_activity is None or note_days < days_since_activity:
                            days_since_activity = note_days

            # Combine all data
            enriched = {
                **case,  # All insurance.json fields
                **refs,  # Cross-referenced data
                **folder_info,  # Case folder info
                "days_since_activity": days_since_activity,
                "last_activity_date": parse_date(last_note_date) if last_note_date else None
            }

            enriched_cases.append(enriched)

        # Sort by priority (days since activity, oldest first - needs attention)
        enriched_cases.sort(key=lambda x: x.get("days_since_activity") or 9999, reverse=True)

        # Format output
        if format == "markdown":
            return format_markdown(enriched_cases)
        else:
            return json.dumps({
                "report_type": "active_negotiations_comprehensive",
                "generated": datetime.now().isoformat(),
                "total_cases": len(enriched_cases),
                "cases": enriched_cases
            }, indent=2, default=str)

    except Exception as e:
        error_msg = f"Report generation failed: {str(e)}"
        if format == "json":
            return json.dumps({"error": error_msg})
        else:
            return f"ERROR: {error_msg}"


def format_markdown(cases: List[Dict[str, Any]]) -> str:
    """Format comprehensive data as markdown report."""
    output = []

    # Header
    output.append("# Active Negotiations Report")
    output.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append(f"**Total Active Cases:** {len(cases)}\n")

    if not cases:
        output.append("*No active negotiations found.*")
        return "\n".join(output)

    # Executive Summary
    output.append("## Executive Summary\n")

    total_demanded = sum(c.get("demanded_amount") or 0 for c in cases)
    total_offered = sum(c.get("current_offer") or 0 for c in cases)
    total_liens = sum(c.get("total_lien_amount") or 0 for c in cases)
    cases_with_offers = sum(1 for c in cases if c.get("current_offer"))
    cases_needing_attention = sum(1 for c in cases if (c.get("days_since_activity") or 0) > 30)

    output.append(f"- **Total Demanded:** ${total_demanded:,.2f}")
    output.append(f"- **Total Current Offers:** ${total_offered:,.2f}")
    output.append(f"- **Total Outstanding Liens:** ${total_liens:,.2f}")
    output.append(f"- **Cases with Offers:** {cases_with_offers} of {len(cases)}")
    output.append(f"- **Cases Needing Attention (>30 days):** {cases_needing_attention}\n")

    # Summary Table
    output.append("## Quick Reference Table\n")
    output.append("| Priority | Client | Insurance | Adjuster | Demand | Offer | Liens | Days Idle |")
    output.append("|----------|--------|-----------|----------|--------|-------|-------|-----------|")

    for i, case in enumerate(cases, 1):
        client = case.get("client_name") or case.get("project_name", "N/A")
        if len(client) > 20:
            client = client[:17] + "..."

        insurance = case.get("insurance_company_name", "N/A")
        if len(insurance) > 20:
            insurance = insurance[:17] + "..."

        adjuster = case.get("insurance_adjuster_name", "N/A")
        if len(adjuster) > 15:
            adjuster = adjuster[:12] + "..."

        demanded = case.get("demanded_amount")
        demand_str = f"${demanded/1000:.0f}K" if demanded else "N/A"

        offered = case.get("current_offer")
        offer_str = f"${offered/1000:.0f}K" if offered else "N/A"

        liens = case.get("total_lien_amount") or 0
        liens_str = f"${liens/1000:.0f}K" if liens > 0 else "-"

        days = case.get("days_since_activity")
        days_str = f"{days}d" if days is not None else "N/A"

        # Priority flag
        priority = "🔴" if (days or 0) > 60 else ("🟡" if (days or 0) > 30 else "🟢")

        output.append(f"| {priority} {i} | {client} | {insurance} | {adjuster} | {demand_str} | {offer_str} | {liens_str} | {days_str} |")

    output.append("\n---\n")

    # Detailed Case Breakdowns
    output.append("## Detailed Case Information\n")

    for i, case in enumerate(cases, 1):
        project_name = case.get("project_name")
        client_name = case.get("client_name") or project_name

        output.append(f"### {i}. {client_name}\n")
        output.append(f"**Project:** `{project_name}`\n")

        # Client Contact
        if case.get("client_contact"):
            contact = case["client_contact"]
            output.append("**Client Contact:**")
            if contact.get("name"):
                output.append(f"  - Name: {contact['name']}")
            if contact.get("phone"):
                output.append(f"  - Phone: {contact['phone']}")
            if contact.get("email"):
                output.append(f"  - Email: {contact['email']}")
            output.append("")

        # Insurance Information
        output.append("**Insurance Details:**")
        output.append(f"  - Company: {case.get('insurance_company_name', 'N/A')}")
        output.append(f"  - Adjuster: {case.get('insurance_adjuster_name', 'N/A')}")
        output.append(f"  - Claim #: {case.get('claim_number', 'N/A')}")
        output.append(f"  - Type: {case.get('insurance_type', 'N/A')}")
        output.append(f"  - Coverage: {case.get('coverage_confirmation', 'Unknown')}\n")

        # Negotiation Status
        output.append("**Negotiation Status:**")

        demanded = case.get("demanded_amount")
        if demanded:
            output.append(f"  - Demand: ${demanded:,.2f}")
            if case.get("date_demand_sent"):
                output.append(f"    - Sent: {parse_date(case['date_demand_sent'])}")
            if case.get("date_demand_acknowledged"):
                output.append(f"    - Acknowledged: {parse_date(case['date_demand_acknowledged'])}")
        else:
            output.append("  - Demand: **Not yet sent**")

        offered = case.get("current_offer")
        if offered:
            output.append(f"  - Current Offer: ${offered:,.2f}")
            gap = demanded - offered if demanded and offered else None
            if gap and demanded:
                gap_pct = (gap / demanded) * 100
                output.append(f"    - Gap: ${gap:,.2f} ({gap_pct:.1f}%)")
        else:
            output.append("  - Current Offer: None")

        if case.get("current_negotiation_status"):
            output.append(f"  - Status: {case['current_negotiation_status']}")

        days = case.get("days_since_activity")
        if days is not None:
            status = "🔴 URGENT" if days > 60 else ("🟡 Needs Follow-up" if days > 30 else "🟢 Active")
            output.append(f"  - **Activity Status:** {status} ({days} days since last activity)")

        output.append("")

        # Outstanding Liens
        if case.get("liens"):
            output.append("**Outstanding Liens:**")
            for lien in case["liens"]:
                output.append(f"  - {lien['holder']}: ${lien['amount']:,.2f} ({lien['status']})")
            output.append(f"  - **Total Liens:** ${case.get('total_lien_amount', 0):,.2f}\n")

        # Medical Treatment
        if case.get("medical_providers"):
            output.append("**Medical Providers:**")
            for provider in case["medical_providers"][:5]:  # Limit to 5
                output.append(f"  - {provider}")
            if len(case["medical_providers"]) > 5:
                output.append(f"  - *(+{len(case['medical_providers']) - 5} more)*")
            output.append("")

        # Case Folder Status
        if case.get("folder_exists"):
            output.append("**Case Files:**")
            output.append(f"  - Folder: `/{project_name}/` ✓")
            if case.get("chronology_exists"):
                output.append(f"  - Medical Chronology: `{case['chronology_path']}` ✓")
            else:
                output.append("  - Medical Chronology: ❌ Not generated")
            output.append("")

        # Recent Activity
        if case.get("recent_notes"):
            output.append("**Recent Activity (Last 30 Days):**")
            for note in case["recent_notes"]:
                output.append(f"  - **{note['date']}** ({note['author']}): {note['summary']}")
            output.append("")

        # Defense Counsel (if in litigation)
        if case.get("defense_counsel"):
            counsel = case["defense_counsel"]
            output.append("**Defense Counsel:**")
            output.append(f"  - Attorney: {counsel.get('name', 'N/A')}")
            if counsel.get("firm"):
                output.append(f"  - Firm: {counsel['firm']}")
            if counsel.get("phone"):
                output.append(f"  - Phone: {counsel['phone']}")
            output.append("")

        # Case Expenses
        if case.get("total_expenses") and case["total_expenses"] > 0:
            output.append(f"**Case Expenses:** ${case['total_expenses']:,.2f}\n")

        # Insurance Notes (last 200 chars)
        if case.get("insurance_notes"):
            notes = case["insurance_notes"]
            if len(notes) > 200:
                notes = "..." + notes[-200:]
            output.append("**Recent Insurance Notes:**")
            output.append(f"  {notes}\n")

        # Action Items
        output.append("**Recommended Next Steps:**")

        if not case.get("demanded_amount"):
            output.append("  - 🔴 **Prepare and send demand letter**")
        elif not case.get("current_offer") and days and days > 30:
            output.append("  - 🟡 **Follow up with adjuster on demand response**")
        elif case.get("current_offer"):
            demanded_amt = case.get("demanded_amount") or 0
            offered_amt = case.get("current_offer") or 0
            if demanded_amt > 0:
                gap_pct = ((demanded_amt - offered_amt) / demanded_amt) * 100
                if gap_pct > 50:
                    output.append("  - 🟡 **Negotiate - significant gap remains**")
                elif gap_pct > 20:
                    output.append("  - 🟢 **Continue negotiations - gap narrowing**")
                else:
                    output.append("  - 🟢 **Review offer with client - close to demand**")

        if not case.get("chronology_exists"):
            output.append("  - 📋 **Generate medical chronology for settlement presentation**")

        if case.get("liens") and not all(l["status"] == "Final" for l in case["liens"]):
            output.append("  - 📄 **Obtain final lien amounts**")

        if days and days > 60:
            output.append("  - ⚠️ **URGENT: Case has been idle for >60 days**")

        output.append("\n---\n")

    # Footer
    output.append("*Report generated by Roscoe Active Negotiations Report Tool*")
    output.append(f"*Database: `/workspace/Database/` | Workspace: `/workspace/`*")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Comprehensive Active Negotiations Report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --format json
  %(prog)s --output /Reports/operational/active_negotiations.md
  %(prog)s --workspace /custom/workspace --database /custom/database
        """
    )
    parser.add_argument(
        "--database",
        default="/Volumes/X10 Pro/Roscoe/workspace/Database",
        help="Path to Database directory (default: /Volumes/X10 Pro/Roscoe/workspace/Database)"
    )
    parser.add_argument(
        "--workspace",
        default="/Volumes/X10 Pro/Roscoe/workspace",
        help="Path to workspace root (default: /Volumes/X10 Pro/Roscoe/workspace)"
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
    report = generate_report(args.database, args.workspace, args.format)

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
