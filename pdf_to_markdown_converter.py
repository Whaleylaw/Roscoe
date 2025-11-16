#!/usr/bin/env python3
"""
PDF to Markdown Converter for Whaley Law Firm Documents

This script:
1. Queries the Supabase doc_files table for all PDFs
2. Downloads each PDF from Supabase storage
3. Converts PDFs to Markdown using Docling
4. Saves Markdown files in the same folder structure as Supabase buckets
5. Deletes the local PDF file after conversion
6. Updates the database with markdown_path and markdown_regenerated_at

Usage:
    python pdf_to_markdown_converter.py [--dry-run] [--limit N] [--max-size MB] [--output-dir PATH]

Arguments:
    --dry-run       Show what would be converted without actually doing it
    --limit N       Process only the first N files (for testing)
    --max-size MB   Skip files larger than this size in MB (default: 50)
    --output-dir    Base directory for output (default: ./converted_documents)
"""

import os
import sys
import argparse
import logging
import csv
import traceback
import psutil
import multiprocessing
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PipelineOptions
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import InputFormat

# Load environment variables from .env file
load_dotenv()

# Fix for macOS segmentation faults with multiprocessing
# Must set before any multiprocessing code runs
if sys.platform == 'darwin':  # macOS
    multiprocessing.set_start_method('spawn', force=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_conversion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PDFToMarkdownConverter:
    """Handles conversion of PDFs from Supabase to Markdown using Docling"""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        output_base_dir: str = "./converted_documents",
        max_file_size_mb: float = 50.0
    ):
        """
        Initialize the converter

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            output_base_dir: Base directory for converted files
            max_file_size_mb: Maximum file size to process in MB
        """
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.output_base_dir = Path(output_base_dir)
        self.max_file_size_bytes = int(max_file_size_mb * 1024 * 1024)

        # Initialize DocumentConverter with default settings
        # macOS fork() issue is handled by setting multiprocessing start method to 'spawn'
        self.converter = DocumentConverter()

        self.error_log_path = Path("conversion_errors.csv")

        # Create output directory if it doesn't exist
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

        # Initialize error log CSV
        self._initialize_error_log()

        logger.info(f"Initialized converter with output directory: {self.output_base_dir}")
        logger.info(f"Maximum file size: {max_file_size_mb} MB")
        logger.info(f"Error log file: {self.error_log_path}")

    def _initialize_error_log(self):
        """Initialize the error log CSV file with headers if it doesn't exist"""
        if not self.error_log_path.exists():
            with open(self.error_log_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'uuid', 'project_name', 'filename',
                    'file_url', 'error_type', 'error_message', 'size_bytes'
                ])
            logger.info(f"Created error log file: {self.error_log_path}")

    def _log_error(self, file_record: Dict, error_type: str, error_message: str):
        """
        Log an error to the CSV file

        Args:
            file_record: Database record for the file
            error_type: Type of error (download, conversion, database_update, etc.)
            error_message: Detailed error message
        """
        try:
            with open(self.error_log_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    file_record.get('uuid', 'N/A'),
                    file_record.get('project_name', 'N/A'),
                    file_record.get('filename', 'N/A'),
                    file_record.get('file_url', 'N/A'),
                    error_type,
                    error_message,
                    file_record.get('size_bytes', 'N/A')
                ])
        except Exception as e:
            logger.error(f"Failed to write to error log: {str(e)}")

    def get_pdf_files(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Query Supabase for all PDF files with pagination support

        Args:
            limit: Optional limit on number of files to retrieve

        Returns:
            List of file records from the database
        """
        all_files = []
        page_size = 1000  # Supabase default max
        offset = 0

        logger.info("Fetching PDF files from database...")

        while True:
            # Build query with pagination
            # Only fetch files that haven't been converted yet (markdown_path is null)
            query = self.supabase.table('doc_files').select(
                'uuid, project_name, filename, storage_path, file_url, '
                'content_type, size_bytes, storage_bucket, markdown_path'
            ).eq('content_type', 'application/pdf').not_.is_('file_url', 'null').is_('markdown_path', 'null')

            # Apply pagination
            query = query.range(offset, offset + page_size - 1)

            try:
                response = query.execute()
                batch = response.data

                if not batch:
                    # No more results
                    break

                all_files.extend(batch)
                logger.info(f"  Fetched {len(batch)} files (total so far: {len(all_files)})")

                # If we got fewer than page_size, we've reached the end
                if len(batch) < page_size:
                    break

                # If user specified a limit and we've reached it, stop
                if limit and len(all_files) >= limit:
                    all_files = all_files[:limit]
                    break

                offset += page_size

            except Exception as e:
                logger.error(f"Error fetching files at offset {offset}: {e}")
                break

        logger.info(f"Found {len(all_files)} PDF files to process")
        return all_files

    def download_pdf(self, url: str, local_path: Path) -> bool:
        """
        Download a PDF from URL to local path

        Args:
            url: URL of the PDF file
            local_path: Local path to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Downloading {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # Create parent directory if needed
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file in chunks
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.debug(f"Downloaded to {local_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            return False

    def convert_pdf_to_markdown(self, pdf_path: Path) -> Optional[str]:
        """
        Convert a PDF file to Markdown using Docling

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Markdown content as string, or None if conversion failed
        """
        try:
            logger.debug(f"Converting {pdf_path} to Markdown")
            result = self.converter.convert(str(pdf_path))
            markdown_content = result.document.export_to_markdown()
            logger.debug(f"Successfully converted {pdf_path}")
            return markdown_content

        except Exception as e:
            logger.error(f"Failed to convert {pdf_path}: {str(e)}")
            logger.error(f"Conversion error traceback:\n{traceback.format_exc()}")
            return None

    def save_markdown(self, content: str, output_path: Path) -> bool:
        """
        Save Markdown content to file

        Args:
            content: Markdown content as string
            output_path: Path to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.debug(f"Saved Markdown to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save Markdown to {output_path}: {str(e)}")
            return False

    def update_database_record(self, uuid: int, markdown_path: str) -> bool:
        """
        Update the database record with markdown_path and timestamp

        Args:
            uuid: Record UUID
            markdown_path: Relative path to the markdown file

        Returns:
            True if successful, False otherwise
        """
        try:
            self.supabase.table('doc_files').update({
                'markdown_path': markdown_path,
                'markdown_regenerated_at': datetime.utcnow().isoformat()
            }).eq('uuid', uuid).execute()

            logger.debug(f"Updated database record {uuid}")
            return True

        except Exception as e:
            logger.error(f"Failed to update database record {uuid}: {str(e)}")
            return False

    def process_file(self, file_record: Dict, dry_run: bool = False) -> bool:
        """
        Process a single PDF file: download, convert, save, cleanup

        Args:
            file_record: Database record for the file
            dry_run: If True, only log what would happen without actually doing it

        Returns:
            True if successful, False otherwise
        """
        filename = file_record['filename']
        file_url = file_record['file_url']
        storage_path = file_record['storage_path']
        size_bytes = file_record.get('size_bytes', 0)
        uuid = file_record['uuid']

        # Check file size (handle None values from database)
        if size_bytes is not None and size_bytes > self.max_file_size_bytes:
            size_mb = size_bytes / (1024 * 1024)
            logger.warning(
                f"Skipping {filename} - size {size_mb:.2f} MB exceeds limit "
                f"of {self.max_file_size_bytes / (1024 * 1024):.2f} MB"
            )
            return False

        # Determine output paths based on storage_path
        # storage_path is like "Project-Name/filename.pdf"
        # We want to preserve this structure
        if storage_path:
            relative_dir = Path(storage_path).parent
            base_filename = Path(storage_path).stem  # filename without extension
        else:
            # Fallback if storage_path is missing
            relative_dir = Path(file_record.get('project_name', 'unknown'))
            base_filename = Path(filename).stem

        # Create paths
        pdf_download_path = self.output_base_dir / relative_dir / filename
        markdown_output_path = self.output_base_dir / relative_dir / f"{base_filename}.md"
        relative_markdown_path = str(relative_dir / f"{base_filename}.md")

        # Display file size safely
        size_display = f"({size_bytes / 1024:.2f} KB)" if size_bytes is not None else "(unknown size)"
        logger.info(f"Processing: {filename} {size_display}")

        if dry_run:
            logger.info(f"  [DRY RUN] Would download from: {file_url}")
            logger.info(f"  [DRY RUN] Would convert to: {markdown_output_path}")
            logger.info(f"  [DRY RUN] Would delete: {pdf_download_path}")
            logger.info(f"  [DRY RUN] Would update DB with path: {relative_markdown_path}")
            return True

        # Download PDF
        if not self.download_pdf(file_url, pdf_download_path):
            self._log_error(file_record, 'download_failed', f'Failed to download from {file_url}')
            return False

        try:
            # Convert to Markdown
            markdown_content = self.convert_pdf_to_markdown(pdf_download_path)
            if markdown_content is None:
                self._log_error(file_record, 'conversion_failed', 'PDF to Markdown conversion failed')
                return False

            # Save Markdown
            if not self.save_markdown(markdown_content, markdown_output_path):
                self._log_error(file_record, 'save_failed', f'Failed to save markdown to {markdown_output_path}')
                return False

            # Update database
            if not self.update_database_record(uuid, relative_markdown_path):
                logger.warning(f"Failed to update database for {filename}, but conversion succeeded")

            # Delete the local PDF
            try:
                pdf_download_path.unlink()
                logger.debug(f"Deleted temporary PDF: {pdf_download_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary PDF {pdf_download_path}: {str(e)}")

            logger.info(f"  ✓ Successfully converted to {markdown_output_path}")
            return True

        except Exception as e:
            error_msg = f"Error processing {filename}: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            self._log_error(file_record, 'processing_error', f"{str(e)} | {traceback.format_exc()[:500]}")
            # Clean up downloaded PDF if conversion failed
            if pdf_download_path.exists():
                try:
                    pdf_download_path.unlink()
                except:
                    pass
            return False

    def process_all(self, limit: Optional[int] = None, dry_run: bool = False):
        """
        Process all PDF files from the database

        Args:
            limit: Optional limit on number of files to process
            dry_run: If True, only show what would happen without doing it
        """
        files = self.get_pdf_files(limit)

        if not files:
            logger.info("No PDF files to process")
            return

        total = len(files)
        successful = 0
        failed = 0
        skipped = 0

        logger.info(f"Starting conversion of {total} files...")
        logger.info("=" * 80)

        for i, file_record in enumerate(files, 1):
            try:
                # Log memory usage every 10 files
                if i % 10 == 0:
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    logger.info(f"Memory usage: {memory_mb:.2f} MB")

                logger.info(f"\n[{i}/{total}] Processing {file_record['filename']}")

                result = self.process_file(file_record, dry_run)

                if result:
                    successful += 1
                else:
                    # Check if it was skipped due to size
                    file_size = file_record.get('size_bytes')
                    if file_size is not None and file_size > self.max_file_size_bytes:
                        skipped += 1
                    else:
                        failed += 1
            except Exception as e:
                logger.error(f"CRITICAL ERROR processing file {i}/{total}: {file_record.get('filename', 'UNKNOWN')}")
                logger.error(f"Error: {str(e)}")
                logger.error(f"Full traceback:\n{traceback.format_exc()}")
                # Log memory at time of error
                try:
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    logger.error(f"Memory at error: {memory_mb:.2f} MB")
                except:
                    pass
                self._log_error(file_record, 'critical_error', f"Critical loop error: {str(e)} | {traceback.format_exc()[:500]}")
                failed += 1
                # Continue processing next file instead of crashing
                continue

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("Conversion Summary:")
        logger.info(f"  Total files: {total}")
        logger.info(f"  Successful: {successful}")
        logger.info(f"  Failed: {failed}")
        logger.info(f"  Skipped (too large): {skipped}")
        logger.info("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Convert PDFs from Supabase to Markdown using Docling'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be converted without actually doing it'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Process only the first N files (for testing)'
    )
    parser.add_argument(
        '--max-size',
        type=float,
        default=50.0,
        help='Skip files larger than this size in MB (default: 50)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./converted_documents',
        help='Base directory for output (default: ./converted_documents)'
    )

    args = parser.parse_args()

    # Get Supabase credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        logger.error(
            "Missing Supabase credentials. Please set SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY) environment variables."
        )
        sys.exit(1)

    # Create converter and run
    converter = PDFToMarkdownConverter(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        output_base_dir=args.output_dir,
        max_file_size_mb=args.max_size
    )

    try:
        converter.process_all(limit=args.limit, dry_run=args.dry_run)
    except KeyboardInterrupt:
        logger.info("\n\nConversion interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"FATAL ERROR: {str(e)}", exc_info=True)
        # Write detailed crash report
        crash_report_path = Path("conversion_crash_report.log")
        with open(crash_report_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"CRASH REPORT - {datetime.now().isoformat()}\n")
            f.write(f"{'='*80}\n")
            f.write(f"Error: {str(e)}\n\n")
            f.write(f"Full Traceback:\n{traceback.format_exc()}\n")
            f.write(f"{'='*80}\n\n")
        logger.error(f"Crash report written to {crash_report_path}")
        sys.exit(1)


if __name__ == '__main__':
    main()
