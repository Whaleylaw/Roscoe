# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the **Whaley Law Firm** repository containing tools and frameworks for building AI-powered legal document processing and case management systems. The repository integrates:

- **Docling**: Advanced PDF-to-Markdown conversion with layout understanding
- **CopilotKit**: AI agent framework for building copilot interfaces
- **Supabase**: Backend database and storage for legal case files
- **Claude Code Superpowers**: Custom skills and workflows for enhanced development

## Primary Systems

### 1. PDF Document Processing Pipeline

The core document processing tool (`pdf_to_markdown_converter.py`) downloads PDFs from Supabase storage, converts them to Markdown using Docling, and updates the database.

**Key Features:**
- Batch processing with pagination support (1000 files/batch)
- Maintains folder structure from Supabase `storage_path`
- Error logging to `conversion_errors.csv`
- Database updates with `markdown_path` and `markdown_regenerated_at`
- Temporary PDF cleanup after conversion

**Running the Converter:**
```bash
# Basic usage
python pdf_to_markdown_converter.py

# Test with limited files
python pdf_to_markdown_converter.py --limit 10 --dry-run

# Custom settings
python pdf_to_markdown_converter.py --limit 20 --max-size 25 --output-dir ./my_docs
```

**Environment Setup:**
```bash
# Run setup script to configure environment
./setup_env.sh

# Or manually export credentials
export SUPABASE_URL="your-supabase-url"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
```

**Database Schema:**
- Table: `doc_files`
- Key fields: `uuid`, `project_name`, `filename`, `storage_path`, `file_url`, `content_type`, `size_bytes`, `markdown_path`, `markdown_regenerated_at`
- Storage: Supabase storage buckets with paths like `{project-name}/{filename}.pdf`

### 2. Supabase Data Exports

The `supabase-csv/` directory contains CSV exports of case management data:
- `case_projects_rows.csv` - Case/project metadata
- `case_notes_rows.csv` - Case notes (~24MB, largest file)
- `doc_files_rows.csv` - Document file metadata (~6.8MB)
- `contact_directory_rows.csv` - Contact information
- `case_expenses_rows.csv`, `case_insurance_rows.csv`, `case_liens_rows.csv`, etc.

### 3. Converted Documents Structure

Output directory `converted_documents/` organizes files by case:
```
converted_documents/
├── {Client-Name}-{CaseType}-{Date}/
│   ├── document1.md
│   ├── document2.md
│   └── subfolder/
│       └── document3.md
```

Case types: MVA (Motor Vehicle Accident), WC (Workers Compensation), SF (Slip and Fall), Premise Liability, Dual cases

### 4. Integrated Frameworks

**Docling** (`docling-main/`):
- Advanced PDF understanding including tables, formulas, images
- Export formats: Markdown, HTML, DocTags, JSON
- OCR support for scanned documents
- Local execution for sensitive data

**CopilotKit** (`CopilotKit-main/`):
- AI copilot/agent framework
- Supports multiple agent frameworks: LangGraph, CrewAI, Microsoft Agent Framework
- LLM adapters: OpenAI, Anthropic, Groq, Google Generative AI
- Quick start: `npx copilotkit@latest init`

## Development Workflows

### Claude Code Superpowers

This repository uses the Superpowers plugin with custom skills in `.claude/skills/`:

**Key Skills:**
- `using-superpowers` - Mandatory first skill, establishes workflows for skill checking
- `brainstorming` - Structured design refinement before coding
- `systematic-debugging` - Four-phase debugging framework
- `test-driven-development` - RED-GREEN-REFACTOR cycle
- `requesting-code-review` - Code review workflows
- `supabase-edge-functions-specialist` - Supabase Edge Functions debugging

**Slash Commands** (in `.claude/commands/`):
- `/brainstorm` - Start brainstorming session
- `/write-plan` - Create detailed implementation plan
- `/execute-plan` - Execute plan in batches with checkpoints

**Hooks** (in `.claude/hooks/`):
- `session-start.sh` - Loads using-superpowers skill at session start
- `hooks.json` - Hook configuration

**Important:** The session start hook automatically loads the `using-superpowers` skill, which establishes mandatory workflows including skill checking before tasks and brainstorming before coding.

## Technical Stack

**Python:**
- Docling >= 2.61.1
- Supabase >= 2.0.0
- Requests >= 2.31.0

**Database:**
- Supabase PostgreSQL with Row Level Security (RLS)
- Storage buckets for PDF files
- Service role key required for backend operations (bypasses RLS)

**Document Processing:**
- Input: PDF files from Supabase storage
- Processing: Docling converter with layout analysis
- Output: Markdown files with preserved folder structure
- Logging: `pdf_conversion.log` and `conversion_errors.csv`

## Architecture Considerations

### Data Flow
1. PDFs uploaded to Supabase storage buckets
2. Metadata stored in `doc_files` table with `storage_path`, `file_url`
3. Python converter downloads PDFs, converts via Docling
4. Markdown saved to `converted_documents/{project-name}/`
5. Database updated with `markdown_path` for retrieval

### Error Handling
- File size limits (default 50MB, configurable via `--max-size`)
- Comprehensive error logging with CSV tracking
- Graceful skipping of failed conversions
- Automatic cleanup of temporary PDF files
- Resume capability (skips already converted files)

### Legal Domain Context
This is a law firm case management system handling:
- Client case files (personal injury: MVA, WC, premise liability)
- Medical records and provider information
- Case expenses, liens, insurance details
- Litigation contacts and pleadings
- Document-heavy workflows requiring PDF processing

Future development should focus on AI agent tools for:
- Contract review and analysis
- Legal research and case law search
- Document drafting and generation
- Client intake automation
- Case summarization
