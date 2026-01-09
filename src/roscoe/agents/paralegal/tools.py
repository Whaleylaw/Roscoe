"""
Roscoe Paralegal Agent Tools

This module provides tools for the paralegal agent:
- Internet search (Tavily)
- Multimodal analysis (image, audio, video)
- Slack notifications
- Script execution with GCS filesystem access (Docker)
- Knowledge graph read/write (direct Cypher)
- Workflow state management
"""

import os
import json
import re
from typing import Literal, Optional, Any, List, Dict
from pathlib import Path
from tavily import TavilyClient
from langchain_core.messages import HumanMessage
import base64

# Import multimodal LLM getter for analyze_image, analyze_audio, analyze_video tools
# IMPORTANT: Use the getter function, not the module-level variable (which is None)
from roscoe.agents.paralegal.models import get_multimodal_llm

# GCS bucket name (client created lazily to avoid pickle errors)
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "whaley_law_firm")

# NOTE: script_executor was removed in favor of ShellToolMiddleware
# The middleware provides a persistent shell session with Glob/Grep tools
# pointing to LOCAL_WORKSPACE for fast file access

# Import Lob.com physical mail tools
from roscoe.agents.paralegal.lob_tools import (
    verify_address,
    send_letter,
    send_certified_mail,
    send_postcard,
    check_mail_status,
    list_sent_mail,
)

# =============================================================================
# LAZY CLIENT INITIALIZATION
# These clients contain thread locks that can't be serialized by LangGraph
# checkpointing. We create them only when needed, not at module import time.
# =============================================================================

def _get_gcs_client():
    """Lazily initialize GCS client to avoid pickle errors with LangGraph checkpointing."""
    try:
        from google.cloud import storage
        client = storage.Client()
        return client, client.bucket(GCS_BUCKET_NAME)
    except Exception as e:
        print(f"Warning: GCS client initialization failed: {e}")
        return None, None


def _get_tavily_client():
    """Lazily initialize Tavily client to avoid pickle errors."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return None
    try:
        return TavilyClient(api_key=api_key)
    except Exception as e:
        print(f"Warning: Tavily client initialization failed: {e}")
        return None




def _get_slack_client():
    """Lazily initialize Slack client to avoid pickle errors."""
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        return None
    try:
        from slack_sdk import WebClient
        return WebClient(token=token)
    except ImportError:
        print("Warning: slack-sdk not installed. Slack integration disabled.")
        return None

# Import workspace resolver for hybrid local/GCS file operations
from roscoe.core.workspace_resolver import (
    resolve_path,
    is_text_file,
    sync_file_to_gcs,
    LOCAL_WORKSPACE,
    GCS_WORKSPACE,
)

# NOTE: File operations now use resolve_path() from workspace_resolver module which routes
# text files to LOCAL_WORKSPACE and binary files to GCS_WORKSPACE


# Define the internet search tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> str:
    """
    Internet search tool able to provide detailed search results and page content.

    Args:
        query: The search query to perform.
        max_results: Maximum number of results to return (default: 5).
        topic: The category of search - 'general', 'news', or 'finance' (default: 'general').
        include_raw_content: Whether to include raw page content in results (default: False).

    Returns:
        A string containing the top search results and page content.
    """
    # Lazy initialization to avoid pickle errors
    client = _get_tavily_client()
    if not client:
        return "Error: Tavily API key not configured. Set TAVILY_API_KEY environment variable."

    try:
        search_results = client.search(
            query=query,
            max_results=max_results,
            topic=topic,
            include_raw_content=include_raw_content,
        )
        return search_results

    except Exception as e:
        return f"Search error: {str(e)}"


# Define the image analysis tool
def analyze_image(
    file_path: str,
    analysis_prompt: Optional[str] = None,
) -> str:
    """
    Analyze an image file using Google Gemini's multimodal vision capabilities.

    Perfect for analyzing accident photos, scene documentation, injury photos,
    property damage, or any visual evidence in personal injury cases.

    Args:
        file_path: Workspace-relative path to the image file (e.g., "/case_folder/photos/accident_scene.jpg")
        analysis_prompt: Optional specific analysis instructions. If not provided, uses legal evidence default.

    Returns:
        Detailed analysis of the image with legally relevant observations.

    Examples:
        analyze_image("/mo_alif/photos/accident_scene_01.jpg")
        analyze_image("/mo_alif/photos/vehicle_damage.jpg", "Describe the extent and location of vehicle damage")
    """
    try:
        # Convert workspace-relative path to absolute path
        # Images are binary files - always use GCS workspace mount
        if file_path.startswith('/'):
            file_path = file_path[1:]  # Remove leading slash
        abs_path = GCS_WORKSPACE / file_path

        if not abs_path.exists():
            return f"Error: Image file not found at {file_path}"

        # Read and encode image
        with open(abs_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Determine image type
        ext = abs_path.suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')

        # Default legal evidence analysis prompt
        if not analysis_prompt:
            analysis_prompt = """Analyze this image as legal evidence in a personal injury case. Provide:

1. **Overall Description**: What the image shows
2. **Key Observable Details**: Specific details visible (conditions, damage, injuries, positions, etc.)
3. **Scene Conditions**: Lighting, weather, environment (if applicable)
4. **Damage/Injury Assessment**: Extent and nature of any damage or injuries visible
5. **Legally Relevant Observations**: Details that could support or weaken case theories
6. **Text/Signs Visible**: Any readable text, signs, or labels
7. **Timestamp/Metadata**: Any visible timestamps or identifying information

Be specific, objective, and thorough. Focus on facts, not conclusions."""

        # Create message with image using Gemini's inline_data format
        message = HumanMessage(
            content=[
                {"type": "text", "text": analysis_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{image_data}"}
                }
            ]
        )

        # Get analysis from LLM (lazily initialized)
        response = get_multimodal_llm().invoke([message])

        return f"**Image Analysis: {file_path}**\n\n{response.content}"

    except Exception as e:
        return f"Image analysis error: {str(e)}"


# Define the audio analysis tool (uses OpenAI Whisper for transcription)
def analyze_audio(
    file_path: str,
    analysis_focus: Optional[str] = None,
) -> str:
    """
    Transcribe and analyze an audio file using OpenAI Whisper.

    Perfect for analyzing 911 calls, witness statements, dispatch recordings,
    recorded depositions, or any audio evidence in personal injury cases.

    Args:
        file_path: Workspace-relative path to the audio file (e.g., "/case_folder/audio/911_call.mp3")
        analysis_focus: Optional specific analysis focus for post-transcription analysis.

    Returns:
        Transcription and analysis of the audio with legally relevant observations.

    Examples:
        analyze_audio("/mo_alif/investigation/911_call_03-15-2024.mp3")
        analyze_audio("/mo_alif/investigation/witness_statement.wav", "Focus on the witness's description of the accident sequence")
    """
    try:
        from openai import OpenAI
        
        # Convert workspace-relative path to absolute path
        # Audio files are binary - always use GCS workspace mount
        if file_path.startswith('/'):
            file_path = file_path[1:]  # Remove leading slash
        abs_path = GCS_WORKSPACE / file_path

        if not abs_path.exists():
            return f"Error: Audio file not found at {file_path}"

        # Check file size - Whisper has a 25MB limit
        file_size_mb = abs_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 25:
            return f"Error: Audio file is {file_size_mb:.1f}MB, exceeds Whisper's 25MB limit. Please compress or split the file."

        # Supported formats for Whisper
        supported_formats = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}
        ext = abs_path.suffix.lower()
        if ext not in supported_formats:
            return f"Error: Unsupported audio format '{ext}'. Supported: {', '.join(supported_formats)}"

        # Initialize OpenAI client
        client = OpenAI()
        
        # Transcribe with Whisper
        with open(abs_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",  # Get timestamps
                timestamp_granularities=["segment"]
            )
        
        # Format the transcription with timestamps
        transcript_text = transcription.text
        segments = getattr(transcription, 'segments', [])
        
        # Build formatted output
        result_parts = [f"**Audio Transcription: {file_path}**\n"]
        result_parts.append(f"Duration: {transcription.duration:.1f} seconds\n")
        result_parts.append(f"Language: {transcription.language}\n\n")
        
        result_parts.append("## Full Transcript\n\n")
        result_parts.append(transcript_text)
        result_parts.append("\n\n")
        
        # Add timestamped segments if available
        if segments:
            result_parts.append("## Timestamped Segments\n\n")
            for seg in segments:
                # Segments are objects with attributes, not dicts
                start = getattr(seg, 'start', 0)
                end = getattr(seg, 'end', 0)
                text = getattr(seg, 'text', '')
                result_parts.append(f"[{start:.1f}s - {end:.1f}s] {text}\n")
        
        # If analysis focus provided, add note for agent to analyze
        if analysis_focus:
            result_parts.append(f"\n\n## Analysis Focus\n\n{analysis_focus}\n")
            result_parts.append("\n*Note: Use the transcript above to provide analysis based on the focus area.*")

        return "".join(result_parts)

    except ImportError:
        return "Error: OpenAI package not installed. Run: pip install openai"
    except Exception as e:
        return f"Audio transcription error: {str(e)}"


# Define the video analysis tool
def analyze_video(
    file_path: str,
    analysis_focus: Optional[str] = None,
    extract_key_frames: bool = False,
) -> str:
    """
    Analyze a video file using Google Gemini's multimodal video capabilities.

    Perfect for analyzing body camera footage, dashcam videos, surveillance footage,
    deposition videos, or any video evidence in personal injury cases.

    Args:
        file_path: Workspace-relative path to the video file (e.g., "/case_folder/video/bodycam.mp4")
        analysis_focus: Optional specific analysis instructions. If not provided, uses comprehensive legal analysis.
        extract_key_frames: If True, will note timestamps for key moments (frames can be extracted separately).

    Returns:
        Comprehensive video analysis with timeline, transcription, and visual observations.

    Examples:
        analyze_video("/mo_alif/investigation/bodycam_footage.mp4")
        analyze_video("/mo_alif/investigation/dashcam.mp4", "Focus on traffic signals and vehicle positions", extract_key_frames=True)
    """
    try:
        # Convert workspace-relative path to absolute path
        # Video files are binary - always use GCS workspace mount
        if file_path.startswith('/'):
            file_path = file_path[1:]  # Remove leading slash
        abs_path = GCS_WORKSPACE / file_path

        if not abs_path.exists():
            return f"Error: Video file not found at {file_path}"

        # Read and encode video
        with open(abs_path, 'rb') as f:
            video_data = base64.b64encode(f.read()).decode('utf-8')

        # Determine video type
        ext = abs_path.suffix.lower()
        mime_types = {
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.webm': 'video/webm',
            '.mkv': 'video/x-matroska'
        }
        mime_type = mime_types.get(ext, 'video/mp4')

        # Default legal evidence analysis prompt
        if not analysis_focus:
            analysis_focus = f"""Analyze this video as legal evidence in a personal injury case. Provide:

1. **Video Overview**: Duration, general content, and context
2. **Visual Timeline**: Chronological description of what's visible, with timestamps
3. **Audio Transcription**: Complete transcript of all speech with speaker identification and timestamps
4. **Scene Conditions**: Lighting, weather, visibility throughout video
5. **Key Visual Details**: Important objects, positions, movements, actions visible
6. **Incident Documentation**: If accident/incident visible, detailed description with timestamp
7. **Environmental Factors**: Road conditions, obstacles, signage, traffic signals visible
8. **Person/Vehicle Identification**: Description of people, vehicles, license plates if visible
9. **Legally Relevant Observations**: Visual or audio evidence supporting/weakening case theories
{'10. **Key Frame Timestamps**: Specific timestamps for critical moments requiring frame extraction' if extract_key_frames else ''}

Be thorough and precise. Quote audio verbatim. Note exact timestamps for all significant events."""

        # Create message with video using Gemini's inline_data format
        message = HumanMessage(
            content=[
                {"type": "text", "text": analysis_focus},
                {
                    "type": "media",
                    "data": video_data,
                    "mime_type": mime_type
                }
            ]
        )

        # Get analysis from LLM (lazily initialized)
        response = get_multimodal_llm().invoke([message])

        analysis_result = f"**Video Analysis: {file_path}**\n\n{response.content}"

        if extract_key_frames:
            analysis_result += "\n\n**NOTE**: To extract frames at the timestamps mentioned above, use the bash tool with ffmpeg:\n"
            analysis_result += f"Example: `ffmpeg -i {file_path} -ss HH:MM:SS -frames:v 1 /Reports/frames/frame_description_HH-MM-SS.jpg`"

        return analysis_result

    except Exception as e:
        return f"Video analysis error: {str(e)}"


# Define the Slack notification tool
def send_slack_message(
    message: str,
    channel: Optional[str] = None,
    thread_ts: Optional[str] = None,
    urgency: Literal["normal", "high", "urgent"] = "normal",
) -> str:
    """
    Send a message to Slack about task completion, updates, or alerts.

    Use this to notify about important events like:
    - Task completions (medical analysis done, research complete)
    - Red flags or concerns discovered
    - Case status updates
    - Errors or issues requiring attention

    Args:
        message: The message content to send
        channel: Slack channel (e.g., "#legal-updates") or user ID. Defaults to #legal-updates
        thread_ts: Optional thread timestamp to reply in a thread
        urgency: "normal", "high", or "urgent" - adds appropriate emoji

    Returns:
        Confirmation message or error

    Examples:
        send_slack_message("Medical analysis complete for Wilson case", "#wilson-case")
        send_slack_message("⚠️ Red flag: 6-month treatment gap detected", urgency="high")
        send_slack_message("Research complete on Kentucky comparative negligence", "#legal-research")
    """
    # Lazy initialization to avoid pickle errors
    client = _get_slack_client()
    if not client:
        return "Slack integration not configured. Set SLACK_BOT_TOKEN environment variable."

    try:
        # Default channel
        if channel is None:
            channel = os.environ.get("SLACK_DEFAULT_CHANNEL", "#legal-updates")

        # Add emoji based on urgency
        emoji_map = {
            "normal": "✅",
            "high": "⚠️",
            "urgent": "🚨"
        }

        formatted_message = f"{emoji_map.get(urgency, '📢')} {message}"

        # Send message
        response = client.chat_postMessage(
            channel=channel,
            text=formatted_message,
            thread_ts=thread_ts
        )

        return f"Message sent to {channel}"

    except Exception as e:
        return f"Failed to send Slack message: {str(e)}"


# =============================================================================
# FILE OPERATIONS TOOLS
# =============================================================================

def move_file(
    source_path: str,
    destination_path: str,
    overwrite: bool = False,
) -> str:
    """
    Move a file from one location to another in the workspace.

    Use this when:
    - A tool creates a file in /Reports/ and you need to move it to a case folder
    - User uploads a document that needs to be filed in the correct bucket
    - Reorganizing files between folders
    - Renaming a file (move to same directory with new name)

    Args:
        source_path: Workspace-relative path to the file to move.
            Example: "/Reports/docket_lookup_result.json"
        destination_path: Workspace-relative path where file should go.
            Example: "/projects/Abby-Sitgraves-MVA-7-13-2024/Litigation/docket.json"
        overwrite: If True, overwrite destination if it exists. Default: False.

    Returns:
        Confirmation message with old and new paths.

    Examples:
        # Move a docket file to case folder
        move_file(
            source_path="/Reports/docket_lookup.json",
            destination_path="/projects/Abby-Sitgraves-MVA-7-13-2024/Litigation/docket.json"
        )

        # Move uploaded document to appropriate bucket
        move_file(
            source_path="/uploads/medical_record.pdf",
            destination_path="/projects/Wilson-MVA-2024/Medical Records/spine_mri.pdf"
        )

        # Rename a file
        move_file(
            source_path="/Reports/summary.md",
            destination_path="/Reports/wilson_case_summary.md"
        )
    """
    import shutil

    try:
        # Normalize paths (keep original for messages)
        clean_source = source_path.lstrip('/')
        clean_dest = destination_path.lstrip('/')

        # Use workspace resolver for path resolution (routes to local or GCS based on file type)
        abs_source = resolve_path(source_path, 'read')
        abs_dest = resolve_path(destination_path, 'write')

        # Validate source exists
        if not abs_source.exists():
            return f"❌ Source file not found: {source_path}"

        if not abs_source.is_file():
            return f"❌ Source is not a file: {source_path}"

        # Check destination
        if abs_dest.exists() and not overwrite:
            return f"❌ Destination already exists: {destination_path}\nUse overwrite=True to replace."

        # Create destination directory if needed
        abs_dest.parent.mkdir(parents=True, exist_ok=True)

        # Move the file
        shutil.move(str(abs_source), str(abs_dest))

        # Sync to GCS if destination is a text file in local workspace
        if is_text_file(clean_dest):
            sync_file_to_gcs(clean_dest)

        return f"""✅ File moved successfully

**From**: {source_path}
**To**: {destination_path}"""

    except PermissionError:
        return f"❌ Permission denied moving file"
    except Exception as e:
        return f"❌ Error moving file: {str(e)}"


def copy_file(
    source_path: str,
    destination_path: str,
    overwrite: bool = False,
) -> str:
    """
    Copy a file from one location to another in the workspace.

    Use this when:
    - You need a file in multiple locations
    - Creating a backup before modifying
    - Duplicating a template for a new use

    Args:
        source_path: Workspace-relative path to the file to copy.
            Example: "/Templates/demand_letter.docx"
        destination_path: Workspace-relative path for the copy.
            Example: "/projects/Wilson-MVA-2024/Negotiation Settlement/demand_letter_draft.docx"
        overwrite: If True, overwrite destination if it exists. Default: False.

    Returns:
        Confirmation message with source and destination paths.

    Examples:
        # Copy a template for a case
        copy_file(
            source_path="/Templates/demand_letter.docx",
            destination_path="/projects/Wilson-MVA-2024/Negotiation Settlement/demand_draft.docx"
        )

        # Create a backup
        copy_file(
            source_path="/projects/Wilson-MVA-2024/notes.json",
            destination_path="/projects/Wilson-MVA-2024/notes_backup.json"
        )
    """
    import shutil

    try:
        # Normalize paths (keep original for messages)
        clean_source = source_path.lstrip('/')
        clean_dest = destination_path.lstrip('/')

        # Use workspace resolver for path resolution (routes to local or GCS based on file type)
        abs_source = resolve_path(source_path, 'read')
        abs_dest = resolve_path(destination_path, 'write')

        # Validate source exists
        if not abs_source.exists():
            return f"❌ Source file not found: {source_path}"

        if not abs_source.is_file():
            return f"❌ Source is not a file: {source_path}"

        # Check destination
        if abs_dest.exists() and not overwrite:
            return f"❌ Destination already exists: {destination_path}\nUse overwrite=True to replace."

        # Create destination directory if needed
        abs_dest.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file (preserve metadata with copy2)
        shutil.copy2(str(abs_source), str(abs_dest))

        # Sync to GCS if destination is a text file in local workspace
        if is_text_file(clean_dest):
            sync_file_to_gcs(clean_dest)

        return f"""✅ File copied successfully

**From**: {source_path}
**To**: {destination_path}"""

    except PermissionError:
        return f"❌ Permission denied copying file"
    except Exception as e:
        return f"❌ Error copying file: {str(e)}"


def display_document(
    file_path: str,
    title: Optional[str] = None,
) -> str:
    """
    Display a document or artifact in the UI canvas (right panel).

    Use this when:
    - You've created an HTML report/visualization and want to show it to the user
    - You want to display a PDF, Word doc, or other viewable file
    - You want to highlight a specific document for the user to review
    - After creating any artifact that the user should see immediately

    The UI will automatically open the right panel and display the document.

    Supported file types:
    - HTML (.html) - Rendered in secure sandbox
    - PDF (.pdf) - Displayed with page controls
    - Word (.docx) - Converted to viewable format
    - Markdown (.md) - Rendered with formatting
    - Images (.png, .jpg, .gif) - Displayed directly

    Args:
        file_path: Workspace-relative path to the file to display.
            Example: "/Reports/case_timeline.html"
            Example: "/projects/Wilson-MVA-2024/Medical Records/MRI_report.pdf"
        title: Optional display title. Defaults to filename.

    Returns:
        JSON response indicating the file to display (UI will handle rendering).

    Examples:
        # Display an HTML timeline you just created
        display_document("/Reports/wilson_timeline.html", "Wilson Case Timeline")

        # Show a PDF to the user
        display_document("/projects/Wilson-MVA-2024/Medical Records/spine_mri.pdf")

        # Display a demand letter draft
        display_document("/projects/Wilson-MVA-2024/Negotiation Settlement/demand_draft.html")
    """
    try:
        # Normalize path
        if file_path.startswith('/'):
            file_path = file_path[1:]

        # Use workspace resolver to route to local (text) or GCS (binary)
        abs_path = resolve_path(file_path, 'read')

        # Validate file exists
        if not abs_path.exists():
            return f"❌ File not found: {file_path}"

        if not abs_path.is_file():
            return f"❌ Path is not a file: {file_path}"

        # Determine file type
        ext = abs_path.suffix.lower()
        type_map = {
            '.html': 'html',
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.doc': 'docx',
            '.md': 'md',
            '.markdown': 'md',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.gif': 'image',
            '.webp': 'image',
        }

        doc_type = type_map.get(ext, 'unknown')
        if doc_type == 'unknown':
            return f"⚠️ Unsupported file type: {ext}. Supported: .html, .pdf, .docx, .md, images"

        # Return a special JSON structure that the UI will detect
        # The path should have leading slash for the UI
        display_path = f"/{file_path}" if not file_path.startswith('/') else file_path
        display_title = title or abs_path.name

        # Return structured response that UI can parse
        return json.dumps({
            "__display_document__": True,
            "path": display_path,
            "type": doc_type,
            "title": display_title,
        })

    except Exception as e:
        return f"❌ Error displaying document: {str(e)}"


def upload_file_to_slack(
    file_path: str,
    channel: Optional[str] = None,
    title: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """
    Upload a file (report, document, etc.) to Slack.

    Use this to share analysis reports, summaries, or other documents directly in Slack.

    Args:
        file_path: Workspace-relative path to file (e.g., "/Reports/summary_Wilson.md")
        channel: Slack channel to upload to. Defaults to #legal-updates
        title: Title for the file in Slack
        comment: Optional comment/message with the file upload

    Returns:
        Confirmation message or error

    Examples:
        upload_file_to_slack("/Reports/FINAL_SUMMARY_Wilson.md", "#wilson-case", "Final Medical Analysis")
        upload_file_to_slack("/Reports/causation_analysis.md", title="Causation Report", comment="Strong causation found")
    """
    # Lazy initialization to avoid pickle errors
    client = _get_slack_client()
    if not client:
        return "Slack integration not configured. Set SLACK_BOT_TOKEN environment variable."

    try:
        # Convert workspace-relative path to absolute path
        if file_path.startswith('/'):
            file_path = file_path[1:]
        # Use workspace resolver to route to local (text) or GCS (binary)
        abs_path = resolve_path(file_path, 'read')

        if not abs_path.exists():
            return f"Error: File not found at {file_path}"

        # Default channel
        if channel is None:
            channel = os.environ.get("SLACK_DEFAULT_CHANNEL", "#legal-updates")

        # Default title
        if title is None:
            title = abs_path.name

        # Upload file
        response = client.files_upload_v2(
            channel=channel,
            file=str(abs_path),
            title=title,
            initial_comment=comment
        )

        return f"File uploaded to {channel}: {title}"

    except Exception as e:
        return f"Failed to upload file to Slack: {str(e)}"


# =============================================================================
# GCS (Google Cloud Storage) Tools
# For uploading files to cloud storage and getting signed URLs
# =============================================================================

def save_to_gcs(
    local_path: str,
    gcs_path: Optional[str] = None,
    content_type: Optional[str] = None,
) -> str:
    """
    Upload a file from the workspace to Google Cloud Storage.

    Use this when:
    - You've generated a large file (PDF, image) that needs cloud storage
    - You want to ensure a file is backed up to cloud storage
    - You need to make a file available via a shareable URL
    - You're saving binary files that shouldn't be stored locally

    Args:
        local_path: Workspace-relative path to the file to upload.
            Example: "/Reports/case_timeline.html"
        gcs_path: Optional destination path in GCS. If not provided, uses the same
            path as local_path. Example: "/projects/Wilson/reports/timeline.html"
        content_type: Optional MIME type (auto-detected if not provided).
            Example: "application/pdf", "text/html"

    Returns:
        Confirmation with GCS path, or error message.

    Note: This tool only uploads - it does NOT delete files from GCS.

    Examples:
        # Upload a generated PDF report
        save_to_gcs("/Reports/medical_summary.pdf")

        # Upload with custom destination
        save_to_gcs(
            local_path="/Reports/timeline.html",
            gcs_path="/projects/Wilson-MVA-2024/Reports/final_timeline.html"
        )
    """
    try:
        # Get GCS client lazily
        client, bucket = _get_gcs_client()
        if not bucket:
            return "Error: GCS client not available. Check GCS credentials."

        # Resolve local path using workspace resolver
        abs_local = resolve_path(local_path, 'read')

        if not abs_local.exists():
            return f"Error: Local file not found: {local_path}"

        if not abs_local.is_file():
            return f"Error: Path is not a file: {local_path}"

        # Determine GCS destination path
        if gcs_path is None:
            gcs_path = local_path
        clean_gcs_path = gcs_path.lstrip('/')

        # Auto-detect content type if not provided
        if content_type is None:
            import mimetypes
            content_type, _ = mimetypes.guess_type(str(abs_local))

        # Upload to GCS
        blob = bucket.blob(clean_gcs_path)
        blob.upload_from_filename(str(abs_local), content_type=content_type)

        return f"""✅ File uploaded to GCS successfully

**Local**: {local_path}
**GCS**: gs://{GCS_BUCKET_NAME}/{clean_gcs_path}
**Size**: {abs_local.stat().st_size:,} bytes"""

    except Exception as e:
        return f"Error uploading to GCS: {str(e)}"


def get_gcs_url(
    gcs_path: str,
    expiration_minutes: int = 60,
) -> str:
    """
    Get a signed URL for a file stored in Google Cloud Storage.

    Use this when:
    - You need to share a PDF or large file with the user via URL
    - The UI needs to display a file stored in GCS
    - You want to provide temporary access to a binary file
    - You're sharing evidence or documents externally

    Args:
        gcs_path: Path to the file in GCS bucket.
            Example: "/projects/Wilson-MVA-2024/Medical Records/spine_mri.pdf"
        expiration_minutes: How long the URL should be valid (default: 60 minutes).
            Maximum: 7 days (10080 minutes)

    Returns:
        Signed URL that can be used to access the file directly.

    Note: This tool only reads - it does NOT delete files from GCS.

    Examples:
        # Get URL for a PDF
        get_gcs_url("/projects/Wilson-MVA-2024/Medical Records/mri_report.pdf")

        # Get longer-lived URL (24 hours)
        get_gcs_url("/Reports/final_analysis.pdf", expiration_minutes=1440)
    """
    from datetime import timedelta

    try:
        # Get GCS client lazily
        client, bucket = _get_gcs_client()
        if not bucket:
            return "Error: GCS client not available. Check GCS credentials."

        clean_path = gcs_path.lstrip('/')

        # Get the blob
        blob = bucket.blob(clean_path)

        # Check if file exists
        if not blob.exists():
            return f"Error: File not found in GCS: {gcs_path}"

        # Cap expiration at 7 days
        expiration_minutes = min(expiration_minutes, 10080)

        # Generate signed URL
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET",
        )

        return f"""✅ Signed URL generated (valid for {expiration_minutes} minutes)

**GCS Path**: gs://{GCS_BUCKET_NAME}/{clean_path}
**URL**: {url}"""

    except Exception as e:
        return f"Error generating GCS URL: {str(e)}"


def list_gcs_files(
    prefix: str = "",
    max_results: int = 100,
) -> str:
    """
    List files in Google Cloud Storage under a given prefix/path.

    Use this when:
    - You need to see what files exist in GCS for a case
    - You're looking for binary files (PDFs, images) that aren't stored locally
    - You want to browse the cloud storage contents

    Args:
        prefix: Path prefix to filter files. Example: "/projects/Wilson-MVA-2024/"
        max_results: Maximum number of files to return (default: 100)

    Returns:
        List of files with their sizes and paths.

    Examples:
        # List all files in a case folder
        list_gcs_files("/projects/Wilson-MVA-2024/")

        # List only Medical Records
        list_gcs_files("/projects/Wilson-MVA-2024/Medical Records/")

        # List root directories
        list_gcs_files("/", max_results=50)
    """
    try:
        # Get GCS client lazily
        client, bucket = _get_gcs_client()
        if not bucket:
            return "Error: GCS client not available. Check GCS credentials."

        clean_prefix = prefix.lstrip('/')

        # List blobs
        blobs = list(bucket.list_blobs(prefix=clean_prefix, max_results=max_results))

        if not blobs:
            return f"No files found under: {prefix}"

        # Format results
        result_lines = [f"**Files in GCS** (prefix: `{prefix}`)\n"]

        total_size = 0
        for blob in blobs:
            size = blob.size or 0
            total_size += size
            size_str = f"{size:,}" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
            result_lines.append(f"- `{blob.name}` ({size_str})")

        result_lines.append(f"\n**Total**: {len(blobs)} files, {total_size/(1024*1024):.1f}MB")

        if len(blobs) == max_results:
            result_lines.append(f"\n*Results limited to {max_results} files*")

        return "\n".join(result_lines)

    except Exception as e:
        return f"Error listing GCS files: {str(e)}"


# =============================================================================
# NOTE: Script execution tools (execute_python_script, execute_python_script_with_browser)
# were removed in favor of ShellToolMiddleware which provides:
# - Persistent shell session with Glob/Grep file search
# - Direct access to LOCAL_WORKSPACE for fast text file operations
# - Native filesystem access without Docker overhead
# =============================================================================


# =============================================================================
# Skills Discovery Tools
# =============================================================================

def list_skills() -> str:
    """
    List all available skills with their YAML descriptions.
    
    Use this tool when you need to:
    - See what skills are available for a task
    - Find the right skill for a specific workflow
    - Understand what capabilities are available
    
    The middleware automatically injects relevant skills based on user messages,
    but you can use this tool to manually browse and select skills when needed.
    
    Returns:
        Formatted list of all available skills with their descriptions,
        triggers, and requirements.
    
    Examples:
        list_skills()  # Show all available skills
    """
    try:
        from roscoe.core.skill_middleware import get_middleware_instance
        
        middleware = get_middleware_instance()
        if middleware is None:
            return "Error: Skill middleware not initialized. Skills may not be available yet."
        
        return middleware.get_skills_summary()
        
    except ImportError:
        return "Error: Could not import skill middleware."
    except Exception as e:
        return f"Error listing skills: {str(e)}"


def refresh_skills() -> str:
    """
    Rescan skills directory and reload all skills.
    
    Use this if new skills have been added mid-session and you want
    to make them available without restarting.
    
    Returns:
        Confirmation message with number of skills loaded.
    
    Examples:
        refresh_skills()  # Reload all skills from disk
    """
    try:
        from roscoe.core.skill_middleware import get_middleware_instance
        
        middleware = get_middleware_instance()
        if middleware is None:
            return "Error: Skill middleware not initialized."
        
        count = middleware.refresh_skills()
        return f"✅ Skills refreshed. Loaded {count} skills."
        
    except ImportError:
        return "Error: Could not import skill middleware."
    except Exception as e:
        return f"Error refreshing skills: {str(e)}"


def load_skill(skill_name: str) -> str:
    """
    Load a specific skill by name and return its full content.
    
    Use this when:
    - The middleware didn't auto-select the skill you need
    - You want to explicitly use a specific skill
    - You need to see the full skill instructions
    
    Args:
        skill_name: Name of the skill to load (e.g., "pdf", "docx", "medical-records-analysis")
    
    Returns:
        Full skill content (SKILL.md) or error message if not found.
    
    Examples:
        load_skill("pdf")  # Load the PDF skill
        load_skill("docx")  # Load the DOCX skill
        load_skill("medical-records-analysis")  # Load medical records skill
    """
    try:
        from roscoe.core.skill_middleware import get_middleware_instance
        
        middleware = get_middleware_instance()
        if middleware is None:
            return "Error: Skill middleware not initialized."
        
        skill = middleware.get_skill_by_name(skill_name)
        if skill is None:
            # Try to find similar skills
            available = [s['name'] for s in middleware.manifest['skills']]
            return f"Skill '{skill_name}' not found. Available skills: {', '.join(available)}"
        
        # Load and return full skill content
        content = middleware._load_skill_file(skill['file'])
        return f"# Skill: {skill_name}\n\n{content}"
        
    except ImportError:
        return "Error: Could not import skill middleware."
    except Exception as e:
        return f"Error loading skill: {str(e)}"


# =============================================================================
# KNOWLEDGE GRAPH WRITE TOOL (Direct Cypher)
# =============================================================================
# This tool creates entities and relationships using direct Cypher queries.
# Agent must reference KNOWLEDGE_GRAPH_SCHEMA.md for correct entity types and properties.

def write_entity(
    entity_type: str,
    properties: Dict[str, Any],
    relationships: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Create an entity in the knowledge graph with optional relationships.

    This is the universal write tool for creating any entity type. The agent
    must reference KNOWLEDGE_GRAPH_SCHEMA.md to understand valid entity types,
    required properties, and relationship patterns.

    Args:
        entity_type: The entity type to create (e.g., "BIClaim", "Facility", "InsurancePolicy")
            Must match an entity type from the schema. Common types:
            - Case, Client, Defendant
            - Facility, Location, HealthSystem
            - BIClaim, PIPClaim, UMClaim, UIMClaim, WCClaim
            - InsurancePolicy, InsurancePayment
            - Insurer, Adjuster
            - Lien, LienHolder
            - Attorney, LawFirm, LawFirmOffice
            - MedicalVisit, Bill, Expense
            - CourtEvent, Pleading
            - Document (for associating files to entities)

        properties: Dict of entity properties (e.g., {"name": "State Farm", "phone": "800-555-1234"})
            Common properties:
            - name (REQUIRED for most entities)
            - All other properties are entity-specific (see schema)

        relationships: Optional list of relationships to create. Each dict contains:
            - rel_type: Relationship type (e.g., "UNDER_POLICY", "TREATED_AT", "PART_OF")
            - target_entity_type: Type of target entity (e.g., "InsurancePolicy", "Facility")
            - target_properties: Dict to match target entity (e.g., {"name": "Policy-123"})
            - direction: "outgoing" (default) or "incoming"

    Returns:
        Confirmation message with created entity and relationships.

    Examples:
        # Create a BI claim with insurance policy relationship
        write_entity(
            entity_type="BIClaim",
            properties={
                "claim_number": "17-87C986K",
                "status": "active",
                "date_filed": "2025-12-01",
                "amount_demanded": 50000.00
            },
            relationships=[
                {
                    "rel_type": "UNDER_POLICY",
                    "target_entity_type": "InsurancePolicy",
                    "target_properties": {"policy_number": "POL-123456"}
                },
                {
                    "rel_type": "HAS_CLAIM",
                    "target_entity_type": "Case",
                    "target_properties": {"name": "Christopher-Lanier-MVA-6-28-2025"},
                    "direction": "incoming"
                }
            ]
        )

        # Create a medical facility
        write_entity(
            entity_type="Facility",
            properties={
                "name": "Norton Orthopedic Institute",
                "specialty": "Orthopedics",
                "phone": "502-555-1234",
                "records_request_method": "portal",
                "records_request_url": "https://norton.org/records"
            },
            relationships=[
                {
                    "rel_type": "PART_OF",
                    "target_entity_type": "HealthSystem",
                    "target_properties": {"name": "Norton Healthcare"}
                }
            ]
        )

        # Create treatment relationship
        write_entity(
            entity_type="Location",
            properties={
                "name": "Starlight Chiropractic",
                "address": "123 Main St, Louisville, KY",
                "phone": "502-555-9999"
            },
            relationships=[
                {
                    "rel_type": "TREATED_AT",
                    "target_entity_type": "Client",
                    "target_properties": {"name": "Christopher Lanier"},
                    "direction": "incoming"
                }
            ]
        )
    """
    import asyncio

    try:
        from roscoe.core.graphiti_client import run_cypher_query

        async def _create_entity():
            # Build property string for Cypher CREATE
            prop_items = []
            for key, value in properties.items():
                if isinstance(value, str):
                    # Escape quotes in strings
                    escaped_value = value.replace("'", "\\'")
                    prop_items.append(f"{key}: '{escaped_value}'")
                elif isinstance(value, (int, float)):
                    prop_items.append(f"{key}: {value}")
                elif isinstance(value, bool):
                    prop_items.append(f"{key}: {str(value).lower()}")
                elif value is None:
                    continue  # Skip null values
                else:
                    # For complex types, convert to string
                    prop_items.append(f"{key}: '{str(value)}'")

            props_str = ", ".join(prop_items)

            # Create the entity
            create_query = f"""
                CREATE (e:{entity_type} {{{props_str}}})
                RETURN e.name as name, labels(e)[0] as type
            """

            result = await run_cypher_query(create_query)

            if not result:
                return {"error": "Entity creation failed - no result returned"}

            created_entity = result[0]
            entity_name = created_entity.get("name")

            # Create relationships if specified
            created_relationships = []
            if relationships:
                for rel in relationships:
                    rel_type = rel.get("rel_type")
                    target_type = rel.get("target_entity_type")
                    target_props = rel.get("target_properties", {})
                    direction = rel.get("direction", "outgoing")

                    if not rel_type or not target_type or not target_props:
                        continue

                    # Build match condition for target
                    target_match_items = []
                    for key, value in target_props.items():
                        if isinstance(value, str):
                            escaped = value.replace("'", "\\'")
                            target_match_items.append(f"{key}: '{escaped}'")
                        else:
                            target_match_items.append(f"{key}: {value}")

                    target_match_str = ", ".join(target_match_items)

                    # Create relationship query
                    if direction == "incoming":
                        # Target -> Created Entity
                        rel_query = f"""
                            MATCH (source:{entity_type} {{name: '{entity_name}'}})
                            MATCH (target:{target_type} {{{target_match_str}}})
                            CREATE (target)-[r:{rel_type}]->(source)
                            RETURN type(r) as rel_type
                        """
                    else:
                        # Created Entity -> Target
                        rel_query = f"""
                            MATCH (source:{entity_type} {{name: '{entity_name}'}})
                            MATCH (target:{target_type} {{{target_match_str}}})
                            CREATE (source)-[r:{rel_type}]->(target)
                            RETURN type(r) as rel_created
                        """

                    try:
                        rel_result = await run_cypher_query(rel_query)
                        if rel_result:
                            created_relationships.append({
                                "type": rel_type,
                                "target": target_type,
                                "direction": direction
                            })
                    except Exception as e:
                        # Log error but continue with other relationships
                        created_relationships.append({
                            "type": rel_type,
                            "error": str(e)[:100]
                        })

            return {
                "success": True,
                "entity": {
                    "type": entity_type,
                    "name": entity_name,
                    "properties": properties
                },
                "relationships_created": created_relationships
            }

        result = _run_async(_create_entity())

        if result.get("error"):
            return f"❌ Entity creation failed: {result['error']}"

        # Format success response
        output = [
            f"✅ Entity created in knowledge graph",
            "",
            f"**Type**: {result['entity']['type']}",
            f"**Name**: {result['entity']['name']}",
            ""
        ]

        if result.get("relationships_created"):
            output.append(f"**Relationships** ({len(result['relationships_created'])} created):")
            for rel in result['relationships_created']:
                if "error" in rel:
                    output.append(f"  ❌ {rel['type']}: {rel['error']}")
                else:
                    arrow = "<-" if rel['direction'] == "incoming" else "->"
                    output.append(f"  ✅ {arrow}[:{rel['type']}]{arrow} {rel['target']}")

        return "\n".join(output)

    except Exception as e:
        return f"❌ Error creating entity: {str(e)}"


# =============================================================================
# KNOWLEDGE GRAPH READ TOOLS
# =============================================================================
# Reading tools use direct Cypher or semantic search.

def query_case_graph(
    query: str,
    case_name: Optional[str] = None,
    max_results: int = 20,
) -> str:
    """
    Search the knowledge graph using natural language.
    
    This tool performs semantic search across all case data stored in Graphiti.
    It can find information even if you don't know the exact wording - the graph
    understands meaning and relationships.
    
    Args:
        query: Natural language question or search query. Examples:
            - "What insurance claims are open for this case?"
            - "Who is the adjuster for the State Farm claim?"
            - "What medical providers treated the client?"
            - "When was the demand sent?"
        case_name: Optional case folder name to scope the search.
            If provided, only searches within that case's data.
            If omitted, searches across all cases.
        max_results: Maximum number of results to return (default: 20)
    
    Returns:
        Relevant facts and information from the knowledge graph.
    
    Examples:
        query_case_graph("What is the status of the BI claim?", case_name="Christopher-Lanier-MVA-6-28-2025")
        query_case_graph("Which cases have Progressive insurance?")
        query_case_graph("What treatments did the client receive?", case_name="Wilson-MVA-2024")
    """
    import asyncio
    
    graphiti_enabled = os.environ.get("GRAPHITI_ENABLED", "true").lower() == "true"
    
    if not graphiti_enabled:
        return "Error: Knowledge graph is disabled. Set GRAPHITI_ENABLED=true to enable."
    
    try:
        from roscoe.core.graphiti_client import search_case_episodes, get_case_entities
        
        async def _search():
            return await search_case_episodes(
                query=query,
                case_name=case_name,
                num_results=max_results,
            )
        
        # Run async in sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _search())
                    results = future.result(timeout=60)
            else:
                results = asyncio.run(_search())
        except RuntimeError:
            results = asyncio.run(_search())
        
        if not results:
            scope = f" for case {case_name}" if case_name else ""
            return f"No results found{scope}. The case may not be in the knowledge graph yet, or the query didn't match any stored information."
        
        # Format results
        output_lines = [f"## Knowledge Graph Search Results\n"]
        output_lines.append(f"**Query**: {query}")
        if case_name:
            output_lines.append(f"**Case**: {case_name}")
        output_lines.append(f"**Results**: {len(results)} facts found\n")
        
        for i, result in enumerate(results, 1):
            fact = getattr(result, 'fact', str(result))
            output_lines.append(f"{i}. {fact}")
        
        return "\n".join(output_lines)
        
    except ImportError as e:
        return f"Error: Graphiti client not available. {str(e)}"
    except Exception as e:
        return f"Error querying knowledge graph: {str(e)}"


def graph_query(
    query_type: Literal[
        "cases_by_provider",
        "cases_by_insurer",
        "provider_stats",
        "insurer_stats",
        "entity_relationships",
        "case_graph",
        "custom_cypher"
    ],
    entity_name: Optional[str] = None,
    case_name: Optional[str] = None,
    custom_query: Optional[str] = None,
) -> str:
    """
    Query the knowledge graph directly for structural/relationship data.
    
    Unlike query_case_graph (which uses semantic search), this tool runs
    Cypher queries against the graph database for exact structural queries.
    Much faster for relationship-based lookups.
    
    Args:
        query_type: Type of query to run:
            - "cases_by_provider": All cases for a medical provider
            - "cases_by_insurer": All cases with claims against an insurer
            - "provider_stats": Provider frequency across all cases
            - "insurer_stats": Insurance company frequency across all cases
            - "entity_relationships": All relationships for an entity
            - "case_graph": Full graph structure for a case (nodes + edges)
            - "custom_cypher": Run a custom Cypher query
        entity_name: Name to search for (required for cases_by_*, entity_relationships)
        case_name: Case folder name (required for case_graph)
        custom_query: Cypher query string (required for custom_cypher)
    
    Returns:
        Formatted results from the graph query.
    
    Examples:
        # Find all cases where Allstar Chiropractic treated the client
        graph_query("cases_by_provider", entity_name="Allstar Chiropractic")
        
        # Find all cases with State Farm claims
        graph_query("cases_by_insurer", entity_name="State Farm")
        
        # Get provider statistics
        graph_query("provider_stats")
        
        # Get full graph for a case
        graph_query("case_graph", case_name="Christopher-Lanier-MVA-6-28-2025")
    """
    import asyncio
    
    graphiti_enabled = os.environ.get("GRAPHITI_ENABLED", "true").lower() == "true"
    
    if not graphiti_enabled:
        return "Error: Knowledge graph is disabled. Set GRAPHITI_ENABLED=true to enable."
    
    try:
        from roscoe.core.graphiti_client import (
            get_cases_by_provider,
            get_cases_by_insurer,
            get_provider_stats,
            get_insurer_stats,
            get_entity_relationships,
            get_case_graph,
            run_cypher_query,
        )
        
        async def _run_query():
            if query_type == "cases_by_provider":
                if not entity_name:
                    return {"error": "entity_name required for cases_by_provider"}
                return await get_cases_by_provider(entity_name)
            
            elif query_type == "cases_by_insurer":
                if not entity_name:
                    return {"error": "entity_name required for cases_by_insurer"}
                return await get_cases_by_insurer(entity_name)
            
            elif query_type == "provider_stats":
                return await get_provider_stats()
            
            elif query_type == "insurer_stats":
                return await get_insurer_stats()
            
            elif query_type == "entity_relationships":
                if not entity_name:
                    return {"error": "entity_name required for entity_relationships"}
                return await get_entity_relationships(entity_name)
            
            elif query_type == "case_graph":
                if not case_name:
                    return {"error": "case_name required for case_graph"}
                return await get_case_graph(case_name)
            
            elif query_type == "custom_cypher":
                if not custom_query:
                    return {"error": "custom_query required for custom_cypher"}
                return await run_cypher_query(custom_query)
            
            else:
                return {"error": f"Unknown query_type: {query_type}"}
        
        # Run async
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _run_query())
                    results = future.result(timeout=60)
            else:
                results = asyncio.run(_run_query())
        except RuntimeError:
            results = asyncio.run(_run_query())
        
        # Helper to filter out large/noisy fields from results
        def _clean_value(v):
            """Strip embeddings and truncate large values."""
            if isinstance(v, list) and len(v) > 10:
                # Likely an embedding vector - skip it
                if all(isinstance(x, (int, float)) for x in v[:5]):
                    return "[embedding vector omitted]"
            if isinstance(v, str) and len(v) > 500:
                return v[:500] + "..."
            return v

        def _clean_record(record):
            """Remove embedding fields and clean values."""
            if isinstance(record, dict):
                cleaned = {}
                for k, v in record.items():
                    # Skip embedding fields entirely
                    if k in ('embedding', 'vector', 'embeddings'):
                        continue
                    cleaned[k] = _clean_value(v)
                return cleaned
            return record

        # Format results
        if isinstance(results, dict) and "error" in results:
            return f"Error: {results['error']}"

        if isinstance(results, list):
            if not results:
                return f"No results found for {query_type} query."

            output = [f"## Graph Query: {query_type}\n"]
            if entity_name:
                output.append(f"**Entity**: {entity_name}\n")
            if case_name:
                output.append(f"**Case**: {case_name}\n")

            output.append(f"**Results**: {len(results)} records\n")

            # Format as table if small, otherwise as list
            if results and len(results) <= 50:
                for i, record in enumerate(results, 1):
                    cleaned = _clean_record(record)
                    items = [f"{k}: {v}" for k, v in cleaned.items()]
                    output.append(f"{i}. {', '.join(items)}")
            else:
                output.append(f"(Showing first 50 of {len(results)} results)")
                for i, record in enumerate(results[:50], 1):
                    cleaned = _clean_record(record)
                    items = [f"{k}: {v}" for k, v in cleaned.items()]
                    output.append(f"{i}. {', '.join(items)}")
            
            return "\n".join(output)
        
        elif isinstance(results, dict):
            # For case_graph results
            output = [f"## Graph Query: {query_type}\n"]
            if results.get("case_name"):
                output.append(f"**Case**: {results['case_name']}")
            output.append(f"**Nodes**: {results.get('node_count', 0)}")
            output.append(f"**Edges**: {results.get('edge_count', 0)}\n")
            
            if results.get("nodes"):
                output.append("### Entities")
                for node in results["nodes"][:20]:
                    output.append(f"- {node.get('type', 'Unknown')}: {node.get('name', 'Unknown')}")
            
            return "\n".join(output)
        
        return str(results)
        
    except ImportError as e:
        return f"Error: Graphiti client not available. {str(e)}"
    except Exception as e:
        return f"Error executing graph query: {str(e)}"


def get_case_structure(
    case_name: str,
    info_type: Optional[Literal["Client", "Insurance", "Provider", "Lien", "Phase"]] = None,
) -> str:
    """
    Get structured case information (parties, insurance, providers, status).

    This queries STRUCTURED data (not episodes/notes). Use when you need:
    - Current parties: Client, defendants, attorneys
    - Insurance: Claims, insurers, adjusters, coverage
    - Medical providers treating the client
    - Liens and lienholders
    - Phase and workflow status

    For details/timeline/communications, use query_case_graph() instead.

    Args:
        case_name: Case folder name
        info_type: Optional filter. Options: "Client", "Insurance", "Provider", "Lien", "Phase"
                   If None, returns all types.

    Returns:
        Formatted structured case information

    Examples:
        get_case_structure("Abby-Sitgraves-MVA-7-13-2024")  # All info
        get_case_structure("Abby-Sitgraves-MVA-7-13-2024", info_type="Insurance")  # Just insurance
    """
    import asyncio

    graphiti_enabled = os.environ.get("GRAPHITI_ENABLED", "true").lower() == "true"

    if not graphiti_enabled:
        return "Error: Knowledge graph is disabled."

    try:
        from roscoe.core.graphiti_client import get_case_entities

        async def _get():
            entity_types = [info_type] if info_type else None
            return await get_case_entities(case_name, entity_types=entity_types)

        result = _run_async(_get())

        if "error" in result:
            return f"❌ {result['error']}"

        # Format output
        output = [f"## Case Structure: {case_name}\n"]

        if result.get("client"):
            c = result["client"]
            output.append("### Client")
            output.append(f"- **Name**: {c.get('name')}")
            if c.get('phone'):
                output.append(f"- **Phone**: {c.get('phone')}")
            if c.get('email'):
                output.append(f"- **Email**: {c.get('email')}")
            output.append("")

        if result.get("insurance"):
            output.append(f"### Insurance ({len(result['insurance'])} claims)")
            for ins in result["insurance"]:
                labels = ins.get('claim_labels', [])
                claim_type = [l for l in labels if l != 'Entity'][0] if labels else 'Claim'
                output.append(f"- **{ins.get('insurer_name', 'Unknown')}** ({claim_type})")
                if ins.get('claim_number'):
                    output.append(f"  Claim #: {ins['claim_number']}")
                if ins.get('adjuster_name'):
                    output.append(f"  Adjuster: {ins['adjuster_name']}")
            output.append("")

        if result.get("providers"):
            output.append(f"### Medical Providers ({len(result['providers'])})")
            for p in result["providers"]:
                output.append(f"- {p.get('name')} ({p.get('specialty', 'Unknown')})")
            output.append("")

        if result.get("liens"):
            output.append(f"### Liens ({len(result['liens'])})")
            for l in result["liens"]:
                output.append(f"- {l.get('holder_name')}: ${l.get('amount', 0):,.2f}")
            output.append("")

        if result.get("phase"):
            output.append(f"### Current Phase")
            output.append(f"- **{result['phase'].get('phase_display')}** ({result['phase'].get('phase_name')})")
            output.append("")

        return "\n".join(output)

    except Exception as e:
        return f"Error: {str(e)}"


def get_workflow_resources(
    phase: Optional[str] = None,
    workflow: Optional[str] = None,
    step_id: Optional[str] = None,
    resource_type: Literal[
        "all",
        "workflows",
        "landmarks",
        "steps",
        "skills",
        "checklists",
        "templates"
    ] = "all",
) -> str:
    """
    Query workflow definitions and resources from the knowledge graph.
    
    This tool retrieves workflow structure that has been loaded into the graph:
    - Phases with their workflows and landmarks
    - Workflow steps and their sequence
    - Skills, checklists, and templates associated with workflows
    
    Use this to understand what workflows are available, what steps to follow,
    and what resources (templates, checklists) to use for each task.
    
    Args:
        phase: Phase name (e.g., "file_setup", "treatment", "demand_in_progress")
            If provided, returns workflows/landmarks for that phase.
        workflow: Workflow name (e.g., "insurance_bi_claim", "request_records_bills")
            If provided, returns steps and resources for that workflow.
        step_id: Step ID within a workflow.
            If provided with workflow, returns resources for that specific step.
        resource_type: Type of resource to retrieve:
            - "all": All available information
            - "workflows": Just workflows for the phase
            - "landmarks": Just landmarks/checkpoints for the phase
            - "steps": Just steps for the workflow
            - "skills": Skills that apply to the phase
            - "checklists": Available checklists
            - "templates": Templates associated with workflow
    
    Returns:
        Formatted workflow resources from the knowledge graph.
    
    Examples:
        # Get all workflows for file_setup phase
        get_workflow_resources(phase="file_setup")
        
        # Get steps for the insurance_bi_claim workflow
        get_workflow_resources(workflow="insurance_bi_claim")
        
        # Get landmarks to verify for treatment phase
        get_workflow_resources(phase="treatment", resource_type="landmarks")
        
        # Get skills applicable to demand phase
        get_workflow_resources(phase="demand_in_progress", resource_type="skills")
        
        # Get resources for a specific workflow step
        get_workflow_resources(workflow="intake", step_id="collect_client_info")
    """
    import asyncio
    
    graphiti_enabled = os.environ.get("GRAPHITI_ENABLED", "true").lower() == "true"
    
    if not graphiti_enabled:
        return "Error: Knowledge graph is disabled. Set GRAPHITI_ENABLED=true to enable."
    
    try:
        from roscoe.core.graphiti_client import (
            get_all_phases,
            get_phase_info,
            get_phase_workflows,
            get_phase_landmarks,
            get_workflow_info,
            get_workflow_steps,
            get_step_resources,
            get_applicable_skills,
            get_all_checklists,
        )
        
        async def _get_resources():
            output = []
            
            # Case 1: Specific step resources
            if workflow and step_id:
                resources = await get_step_resources(workflow, step_id)
                output.append(f"## Resources for Step: {step_id}")
                output.append(f"**Workflow**: {workflow}\n")
                
                if resources.get("skills"):
                    output.append("### Skills")
                    for skill in resources["skills"]:
                        output.append(f"- **{skill.get('name')}**: `{skill.get('path')}`")
                
                if resources.get("checklists"):
                    output.append("\n### Checklists")
                    for cl in resources["checklists"]:
                        output.append(f"- **{cl.get('name')}**: `{cl.get('path')}`")
                
                if resources.get("templates"):
                    output.append("\n### Templates")
                    for tpl in resources["templates"]:
                        output.append(f"- **{tpl.get('name')}**: `{tpl.get('path')}`")
                
                if resources.get("tools"):
                    output.append("\n### Tools")
                    for tool in resources["tools"]:
                        output.append(f"- **{tool.get('name')}**: `{tool.get('path')}`")
                
                if not any(resources.values()):
                    output.append("_No specific resources linked to this step._")
                
                return "\n".join(output)
            
            # Case 2: Workflow information
            if workflow:
                wf_info = await get_workflow_info(workflow)
                
                if not wf_info:
                    return f"Workflow '{workflow}' not found in knowledge graph."
                
                output.append(f"## Workflow: {wf_info.get('display_name', workflow)}")
                output.append(f"**Phase**: {wf_info.get('phase')}")
                if wf_info.get('description'):
                    output.append(f"**Description**: {wf_info.get('description')}")
                if wf_info.get('instructions_path'):
                    output.append(f"**Instructions**: `{wf_info.get('instructions_path')}`")
                output.append("")
                
                if resource_type in ["all", "steps"] and wf_info.get("steps"):
                    output.append("### Steps")
                    for step in wf_info["steps"]:
                        owner = "🤖 Agent" if step.get("owner") == "agent" else "👤 User"
                        auto = "⚡ Can automate" if step.get("can_automate") else ""
                        output.append(f"{step.get('order')}. **{step.get('name')}** ({owner}) {auto}")
                        if step.get("description"):
                            output.append(f"   _{step.get('description')}_")
                
                if resource_type in ["all", "skills"] and wf_info.get("skills"):
                    output.append("\n### Associated Skills")
                    for skill in wf_info["skills"]:
                        ready = "✅" if skill.get("agent_ready") else "⚠️"
                        output.append(f"- {ready} **{skill.get('name')}**: `{skill.get('path')}`")
                
                if resource_type in ["all", "templates"] and wf_info.get("templates"):
                    output.append("\n### Templates")
                    for tpl in wf_info["templates"]:
                        output.append(f"- **{tpl.get('name')}** ({tpl.get('file_type')}): `{tpl.get('path')}`")
                
                return "\n".join(output)
            
            # Case 3: Phase information
            if phase:
                if resource_type == "workflows":
                    workflows = await get_phase_workflows(phase)
                    output.append(f"## Workflows for Phase: {phase}\n")
                    if workflows:
                        for wf in workflows:
                            output.append(f"- **{wf.get('name')}**: {wf.get('description', '_No description_')}")
                            if wf.get('instructions_path'):
                                output.append(f"  📄 `{wf.get('instructions_path')}`")
                    else:
                        output.append("_No workflows defined for this phase._")
                    return "\n".join(output)
                
                elif resource_type == "landmarks":
                    landmarks = await get_phase_landmarks(phase)
                    output.append(f"## Landmarks for Phase: {phase}\n")
                    if landmarks:
                        for lm in landmarks:
                            mandatory = "🔴 Required" if lm.get("mandatory") else "🟡 Optional"
                            output.append(f"### {lm.get('order')}. {lm.get('name')} {mandatory}")
                            if lm.get("description"):
                                output.append(f"_{lm.get('description')}_")
                            if lm.get("sub_landmarks"):
                                output.append("**Sub-landmarks:**")
                                for sub in lm["sub_landmarks"]:
                                    if sub:
                                        output.append(f"  - {sub.get('name')}")
                            output.append("")
                    else:
                        output.append("_No landmarks defined for this phase._")
                    return "\n".join(output)
                
                elif resource_type == "skills":
                    skills = await get_applicable_skills(phase)
                    output.append(f"## Skills for Phase: {phase}\n")
                    if skills:
                        for skill in skills:
                            ready = "✅" if skill.get("agent_ready") else "⚠️"
                            score = f"(score: {skill.get('quality_score', 0)})" if skill.get('quality_score') else ""
                            output.append(f"- {ready} **{skill.get('name')}** {score}")
                            if skill.get("description"):
                                output.append(f"  _{skill.get('description')}_")
                            output.append(f"  📄 `{skill.get('path')}`")
                    else:
                        output.append("_No skills mapped to this phase._")
                    return "\n".join(output)
                
                else:  # "all"
                    phase_info = await get_phase_info(phase)
                    
                    if not phase_info:
                        return f"Phase '{phase}' not found in knowledge graph."
                    
                    output.append(f"## Phase: {phase_info.get('display_name', phase)}")
                    output.append(f"**Track**: {phase_info.get('track')}")
                    output.append(f"**Order**: {phase_info.get('order')}")
                    if phase_info.get("next_phase"):
                        output.append(f"**Next Phase**: {phase_info.get('next_phase')}")
                    output.append("")
                    
                    if phase_info.get("workflows"):
                        output.append("### Available Workflows")
                        for wf in phase_info["workflows"]:
                            output.append(f"- **{wf.get('name')}**: {wf.get('description', '_No description_')}")
                        output.append("")
                    
                    if phase_info.get("landmarks"):
                        output.append("### Landmarks (Checkpoints)")
                        for lm in phase_info["landmarks"]:
                            mandatory = "🔴" if lm.get("mandatory") else "🟡"
                            output.append(f"{mandatory} {lm.get('name')}")
                    
                    return "\n".join(output)
            
            # Case 4: No specific phase/workflow - show overview
            if resource_type == "checklists":
                checklists = await get_all_checklists()
                output.append("## All Checklists\n")
                if checklists:
                    for cl in checklists:
                        output.append(f"- **{cl.get('name')}**: `{cl.get('path')}`")
                        if cl.get("when_to_use"):
                            output.append(f"  _When: {cl.get('when_to_use')[:100]}..._")
                else:
                    output.append("_No checklists found in knowledge graph._")
                return "\n".join(output)
            
            # Default: Show all phases
            phases = await get_all_phases()
            output.append("## All Phases\n")
            if phases:
                for p in phases:
                    output.append(f"{p.get('order')}. **{p.get('display_name', p.get('name'))}** ({p.get('track')})")
                    if p.get("next_phase"):
                        output.append(f"   → Next: {p.get('next_phase')}")
                output.append("\n_Use `get_workflow_resources(phase=\"...\")` to see workflows for a specific phase._")
            else:
                output.append("_No phases found. Workflow definitions may not be loaded._")
            
            return "\n".join(output)
        
        # Run async
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _get_resources())
                    result = future.result(timeout=60)
            else:
                result = asyncio.run(_get_resources())
        except RuntimeError:
            result = asyncio.run(_get_resources())
        
        return result
        
    except ImportError as e:
        return f"Error: Graphiti client not available. {str(e)}"
    except Exception as e:
        return f"Error getting workflow resources: {str(e)}"


# =============================================================================
# WORKFLOW STATE MANAGEMENT TOOLS
# =============================================================================
# These tools update the deterministic workflow state stored in the graph.

def _run_async(coro):
    """Helper to run async code from sync context."""
    import asyncio
    try:
        # Try to get existing loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, need to use thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result(timeout=120)
        elif loop.is_closed():
            # Loop is closed, create a new one and don't close it
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
            # Don't close - let it persist for subsequent calls
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop at all, create one
        return asyncio.run(coro)
    except Exception as e:
        # Fallback: always use asyncio.run
        return asyncio.run(coro)


def update_landmark(
    case_name: str,
    landmark_id: str,
    status: Literal["complete", "incomplete", "in_progress", "not_applicable"],
    sub_steps: Optional[Dict[str, bool]] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Update a landmark's status for a case in the knowledge graph.
    
    Landmarks are checkpoints that track case progress. Each phase has multiple
    landmarks that should be completed before advancing to the next phase.
    Some landmarks are "hard blockers" - the case cannot advance until they're complete.
    
    Use this tool when:
    - You've completed a workflow and need to mark its landmark complete
    - A task is in progress and you want to track that
    - A landmark doesn't apply to this case (e.g., no wage loss claim)
    
    Args:
        case_name: The case folder name (e.g., "Christopher-Lanier-MVA-6-28-2025")
        landmark_id: The landmark identifier. Common landmarks include:
            File Setup phase:
            - "retainer_signed" (HARD BLOCKER)
            - "full_intake_complete"
            - "insurance_claims_setup"
            - "providers_setup"
            
            Treatment phase:
            - "client_checkin_current"
            - "providers_monitored"
            - "treatment_complete"
            
            Demand phase:
            - "all_records_received"
            - "all_bills_received"
            - "demand_sent" (HARD BLOCKER)
            
            Negotiation phase:
            - "initial_offer_received"
            - "settlement_reached"
            
        status: The new status:
            - "complete": Task/checkpoint is fully done
            - "in_progress": Currently working on it
            - "incomplete": Not started or blocked
            - "not_applicable": Doesn't apply to this case
        sub_steps: Optional dict of sub-step completions for complex landmarks.
            Example for insurance_claims_setup:
            {"bi_insurance_identified": True, "bi_lor_sent": True, "bi_claim_acknowledged": False}
        notes: Optional notes explaining the status or what was done.
    
    Returns:
        Confirmation message with updated status.
    
    Examples:
        # Mark retainer signed (hard blocker for file_setup)
        update_landmark(
            case_name="Christopher-Lanier-MVA-6-28-2025",
            landmark_id="retainer_signed",
            status="complete",
            notes="Signed via DocuSign on 2025-12-15"
        )
        
        # Mark insurance setup in progress with sub-steps
        update_landmark(
            case_name="Christopher-Lanier-MVA-6-28-2025",
            landmark_id="insurance_claims_setup",
            status="in_progress",
            sub_steps={
                "bi_insurance_identified": True,
                "bi_lor_sent": True,
                "bi_claim_acknowledged": False,
                "pip_carrier_determined": True,
                "pip_application_sent": True
            },
            notes="Waiting on BI claim acknowledgment from State Farm"
        )
        
        # Mark wage loss as not applicable
        update_landmark(
            case_name="Wilson-MVA-2024",
            landmark_id="wage_loss_documented",
            status="not_applicable",
            notes="Client did not miss work"
        )
    """
    graphiti_enabled = os.environ.get("GRAPHITI_ENABLED", "true").lower() == "true"
    
    if not graphiti_enabled:
        return "Error: Knowledge graph is disabled. Set GRAPHITI_ENABLED=true to enable."
    
    try:
        from roscoe.core.graphiti_client import update_case_landmark_status, get_landmark_status
        
        async def _update():
            # Update the landmark
            success = await update_case_landmark_status(
                case_name=case_name,
                landmark_id=landmark_id,
                status=status,
                sub_steps=sub_steps,
                notes=notes
            )
            
            if not success:
                return None
            
            # Get the updated status
            return await get_landmark_status(case_name, landmark_id)
        
        result = _run_async(_update())
        
        if not result:
            return f"❌ Failed to update landmark '{landmark_id}' for case '{case_name}'. The landmark may not exist."
        
        # Format response
        status_emoji = {
            "complete": "✅",
            "in_progress": "🔄",
            "incomplete": "⏳",
            "not_applicable": "➖"
        }
        
        emoji = status_emoji.get(status, "📌")
        is_hard = " (HARD BLOCKER)" if result.get("is_hard_blocker") else ""
        
        output = [
            f"{emoji} Landmark updated: **{result.get('display_name', landmark_id)}**{is_hard}",
            "",
            f"**Case**: {case_name}",
            f"**Status**: {status}",
            f"**Phase**: {result.get('phase')}",
        ]
        
        if notes:
            output.append(f"**Notes**: {notes}")
        
        if sub_steps:
            completed = sum(1 for v in sub_steps.values() if v)
            total = len(sub_steps)
            output.append(f"**Sub-steps**: {completed}/{total} complete")
        
        return "\n".join(output)
        
    except ImportError as e:
        return f"Error: Graphiti client not available. {str(e)}"
    except Exception as e:
        return f"Error updating landmark: {str(e)}"


def advance_phase(
    case_name: str,
    target_phase: Optional[str] = None,
    force: bool = False,
) -> str:
    """
    Advance a case to the next phase or a specific target phase.
    
    Before advancing, this checks that all "hard blocker" landmarks for the
    current phase are complete. If any are incomplete, the advance will fail
    unless force=True (admin override).
    
    Use this tool when:
    - A case has completed all requirements for its current phase
    - You need to manually set a case to a specific phase
    - You need to override blockers (with force=True)
    
    Args:
        case_name: The case folder name (e.g., "Christopher-Lanier-MVA-6-28-2025")
        target_phase: Optional specific phase to advance to. If not provided,
            advances to the natural next phase. Valid phases:
            - "file_setup" (phase 1)
            - "treatment" (phase 2)
            - "demand_in_progress" (phase 3)
            - "negotiation" (phase 4)
            - "settlement" (phase 5)
            - "lien_phase" (phase 6)
            - "complaint" (phase 7)
            - "discovery" (phase 8)
            - "mediation" (phase 9)
            - "trial_prep" (phase 10)
            - "trial" (phase 11)
            - "closed" (phase 12)
        force: If True, skip hard blocker checks and force the phase change.
            Use sparingly - only for admin overrides or corrections.
    
    Returns:
        Confirmation message or error if blockers prevent advancement.
    
    Examples:
        # Advance to the next natural phase
        advance_phase("Christopher-Lanier-MVA-6-28-2025")
        
        # Advance to a specific phase
        advance_phase("Christopher-Lanier-MVA-6-28-2025", target_phase="treatment")
        
        # Force advance even with incomplete hard blockers (admin override)
        advance_phase("Christopher-Lanier-MVA-6-28-2025", target_phase="demand_in_progress", force=True)
    """
    graphiti_enabled = os.environ.get("GRAPHITI_ENABLED", "true").lower() == "true"
    
    if not graphiti_enabled:
        return "Error: Knowledge graph is disabled. Set GRAPHITI_ENABLED=true to enable."
    
    try:
        from roscoe.core.graphiti_client import (
            get_case_phase,
            advance_case_to_phase,
            check_phase_can_advance
        )
        
        async def _advance():
            # Get current phase (may be None for cases that predate workflow system)
            current = await get_case_phase(case_name)
            current_phase = current.get("name") if current else None

            # Determine target phase
            if target_phase:
                # Explicit target provided - use it
                actual_target = target_phase
            elif current:
                # No explicit target - use next phase from current
                actual_target = current.get("next_phase")
                if not actual_target:
                    return {"error": f"No next phase defined for '{current_phase}'. Use target_phase to specify."}
            else:
                # No current phase AND no target - can't determine where to go
                # Check if case exists at all first
                from roscoe.core.graphiti_client import run_cypher_query
                case_check = await run_cypher_query(
                    """
                    OPTIONAL MATCH (c1:Case {name: $case_name})
                    OPTIONAL MATCH (c2:Entity {entity_type: 'Case', name: $case_name})
                    WITH COALESCE(c1, c2) as c
                    WHERE c IS NOT NULL
                    RETURN c.name as name
                    """,
                    {"case_name": case_name}
                )
                if not case_check:
                    return {"error": f"Case '{case_name}' not found."}
                else:
                    return {"error": f"Case '{case_name}' has no phase set. Use target_phase to initialize it (e.g., target_phase='onboarding' or target_phase='file_setup')."}

            # Check if can advance (unless forcing or initializing)
            if not force and current_phase:
                check = await check_phase_can_advance(case_name, current_phase)
                if not check.get("can_advance"):
                    return {
                        "blocked": True,
                        "current_phase": current_phase,
                        "target_phase": actual_target,
                        "blockers": check.get("blocking_landmarks", [])
                    }

            # Perform the advance (or initial phase set)
            result = await advance_case_to_phase(case_name, actual_target, force)
            return result
        
        result = _run_async(_advance())
        
        # Handle errors
        if result.get("error"):
            return f"❌ {result['error']}"
        
        # Handle blocked
        if result.get("blocked"):
            output = [
                "⚠️ Cannot advance phase - incomplete hard blockers:",
                "",
                f"**Current Phase**: {result['current_phase']}",
                f"**Target Phase**: {result['target_phase']}",
                "",
                "**Blocking Landmarks**:"
            ]
            for blocker in result.get("blockers", []):
                name = blocker.get("display_name", blocker.get("landmark_id"))
                status = blocker.get("current_status", "incomplete")
                output.append(f"  - ❌ {name}: {status}")
            
            output.append("")
            output.append("Complete these landmarks first, or use force=True to override.")
            return "\n".join(output)
        
        # Success
        if result.get("success"):
            force_note = " (forced)" if force else ""
            prev_phase = result.get('previous_phase')
            prev_phase_line = f"**Previous Phase**: {prev_phase}" if prev_phase else "**Previous Phase**: (none - workflow initialized)"
            action_word = "advanced" if prev_phase else "initialized"
            return f"""✅ Phase {action_word}{force_note}

**Case**: {case_name}
{prev_phase_line}
**New Phase**: {result.get('new_phase')}
**Entered At**: {result.get('entered_at', 'now')[:10]}

The case is now in the **{result.get('new_phase')}** phase."""
        
        return f"❌ Unexpected result: {result}"
        
    except ImportError as e:
        return f"Error: Graphiti client not available. {str(e)}"
    except Exception as e:
        return f"Error advancing phase: {str(e)}"


def get_case_workflow_status(case_name: str) -> str:
    """
    Get the complete workflow status for a case from the knowledge graph.
    
    This returns the deterministic workflow state including:
    - Current phase and when it was entered
    - All landmark statuses for the current phase
    - Whether the case can advance to the next phase
    - Which hard blockers are incomplete (if any)
    - Suggested workflows to complete incomplete landmarks
    
    Use this tool when:
    - You need to understand where a case is in its lifecycle
    - You need to know what tasks remain for the current phase
    - You want to check if a case is ready to advance
    
    Args:
        case_name: The case folder name (e.g., "Christopher-Lanier-MVA-6-28-2025")
    
    Returns:
        Formatted workflow status with phase, landmarks, and next actions.
    
    Examples:
        get_case_workflow_status("Christopher-Lanier-MVA-6-28-2025")
        get_case_workflow_status("Wilson-MVA-2024")
    """
    graphiti_enabled = os.environ.get("GRAPHITI_ENABLED", "true").lower() == "true"
    
    if not graphiti_enabled:
        return "Error: Knowledge graph is disabled. Set GRAPHITI_ENABLED=true to enable."
    
    try:
        from roscoe.workflow_engine.orchestrator.graph_state_computer import (
            GraphWorkflowStateComputer
        )
        
        async def _get_status():
            computer = GraphWorkflowStateComputer()
            state = await computer.compute_state(case_name)
            return state.format_for_prompt()
        
        result = _run_async(_get_status())
        return result
        
    except ImportError as e:
        return f"Error: Workflow state computer not available. {str(e)}"
    except Exception as e:
        return f"Error getting workflow status: {str(e)}"


def recalculate_case_phase(case_name: str) -> str:
    """
    Recalculate which phase a case should be in based on landmark completion.
    
    This analyzes the current phase's landmark statuses and determines if the case
    is ready to advance to the next phase. Use this after marking landmarks complete
    to check if ready for phase advancement.
    
    Returns analysis including:
    - Current phase and completion percentage
    - Hard blockers (if any)
    - Whether case can advance
    - Whether case SHOULD advance (>80% complete)
    - Recommendation
    
    Use this tool when:
    - You've just marked a landmark as complete
    - User asks "are we ready to move to the next phase?"
    - You want to check overall phase progress
    
    Args:
        case_name: The case folder name
    
    Returns:
        Phase readiness analysis with recommendation
    
    Examples:
        recalculate_case_phase("Caryn-McCay-MVA-7-30-2023")
        recalculate_case_phase("Wilson-MVA-2024")
    """
    graphiti_enabled = os.environ.get("GRAPHITI_ENABLED", "true").lower() == "true"
    
    if not graphiti_enabled:
        return "Error: Knowledge graph is disabled. Set GRAPHITI_ENABLED=true to enable."
    
    try:
        from roscoe.core.graphiti_client import (
            get_case_phase,
            get_case_landmark_statuses,
        )

        async def _recalculate():
            # Get current phase using existing function
            phase = await get_case_phase(case_name)

            if not phase:
                return f"❌ Error: Case '{case_name}' not found or no phase set"

            current_phase = phase.get('name')
            current_order = phase.get('phase_number', 0)
            next_phase = phase.get('next_phase')
            subphase_name = phase.get('subphase_name')
            subphase_display = phase.get('subphase_display')

            # Get landmark statuses for current phase using existing function
            all_landmarks = await get_case_landmark_statuses(case_name, phase_name=current_phase)

            if not all_landmarks:
                return f"❌ Error: No landmarks found for phase '{current_phase}'"

            landmarks = all_landmarks  # Already filtered to current phase
            
            # Analyze completion
            total = len(landmarks)
            complete = len([lm for lm in landmarks if lm.get('status') == 'complete'])
            in_progress = len([lm for lm in landmarks if lm.get('status') == 'in_progress'])
            completion_pct = (complete / total * 100) if total > 0 else 0
            
            # Find hard blockers
            hard_blockers = [
                lm for lm in landmarks
                if lm.get('is_hard_blocker') and lm.get('status') not in ['complete', 'not_applicable']
            ]
            
            # Determine recommendation
            can_advance = len(hard_blockers) == 0
            should_advance = can_advance and completion_pct >= 80
            
            # Format response
            lines = [f"**Phase Readiness Analysis for {case_name}**\n"]
            lines.append(f"Current Phase: **{phase.get('display_name')}** (Phase {current_order})")
            if subphase_name:
                lines.append(f"Current Sub-Phase: **{subphase_display}**")
            lines.append(f"\n**Progress:** {complete}/{total} landmarks complete ({completion_pct:.0f}%)")
            lines.append(f"- Complete: {complete}")
            lines.append(f"- In Progress: {in_progress}")
            lines.append(f"- Not Started: {total - complete - in_progress}\n")

            if can_advance:
                lines.append(f"✅ **READY TO ADVANCE**")
                lines.append(f"Next Phase: **{next_phase}**\n")
                if should_advance:
                    lines.append(f"**Recommendation:** Advance now ({completion_pct:.0f}% complete)")
                    lines.append(f"Use `advance_phase('{case_name}')` to proceed")
                else:
                    lines.append(f"**Recommendation:** Can advance, but consider completing more landmarks first")
                    lines.append(f"Currently {completion_pct:.0f}% complete (recommend >80%)")
            else:
                lines.append(f"❌ **CANNOT ADVANCE** - Hard blockers remaining:\n")
                for blocker in hard_blockers:
                    blocker_name = blocker.get('display_name') or blocker.get('landmark_id')
                    lines.append(f"  - **{blocker_name}** (status: {blocker.get('status')})")
                lines.append(f"\nComplete these hard blockers before advancing to {next_phase}")
            
            return "\n".join(lines)
        
        result = _run_async(_recalculate())
        return result
        
    except Exception as e:
        return f"Error recalculating phase: {str(e)}"


# =============================================================================
# MEDICAL RECORDS ANALYSIS DISPATCH TOOLS
# Fire-and-forget pattern for background analysis (see Anthropic "Effective Harnesses")
# =============================================================================

# Analysis jobs directory - shared between paralegal and medical records agent
ANALYSIS_JOBS_DIR = LOCAL_WORKSPACE / "analysis_jobs"


def dispatch_medical_records_analysis(
    case_name: str,
    case_folder: str,
) -> str:
    """
    Dispatch comprehensive medical records analysis to a background agent.

    This starts a fire-and-forget analysis workflow that runs asynchronously.
    The analysis agent will:
    1. Extract facts from litigation documents (complaint, police reports)
    2. Inventory and extract all medical records
    3. Build treatment chronology
    4. Analyze causation, inconsistencies, red flags, missing records
    5. Create attorney-ready FINAL_SUMMARY.md

    You can continue with other tasks while the analysis runs in the background.
    Use get_medical_analysis_status(job_id) to check progress.

    Args:
        case_name: Human-readable case name (e.g., "Caryn McCay MVA")
        case_folder: Workspace path to case folder (e.g., "/projects/Caryn-McCay-MVA-7-30-2023")

    Returns:
        Job details including job_id for status checking

    Examples:
        dispatch_medical_records_analysis("Caryn McCay MVA", "/projects/Caryn-McCay-MVA-7-30-2023")
        dispatch_medical_records_analysis("Wilson MVA 2024", "/projects/Wilson-MVA-2024")
    """
    import uuid
    from datetime import datetime

    try:
        # Generate unique job ID
        job_id = f"med-analysis-{uuid.uuid4().hex[:8]}"

        # Create job directory and status file
        job_dir = ANALYSIS_JOBS_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Initial job status
        job_status = {
            "job_id": job_id,
            "case_name": case_name,
            "case_folder": case_folder,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "current_phase": "setup",
            "message": "Analysis queued, waiting for agent to start",
            "phase_history": [],
        }

        # Write status file
        status_path = job_dir / "status.json"
        status_path.write_text(json.dumps(job_status, indent=2))

        # TODO: In production, this would POST to LangGraph API to start the agent
        # POST /threads with graph_id="medical_records_agent"
        # For now, we create the job entry and the medical records agent
        # would be started separately (via langgraph CLI or API)

        # Check if case folder exists
        case_path = GCS_WORKSPACE / case_folder.lstrip("/")
        if not case_path.exists():
            return f"""❌ Case folder not found: {case_folder}

Please verify the case folder path exists in the workspace."""

        # Check for medical records folder
        medical_records_path = case_path / "Medical Records"
        has_medical_records = medical_records_path.exists()

        return f"""✅ **Medical Records Analysis Dispatched**

**Job ID:** `{job_id}`
**Case:** {case_name}
**Case Folder:** {case_folder}
**Status:** Queued

**Case Folder Check:**
- Medical Records folder: {"✅ Found" if has_medical_records else "⚠️ Not found"}

**Next Steps:**
1. The analysis agent will start automatically
2. Use `get_medical_analysis_status("{job_id}")` to check progress
3. Results will be saved to `{case_folder}/reports/FINAL_SUMMARY.md`

**Analysis Phases:**
1. Fact Investigation - Extract details from litigation docs
2. Medical Organization & Extraction - Inventory + extract all records
3. Parallel Analysis - Inconsistencies, red flags, causation, missing records
4. Final Synthesis - Create attorney-ready summary

I'll continue with other tasks while this runs in the background."""

    except Exception as e:
        return f"❌ Error dispatching medical records analysis: {str(e)}"


def get_medical_analysis_status(job_id: str) -> str:
    """
    Check the status of a dispatched medical records analysis job.

    Args:
        job_id: The job ID returned by dispatch_medical_records_analysis

    Returns:
        Current status, phase, progress, and any results

    Examples:
        get_medical_analysis_status("med-analysis-abc12345")
    """
    try:
        job_dir = ANALYSIS_JOBS_DIR / job_id
        status_path = job_dir / "status.json"

        if not status_path.exists():
            return f"❌ Job not found: {job_id}\n\nUse list_analysis_jobs() to see available jobs."

        job_status = json.loads(status_path.read_text())

        status = job_status.get("status", "unknown")
        current_phase = job_status.get("current_phase", "unknown")
        message = job_status.get("message", "")
        case_name = job_status.get("case_name", "Unknown")
        case_folder = job_status.get("case_folder", "")
        created_at = job_status.get("created_at", "")
        updated_at = job_status.get("updated_at", "")
        result_path = job_status.get("result_path", "")
        error = job_status.get("error", "")

        # Build status display
        status_emoji = {
            "queued": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
        }.get(status, "❓")

        lines = [
            f"**Medical Records Analysis Status**\n",
            f"**Job ID:** `{job_id}`",
            f"**Case:** {case_name}",
            f"**Status:** {status_emoji} {status.upper()}",
            f"**Current Phase:** {current_phase}",
        ]

        if message:
            lines.append(f"**Message:** {message}")

        if created_at:
            lines.append(f"**Started:** {created_at}")
        if updated_at:
            lines.append(f"**Last Update:** {updated_at}")

        if status == "completed" and result_path:
            lines.append(f"\n**Results Available:**")
            lines.append(f"📄 `{result_path}`")
            lines.append(f"\nWould you like me to read the summary?")

        if status == "failed" and error:
            lines.append(f"\n**Error:** {error}")

        # Show phase history if available
        phase_history = job_status.get("phase_history", [])
        if phase_history:
            lines.append(f"\n**Phase History:**")
            for ph in phase_history[-5:]:  # Show last 5 phases
                lines.append(f"  - {ph.get('phase')}: {ph.get('started_at', '')}")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Error checking job status: {str(e)}"


def list_analysis_jobs() -> str:
    """
    List all medical records analysis jobs.

    Returns a summary of all dispatched analysis jobs including their status.

    Returns:
        List of jobs with status, case name, and creation time
    """
    try:
        if not ANALYSIS_JOBS_DIR.exists():
            return "No analysis jobs found. Use dispatch_medical_records_analysis() to start one."

        jobs = []
        for job_dir in ANALYSIS_JOBS_DIR.iterdir():
            if job_dir.is_dir():
                status_path = job_dir / "status.json"
                if status_path.exists():
                    try:
                        job_status = json.loads(status_path.read_text())
                        jobs.append({
                            "job_id": job_status.get("job_id", job_dir.name),
                            "case_name": job_status.get("case_name", "Unknown"),
                            "status": job_status.get("status", "unknown"),
                            "current_phase": job_status.get("current_phase", ""),
                            "created_at": job_status.get("created_at", ""),
                        })
                    except Exception:
                        pass

        if not jobs:
            return "No analysis jobs found. Use dispatch_medical_records_analysis() to start one."

        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        lines = ["**Medical Records Analysis Jobs**\n"]

        status_emoji = {
            "queued": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
        }

        for job in jobs:
            emoji = status_emoji.get(job["status"], "❓")
            lines.append(
                f"- `{job['job_id']}` {emoji} **{job['case_name']}** "
                f"({job['status']}, phase: {job['current_phase']})"
            )

        lines.append(f"\nUse `get_medical_analysis_status(job_id)` for details.")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Error listing analysis jobs: {str(e)}"
