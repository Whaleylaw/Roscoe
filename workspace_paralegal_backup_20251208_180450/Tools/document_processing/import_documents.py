#!/usr/bin/env python3
"""
Batch PDF Import Tool - Pre-process all PDFs to Markdown

Finds all PDFs in a case folder and processes them to markdown format,
creating .md files alongside each PDF. Agents can then read the .md files
directly instead of re-processing PDFs every time.

Usage:
    python /Tools/import_documents.py <case_folder> [options]

Arguments:
    case_folder: Path to case folder containing PDFs

Options:
    --force          Re-process all PDFs even if .md files exist
    --quality-threshold N  Flag documents with quality score below N (default: 60)
    --report-dir DIR      Directory for reports (default: /Reports/)

Examples:
    # Process all PDFs in mo_alif case
    python /Tools/import_documents.py /mo_alif

    # Re-process all PDFs (ignore cache)
    python /Tools/import_documents.py /mo_alif --force

    # Custom quality threshold for flagging
    python /Tools/import_documents.py /mo_alif --quality-threshold 70

Output:
    - Creates .md file for each PDF (same directory as PDF)
    - Creates /Reports/import_log.json (machine-readable log)
    - Creates /Reports/DOCUMENT_INDEX.md (human-readable index)
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def find_pdfs(case_folder):
    """
    Find all PDF files in case folder recursively.

    Args:
        case_folder: Path to case folder

    Returns:
        list: List of Path objects for PDF files
    """
    case_path = Path(case_folder)

    if not case_path.exists():
        print(f"ERROR: Case folder not found: {case_folder}", file=sys.stderr)
        return []

    pdfs = list(case_path.rglob("*.pdf"))
    pdfs.extend(case_path.rglob("*.PDF"))  # Case-insensitive

    # Sort by path for consistent ordering
    pdfs.sort()

    return pdfs


def process_pdf(pdf_path, force=False, tools_dir="/Tools"):
    """
    Process a single PDF to markdown using read_pdf.py.

    Args:
        pdf_path: Path to PDF file
        force: Force re-processing even if .md exists
        tools_dir: Path to Tools directory

    Returns:
        dict: Processing result with metadata
    """
    pdf_file = Path(pdf_path)
    md_file = pdf_file.with_suffix('.md')

    # Build command
    cmd = [
        "python",
        f"{tools_dir}/read_pdf.py",
        str(pdf_path),
        "--output-format", "markdown"
    ]

    if force:
        cmd.append("--no-cache")

    # Execute read_pdf.py
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per PDF
        )

        # Parse output for metadata (stderr contains processing info)
        stderr_lines = result.stderr.strip().split('\n')

        # Extract quality info from stderr if present
        quality_score = None
        quality_level = "unknown"
        method = "unknown"
        needs_review = False

        for line in stderr_lines:
            if "Confidence Score:" in line:
                try:
                    quality_score = float(line.split(':')[1].split('/')[0].strip())
                except:
                    pass
            if "Overall Quality:" in line:
                quality_level = line.split(':')[1].strip()
            if "Extracting with" in line:
                if "PDFPlumber" in line:
                    method = "pdfplumber"
                elif "OCR" in line:
                    method = "ocr"
            if "RECOMMENDATION:" in line or "needs_review: true" in line:
                needs_review = True

        # Check if .md file was created
        if md_file.exists():
            # Parse metadata from frontmatter
            md_content = md_file.read_text(encoding='utf-8')
            lines = md_content.split('\n')

            # Extract metadata from frontmatter
            if lines[0] == '---':
                for line in lines[1:20]:  # Check first 20 lines for frontmatter
                    if line == '---':
                        break
                    if line.startswith('quality_score:'):
                        try:
                            quality_score = float(line.split(':')[1].strip())
                        except:
                            pass
                    if line.startswith('overall_quality:'):
                        quality_level = line.split(':')[1].strip()
                    if line.startswith('extraction_method:'):
                        method = line.split(':')[1].strip()
                    if line.startswith('needs_review:'):
                        needs_review = 'true' in line.lower()

            return {
                'success': True,
                'pdf_path': str(pdf_path),
                'md_path': str(md_file),
                'method': method,
                'quality_score': quality_score or 0,
                'quality_level': quality_level,
                'needs_review': needs_review,
                'file_size_kb': pdf_file.stat().st_size / 1024,
                'processed_at': datetime.now().isoformat()
            }
        else:
            return {
                'success': False,
                'pdf_path': str(pdf_path),
                'error': 'Markdown file not created',
                'stderr': result.stderr
            }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'pdf_path': str(pdf_path),
            'error': 'Processing timeout (>5 minutes)'
        }
    except Exception as e:
        return {
            'success': False,
            'pdf_path': str(pdf_path),
            'error': str(e)
        }


def create_import_log(results, case_folder, report_dir):
    """
    Create machine-readable import log JSON.

    Args:
        results: List of processing results
        case_folder: Path to case folder
        report_dir: Directory for reports
    """
    report_path = Path(report_dir)
    report_path.mkdir(parents=True, exist_ok=True)

    log_file = report_path / "import_log.json"

    total = len(results)
    successful = sum(1 for r in results if r.get('success'))
    failed = total - successful
    needs_review = sum(1 for r in results if r.get('needs_review'))

    log_data = {
        'case_folder': str(case_folder),
        'import_date': datetime.now().isoformat(),
        'total_pdfs': total,
        'successful': successful,
        'failed': failed,
        'needs_review': needs_review,
        'documents': results
    }

    log_file.write_text(json.dumps(log_data, indent=2), encoding='utf-8')
    print(f"\n✓ Import log saved: {log_file}", file=sys.stderr)


def create_document_index(results, case_folder, report_dir, quality_threshold):
    """
    Create human-readable document index in markdown.

    Args:
        results: List of processing results
        case_folder: Path to case folder
        report_dir: Directory for reports
        quality_threshold: Quality score threshold for flagging
    """
    report_path = Path(report_dir)
    report_path.mkdir(parents=True, exist_ok=True)

    index_file = report_path / "DOCUMENT_INDEX.md"

    lines = []
    lines.append("# Document Import Index")
    lines.append(f"**Case:** {Path(case_folder).name}")
    lines.append(f"**Import Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Total Documents:** {len(results)}")
    lines.append("")

    # Group by subdirectory
    from collections import defaultdict
    by_folder = defaultdict(list)

    for result in results:
        if result.get('success'):
            pdf_path = Path(result['pdf_path'])
            # Get relative path from case folder
            try:
                rel_path = pdf_path.relative_to(Path(case_folder))
                folder_name = str(rel_path.parent) if rel_path.parent != Path('.') else "Root"
            except:
                folder_name = "Unknown"

            by_folder[folder_name].append(result)

    # Output by folder
    for folder_name in sorted(by_folder.keys()):
        docs = by_folder[folder_name]
        lines.append(f"## {folder_name} ({len(docs)} documents)")
        lines.append("")

        for doc in docs:
            pdf_name = Path(doc['pdf_path']).name
            quality_score = doc.get('quality_score', 0)
            quality_level = doc.get('quality_level', 'unknown')
            method = doc.get('method', 'unknown')

            # Icon based on quality
            if doc.get('needs_review'):
                icon = "⚠️"
            elif quality_score >= 80:
                icon = "✓"
            else:
                icon = "○"

            lines.append(f"### {icon} {pdf_name}")
            lines.append(f"- **Source:** `{doc['pdf_path']}`")
            lines.append(f"- **Extracted:** `{doc['md_path']}`")
            lines.append(f"- **Method:** {method.title()}")
            lines.append(f"- **Quality:** {quality_level.title()} ({quality_score:.0f}/100)")

            if doc.get('needs_review'):
                lines.append(f"- **⚠️ Needs Review:** Quality below threshold or flagged for cloud processing")

            lines.append("")

    # Documents needing review section
    needs_review = [r for r in results if r.get('needs_review') or r.get('quality_score', 100) < quality_threshold]
    if needs_review:
        lines.append("---")
        lines.append("")
        lines.append("## Documents Needing Review")
        lines.append("")

        for doc in needs_review:
            pdf_name = Path(doc['pdf_path']).name
            quality_score = doc.get('quality_score', 0)

            lines.append(f"### ⚠️ {pdf_name}")
            lines.append(f"- **Quality:** {quality_score:.0f}/100")
            if quality_score < 40:
                lines.append(f"- **Recommendation:** Consider Google Cloud Document AI for better accuracy")
            lines.append("")

    # Summary statistics
    lines.append("---")
    lines.append("")
    lines.append("## Summary Statistics")
    lines.append("")

    successful = [r for r in results if r.get('success')]
    pdfplumber_count = sum(1 for r in successful if r.get('method') == 'pdfplumber')
    ocr_count = sum(1 for r in successful if r.get('method') == 'ocr')
    excellent_count = sum(1 for r in successful if r.get('quality_score', 0) >= 80)
    good_count = sum(1 for r in successful if 60 <= r.get('quality_score', 0) < 80)
    fair_count = sum(1 for r in successful if r.get('quality_score', 0) < 60)

    lines.append(f"- **Total Documents Processed:** {len(successful)}")
    lines.append(f"- **Text-based PDFs (PDFPlumber):** {pdfplumber_count}")
    lines.append(f"- **Scanned PDFs (OCR):** {ocr_count}")
    lines.append(f"- **Excellent Quality (≥80):** {excellent_count}")
    lines.append(f"- **Good Quality (60-79):** {good_count}")
    lines.append(f"- **Needs Review (<60):** {fair_count}")

    index_file.write_text("\n".join(lines), encoding='utf-8')
    print(f"✓ Document index saved: {index_file}", file=sys.stderr)


def main():
    """Command-line interface for batch PDF import."""
    parser = argparse.ArgumentParser(
        description="Batch import PDFs to Markdown format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /mo_alif
  %(prog)s /mo_alif --force
  %(prog)s /mo_alif --quality-threshold 70

Output:
  - Creates .md file for each PDF (same directory as PDF)
  - Creates /Reports/import_log.json (machine-readable)
  - Creates /Reports/DOCUMENT_INDEX.md (human-readable)
        """
    )

    parser.add_argument(
        "case_folder",
        help="Path to case folder containing PDFs"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-process all PDFs even if .md files exist"
    )

    parser.add_argument(
        "--quality-threshold",
        type=int,
        default=60,
        help="Flag documents with quality score below this value (default: 60)"
    )

    parser.add_argument(
        "--report-dir",
        default="/Reports",
        help="Directory for reports (default: /Reports)"
    )

    args = parser.parse_args()

    print(f"\n{'='*80}", file=sys.stderr)
    print(f"BATCH PDF IMPORT", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    print(f"\nCase Folder: {args.case_folder}", file=sys.stderr)

    # Find all PDFs
    print(f"\n[Step 1] Finding PDFs...", file=sys.stderr)
    pdfs = find_pdfs(args.case_folder)

    if not pdfs:
        print(f"ERROR: No PDF files found in {args.case_folder}", file=sys.stderr)
        sys.exit(1)

    print(f"  Found {len(pdfs)} PDF files", file=sys.stderr)

    # Process each PDF
    print(f"\n[Step 2] Processing PDFs to Markdown...", file=sys.stderr)
    results = []

    for i, pdf_path in enumerate(pdfs, start=1):
        print(f"  [{i}/{len(pdfs)}] Processing: {pdf_path.name}...", file=sys.stderr, end='')

        result = process_pdf(pdf_path, force=args.force)
        results.append(result)

        if result.get('success'):
            quality = result.get('quality_score', 0)
            print(f" ✓ ({quality:.0f}/100)", file=sys.stderr)
        else:
            print(f" ✗ FAILED: {result.get('error')}", file=sys.stderr)

    # Create reports
    print(f"\n[Step 3] Generating Reports...", file=sys.stderr)
    create_import_log(results, args.case_folder, args.report_dir)
    create_document_index(results, args.case_folder, args.report_dir, args.quality_threshold)

    # Final summary
    successful = sum(1 for r in results if r.get('success'))
    failed = len(results) - successful
    needs_review = sum(1 for r in results if r.get('needs_review') or r.get('quality_score', 100) < args.quality_threshold)

    print(f"\n{'='*80}", file=sys.stderr)
    print(f"✓ IMPORT COMPLETE", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    print(f"\nDocuments Processed: {successful}/{len(results)}", file=sys.stderr)
    if failed > 0:
        print(f"Failed: {failed}", file=sys.stderr)
    if needs_review > 0:
        print(f"⚠️  Needs Review: {needs_review} (see DOCUMENT_INDEX.md)", file=sys.stderr)

    print(f"\nAll extracted markdown files saved alongside PDFs", file=sys.stderr)
    print(f"Reports saved to: {args.report_dir}/", file=sys.stderr)
    print(f"{'='*80}\n", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
