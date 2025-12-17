"""
PDFPlumber Processor (Tier 1)

Extracts text and tables from text-based PDFs using pdfplumber.
Best for: Modern medical records, typed reports, electronic documents.
"""

import sys
from pathlib import Path


def extract_with_pdfplumber(pdf_path):
    """
    Extract text and tables from PDF using pdfplumber.

    Args:
        pdf_path: Path to PDF file

    Returns:
        dict: {
            'success': bool,
            'text': str,
            'tables': list,
            'page_count': int,
            'method': 'pdfplumber',
            'error': str (if failed)
        }
    """
    try:
        import pdfplumber
    except ImportError:
        return {
            'success': False,
            'error': 'pdfplumber not installed. Run: pip install pdfplumber',
            'method': 'pdfplumber'
        }

    try:
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            return {
                'success': False,
                'error': f'File not found: {pdf_path}',
                'method': 'pdfplumber'
            }

        with pdfplumber.open(pdf_path) as pdf:
            num_pages = len(pdf.pages)

            # Extract text from all pages
            text_parts = []
            text_parts.append("=" * 80)
            text_parts.append(f"PDF: {pdf_file.name}")
            text_parts.append(f"Total Pages: {num_pages}")
            text_parts.append(f"Extraction Method: PDFPlumber (Tier 1)")
            text_parts.append("=" * 80)
            text_parts.append("")

            all_tables = []

            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    # Extract text
                    page_text = page.extract_text()

                    text_parts.append(f"\n{'='*80}")
                    text_parts.append(f"PAGE {page_num} of {num_pages}")
                    text_parts.append('='*80)
                    text_parts.append(page_text if page_text else "[No text on this page]")

                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table_num, table in enumerate(tables, start=1):
                            all_tables.append({
                                'page': page_num,
                                'table_number': table_num,
                                'rows': table,
                                'row_count': len(table),
                                'column_count': len(table[0]) if table else 0
                            })

                            # Add table to text output
                            text_parts.append(f"\n[TABLE {table_num} on Page {page_num}]")
                            for row in table:
                                text_parts.append(" | ".join([str(cell) if cell else "" for cell in row]))

                    print(f"  ✓ Page {page_num}/{num_pages} extracted", file=sys.stderr)

                except Exception as e:
                    error_msg = f"  ✗ Error on page {page_num}: {str(e)}"
                    print(error_msg, file=sys.stderr)
                    text_parts.append(f"\n[ERROR ON PAGE {page_num}: {str(e)}]")

            full_text = "\n".join(text_parts)

            return {
                'success': True,
                'text': full_text,
                'tables': all_tables,
                'page_count': num_pages,
                'method': 'pdfplumber',
                'char_count': len(full_text),
                'table_count': len(all_tables)
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'PDFPlumber extraction failed: {str(e)}',
            'method': 'pdfplumber'
        }
