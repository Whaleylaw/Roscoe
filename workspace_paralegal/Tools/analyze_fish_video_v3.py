import google.generativeai as genai
import os
import time
from datetime import datetime

# Configure API
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Video path
video_path = "/projects/Alma-Cristobal-MVA-2-15-2024/Investigation/2024-02-15 - Alma Cristobal - Investigation - LMPD - Body Camera Officer Fish (Redacted).mp4"
output_path = "/projects/Alma-Cristobal-MVA-2-15-2024/reports/Officer_Fish_Body_Camera_Analysis.md"

print(f"Uploading {video_path}...")
try:
    uploaded_file = genai.upload_file(video_path)
except Exception as e:
    print(f"Error uploading file: {e}")
    exit(1)

# Wait for processing
print(f"Waiting for processing...")
while uploaded_file.state.name == "PROCESSING":
    time.sleep(2)
    uploaded_file = genai.get_file(uploaded_file.name)

if uploaded_file.state.name == "FAILED":
    print("Video processing failed.")
    exit(1)

print(f"Processing Officer Fish video...")

# Analyze with full case context
model = genai.GenerativeModel("gemini-2.0-flash-exp")

prompt = '''Analyze this police body camera video from Officer Fish as legal evidence in a personal injury case.

CASE CONTEXT:
- Client: Alma Socorro Cristobal Avendaño (Plaintiff)
- Incident: Sideswipe collision, I-65 NB, Louisville, KY, Feb 15 2024, 19:45
- Client's Vehicle: 2014 Black Nissan Sentra
- Defendant: Roy Hamilton, driving 2022 Freightliner commercial truck for Crete Carrier
- Client's Version: Hamilton merged into her lane, forced her into guardrail
- Defendant's Version (deposition): No collision occurred while driving, damage happened later while parked
- Client's Injuries: Fractured left clavicle, chest pain, shoulder pain, EMS transport

CRITICAL FINDING FROM OFFICER KELLY'S VIDEO:
- Hamilton admitted at scene (08:30): "Yeah I think I hit her" - contradicts his deposition testimony
- Plaintiff admitted no driver's license
- Plaintiff complained of seatbelt pain, requested ambulance
- No visible truck damage observed
- Officer Kelly noted plaintiff appeared distracted

ANALYSIS REQUIRED:

1. **Full Transcript with Timestamps**
   - Transcribe all speech with [HH:MM:SS] timestamps
   - Identify speakers using case context (Alma Cristobal, Roy Hamilton, Officer Fish, other officers, EMS, witnesses)
   - Note basis for speaker identification
   - Use exact quotes

2. **Visual Timeline**
   - Describe what's happening with timestamps
   - Note vehicles visible (black Nissan Sentra, Freightliner truck)
   - Note damage visible to vehicles (any angles not captured by Officer Kelly?)
   - Note guardrail damage if visible
   - Note Cristobal's condition (visible injury, distress)
   - Note scene conditions (weather, lighting, road)
   - Mark key events: [HH:MM:SS] **KEY EVENT**: Description
   - What does Officer Fish do/observe/document?

3. **New Evidence vs. Officer Kelly's Video**
   - What NEW information does this provide?
   - What CORROBORATES Officer Kelly's findings?
   - What CONTRADICTS Officer Kelly's findings?
   - Does Officer Fish capture different interactions or angles?

4. **Legal Observations**
   - Evidence supporting/contradicting Cristobal's version
   - Evidence supporting/contradicting Hamilton's "no collision" claim
   - Evidence of collision occurrence and dynamics
   - Evidence of fault (who merged into whom)
   - Evidence of injury causation (contemporaneous complaints)
   - Credibility evidence for both parties
   - Red flags or weaknesses
   - Does Officer Fish interview either driver? What do they say?

5. **Key Frames for Extraction**
   - Identify critical timestamps showing:
     * Vehicle damage (any angles Officer Kelly didn't capture)
     * Guardrail damage
     * Scene overview
     * Cristobal showing injury/distress
     * Any unique observations not in Officer Kelly's video

Be thorough, objective, cite timestamps, compare to Officer Kelly's findings, identify what's new/different.'''

try:
    response = model.generate_content([uploaded_file, prompt])
    
    # Save analysis
    with open(output_path, "w") as f:
        f.write("# Officer Fish Body Camera Analysis\n\n")
        f.write(f"**Case:** Alma Socorro Cristobal Avendaño v. Crete Carrier Corporation and Roy Hamilton\n")
        f.write(f"**Evidence Type:** Police Body Camera Video - Officer Fish (Redacted)\n")
        f.write(f"**Date Analyzed:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Analyst:** Roscoe (Multimedia Evidence Analysis - Gemini 3 Pro)\n\n")
        f.write("---\n\n")
        f.write(response.text)

    print(f"Analysis saved to {output_path}")

except Exception as e:
    print(f"Error generating content: {e}")

# Clean up
try:
    genai.delete_file(uploaded_file.name)
    print("Cleaned up uploaded file.")
except Exception as e:
    print(f"Error deleting file: {e}")
