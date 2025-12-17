#!/usr/bin/env python3
"""
Workspace-Wide Batch PDF Import - Process ALL Case Folders

Recursively processes all case folders in the workspace, converting all PDFs
to markdown format. Maintains progress tracking so it can resume after crashes.

Usage:
    python /Tools/batch_import_all.py [options]

Options:
    --workspace DIR       Workspace root directory (default: /)
    --force              Re-process all folders even if marked complete
    --resume             Resume from last checkpoint (default behavior)
    --progress-file FILE  Custom progress file path (default: /Reports/batch_import_progress.json)

Examples:
    # Start batch import of entire workspace
    python /Tools/batch_import_all.py

    # Resume from crash
    python /Tools/batch_import_all.py --resume

    # Force re-process everything
    python /Tools/batch_import_all.py --force

    # Custom workspace location
    python /Tools/batch_import_all.py --workspace /custom/workspace

Progress Tracking:
    - Progress saved to /Reports/batch_import_progress.json
    - Updates after each folder completes
    - Can resume from checkpoint if process crashes
    - Tracks: completed folders, current folder, statistics

Folder Selection:
    - Only processes folders that contain PDFs
    - Skips: Reports/, Tools/, Skills/, .git/, hidden folders
    - Case folders detected automatically (contain medical_records, medical_bills, litigation, or PDFs)
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import argparse


def load_progress(progress_file):
    """
    Load progress from checkpoint file.

    Args:
        progress_file: Path to progress JSON file

    Returns:
        dict: Progress data or empty dict if no progress file
    """
    progress_path = Path(progress_file)

    if not progress_path.exists():
        return {
            'version': '1.0',
            'started': datetime.now().isoformat(),
            'last_update': None,
            'completed_folders': [],
            'current_folder': None,
            'failed_folders': [],
            'statistics': {
                'total_folders': 0,
                'completed': 0,
                'failed': 0,
                'total_pdfs': 0,
                'total_processed': 0
            }
        }

    try:
        with open(progress_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠ Warning: Could not load progress file: {e}", file=sys.stderr)
        print(f"  Starting fresh...", file=sys.stderr)
        return {
            'version': '1.0',
            'started': datetime.now().isoformat(),
            'last_update': None,
            'completed_folders': [],
            'current_folder': None,
            'failed_folders': [],
            'statistics': {
                'total_folders': 0,
                'completed': 0,
                'failed': 0,
                'total_pdfs': 0,
                'total_processed': 0
            }
        }


def save_progress(progress_data, progress_file):
    """
    Save progress to checkpoint file.

    Args:
        progress_data: Progress dict
        progress_file: Path to progress JSON file
    """
    progress_path = Path(progress_file)
    progress_path.parent.mkdir(parents=True, exist_ok=True)

    progress_data['last_update'] = datetime.now().isoformat()

    try:
        with open(progress_path, 'w') as f:
            json.dump(progress_data, f, indent=2)
    except Exception as e:
        print(f"⚠ Warning: Could not save progress: {e}", file=sys.stderr)


def find_case_folders(workspace_root):
    """
    Find all case folders in workspace.

    Args:
        workspace_root: Path to workspace root

    Returns:
        list: List of Path objects for case folders
    """
    workspace_path = Path(workspace_root)

    if not workspace_path.exists():
        print(f"ERROR: Workspace not found: {workspace_root}", file=sys.stderr)
        return []

    # Skip these directories
    skip_dirs = {'Reports', 'Tools', 'Skills', '.git', '__pycache__', 'venv', 'env'}

    case_folders = []

    # Find all directories
    for item in workspace_path.iterdir():
        if not item.is_dir():
            continue

        # Skip hidden and system directories
        if item.name.startswith('.') or item.name in skip_dirs:
            continue

        # Check if folder contains PDFs (case folder indicator)
        pdf_files = list(item.rglob("*.pdf"))
        pdf_files.extend(item.rglob("*.PDF"))

        if pdf_files:
            case_folders.append(item)

    # Sort for consistent ordering
    case_folders.sort()

    return case_folders


def process_case_folder(case_folder, force=False):
    """
    Process all PDFs in a case folder.

    Args:
        case_folder: Path to case folder
        force: Force re-processing even if .md files exist

    Returns:
        dict: Processing result with statistics
    """
    case_path = Path(case_folder)

    print(f"\n{'='*80}", file=sys.stderr)
    print(f"PROCESSING CASE FOLDER: {case_path.name}", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    print(f"Path: {case_path}", file=sys.stderr)

    # Find all PDFs
    pdf_files = list(case_path.rglob("*.pdf"))
    pdf_files.extend(case_path.rglob("*.PDF"))
    pdf_files = list(set(pdf_files))  # Remove duplicates
    pdf_files.sort()

    print(f"Found {len(pdf_files)} PDF files", file=sys.stderr)

    if not pdf_files:
        return {
            'success': True,
            'folder': str(case_path),
            'pdf_count': 0,
            'processed': 0,
            'cached': 0,
            'failed': 0,
            'message': 'No PDFs found'
        }

    # Process each PDF
    processed = 0
    cached = 0
    failed = 0

    for i, pdf_path in enumerate(pdf_files, start=1):
        md_path = pdf_path.with_suffix('.md')

        # Check file size
        pdf_size_mb = pdf_path.stat().st_size / (1024 * 1024)

        # Check if already processed (unless force)
        if not force and md_path.exists():
            # Check timestamps
            pdf_mtime = pdf_path.stat().st_mtime
            md_mtime = md_path.stat().st_mtime

            if md_mtime >= pdf_mtime:
                size_info = f" ({pdf_size_mb:.1f}MB)" if pdf_size_mb > 10 else ""
                print(f"  [{i}/{len(pdf_files)}] {pdf_path.name}{size_info} - Cached ✓", file=sys.stderr)
                cached += 1
                continue

        # Process PDF
        size_info = f" ({pdf_size_mb:.1f}MB)" if pdf_size_mb > 10 else ""
        print(f"  [{i}/{len(pdf_files)}] Processing: {pdf_path.name}{size_info}...", file=sys.stderr, end='', flush=True)

        try:
            # Get absolute path to read_pdf.py (same directory as this script)
            script_dir = Path(__file__).parent
            read_pdf_path = script_dir / "read_pdf.py"

            cmd = [
                "python",
                str(read_pdf_path),
                str(pdf_path),
                "--output-format", "markdown"
            ]

            # Dynamic timeout based on file size
            # Small PDFs (<10MB): 5 minutes
            # Medium PDFs (10-50MB): 15 minutes
            # Large PDFs (>50MB): 30 minutes
            if pdf_size_mb < 10:
                timeout = 300  # 5 minutes
            elif pdf_size_mb < 50:
                timeout = 900  # 15 minutes
            else:
                timeout = 1800  # 30 minutes

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if md_path.exists():
                # Extract quality score from md file
                try:
                    md_content = md_path.read_text(encoding='utf-8')
                    quality_score = 0
                    for line in md_content.split('\n')[:20]:
                        if line.startswith('quality_score:'):
                            quality_score = int(float(line.split(':')[1].strip()))
                            break
                    print(f" ✓ ({quality_score}/100)", file=sys.stderr)
                except:
                    print(f" ✓", file=sys.stderr)

                processed += 1
            else:
                print(f" ✗ FAILED", file=sys.stderr)
                failed += 1

        except subprocess.TimeoutExpired:
            print(f" ✗ TIMEOUT", file=sys.stderr)
            failed += 1
        except Exception as e:
            print(f" ✗ ERROR: {e}", file=sys.stderr)
            failed += 1

    # Generate reports for this case folder
    print(f"\nGenerating case folder reports...", file=sys.stderr)
    try:
        # Get absolute path to import_documents.py
        script_dir = Path(__file__).parent
        import_docs_path = script_dir / "import_documents.py"

        # Use import_documents.py to generate reports (it won't re-process PDFs since .md files exist)
        cmd = [
            "python",
            str(import_docs_path),
            str(case_path),
            "--report-dir", str(case_path.parent / "Reports" / f"{case_path.name}_reports")
        ]

        subprocess.run(cmd, capture_output=True, timeout=60)
        print(f"  ✓ Reports generated in /Reports/{case_path.name}_reports/", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠ Could not generate reports: {e}", file=sys.stderr)

    return {
        'success': True,
        'folder': str(case_path),
        'folder_name': case_path.name,
        'pdf_count': len(pdf_files),
        'processed': processed,
        'cached': cached,
        'failed': failed
    }


def main():
    """Command-line interface for workspace-wide batch import."""
    parser = argparse.ArgumentParser(
        description="Batch import ALL case folders in workspace to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --resume
  %(prog)s --force
  %(prog)s --workspace /custom/workspace

Progress Tracking:
  Progress saved to /Reports/batch_import_progress.json after each folder.
  Can resume from checkpoint if process crashes or is interrupted.
        """
    )

    # Determine default paths based on script location
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent  # workspace directory
    default_progress_file = workspace_root / "Reports" / "batch_import_progress.json"

    parser.add_argument(
        "--workspace",
        default=str(workspace_root),
        help=f"Workspace root directory (default: {workspace_root})"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-process all folders even if marked complete"
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint (default behavior)"
    )

    parser.add_argument(
        "--progress-file",
        default=str(default_progress_file),
        help=f"Progress file path (default: {default_progress_file})"
    )

    args = parser.parse_args()

    print(f"\n{'='*80}", file=sys.stderr)
    print(f"WORKSPACE-WIDE BATCH PDF IMPORT", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    print(f"Workspace: {args.workspace}", file=sys.stderr)
    print(f"Progress File: {args.progress_file}", file=sys.stderr)

    # Load progress
    progress = load_progress(args.progress_file)

    if args.force:
        print(f"\n⚠ Force mode: Re-processing all folders", file=sys.stderr)
        progress['completed_folders'] = []
        progress['failed_folders'] = []

    # Find all case folders
    print(f"\n[Step 1] Finding case folders...", file=sys.stderr)
    case_folders = find_case_folders(args.workspace)

    if not case_folders:
        print(f"ERROR: No case folders found in {args.workspace}", file=sys.stderr)
        sys.exit(1)

    print(f"  Found {len(case_folders)} case folders", file=sys.stderr)

    # Filter out completed folders (unless force)
    if not args.force:
        completed_set = set(progress.get('completed_folders', []))
        pending_folders = [f for f in case_folders if str(f) not in completed_set]

        if len(pending_folders) < len(case_folders):
            print(f"  {len(case_folders) - len(pending_folders)} folders already completed (skipping)", file=sys.stderr)
            print(f"  {len(pending_folders)} folders remaining", file=sys.stderr)

        case_folders = pending_folders

    if not case_folders:
        print(f"\n✓ All folders already processed!", file=sys.stderr)
        print(f"  Use --force to re-process", file=sys.stderr)
        sys.exit(0)

    # Update statistics
    progress['statistics']['total_folders'] = len(case_folders)

    # Process each case folder
    print(f"\n[Step 2] Processing case folders...", file=sys.stderr)

    for i, case_folder in enumerate(case_folders, start=1):
        print(f"\n{'='*80}", file=sys.stderr)
        print(f"FOLDER {i}/{len(case_folders)}: {case_folder.name}", file=sys.stderr)
        print(f"{'='*80}", file=sys.stderr)

        # Update current folder in progress
        progress['current_folder'] = str(case_folder)
        save_progress(progress, args.progress_file)

        # Process folder
        try:
            result = process_case_folder(case_folder, force=args.force)

            if result['success']:
                # Mark as completed
                progress['completed_folders'].append(str(case_folder))
                progress['statistics']['completed'] += 1
                progress['statistics']['total_pdfs'] += result['pdf_count']
                progress['statistics']['total_processed'] += result['processed']

                # Remove from failed if it was there
                if str(case_folder) in progress.get('failed_folders', []):
                    progress['failed_folders'].remove(str(case_folder))

                print(f"\n✓ Folder Complete: {case_folder.name}", file=sys.stderr)
                print(f"  PDFs: {result['pdf_count']}", file=sys.stderr)
                print(f"  Processed: {result['processed']}", file=sys.stderr)
                print(f"  Cached: {result['cached']}", file=sys.stderr)
                if result['failed'] > 0:
                    print(f"  Failed: {result['failed']}", file=sys.stderr)

            else:
                # Mark as failed
                if str(case_folder) not in progress.get('failed_folders', []):
                    progress['failed_folders'].append(str(case_folder))
                progress['statistics']['failed'] += 1

                print(f"\n✗ Folder Failed: {case_folder.name}", file=sys.stderr)

        except KeyboardInterrupt:
            print(f"\n\n⚠ Process interrupted by user", file=sys.stderr)
            progress['current_folder'] = None
            save_progress(progress, args.progress_file)
            print(f"\nProgress saved. Run again to resume from: {case_folder.name}", file=sys.stderr)
            sys.exit(130)

        except Exception as e:
            print(f"\n✗ Unexpected error processing {case_folder.name}: {e}", file=sys.stderr)

            if str(case_folder) not in progress.get('failed_folders', []):
                progress['failed_folders'].append(str(case_folder))
            progress['statistics']['failed'] += 1

        # Save progress after each folder
        progress['current_folder'] = None
        save_progress(progress, args.progress_file)

    # Final summary
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"✓ BATCH IMPORT COMPLETE", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    print(f"\nFolders Processed: {progress['statistics']['completed']}/{progress['statistics']['total_folders']}", file=sys.stderr)
    print(f"Total PDFs Processed: {progress['statistics']['total_processed']}", file=sys.stderr)

    if progress['statistics']['failed'] > 0:
        print(f"\nFailed Folders: {progress['statistics']['failed']}", file=sys.stderr)
        for folder in progress.get('failed_folders', []):
            print(f"  - {Path(folder).name}", file=sys.stderr)

    print(f"\nProgress saved to: {args.progress_file}", file=sys.stderr)
    print(f"Individual case reports in: /Reports/<case_name>_reports/", file=sys.stderr)
    print(f"{'='*80}\n", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
