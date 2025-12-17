# Document Generation Tools

This directory contains tools for generating professional legal documents.

## Tools Overview

### 1. demand_generator.py

Converts markdown demand letters to professional DOCX/PDF documents.

**Usage:**
```bash
# Command line
python demand_generator.py input.md output.docx --pdf

# Programmatic
from demand_generator import generate_demand_letter
result = generate_demand_letter(markdown_content, output_path, convert_to_pdf=True)
```

**Features:**
- Parses markdown (headers, tables, lists, bold/italic)
- Creates properly formatted DOCX with Times New Roman font
- Converts to PDF via LibreOffice

---

### 2. exhibit_compiler.py

Compiles a demand letter PDF with exhibits into a single combined PDF.

**Usage:**
```bash
python exhibit_compiler.py manifest.yaml [--no-covers] [--output path]
```

**Manifest format (YAML):**
```yaml
demand_letter: "/path/to/demand.pdf"
output: "/path/to/combined.pdf"
exhibits:
  - letter: A
    description: "Provider Name - Records"
    path: "/path/to/exhibit_a.pdf"
```

**Features:**
- Generates exhibit cover pages (EXHIBIT A, EXHIBIT B, etc.)
- Combines all PDFs in order
- Supports YAML or JSON manifests

---

### 3. letterhead_generator.py

Generates documents on firm letterhead from markdown content.

**Usage:**
```bash
python letterhead_generator.py input.md output.docx [--no-pdf] [--template path]
```

**Features:**
- Uses pandoc with `--reference-doc` for style inheritance
- Copies header/footer/logo from template
- Converts to PDF via LibreOffice

---

## Dependencies

```bash
pip install python-docx pypdf reportlab pyyaml
brew install --cask libreoffice  # macOS
brew install pandoc              # macOS
```

---

## Workflow: Complete Demand Package

1. **Draft demand letter** in markdown format
2. **Generate PDF** using `demand_generator.py`
3. **Create exhibit manifest** listing all supporting documents
4. **Compile final package** using `exhibit_compiler.py`

```bash
# Step 1: Generate demand letter PDF
python demand_generator.py "James Sadler - Demand.md" "James Sadler - Demand.docx" --pdf

# Step 2: Compile with exhibits
python exhibit_compiler.py exhibit_manifest.yaml
```

Output: Single PDF with demand letter + exhibit cover pages + exhibits

---

## File Locations

| Tool | Path |
|------|------|
| demand_generator.py | `workspace_paralegal/Tools/document_generation/demand_generator.py` |
| exhibit_compiler.py | `workspace_paralegal/Tools/document_generation/exhibit_compiler.py` |
| letterhead_generator.py | `workspace_paralegal/Tools/document_generation/letterhead_generator.py` |
| Letterhead Template | `workspace_paralegal/forms/2021 Whaley Letterhead (1).docx` |
| Demand Template | `workspace_paralegal/forms/demand_letter_TEMPLATE.md` |

