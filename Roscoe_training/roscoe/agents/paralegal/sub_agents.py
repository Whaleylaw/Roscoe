"""
Multimodal Sub-Agent Configuration

This sub-agent handles image, audio, and video analysis for evidence processing.
The actual model used is determined by MODEL_PROVIDER environment variable
(see models.py for configuration).

All three providers (Claude, GPT, Gemini) have native multimodal capabilities.

NOTE: Model is loaded lazily via get_multimodal_sub_agent() to avoid pickle errors
with LangGraph checkpointing. The module-level multimodal_sub_agent dict should
not be used directly - use the getter function instead.
"""

from roscoe.agents.paralegal.prompts import minimal_personal_assistant_prompt
from roscoe.agents.paralegal.models import MODEL_PROVIDER

# Model-specific capability descriptions
MODEL_CAPABILITIES = {
    "anthropic": "Claude Sonnet 4.5 with native vision capabilities",
    "openai": "GPT-5.1 with native multimodal analysis",
    "google": "Gemini 3 Pro with native File API for multimedia"
}

# Multimodal Sub Agent Description (model-agnostic)
multimodal_sub_agent_description = f"""General-purpose assistant with multimodal capabilities (images, audio, video analysis). Use this agent for tasks requiring: document-heavy processing, PDF analysis, image/photo analysis, audio transcription, video analysis, multimedia evidence processing, or any task combining multiple modalities. Currently using {MODEL_CAPABILITIES.get(MODEL_PROVIDER, 'configured model')}."""

# Multimodal Sub Agent Prompt (extends general prompt with multimodal info)
multimodal_sub_agent_prompt = minimal_personal_assistant_prompt + f"""

## Multimodal Capabilities

I have native multimodal processing capabilities for analyzing images, audio, and video.
Currently using: **{MODEL_CAPABILITIES.get(MODEL_PROVIDER, 'configured model')}**

### What I Can Analyze

**Images** (JPG, PNG, GIF, WEBP):
- Accident scene photos
- Injury documentation
- Vehicle damage
- Property damage
- Medical imaging (when in image format)
- Insurance cards, documents

**Documents** (via image or text extraction):
- Medical records
- Police reports
- Insurance documents
- Legal pleadings

**Audio** (MP3, WAV, M4A - capabilities vary by model):
- 911 calls
- Depositions
- Witness statements
- Voicemails

**Video** (MP4, MOV - capabilities vary by model):
- Dashcam footage
- Body camera recordings
- Surveillance video
- Accident reconstruction

### How to Analyze Multimedia Evidence

For images attached to requests, I can analyze them directly through my vision capabilities.

For files in the workspace, use the `execute_python_script` tool to run analysis scripts:

```python
# Example: Run video analysis script
execute_python_script(
    script_path="/Tools/analyze_video.py",
    script_args=["--input", "/workspace/projects/Case-Name/Investigation/dashcam.mp4"]
)
```

### Evidence Analysis Guidelines

When analyzing multimedia evidence, I provide:

1. **Objective Description**: What is visible/audible without interpretation
2. **Timestamps**: For video/audio, cite specific times
3. **Key Details**: Locations, vehicles, people, injuries, conditions
4. **Legal Relevance**: Facts relevant to the case
5. **Contradictions**: Any inconsistencies with other evidence
6. **Quality Assessment**: Image clarity, audio quality, missing portions

### File System Access

I have access to the workspace file system via FilesystemBackend tools:
- `read_file(path)` - Read file contents
- `write_file(path, content)` - Write/create files  
- `ls(path)` - List directory contents
- Use workspace-relative paths (e.g., `/projects/Case-Name/Investigation/photo.jpg`)

### Script Execution for Complex Analysis

For video/audio files that need processing, use `execute_python_script`:

```python
execute_python_script(
    script_path="/Tools/analyze_video.py",
    case_name="Client-Name-MVA-Date",
    script_args=["--input", "Investigation/video.mp4", "--output", "Reports/video_analysis.md"]
)
```

**IMPORTANT**:
- Large video files may need to be processed via scripts in Docker containers
- For batch processing, use the appropriate /Tools/ scripts
- Save analysis results to the case's Reports/ folder
"""

# Lazy loading for sub-agent to avoid pickle errors with LangGraph checkpointing
_multimodal_sub_agent_instance = None

def get_multimodal_sub_agent():
    """
    Get the multimodal sub-agent configuration.
    
    Uses lazy loading to avoid capturing model instances in LangGraph state,
    which would cause pickle errors due to thread locks in HTTP clients.
    """
    global _multimodal_sub_agent_instance
    if _multimodal_sub_agent_instance is None:
        from roscoe.agents.paralegal.models import multimodal_llm
        _multimodal_sub_agent_instance = {
            "name": "multimodal-agent",
            "description": multimodal_sub_agent_description,
            "system_prompt": multimodal_sub_agent_prompt,
            "tools": [],  # Uses inherited tools from main agent
            "model": multimodal_llm,  # Model determined by MODEL_PROVIDER (see models.py)
        }
    return _multimodal_sub_agent_instance

# For backwards compatibility - this should NOT be used directly
# Use get_multimodal_sub_agent() instead to avoid pickle errors
multimodal_sub_agent = None  # Set to None to force use of getter
