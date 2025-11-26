import google.generativeai as genai
import os
import time

# Configure API
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Video path
video_path = "/projects/Alma-Cristobal-MVA-2-15-2024/Investigation/2024-02-15 - Alma Cristobal - Investigation - LMPD - Body Camera Officer Fish (Redacted).mp4"

print(f"Uploading {video_path}...")
try:
    uploaded_file = genai.upload_file(video_path)
except Exception as e:
    print(f"Error uploading file: {e}")
    exit(1)

# Wait for processing
print("Waiting for video processing...")
while uploaded_file.state.name == "PROCESSING":
    time.sleep(2)
    uploaded_file = genai.get_file(uploaded_file.name)

if uploaded_file.state.name == "FAILED":
    print("Video processing failed.")
    exit(1)

print(f"Video processed. Analyzing with Gemini 1.5 Pro...")

# Analyze with full case context
model = genai.GenerativeModel("gemini-1.5-pro")

prompt = f'''Analyze this police body camera video (Officer Fish) as legal evidence in a personal injury case.

CASE CONTEXT:
- Client: Alma Socorro Cristobal Avendaño (Plaintiff)
- Incident: Sideswipe collision, I-65 NB, Louisville, KY, Feb 15 2024, 19:45
- Client's Vehicle: 2014 Black Nissan Sentra
- Defendant: Roy Hamilton, driving 2022 Freightliner commercial truck for Crete Carrier
- Client's Version: Hamilton merged into her lane, forced her into guardrail
- Defendant's Version (deposition): No collision occurred while driving, damage happened later while parked
- Client's Injuries: Fractured left clavicle, chest pain, shoulder pain, EMS transport
- Officer on this body camera: Fish

CRITICAL FINDINGS FROM OFFICER KELLY'S VIDEO (already analyzed):
- Hamilton admitted at scene (08:30): "Yeah I think I hit her"
- Cristobal admitted: No driver's license
- Officer Kelly observed: Cristobal appeared distracted ("eating")
- Damage disparity: Severe Nissan damage, no visible truck damage

ANALYSIS REQUIRED:

1. **Full Transcript with Timestamps**
   - Transcribe all speech with [HH:MM:SS] timestamps
   - Identify speakers using case context (Alma Cristobal, Roy Hamilton, Officer Fish, EMS, etc.)
   - Note basis for speaker identification

2. **Visual Timeline**
   - Describe what's happening with timestamps
   - Note vehicles visible (black Nissan Sentra, Freightliner truck)
   - Note damage visible to vehicles
   - Note guardrail damage
   - Note Cristobal's condition (visible injury, distress)
   - Note scene conditions (weather, lighting, road)
   - Mark key events: [HH:MM:SS] **KEY EVENT**: Description

3. **Legal Observations**
   - Evidence supporting/contradicting Cristobal's version
   - Evidence supporting/contradicting Hamilton's "no collision" claim
   - Evidence of collision occurrence and dynamics
   - Evidence of fault (who merged into whom)
   - Evidence of injury causation (contemporaneous complaints)
   - Credibility evidence for both parties
   - Red flags or weaknesses

4. **Unique Contributions**
   - What does Officer Fish's video show that Officer Kelly's did NOT?
   - Different conversations, statements, viewing angles, timeline coverage?

5. **Key Frames for Extraction**
   - Identify critical timestamps showing:
     * Vehicle damage (different angles than Kelly's video)
     * Guardrail damage
     * Scene overview
     * Cristobal's condition
     * Any moment proving/disproving disputed facts

Be thorough, objective, cite timestamps, think like an attorney. Focus on what's UNIQUE in Fish's video compared to Kelly's already-analyzed footage.'''

try:
    response = model.generate_content([uploaded_file, prompt])
    
    # Save analysis
    output_path = "/projects/Alma-Cristobal-MVA-2-15-2024/reports/Officer_Fish_Body_Camera_Analysis.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        f.write("# Body Camera Analysis: Officer Fish\n\n")
        f.write(f"**Case:** Alma Socorro Cristobal Avendaño v. Crete Carrier Corporation and Roy Hamilton\n")
        f.write(f"**Evidence Type:** Police Body Camera Video - Officer Fish (Redacted)\n")
        f.write(f"**Date Analyzed:** 2025-11-25\n")
        f.write(f"**Analyst:** Roscoe (Multimedia Evidence Analysis - Gemini 1.5 Pro)\n\n")
        f.write("---\n\n")
        f.write(response.text)

    print(f"Analysis complete. Saved to {output_path}")

except Exception as e:
    print(f"Error generating content: {e}")

# Clean up
try:
    genai.delete_file(uploaded_file.name)
    print("Remote file deleted.")
except Exception as e:
    print(f"Error deleting file: {e}")
