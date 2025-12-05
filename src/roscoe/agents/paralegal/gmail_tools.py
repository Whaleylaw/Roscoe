"""
Gmail Tools for Roscoe Paralegal Agent

Provides email functionality for case management:
- Search emails by query
- Read specific emails
- Send emails
- Create drafts
- Get email threads

All tools use lazy initialization to avoid pickle issues with LangGraph checkpointing.
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List, Literal
from datetime import datetime


def _get_gmail_service():
    """Lazily get Gmail API service."""
    from roscoe.core.google_auth import get_gmail_service
    return get_gmail_service()


def _decode_message_body(payload: dict) -> str:
    """
    Decode email body from Gmail API payload.
    Handles both simple and multipart messages.
    """
    body = ""
    
    if 'body' in payload and payload['body'].get('data'):
        # Simple message
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')
    elif 'parts' in payload:
        # Multipart message - look for text/plain or text/html
        for part in payload['parts']:
            mime_type = part.get('mimeType', '')
            if mime_type == 'text/plain' and part.get('body', {}).get('data'):
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
                break
            elif mime_type == 'text/html' and part.get('body', {}).get('data') and not body:
                # Fallback to HTML if no plain text
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
            elif 'parts' in part:
                # Nested multipart
                body = _decode_message_body(part)
                if body:
                    break
    
    return body


def _format_email_summary(msg: dict, include_body: bool = False) -> dict:
    """Format email message into a clean summary dict."""
    headers = {h['name'].lower(): h['value'] for h in msg.get('payload', {}).get('headers', [])}
    
    summary = {
        "id": msg.get('id'),
        "thread_id": msg.get('threadId'),
        "from": headers.get('from', 'Unknown'),
        "to": headers.get('to', ''),
        "cc": headers.get('cc', ''),
        "subject": headers.get('subject', '(No Subject)'),
        "date": headers.get('date', ''),
        "snippet": msg.get('snippet', ''),
        "labels": msg.get('labelIds', []),
    }
    
    if include_body:
        summary["body"] = _decode_message_body(msg.get('payload', {}))
    
    return summary


def search_emails(
    query: str,
    max_results: int = 10,
    include_spam_trash: bool = False,
) -> str:
    """
    Search Gmail inbox using Gmail search syntax.
    
    Use Gmail's powerful search operators to find specific emails:
    - from:sender@email.com - emails from specific sender
    - to:recipient@email.com - emails to specific recipient
    - subject:keyword - emails with keyword in subject
    - has:attachment - emails with attachments
    - after:2024/01/01 - emails after date
    - before:2024/12/31 - emails before date
    - is:unread - unread emails only
    - label:important - emails with specific label
    - "exact phrase" - emails containing exact phrase
    
    Args:
        query: Gmail search query (e.g., "from:client@email.com subject:Wilson case")
        max_results: Maximum number of emails to return (default: 10, max: 50)
        include_spam_trash: Include spam and trash folders (default: False)
    
    Returns:
        Summary of matching emails with id, sender, subject, date, and snippet
    
    Examples:
        search_emails("from:adjuster@insurance.com after:2024/06/01")
        search_emails("subject:Wilson MVA settlement")
        search_emails("has:attachment from:medicalrecords@hospital.com")
    """
    service = _get_gmail_service()
    if not service:
        return "Error: Gmail not configured. Set up Google OAuth credentials first."
    
    try:
        # Limit max results
        max_results = min(max_results, 50)
        
        # Search for messages
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results,
            includeSpamTrash=include_spam_trash
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            return f"No emails found matching: {query}"
        
        # Get details for each message
        email_summaries = []
        for msg in messages:
            full_msg = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            
            email_summaries.append(_format_email_summary(full_msg))
        
        # Format output
        output_lines = [f"Found {len(email_summaries)} emails matching: {query}\n"]
        
        for i, email in enumerate(email_summaries, 1):
            output_lines.append(f"**{i}. {email['subject']}**")
            output_lines.append(f"   From: {email['from']}")
            output_lines.append(f"   Date: {email['date']}")
            output_lines.append(f"   Snippet: {email['snippet'][:100]}...")
            output_lines.append(f"   ID: {email['id']}")
            output_lines.append("")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error searching emails: {str(e)}"


def get_email(
    message_id: str,
    include_attachments: bool = False,
) -> str:
    """
    Get full content of a specific email by message ID.
    
    Use this after search_emails to read the complete email body
    when you need more than just the snippet.
    
    Args:
        message_id: Gmail message ID (from search_emails results)
        include_attachments: List attachment names (default: False)
    
    Returns:
        Full email content including headers and body
    
    Examples:
        get_email("18abc123def456")
        get_email("18abc123def456", include_attachments=True)
    """
    service = _get_gmail_service()
    if not service:
        return "Error: Gmail not configured. Set up Google OAuth credentials first."
    
    try:
        msg = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        email = _format_email_summary(msg, include_body=True)
        
        # Format output
        output_lines = [
            f"**Subject:** {email['subject']}",
            f"**From:** {email['from']}",
            f"**To:** {email['to']}",
        ]
        
        if email['cc']:
            output_lines.append(f"**CC:** {email['cc']}")
        
        output_lines.extend([
            f"**Date:** {email['date']}",
            f"**Labels:** {', '.join(email['labels'])}",
            "",
            "**Body:**",
            email.get('body', '(No body content)')
        ])
        
        # List attachments if requested
        if include_attachments:
            attachments = []
            for part in msg.get('payload', {}).get('parts', []):
                filename = part.get('filename')
                if filename:
                    attachments.append(filename)
            
            if attachments:
                output_lines.extend([
                    "",
                    "**Attachments:**",
                    *[f"  - {a}" for a in attachments]
                ])
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error getting email: {str(e)}"


def send_email(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    reply_to_message_id: Optional[str] = None,
) -> str:
    """
    Send an email from the configured Gmail account.
    
    IMPORTANT: Always confirm with the attorney before sending emails
    to clients, adjusters, or opposing counsel.
    
    Args:
        to: Recipient email address(es), comma-separated for multiple
        subject: Email subject line
        body: Email body (plain text)
        cc: CC recipients (optional), comma-separated
        bcc: BCC recipients (optional), comma-separated
        reply_to_message_id: Message ID to reply to (threads the email)
    
    Returns:
        Confirmation message with sent email ID
    
    Examples:
        send_email("client@email.com", "Case Update - Wilson MVA", "Dear Mr. Wilson...")
        send_email("adjuster@insurance.com", "Re: Demand Letter", "Please find attached...", cc="attorney@firm.com")
    """
    service = _get_gmail_service()
    if not service:
        return "Error: Gmail not configured. Set up Google OAuth credentials first."
    
    try:
        # Create message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        # Attach body
        message.attach(MIMEText(body, 'plain'))
        
        # Encode message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Prepare send request
        send_body = {'raw': raw}
        
        # If replying, set thread ID
        if reply_to_message_id:
            # Get the original message to find thread ID
            original = service.users().messages().get(
                userId='me',
                id=reply_to_message_id,
                format='minimal'
            ).execute()
            send_body['threadId'] = original.get('threadId')
        
        # Send
        sent = service.users().messages().send(
            userId='me',
            body=send_body
        ).execute()
        
        return f"✅ Email sent successfully!\n   To: {to}\n   Subject: {subject}\n   Message ID: {sent['id']}"
        
    except Exception as e:
        return f"Error sending email: {str(e)}"


def create_draft(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
) -> str:
    """
    Create an email draft for attorney review before sending.
    
    Use this when composing important emails (demand letters, 
    settlement offers, client communications) that should be
    reviewed before sending.
    
    Args:
        to: Recipient email address(es)
        subject: Email subject line
        body: Email body (plain text)
        cc: CC recipients (optional)
    
    Returns:
        Confirmation with draft ID (can be edited in Gmail)
    
    Examples:
        create_draft("adjuster@insurance.com", "Demand Letter - Wilson MVA", "Dear Sir/Madam...")
        create_draft("client@email.com", "Settlement Offer Review", "We have received an offer...")
    """
    service = _get_gmail_service()
    if not service:
        return "Error: Gmail not configured. Set up Google OAuth credentials first."
    
    try:
        # Create message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        
        message.attach(MIMEText(body, 'plain'))
        
        # Encode
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Create draft
        draft = service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw}}
        ).execute()
        
        return f"📝 Draft created successfully!\n   To: {to}\n   Subject: {subject}\n   Draft ID: {draft['id']}\n\nOpen Gmail to review and send."
        
    except Exception as e:
        return f"Error creating draft: {str(e)}"


def get_thread(
    thread_id: str,
    max_messages: int = 20,
) -> str:
    """
    Get all messages in an email thread/conversation.
    
    Use this to see the full email chain for context, especially
    for ongoing negotiations or case correspondence.
    
    Args:
        thread_id: Gmail thread ID (from search_emails or get_email results)
        max_messages: Maximum messages to retrieve (default: 20)
    
    Returns:
        All emails in the thread, chronologically ordered
    
    Examples:
        get_thread("thread_abc123")
    """
    service = _get_gmail_service()
    if not service:
        return "Error: Gmail not configured. Set up Google OAuth credentials first."
    
    try:
        thread = service.users().threads().get(
            userId='me',
            id=thread_id,
            format='full'
        ).execute()
        
        messages = thread.get('messages', [])[:max_messages]
        
        if not messages:
            return f"No messages found in thread {thread_id}"
        
        output_lines = [f"**Email Thread** (ID: {thread_id})", f"Messages: {len(messages)}", ""]
        
        for i, msg in enumerate(messages, 1):
            email = _format_email_summary(msg, include_body=True)
            
            output_lines.extend([
                f"--- Message {i} ---",
                f"**From:** {email['from']}",
                f"**Date:** {email['date']}",
                f"**Subject:** {email['subject']}",
                "",
                email.get('body', '(No body)'),
                ""
            ])
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error getting thread: {str(e)}"


def list_labels() -> str:
    """
    List all Gmail labels/folders available.
    
    Returns:
        List of label names and IDs for use in searches
    """
    service = _get_gmail_service()
    if not service:
        return "Error: Gmail not configured. Set up Google OAuth credentials first."
    
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        if not labels:
            return "No labels found."
        
        output_lines = ["**Gmail Labels:**", ""]
        
        for label in sorted(labels, key=lambda x: x['name']):
            output_lines.append(f"  - {label['name']} (ID: {label['id']})")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error listing labels: {str(e)}"


def save_email_to_case(
    message_id: str,
    case_folder: str,
    subfolder: str = "Correspondence",
    include_attachments: bool = True,
    custom_filename: Optional[str] = None,
) -> str:
    """
    Save a complete email (.eml format) to a case folder in the workspace.
    
    Downloads the full email including all headers, body, and optionally 
    attachments, preserving it exactly as received. The .eml file can be 
    opened in any email client (Outlook, Thunderbird, Apple Mail, etc.).
    
    Args:
        message_id: Gmail message ID (from search_emails results)
        case_folder: Case folder name (e.g., "Queen-Huntsman-MVA-12-22-2022")
        subfolder: Subfolder within case to save to (default: "Correspondence")
        include_attachments: Also save attachments separately (default: True)
        custom_filename: Custom filename for the .eml (default: auto-generated from date/subject)
    
    Returns:
        Confirmation with saved file paths
    
    Examples:
        save_email_to_case("18abc123def", "Queen-Huntsman-MVA-12-22-2022")
        save_email_to_case("18abc123def", "Wilson-MVA-2024", subfolder="Loan Documents")
        save_email_to_case("18abc123def", "McCay-Case", custom_filename="settlement_offer.eml")
    """
    import re
    from pathlib import Path
    from email import policy
    from email.parser import BytesParser
    
    service = _get_gmail_service()
    if not service:
        return "Error: Gmail not configured. Set up Google OAuth credentials first."
    
    # Get workspace directory
    workspace_dir = os.environ.get('WORKSPACE_DIR', '/mnt/workspace')
    
    try:
        # Get the raw email (RFC 2822 format)
        msg = service.users().messages().get(
            userId='me',
            id=message_id,
            format='raw'
        ).execute()
        
        # Decode the raw message
        raw_email = base64.urlsafe_b64decode(msg['raw'])
        
        # Parse to get metadata for filename
        parsed = BytesParser(policy=policy.default).parsebytes(raw_email)
        subject = parsed.get('subject', 'no_subject')
        date_str = parsed.get('date', '')
        from_addr = parsed.get('from', 'unknown')
        
        # Parse date for filename
        try:
            # Try to parse the email date
            from email.utils import parsedate_to_datetime
            email_date = parsedate_to_datetime(date_str)
            date_prefix = email_date.strftime('%Y-%m-%d')
        except Exception:
            date_prefix = datetime.now().strftime('%Y-%m-%d')
        
        # Sanitize subject for filename
        safe_subject = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', subject)
        safe_subject = safe_subject[:50].strip()  # Limit length
        
        # Generate filename
        if custom_filename:
            if not custom_filename.endswith('.eml'):
                custom_filename += '.eml'
            eml_filename = custom_filename
        else:
            eml_filename = f"{date_prefix}_{safe_subject}.eml"
        
        # Build save path
        save_dir = Path(workspace_dir) / "projects" / case_folder / subfolder
        save_dir.mkdir(parents=True, exist_ok=True)
        
        eml_path = save_dir / eml_filename
        
        # Save the raw .eml file
        with open(eml_path, 'wb') as f:
            f.write(raw_email)
        
        saved_files = [f"📧 Email: {eml_path.relative_to(workspace_dir)}"]
        
        # Extract and save attachments if requested
        if include_attachments:
            # Get full message to find attachments
            full_msg = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            attachments_dir = save_dir / "attachments"
            
            def extract_attachments(payload, msg_id):
                """Recursively extract attachments from message parts."""
                attachments = []
                
                if 'parts' in payload:
                    for part in payload['parts']:
                        filename = part.get('filename')
                        if filename and part.get('body', {}).get('attachmentId'):
                            # Get the attachment data
                            att = service.users().messages().attachments().get(
                                userId='me',
                                messageId=msg_id,
                                id=part['body']['attachmentId']
                            ).execute()
                            
                            # Decode and save
                            data = base64.urlsafe_b64decode(att['data'])
                            
                            # Create attachments directory if needed
                            attachments_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Sanitize filename
                            safe_filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
                            att_path = attachments_dir / f"{date_prefix}_{safe_filename}"
                            
                            with open(att_path, 'wb') as f:
                                f.write(data)
                            
                            attachments.append(str(att_path.relative_to(workspace_dir)))
                        
                        # Recurse for nested parts
                        if 'parts' in part:
                            attachments.extend(extract_attachments(part, msg_id))
                
                return attachments
            
            attachment_paths = extract_attachments(full_msg.get('payload', {}), message_id)
            
            for att_path in attachment_paths:
                saved_files.append(f"📎 Attachment: {att_path}")
        
        # Build result message
        result_lines = [
            f"✅ Email saved to case folder!",
            f"",
            f"**Case:** {case_folder}",
            f"**Subfolder:** {subfolder}",
            f"**From:** {from_addr}",
            f"**Subject:** {subject}",
            f"**Date:** {date_str}",
            f"",
            f"**Saved Files:**"
        ]
        result_lines.extend([f"  - {f}" for f in saved_files])
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Error saving email: {str(e)}"


def save_emails_batch(
    message_ids: List[str],
    case_folder: str,
    subfolder: str = "Correspondence",
    include_attachments: bool = True,
) -> str:
    """
    Save multiple emails to a case folder in batch.
    
    Efficiently downloads and saves multiple emails at once.
    Use this after search_emails to save all matching emails to a case.
    
    Args:
        message_ids: List of Gmail message IDs to save
        case_folder: Case folder name (e.g., "Queen-Huntsman-MVA-12-22-2022")
        subfolder: Subfolder within case to save to (default: "Correspondence")
        include_attachments: Also save attachments (default: True)
    
    Returns:
        Summary of saved emails and any errors
    
    Examples:
        save_emails_batch(["id1", "id2", "id3"], "Queen-Huntsman-MVA-12-22-2022", "Loan Emails")
    """
    if not message_ids:
        return "Error: No message IDs provided."
    
    results = []
    success_count = 0
    error_count = 0
    
    for i, msg_id in enumerate(message_ids, 1):
        try:
            result = save_email_to_case(
                message_id=msg_id,
                case_folder=case_folder,
                subfolder=subfolder,
                include_attachments=include_attachments
            )
            
            if result.startswith("✅"):
                success_count += 1
                # Extract just the filename for summary
                results.append(f"  ✅ [{i}/{len(message_ids)}] {msg_id[:12]}... saved")
            else:
                error_count += 1
                results.append(f"  ❌ [{i}/{len(message_ids)}] {msg_id[:12]}... {result}")
                
        except Exception as e:
            error_count += 1
            results.append(f"  ❌ [{i}/{len(message_ids)}] {msg_id[:12]}... Error: {str(e)}")
    
    # Build summary
    summary = [
        f"**Batch Email Save Complete**",
        f"",
        f"**Case:** {case_folder}/{subfolder}",
        f"**Total:** {len(message_ids)} emails",
        f"**Saved:** {success_count} ✅",
        f"**Errors:** {error_count} ❌",
        f"",
        f"**Details:**"
    ]
    summary.extend(results)
    
    return "\n".join(summary)

