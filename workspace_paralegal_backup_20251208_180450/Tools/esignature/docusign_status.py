#!/usr/bin/env python3
"""
DocuSign Envelope Status Checker

Check the status of a DocuSign envelope (document sent for signature).

Usage:
    python docusign_status.py <envelope_id> [options]
    python docusign_status.py --list [--days 7]

Examples:
    # Check specific envelope
    python docusign_status.py abc123-def456-ghi789

    # List recent envelopes
    python docusign_status.py --list --days 30

    # Get detailed recipient status
    python docusign_status.py abc123-def456-ghi789 --recipients
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from docusign_esign import EnvelopesApi
    from docusign_config import get_config, DOCUSIGN_AVAILABLE
except ImportError:
    DOCUSIGN_AVAILABLE = False


def get_envelope_status(
    envelope_id: str,
    include_recipients: bool = False,
    use_production: bool = False
) -> dict:
    """
    Get the status of a specific envelope.
    
    Args:
        envelope_id: The DocuSign envelope ID
        include_recipients: Include detailed recipient status
        use_production: Use production DocuSign
        
    Returns:
        Dictionary with envelope status details
    """
    if not DOCUSIGN_AVAILABLE:
        return {
            "success": False,
            "error": "DocuSign SDK not installed. Run: pip install docusign-esign"
        }
    
    try:
        config = get_config(use_production=use_production)
        api_client = config.get_api_client()
        envelopes_api = EnvelopesApi(api_client)
        
        # Get envelope
        envelope = envelopes_api.get_envelope(
            account_id=config.account_id,
            envelope_id=envelope_id
        )
        
        result = {
            "success": True,
            "envelope_id": envelope.envelope_id,
            "status": envelope.status,
            "status_changed_date_time": envelope.status_changed_date_time,
            "created_date_time": envelope.created_date_time,
            "sent_date_time": envelope.sent_date_time,
            "completed_date_time": envelope.completed_date_time,
            "email_subject": envelope.email_subject,
            "environment": "production" if use_production else "demo"
        }
        
        # Map status to human-readable
        status_map = {
            "sent": "Waiting for signatures",
            "delivered": "Viewed by recipient",
            "completed": "All signatures collected",
            "declined": "Recipient declined to sign",
            "voided": "Envelope voided/cancelled",
            "created": "Draft (not sent)"
        }
        result["status_description"] = status_map.get(envelope.status, envelope.status)
        
        # Include recipient details if requested
        if include_recipients:
            recipients = envelopes_api.list_recipients(
                account_id=config.account_id,
                envelope_id=envelope_id
            )
            
            result["recipients"] = []
            for signer in recipients.signers or []:
                result["recipients"].append({
                    "name": signer.name,
                    "email": signer.email,
                    "status": signer.status,
                    "signed_date_time": signer.signed_date_time,
                    "delivered_date_time": signer.delivered_date_time,
                    "routing_order": signer.routing_order
                })
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get envelope status: {str(e)}",
            "envelope_id": envelope_id
        }


def list_recent_envelopes(
    days: int = 7,
    status_filter: str = None,
    use_production: bool = False
) -> dict:
    """
    List recent envelopes.
    
    Args:
        days: Number of days to look back
        status_filter: Filter by status (sent, completed, etc.)
        use_production: Use production DocuSign
        
    Returns:
        Dictionary with list of envelopes
    """
    if not DOCUSIGN_AVAILABLE:
        return {
            "success": False,
            "error": "DocuSign SDK not installed. Run: pip install docusign-esign"
        }
    
    try:
        config = get_config(use_production=use_production)
        api_client = config.get_api_client()
        envelopes_api = EnvelopesApi(api_client)
        
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # List envelopes
        kwargs = {
            "account_id": config.account_id,
            "from_date": from_date
        }
        if status_filter:
            kwargs["status"] = status_filter
        
        envelopes_list = envelopes_api.list_status_changes(**kwargs)
        
        envelopes = []
        for env in envelopes_list.envelopes or []:
            envelopes.append({
                "envelope_id": env.envelope_id,
                "status": env.status,
                "email_subject": env.email_subject,
                "created_date_time": env.created_date_time,
                "sent_date_time": env.sent_date_time,
                "completed_date_time": env.completed_date_time
            })
        
        return {
            "success": True,
            "envelopes": envelopes,
            "count": len(envelopes),
            "from_date": from_date,
            "status_filter": status_filter,
            "environment": "production" if use_production else "demo"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list envelopes: {str(e)}"
        }


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Check DocuSign envelope status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "envelope_id",
        nargs="?",
        help="Envelope ID to check (optional if using --list)"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List recent envelopes"
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=7,
        help="Days to look back for --list (default: 7)"
    )
    parser.add_argument(
        "--status", "-s",
        choices=["sent", "delivered", "completed", "declined", "voided", "created"],
        help="Filter by status (for --list)"
    )
    parser.add_argument(
        "--recipients", "-r",
        action="store_true",
        help="Include detailed recipient status"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Use production DocuSign (default: demo/sandbox)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output"
    )
    
    args = parser.parse_args()
    
    if args.list:
        result = list_recent_envelopes(
            days=args.days,
            status_filter=args.status,
            use_production=args.production
        )
    elif args.envelope_id:
        result = get_envelope_status(
            envelope_id=args.envelope_id,
            include_recipients=args.recipients,
            use_production=args.production
        )
    else:
        parser.print_help()
        sys.exit(1)
    
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))
    
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

