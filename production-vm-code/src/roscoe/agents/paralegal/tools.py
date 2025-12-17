"""
Roscoe Paralegal Agent Tools

This module provides tools for the paralegal agent:
- Internet search (Tavily)
- Multimodal analysis (image, audio, video)
- Slack notifications
- Script execution with GCS filesystem access (Docker)
- UI script execution (render_ui_script) - universal UI renderer
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

# Import script executor (supports Docker or native execution)
from roscoe.agents.paralegal.script_executor import (
    execute_python_script as _execute_python_script,
    format_execution_result,
    ScriptExecutionError,
    check_docker_available,
    get_execution_stats,
    get_execution_mode_info,
)

# Import Word template pipeline for document generation
from roscoe.agents.paralegal.word_template_pipeline import (
    fill_and_export_template as _fill_and_export_template,
    render_docx_template as _render_docx_template,
    convert_docx_to_pdf as _convert_docx_to_pdf,
    convert_doc_to_docx as _convert_doc_to_docx,
    list_template_placeholders as _list_template_placeholders,
    check_dependencies as _check_word_deps,
    TemplateError,
    LibreOfficeNotFoundError,
    TemplateNotFoundError,
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

# Get workspace root for file operations (paralegal agent workspace)
# Use WORKSPACE_DIR env var (set in production), fallback to relative path for local dev
workspace_root = Path(os.environ.get("WORKSPACE_DIR", str(Path(__file__).parent.parent.parent.parent.parent / "workspace_paralegal")))


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
        if file_path.startswith('/'):
            file_path = file_path[1:]  # Remove leading slash
        abs_path = workspace_root / file_path

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
        if file_path.startswith('/'):
            file_path = file_path[1:]  # Remove leading slash
        abs_path = workspace_root / file_path

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
        if file_path.startswith('/'):
            file_path = file_path[1:]  # Remove leading slash
        abs_path = workspace_root / file_path

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
        abs_path = workspace_root / file_path

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
# Script Execution Tools (Docker-based with GCS filesystem access)
# =============================================================================

def execute_python_script(
    script_path: str,
    case_name: Optional[str] = None,
    script_args: Optional[list[str]] = None,
    working_dir: Optional[str] = None,
    timeout: int = 300,
) -> str:
    """
    Execute a Python script from /Tools/ with direct GCS filesystem access.

    This runs scripts in isolated Docker containers that have read-write access
    to the entire workspace at /mnt/workspace. Changes made by scripts persist
    to GCS automatically via gcsfuse.

    Use this for:
    - Running /Tools/ scripts (create_file_inventory.py, analyze_medical_records.py)
    - Data processing that needs to modify actual files
    - Complex analysis workflows requiring filesystem access
    - Batch operations on case folders

    Note: For simple file operations (read, write, move), use native filesystem
    capabilities. This tool is specifically for executing Python scripts.

    Args:
        script_path: Path to Python script relative to workspace root.
                    Example: "/Tools/create_file_inventory.py" or "Tools/analyze.py"
        case_name: Optional case folder name to set as working directory.
                  Example: "Wilson-MVA-2024" -> sets working dir to /workspace/projects/Wilson-MVA-2024
        script_args: Optional list of command-line arguments for the script.
                    Example: ["--format", "json", "--output", "Reports/result.json"]
        working_dir: Optional explicit working directory (overrides case_name).
        timeout: Maximum execution time in seconds (default: 300, max: 1800).

    Returns:
        Formatted execution results including stdout, stderr, and status.

    Examples:
        # Run file inventory on a case
        execute_python_script(
            script_path="/Tools/create_file_inventory.py",
            case_name="Wilson-MVA-2024"
        )

        # Run analysis with arguments
        execute_python_script(
            script_path="/Tools/analyze_medical_records.py",
            case_name="Wilson-MVA-2024",
            script_args=["--output", "Reports/analysis.md", "--verbose"]
        )

        # Run document import
        execute_python_script(
            script_path="/Tools/document_processing/batch_import_all.py",
            script_args=["--case", "Wilson-MVA-2024"]
        )

        # Run legal research script
        execute_python_script(
            script_path="/Tools/legal_research/search_case_law.py",
            script_args=["negligence standard of care", "--courts", "ky,kyctapp"]
        )
    """
    try:
        result = _execute_python_script(
            script_path=script_path,
            case_name=case_name,
            script_args=script_args,
            working_dir=working_dir,
            timeout=timeout,
            enable_playwright=False,
        )

        return format_execution_result(result)

    except ScriptExecutionError as e:
        return f"❌ Script execution failed: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def execute_python_script_with_browser(
    script_path: str,
    case_name: Optional[str] = None,
    script_args: Optional[list[str]] = None,
    timeout: int = 600,
) -> str:
    """
    Execute a Python script with Playwright browser automation capabilities.

    This uses a Docker image with Chromium pre-installed for browser automation.
    Scripts can use Playwright to navigate websites, extract data, take screenshots,
    and perform web automation tasks.

    Use this for:
    - Web scraping (legal research, court records, public records)
    - Automated form filling
    - Screenshot capture of web pages
    - Web-based data extraction

    Note: This uses a larger Docker image and may be slower to start.
    Use regular execute_python_script() when browser automation isn't needed.

    Args:
        script_path: Path to Playwright-enabled Python script.
        case_name: Optional case folder for working directory.
        script_args: Optional command-line arguments.
        timeout: Maximum execution time (default: 600s due to browser overhead).

    Returns:
        Formatted execution results.

    Examples:
        # Scrape court records
        execute_python_script_with_browser(
            script_path="/Tools/web_scraping/courtlistener_search.py",
            script_args=["personal injury", "Kentucky"]
        )

        # Take screenshot of a webpage
        execute_python_script_with_browser(
            script_path="/Tools/web_scraping/screenshot_page.py",
            script_args=["https://example.com", "--output", "Reports/screenshot.png"]
        )
    """
    try:
        result = _execute_python_script(
            script_path=script_path,
            case_name=case_name,
            script_args=script_args,
            timeout=timeout,
            enable_playwright=True,
        )

        return format_execution_result(result)

    except ScriptExecutionError as e:
        return f"❌ Browser script execution failed: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def get_script_execution_stats(hours: int = 24) -> str:
    """
    Get statistics on script execution health and usage.

    Use this to monitor script execution performance and identify issues.

    Args:
        hours: Number of hours to look back (default: 24).

    Returns:
        Formatted statistics report.

    Examples:
        get_script_execution_stats()        # Last 24 hours
        get_script_execution_stats(hours=1) # Last hour
    """
    stats = get_execution_stats(hours)

    lines = [
        f"**Script Execution Stats (Last {hours} hours)**",
        "",
        f"Total Executions: {stats['total_executions']}",
        f"Success Rate: {stats['success_rate']*100:.1f}%",
        f"Average Duration: {stats['average_duration']:.2f}s",
        "",
        "**Most Used Scripts:**",
    ]

    for script, count in stats['most_used_scripts'].items():
        lines.append(f"  - `{script}`: {count} executions")

    if not stats['most_used_scripts']:
        lines.append("  (none)")

    return "\n".join(lines)


def check_script_execution_mode() -> str:
    """
    Check the current script execution mode and capabilities.
    
    Use this to diagnose script execution issues. Shows whether Docker
    or native Python execution will be used, and what capabilities are available.
    
    Returns:
        Diagnostic information about script execution setup.
    
    Examples:
        check_script_execution_mode()
    """
    info = get_execution_mode_info()
    
    # Determine status indicators
    docker_status = "✅" if info['docker_daemon_available'] else "❌"
    base_image_status = "✅" if info['base_image_available'] else "❌"
    playwright_status = "✅" if info['playwright_image_available'] else "❌"
    
    mode_emoji = "🐳" if info['effective_mode'] == "docker" else "🐍"
    
    lines = [
        "**Script Execution Configuration**",
        "",
        f"Configured Mode: `{info['configured_mode']}`",
        f"Effective Mode: {mode_emoji} **{info['effective_mode']}**",
        "",
        "**Docker Status:**",
        f"  {docker_status} Docker SDK installed: {info['docker_sdk_installed']}",
        f"  {docker_status} Docker daemon available: {info['docker_daemon_available']}",
        f"  {base_image_status} Base image (`{info['base_image']}`): {'Available' if info['base_image_available'] else 'Not found'}",
        f"  {playwright_status} Playwright image (`{info['playwright_image']}`): {'Available' if info['playwright_image_available'] else 'Not found'}",
        "",
        "**Paths:**",
        f"  Workspace: `{info['workspace_root']}`",
        f"  Python: `{info['native_python']}`",
    ]
    
    # Add recommendations if Docker isn't working
    if info['effective_mode'] == 'native' and info['configured_mode'] == 'auto':
        lines.append("")
        lines.append("**Note:** Running in native mode because Docker/images unavailable.")
        lines.append("Scripts will run directly with the host Python interpreter.")
        
        if not info['docker_daemon_available']:
            lines.append("")
            lines.append("To enable Docker execution:")
            lines.append("  1. Ensure Docker is installed and running")
            lines.append("  2. Run: `cd docker/roscoe-python-runner && ./build.sh`")
    
    return "\n".join(lines)


# UI Script Execution Tool (Universal UI Component Renderer)
# =============================================================================

def render_ui_script(
    script_path: str,
    script_args: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Execute a UI script and return structured data for the workbench UI.

    This is the *only* supported UI integration surface. The agent calls
    `render_ui_script(...)` and the frontend applies the returned UI commands
    (calendar/monaco/viewer/workbench) automatically.

    UI scripts live in `/Tools/UI/**` in the workspace bucket and must output
    **valid JSON** to stdout.

    Expected output (recommended):

      {
        "success": true,
        "title": "Optional label",
        "commands": [
          { "type": "workbench.setCenterView", "view": "calendar" },
          { "type": "calendar.setEvents", "events": [ ... ] }
        ]
      }

    Legacy UI scripts (old CopilotKit UI) should be moved under `/Tools/UI_legacy`
    and are blocked by this tool.

    Args:
        script_path: Path to UI script under Tools/UI/ (e.g., "UI/calendar/show_day.py")
        script_args: Arguments to pass to the script (e.g., ["--date", "2025-12-17"])

    Returns:
        Dictionary with UI commands for the frontend to apply.

    Examples:
        # Show today's calendar (Google + Roscoe events):
        render_ui_script("UI/calendar/show_day.py", ["--date", "2025-12-16", "--days", "1"])
        # Open a workspace file in Monaco:
        render_ui_script("UI/monaco/open.py", ["--path", "projects/Case-Name/notes.md"])
        # Open a workspace file in the viewer:
        render_ui_script("UI/viewer/open.py", ["--path", "projects/Case-Name/exhibit.pdf"])
    """
    import subprocess
    import sys
    
    # Normalize script path
    if not script_path.startswith("/"):
        script_path = "/" + script_path
    if not script_path.startswith("/Tools/"):
        script_path = "/Tools" + script_path

    # Block legacy UI scripts outright.
    if script_path.startswith("/Tools/UI_legacy/"):
        return {
            "success": False,
            "error": f"Legacy UI scripts are disabled: {script_path}",
        }
    
    # Get workspace path
    workspace_dir = os.environ.get("WORKSPACE_DIR", str(workspace_root))
    workspace_path = Path(workspace_dir)
    
    # Build full script path
    full_script_path = workspace_path / script_path.lstrip("/")
    
    if not full_script_path.exists():
        return {
            "error": f"UI script not found: {script_path}",
            "success": False
        }

    # Hard safety: only allow scripts under Tools/UI/ for the new workbench UI.
    # (Everything else is treated as legacy or non-UI.)
    try:
        rel = full_script_path.relative_to(workspace_path)
    except Exception:
        return {"success": False, "error": f"Invalid script path: {script_path}"}

    if not str(rel).startswith("Tools/UI/"):
        return {
            "success": False,
            "error": f"UI scripts must be under Tools/UI/. Refusing: {script_path}",
        }
    
    # Build command
    cmd = [sys.executable, str(full_script_path)]
    if script_args:
        cmd.extend(script_args)
    
    # Set environment for script
    env = os.environ.copy()
    env["WORKSPACE_DIR"] = str(workspace_path)
    
    # Add UI directory to Python path
    ui_dir = str(workspace_path / "Tools" / "UI")
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{ui_dir}:{existing_pythonpath}" if existing_pythonpath else ui_dir
    
    try:
        # Run the script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
            cwd=ui_dir,
        )
        
        # Parse JSON output
        if result.returncode == 0:
            try:
                output = json.loads(result.stdout)
                return output
            except json.JSONDecodeError:
                return {
                    "error": f"Script output is not valid JSON: {result.stdout[:500]}",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": False
                }
        else:
            error_output = result.stderr or result.stdout
            try:
                output = json.loads(result.stdout)
                return output
            except json.JSONDecodeError:
                return {
                    "error": f"Script execution failed: {error_output[:500]}",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": False
                }
        
    except subprocess.TimeoutExpired:
        return {
            "error": "Script execution timed out after 60 seconds",
            "success": False
        }
    except Exception as e:
        return {
            "error": f"Failed to execute script: {str(e)}",
            "success": False
    }


def render_calendar(
    date: str,
    days: int = 1,
    include_google: bool = True,
    include_roscoe: bool = True,
) -> Dict[str, Any]:
    """
    Render the calendar UI with events from local calendar database.

    This is a direct calendar rendering tool that reads from the JSON calendar
    database and returns UI commands without executing external scripts.

    Args:
        date: Date to show in ISO format (YYYY-MM-DD), e.g., "2025-12-17"
        days: Number of days to display (default: 1)
        include_google: Include Google Calendar events (default: True)
        include_roscoe: Include Roscoe/local calendar events (default: True)

    Returns:
        Dictionary with UI commands to display the calendar.

    Examples:
        render_calendar("2025-12-17")
        render_calendar("2025-12-17", days=7)
        render_calendar("2025-12-17", include_google=False)  # Local only
    """
    from datetime import datetime, timedelta

    try:
        # Parse the date
        try:
            start_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid date format: {date}. Use YYYY-MM-DD format."
            }

        end_date = start_date + timedelta(days=days - 1)

        # Read calendar.json from workspace
        calendar_json_path = workspace_root / "Database" / "calendar.json"

        if not calendar_json_path.exists():
            return {
                "success": False,
                "error": "Calendar database not found at /Database/calendar.json"
            }

        with open(calendar_json_path, 'r') as f:
            all_events = json.load(f)

        # Filter events for the date range
        filtered_events = []
        for event in all_events:
            event_date_str = event.get("date") or event.get("start_date")
            if not event_date_str:
                continue

            try:
                event_date = datetime.strptime(event_date_str[:10], "%Y-%m-%d")
                if start_date <= event_date <= end_date:
                    # Filter by source if requested
                    source = event.get("source", "roscoe")
                    if source == "google" and not include_google:
                        continue
                    if source == "roscoe" and not include_roscoe:
                        continue
                    filtered_events.append(event)
            except (ValueError, TypeError):
                continue

        # Sort events by date/time
        filtered_events.sort(key=lambda e: (
            e.get("date") or e.get("start_date", ""),
            e.get("time") or e.get("start_time", "00:00")
        ))

        # Build UI commands
        title_suffix = f" - {days} day{'s' if days > 1 else ''}" if days > 1 else ""

        return {
            "success": True,
            "title": f"Calendar ({date}){title_suffix}",
            "commands": [
                {
                    "type": "workbench.setCenterView",
                    "view": "calendar"
                },
                {
                    "type": "calendar.setEvents",
                    "events": filtered_events,
                    "date": date,
                    "days": days
                }
            ]
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to render calendar: {str(e)}"
        }


# =============================================================================
# Word Template & PDF Export Tools
# =============================================================================

def fill_word_template(
    template_path: str,
    output_path: str,
    context: Dict[str, Any],
    export_pdf: bool = True,
) -> str:
    """
    Fill a Word (.docx) template with provided data and optionally export to PDF.
    
    This tool fills Jinja2-style placeholders ({{ variable_name }}) in Word templates
    with the values you provide. Perfect for generating legal documents like:
    - Letters of Representation
    - Medical Records Requests
    - Demand Letters
    - Settlement Agreements
    - Court Filings
    
    The template must use Jinja2 placeholder syntax: {{ variable_name }}
    
    Args:
        template_path: Workspace-relative path to the .docx template file.
                      Example: "/forms/templates/Letter_of_Representation.docx"
        output_path: Workspace-relative path for the filled document.
                    Example: "/wilson-case/Documents/Wilson_LOR.docx"
        context: Dictionary of placeholder values to fill in.
                Example: {"client_name": "John Wilson", "date": "January 15, 2024"}
        export_pdf: If True, also generate a PDF version (default: True).
        
    Returns:
        Summary of the operation including paths to generated files.
        
    Examples:
        # Generate a Letter of Representation
        fill_word_template(
            template_path="/forms/templates/Letter_of_Rep.docx",
            output_path="/wilson-case/Documents/Wilson_LOR.docx",
            context={
                "client_name": "John Wilson",
                "date_of_accident": "January 15, 2024",
                "insurance_company": "State Farm",
                "claim_number": "CLM-123456",
                "adjuster_name": "Sarah Smith"
            }
        )
        
        # Generate a Medical Records Request (DOCX only, no PDF)
        fill_word_template(
            template_path="/forms/templates/Medical_Records_Request.docx",
            output_path="/wilson-case/Medical/Records_Request_Baptist.docx",
            context={
                "patient_name": "John Wilson",
                "dob": "March 5, 1985",
                "provider_name": "Baptist Health",
                "treatment_dates": "January 15, 2024 to Present"
            },
            export_pdf=False
        )
    """
    try:
        # Convert workspace-relative paths to absolute paths
        if template_path.startswith('/'):
            template_path = template_path[1:]
        if output_path.startswith('/'):
            output_path = output_path[1:]
            
        abs_template = workspace_root / template_path
        abs_output = workspace_root / output_path
        
        # Check template exists
        if not abs_template.exists():
            return f"❌ Template not found: {template_path}\n\nCheck that the template exists in the workspace."
        
        # Fill template and optionally export PDF
        result = _fill_and_export_template(
            template_path=abs_template,
            output_path=abs_output,
            context=context,
            export_pdf=export_pdf,
        )
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            return f"❌ Template filling failed: {error_msg}"
        
        # Build success response
        lines = [
            "✅ **Template Filled Successfully**",
            "",
            f"📄 **DOCX Output:** `{output_path}`",
        ]
        
        if result.get("pdf_path"):
            pdf_rel = Path(result["pdf_path"]).relative_to(workspace_root)
            lines.append(f"📑 **PDF Output:** `{pdf_rel}`")
        elif export_pdf and result.get("pdf_error"):
            lines.append(f"⚠️ **PDF Export Failed:** {result['pdf_error']}")
        
        # Report placeholders
        if result.get("placeholders_filled"):
            lines.append(f"\n**Placeholders Filled ({len(result['placeholders_filled'])}):**")
            for p in result["placeholders_filled"][:10]:
                lines.append(f"  ✓ {p}")
            if len(result["placeholders_filled"]) > 10:
                lines.append(f"  ... and {len(result['placeholders_filled']) - 10} more")
        
        if result.get("placeholders_unfilled"):
            lines.append(f"\n**⚠️ Unfilled Placeholders ({len(result['placeholders_unfilled'])}):**")
            for p in result["placeholders_unfilled"]:
                lines.append(f"  ○ {p}")
        
        return "\n".join(lines)
        
    except TemplateNotFoundError as e:
        return f"❌ Template not found: {str(e)}"
    except LibreOfficeNotFoundError as e:
        return f"❌ LibreOffice not available for PDF export: {str(e)}\n\nThe DOCX was created but PDF export requires LibreOffice."
    except TemplateError as e:
        return f"❌ Template error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def export_pdf_from_docx(
    docx_path: str,
    output_dir: Optional[str] = None,
) -> str:
    """
    Convert a Word document (.docx) to high-fidelity PDF using LibreOffice.
    
    This produces professional-quality PDFs that preserve the original Word
    document's formatting, fonts, tables, and layout.
    
    Args:
        docx_path: Workspace-relative path to the .docx file.
                  Example: "/wilson-case/Documents/Demand_Letter.docx"
        output_dir: Optional directory for the PDF output.
                   If not provided, PDF is saved alongside the DOCX.
                   Example: "/wilson-case/Documents/PDFs/"
                   
    Returns:
        Summary including the path to the generated PDF.
        
    Examples:
        # Convert a single document
        export_pdf_from_docx("/wilson-case/Documents/Settlement_Agreement.docx")
        
        # Specify output directory
        export_pdf_from_docx(
            docx_path="/wilson-case/Documents/Demand_Letter.docx",
            output_dir="/wilson-case/Documents/PDFs/"
        )
    """
    try:
        # Convert workspace-relative paths to absolute paths
        if docx_path.startswith('/'):
            docx_path = docx_path[1:]
        abs_docx = workspace_root / docx_path
        
        if not abs_docx.exists():
            return f"❌ Document not found: {docx_path}"
        
        abs_output_dir = None
        if output_dir:
            if output_dir.startswith('/'):
                output_dir = output_dir[1:]
            abs_output_dir = workspace_root / output_dir
        
        result = _convert_docx_to_pdf(
            input_path=abs_docx,
            output_dir=abs_output_dir,
        )
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            return f"❌ PDF conversion failed: {error_msg}"
        
        pdf_rel = Path(result["output_path"]).relative_to(workspace_root)
        return f"✅ **PDF Generated Successfully**\n\n📑 **Output:** `{pdf_rel}`"
        
    except LibreOfficeNotFoundError as e:
        return f"❌ LibreOffice not available: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def convert_doc_to_docx(
    doc_path: str,
    output_dir: Optional[str] = None,
) -> str:
    """
    Convert a legacy Word document (.doc) to modern .docx format.
    
    Use this when you have old .doc files that need to be converted to
    .docx format for template filling or other processing.
    
    Args:
        doc_path: Workspace-relative path to the .doc file.
                 Example: "/forms/templates/Old_Template.doc"
        output_dir: Optional directory for the output .docx file.
                   If not provided, saved alongside the original.
                   
    Returns:
        Summary including the path to the converted .docx file.
        
    Examples:
        convert_doc_to_docx("/forms/templates/Legacy_Letter.doc")
        
        convert_doc_to_docx(
            doc_path="/forms/Legacy_Form.doc",
            output_dir="/forms/converted/"
        )
    """
    try:
        # Convert workspace-relative paths to absolute paths
        if doc_path.startswith('/'):
            doc_path = doc_path[1:]
        abs_doc = workspace_root / doc_path
        
        if not abs_doc.exists():
            return f"❌ Document not found: {doc_path}"
        
        abs_output_dir = None
        if output_dir:
            if output_dir.startswith('/'):
                output_dir = output_dir[1:]
            abs_output_dir = workspace_root / output_dir
        
        result = _convert_doc_to_docx(
            input_path=abs_doc,
            output_dir=abs_output_dir,
        )
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            return f"❌ Conversion failed: {error_msg}"
        
        docx_rel = Path(result["output_path"]).relative_to(workspace_root)
        return f"✅ **Conversion Successful**\n\n📄 **Output:** `{docx_rel}`"
        
    except LibreOfficeNotFoundError as e:
        return f"❌ LibreOffice not available: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def list_template_variables(
    template_path: str,
) -> str:
    """
    List all placeholder variables in a Word template.
    
    Use this to discover what variables a template expects before filling it.
    This helps you prepare the correct context dictionary for fill_word_template.
    
    Args:
        template_path: Workspace-relative path to the .docx template.
                      Example: "/forms/templates/Letter_of_Rep.docx"
                      
    Returns:
        List of placeholder variable names found in the template.
        
    Examples:
        list_template_variables("/forms/templates/Medical_Records_Request.docx")
        list_template_variables("/forms/templates/Demand_Letter.docx")
    """
    try:
        # Convert workspace-relative path to absolute path
        if template_path.startswith('/'):
            template_path = template_path[1:]
        abs_template = workspace_root / template_path
        
        if not abs_template.exists():
            return f"❌ Template not found: {template_path}"
        
        placeholders = _list_template_placeholders(abs_template)
        
        if not placeholders:
            return f"ℹ️ **No placeholders found in template**\n\nThe template `{template_path}` doesn't contain any Jinja2-style placeholders ({{ variable_name }})."
        
        lines = [
            f"📋 **Template Variables in `{template_path}`**",
            "",
            f"Found **{len(placeholders)}** placeholder(s):",
            "",
        ]
        
        for p in placeholders:
            lines.append(f"  • `{p}`")
        
        lines.extend([
            "",
            "---",
            "**Usage:** Provide these as keys in the `context` dictionary when calling `fill_word_template()`.",
        ])
        
        return "\n".join(lines)
        
    except TemplateNotFoundError as e:
        return f"❌ Template not found: {str(e)}"
    except TemplateError as e:
        return f"❌ Template error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def check_document_tools_status() -> str:
    """
    Check the status of document generation tools and dependencies.
    
    Use this to verify that all required dependencies (docxtpl, python-docx,
    LibreOffice) are properly installed and available.
    
    Returns:
        Diagnostic information about document tool availability.
        
    Examples:
        check_document_tools_status()
    """
    try:
        deps = _check_word_deps()
        
        lines = [
            "**Document Generation Tools Status**",
            "",
            "**Python Libraries:**",
            f"  {'✅' if deps['docxtpl_available'] else '❌'} docxtpl: {'Available' if deps['docxtpl_available'] else 'Not installed'}",
            f"  {'✅' if deps['python_docx_available'] else '❌'} python-docx: {'Available' if deps['python_docx_available'] else 'Not installed'}",
            "",
            "**External Tools:**",
            f"  {'✅' if deps['libreoffice_available'] else '❌'} LibreOffice: {'Available' if deps['libreoffice_available'] else 'Not installed'}",
        ]
        
        if deps['libreoffice_path']:
            lines.append(f"     Path: `{deps['libreoffice_path']}`")
        
        lines.append("")
        
        if deps['all_available']:
            lines.append("✅ **All document tools are available!**")
            lines.append("")
            lines.append("Available operations:")
            lines.append("  • Fill Word templates with `fill_word_template()`")
            lines.append("  • Export to PDF with `export_pdf_from_docx()`")
            lines.append("  • Convert .doc to .docx with `convert_doc_to_docx()`")
            lines.append("  • List template variables with `list_template_variables()`")
        else:
            lines.append(f"⚠️ **Missing dependencies:** {', '.join(deps['missing'])}")
            lines.append("")
            lines.append("**Installation:**")
            if "docxtpl" in deps['missing'] or "python-docx" in deps['missing']:
                lines.append("  Python: `pip install docxtpl python-docx`")
            if "LibreOffice (soffice)" in deps['missing']:
                lines.append("  macOS: `brew install --cask libreoffice`")
                lines.append("  Ubuntu: `sudo apt install libreoffice`")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"❌ Error checking status: {str(e)}"
