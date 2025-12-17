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

```bash
# Read the case overview from the case folder
read_file("/projects/{case-folder}/case_information/overview.json")
```

**Extract from overview:**
- `client_name` - Full name of the client
- `case_summary` - Summary of the incident
- `accident_date` - When the incident occurred
- Current case status and key facts

### Step 2: Read Accident Report

```bash
# Look in the Investigation folder for the accident report
ls("/projects/{case-folder}/Investigation/")
# Find and read: "Traffic Collision Report" (PDF or markdown)
read_file("/projects/{case-folder}/Investigation/{accident-report-file}")
```

**Extract from accident report:**
- `incident_location` - Where incident occurred
- `incident_summary` - What happened (from report)
- Vehicles involved
- Witnesses identified
- Officer observations

### Step 3: Read Litigation Documents (if available)

```bash
# Check for complaint or other litigation documents
ls("/projects/{case-folder}/Litigation/")
# Read complaint if available
read_file("/projects/{case-folder}/Litigation/complaint.pdf")
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

# Upload the multimedia file
file_path = "/absolute/path/to/audio_or_video_file"  # Convert workspace path to absolute
uploaded_file = genai.upload_file(file_path)

# Wait for processing
import time
while uploaded_file.state.name == "PROCESSING":
    time.sleep(1)
    uploaded_file = genai.get_file(uploaded_file.name)

# Analyze with case context
model = genai.GenerativeModel("gemini-3-pro-preview")

# Create analysis prompt with case context
prompt = f'''Analyze this {"audio" if ".mp3" or ".wav" in file_path else "video"} as legal evidence in a personal injury case.

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

**Important:**
- Convert workspace-relative paths to absolute paths before uploading to Gemini
- Video files must be under 2GB
- Use absolute paths: `os.path.join("/Volumes/X10 Pro/Roscoe/workspace", path.lstrip("/"))`

---

## Phase 3: Extract Video Frames (if needed)

If analysis identifies key moments, extract frames using ffmpeg:

```bash
# Extract frame at critical timestamp
ffmpeg -i /absolute/path/to/video.mp4 -ss 00:01:15 -frames:v 1 /Reports/frames/{video_name}_00-01-15.jpg
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

**Format your analysis into this structure and save to `/Reports/`:**

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

**Incident:** {incident_summary}

**Client's Version:** {client_version_from_case_summary}

**Disputed Facts:**
- {fact_1}
- {fact_2}

---

## Transcript

### Full Transcript with Timestamps

[00:00:00 - 00:00:05] **Speaker (identified as: 911 Dispatcher)**: "911, what's your emergency?"
- **Basis for ID:** Professional language, 911 protocol questions

[00:00:05 - 00:00:12] **Speaker (identified as: {client_name})**: "There's been a car accident at {location}."
- **Basis for ID:** Provides personal information matching client, describes incident consistent with case facts at {incident_location}

[Continue full transcript with ALL speech and timestamps...]

---

## Visual Timeline (Video Only)

[00:00:00] Scene opens - {description}
- **Observations:** Weather, lighting, road conditions, traffic
- **Visible:** {what's in frame}

[00:00:15] ⚠️ **KEY EVENT: {Critical moment}**
- **What happened:** {detailed description}
- **Frame extracted:** `/Reports/frames/{video}_00-00-15.jpg`
- **Legal significance:** {why this matters}

[Continue timeline for entire video...]

---

## Legal Analysis

### Consistency with Case Facts

✅ **CONSISTENT:**
- Client stated "{quote}" → Evidence shows: {what evidence confirms}
- Case summary says "{fact}" → Evidence confirms: {corroboration}

⚠️ **INCONSISTENCIES:**
- Client stated "{quote}" BUT evidence shows: {contradiction}
- OR: None identified

### Key Evidence Observations

**1. {Evidence Item}** (timestamp: HH:MM:SS)
- **Description:** {what was observed}
- **Legal significance:** {supports liability / causation / damages}
- **Citation:** per {Evidence Type} at HH:MM:SS (frame: {path if video})

**2. {Evidence Item}** (timestamp: HH:MM:SS)
- **Description:** {what was observed}
- **Legal significance:** {how this helps case}
- **Citation:** per {Evidence Type} at HH:MM:SS

[Continue for all key observations...]

### Red Flags / Weaknesses

⚠️ **Potential Issues:**
- {weakness_1} - {why this could be problematic}
- {weakness_2} - {concern}

**Mitigation:**
- {how to address weakness_1}
- {how to address weakness_2}

---

## Emotional State / Sentiment (if applicable for audio)

**Caller emotion:** {distressed / calm / angry / frightened}
**Voice characteristics:** {shakiness / urgency / confusion}
**Consistency:** {is emotional state consistent with traumatic event?}
**Legal relevance:** {supports genuineness of injuries / credibility}

---

## Recommendations

**Attorney Action Items:**
1. ✅ {Action based on strong evidence found}
2. ✅ {Action based on helpful evidence}
3. ⚠️ {Action to address identified weakness}

**Additional Investigation:**
- {Suggested follow-up investigation}
- {Additional evidence to obtain}
- {Witnesses to interview}

---

## Citations for Pleadings

**For Complaint/Demand:**
> "Per {Evidence Type} at timestamp HH:MM:SS (frame: {path if applicable}), {factual statement with legal significance}."

**For Causation:**
> "Per {Evidence Type} at HH:MM:SS, {evidence of injury causation}."

**For Liability:**
> "Per {Evidence Type} at HH:MM:SS, {evidence of fault}."

---

**Analysis Complete**
```

**Save report to:**
- `/Reports/multimedia_analysis_{evidence_name}_{client_lastname}.md`

**Save frames to:**
- `/Reports/frames/{video_name}_{HH-MM-SS}.jpg`

---

## Citation Requirements

**Every factual claim must have a precise citation:**
- Audio: "per 911 Call at 00:02:30, caller states..."
- Video: "per Body Camera Video at 00:15:30 (frame: /Reports/frames/bodycam_00-15-30.jpg), officer observes..."
- Always include timestamp in [HH:MM:SS] format
- For video, include frame path if extracted

---

## Speaker Identification Best Practices

**Don't just label "Speaker A, Speaker B"**

**Make informed inferences:**
- "Speaker identified as {client_name} based on:
  - Provides personal information matching client (name, address)
  - Describes incident consistent with case summary
  - Uses first-person perspective consistent with client role"

- "Speaker identified as Police Officer based on:
  - Professional language and terminology
  - Radio communication patterns
  - Official capacity statements"

- "Speaker identified as Witness based on:
  - Third-person perspective
  - Location at scene
  - Knowledge of events"

**Always note the basis for identification**

---

## Example Usage

**User gives you task:**
> "Analyze the body camera video from Officer Kelly for the Alma Cristobal case. File: `/projects/Alma-Cristobal-MVA-2-15-2024/Investigation/2024-02-15 - Body Camera Officer Kelly (Redacted).mp4`"

**Your workflow:**

1. **Load context:**
   - Read `/projects/Alma-Cristobal-MVA-2-15-2024/case_information/overview.json`
   - Extract: client_name = "Alma Socorro Cristobal Avendaño", incident_summary = "Sideswipe collision with commercial truck on I-65"
   - Read accident report from Investigation folder
   - Extract: incident_location = "I-65 northbound, Louisville, KY", incident_date = "2024-02-15"

2. **Analyze video with Gemini:**
   - Upload video to Gemini File API
   - Provide full case context in prompt
   - Request transcript, visual timeline, speaker ID, legal analysis
   - Get comprehensive response

3. **Extract frames:**
   - Identify key moments from analysis
   - Use ffmpeg to extract frames at critical timestamps
   - Save to `/Reports/frames/`

4. **Write attorney-ready report:**
   - Format analysis into structured report
   - Add citations with timestamps and frame references
   - Include legal observations and recommendations
   - Save to `/Reports/multimedia_analysis_bodycam_kelly_Cristobal.md`

5. **Deliver:**
   - Summarize key findings
   - Highlight supportive evidence and concerns
   - Provide path to full report

---

**Remember: Context + Analysis, not just transcription. Use case knowledge to identify speakers, spot contradictions, and provide legal insights.**
