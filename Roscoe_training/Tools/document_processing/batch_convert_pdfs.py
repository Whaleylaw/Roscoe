#!/usr/bin/env python3
"""
Batch convert all PDFs in a folder to Markdown.

Usage:
    python batch_convert_pdfs.py <folder_path>
"""

import sys
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_pdf(pdf_path: Path, read_pdf_script: Path) -> dict:
    """Process a single PDF to markdown."""
    md_path = pdf_path.with_suffix('.md')
    
    # Skip if markdown already exists
    if md_path.exists():
        return {
            'pdf': str(pdf_path),
            'status': 'skipped',
            'message': 'Markdown already exists'
        }
    
    try:
        result = subprocess.run(
            ['python', str(read_pdf_script), str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if md_path.exists():
            return {
                'pdf': str(pdf_path.name),
                'status': 'success',
                'md': str(md_path)
            }
        else:
            return {
                'pdf': str(pdf_path.name),
                'status': 'failed',
                'error': result.stderr[-500:] if result.stderr else 'Unknown error'
            }
    except subprocess.TimeoutExpired:
        return {
            'pdf': str(pdf_path.name),
            'status': 'failed',
            'error': 'Timeout (>5 min)'
        }
    except Exception as e:
        return {
            'pdf': str(pdf_path.name),
            'status': 'failed',
            'error': str(e)
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_convert_pdfs.py <folder_path>")
        sys.exit(1)
    
    folder = Path(sys.argv[1])
    if not folder.exists():
        print(f"ERROR: Folder not found: {folder}")
        sys.exit(1)
    
    # Find read_pdf.py in same directory as this script
    script_dir = Path(__file__).parent
    read_pdf_script = script_dir / "read_pdf.py"
    
    if not read_pdf_script.exists():
        print(f"ERROR: read_pdf.py not found at {read_pdf_script}")
        sys.exit(1)
    
    # Find all PDFs recursively
    pdfs = list(folder.rglob("*.pdf")) + list(folder.rglob("*.PDF"))
    pdfs = sorted(set(pdfs))  # Remove duplicates, sort
    
    print(f"\n{'='*60}")
    print(f"BATCH PDF TO MARKDOWN CONVERSION")
    print(f"{'='*60}")
    print(f"Folder: {folder}")
    print(f"PDFs found: {len(pdfs)}")
    print(f"{'='*60}\n")
    
    if not pdfs:
        print("No PDFs found!")
        sys.exit(0)
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    # Process with thread pool for parallel execution
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(process_pdf, pdf, read_pdf_script): pdf 
            for pdf in pdfs
        }
        
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            status = result['status']
            
            if status == 'success':
                success_count += 1
                print(f"[{i}/{len(pdfs)}] ✓ {result['pdf']}")
            elif status == 'skipped':
                skip_count += 1
                print(f"[{i}/{len(pdfs)}] ○ {result['pdf']} (already exists)")
            else:
                fail_count += 1
                print(f"[{i}/{len(pdfs)}] ✗ {result['pdf']}: {result.get('error', 'Unknown')[:80]}")
    
    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"Converted: {success_count}")
    print(f"Skipped (already exist): {skip_count}")
    print(f"Failed: {fail_count}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

