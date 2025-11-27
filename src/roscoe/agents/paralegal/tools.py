import os
from typing import Literal, Optional
from pathlib import Path
from tavily import TavilyClient
from langchain_core.messages import HumanMessage
from roscoe.agents.paralegal.models import multimodal_llm
import base64
import shlex

# Initialize the Tavily client
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Initialize Slack client (optional - only if token is set)
slack_client = None
if os.environ.get("SLACK_BOT_TOKEN"):
    try:
        from slack_sdk import WebClient
        slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    except ImportError:
        print("Warning: slack-sdk not installed. Slack integration disabled.")

# Initialize Runloop client (optional - only if API key is set)
runloop_client = None
if os.environ.get("RUNLOOP_API_KEY"):
    try:
        from runloop_api_client import Runloop
        runloop_client = Runloop(bearer_token=os.environ["RUNLOOP_API_KEY"])
    except ImportError:
        print("Warning: runloop-api-client not installed. Code execution disabled.")

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


# Define the code execution tool (Runloop sandbox)
def execute_code(
    command: str,
    working_dir: str = "/workspace",
    timeout: int = 60,
    input_files: Optional[list[str]] = None,
) -> str:
    """
    Execute shell commands or Python code in an isolated Runloop sandbox.

    Perfect for running Tools scripts, data analysis, file processing, or any
    code execution tasks. Each execution runs in a clean, isolated container.
    Can auto-upload files from your workspace to the sandbox before execution.

    Use this to:
    - Execute Tools scripts: `python /workspace/Tools/pubmed_search.py "query"`
    - Run data analysis, process files, extract PDFs
    - Install packages and run complex workflows
    - Any bash/Python code that needs execution

    Args:
        command: Shell command or script to execute
        working_dir: Working directory in sandbox (default: /workspace)
        timeout: Maximum execution time in seconds (default: 60)
        input_files: Optional list of workspace paths to upload to the sandbox before running.
                    (e.g. ["/Tools/script.py", "/data/file.csv"]).
                    Files will be uploaded to matching paths under /home/user (the default sandbox CWD).
                    Example: "/Tools/script.py" uploads to "./Tools/script.py"

    Returns:
        Command output (stdout + stderr) or error message

    Examples:
        execute_code("python /workspace/Tools/pubmed_search.py 'whiplash'")
        execute_code("ls -la /workspace/projects/Abby-Sitgraves-MVA-7-13-2024")
        execute_code("pip install pandas && python analyze.py", input_files=["/Tools/analyze.py"])
    """
    if not runloop_client:
        return "Code execution not configured. Set RUNLOOP_API_KEY environment variable."

    try:
        # Create a devbox (sandbox container)
        devbox = runloop_client.devboxes.create_and_await_running(
            name=f"roscoe-exec-{os.urandom(4).hex()}",
            # Can add blueprint_id here if you have a pre-configured environment
        )

        try:
            # Upload input files if requested
            uploaded_paths = []
            if input_files:
                for file_path in input_files:
                    # Resolve local path
                    if file_path.startswith('/'):
                        clean_path = file_path[1:]
                    else:
                        clean_path = file_path
                    
                    local_abs_path = workspace_root / clean_path
                    
                    if not local_abs_path.exists():
                        return f"Error: Input file not found: {file_path}"
                    
                    # Determine remote path (preserve structure relative to workspace)
                    # Runloop upload path is relative to home, so we map /workspace -> . (or explicit path)
                    # NOTE: RunLoop standard blueprint usually has user home.
                    # We'll assume we want to place files in /home/user/workspace or similar,
                    # but let's stick to uploading to relative paths that mirror the input.
                    remote_path = clean_path
                    
                    with open(local_abs_path, "rb") as f:
                        runloop_client.devboxes.upload_file(
                            devbox.id,
                            path=remote_path,
                            file=f
                        )
                    uploaded_paths.append(remote_path)

            # Execute command in devbox (devbox_id is positional!)
            # If we uploaded files to relative paths, they are likely in the default workdir (e.g. /home/user)
            # If the user expects them in /workspace, we might need to adjust or move them.
            # For now, we assume the command handles paths or we run relative to where files landed.
            
            result = runloop_client.devboxes.execute_and_await_completion(
                devbox.id,  # Positional argument
                command=command,  # Keyword argument
            )

            # Format output
            output = []
            if uploaded_paths:
                output.append(f"**Uploaded Files (relative to sandbox home):**\n" + "\n".join([f"- {p}" for p in uploaded_paths]))
                
            if result.stdout:
                output.append(f"**stdout:**\n{result.stdout}")
            if result.stderr:
                output.append(f"**stderr:**\n{result.stderr}")

            exit_code = result.exit_status or 0
            output.append(f"\n**Exit code:** {exit_code}")

            return "\n\n".join(output) if output else "Command completed (no output)"

        finally:
            # Clean up devbox
            try:
                runloop_client.devboxes.shutdown(devbox.id)  # Positional
            except:
                pass  # Best effort cleanup

    except Exception as e:
        return f"Code execution error: {str(e)}"
