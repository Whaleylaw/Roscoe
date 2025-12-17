#!/usr/bin/env python3
"""
DocuSign Send Document for Signature

Send a document to one or more signers via DocuSign.
Supports PDF documents and configurable signature placement.

Usage:
    python docusign_send.py <document_path> --signer-email <email> --signer-name <name> [options]

Examples:
    # Send retainer agreement
    python docusign_send.py "/path/to/retainer.pdf" \
        --signer-email "client@email.com" \
        --signer-name "John Smith" \
        --subject "Please sign: Retainer Agreement"

    # Send with specific signature anchor
    python docusign_send.py "/path/to/hipaa.pdf" \
        --signer-email "client@email.com" \
        --signer-name "John Smith" \
        --anchor "/sig1/"

    # Send to multiple signers
    python docusign_send.py "/path/to/document.pdf" \
        --signer-email "client@email.com" --signer-name "John Smith" \
        --signer-email "spouse@email.com" --signer-name "Jane Smith"
"""

import argparse
import json
import sys
import base64
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from docusign_esign import EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients
    from docusign_config import get_config, DOCUSIGN_AVAILABLE
except ImportError:
    DOCUSIGN_AVAILABLE = False


def send_document(
    document_path: str,
    signer_emails: list[str],
    signer_names: list[str],
    subject: str = "Please sign this document",
    message: str = "Please review and sign this document.",
    anchor_string: str = "/sig1/",
    use_production: bool = False
) -> dict:
    """
    Send a document for signature via DocuSign.
    
    Args:
        document_path: Path to the PDF document to send
        signer_emails: List of signer email addresses
        signer_names: List of signer names (same order as emails)
        subject: Email subject line
        message: Email body message
        anchor_string: Text anchor for signature placement (e.g., "/sig1/")
        use_production: Use production DocuSign (default: demo/sandbox)
        
    Returns:
        Dictionary with envelope_id, status, and other details
    """
    if not DOCUSIGN_AVAILABLE:
        return {
            "success": False,
            "error": "DocuSign SDK not installed. Run: pip install docusign-esign"
        }
    
    # Validate inputs
    doc_path = Path(document_path)
    if not doc_path.exists():
        return {
            "success": False,
            "error": f"Document not found: {document_path}"
        }
    
    if len(signer_emails) != len(signer_names):
        return {
            "success": False,
            "error": "Number of signer emails must match number of signer names"
        }
    
    if not signer_emails:
        return {
            "success": False,
            "error": "At least one signer is required"
        }
    
    try:
        # Get configuration and API client
        config = get_config(use_production=use_production)
        api_client = config.get_api_client()
        
        # Read document
        with open(doc_path, "rb") as f:
            document_bytes = f.read()
        
        document_b64 = base64.b64encode(document_bytes).decode("ascii")
        
        # Determine file extension
        file_ext = doc_path.suffix.lower().lstrip(".")
        if file_ext not in ["pdf", "doc", "docx"]:
            file_ext = "pdf"
        
        # Create document object
        document = Document(
            document_base64=document_b64,
            name=doc_path.name,
            file_extension=file_ext,
            document_id="1"
        )
        
        # Create signers with signature tabs
        signers = []
        for i, (email, name) in enumerate(zip(signer_emails, signer_names), start=1):
            # Create signature tab with anchor
            sign_here = SignHere(
                anchor_string=anchor_string if i == 1 else f"/sig{i}/",
                anchor_units="pixels",
                anchor_y_offset="10",
                anchor_x_offset="20"
            )
            
            # If no anchor found, use fixed position
            sign_here_fixed = SignHere(
                document_id="1",
                page_number="1",
                x_position="100",
                y_position="700"
            )
            
            signer = Signer(
                email=email,
                name=name,
                recipient_id=str(i),
                routing_order=str(i),
                tabs=Tabs(sign_here_tabs=[sign_here])
            )
            signers.append(signer)
        
        # Create envelope
        envelope_definition = EnvelopeDefinition(
            email_subject=subject,
            email_blurb=message,
            documents=[document],
            recipients=Recipients(signers=signers),
            status="sent"  # "sent" to send immediately, "created" for draft
        )
        
        # Send envelope
        envelopes_api = EnvelopesApi(api_client)
        result = envelopes_api.create_envelope(
            account_id=config.account_id,
            envelope_definition=envelope_definition
        )
        
        return {
            "success": True,
            "envelope_id": result.envelope_id,
            "status": result.status,
            "status_date_time": result.status_date_time,
            "uri": result.uri,
            "document": doc_path.name,
            "signers": [{"email": e, "name": n} for e, n in zip(signer_emails, signer_names)],
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "environment": "production" if use_production else "demo"
        }
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"DocuSign API error: {str(e)}"
        }


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Send a document for signature via DocuSign",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "document",
        help="Path to the document to send (PDF, DOC, DOCX)"
    )
    parser.add_argument(
        "--signer-email", "-e",
        action="append",
        required=True,
        dest="signer_emails",
        help="Signer email address (can specify multiple)"
    )
    parser.add_argument(
        "--signer-name", "-n",
        action="append",
        required=True,
        dest="signer_names",
        help="Signer name (must match number of emails)"
    )
    parser.add_argument(
        "--subject", "-s",
        default="Please sign this document",
        help="Email subject line"
    )
    parser.add_argument(
        "--message", "-m",
        default="Please review and sign this document at your earliest convenience.",
        help="Email body message"
    )
    parser.add_argument(
        "--anchor", "-a",
        default="/sig1/",
        help="Signature anchor string in document (default: /sig1/)"
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
    
    result = send_document(
        document_path=args.document,
        signer_emails=args.signer_emails,
        signer_names=args.signer_names,
        subject=args.subject,
        message=args.message,
        anchor_string=args.anchor,
        use_production=args.production
    )
    
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))
    
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()

