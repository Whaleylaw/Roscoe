---
name: case-file-organization
description: Use when organizing disorganized case files, standardizing filenames, or categorizing documents into proper folders - applies 8-bucket system with standardized naming convention for personal injury case files and delegates work to sub-agents
---

# Case File Organization

**IMPORTANT: Before proceeding with this skill, you MUST announce to the user that you are using the "Case File Organization" skill.**

Example announcement: "I'm activating the Case File Organization skill to standardize and organize these case files according to the 8-bucket system."

## Overview

Standardizes organization, naming, and categorization of personal injury case files using an 8-bucket directory system and strict naming conventions. This skill ensures consistency, facilitates retrieval, and optimizes the file system.

**Core principle:** Every case file belongs in one of 8 buckets. Every filename follows the same pattern. All work is delegated to specialized sub-agents.

## When to Use

Use this skill when:
- Case files are disorganized or in the root folder
- Filenames don't follow a standard pattern
- Files need categorization into proper subdirectories
- Preparing files for vector database integration
- Client asks for file organization or cleanup
- Processing a "Review_Needed" folder

When NOT to use:
- Files are already properly organized and named
- Non-case files (internal firm documents, templates)
- Active documents being edited

## Execution Workflow

This skill orchestrates file organization through a 5-phase pipeline. You delegate all work to sub-agents except for Phase 3 decision point review.

### Phase 1: Inventory (Python Script - Content-Only Mode)

Run the inventory script to generate a complete file list with filename bias elimination:

```bash
python3 /Volumes/X10\ Pro/Roscoe/workspace_paralegal/Skills/case-file-organization/create_file_inventory.py "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}"
```

**PATH MAPPING CRITICAL:**

**For MAIN AGENT (you):**
- **FilesystemBackend operations** (read_file, write_file, ls, grep, etc.): Use VIRTUAL paths
  - Example: `read_file("/projects/{case_name}/Reports/file_inventory_{case_name}.md")`
  - Example: `ls("/projects/{case_name}/Reports")`
- **Shell tool operations** (bash commands): Use ABSOLUTE host paths
  - Example: `bash python3 "/Volumes/X10 Pro/Roscoe/workspace_paralegal/Skills/..."`
  - Example: `bash wc -l "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}/Reports/..."`

**For SUB-AGENTS:**
- **All operations**: Use VIRTUAL paths ONLY (they inherit FilesystemBackend)
  - Example: `/projects/{case_name}/Reports/...`
  - Example: `/Tools/_generated/...`
- **No shell access**: Sub-agents cannot execute bash commands

**Summary:**
- Virtual paths: `/projects/...`, `/Tools/...` (FilesystemBackend for both main and sub-agents)
- Absolute paths: `/Volumes/X10 Pro/Roscoe/workspace_paralegal/...` (Shell tool for main agent ONLY)

**What this script does (Content-Only Mode):**
1. **Scrambles filenames** to eliminate naming bias:
   - Moves all PDFs to `_pdf_originals/` temporary folder (preserving structure)
   - Renames .md files to scrambled sequential names: `doc_0001.md`, `doc_0002.md`, etc.
   - Creates mapping file: `/Reports/pdf_md_mapping_{case_name}.json` (scrambled → original paths)

2. **Generates file inventory:**
   - Lists ALL scrambled .md files (sub-agents will analyze ONLY content, no filename bias)
   - Lists non-PDF files (images, emails) with original names (NOT scrambled)
   - Creates `/projects/{case_name}/Reports/file_inventory_{case_name}.md`

3. **Why scrambling:**
   - Forces sub-agents to base names ONLY on file content
   - Eliminates copying from original filenames
   - Improves naming quality and consistency
   - PDFs reunited with .md files in Phase 4 using mapping

**Output files:**
- `/projects/{case_name}/Reports/file_inventory_{case_name}.md` - Lists scrambled .md files for analysis
- `/projects/{case_name}/Reports/pdf_md_mapping_{case_name}.json` - Maps `doc_0001.md` → original PDF path
- `/projects/{case_name}/_pdf_originals/` - PDFs moved here temporarily (hidden from sub-agents)

**Output format:**
```
| Path | Type | Notes |
|------|------|-------|
| doc_0001.md | MD | PDF companion (scrambled name) |
| doc_0002.md | MD | PDF companion (scrambled name) |
| photo1.jpg | IMAGE | |
| email1.eml | EML | |
```

### Phase 2: Analysis & Mapping

**IMPORTANT: Check file count first to determine parallelization strategy.**

**File Count Threshold Decision:**

1. **Count total files (use virtual path for read_file, or bash with absolute path):**
   ```bash
   # Option 1: Read via FilesystemBackend
   read_file("/projects/{case_name}/Reports/file_inventory_{case_name}.md")

   # Option 2: Count via bash (use absolute path)
   wc -l "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}/Reports/file_inventory_{case_name}.md"
   ```

2. **Apply threshold:**
   - **≤ 40 files:** Single sub-agent (standard workflow)
   - **> 40 files:** Multiple sub-agents in batches (divide workload)

**Threshold rationale:**
- Each file requires reading (500-5000 tokens)
- Sub-agent needs context for: inventory, skill instructions, categorization rules, output generation
- Summarization middleware triggers at 150K-200K tokens
- At ~40 files, sub-agent uses ~195K tokens total (safely under 200K limit)
- Beyond 40 files, risk of triggering automatic summarization and quality degradation

**Batching rationale:**
- Maximum 4 sub-agents spawn concurrently (resource constraint)
- If more than 4 sub-agents needed, process in batches of 4
- Wait for batch to complete before spawning next batch
- Example: 13 sub-agents needed → Batch 1 (4), Batch 2 (4), Batch 3 (4), Batch 4 (1)

---

#### Option A: Single Sub-Agent (≤ 40 files)

Spawn ONE general-purpose sub-agent with the **analysis-and-mapping sub-skill**:

```
Task: Analyze files and create reorganization mapping

Follow the complete analysis-and-mapping sub-skill at:
/workspace/Skills/case-file-organization/sub-skills/analysis-and-mapping.md

This sub-skill contains ALL the rules you need:
- 8-bucket categorization rules
- Complete naming convention
- Dating protocol
- Multi-party case handling
- Email and court notice rules
- Duplicate detection
- File reading instructions

Your deliverable:
Create `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md` with complete mapping

Note: Use virtual workspace paths starting with / (e.g., /projects/{case_name}/...)
```

**Why use a sub-skill:**
- Sub-agent gets complete context (all naming rules, categorization logic)
- No information loss when delegating
- Sub-agent can work independently with full instructions
- Main agent doesn't need to relay complex rules

---

#### Option B: Multiple Sub-Agents in Parallel (> 40 files)

For large file sets, divide the workload across multiple sub-agents to prevent context window exhaustion.

**Step 1: Calculate number of sub-agents needed**

```bash
# Get total file count (subtract 2 for header rows)
total_files=$(wc -l < /Reports/file_inventory_{case_name}.md)
file_count=$((total_files - 2))

# Recommended sub-agent count:
# 41-80 files    → 2 sub-agents (~20-40 files each)
# 81-120 files   → 3 sub-agents (~27-40 files each)
# 121-160 files  → 4 sub-agents (~30-40 files each)
# 161-240 files  → 6 sub-agents (~27-40 files each)
# 241-320 files  → 8 sub-agents (~30-40 files each)
# 321-400 files  → 10 sub-agents (~32-40 files each)
# 401-600 files  → 15 sub-agents (~27-40 files each, processed in batches)
# 601-1000 files → 25 sub-agents (~24-40 files each, processed in batches)
# 1001-2000 files → 50 sub-agents (~20-40 files each, processed in batches)
```

**Formula:** `num_agents = ceil(file_count / 40)`

**Step 2: Divide file inventory into chunks**

Create separate inventory files for each sub-agent using bash (absolute paths):

```bash
# Set paths (use absolute host paths for bash operations)
CASE_DIR="/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}"
REPORTS_DIR="$CASE_DIR/Reports"

# Extract header from original inventory
head -2 "$REPORTS_DIR/file_inventory_{case_name}.md" > "$REPORTS_DIR/file_inventory_header.md"

# Split remaining files into chunks (excluding header)
tail -n +3 "$REPORTS_DIR/file_inventory_{case_name}.md" > "$REPORTS_DIR/file_inventory_body.md"

# Calculate lines per chunk (40 files per sub-agent)
total_lines=$(wc -l < "$REPORTS_DIR/file_inventory_body.md")
chunk_size=40

# Split into chunks using split command
cd "$REPORTS_DIR"
split -l $chunk_size file_inventory_body.md file_chunk_

# Add headers back to each chunk and rename
for chunk in file_chunk_*; do
  chunk_num="${chunk#file_chunk_}"
  cat file_inventory_header.md "$chunk" > "file_inventory_chunk_${chunk_num}_{case_name}.md"
  rm "$chunk"
done

# Cleanup
rm file_inventory_header.md file_inventory_body.md
```

**Step 3: Spawn multiple sub-agents in parallel**

For each chunk file, spawn a sub-agent with a modified task:

```
Task: Analyze your assigned file subset and create partial reorganization mapping

YOU ARE SUB-AGENT #{chunk_number} OF {total_agents}

Follow the complete analysis-and-mapping sub-skill at:
/workspace/Skills/case-file-organization/sub-skills/analysis-and-mapping.md

IMPORTANT MODIFICATIONS FOR PARALLEL PROCESSING:
1. Read YOUR assigned inventory: /projects/{case_name}/Reports/file_inventory_chunk_{chunk_id}_{case_name}.md
2. ONLY analyze files listed in YOUR chunk (ignore all other files)
3. Save your partial mapping to: /projects/{case_name}/Reports/file_reorganization_map_chunk_{chunk_id}_{case_name}.md

This sub-skill contains ALL the rules you need:
- 8-bucket categorization rules
- Complete naming convention
- Dating protocol
- Multi-party case handling
- Email and court notice rules
- Duplicate detection
- File reading instructions

Your deliverable:
Create `/projects/{case_name}/Reports/file_reorganization_map_chunk_{chunk_id}_{case_name}.md` with:
- Mapping for ONLY your assigned files
- Same format as full mapping (table with columns: Current Path | Has .md? | Action | Target Bucket | New Filename | Notes)
- Duplicates identified within YOUR chunk
- Files requiring review flagged

Note: Use virtual workspace paths starting with / (e.g., /projects/{case_name}/...)
```

**Parallel Execution:**
- Process in batches of 4 to avoid overwhelming the system
- Example: 47 sub-agents total = 12 batches (4+4+4+4+4+4+4+4+4+4+4+3)
- Wait for each batch to complete before spawning next batch

**Step 4: Merge partial mappings into comprehensive map**

Once all sub-agents complete, merge their outputs using bash (absolute paths):

```bash
# Set paths
REPORTS_DIR="/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}/Reports"

# Create master mapping file
echo "# File Reorganization Map: {Case Name}" > "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "**Date Created:** $(date)" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "**Processing Method:** Parallel ({num_agents} sub-agents)" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"

# Extract and combine statistics from all chunks
echo "## Summary Statistics" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"

# Aggregate totals
total_move=0
total_delete=0
total_review=0

for chunk_map in "$REPORTS_DIR"/file_reorganization_map_chunk_*; do
  move_count=$(grep "Files to Move:" "$chunk_map" | awk '{print $NF}')
  delete_count=$(grep "Duplicates to Delete:" "$chunk_map" | awk '{print $NF}')
  review_count=$(grep "Files Needing Review:" "$chunk_map" | awk '{print $NF}')

  total_move=$((total_move + move_count))
  total_delete=$((total_delete + delete_count))
  total_review=$((total_review + review_count))
done

echo "- **Files to Move:** $total_move" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "- **Duplicates to Delete:** $total_delete" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "- **Files Needing Review:** $total_review" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"

# Combine reorganization plans
echo "## Reorganization Plan" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "| Current Path | Has .md? | Action | Target Bucket | New Filename | Notes |" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "|--------------|----------|--------|---------------|--------------|-------|" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"

for chunk_map in "$REPORTS_DIR"/file_reorganization_map_chunk_*; do
  grep "^|" "$chunk_map" | grep -v "Current Path" | grep -v "^|---" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
done

echo "" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"

# Combine files requiring review
echo "## Files Requiring User Review" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"

for chunk_map in "$REPORTS_DIR"/file_reorganization_map_chunk_*; do
  sed -n '/## Files Requiring User Review/,/## Duplicates Identified/p' "$chunk_map" | grep -v "^##" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
done

# Combine duplicates
echo "## Duplicates Identified for Deletion" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "| File | Reason | Keep Instead |" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
echo "|------|--------|--------------|" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"

for chunk_map in "$REPORTS_DIR"/file_reorganization_map_chunk_*; do
  sed -n '/## Duplicates Identified/,/## Recommendations/p' "$chunk_map" | grep "^|" | grep -v "File" | grep -v "^|---" >> "$REPORTS_DIR/file_reorganization_map_{case_name}.md"
done

# Cleanup chunk files
rm "$REPORTS_DIR"/file_reorganization_map_chunk_*
rm "$REPORTS_DIR"/file_inventory_chunk_*

echo "Master mapping created: $REPORTS_DIR/file_reorganization_map_{case_name}.md"
```

**Why parallel processing:**
- Each sub-agent stays within context limits (≤40 files)
- No context compression or quality degradation
- Stays safely under 200K token summarization middleware threshold
- Significantly faster for large file sets (multiple agents vs 1)
- Maintains accuracy even on 1800+ file cases
- Scales to unlimited file counts (just add more sub-agents in batches)
- Batching prevents system overload (max 4 concurrent agents)

---

### Phase 2 Validation (CRITICAL - Main Agent)

**After Phase 2 completes, BEFORE proceeding to Phase 3:**

Verify the reorganization map contains actual file rows, not placeholders:

```bash
# Count rows in the reorganization plan table (should match file count)
grep "^|" "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md" | grep -v "Current Path" | grep -v "^|---" | wc -l
```

**Expected:** Row count should equal or exceed the number of files in the inventory (minus header rows).

**If row count is 0 or suspiciously low:**
1. Read the mapping file to check for placeholders like "omitted for brevity" or "<!-- rows would be listed here -->"
2. **REJECT the mapping** and re-run Phase 2 with explicit instructions:
   ```
   CRITICAL ERROR: Your previous mapping used placeholders instead of actual file rows.

   Re-run Phase 2 with this additional instruction:
   - YOU MUST include EVERY SINGLE FILE as a separate row in the reorganization plan table
   - DO NOT use placeholders like "omitted for brevity"
   - DO NOT summarize - list all 150 files with complete Current Path | Has .md? | Action | Target Bucket | New Filename | Notes
   - This mapping will be used for automated file operations - missing rows = files won't be moved
   ```
3. Wait for Phase 2 to complete again
4. Re-validate before proceeding

**Only proceed to Phase 3 if validation passes.**

---

### Phase 3: Quality Review

Spawn a general-purpose sub-agent with the **quality-review sub-skill**:

```
Task: Comprehensive quality assurance review of file reorganization map

Follow the complete quality-review sub-skill at:
/workspace/Skills/case-file-organization/sub-skills/quality-review.md

This sub-skill contains ALL the verification procedures you need:
- Duplicate verification protocol
- Complete re-evaluation of EVERY file (not sampling)
- Categorization and naming validation against actual content
- Error tracking and flagged file handling
- Error rate calculation
- Quality assurance summary format

Your deliverable:
Create `/projects/{case_name}/Reports/quality_review_summary_{case_name}.md` with:
- Duplicate verification results
- Error rate calculation (% of files with issues)
- Complete error breakdown by category
- List of ALL flagged files in REVIEW_NEEDED_Phase_3/
- Clear recommendation (main agent review if ≤20% errors, user review if >20%)
- Statistics for every file checked

Quality standards:
- Re-check EVERY file as if doing Phase 2 yourself
- Flag only clear errors (wrong category, wrong facility, wrong client folder)
- Don't over-critique wording preferences
- Calculate accurate error rate
- Enable data-driven decision on next steps
- Accuracy is paramount - token usage and time don't matter

Note: Use virtual workspace paths starting with / (e.g., /projects/{case_name}/...)
```

**After Phase 3 completes:**

Read the quality review summary to check the error rate:

```bash
# Option 1: Read via FilesystemBackend
read_file("/projects/{case_name}/Reports/quality_review_summary_{case_name}.md")

# Option 2: Check via bash (use absolute path)
grep "Error Rate:" "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}/Reports/quality_review_summary_{case_name}.md"
```

**Decision Point:**

1. **Error rate ≤ 20% (FIRST ATTEMPT):**
   - Review the `/case_root/REVIEW_NEEDED_Phase_3/` folder yourself
   - Read each flagged file and the Phase 3 agent's concern
   - **Use the analysis-and-mapping sub-skill as your reference:**
     - Read: `/workspace/Skills/case-file-organization/sub-skills/analysis-and-mapping.md`
     - Apply the same categorization and naming rules the sub-agents use
   - Make final decision: Keep Phase 2's name or accept Phase 3's recommendation
   - Update the reorganization map with your decisions
   - Proceed to Phase 4 execution

2. **Error rate > 20% (FIRST ATTEMPT):**
   - **AUTOMATIC RETRY - Do NOT escalate to user yet**
   - Archive the failed attempt:
     ```bash
     mv /Reports/file_reorganization_map_{case_name}.md /Reports/file_reorganization_map_{case_name}_attempt1.md
     mv /Reports/quality_review_summary_{case_name}.md /Reports/quality_review_summary_{case_name}_attempt1.md
     ```
   - **Re-run Phase 2** with access to Phase 3's error report:
     - Spawn new Phase 2 sub-agent with analysis-and-mapping sub-skill
     - **IMPORTANT:** Include in Phase 2 task prompt:
       ```
       RETRY ATTEMPT: Phase 3 found {XX}% error rate on the previous attempt.

       Review the previous error report at:
       /Reports/quality_review_summary_{case_name}_attempt1.md

       Common errors found in previous attempt:
       - [List top error categories from Phase 3 report]

       Use this feedback to improve your analysis. Pay special attention to:
       - Correct facility names for medical records
       - Proper categorization (Medical Record vs Investigation, etc.)
       - Client-specific documents in multi-party cases
       - Dating protocol (service date vs received date)
       ```
   - Wait for Phase 2 to complete
   - **Re-run Phase 3** on the new reorganization map
   - **Check error rate again:**

3. **Error rate ≤ 20% (SECOND ATTEMPT):**
   - Review the `/case_root/REVIEW_NEEDED_Phase_3/` folder yourself
   - Use `/workspace/Skills/case-file-organization/sub-skills/analysis-and-mapping.md` as reference
   - Make final decision on flagged files
   - Update the reorganization map with your decisions
   - Proceed to Phase 4 execution
   - **Success:** Automatic retry fixed the issues

4. **Error rate > 20% (SECOND ATTEMPT):**
   - **NOW escalate to user**
   - Present both quality review summaries to user:
     - `/Reports/quality_review_summary_{case_name}_attempt1.md` (first attempt - {XX}% error rate)
     - `/Reports/quality_review_summary_{case_name}.md` (second attempt - {XX}% error rate)
   - Show the user what errors persisted across both attempts
   - Ask user to review `/case_root/REVIEW_NEEDED_Phase_3/` folder
   - Get user guidance on how to proceed
   - Options:
     - User provides specific corrections
     - User approves proceeding despite high error rate
     - User manually fixes flagged files

### Phase 4: Execution

**Prerequisites:**
- Phase 3 quality review complete
- Error rate ≤ 20% after main agent review, OR
- Error rate > 20% but user has provided approval/guidance

**CRITICAL: File operations must be done via bash script, not one-by-one.**

**Step 1: Generate Script** (sub-agent)

Spawn a general-purpose sub-agent with the **execution sub-skill** to generate the bash script:

```
Task: Generate bash script for file reorganization with PDF+MD reunification

Follow the complete execution sub-skill at:
/workspace/Skills/case-file-organization/sub-skills/execution.md

This sub-skill contains ALL the instructions you need:
- How to read the approved mapping AND pdf_md_mapping JSON file
- PDF+MD reunification workflow (scrambled .md → proper name, PDF from _pdf_originals → proper name)
- Complete bash script template with cleanup commands
- File operation rules (scrambled vs non-scrambled files, emails, duplicates)
- Script generation best practices

Your deliverable:
Save bash script to: `/Tools/_generated/reorganize_{case_name}.sh`

IMPORTANT:
- Read reorganization map from: /projects/{case_name}/Reports/file_reorganization_map_{case_name}.md
- Read PDF-MD mapping from: /projects/{case_name}/Reports/pdf_md_mapping_{case_name}.json
- Generate bash script with:
  - Absolute path cd command: cd "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}"
  - mv commands for scrambled .md files (e.g., doc_0042.md → proper name)
  - mv commands for PDFs from _pdf_originals/ (using mapping JSON)
  - Cleanup commands: rm -rf "_pdf_originals" and mapping JSON
- YOU generate the script, MAIN AGENT will execute it
```

**Step 2: Execute Script** (main agent via shell tool)

After sub-agent generates the script, execute it using the shell tool with absolute host paths:

```bash
# Read the generated script first (optional - to review)
read_file("/Tools/_generated/reorganize_{case_name}.sh")

# Execute the script with logging
bash "/Volumes/X10 Pro/Roscoe/workspace_paralegal/Tools/_generated/reorganize_{case_name}.sh" 2>&1 | tee "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}/Reports/reorganization_log_{case_name}.txt"
```

**PATH MAPPING:**
- Sub-agent writes script using virtual path: `/Tools/_generated/reorganize_{case_name}.sh`
- Main agent executes using absolute path: `/Volumes/X10 Pro/Roscoe/workspace_paralegal/Tools/_generated/reorganize_{case_name}.sh`
- Script contents use absolute path for cd, then relative paths for operations

**Why split sub-agent and main agent tasks:**
- Sub-agent uses FilesystemBackend (virtual paths) to read mapping and write script
- Main agent uses shell tool (absolute paths) to execute bash script
- This separation matches the path mapping architecture

### Phase 5: Verification & Report

Spawn a general-purpose sub-agent with the **verification sub-skill**:

```
Task: Verify reorganization and create summary report

Follow the complete verification sub-skill at:
/workspace/Skills/case-file-organization/sub-skills/verification.md

This sub-skill contains ALL the verification procedures you need:
- Directory structure verification
- Files in root check
- Naming convention validation
- Companion .md file verification
- File count by bucket
- Execution log review
- Issue identification and recommendations

Your deliverable:
Create `/projects/{case_name}/Reports/reorganization_summary_{case_name}.md` with:
- Verification results (directory structure, naming, companions)
- File distribution by bucket
- Execution log summary
- Issues found (if any)
- Overall assessment (SUCCESS/ISSUES/FAILED)
- Recommendations for next steps

Note: Use virtual workspace paths starting with / (e.g., /projects/{case_name}/...)
```

**Why use a sub-skill:**
- Sub-agent gets complete verification checklist and procedures
- Standardized verification across all cases
- Clear success criteria and reporting format
- Sub-agent works independently with full verification context

## Summary

This skill orchestrates a 5-phase file organization pipeline with validation checkpoints and filename bias elimination:

1. **Phase 1:** Run Python script for inventory (main agent uses shell tool)
   - **Content-Only Mode:** Scrambles .md filenames, hides PDFs in `_pdf_originals/`, creates mapping
   - Eliminates filename bias - sub-agents analyze ONLY file content

2. **Phase 2:** Delegate analysis to sub-agent(s) with analysis-and-mapping sub-skill
   - Sub-agents work with scrambled .md files (`doc_0001.md`, `doc_0002.md`, etc.)
   - Names determined purely from content (no original filename influence)
   - **Validation checkpoint:** Verify mapping has actual file rows (not placeholders)
   - If validation fails: reject and re-run Phase 2 with explicit no-summarizing instructions

3. **Phase 3:** Delegate quality review to sub-agent with quality-review sub-skill
   - **Decision point:** Review flagged files if error rate ≤ 20%
   - Use analysis-and-mapping sub-skill as reference when reviewing

4. **Phase 4:** Two-step execution with PDF+MD reunification
   - **Step 1:** Sub-agent generates bash script (reads mapping + pdf_md_mapping JSON)
   - Script reunites scrambled .md with PDFs from `_pdf_originals/` using same proper names
   - Cleanup removes `_pdf_originals/` and mapping file
   - **Step 2:** Main agent executes script (using shell tool/absolute paths)

5. **Phase 5:** Delegate verification to sub-agent with verification sub-skill

**Your role:** Orchestrate the workflow, validate Phase 2 output, make Phase 3 decisions, execute Phase 4 script, communicate with user

**Sub-agents' role:** Do all the detailed categorization, naming (from content only), script generation, and verification work

**Key Innovation:** Scrambled filenames force content-based analysis, improving naming quality and consistency
