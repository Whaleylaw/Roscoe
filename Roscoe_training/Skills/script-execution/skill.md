---
name: script-execution
description: Use when executing Python scripts from /Tools/ with direct GCS filesystem access - runs scripts in Docker containers for file operations, data processing, web scraping, batch operations, and automation tasks.
---

# Script Execution Skill

## Overview

Execute Python scripts from `/Tools/` with direct access to the GCS filesystem. Scripts run in isolated Docker containers with read-write access to all workspace files.

## When To Use

Use this skill when you need to:
- Run Python scripts from the `/Tools/` directory
- Execute data processing or analysis scripts
- Run file reorganization or batch operations
- Perform web scraping with browser automation
- Execute any script that needs to modify files

## Available Tools

### execute_python_script()

Execute Python scripts with filesystem access.

```python
execute_python_script(
    script_path="/Tools/create_file_inventory.py",
    case_name="Wilson-MVA-2024",
    script_args=["--format", "json"]
)
```

### execute_python_script_with_browser()

Execute scripts requiring browser automation (Playwright).

```python
execute_python_script_with_browser(
    script_path="/Tools/web_scraping/courtlistener_search.py",
    script_args=["personal injury Kentucky"]
)
```

## Examples

### File Inventory
```
Run create_file_inventory.py on the Wilson case to list all files
```

### Medical Analysis
```
Execute analyze_medical_records.py for Wilson-MVA-2024 and save to Reports/
```

### Document Import
```
Run batch_import_all.py to process all PDFs in the Sitgraves case
```

### Legal Research
```
Use the CourtListener search script to find Kentucky personal injury cases
```

### PDF Processing
```
Run read_pdf.py to extract text from Medical Records/report.pdf
```

## Script Categories

### Document Processing (`/Tools/document_processing/`)
- `read_pdf.py` - Extract text from PDFs
- `batch_import_all.py` - Import all case documents
- `import_documents.py` - Import specific documents

### Legal Research (`/Tools/legal_research/`)
- `search_case_law.py` - Search for case law
- `explore_citations.py` - Navigate citation networks
- `get_opinion_full_text.py` - Get full opinion text
- `find_my_cases.py` - Find cases by attorney
- `oral_arguments_search.py` - Search oral arguments

### Medical Research (`/Tools/medical_research/`)
- `pubmed_search.py` - Search PubMed
- `semantic_scholar_search.py` - Search academic papers

### Reporting (`/Tools/reporting/`)
- `active_negotiations_report.py` - Active settlement negotiations
- `outstanding_medical_records_report.py` - Pending records
- `outstanding_medical_bills_report.py` - Pending bills

### Research (`/Tools/research/`)
- `internet_search.py` - Web search via Tavily
- `expert_witness_lookup.py` - Expert credential lookup

## Tips

1. **Specify case_name** when running scripts that operate on case folders
2. **Use script_args** to pass command-line arguments
3. **Check output** for success/failure status and any errors
4. **Execution logs** are saved to `/Database/script_execution_logs/`
5. **Timeout** defaults to 5 minutes; increase for long operations

## Notes

- Scripts run in isolated Docker containers
- Changes persist to GCS automatically
- API keys are passed through to scripts
- Non-root execution for security

