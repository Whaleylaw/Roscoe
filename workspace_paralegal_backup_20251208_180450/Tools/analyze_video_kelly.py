import google.generativeai as genai
import os
import time

# Configure API
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# File path
file_path = "/Volumes/X10 Pro/Roscoe/workspace/projects/Alma-Cristobal-MVA-2-15-2024/Investigation/2024-02-15 - Alma Cristobal - Investigation - LMPD - Body Camera Officer Kelly (Redacted).mp4"

print(f"Uploading file: {file_path}")

# Upload file
try:
    video_file = genai.upload_file(file_path)
    print(f"Upload complete. File name: {video_file.name}")
except Exception as e:
    print(f"Error uploading file: {e}")
    exit(1)

# Wait for processing
print("Waiting for processing...")
while video_file.state.name == "PROCESSING":
    print(".", end="", flush=True)
    time.sleep(2)
    video_file = genai.get_file(video_file.name)

print(f"\nProcessing complete. State: {video_file.state.name}")

if video_file.state.name == "FAILED":
    print("Video processing failed.")
    exit(1)

# Analyze with Gemini 3 Pro
print("Analyzing with Gemini 3 Pro...")
model = genai.GenerativeModel("gemini-3-pro-preview")

prompt = """
Analyze this body camera video evidence for a personal injury case. 
This is critical legal evidence. Be precise, objective, and thorough.

Please provide a detailed report covering the following sections:

1. **Audio Transcript**: Provide a verbatim transcript of all audible dialogue, including timestamps and speaker identification (e.g., Officer Kelly, Driver, Dispatch, Witness).
2. **Visual Timeline**: Create a chronological log of visual events. What is seen at specific timestamps?
3. **Key Accident Facts**:
   - **Location**: Identify street names, landmarks, or GPS coordinates visible.
   - **Vehicles**: Describe all involved vehicles (Make, Model, Color, License Plates if visible).
   - **Incident Details**: What appears to have happened based on the scene and statements?
   - **Injuries**: Describe any visible injuries or complaints of pain mentioned.
   - **Parties**: Identify who is present (Police, EMS, Drivers, Passengers).
4. **Visual Evidence Assessment**:
   - **Vehicle Damage**: Describe the specific damage to vehicles and its location.
   - **Road/Environmental Conditions**: Weather, lighting, road surface, traffic conditions.
   - **Debris/Skid Marks**: Note any physical evidence on the roadway.
5. **Contradictions/Inconsistencies**: Note any discrepancies between statements and visual evidence, or between different speakers.

Format the output clearly with Markdown headings.
"""

try:
    response = model.generate_content([video_file, prompt])
    print("\n--- ANALYSIS RESULT ---\n")
    print(response.text)
except Exception as e:
    print(f"Error generating content: {e}")

# Cleanup
try:
    genai.delete_file(video_file.name)
    print("\nFile deleted from Gemini storage.")
except Exception as e:
    print(f"Error deleting file: {e}")
