"""
PDF Processing Module for Medical/Legal Documents

Tiered OCR pipeline:
- Tier 1: PDFPlumber (fast, text-based PDFs)
- Tier 2: PyTesseract (scanned PDFs, OCR)
- Tier 3: Google Cloud Document AI (future - complex cases)
"""

from .pdfplumber_processor import extract_with_pdfplumber
from .ocr_processor import extract_with_ocr
from .quality_metrics import assess_quality, classify_pdf

__all__ = [
    'extract_with_pdfplumber',
    'extract_with_ocr',
    'assess_quality',
    'classify_pdf'
]
