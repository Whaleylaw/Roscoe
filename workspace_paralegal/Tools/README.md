# Tools Directory

## Concept: Dynamic Tool Discovery for Token Efficiency

Instead of binding tools to agents with full descriptions in every message context, this directory enables **dynamic tool discovery**:

1. **Agents read `tools_manifest.json`** when they need a tool
2. **Find the right tool** from descriptions and use cases
3. **Execute it directly** as a standalone Python script
4. **Process output incrementally** using grep/jq/awk if results are large

## Token Savings

Traditional approach:
- Tool descriptions included in EVERY message
- ~500-1000 tokens per tool per message
- With 5 tools = 2500-5000 tokens per message

Dynamic discovery approach:
- Agent reads manifest only when needed (~1000 tokens once)
- Executes tool, gets results
- Can filter large results with grep before reading
- **Saves thousands of tokens per conversation**

## How Agents Use This

### Step 1: Discover Available Tools
```python
# Read the manifest when you need a tool
tools_manifest = read_file('/Tools/tools_manifest.json')
manifest = json.loads(tools_manifest)

# Browse available tools
for tool in manifest['tools']:
    print(f"{tool['name']}: {tool['description']}")
```

### Step 2: Execute a Tool
```python
import subprocess

# Run internet search
result = subprocess.run(
    ['python', '/Tools/internet_search.py', 'Kentucky personal injury statute', '--pretty'],
    capture_output=True,
    text=True
)

# Parse JSON output
search_results = json.loads(result.stdout)
```

### Step 3: Process Large Output
```bash
# If results are huge, filter before reading
python /Tools/internet_search.py "expert witness neurology" --pretty | grep -i "university"

# Extract specific fields with jq
python /Tools/internet_search.py "medical research" | jq '.results.results[] | .title'

# Count results
python /Tools/internet_search.py "case law" | jq '.results.results | length'
```

## Directory Structure

```
/Tools/
├── tools_manifest.json       # Master registry of all permanent tools
├── README.md                 # This file
│
├── research/                 # General research tools (2)
├── medical_research/         # Medical/academic research tools (2)
├── legal_research/           # Legal research tools (7)
├── document_processing/      # PDF extraction tools (2)
│
├── _generated/               # Agent-generated scripts (temporary)
└── _archive/                 # Deprecated tools (replaced/obsolete)
```

## Available Tools (13 Permanent Tools)

See `tools_manifest.json` for complete list with usage examples. Each category folder also has its own `manifest.json`.

### Research (2 tools)
- **research/internet_search.py** - General web search via Tavily
- **research/expert_witness_lookup.py** - Verify expert credentials

### Medical Research (2 tools)
- **medical_research/pubmed_search.py** - PubMed medical literature search
- **medical_research/semantic_scholar_search.py** - Academic papers search

### Legal Research (7 tools)
- **legal_research/search_case_law.py** - CourtListener opinion search
- **legal_research/explore_citations.py** - Citation network analysis
- **legal_research/get_opinion_full_text.py** - Full opinion retrieval
- **legal_research/find_my_cases.py** - Find attorney's cases
- **legal_research/get_docket_details.py** - Full docket sheets
- **legal_research/monitor_upcoming_dates.py** - Calendar/deadline tracking
- **legal_research/oral_arguments_search.py** - Oral argument transcripts

### Document Processing (2 tools + modules)
- **document_processing/read_pdf.py** - PDF to markdown extraction
- **document_processing/import_documents.py** - Batch PDF import
- **document_processing/pdf_processors/** - Processing modules

## Agent-Generated Scripts

**Location:** `/Tools/_generated/`

This folder contains **temporary, case-specific scripts** created by agents during case processing (e.g., file reorganization scripts, batch processing scripts). These are not permanent tools.

**Key differences:**
- **Permanent tools** → `/Tools/[category]/` (reusable, tested, in manifest)
- **Generated scripts** → `/Tools/_generated/` (case-specific, temporary, not in manifest)

**Cleanup:** Scripts older than 90 days can be safely deleted. See `/Tools/_generated/README.md` for details.

## Adding New Tools

1. Create standalone Python script in this directory
2. Make it executable: `chmod +x script.py`
3. Accept arguments via command line
4. Output results to stdout (preferably JSON)
5. Add entry to `tools_manifest.json` with:
   - Name and description
   - Usage examples
   - When to use it
   - Output format

## Tool Guidelines

**Good tool design:**
- ✅ Standalone (minimal dependencies)
- ✅ CLI-based (argparse)
- ✅ JSON output to stdout
- ✅ Error handling with exit codes
- ✅ Self-documenting (--help)

**Avoid:**
- ❌ Importing from agent codebase
- ❌ Complex setup requirements
- ❌ Non-parseable output formats
- ❌ Silent failures

## Example: Creating a New Tool

```python
#!/usr/bin/env python3
"""
my_tool.py - Does something useful

Usage:
    python my_tool.py input [--option value]
"""

import sys
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="My useful tool")
    parser.add_argument("input", help="Input data")
    parser.add_argument("--option", default="default", help="Optional parameter")
    args = parser.parse_args()

    try:
        # Do work
        result = {"success": True, "output": "result"}
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Then add to `tools_manifest.json`:
```json
{
  "name": "my_tool",
  "file": "my_tool.py",
  "description": "Does something useful",
  "usage": "python /Tools/my_tool.py input [--option value]",
  "when_to_use": ["When you need to do X", "When situation Y occurs"]
}
```

## Benefits of This Approach

1. **Token Efficiency**: Only load tool info when needed
2. **Scalability**: Add unlimited tools without bloating agent config
3. **Flexibility**: Update tools without redeploying agent
4. **Output Control**: Process large results incrementally
5. **Modularity**: Tools are independently testable
6. **Cost Savings**: Lower token usage = lower API costs

## Testing Tools

Test tools directly from command line:

```bash
# Test internet search
python /Tools/internet_search.py "test query" --pretty

# Test with output filtering
python /Tools/internet_search.py "test" | jq '.results.results[] | .title'

# Check error handling
python /Tools/internet_search.py "test" --max-results 999
```
