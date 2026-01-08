#!/usr/bin/env python3
"""
Clean Up Email Episodes

Converts messy email episodes into clean, natural language format.

Before:
    From: justin@whaleylawfirm.com
    To: adjuster@insurance.com
    [metadata, signatures, confidentiality notices...]

After:
    On November 25, 2024, Justin Chumbley emailed Justine Cruz at American Family Insurance:

    [clean message body]

Usage:
    python cleanup_email_episodes.py
    python cleanup_email_episodes.py --dry-run
    python cleanup_email_episodes.py --case "James-Kiper-MVA-12-5-2022"
"""

import json
import re
from pathlib import Path
from datetime import datetime
import argparse


def extract_email(text: str) -> str:
    """Extract email address from text like 'Name <email@domain.com>' or 'email@domain.com'"""
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else text


def extract_name_from_email(email_text: str) -> str:
    """
    Extract name from email field.

    Examples:
        "justin@whaleylawfirm.com" → "justin"
        "Justin Chumbley <justin@email.com>" → "Justin Chumbley"
        "'Aaron Whaley' [agwhaley@email.com]" → "Aaron Whaley"
    """
    # Try to find name before email
    name_match = re.search(r"(['\"]?)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\1\s*[<\[]", email_text)
    if name_match:
        return name_match.group(2)

    # Fallback: extract username from email
    email = extract_email(email_text)
    username = email.split('@')[0] if '@' in email else email

    # Clean up common patterns
    username = username.replace('.', ' ').replace('_', ' ').title()
    return username


def is_email_episode(episode_body: str) -> bool:
    """Check if this episode is an email."""
    if not episode_body:
        return False

    indicators = [
        "From:" in episode_body and ("To:" in episode_body or "Date:" in episode_body),
        "@" in episode_body and "mailto:" in episode_body,
        "Subject:" in episode_body,
        "Sent:" in episode_body and "From:" in episode_body
    ]
    return any(indicators)


def clean_email_episode(episode_body: str, episode_name: str, date: str) -> str:
    """
    Clean up an email episode into natural language format.

    Args:
        episode_body: Raw email content
        episode_name: Episode name (may contain sender info)
        date: Episode date

    Returns:
        Cleaned natural language version
    """
    lines = episode_body.split('\n')

    # Extract key fields
    from_sender = None
    to_recipient = None
    subject = None
    email_date = None
    body_lines = []

    # Flags for parsing state
    in_metadata = False
    in_signature = False
    in_confidentiality = False
    found_body_start = False

    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines at start
        if not found_body_start and not line_stripped:
            continue

        # Extract From
        if line_stripped.startswith("From:") and not from_sender:
            from_sender = line_stripped[5:].strip()
            continue

        # Extract To
        if line_stripped.startswith("To:") and not to_recipient:
            to_recipient = line_stripped[3:].strip()
            continue

        # Extract Subject
        if line_stripped.startswith("Subject:") and not subject:
            subject = line_stripped[8:].strip()
            continue

        # Extract Date (prefer email date over episode date)
        if line_stripped.startswith("Date:") or line_stripped.startswith("Sent:"):
            date_text = line_stripped.split(':', 1)[1].strip()
            if date_text and not email_date:
                email_date = date_text
            continue

        # Skip metadata sections
        if "METADATA INFORMATION" in line_stripped or "htmlFileName=" in line_stripped:
            in_metadata = True
            continue

        if in_metadata:
            if not line_stripped or line_stripped.startswith("Confidentiality"):
                in_metadata = False
            continue

        # Skip template markers
        if line_stripped.startswith("#Template:") or line_stripped.startswith("#META"):
            continue

        # Skip signature blocks (phone/fax/address)
        if re.match(r'(Ph|Phone|Fax|Office):\s*\(?\d{3}\)?', line_stripped):
            in_signature = True
            continue

        if in_signature:
            # End signature when we hit body content or confidentiality
            if line_stripped and not re.match(r'^\d+\s+\w+', line_stripped) and len(line_stripped) > 50:
                in_signature = False
            else:
                continue

        # Skip confidentiality notices
        if "Confidentiality Notice:" in line_stripped or "confidential and intended solely" in line_stripped:
            in_confidentiality = True
            continue

        if in_confidentiality:
            continue

        # Skip common email artifacts
        if any(skip in line_stripped for skip in [
            "CLAIM INFORMATION",
            "Claim Number:",
            "Policy Number:",
            "Date Of Loss:",
            "Policyholder:",
            "---Begin Message---",
            "---End Message---",
        ]):
            continue

        # Skip mailto links (keep content, strip link syntax)
        line_stripped = re.sub(r'\[([^\]]+)\]\(mailto:[^\)]+\)', r'\1', line_stripped)

        # Skip empty "From:" or other artifacts
        if line_stripped in ["From:", "To:", "Subject:", "Date:", ""]:
            continue

        # If we've found substantial content, mark body as started
        if len(line_stripped) > 20:
            found_body_start = True

        # Add to body
        if found_body_start and line_stripped:
            body_lines.append(line)

    # Extract names from email fields
    sender_name = extract_name_from_email(from_sender) if from_sender else "Unknown"
    recipient_name = extract_name_from_email(to_recipient) if to_recipient else "recipient"

    # Format date nicely
    formatted_date = email_date if email_date else date
    if formatted_date:
        try:
            # Try to parse and format
            if "GMT" in formatted_date:
                # Parse: "Mon Nov 25 2024 05:55:31 GMT-05:00"
                date_part = formatted_date.split("GMT")[0].strip()
                dt = datetime.strptime(date_part, "%a %b %d %Y %H:%M:%S")
                formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
            elif "/" in formatted_date:
                # Parse: "11/25/2024"
                dt = datetime.strptime(formatted_date.split()[0], "%m/%d/%Y")
                formatted_date = dt.strftime("%B %d, %Y")
        except:
            pass

    # Build clean version
    clean_parts = []

    # Opening line
    if subject:
        clean_parts.append(f"On {formatted_date}, {sender_name} emailed {recipient_name} regarding \"{subject}\":")
    else:
        clean_parts.append(f"On {formatted_date}, {sender_name} emailed {recipient_name}:")

    clean_parts.append("")

    # Body (join and clean up)
    body_text = '\n'.join(body_lines).strip()

    # Remove excessive blank lines
    body_text = re.sub(r'\n\n\n+', '\n\n', body_text)

    # Remove leading/trailing whitespace from each line
    body_lines_cleaned = [line.rstrip() for line in body_text.split('\n')]
    body_text = '\n'.join(body_lines_cleaned)

    clean_parts.append(body_text)

    return '\n'.join(clean_parts)


def cleanup_episodes_file(case_file: Path, dry_run: bool = False) -> dict:
    """
    Clean up email episodes in a case file.

    Returns dict with stats
    """
    # Load episodes
    with open(case_file, 'r') as f:
        episodes = json.load(f)

    stats = {
        "total": len(episodes),
        "emails_found": 0,
        "emails_cleaned": 0,
        "skipped": 0,
        "unchanged": 0
    }

    for episode in episodes:
        # Skip if already marked to skip
        if episode.get("skip"):
            stats["skipped"] += 1
            continue

        episode_body = episode.get("episode_body", "")

        # Check if it's an email
        if is_email_episode(episode_body):
            stats["emails_found"] += 1

            # Clean it
            try:
                cleaned_body = clean_email_episode(
                    episode_body,
                    episode.get("episode_name", ""),
                    episode.get("date", "")
                )

                if not dry_run:
                    episode["episode_body"] = cleaned_body

                stats["emails_cleaned"] += 1
            except Exception as e:
                print(f"   ⚠️  Error cleaning episode in {case_file.name}: {e}")
                stats["unchanged"] += 1
        else:
            stats["unchanged"] += 1

    # Write back if not dry run
    if not dry_run and stats["emails_cleaned"] > 0:
        with open(case_file, 'w') as f:
            json.dump(episodes, f, indent=2)

    return stats


def main():
    parser = argparse.ArgumentParser(description='Clean up email episodes')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--case', type=str, help='Only process this specific case file')
    args = parser.parse_args()

    by_case_dir = Path("/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/by_case")

    print("=" * 70)
    print("CLEANING EMAIL EPISODES")
    print("=" * 70)
    print(f"Directory: {by_case_dir}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Get files to process
    if args.case:
        case_files = [by_case_dir / f"{args.case}.json"]
        if not case_files[0].exists():
            print(f"❌ Case file not found: {case_files[0]}")
            return
    else:
        case_files = sorted([f for f in by_case_dir.glob("*.json") if f.is_file()])

    print(f"Processing {len(case_files)} case files...")
    print()

    # Process each file
    total_stats = {
        "total": 0,
        "emails_found": 0,
        "emails_cleaned": 0,
        "skipped": 0,
        "unchanged": 0
    }

    files_with_emails = 0

    for case_file in case_files:
        stats = cleanup_episodes_file(case_file, args.dry_run)

        # Aggregate stats
        for key in total_stats:
            total_stats[key] += stats[key]

        if stats["emails_found"] > 0:
            files_with_emails += 1
            if files_with_emails <= 10 or stats["emails_cleaned"] > 50:
                status = "[DRY RUN]" if args.dry_run else "✅"
                print(f"{status} {case_file.name}: {stats['emails_cleaned']}/{stats['emails_found']} emails cleaned")

    if files_with_emails > 10:
        print(f"   ... and {files_with_emails - 10} more files with emails")

    print()
    print("=" * 70)
    print("CLEANUP COMPLETE" if not args.dry_run else "DRY RUN COMPLETE")
    print("=" * 70)
    print(f"Total episodes: {total_stats['total']}")
    print(f"Emails found: {total_stats['emails_found']}")
    print(f"Emails cleaned: {total_stats['emails_cleaned']}")
    print(f"Already skipped: {total_stats['skipped']}")
    print(f"Unchanged (non-email): {total_stats['unchanged']}")
    print()

    if not args.dry_run:
        print(f"✅ Updated {files_with_emails} case files")
    else:
        print(f"[DRY RUN] Would update {files_with_emails} case files")

    print("=" * 70)


if __name__ == "__main__":
    main()
