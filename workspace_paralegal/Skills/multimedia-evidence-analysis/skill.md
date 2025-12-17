# Multimedia Evidence Analysis Skill

**FOR MULTIMODAL SUB-AGENT (Gemini 3 Pro)**

This skill provides complete instructions for analyzing audio and video evidence WITH full case context to deliver attorney-ready analysis with transcription, speaker identification, and legal insights.

---

## Your Task

You are analyzing multimedia evidence (audio or video) for a personal injury case. Your analysis must include case context, not just raw transcription.

---

## Phase 1: Load Case Context FIRST

**Before analyzing the multimedia file, gather case context:**

### Step 1: Read Case Overview

```python
# Read the case overview from the case folder
read_file("projects/{case-folder}/overview.json")
```

**Extract from overview:**
- `client_name` - Full name of the client
- `case_summary` - Summary of the incident
- `accident_date` - When the incident occurred
- Current case status and key facts

### Step 2: Read Accident Report

```python
# Look in the Investigation folder for the accident report
ls("projects/{case-folder}/Investigation/")
# Find and read: "Traffic Collision Report" (PDF or markdown)
read_file("projects/{case-folder}/Investigation/{accident-report-file}")
```

**Extract from accident report:**
- `incident_location` - Where incident occurred
- `incident_summary` - What happened (from report)
- Vehicles involved
- Witnesses identified
- Officer observations

### Step 3: Read Litigation Documents (if available)

```python
# Check for complaint or other litigation documents
ls("projects/{case-folder}/Litigation/")
# Read complaint if available
read_file("projects/{case-folder}/Litigation/complaint.pdf")
```

**What you now know (define these variables for use throughout analysis):**
- `client_name` - Client's full name
- `incident_summary` - What happened in the incident
- `incident_date` - When it occurred
- `incident_location` - Where it occurred
- `client_role` - Plaintiff or defendant
- `disputed_facts` - What's contested (from complaint/answer)
- `known_witnesses` - Who was present

---

## Phase 2: Analyze Multimedia Evidence with Gemini Native Capabilities

**Now analyze the audio/video file using Gemini's native multimodal processing:**

### For Audio or Video Files

Use Python code execution with Gemini's File API:

```python
import google.generativeai as genai
import os

# Configure API (already set via GOOGLE_API_KEY environment variable)
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Upload the multimedia file - use workspace path
# Files are accessible at /workspace/ within the execution environment
file_path = "/workspace/projects/{case-folder}/Investigation/{video-file}.mp4"
uploaded_file = genai.upload_file(file_path)

# Wait for processing
import time
while uploaded_file.state.name == "PROCESSING":
    time.sleep(1)
    uploaded_file = genai.get_file(uploaded_file.name)

# Analyze with case context
model = genai.GenerativeModel("gemini-3-pro-preview")

# Create analysis prompt with case context
prompt = f'''Analyze this {"audio" if ".mp3" in file_path or ".wav" in file_path else "video"} as legal evidence in a personal injury case.

CASE CONTEXT:
- Client: {client_name} ({client_role})
- Incident: {incident_summary}
- Date: {incident_date}
- Location: {incident_location}
- Disputed Facts: {disputed_facts}
- Known Witnesses: {known_witnesses}

ANALYSIS REQUIRED:

1. **Full Transcript with Timestamps**
   - Transcribe all speech with [HH:MM:SS] timestamps
   - Use exact quotes

2. **Speaker Identification** (use case context to identify intelligently)
   - Don't just say "Speaker A, Speaker B"
   - Make informed inferences: "Speaker identified as {client_name} based on: provides personal information matching client, describes incident consistent with case facts"
   - Note basis for each identification

3. **Visual Timeline** (for video only)
   - Describe what's happening in the video with timestamps
   - Note key events: [HH:MM:SS] **KEY EVENT**: Description
   - Identify vehicles, people, locations visible
   - Note damage, injuries, conditions, weather

4. **Comparison to Case Facts**
   - What in this evidence SUPPORTS client's version: {incident_summary}
   - What CONTRADICTS or raises questions
   - What NEW facts are revealed

5. **Legal Observations**
   - Evidence of fault/liability
   - Evidence of injury causation
   - Contemporaneous complaints of injury
   - Helpful evidence for case
   - Red flags or weaknesses

6. **Key Moments** (for video)
   - Identify critical timestamps where key events occur
   - Note any frames that should be extracted for evidence
   - Example: "00:01:15 - Red light violation visible, extract frame"

Be thorough, objective, cite timestamps for everything, and think like an attorney evaluating evidence.'''

response = model.generate_content([uploaded_file, prompt])

# Clean up (optional - files auto-delete after 48 hours)
genai.delete_file(uploaded_file.name)

print(response.text)
```

**Important Path Notes:**
- Within code execution, files are accessible at `/workspace/` paths
- Virtual paths (`projects/...`) need to be translated to `/workspace/projects/...` in code
- Video files must be under 2GB

---

## Phase 3: Extract Video Frames (if needed)

If analysis identifies key moments, extract frames using a Python script.

**Ask the main agent to run frame extraction via `execute_python_script`:**

```
Main agent: Please extract frames at these critical timestamps:
- 00:01:15 - Red light violation visible
- 00:02:30 - Impact moment
- 00:03:45 - Vehicle damage visible

Use execute_python_script to run:
execute_python_script(
    script_path="Tools/extract_video_frames.py",
    script_args=[
        "/workspace/projects/{case-folder}/Investigation/{video-file}.mp4",
        "00:01:15",
        "00:02:30", 
        "00:03:45"
    ]
)
```

**When to extract frames:**
- Traffic violations visible (red light, lane departure)
- Impact moment
- Vehicle damage visible
- Injuries visible
- Scene conditions (weather, lighting, road)
- Any moment that proves/disproves a fact

---

## Phase 4: Synthesize Attorney-Ready Report

**Format your analysis into this structure and save to `Reports/`:**

```markdown
# Multimedia Evidence Analysis: {Evidence Name}

**Case:** {client_name} v. {Defendant}
**Evidence Type:** 911 Call / Dashcam Video / Body Camera / Police Radio / Deposition
**Date Analyzed:** {current_date}
**Analyst:** Roscoe (Multimedia Evidence Analysis)

---

## Evidence Overview

- **File:** {file_name}
- **Duration:** {duration}
- **Date/Time Recorded:** {recording_datetime}
- **Relevance:** {why_this_matters_to_case}

---

## Case Context Summary

[Brief summary of case facts loaded in Phase 1]

---

## Full Transcript

[Complete transcript with timestamps and speaker identification]

[HH:MM:SS] **SPEAKER (Identification Basis):** "Quote"

---

## Visual Timeline (Video Only)

| Timestamp | Description | Legal Significance |
|-----------|-------------|-------------------|
| 00:00:00 | Video begins, shows... | |
| 00:01:15 | **KEY**: Red light visible | Proves defendant negligence |
| ... | ... | ... |

---

## Speaker Identification

| Speaker | Identification | Basis for ID |
|---------|---------------|--------------|
| Male Voice 1 | {client_name} | States personal information, describes injuries consistent with complaint |
| Female Voice | 911 Dispatcher | Official procedural language, call routing |
| ... | ... | ... |

---

## Key Evidence Points

### Supports Client's Case:
1. [Finding with timestamp]
2. [Finding with timestamp]

### Raises Questions / Weaknesses:
1. [Finding with timestamp]
2. [Finding with timestamp]

### New Facts Revealed:
1. [Finding with timestamp]

---

## Extracted Frames (if applicable)

| Timestamp | Description | File |
|-----------|-------------|------|
| 00:01:15 | Red light visible | `Reports/frames/{case}_00-01-15.jpg` |
| 00:02:30 | Impact moment | `Reports/frames/{case}_00-02-30.jpg` |

---

## Legal Analysis

### Liability Evidence:
[What this evidence shows about fault]

### Causation Evidence:
[What this evidence shows about injury causation]

### Damages Evidence:
[What this evidence shows about injuries/pain]

---

## Recommendations

1. [Action item for attorney]
2. [Additional evidence to obtain]
3. [Witness to depose based on this evidence]
```

---

## Output Location

**Save your analysis report to:**
- **File:** `projects/{case-folder}/Reports/multimedia_analysis_{evidence_name}.md`
- **Format:** Markdown with all sections above

**Save extracted frames to:**
- **Directory:** `projects/{case-folder}/Reports/frames/`
- **Naming:** `{case_name}_{timestamp}.jpg`

---

## CRITICAL: File Paths

**ALWAYS use workspace-relative paths:**

**For FilesystemBackend tools (read_file, ls, write_file):**
- ✅ CORRECT: `projects/{case-folder}/Reports/analysis.md`
- ✅ CORRECT: `projects/{case-folder}/Investigation/video.mp4`
- ❌ WRONG: `/Volumes/X10 Pro/Roscoe/workspace/Reports/...` (Mac path)
- ❌ WRONG: `../workspace/...` (relative path)

**For code execution (when accessing files in Python):**
- ✅ CORRECT: `/workspace/projects/{case-folder}/Investigation/video.mp4`
- ❌ WRONG: `/Volumes/X10 Pro/...` (Mac path)

---

## Tools Available

**FilesystemBackend Tools:**
- `ls` - List files and directories
- `read_file` - Read text files and extract text from PDFs
- `grep` - Search for text patterns
- `write_file` - Create new files

**Code Execution:**
- Native Python code execution with access to google.generativeai
- Files accessible at `/workspace/` paths

**For video frame extraction, ask main agent to use:**
- `execute_python_script` with `Tools/extract_video_frames.py`

---

## Important Notes

1. **Load case context FIRST** - Never analyze in vacuum
2. **Use case facts to inform speaker ID** - Don't use generic "Speaker A"
3. **Think like an attorney** - What does this evidence prove or disprove?
4. **Cite timestamps for everything** - Makes evidence usable in court
5. **Note weaknesses too** - Attorney needs to know problems before opponents find them
6. **Extract key frames** - Visual evidence for depositions and trial
