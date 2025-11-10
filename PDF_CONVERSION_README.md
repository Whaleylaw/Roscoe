# PDF to Markdown Converter

This tool downloads PDF files from your Supabase `doc_files` table, converts them to Markdown using Docling, and saves them locally while maintaining the same folder structure as your Supabase storage buckets.

## Features

- Downloads PDFs from Supabase storage
- Converts PDFs to Markdown using Docling
- Maintains folder structure based on `storage_path`
- Deletes temporary PDF files after conversion
- Updates database with markdown file paths and timestamps
- Configurable file size limits to skip large files
- Dry-run mode for testing
- Comprehensive logging
- Resume capability (skips already converted files based on database)

## Prerequisites

1. Python 3.8 or higher
2. Supabase project credentials
3. Docling installed (already done)

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Set up your Supabase credentials as environment variables:

```bash
export SUPABASE_URL="your-supabase-url"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
```

Or add them to a `.env` file:

```bash
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

## Usage

### Basic Usage

Convert all PDFs:

```bash
python pdf_to_markdown_converter.py
```

### Test with Limited Files

Convert only the first 10 files:

```bash
python pdf_to_markdown_converter.py --limit 10
```

### Dry Run

See what would be converted without actually doing it:

```bash
python pdf_to_markdown_converter.py --dry-run --limit 5
```

### Custom Output Directory

Specify a different output directory:

```bash
python pdf_to_markdown_converter.py --output-dir /path/to/output
```

### Adjust File Size Limit

Skip files larger than 100 MB:

```bash
python pdf_to_markdown_converter.py --max-size 100
```

### Combined Options

```bash
python pdf_to_markdown_converter.py --limit 20 --max-size 25 --output-dir ./my_docs
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dry-run` | Show what would be converted without doing it | False |
| `--limit N` | Process only the first N files | None (all files) |
| `--max-size MB` | Skip files larger than this size in MB | 50 |
| `--output-dir PATH` | Base directory for output | `./converted_documents` |

## Output Structure

The program maintains your Supabase folder structure. For example:

```
converted_documents/
├── Project-Name-1/
│   ├── document1.md
│   ├── document2.md
│   └── subfolder/
│       └── document3.md
└── Project-Name-2/
    └── document4.md
```

Each file's location matches the `storage_path` from your `doc_files` table.

## Logging

The program creates two logs:

1. **Console output**: Real-time progress
2. **pdf_conversion.log**: Detailed log file for troubleshooting

## Database Updates

For each successfully converted file, the program updates the `doc_files` table with:

- `markdown_path`: Relative path to the markdown file
- `markdown_regenerated_at`: Timestamp of conversion

## Troubleshooting

### Missing Credentials Error

If you see "Missing Supabase credentials", make sure you've set the environment variables:

```bash
export SUPABASE_URL="your-url"
export SUPABASE_SERVICE_ROLE_KEY="your-key"
```

### Files Being Skipped

Check the log for the reason. Common causes:
- File size exceeds limit (adjust with `--max-size`)
- Download failed (check network connection)
- Conversion failed (check Docling compatibility)

### Large Files

Some PDF files may be very large. Consider:
- Increasing `--max-size` limit
- Processing large files separately
- Checking available disk space

## Notes

- The program is designed to be resumable - you can stop and restart it
- Temporary PDF files are deleted after successful conversion to save disk space
- Only PDFs where `content_type = 'application/pdf'` and `is_uploaded_to_storage = true` are processed
- Files without a valid `file_url` are skipped

## Statistics

After completion, you'll see a summary:

```
Conversion Summary:
  Total files: 100
  Successful: 95
  Failed: 2
  Skipped (too large): 3
```

## Safety Features

1. **Dry-run mode**: Test before running on all files
2. **File size limits**: Prevent processing of extremely large files
3. **Error handling**: Continues processing even if individual files fail
4. **Logging**: Detailed logs for troubleshooting
5. **Temporary file cleanup**: Deletes PDFs even if conversion fails
