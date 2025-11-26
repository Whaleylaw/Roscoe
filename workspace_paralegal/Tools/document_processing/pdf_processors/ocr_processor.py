"""
PyTesseract OCR Processor (Tier 2)

Performs OCR on scanned/image-based PDFs using Tesseract.
Best for: Scanned medical records, older documents, image-based PDFs.

Requirements:
    - pytesseract: pip install pytesseract
    - pdf2image: pip install pdf2image
    - Tesseract binary: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)
"""

import sys
from pathlib import Path


def extract_with_ocr(pdf_path, language='eng', dpi=300):
    """
    Extract text from PDF using OCR (Optical Character Recognition).

    Args:
        pdf_path: Path to PDF file
        language: OCR language (default: 'eng' for English)
        dpi: Image resolution for OCR (default: 300, higher = better quality but slower)

    Returns:
        dict: {
            'success': bool,
            'text': str,
            'page_count': int,
            'method': 'ocr',
            'confidence': str,
            'error': str (if failed)
        }
    """
    # Check for required libraries
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError as e:
        missing_lib = 'pdf2image' if 'pdf2image' in str(e) else 'pytesseract'
        return {
            'success': False,
            'error': f'{missing_lib} not installed. Run: pip install {missing_lib}',
            'method': 'ocr',
            'help': 'Also ensure Tesseract is installed: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)'
        }

    try:
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            return {
                'success': False,
                'error': f'File not found: {pdf_path}',
                'method': 'ocr'
            }

        print(f"Converting PDF to images (DPI: {dpi})...", file=sys.stderr)

        # Convert PDF pages to images
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
        except Exception as e:
            return {
                'success': False,
                'error': f'PDF to image conversion failed: {str(e)}. Ensure poppler is installed.',
                'method': 'ocr',
                'help': 'Install poppler: brew install poppler (macOS) or apt-get install poppler-utils (Linux)'
            }

        num_pages = len(images)
        print(f"Processing {num_pages} pages with OCR...", file=sys.stderr)

        # Extract text from each page
        text_parts = []
        text_parts.append("=" * 80)
        text_parts.append(f"PDF: {pdf_file.name}")
        text_parts.append(f"Total Pages: {num_pages}")
        text_parts.append(f"Extraction Method: OCR (PyTesseract - Tier 2)")
        text_parts.append(f"OCR Language: {language}")
        text_parts.append(f"OCR DPI: {dpi}")
        text_parts.append("=" * 80)
        text_parts.append("")

        total_chars = 0

        for page_num, image in enumerate(images, start=1):
            try:
                # Perform OCR on the image
                page_text = pytesseract.image_to_string(image, lang=language)

                text_parts.append(f"\n{'='*80}")
                text_parts.append(f"PAGE {page_num} of {num_pages}")
                text_parts.append('='*80)
                text_parts.append(page_text if page_text.strip() else "[No text detected on this page]")

                total_chars += len(page_text)

                print(f"  ✓ Page {page_num}/{num_pages} OCR complete ({len(page_text)} chars)", file=sys.stderr)

            except Exception as e:
                error_msg = f"  ✗ OCR error on page {page_num}: {str(e)}"
                print(error_msg, file=sys.stderr)
                text_parts.append(f"\n[OCR ERROR ON PAGE {page_num}: {str(e)}]")

        full_text = "\n".join(text_parts)

        # Assess OCR confidence (heuristic based on output)
        avg_chars_per_page = total_chars / num_pages if num_pages > 0 else 0
        if avg_chars_per_page < 50:
            confidence = "low"
        elif avg_chars_per_page < 500:
            confidence = "medium"
        else:
            confidence = "high"

        return {
            'success': True,
            'text': full_text,
            'page_count': num_pages,
            'method': 'ocr',
            'confidence': confidence,
            'char_count': len(full_text),
            'avg_chars_per_page': avg_chars_per_page,
            'language': language,
            'dpi': dpi
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'OCR extraction failed: {str(e)}',
            'method': 'ocr'
        }
