# Multimedia Evidence Analysis Trigger

**FOR MAIN AGENT (Claude Sonnet 4.5)**

## When to Use This Skill

Use this skill when the user asks you to:
- Analyze audio evidence (911 calls, depositions, witness statements, police radio)
- Analyze video evidence (dashcam, body camera, surveillance, depositions)
- Transcribe audio or video with case context
- Review multimedia evidence from accident scenes
- Analyze any audio or video file for legal purposes
- Get speaker identification from audio/video
- Extract frames from video evidence
- Get visual timelines from video evidence

**Key triggers:**
- "analyze this video"
- "analyze this audio"
- "transcribe this 911 call"
- "review the dashcam footage"
- "analyze the body camera video"
- "what's in this audio file"
- "what's in this video file"
- "transcribe this deposition"

---

## Your Task

When the user asks you to analyze audio or video evidence, **delegate to the multimodal sub-agent** with the multimedia-evidence-analysis skill.

---

## How to Delegate

**Step 1: Identify the multimedia file path** from user's request

**Step 2: Spawn multimodal sub-agent** with the multimedia-evidence-analysis skill:

```python
spawn_sub_agent(
    agent="multimodal-agent",  # Gemini 3 Pro multimodal sub-agent
    skill="/workspace/Skills/multimedia-evidence-analysis/skill.md",
    task=f"""
    Analyze this audio/video evidence for the {case_name} case:

    **File:** {multimedia_file_path}

    Follow the multimedia-evidence-analysis skill instructions:
    1. Load case context FIRST (overview.json, accident report, complaint)
    2. Analyze the multimedia file with Gemini's native capabilities
    3. Provide attorney-ready analysis with:
       - Full transcript with timestamps
       - Speaker identification (using case context)
       - Visual timeline (for video)
       - Legal analysis (consistency with case facts)
       - Key evidence observations
       - Citations for pleadings
    4. Save report to /Reports/

    The skill provides complete step-by-step instructions.
    """
)
```

**Step 3: Wait for sub-agent to complete**

**Step 4: Report results to user:**
- Summarize key findings from the analysis
- Highlight important evidence found
- Note any concerns or red flags
- Provide path to the full report

---

## Example

**User:** "Analyze the body camera video from Officer Kelly for the Alma Cristobal case. It's at /projects/Alma-Cristobal-MVA-2-15-2024/Investigation/2024-02-15 - Body Camera Officer Kelly (Redacted).mp4"

**Your response:**

"I'll analyze that body camera video with full case context. Let me delegate this to the multimodal sub-agent with the multimedia-evidence-analysis skill."

```python
spawn_sub_agent(
    agent="multimodal-agent",
    skill="/workspace/Skills/multimedia-evidence-analysis/skill.md",
    task="""
    Analyze this body camera video for the Alma Cristobal case:

    **File:** /projects/Alma-Cristobal-MVA-2-15-2024/Investigation/2024-02-15 - Body Camera Officer Kelly (Redacted).mp4

    Follow the multimedia-evidence-analysis skill instructions:
    1. Load case context from overview.json and accident report
    2. Analyze video with Gemini (transcript, visual timeline, speaker ID)
    3. Compare evidence to case facts
    4. Provide attorney-ready analysis with citations
    5. Save to /Reports/
    """
)
```

Then after analysis completes: "The body camera video analysis is complete. Key findings: [summary]. Full report saved to /Reports/multimedia_analysis_bodycam_kelly_Cristobal.md"

---

## Important Notes

**DO NOT try to analyze multimedia yourself** - you (main agent) don't have multimodal capabilities. Always delegate to the multimodal-agent.

**DO provide the full skill path** when spawning the sub-agent: `/workspace/Skills/multimedia-evidence-analysis/skill.md`

**DO provide the file path** from the user's request in your task description

**The multimedia-evidence-analysis skill handles everything** - context loading, analysis, report writing. You just delegate and report results.

---

## Model Required

**Main Agent:** Claude Sonnet 4.5 (you)
- Your job: Recognize the request and delegate
- Multimodal agent does the actual analysis

---

**Remember: Your only job is to recognize multimedia analysis requests and delegate to the multimodal sub-agent with the proper skill file. The skill does the rest.**
