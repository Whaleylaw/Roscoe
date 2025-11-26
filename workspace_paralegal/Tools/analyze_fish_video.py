import google.generativeai as genai
import os
import time

# Configure API
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# File path
file_path = "/projects/Alma-Cristobal-MVA-2-15-2024/Investigation/2024-02-15 - Alma Cristobal - Investigation - LMPD - Body Camera Officer Fish (Redacted).mp4"

# Upload file
print(f"Uploading {file_path}...")
uploaded_file = genai.upload_file(file_path)

# Wait for processing
print("Waiting for processing...")
while uploaded_file.state.name == "PROCESSING":
    time.sleep(2)
    uploaded_file = genai.get_file(uploaded_file.name)

if uploaded_file.state.name == "FAILED":
    print("File processing failed.")
    exit(1)

print("File processed successfully.")

# Model setup
model = genai.GenerativeModel("gemini-1.5-pro-002")

# Prompt
prompt = """
Analyze Officer Fish's body camera video from the Alma Cristobal MVA case.

**Case Context:**
Alma Cristobal (plaintiff) vs. Roy Hamilton/Crete Carrier. Sideswipe collision on I-65 NB, Louisville, KY on Feb 15, 2024 at 19:45. Cristobal claims Hamilton's truck merged into her lane forcing her into guardrail. Hamilton claims in deposition "no collision occurred."

**Comparison Context (Officer Kelly's Video Findings):**
- Hamilton admitted at scene: "Yeah I think I hit her" (contradicting deposition)
- Cristobal admitted: no driver's license
- Officer noted Cristobal appeared distracted ("eating, wasn't looking")
- Severe sedan damage, NO visible truck damage
- Cristobal in pain, requested ambulance, complained pain "from seatbelt"

**Your Task:**
1. **Full Transcript:** Provide a verbatim transcript with timestamps [HH:MM:SS] and speaker identification (Cristobal, Hamilton, Officer Fish, other officers, EMS).
2. **Visual Timeline:** Describe what is visible at key timestamps, focusing on vehicle positions, damage, and scene layout.
3. **Comparison Analysis:** Compare findings to Officer Kelly's video. What is NEW? What is CONFIRMED? Are there CONTRADICTIONS?
4. **Legal Analysis:**
    - **Fault Evidence:** Any statements or physical evidence regarding the merge/collision.
    - **Injury Evidence:** Cristobal's condition, complaints, EMS interaction.
    - **Credibility:** Consistency of statements by both parties.
5. **Critical Frames:** Identify timestamps for critical frame extraction (e.g., clear views of damage, specific interactions).

**Focus:**
- Listen carefully for any NEW statements from Hamilton or Cristobal.
- Look for different angles of vehicle damage (especially the truck).
- Note Officer Fish's unique observations or interactions.
- Establish a timeline of events from Fish's perspective.

Format the output as a structured report.
"""

# Generate content
print("Generating analysis...")
response = model.generate_content([uploaded_file, prompt])

print(response.text)

# Cleanup
genai.delete_file(uploaded_file.name)
