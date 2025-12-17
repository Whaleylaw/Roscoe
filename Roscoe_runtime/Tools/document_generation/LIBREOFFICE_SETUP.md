# LibreOffice Setup for Word Template Pipeline

This document covers how to install LibreOffice for converting `.docx` files to PDF and `.doc` files to `.docx`.

## Why LibreOffice?

LibreOffice provides the highest-fidelity conversion from Word documents to PDF:
- Preserves all formatting, fonts, headers/footers, and styles
- Matches the layout you'd get opening the document in Microsoft Word
- Cross-platform (macOS, Linux, Windows)
- Free and open source

## Installation

### macOS (Local Development)

**Option 1: Homebrew (Recommended)**
```bash
brew install --cask libreoffice
```

After installation, `soffice` should be available at:
```
/Applications/LibreOffice.app/Contents/MacOS/soffice
```

The word_template_pipeline.py module will find it automatically.

**Option 2: Direct Download**
1. Download from https://www.libreoffice.org/download/download/
2. Drag to Applications folder
3. The module will find it automatically in the default location

### Ubuntu/Debian (Production VM)

**Standard Installation**
```bash
sudo apt-get update
sudo apt-get install -y libreoffice libreoffice-writer
```

**Headless Only (Smaller footprint for servers)**
```bash
sudo apt-get update
sudo apt-get install -y libreoffice-writer-nogui
```

**With Common Fonts (Recommended)**
```bash
sudo apt-get update
sudo apt-get install -y libreoffice fonts-dejavu fonts-liberation fonts-freefont-ttf
```

### Google Compute Engine (GCE) - Ubuntu VM

```bash
# Update package list
sudo apt-get update

# Install LibreOffice headless with fonts
sudo apt-get install -y \
    libreoffice \
    fonts-dejavu \
    fonts-liberation \
    fonts-freefont-ttf

# Verify installation
soffice --version
```

## Font Considerations

If your Word templates use specific fonts, you may need to install them:

**For Microsoft fonts (Times New Roman, Arial, etc.) on Ubuntu:**
```bash
sudo apt-get install -y ttf-mscorefonts-installer
```

**For custom firm fonts:**
1. Copy `.ttf` or `.otf` files to `/usr/local/share/fonts/`
2. Run `sudo fc-cache -fv` to update font cache

## Verification

Test that LibreOffice is working:

```bash
# Check installation
soffice --version

# Test conversion (creates test.pdf)
echo "Test document" > /tmp/test.txt
soffice --headless --convert-to pdf --outdir /tmp /tmp/test.txt
ls -la /tmp/test.pdf
```

## Python Module Verification

From Python, verify the module can find LibreOffice:

```python
from word_template_pipeline import check_dependencies

deps = check_dependencies()
print(deps)
# Should show: {'docxtpl': True, 'python-docx': True, 'libreoffice': True}
```

## Troubleshooting

### "LibreOffice not found" Error

1. Verify LibreOffice is installed:
   ```bash
   which soffice
   # or on macOS
   ls -la /Applications/LibreOffice.app/Contents/MacOS/soffice
   ```

2. If installed but not found, add to PATH:
   ```bash
   # macOS
   export PATH="/Applications/LibreOffice.app/Contents/MacOS:$PATH"
   
   # Linux
   export PATH="/usr/bin:$PATH"
   ```

### Conversion Hangs or Times Out

LibreOffice sometimes has issues in headless mode. Try:

```bash
# Kill any stuck soffice processes
pkill -9 soffice

# Remove LibreOffice profile lock
rm -rf ~/.config/libreoffice/4/.~lock.*
```

### Fonts Missing in PDF Output

If fonts appear as boxes or wrong substitutes:

1. Install required fonts (see Font Considerations above)
2. Regenerate font cache:
   ```bash
   sudo fc-cache -fv
   ```
3. Restart LibreOffice processes

### Permission Issues on GCE

If running as a service account:

```bash
# Ensure the user has a home directory for LibreOffice profile
sudo mkdir -p /home/serviceaccount
sudo chown serviceaccount:serviceaccount /home/serviceaccount
export HOME=/home/serviceaccount
```

## Docker Deployment

If deploying in Docker, add to your Dockerfile:

```dockerfile
FROM python:3.11-slim

# Install LibreOffice
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-dejavu \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app
```

## Usage Example

```python
from word_template_pipeline import fill_and_export_template

result = fill_and_export_template(
    template_path="forms/templates/Medical Record Request.docx",
    output_path="output/John_Smith_Medical_Request.docx",
    context={
        "client_name": "John Smith",
        "provider_name": "ABC Medical Center",
        "date_of_loss": "January 15, 2024",
        "today_date": "December 12, 2025"
    },
    export_pdf=True
)

print(f"DOCX: {result['docx_path']}")
print(f"PDF:  {result['pdf_path']}")
```
