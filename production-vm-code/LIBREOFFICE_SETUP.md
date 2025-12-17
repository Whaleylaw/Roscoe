# LibreOffice Setup for Document Generation

This guide covers installing LibreOffice for high-fidelity PDF conversion from Word documents.

## Why LibreOffice?

The document generation tools use LibreOffice in headless mode to:
- Convert `.docx` files to PDF with maximum layout fidelity
- Convert legacy `.doc` files to `.docx` format
- Preserve fonts, tables, headers/footers, and complex formatting

## Installation

### macOS (Local Development)

**Option 1: Homebrew (Recommended)**
```bash
brew install --cask libreoffice
```

**Option 2: Direct Download**
1. Download from https://www.libreoffice.org/download/download/
2. Install the `.dmg` package
3. Move to `/Applications/`

**Verify Installation:**
```bash
/Applications/LibreOffice.app/Contents/MacOS/soffice --version
```

### Ubuntu/Debian (Production - GCE)

**Headless Mode (Recommended for servers):**
```bash
sudo apt update
sudo apt install -y libreoffice-writer-nogui libreoffice-calc-nogui
```

**Full Installation (if headless doesn't work):**
```bash
sudo apt install -y libreoffice
```

**Install Fonts (Important for consistent rendering):**
```bash
# Microsoft core fonts
sudo apt install -y ttf-mscorefonts-installer

# Additional fonts
sudo apt install -y fonts-liberation fonts-freefont-ttf
```

**Verify Installation:**
```bash
soffice --version
# or
libreoffice --version
```

## Verification

Run this Python script to verify the setup:

```python
from roscoe.agents.paralegal.word_template_pipeline import check_dependencies

deps = check_dependencies()
print(f"docxtpl: {deps['docxtpl_available']}")
print(f"python-docx: {deps['python_docx_available']}")
print(f"LibreOffice: {deps['libreoffice_available']}")
if deps['libreoffice_path']:
    print(f"LibreOffice path: {deps['libreoffice_path']}")
```

Or use the agent tool:
```
check_document_tools_status()
```

## Troubleshooting

### "LibreOffice not found"

The pipeline checks these paths in order:

**macOS:**
- `/Applications/LibreOffice.app/Contents/MacOS/soffice`
- `/opt/homebrew/bin/soffice`
- `/usr/local/bin/soffice`

**Linux:**
- `/usr/bin/soffice`
- `/usr/bin/libreoffice`
- `/usr/lib/libreoffice/program/soffice`
- `/snap/bin/libreoffice`

If LibreOffice is installed elsewhere, add it to your PATH:
```bash
export PATH="/path/to/libreoffice/bin:$PATH"
```

### Conversion Hangs

LibreOffice can hang if another instance is running. The pipeline uses isolated user profiles to avoid this, but if issues persist:

1. Kill any running LibreOffice processes:
   ```bash
   pkill -f soffice
   ```

2. Remove any stale lock files:
   ```bash
   rm -rf ~/.config/libreoffice/4/.~lock.*
   ```

### Fonts Missing in PDF

If the PDF looks different from the Word document:

1. Install Microsoft fonts on Linux:
   ```bash
   sudo apt install ttf-mscorefonts-installer
   ```

2. Regenerate font cache:
   ```bash
   fc-cache -fv
   ```

3. Ensure the fonts used in the template are installed on the server

### Conversion Times Out

Increase the timeout parameter when calling conversion functions:
```python
convert_docx_to_pdf(input_path, timeout=300)  # 5 minutes
```

## Docker Deployment

For containerized deployments, add to your Dockerfile:

```dockerfile
# Install LibreOffice
RUN apt-get update && apt-get install -y \
    libreoffice-writer-nogui \
    libreoffice-calc-nogui \
    fonts-liberation \
    fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

# Optional: Microsoft fonts (requires accepting EULA)
RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections \
    && apt-get update \
    && apt-get install -y ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/*
```

## Performance Notes

- First conversion may be slower as LibreOffice initializes
- Subsequent conversions are typically faster
- Headless mode (`libreoffice-*-nogui`) has lower memory footprint
- Each conversion uses an isolated user profile to prevent conflicts

## Available Agent Tools

Once set up, these tools are available to the agent:

| Tool | Description |
|------|-------------|
| `fill_word_template()` | Fill a .docx template with data and optionally export to PDF |
| `export_pdf_from_docx()` | Convert a .docx file to high-fidelity PDF |
| `convert_doc_to_docx()` | Convert legacy .doc files to .docx format |
| `list_template_variables()` | List all placeholders in a template |
| `check_document_tools_status()` | Verify all dependencies are available |
