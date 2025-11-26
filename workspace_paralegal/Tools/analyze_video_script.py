import google.generativeai as genai
import os
import time

# Configure API
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# File path
file_path = "/projects/Alma-Cristobal-MVA-2-15-2024/Investigation/2024-02-15 - Alma Cristobal - Investigation - LMPD - Body Camera Officer Kelly (Redacted).mp4"

print(f"Uploading {file_path}...")
try:
    video_file = genai.upload_file(file_path)
    
    # Wait for processing
    print("Waiting for processing...")
    while video_file.state.name == "PROCESSING":
        time.sleep(2)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        print(f"Video processing failed: {video_file.state.name}")
    else:
        print("Processing complete. Generating analysis...")
        
        # Analyze with Gemini 1.5 Pro
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        prompt = """
        Analyze this body camera video file from a motor vehicle accident investigation involving Alma Cristobal on Feb 15, 2024.
        
        I need a comprehensive legal evidence report with the following EXACT sections:

        1. **Evidence Overview**:
           - Duration of video
           - Date/Time (if visible on overlay or deducible)
           - General setting/scene description

        2. **Full Audio Transcript with Timestamps**:
           - Provide a verbatim transcript.
           - Format: `[MM:SS] Speaker: Text`
           - Identify speakers as best as possible (e.g., Officer Kelly, Driver, Witness, Dispatch).

        3. **Visual Timeline**:
           - Describe what is visually happening at key timestamps.
           - Format: `[MM:SS] Visual description`
           - Focus on officer actions, vehicle views, and scene details.

        4. **Accident Facts Summary**:
           - Location details (street names, landmarks)
           - Vehicles involved (Make, Model, Color, License Plates if visible)
           - Narrative of the incident (what happened based on statements)
           - Injuries mentioned or observed
           - Medical response details

        5. **Vehicle Descriptions and Damage Assessment**:
           - Describe the specific damage to the vehicle(s).
           - Note location of damage (front, rear, driver side, etc.).
           - Note airbag deployment or other interior conditions if visible.

        6. **Notable Observations**:
           - Road conditions (wet/dry, lighting)
           - Traffic patterns
           - Weather
           - Any specific evidence pointed out (skid marks, debris).

        7. **Inconsistencies or Concerns**:
           - Any contradictions between statements and visual evidence.
           - Any missing information or unclear details.

        Be objective, thorough, and precise. This is for a legal case file.
        """
        
        response = model.generate_content([video_file, prompt])
        print(response.text)
        
        # Cleanup
        genai.delete_file(video_file.name)

except Exception as e:
    print(f"An error occurred: {e}")
