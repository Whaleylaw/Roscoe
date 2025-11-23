import os
from typing import Literal, Optional
from pathlib import Path
from tavily import TavilyClient
from langchain_core.messages import HumanMessage
from models import multimodal_llm
import base64

# Initialize the Tavily client
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Get workspace root for file operations
workspace_root = Path(__file__).parent / "workspace"

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
