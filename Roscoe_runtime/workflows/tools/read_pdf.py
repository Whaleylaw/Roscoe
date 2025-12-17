#!/usr/bin/env python3
"""
Medical/Legal PDF Processing Tool with Tiered OCR Pipeline

Extracts text and tables from PDFs using a 3-tier approach:
- Tier 1: PDFPlumber (fast, text-based PDFs)
- Tier 2: PyTesseract OCR (scanned/image-based PDFs)
- Tier 3: Google Cloud Document AI (future - complex cases)

Usage:
    python /Tools/read_pdf.py <pdf_file_path> [output_file_path] [options]

Arguments:
    pdf_file_path: Path to the PDF file to read
    output_file_path: (Optional) Path to save extracted content.
                      Defaults to <pdf_name>.md alongside PDF.

Options:
    --force-ocr         Force OCR processing (Tier 2) even if text is detected
    --extract-tables    Save tables to separate JSON file (text format only)
    --quality-report    Show quality metrics and classification
    --method METHOD     Force specific method: pdfplumber|ocr|auto (default: auto)
    --ocr-dpi DPI       OCR resolution (default: 300, higher = better quality)
    --output-format FMT Output format: markdown|text|json (default: markdown)
    --no-cache          Disable cache - always re-process PDF

Examples:
    # Process PDF to markdown (default, creates doctor_note.md)
    python /Tools/read_pdf.py /case/medical_records/doctor_note.pdf

    # Use cached .md file if it exists (default behavior)
    python /Tools/read_pdf.py /case/medical_records/doctor_note.pdf

    # Force re-processing even if cache exists
    python /Tools/read_pdf.py /case/records/scan.pdf --no-cache

    # Output plain text instead of markdown
    python /Tools/read_pdf.py /case/records/report.pdf --output-format text

    # Get quality report
    python /Tools/read_pdf.py /case/records/doc.pdf --quality-report

    # Save to specific location
    python /Tools/read_pdf.py /case/records/report.pdf /Reports/report.md
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Import our PDF processors
try:
    from pdf_processors.pdfplumber_processor import extract_with_pdfplumber
    from pdf_processors.ocr_processor import extract_with_ocr
    from pdf_processors.quality_metrics import assess_quality, classify_pdf
except ImportError:
    # If running from different directory, try adding Tools to path
    import os
    tools_dir = Path(__file__).parent
    sys.path.insert(0, str(tools_dir))
    from pdf_processors.pdfplumber_processor import extract_with_pdfplumber
    from pdf_processors.ocr_processor import extract_with_ocr
    from pdf_processors.quality_metrics import assess_quality, classify_pdf


def format_as_markdown(result, pdf_path):
    """
    Convert extraction result to markdown format with frontmatter.

    Args:
        result: Extraction result dict from extract_pdf_text
        pdf_path: Path to source PDF file

    Returns:
        str: Markdown formatted text with metadata, tables, and page markers
    """
    lines = []

    # Frontmatter with metadata
    lines.append("---")
    lines.append(f"source: {Path(pdf_path).name}")
    lines.append(f"extraction_method: {result.get('method', 'unknown')}")

    quality = result.get('quality', {})
    lines.append(f"quality_score: {quality.get('confidence_score', 0):.0f}")
    lines.append(f"overall_quality: {quality.get('overall_quality', 'unknown')}")

    lines.append(f"pages: {result.get('page_count', 0)}")
    lines.append(f"extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if quality.get('needs_cloud_ai'):
        lines.append("needs_review: true")
        lines.append(f"issues: {', '.join(quality.get('issues', []))}")

    lines.append("---")
    lines.append("")

    # Main text content
    text = result.get('text', '')

    # If we have page-by-page data, format with page markers
    if 'pages' in result and isinstance(result['pages'], list):
        for i, page_data in enumerate(result['pages'], start=1):
            lines.append(f"# Page {i}")
            lines.append("")
            lines.append(page_data.get('text', '').strip())
            lines.append("")
    else:
        # Just add the text as-is
        lines.append(text)

    # Add tables if present
    tables = result.get('tables', [])
    if tables:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("# Extracted Tables")
        lines.append("")

        for table in tables:
            page = table.get('page', 0)
            table_num = table.get('table_number', 0)
            rows = table.get('rows', [])

            lines.append(f"## Table {table_num} (Page {page})")
            lines.append("")

            if rows:
                # Convert to markdown table
                # First row is typically headers
                if len(rows) > 0:
                    header_row = rows[0]
                    # Clean up None values and convert to strings
                    header_row = [str(cell) if cell is not None else '' for cell in header_row]
                    lines.append("| " + " | ".join(header_row) + " |")
                    lines.append("|" + "|".join(["---" for _ in header_row]) + "|")

                    # Data rows
                    for row in rows[1:]:
                        row = [str(cell) if cell is not None else '' for cell in row]
                        lines.append("| " + " | ".join(row) + " |")

                lines.append("")

    return "\n".join(lines)


def check_cache(pdf_path, use_cache=True):
    """
    Check if a cached markdown file exists for this PDF.

    Args:
        pdf_path: Path to PDF file
        use_cache: Whether to use cache (default: True)

    Returns:
        dict: {
            'cached': bool,
            'cache_path': Path or None,
            'cache_valid': bool (True if cache is newer than PDF)
        }
    """
    if not use_cache:
        return {'cached': False, 'cache_path': None, 'cache_valid': False}

    pdf_file = Path(pdf_path)
    cache_file = pdf_file.with_suffix('.md')

    if not cache_file.exists():
        return {'cached': False, 'cache_path': cache_file, 'cache_valid': False}

    # Check timestamps - cache is valid if it's newer than the PDF
    pdf_mtime = pdf_file.stat().st_mtime
    cache_mtime = cache_file.stat().st_mtime

    cache_valid = cache_mtime >= pdf_mtime

    return {
        'cached': True,
        'cache_path': cache_file,
        'cache_valid': cache_valid
    }


def extract_pdf_text(pdf_path, method='auto', force_ocr=False, ocr_dpi=300):
    """
    Extract text from PDF using tiered pipeline.

    Args:
        pdf_path: Path to PDF file
        method: Extraction method ('auto', 'pdfplumber', 'ocr')
        force_ocr: Force OCR even if text is detected
        ocr_dpi: OCR resolution (default: 300)

    Returns:
        dict: Extraction result with text, quality metrics, etc.
    """
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        return {
            'success': False,
            'error': f'File not found: {pdf_path}'
        }

    if not pdf_file.suffix.lower() == '.pdf':
        return {
            'success': False,
            'error': f'File is not a PDF: {pdf_path}'
        }

    print(f"\nProcessing PDF: {pdf_file.name}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)

    # Step 1: Classify PDF (if auto method)
    if method == 'auto' and not force_ocr:
        print("\n[Step 1] Classifying PDF...", file=sys.stderr)
        classification = classify_pdf(pdf_path)
        print(f"  Classification: {classification.get('classification', 'unknown')}", file=sys.stderr)
        print(f"  Confidence: {classification.get('confidence', 'unknown')}", file=sys.stderr)
        print(f"  Recommendation: {classification.get('recommendation', 'unknown')}", file=sys.stderr)

        # Use recommended method
        if classification.get('recommendation') == 'pdfplumber':
            method = 'pdfplumber'
        elif classification.get('recommendation') == 'ocr':
            method = 'ocr'
        elif classification.get('recommendation') == 'hybrid':
            method = 'hybrid'
        else:
            method = 'pdfplumber'  # Default fallback

    elif force_ocr:
        method = 'ocr'
        classification = {'classification': 'forced_ocr'}

    # Step 2: Extract text using appropriate method
    result = None

    if method == 'pdfplumber' or method == 'hybrid':
        print(f"\n[Step 2] Extracting with PDFPlumber (Tier 1)...", file=sys.stderr)
        result = extract_with_pdfplumber(pdf_path)

        if not result.get('success'):
            print(f"  ✗ PDFPlumber failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
            if method == 'hybrid':
                print("  → Falling back to OCR (Tier 2)...", file=sys.stderr)
                method = 'ocr'
                result = None
        else:
            # Check if extraction quality is too low (hybrid mode)
            if method == 'hybrid':
                quality = assess_quality(result)
                if quality.get('needs_cloud_ai'):
                    print(f"  ⚠ Low quality extraction detected", file=sys.stderr)
                    print("  → Falling back to OCR (Tier 2)...", file=sys.stderr)
                    result = extract_with_ocr(pdf_path, dpi=ocr_dpi)

    if method == 'ocr' and result is None:
        print(f"\n[Step 2] Extracting with OCR (Tier 2)...", file=sys.stderr)
        result = extract_with_ocr(pdf_path, dpi=ocr_dpi)

    if not result.get('success'):
        return result

    # Step 3: Assess quality
    print(f"\n[Step 3] Assessing extraction quality...", file=sys.stderr)
    quality = assess_quality(result)
    print(f"  Overall Quality: {quality.get('overall_quality', 'unknown')}", file=sys.stderr)
    print(f"  Confidence Score: {quality.get('confidence_score', 0):.1f}/100", file=sys.stderr)

    if quality.get('issues'):
        print(f"  Issues Detected:", file=sys.stderr)
        for issue in quality['issues']:
            print(f"    - {issue}", file=sys.stderr)

    if quality.get('needs_cloud_ai'):
        print(f"\n  ⚠ RECOMMENDATION: This document may benefit from cloud processing (Tier 3)", file=sys.stderr)
        print(f"     Google Cloud Document AI would provide better accuracy for this file.", file=sys.stderr)

    # Add classification and quality to result
    result['classification'] = classification if 'classification' in locals() else {}
    result['quality'] = quality

    return result


def main():
    """Command-line interface for PDF extraction."""
    parser = argparse.ArgumentParser(
        description="Extract text from PDFs using tiered OCR pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /case/medical_records/report.pdf
  %(prog)s /case/records/scan.pdf --force-ocr
  %(prog)s /case/records/labs.pdf --extract-tables
  %(prog)s /case/records/doc.pdf --quality-report
  %(prog)s /case/records/report.pdf /Reports/report.txt --extract-tables

Tiered Pipeline:
  Tier 1: PDFPlumber - Fast text extraction for typed documents
  Tier 2: PyTesseract OCR - For scanned/image-based PDFs
  Tier 3: Google Cloud Document AI - Future integration for complex cases

Output is text to stdout (or file if specified).
Quality metrics and progress go to stderr.
        """
    )

    parser.add_argument(
        "pdf_path",
        help="Path to PDF file"
    )

    parser.add_argument(
        "output_path",
        nargs='?',
        help="Optional output file path (prints to stdout if omitted)"
    )

    parser.add_argument(
        "--force-ocr",
        action="store_true",
        help="Force OCR processing (Tier 2) even if text is detected"
    )

    parser.add_argument(
        "--extract-tables",
        action="store_true",
        help="Save tables to separate JSON file (with .tables.json extension)"
    )

    parser.add_argument(
        "--quality-report",
        action="store_true",
        help="Show detailed quality report"
    )

    parser.add_argument(
        "--method",
        choices=['auto', 'pdfplumber', 'ocr'],
        default='auto',
        help="Extraction method (default: auto)"
    )

    parser.add_argument(
        "--ocr-dpi",
        type=int,
        default=300,
        help="OCR resolution in DPI (default: 300, higher = better quality)"
    )

    parser.add_argument(
        "--output-format",
        choices=['markdown', 'text', 'json'],
        default='markdown',
        help="Output format (default: markdown)"
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable cache - always re-process PDF even if .md exists"
    )

    args = parser.parse_args()

    # Check for cached .md file first
    cache_info = check_cache(args.pdf_path, use_cache=not args.no_cache)

    if cache_info['cached'] and cache_info['cache_valid']:
        print(f"\n✓ Using cached extraction: {cache_info['cache_path']}", file=sys.stderr)
        print(f"  (PDF has not been modified since extraction)", file=sys.stderr)

        # Read cached markdown file
        cached_content = cache_info['cache_path'].read_text(encoding='utf-8')

        # If output format is markdown, just use cached file
        if args.output_format == 'markdown':
            if args.output_path:
                output_file = Path(args.output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(cached_content, encoding='utf-8')
                print(f"\n✓ Cached content copied to: {args.output_path}", file=sys.stderr)
            else:
                print("\n" + cached_content)
            print(f"\n✓ Used cached file (no processing needed)", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            sys.exit(0)
        else:
            print(f"  Note: Re-processing to convert to {args.output_format} format", file=sys.stderr)

    elif cache_info['cached'] and not cache_info['cache_valid']:
        print(f"\n⚠ Cached file exists but is outdated (PDF was modified)", file=sys.stderr)
        print(f"  Re-processing PDF...", file=sys.stderr)

    # Extract text
    result = extract_pdf_text(
        args.pdf_path,
        method=args.method,
        force_ocr=args.force_ocr,
        ocr_dpi=args.ocr_dpi
    )

    if not result.get('success'):
        print(f"\nERROR: {result.get('error', 'Unknown error')}", file=sys.stderr)
        if 'help' in result:
            print(f"\n{result['help']}", file=sys.stderr)
        sys.exit(1)

    # Format output based on format flag
    if args.output_format == 'markdown':
        output_content = format_as_markdown(result, args.pdf_path)
        default_ext = '.md'
    elif args.output_format == 'json':
        output_content = json.dumps(result, indent=2)
        default_ext = '.json'
    else:  # text
        output_content = result.get('text', '')
        default_ext = '.txt'

    # Determine output path
    if args.output_path:
        output_file = Path(args.output_path)
    else:
        # Default to .md file alongside PDF
        output_file = Path(args.pdf_path).with_suffix(default_ext)

    # Write output
    if args.output_path or args.output_format == 'markdown':
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(output_content, encoding='utf-8')
        print(f"\n✓ Extracted and saved to: {output_file}", file=sys.stderr)
        if args.output_format == 'markdown':
            print(f"  Format: Markdown with metadata and tables", file=sys.stderr)
    else:
        # Print to stdout
        print("\n" + output_content)

    # Extract tables separately only if --extract-tables flag is used AND not using markdown format
    # (markdown format already includes tables inline)
    if args.extract_tables and args.output_format != 'markdown' and 'tables' in result and result['tables']:
        if args.output_path:
            tables_path = Path(args.output_path).with_suffix('.tables.json')
        else:
            tables_path = Path(args.pdf_path).with_suffix('.tables.json')

        tables_path.write_text(json.dumps(result['tables'], indent=2), encoding='utf-8')
        print(f"✓ {len(result['tables'])} tables extracted and saved to: {tables_path}", file=sys.stderr)

    # Show quality report if requested
    if args.quality_report:
        print("\n" + "=" * 80, file=sys.stderr)
        print("QUALITY REPORT", file=sys.stderr)
        print("=" * 80, file=sys.stderr)
        print(json.dumps({
            'classification': result.get('classification', {}),
            'quality': result.get('quality', {}),
            'metrics': {
                'method': result.get('method'),
                'page_count': result.get('page_count'),
                'char_count': result.get('char_count'),
                'table_count': result.get('table_count', 0)
            }
        }, indent=2), file=sys.stderr)

    print(f"\n✓ Processing complete", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
