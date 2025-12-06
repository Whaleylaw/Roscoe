# Claude Skills Dependencies

This document lists all dependencies required by the integrated Claude Skills for the Roscoe Paralegal Agent.

## Quick Install (Production VM)

```bash
# SSH into VM
gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a

# Python packages
pip install pypdf pdfplumber reportlab openpyxl pillow pdf2image pytesseract \
  defusedxml pyyaml pandas "markitdown[pptx]" pypdfium2 numpy

# System packages
sudo apt-get update
sudo apt-get install -y pandoc libreoffice poppler-utils tesseract-ocr qpdf

# Node.js packages (for document creation)
npm install -g docx pptxgenjs playwright sharp
npx playwright install chromium

# Optional: gtimeout for macOS (formula recalculation timeout)
# brew install coreutils  # provides gtimeout
```

---

## Python Packages

### Core Installation

```bash
pip install pypdf pdfplumber reportlab openpyxl pillow pdf2image pytesseract \
  defusedxml pyyaml pandas "markitdown[pptx]" pypdfium2 numpy
```

### Package Details

| Package | Version | Purpose | Used By |
|---------|---------|---------|---------|
| `pypdf` | >=3.0 | PDF read/write, merge, split, forms | pdf |
| `pdfplumber` | >=0.10 | PDF text/table extraction | pdf |
| `reportlab` | >=4.0 | PDF creation from scratch | pdf, canvas-design |
| `pillow` | >=10.0 | Image processing, validation images | pdf, pptx, canvas-design |
| `pdf2image` | >=1.16 | Convert PDF pages to images | pdf |
| `pytesseract` | >=0.3.10 | OCR for scanned PDFs | pdf |
| `pypdfium2` | >=4.0 | Fast PDF rendering (PyMuPDF alt) | pdf (optional) |
| `numpy` | >=1.24 | Array operations for image processing | pdf |
| `openpyxl` | >=3.1 | Excel creation/editing with formulas | xlsx |
| `pandas` | >=2.0 | Data analysis, Excel I/O | xlsx |
| `defusedxml` | >=0.7 | Secure XML parsing | docx, pptx |
| `markitdown` | >=0.1 | PPTX text extraction | pptx |
| `pyyaml` | >=6.0 | YAML parsing for skill frontmatter | core |

### By Skill

| Skill | Required Packages |
|-------|------------------|
| **pdf** | `pypdf`, `pdfplumber`, `reportlab`, `pillow`, `pdf2image`, `pytesseract` |
| **docx** | `defusedxml` |
| **xlsx** | `pandas`, `openpyxl` |
| **pptx** | `defusedxml`, `markitdown[pptx]`, `pillow` |
| **canvas-design** | `pillow`, `reportlab` |
| **theme-factory** | (none - uses other skill dependencies) |

---

## Node.js Packages

### Core Installation

```bash
npm install -g docx pptxgenjs playwright sharp
npx playwright install chromium
```

### Package Details

| Package | Purpose | Used By |
|---------|---------|---------|
| `docx` | Create new Word documents (docx-js) | docx |
| `pptxgenjs` | Create PowerPoint presentations | pptx |
| `playwright` | HTML rendering for html2pptx | pptx |
| `sharp` | SVG rasterization, image processing | pptx |
| `react`, `react-dom` | Required for react-icons | pptx (optional) |
| `react-icons` | Icons for presentations | pptx (optional) |

### By Skill

| Skill | Required Packages |
|-------|------------------|
| **docx** | `docx` (for creating new documents from scratch) |
| **pptx** | `pptxgenjs`, `playwright`, `sharp` |

---

## System Packages

### Ubuntu/Debian Installation

```bash
sudo apt-get update
sudo apt-get install -y \
  pandoc \
  libreoffice \
  poppler-utils \
  tesseract-ocr \
  qpdf
```

### macOS Installation

```bash
brew install pandoc libreoffice poppler tesseract qpdf
# Optional: gtimeout for recalc.py timeout support
brew install coreutils
```

### Package Details

| Package | Provides | Purpose | Used By |
|---------|----------|---------|---------|
| **pandoc** | `pandoc` | Document conversion, DOCX→Markdown | docx, pptx |
| **libreoffice** | `soffice` | DOCX/PPTX→PDF, Excel formula recalc | docx, pptx, xlsx |
| **poppler-utils** | `pdftotext`, `pdftoppm`, `pdfimages` | PDF text/image extraction | pdf, docx, pptx |
| **tesseract-ocr** | `tesseract` | OCR engine for scanned documents | pdf |
| **qpdf** | `qpdf` | Advanced PDF manipulation, repair | pdf |

### By Skill

| Skill | Required System Packages |
|-------|-------------------------|
| **pdf** | `poppler-utils`, `tesseract-ocr`, `qpdf` |
| **docx** | `pandoc`, `libreoffice`, `poppler-utils` |
| **xlsx** | `libreoffice` |
| **pptx** | `pandoc`, `libreoffice`, `poppler-utils` |
| **canvas-design** | (none) |
| **theme-factory** | (none) |

---

## Verification

### Python Packages

```python
#!/usr/bin/env python3
"""Verify all Python dependencies are installed."""

packages = [
    ("pypdf", "pypdf"),
    ("pdfplumber", "pdfplumber"),
    ("reportlab", "reportlab"),
    ("PIL", "pillow"),
    ("pdf2image", "pdf2image"),
    ("pytesseract", "pytesseract"),
    ("openpyxl", "openpyxl"),
    ("pandas", "pandas"),
    ("defusedxml", "defusedxml"),
    ("yaml", "pyyaml"),
    ("markitdown", "markitdown"),
]

missing = []
for module, package in packages:
    try:
        __import__(module)
        print(f"✓ {package}")
    except ImportError:
        print(f"✗ {package} - MISSING")
        missing.append(package)

if missing:
    print(f"\nInstall missing: pip install {' '.join(missing)}")
else:
    print("\n✓ All Python packages installed!")
```

### System Tools

```bash
#!/bin/bash
echo "Checking system dependencies..."

check_cmd() {
    if command -v "$1" &> /dev/null; then
        echo "✓ $1"
    else
        echo "✗ $1 - MISSING"
    fi
}

check_cmd pandoc
check_cmd soffice      # LibreOffice
check_cmd pdftotext    # poppler-utils
check_cmd pdftoppm     # poppler-utils
check_cmd pdfimages    # poppler-utils
check_cmd tesseract
check_cmd qpdf
```

### Node.js Packages

```bash
#!/bin/bash
echo "Checking Node.js dependencies..."

for pkg in docx pptxgenjs playwright sharp; do
    if npm list -g "$pkg" &> /dev/null; then
        echo "✓ $pkg"
    else
        echo "✗ $pkg - MISSING"
    fi
done
```

---

## Docker Container Notes

If running in Docker, the base image should include:

```dockerfile
# System dependencies
RUN apt-get update && apt-get install -y \
    pandoc \
    libreoffice \
    poppler-utils \
    tesseract-ocr \
    qpdf \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
RUN pip install pypdf pdfplumber reportlab openpyxl pillow pdf2image \
    pytesseract defusedxml pyyaml pandas "markitdown[pptx]"

# Node.js dependencies (if needed)
RUN npm install -g docx pptxgenjs playwright sharp \
    && npx playwright install chromium --with-deps
```

---

## Common Issues

### LibreOffice Not Starting (Headless Mode)

```bash
# Ensure using headless mode
soffice --headless --convert-to pdf document.docx
```

### Tesseract Language Data

```bash
# Install additional language data if needed
sudo apt-get install tesseract-ocr-eng tesseract-ocr-spa
```

### Poppler Version Issues

```bash
# Check version (need >= 0.62 for some features)
pdftotext -v
```

### Playwright Browser Missing

```bash
# Install Chromium browser
npx playwright install chromium
```

---

## Skill-Specific Notes

### PDF Skill

- **Form filling**: Uses `pypdf` for fillable forms, annotations for non-fillable
- **OCR**: Requires `tesseract-ocr` system package + `pytesseract` Python binding
- **Fast rendering**: `pypdfium2` is optional but recommended for large PDFs

### DOCX Skill

- **New documents**: Use `docx` (Node.js) via docx-js workflow
- **Edit existing**: Use `document.py` library (Python) with OOXML manipulation
- **Text extraction**: Uses `pandoc` for markdown conversion

### XLSX Skill

- **Formula recalculation**: Requires LibreOffice (`recalc.py`)
- **Data analysis**: Use `pandas` for reading/analyzing data
- **Formula work**: Use `openpyxl` for creating formulas and formatting

### PPTX Skill

- **New presentations**: Use `html2pptx` workflow with `pptxgenjs` + `playwright`
- **Edit existing**: Use OOXML manipulation (unpack → edit XML → pack)
- **Thumbnails**: Requires `libreoffice` + `poppler-utils` for PDF conversion

### Canvas Design Skill

- **PDF output**: Uses `reportlab` for PDF creation
- **PNG output**: Uses `pillow` for image manipulation
- **Fonts**: Custom fonts in `./canvas-fonts/` directory
