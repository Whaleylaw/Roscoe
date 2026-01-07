"""
Lob.com Physical Mail Tools for Roscoe Paralegal Agent

This module provides tools for sending physical mail (letters, certified mail,
postcards) via Lob.com's API. All tools use lazy client initialization to
avoid LangGraph checkpointing pickle errors.

Environment Variables:
    LOB_API_KEY_TEST: Test API key (no real mail sent)
    LOB_API_KEY_LIVE: Live API key (real postage charges)
    LOB_USE_LIVE_MODE: Set to "true" to use live mode by default

Usage:
    All tools default to test mode. Use use_live_mode=True to send real mail.
    Firm return address is loaded from /Database/firm_settings.json.
"""

import os
import json
from typing import Optional, Dict, Any, Literal
from pathlib import Path
from datetime import datetime, timedelta

# Get workspace root for file operations
workspace_root = Path(os.environ.get("WORKSPACE_DIR", "/mnt/workspace"))


def _get_lob_client():
    """
    Lazily initialize Lob client to avoid pickle errors with LangGraph checkpointing.

    Returns:
        tuple: (lob module or None, mode string "test"/"live" or None)
    """
    use_live = os.environ.get("LOB_USE_LIVE_MODE", "false").lower() == "true"

    if use_live:
        api_key = os.environ.get("LOB_API_KEY_LIVE")
        mode = "live"
    else:
        api_key = os.environ.get("LOB_API_KEY_TEST")
        mode = "test"

    if not api_key:
        return None, mode

    try:
        import lob
        lob.api_key = api_key
        return lob, mode
    except ImportError:
        print("Warning: lob package not installed. Run: pip install lob")
        return None, None


def _get_firm_address() -> Optional[Dict[str, str]]:
    """Load firm return address from settings."""
    settings_path = workspace_root / "Database" / "firm_settings.json"
    try:
        if settings_path.exists():
            with open(settings_path) as f:
                settings = json.load(f)
                return settings.get("return_address")
    except Exception as e:
        print(f"Warning: Could not load firm settings: {e}")
    return None


def _format_address(address: Dict[str, str]) -> Dict[str, str]:
    """Format address dict for Lob API."""
    return {
        "name": address.get("name", ""),
        "company": address.get("company", ""),
        "address_line1": address.get("address_line1", address.get("street", "")),
        "address_line2": address.get("address_line2", ""),
        "address_city": address.get("city", address.get("address_city", "")),
        "address_state": address.get("state", address.get("address_state", "")),
        "address_zip": address.get("zip", address.get("zip_code", address.get("address_zip", ""))),
        "address_country": address.get("country", "US"),
    }


def _log_mail(mail_type: str, mail_id: str, case_name: Optional[str], recipient: str, details: Dict):
    """Log sent mail to Database/mail_log.json for tracking."""
    log_path = workspace_root / "Database" / "mail_log.json"

    entry = {
        "id": mail_id,
        "type": mail_type,
        "case_name": case_name,
        "recipient": recipient,
        "timestamp": datetime.now().isoformat(),
        "details": details
    }

    try:
        if log_path.exists():
            with open(log_path) as f:
                log = json.load(f)
        else:
            log = {"mail_entries": []}

        log["mail_entries"].insert(0, entry)

        # Keep last 1000 entries
        log["mail_entries"] = log["mail_entries"][:1000]

        with open(log_path, "w") as f:
            json.dump(log, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not log mail: {e}")


# =============================================================================
# TOOL: verify_address
# =============================================================================

def verify_address(
    address_line1: str,
    city: str,
    state: str,
    zip_code: str,
    name: Optional[str] = None,
    company: Optional[str] = None,
    address_line2: Optional[str] = None,
) -> str:
    """
    Verify a US mailing address using Lob's address verification API.

    Use this BEFORE sending mail to ensure addresses are deliverable.
    Lob will standardize, correct, and validate the address.

    Args:
        address_line1: Street address (e.g., "123 Main St")
        city: City name (e.g., "Louisville")
        state: State code (e.g., "KY")
        zip_code: ZIP code (e.g., "40202" or "40202-1234")
        name: Optional recipient name
        company: Optional company name
        address_line2: Optional second address line (suite, apt, etc.)

    Returns:
        Verification results including:
        - Standardized address
        - Deliverability status (deliverable, undeliverable, deliverable_missing_unit, etc.)
        - Any corrections made
        - Warnings or errors

    Examples:
        # Verify a client address before sending demand letter
        verify_address(
            address_line1="123 Main Street",
            city="Louisville",
            state="KY",
            zip_code="40202"
        )

        # Verify with company details
        verify_address(
            name="Claims Department",
            company="State Farm Insurance",
            address_line1="One State Farm Plaza",
            city="Bloomington",
            state="IL",
            zip_code="61710"
        )
    """
    lob, mode = _get_lob_client()
    if not lob:
        return f"Error: Lob API key not configured. Set LOB_API_KEY_{mode.upper() if mode else 'TEST'} environment variable."

    try:
        verification = lob.USVerification.create(
            primary_line=address_line1,
            secondary_line=address_line2 or "",
            city=city,
            state=state,
            zip_code=zip_code,
        )

        # Format response
        lines = [
            f"**Address Verification Results** (Mode: {mode})",
            "",
            f"**Deliverability:** {verification.deliverability}",
            "",
            "**Standardized Address:**",
            f"  {verification.primary_line}",
        ]

        if verification.secondary_line:
            lines.append(f"  {verification.secondary_line}")

        zip_full = verification.components.zip_code
        if verification.components.zip_code_plus_4:
            zip_full = f"{zip_full}-{verification.components.zip_code_plus_4}"

        lines.extend([
            f"  {verification.components.city}, {verification.components.state} {zip_full}",
            "",
            f"**County:** {verification.components.county or 'N/A'}",
        ])

        # Add warnings if not fully deliverable
        if verification.deliverability != "deliverable":
            lines.extend([
                "",
                f"**Warning:** Address may have issues - {verification.deliverability}",
            ])
            if hasattr(verification, 'deliverability_analysis'):
                analysis = verification.deliverability_analysis
                if hasattr(analysis, 'dpv_footnotes') and analysis.dpv_footnotes:
                    lines.append(f"  Details: {analysis.dpv_footnotes}")

        return "\n".join(lines)

    except Exception as e:
        return f"Address verification error: {str(e)}"


# =============================================================================
# TOOL: send_letter
# =============================================================================

def send_letter(
    recipient: Dict[str, str],
    content: str,
    case_name: Optional[str] = None,
    description: Optional[str] = None,
    color: bool = False,
    double_sided: bool = True,
    mail_type: Literal["usps_first_class", "usps_standard"] = "usps_first_class",
    return_envelope: bool = False,
    certified: bool = False,
    send_date: Optional[str] = None,
    from_address: Optional[Dict[str, str]] = None,
    use_live_mode: bool = False,
) -> str:
    """
    Send a physical letter via USPS using Lob.com.

    Use this for:
    - Demand letters to insurance companies
    - Legal notices to opposing parties
    - Correspondence to clients
    - Letters to medical providers

    The letter content can be:
    - HTML string (rendered by Lob)
    - Workspace path to PDF file (e.g., "/projects/Wilson/demand_letter.pdf")
    - Workspace path to HTML file (e.g., "/Templates/mail/demand_letter.html")

    Args:
        recipient: Recipient address dict with keys:
            - name (required): Recipient name
            - company: Optional company name
            - address_line1 (required): Street address
            - address_line2: Optional suite/apt
            - city (required): City
            - state (required): State code (e.g., "KY")
            - zip (required): ZIP code

        content: Letter content as:
            - HTML string starting with "<" (e.g., "<html>...")
            - Workspace path to PDF (e.g., "/projects/Wilson/letter.pdf")
            - Workspace path to HTML file (e.g., "/Templates/mail/demand.html")

        case_name: Case name for metadata tracking (e.g., "Wilson-MVA-2024")
        description: Internal description for this letter
        color: Print in color (default: black & white)
        double_sided: Print double-sided (default: True)
        mail_type: "usps_first_class" (2-5 days) or "usps_standard" (5-14 days)
        return_envelope: Include pre-addressed return envelope
        certified: Send as USPS Certified Mail (adds tracking)
        send_date: Schedule for future date (ISO format YYYY-MM-DD, max 180 days)
        from_address: Override firm return address (uses firm_settings.json by default)
        use_live_mode: Set True to send real mail (default: False = test mode)

    Returns:
        Confirmation with letter ID, expected delivery date, and tracking info.

    Examples:
        # Send demand letter from PDF
        send_letter(
            recipient={
                "name": "Claims Department",
                "company": "State Farm Insurance",
                "address_line1": "One State Farm Plaza",
                "city": "Bloomington",
                "state": "IL",
                "zip": "61710"
            },
            content="/projects/Wilson-MVA-2024/Negotiation Settlement/demand_letter.pdf",
            case_name="Wilson-MVA-2024",
            description="Initial demand letter",
            certified=True
        )

        # Send HTML letter
        send_letter(
            recipient={"name": "John Smith", "address_line1": "123 Main St", "city": "Louisville", "state": "KY", "zip": "40202"},
            content="<html><body><h1>Notice</h1><p>This is a legal notice...</p></body></html>",
            case_name="Smith-Case"
        )
    """
    # Temporarily override live mode if specified
    original_live_mode = os.environ.get("LOB_USE_LIVE_MODE")
    if use_live_mode:
        os.environ["LOB_USE_LIVE_MODE"] = "true"

    try:
        lob, mode = _get_lob_client()

        if not lob:
            return f"Error: Lob API key not configured. Set LOB_API_KEY_{mode.upper() if mode else 'TEST'} environment variable."

        # Get from address (firm default or override)
        from_addr = from_address or _get_firm_address()
        if not from_addr:
            return "Error: No return address configured. Set up Database/firm_settings.json or provide from_address parameter."

        # Process content - could be HTML string, PDF path, or HTML file path
        file_handle = None
        if content.strip().startswith("<"):
            # HTML string
            letter_content = content
        elif content.endswith(".pdf"):
            # PDF file path
            pdf_path = workspace_root / content.lstrip("/")
            if not pdf_path.exists():
                return f"Error: PDF file not found: {content}"
            file_handle = open(pdf_path, "rb")
            letter_content = file_handle
        elif content.endswith(".html") or content.endswith(".htm"):
            # HTML file path
            html_path = workspace_root / content.lstrip("/")
            if not html_path.exists():
                return f"Error: HTML file not found: {content}"
            with open(html_path) as f:
                letter_content = f.read()
        else:
            return "Error: Content must be HTML string (starting with <), PDF path (.pdf), or HTML file path (.html)."

        # Build metadata
        metadata = {}
        if case_name:
            metadata["case_name"] = case_name[:500]  # Lob max 500 chars per value

        # Create letter parameters
        letter_params = {
            "to_address": _format_address(recipient),
            "from_address": _format_address(from_addr),
            "file": letter_content,
            "color": color,
            "double_sided": double_sided,
            "mail_type": mail_type,
            "metadata": metadata,
            "use_type": "operational",  # Legal correspondence is operational
        }

        if description:
            letter_params["description"] = description[:255]

        if return_envelope:
            letter_params["return_envelope"] = True

        if send_date:
            letter_params["send_date"] = send_date

        # Add certified mail extra service
        if certified:
            letter_params["extra_service"] = "certified"

        # Send the letter
        letter = lob.Letter.create(**letter_params)

        # Close PDF file handle if opened
        if file_handle:
            file_handle.close()

        # Log the mail
        _log_mail(
            mail_type="letter" if not certified else "certified_letter",
            mail_id=letter.id,
            case_name=case_name,
            recipient=recipient.get("name", "Unknown"),
            details={
                "certified": certified,
                "mail_type": mail_type,
                "expected_delivery": str(letter.expected_delivery_date),
                "color": color,
            }
        )

        # Format response
        lines = [
            f"**Letter Sent Successfully** (Mode: {mode})",
            "",
            f"**Letter ID:** `{letter.id}`",
            f"**Status:** {letter.send_date}",
            f"**Expected Delivery:** {letter.expected_delivery_date}",
            "",
            "**To:**",
            f"  {recipient.get('name', '')}",
        ]

        if recipient.get('company'):
            lines.append(f"  {recipient['company']}")

        lines.extend([
            f"  {recipient.get('address_line1', '')}",
        ])

        if recipient.get('address_line2'):
            lines.append(f"  {recipient['address_line2']}")

        lines.extend([
            f"  {recipient.get('city', '')}, {recipient.get('state', '')} {recipient.get('zip', '')}",
            "",
            f"**Mail Type:** {mail_type}",
            f"**Color:** {'Yes' if color else 'No (B&W)'}",
            f"**Double-Sided:** {'Yes' if double_sided else 'No'}",
        ])

        if certified:
            lines.append("**Certified Mail:** Yes (tracking enabled)")

        if return_envelope:
            lines.append("**Return Envelope:** Included")

        if case_name:
            lines.append(f"**Case:** {case_name}")

        lines.extend([
            "",
            f"**Preview URL:** {letter.url}",
            "",
            f"*Use `check_mail_status(\"{letter.id}\")` to track delivery.*",
        ])

        if mode == "test":
            lines.extend([
                "",
                "**Note:** This is TEST MODE - no actual mail will be sent.",
                "Set `use_live_mode=True` to send real mail.",
            ])

        return "\n".join(lines)

    except Exception as e:
        return f"Letter sending error: {str(e)}"

    finally:
        # Restore original live mode setting
        if original_live_mode is not None:
            os.environ["LOB_USE_LIVE_MODE"] = original_live_mode
        elif use_live_mode:
            os.environ.pop("LOB_USE_LIVE_MODE", None)


# =============================================================================
# TOOL: send_certified_mail
# =============================================================================

def send_certified_mail(
    recipient: Dict[str, str],
    content: str,
    case_name: Optional[str] = None,
    description: Optional[str] = None,
    return_receipt: bool = True,
    send_date: Optional[str] = None,
    from_address: Optional[Dict[str, str]] = None,
    use_live_mode: bool = False,
) -> str:
    """
    Send USPS Certified Mail with tracking and optional return receipt.

    Use this for legal notices that require proof of delivery:
    - Demand letters requiring signature
    - Statutory notices (e.g., UIM claims, bad faith notices)
    - Settlement agreements
    - Termination letters
    - Time-sensitive legal deadlines

    Certified mail provides:
    - Tracking number
    - Proof of mailing
    - Delivery confirmation
    - Optional return receipt (signed by recipient)

    Args:
        recipient: Recipient address dict (same format as send_letter)
        content: Letter content (HTML string, PDF path, or HTML file path)
        case_name: Case name for tracking
        description: Internal description
        return_receipt: Request signed return receipt (default: True)
        send_date: Schedule for future date (ISO format YYYY-MM-DD)
        from_address: Override firm return address
        use_live_mode: Set True to send real mail (default: False = test mode)

    Returns:
        Confirmation with letter ID, certified tracking number, and expected delivery.

    Examples:
        # Send certified demand letter with return receipt
        send_certified_mail(
            recipient={
                "name": "Claims Manager",
                "company": "Progressive Insurance",
                "address_line1": "6300 Wilson Mills Rd",
                "city": "Mayfield Village",
                "state": "OH",
                "zip": "44143"
            },
            content="/projects/Wilson/demand_letter.pdf",
            case_name="Wilson-MVA-2024",
            description="Certified demand - 30 day response required"
        )

        # Send UIM bad faith notice
        send_certified_mail(
            recipient={"name": "Legal Dept", "company": "GEICO", ...},
            content="/projects/Smith/uim_bad_faith_notice.pdf",
            case_name="Smith-UIM-2024",
            description="Statutory UIM bad faith notice"
        )
    """
    # Add note about return receipt in description
    cert_description = description or "Certified Mail"
    if return_receipt:
        cert_description += " (Return Receipt Requested)"

    # Call send_letter with certified=True
    return send_letter(
        recipient=recipient,
        content=content,
        case_name=case_name,
        description=cert_description,
        certified=True,
        mail_type="usps_first_class",  # Certified requires first class
        send_date=send_date,
        from_address=from_address,
        use_live_mode=use_live_mode,
    )


# =============================================================================
# TOOL: send_postcard
# =============================================================================

def send_postcard(
    recipient: Dict[str, str],
    front_content: str,
    back_content: str,
    case_name: Optional[str] = None,
    description: Optional[str] = None,
    size: Literal["4x6", "6x9", "6x11"] = "4x6",
    mail_type: Literal["usps_first_class", "usps_standard"] = "usps_first_class",
    send_date: Optional[str] = None,
    from_address: Optional[Dict[str, str]] = None,
    use_live_mode: bool = False,
) -> str:
    """
    Send a postcard via USPS using Lob.com.

    Use this for:
    - Appointment reminders to clients
    - Treatment follow-up reminders
    - Holiday/seasonal client communications
    - Quick status updates
    - Marketing/outreach

    Args:
        recipient: Recipient address dict (same format as send_letter)

        front_content: Front of postcard as:
            - HTML string starting with "<"
            - Workspace path to image file (PNG, JPG)
            - Workspace path to PDF
            - Workspace path to HTML file

        back_content: Back of postcard (same content options as front)

        case_name: Case name for tracking
        description: Internal description
        size: Postcard size - "4x6" (standard), "6x9", or "6x11"
        mail_type: "usps_first_class" or "usps_standard" (4x6 requires first class)
        send_date: Schedule for future date (ISO format YYYY-MM-DD)
        from_address: Override firm return address
        use_live_mode: Set True to send real mail (default: False = test mode)

    Returns:
        Confirmation with postcard ID and expected delivery.

    Examples:
        # Send appointment reminder
        send_postcard(
            recipient={"name": "John Smith", "address_line1": "123 Main St", "city": "Louisville", "state": "KY", "zip": "40202"},
            front_content="/Templates/mail/appointment_reminder_front.html",
            back_content="<html><body><h2>Appointment Reminder</h2><p>Your follow-up is scheduled for January 15th at 2:00 PM. Please call to confirm: (502) 555-1234</p></body></html>",
            case_name="Smith-MVA-2024",
            description="Treatment follow-up reminder"
        )

        # Send with image front
        send_postcard(
            recipient={...},
            front_content="/Templates/mail/firm_logo_card.png",
            back_content="<html><body><p>Thank you for choosing our firm...</p></body></html>",
            size="6x9"
        )
    """
    # Temporarily override live mode if specified
    original_live_mode = os.environ.get("LOB_USE_LIVE_MODE")
    if use_live_mode:
        os.environ["LOB_USE_LIVE_MODE"] = "true"

    try:
        lob, mode = _get_lob_client()

        if not lob:
            return f"Error: Lob API key not configured. Set LOB_API_KEY_{mode.upper() if mode else 'TEST'} environment variable."

        from_addr = from_address or _get_firm_address()
        if not from_addr:
            return "Error: No return address configured."

        # Process front and back content
        def process_content(content_str: str, side: str):
            if content_str.strip().startswith("<"):
                return content_str
            else:
                file_path = workspace_root / content_str.lstrip("/")
                if not file_path.exists():
                    raise FileNotFoundError(f"{side} file not found: {content_str}")

                ext = file_path.suffix.lower()
                if ext in [".html", ".htm"]:
                    with open(file_path) as f:
                        return f.read()
                elif ext in [".png", ".jpg", ".jpeg", ".pdf"]:
                    return open(file_path, "rb")
                else:
                    raise ValueError(f"Unsupported {side} file type: {ext}")

        front = process_content(front_content, "front")
        back = process_content(back_content, "back")

        metadata = {}
        if case_name:
            metadata["case_name"] = case_name[:500]

        postcard_params = {
            "to_address": _format_address(recipient),
            "from_address": _format_address(from_addr),
            "front": front,
            "back": back,
            "size": size,
            "mail_type": mail_type,
            "metadata": metadata,
            "use_type": "operational",
        }

        if description:
            postcard_params["description"] = description[:255]

        if send_date:
            postcard_params["send_date"] = send_date

        postcard = lob.Postcard.create(**postcard_params)

        # Close file handles if opened
        for content in [front, back]:
            if hasattr(content, 'close'):
                content.close()

        _log_mail(
            mail_type="postcard",
            mail_id=postcard.id,
            case_name=case_name,
            recipient=recipient.get("name", "Unknown"),
            details={
                "size": size,
                "expected_delivery": str(postcard.expected_delivery_date),
            }
        )

        lines = [
            f"**Postcard Sent Successfully** (Mode: {mode})",
            "",
            f"**Postcard ID:** `{postcard.id}`",
            f"**Size:** {size}",
            f"**Expected Delivery:** {postcard.expected_delivery_date}",
            "",
            "**To:**",
            f"  {recipient.get('name', '')}",
            f"  {recipient.get('address_line1', '')}",
            f"  {recipient.get('city', '')}, {recipient.get('state', '')} {recipient.get('zip', '')}",
        ]

        if case_name:
            lines.append(f"**Case:** {case_name}")

        lines.extend([
            "",
            f"**Preview URL:** {postcard.url}",
        ])

        if mode == "test":
            lines.extend([
                "",
                "**Note:** This is TEST MODE - no actual postcard will be sent.",
            ])

        return "\n".join(lines)

    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Postcard sending error: {str(e)}"

    finally:
        if original_live_mode is not None:
            os.environ["LOB_USE_LIVE_MODE"] = original_live_mode
        elif use_live_mode:
            os.environ.pop("LOB_USE_LIVE_MODE", None)


# =============================================================================
# TOOL: check_mail_status
# =============================================================================

def check_mail_status(
    mail_id: str,
) -> str:
    """
    Check the delivery status of sent mail.

    Use this to track:
    - Letter delivery status
    - Postcard delivery status
    - Certified mail tracking events

    Args:
        mail_id: The Lob mail ID returned when mail was sent.
            - Letters start with "ltr_"
            - Postcards start with "psc_"
            - Checks start with "chk_"

    Returns:
        Current status and tracking events for the mail piece.

    Examples:
        check_mail_status("ltr_4868c3b754655f90")
        check_mail_status("psc_208e45e48d271294")
    """
    lob, mode = _get_lob_client()
    if not lob:
        return f"Error: Lob API key not configured."

    try:
        # Determine mail type from ID prefix
        if mail_id.startswith("ltr_"):
            mail = lob.Letter.retrieve(mail_id)
            mail_type = "Letter"
        elif mail_id.startswith("psc_"):
            mail = lob.Postcard.retrieve(mail_id)
            mail_type = "Postcard"
        elif mail_id.startswith("chk_"):
            mail = lob.Check.retrieve(mail_id)
            mail_type = "Check"
        else:
            return f"Error: Unknown mail type for ID: {mail_id}. Expected prefix: ltr_, psc_, or chk_"

        lines = [
            f"**{mail_type} Status** (Mode: {mode})",
            "",
            f"**ID:** `{mail.id}`",
            f"**Expected Delivery:** {mail.expected_delivery_date}",
            f"**Created:** {mail.date_created}",
        ]

        # Add send date if scheduled
        if hasattr(mail, 'send_date') and mail.send_date:
            lines.append(f"**Send Date:** {mail.send_date}")

        # Add tracking events if available (certified mail)
        if hasattr(mail, 'tracking_events') and mail.tracking_events:
            lines.extend([
                "",
                "**Tracking Events:**",
            ])
            for event in mail.tracking_events:
                location = event.location if hasattr(event, 'location') else "N/A"
                lines.append(f"  - {event.time}: {event.name} ({location})")

        # Add metadata (includes case_name)
        if hasattr(mail, 'metadata') and mail.metadata:
            lines.extend([
                "",
                "**Metadata:**",
            ])
            for key, value in mail.metadata.items():
                lines.append(f"  - {key}: {value}")

        lines.extend([
            "",
            f"**Preview URL:** {mail.url}",
        ])

        return "\n".join(lines)

    except Exception as e:
        return f"Error checking mail status: {str(e)}"


# =============================================================================
# TOOL: list_sent_mail
# =============================================================================

def list_sent_mail(
    mail_type: Optional[Literal["letter", "certified_letter", "postcard", "check", "all"]] = "all",
    case_name: Optional[str] = None,
    limit: int = 10,
    days: int = 30,
) -> str:
    """
    List recently sent mail from local log.

    This reads from the local mail log (Database/mail_log.json) which tracks
    all mail sent through these tools.

    Args:
        mail_type: Filter by type:
            - "letter": Standard letters
            - "certified_letter": Certified mail
            - "postcard": Postcards
            - "check": Checks
            - "all": All types (default)
        case_name: Filter by case name (exact match)
        limit: Maximum entries to return (default: 10, max: 100)
        days: Look back period in days (default: 30)

    Returns:
        List of sent mail with IDs, recipients, and status.

    Examples:
        # All recent mail
        list_sent_mail()

        # Letters for specific case
        list_sent_mail(mail_type="letter", case_name="Wilson-MVA-2024")

        # Last week's mail
        list_sent_mail(limit=20, days=7)

        # All certified mail
        list_sent_mail(mail_type="certified_letter")
    """
    log_path = workspace_root / "Database" / "mail_log.json"

    try:
        if not log_path.exists():
            return "No mail log found. No mail has been sent yet."

        with open(log_path) as f:
            log = json.load(f)
            entries = log.get("mail_entries", [])

        if not entries:
            return "Mail log is empty. No mail has been sent yet."

        # Filter entries
        cutoff = datetime.now() - timedelta(days=days)
        limit = min(limit, 100)  # Cap at 100

        filtered = []
        for entry in entries:
            # Filter by date
            try:
                entry_date = datetime.fromisoformat(entry["timestamp"])
                if entry_date < cutoff:
                    continue
            except (KeyError, ValueError):
                continue

            # Filter by type
            if mail_type != "all" and entry.get("type") != mail_type:
                continue

            # Filter by case
            if case_name and entry.get("case_name") != case_name:
                continue

            filtered.append(entry)

            if len(filtered) >= limit:
                break

        if not filtered:
            filters = []
            if mail_type != "all":
                filters.append(f"type={mail_type}")
            if case_name:
                filters.append(f"case={case_name}")
            filters.append(f"days={days}")
            return f"No mail found matching criteria ({', '.join(filters)})"

        lines = [
            f"**Sent Mail** (Last {days} days, showing {len(filtered)} of {len(entries)} total)",
            "",
        ]

        for i, entry in enumerate(filtered, 1):
            entry_type = entry.get('type', 'unknown').replace('_', ' ').title()
            date_str = entry.get('timestamp', '')[:10]

            lines.extend([
                f"**{i}. {entry_type}** - {date_str}",
                f"   ID: `{entry.get('id', 'N/A')}`",
                f"   To: {entry.get('recipient', 'Unknown')}",
            ])

            if entry.get('case_name'):
                lines.append(f"   Case: {entry['case_name']}")

            details = entry.get('details', {})
            if details.get('expected_delivery'):
                lines.append(f"   Expected: {details['expected_delivery']}")

            if details.get('certified'):
                lines.append("   Certified: Yes")

            lines.append("")

        lines.append("*Use `check_mail_status(\"<id>\")` to get detailed status.*")

        return "\n".join(lines)

    except Exception as e:
        return f"Error listing mail: {str(e)}"
