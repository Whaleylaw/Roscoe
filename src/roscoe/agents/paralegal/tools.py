"""
Roscoe Paralegal Agent Tools

This module provides tools for the paralegal agent:
- Internet search (Tavily)
- Multimodal analysis (image, audio, video)
- Slack notifications
- Script execution with GCS filesystem access (Docker)
"""

import os
from typing import Literal, Optional
from pathlib import Path
from tavily import TavilyClient
from langchain_core.messages import HumanMessage
from roscoe.agents.paralegal.models import multimodal_llm
import base64

# Import Docker-based script executor
from roscoe.agents.paralegal.script_executor import (
    execute_python_script as _execute_python_script,
    format_execution_result,
    ScriptExecutionError,
    check_docker_available,
    get_execution_stats,
)

# Initialize the Tavily client
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY", ""))

# Initialize Slack client (optional - only if token is set)
slack_client = None
if os.environ.get("SLACK_BOT_TOKEN"):
    try:
        from slack_sdk import WebClient
        slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    except ImportError:
        print("Warning: slack-sdk not installed. Slack integration disabled.")

# Get workspace root for file operations (paralegal agent workspace)
# Path is relative to repo root (5 levels up from this file)
workspace_root = Path(__file__).parent.parent.parent.parent.parent / "workspace_paralegal"


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

    try:
        search_results = tavily_client.search(
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

        # Create message with image
        message = HumanMessage(
            content=[
                {"type": "text", "text": analysis_prompt},
                {
                    "type": "image_url",
                    "image_url": f"data:{mime_type};base64,{image_data}"
                }
            ]
        )

        # Get analysis from Gemini
        response = multimodal_llm.invoke([message])

        return f"**Image Analysis: {file_path}**\n\n{response.content}"

    except Exception as e:
        return f"Image analysis error: {str(e)}"


# Define the audio analysis tool
def analyze_audio(
    file_path: str,
    analysis_focus: Optional[str] = None,
) -> str:
    """
    Analyze an audio file using Google Gemini's multimodal audio capabilities.

    Perfect for analyzing 911 calls, witness statements, dispatch recordings,
    recorded depositions, or any audio evidence in personal injury cases.

    Args:
        file_path: Workspace-relative path to the audio file (e.g., "/case_folder/audio/911_call.mp3")
        analysis_focus: Optional specific analysis focus. If not provided, provides transcription + legal analysis.

    Returns:
        Transcription and analysis of the audio with legally relevant observations.

    Examples:
        analyze_audio("/mo_alif/investigation/911_call_03-15-2024.mp3")
        analyze_audio("/mo_alif/investigation/witness_statement.wav", "Focus on the witness's description of the accident sequence")
    """
    try:
        # Convert workspace-relative path to absolute path
        if file_path.startswith('/'):
            file_path = file_path[1:]  # Remove leading slash
        abs_path = workspace_root / file_path

        if not abs_path.exists():
            return f"Error: Audio file not found at {file_path}"

        # Read and encode audio
        with open(abs_path, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode('utf-8')

        # Determine audio type
        ext = abs_path.suffix.lower()
        mime_types = {
            '.mp3': 'audio/mp3',
            '.wav': 'audio/wav',
            '.m4a': 'audio/m4a',
            '.ogg': 'audio/ogg',
            '.flac': 'audio/flac'
        }
        mime_type = mime_types.get(ext, 'audio/mp3')

        # Default legal evidence analysis prompt
        if not analysis_focus:
            analysis_focus = """Analyze this audio recording as legal evidence in a personal injury case. Provide:

1. **Complete Transcription**: Full verbatim transcript of all speech
2. **Speaker Identification**: Identify different speakers (Caller, Dispatcher, Witness, etc.)
3. **Timeline of Statements**: Key statements with timestamps
4. **Emotional State**: Tone, urgency, emotional indicators in speech
5. **Key Factual Statements**: Important facts stated about the incident
6. **Inconsistencies or Contradictions**: Any conflicting statements
7. **Background Sounds**: Relevant ambient sounds or environmental audio
8. **Legally Relevant Observations**: Statements that support or weaken case theories

Be thorough and accurate. Use quotation marks for direct quotes."""

        # Create message with audio
        message = HumanMessage(
            content=[
                {"type": "text", "text": analysis_focus},
                {
                    "type": "media",
                    "media_url": f"data:{mime_type};base64,{audio_data}"
                }
            ]
        )

        # Get analysis from Gemini
        response = multimodal_llm.invoke([message])

        return f"**Audio Analysis: {file_path}**\n\n{response.content}"

    except Exception as e:
        return f"Audio analysis error: {str(e)}"


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

        # Create message with video
        message = HumanMessage(
            content=[
                {"type": "text", "text": analysis_focus},
                {
                    "type": "media",
                    "media_url": f"data:{mime_type};base64,{video_data}"
                }
            ]
        )

        # Get analysis from Gemini
        response = multimodal_llm.invoke([message])

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
    if not slack_client:
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
        response = slack_client.chat_postMessage(
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
    if not slack_client:
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
        response = slack_client.files_upload_v2(
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
