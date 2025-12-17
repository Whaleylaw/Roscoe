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
multimodal_sub_agent_description = f"""General-purpose assistant with multimodal capabilities (images, audio, video analysis) and built-in Python code execution. Use this agent for tasks requiring: document-heavy processing, PDF analysis, image/photo analysis, audio transcription, video analysis, multimedia evidence processing, data processing with code, or any task combining multiple modalities. Currently using {MODEL_CAPABILITIES.get(MODEL_PROVIDER, 'configured model')} with Gemini's native code execution enabled."""

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

**For quick processing tasks**, use my built-in code execution:
- Read and process files directly
- Transform data inline
- Quick calculations and analysis

**For complex scripts**, use the main agent's `execute_python_script` tool:
- Pre-written scripts in /Tools/
- Docker-based execution
- Long-running processes

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

### Code Execution (Gemini Native)

**IMPORTANT:** I have Python code execution built directly into my model. This is NOT a tool you call - it's a capability I have. When you need code executed, simply express what you need done, and I will automatically generate and execute Python code to accomplish it.

**How It Works:**
- You don't need to "call" code_execution - it's automatic
- Just describe what you need: "Calculate the sum of the first 50 prime numbers"
- I will automatically generate and execute the Python code
- Results are returned directly in the response

**What I Can Do with Code Execution:**
- Process multimedia files (images, audio, video)
- Perform data analysis and transformation
- Manipulate files and convert formats
- Execute quick calculations and computations
- Read and process files from the workspace
- Generate visualizations and plots

**Available Libraries:**
- NumPy, Pandas (data processing)
- PIL/Pillow (image processing)
- Matplotlib (visualization)
- Standard library (os, json, pathlib, etc.)

**When to Use Code Execution vs execute_python_script:**
- **Use my built-in code execution** for: Quick calculations, data transformations, file processing, inline analysis
- **Use execute_python_script tool** for: Complex scripts, Docker-based execution, long-running processes, pre-written scripts in /Tools/

**Example:**
If you need to analyze a CSV file, just say: "Read the file at /projects/Case-Name/data.csv and calculate the average of column X"

I will automatically:
1. Generate Python code to read the file
2. Execute it using my built-in code execution
3. Return the results

You don't need to ask me to "use code_execution" - I'll use it automatically when code is needed.
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
        # IMPORTANT: Use the getter function, not the module-level variable
        # The module-level multimodal_llm is None (for backwards compatibility)
        from roscoe.agents.paralegal.models import get_multimodal_llm
        from roscoe.agents.paralegal.tools import analyze_image, analyze_audio, analyze_video
        _multimodal_sub_agent_instance = {
            "name": "multimodal-agent",
            "description": multimodal_sub_agent_description,
            "system_prompt": multimodal_sub_agent_prompt,
            "tools": [analyze_image, analyze_audio, analyze_video],  # Multimodal analysis tools
            "model": get_multimodal_llm(),  # Lazily initialized model with code_execution
        }
    return _multimodal_sub_agent_instance

# For backwards compatibility - this should NOT be used directly
# Use get_multimodal_sub_agent() instead to avoid pickle errors
multimodal_sub_agent = None  # Set to None to force use of getter
