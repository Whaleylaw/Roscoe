# Knowledge Graph Query Scripts

**Location:** `/Tools/queries/` (in GCS bucket `whaley_law_firm`)
**Purpose:** Provide common graph queries as executable Python scripts
**Deployment:** Copy these scripts to GCS bucket at `/Tools/queries/`

---

## Overview

These scripts replace the legacy JSON file system with direct knowledge graph queries. Previously, the agent would read JSON files like:
- `~/json-files/caselist.json`
- `~/projects/{case-name}/overview.json`
- `~/projects/{case-name}/insurance.json`
- `~/projects/{case-name}/medical_providers.json`
- `~/projects/{case-name}/liens.json`

Now, all data is in the FalkorDB knowledge graph, and these scripts provide optimized, pre-tested queries.

---

## Architecture Philosophy

**Progressive Disclosure**: Scripts are discovered by the agent as needed via:
- `ls /Tools/queries/` - List available scripts
- File search when agent needs specific data
- Documentation in this README

**Minimal Prompt Footprint**: Scripts are NOT bound as tools in the agent definition, keeping the prompt clean.

**Usage Pattern**:
```python
# Agent discovers and executes scripts
execute_python_script(
    "/Tools/queries/get_case_insurance.py",
    script_args=["Christopher-Lanier-MVA-6-28-2025", "--pretty"]
)
```

---

## Available Scripts

### 1. get_case_overview.py
**Replaces:** `overview.json`
**Returns:** Basic case information, client details, phase, accident details, financials

**Usage:**
```bash
python get_case_overview.py "Christopher-Lanier-MVA-6-28-2025" --pretty
```

**Output Structure:**
```json
{
  "success": true,
  "case_name": "Christopher-Lanier-MVA-6-28-2025",
  "accident_type": "mva",
  "accident_date": "2025-06-28",
  "case_number": "25-CI-12345",
  "filing_date": null,
  "client": {
    "name": "Christopher Lanier",
    "phone": "555-1234",
    "email": "chris@example.com",
    "address": "123 Main St",
    "date_of_birth": "1985-03-15"
  },
  "current_phase": "file_setup",
  "phase_display": "File Setup",
  "financials": {
    "total_expenses": 250.00,
    "total_liens": 15000.00,
    "total_medical_bills": 25000.00,
    "provider_count": 3
  }
}
```

---

### 2. get_case_insurance.py
**Replaces:** `insurance.json`
**Returns:** All insurance claims with policies, insurers, adjusters, coverage limits

**Usage:**
```bash
python get_case_insurance.py "Christopher-Lanier-MVA-6-28-2025" --pretty
```

**Output Structure:**
```json
{
  "success": true,
  "case_name": "Christopher-Lanier-MVA-6-28-2025",
  "total_claims": 2,
  "claims": [
    {
      "claim_number": "17-87C986K",
      "claim_type": "PIPClaim",
      "policy_number": "POL-123456",
      "insurer": {
        "name": "State Farm",
        "phone": "800-555-1234",
        "address": "PO Box 12345"
      },
      "adjuster": {
        "name": "Jane Smith",
        "phone": "502-555-6789",
        "email": "jane.smith@statefarm.com"
      },
      "coverage": {
        "bi_limit": 50000.00,
        "pip_limit": 10000.00,
        "um_limit": 50000.00
      },
      "claim_status": "active",
      "demand_amount": 10000.00,
      "current_offer": 8000.00
    }
  ]
}
```

---

### 3. get_case_providers.py
**Replaces:** `medical_providers.json`
**Returns:** All medical providers using three-tier hierarchy (HealthSystem → Facility → Location)

**Usage:**
```bash
python get_case_providers.py "Christopher-Lanier-MVA-6-28-2025" --pretty
```

**Output Structure:**
```json
{
  "success": true,
  "case_name": "Christopher-Lanier-MVA-6-28-2025",
  "total_providers": 3,
  "providers": [
    {
      "name": "Norton Orthopedic Institute - Downtown",
      "type": "Location",
      "specialty": "Orthopedics",
      "phone": "502-555-1234",
      "fax": "502-555-1235",
      "address": "123 Medical Plaza, Louisville, KY",
      "records_request": {
        "method": "portal",
        "url": "https://norton.org/records"
      },
      "parent": "Norton Orthopedic Institute",
      "parent_type": "Facility",
      "health_system": "Norton Healthcare"
    },
    {
      "name": "Starlight Chiropractic",
      "type": "Facility",
      "specialty": "Chiropractic",
      "phone": "502-555-9999"
    }
  ]
}
```

**Notes:**
- Returns both Facility and Location entities
- Includes full hierarchy path (provider → parent → health_system)
- Includes records_request fields if available
- Queries up the hierarchy for records request information

---

### 4. get_case_liens.py
**Replaces:** `liens.json`
**Returns:** All liens with holder information, amounts, status

**Usage:**
```bash
python get_case_liens.py "Christopher-Lanier-MVA-6-28-2025" --pretty
```

**Output Structure:**
```json
{
  "success": true,
  "case_name": "Christopher-Lanier-MVA-6-28-2025",
  "total_liens": 2,
  "total_amount": 15000.00,
  "total_negotiated": 12000.00,
  "liens": [
    {
      "lien_name": "Norton Healthcare Lien",
      "holder": {
        "name": "Norton Healthcare",
        "type": "hospital",
        "phone": "502-555-0000",
        "address": "PO Box 99999"
      },
      "lien_type": "hospital",
      "amount": 15000.00,
      "negotiated_amount": 12000.00,
      "status": "pending",
      "account_number": "ACC-123456",
      "related_provider": "Norton Hospital"
    }
  ]
}
```

---

### 5. get_case_timeline.py
**Replaces:** Episode queries, provides chronological case history
**Returns:** All episodes for a case in reverse chronological order

**Usage:**
```bash
python get_case_timeline.py "Christopher-Lanier-MVA-6-28-2025" --pretty
python get_case_timeline.py "Christopher-Lanier-MVA-6-28-2025" --limit 50 --pretty
```

**Output Structure:**
```json
{
  "success": true,
  "case_name": "Christopher-Lanier-MVA-6-28-2025",
  "total_episodes": 45,
  "limit_applied": 100,
  "episodes": [
    {
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Insurance update: Christopher-Lanier-MVA-6-28-2025",
      "content": "Called State Farm adjuster Jane Smith. PIP claim approved for $10,000.",
      "valid_at": "2025-12-15T14:30:00",
      "author": "agent",
      "episode_type": "insurance_update",
      "created_at": 1734275400,
      "related_entities": [
        {"entity_name": "State Farm", "entity_type": "Insurer"},
        {"entity_name": "Jane Smith", "entity_type": "Adjuster"}
      ]
    }
  ]
}
```

**Notes:**
- Episodes ordered by valid_at (most recent first)
- Includes all related entities via ABOUT relationships
- Default limit: 100 episodes (override with --limit)

---

## Common Patterns

### Agent Discovery
```python
# Agent can find scripts via ls
ls /Tools/queries/

# Or search for specific functionality
# Agent: "I need to get insurance info for a case"
# → Searches files, finds get_case_insurance.py
```

### Agent Execution
```python
execute_python_script(
    "/Tools/queries/get_case_insurance.py",
    script_args=["Case-Name", "--pretty"]
)
```

### Output Parsing
All scripts output JSON to stdout with standard structure:
```json
{
  "success": true|false,
  "case_name": "...",
  "error": "..." (if success=false),
  ... data fields ...
}
```

---

## When to Use These vs Other Tools

### Use Query Scripts When:
- You need structured case data (overview, insurance, providers, liens)
- You want pre-tested, optimized queries
- You need consistent output format
- Replacing legacy JSON file reads

### Use `query_case_graph()` When:
- You need semantic search ("find episodes about settlement")
- Searching across episode content
- Don't know exact entity names
- Timeline-based natural language queries

### Use `graph_query(custom_cypher)` When:
- You need a custom query not covered by scripts
- Complex multi-hop traversals
- Statistical aggregations
- Cross-case analysis

### Use Middleware Auto-Context When:
- You mention a client name in your message
- Context is automatically injected
- No explicit query needed

---

## Deployment Instructions

### Copy to GCS Bucket
```bash
# Upload all query scripts to GCS
gsutil cp get_case_*.py gs://whaley_law_firm/Tools/queries/
gsutil cp this README gs://whaley_law_firm/Tools/queries/README.md

# Verify
gsutil ls gs://whaley_law_firm/Tools/queries/
```

### Or via gcsfuse on VM
```bash
# If /mnt/workspace is mounted via gcsfuse
cp get_case_*.py /mnt/workspace/Tools/queries/
cp TOOLS_QUERIES_README.md /mnt/workspace/Tools/queries/README.md
```

---

## Error Handling

All scripts follow consistent error handling:

**On Success:**
```json
{"success": true, "case_name": "...", ...data...}
```
Exit code: 0

**On Error:**
```json
{"success": false, "case_name": "...", "error": "Description"}
```
Exit code: 1

---

## Development Notes

### Environment Variables
Scripts use standard FalkorDB connection:
- `FALKORDB_HOST` (default: "localhost")
- `FALKORDB_PORT` (default: "6379")

### Dependencies
- `falkordb` - Graph database client

### Testing Locally
```bash
# Set environment
export FALKORDB_HOST=localhost
export FALKORDB_PORT=6379

# Test a script
python get_case_insurance.py "Christopher-Lanier-MVA-6-28-2025" --pretty
```

### Adding New Query Scripts
1. Follow the template pattern (argparse, JSON output, error handling)
2. Document in this README
3. Upload to GCS bucket
4. No agent code changes needed - scripts are auto-discoverable

---

## Schema Reference

For writing custom queries, see:
- **Schema Documentation:** `/KNOWLEDGE_GRAPH_SCHEMA.md`
- **Entity Definitions:** `/src/roscoe/core/graphiti_client.py`
- **Relationship Patterns:** EDGE_TYPE_MAP in graphiti_client.py

---

**Last Updated:** January 4, 2026
**Maintained By:** Add new scripts as needed, update this README
