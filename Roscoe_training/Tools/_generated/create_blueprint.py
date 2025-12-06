import os
import sys
from runloop_api_client import Runloop

# Key from VM docker-compose logs inspection
API_KEY = "ak_31cdDowS4JBQYN5AOFvYI"

try:
    client = Runloop(bearer_token=API_KEY)
    
    print("Creating blueprint 'roscoe-paralegal-env-v1'...")
    print("This may take a few minutes...")
    
    blueprint = client.blueprints.create_and_await_build_complete(
        name="roscoe-paralegal-env-v1",
        system_setup_commands=[
            "sudo apt-get update",
            "sudo apt-get install -y tesseract-ocr ffmpeg libsm6 libxext6",
            "pip install tavily-python requests python-dotenv google-generativeai pdfplumber pytesseract pandas numpy scikit-learn beautifulsoup4 lxml openpyxl pillow opencv-python moviepy ffmpeg-python"
        ]
    )
    
    print(f"SUCCESS: Blueprint created with ID: {blueprint.id}")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

