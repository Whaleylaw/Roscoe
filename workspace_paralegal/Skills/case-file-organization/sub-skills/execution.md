# Execution Sub-Skill

**Purpose:** Generate bash script for file reorganization based on approved mapping.

**This is Phase 4 of the Case File Organization workflow.**

---

## Your Task

You are generating the file reorganization script. Your job is to:

1. **Read the approved reorganization map**
2. **Generate a complete bash script** with all file operations
3. **Save the script** for main agent to execute

**IMPORTANT:** You generate the script, but the MAIN AGENT will execute it using the shell tool.

**CRITICAL: ALL file operations MUST be done via a single bash script, not one-by-one.**

---

## Inputs

You will work with:
- `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md` - The approved mapping from Phase 2
- `/projects/{case_name}/Reports/pdf_md_mapping_{case_name}.json` - Scrambled → original filename mapping from Phase 1
- `/projects/{case_name}/Reports/quality_review_summary_{case_name}.md` - The QA approval from Phase 3
- Case directory path (provided by main agent)

---

## Step 1: Read the Approved Mapping and PDF-MD Map

**Read the reorganization map:** `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md`
- Which files to move (these will be scrambled .md names like `doc_0001.md`)
- New filenames for each file
- Which bucket (category folder) each file goes to
- Which duplicates to delete
- Files flagged for later review (if any)

**Read the PDF-MD mapping:** `/projects/{case_name}/Reports/pdf_md_mapping_{case_name}.json`
- Maps scrambled .md names (`doc_0001.md`) to original PDF and MD paths
- Structure: `{"doc_0001.md": {"original_pdf": "...", "original_md": "...", "pdf_location": "_pdf_originals/..."}}`
- Use this to reunite PDFs with their renamed .md companions

---

## Step 2: Generate Bash Script

Create a complete bash script and save it to: `/Tools/_generated/reorganize_{case_name}.sh`

**CRITICAL - Understanding the Workflow:**

1. **Reorganization map** lists scrambled .md names (e.g., `doc_0001.md`, `doc_0042.md`)
2. **PDF-MD mapping** shows where each PDF is located in `_pdf_originals/`
3. **For each PDF+MD pair:**
   - Find scrambled .md name in reorganization map (e.g., `doc_0042.md`)
   - Get the new proper filename from the map
   - Look up original PDF location in `pdf_md_mapping_{case_name}.json`
   - Generate TWO mv commands:
     - Move `doc_0042.md` → `BucketName/YYYY-MM-DD - Client - Category - Originator - Description.md`
     - Move `_pdf_originals/original/path.pdf` → `BucketName/YYYY-MM-DD - Client - Category - Originator - Description.pdf`

4. **For non-PDF files** (images, emails):
   - These were NOT scrambled
   - Use original filenames from reorganization map
   - Move as normal with companion .md checks

Use write_file() to save the script with the following structure:

### Script Template:

```bash
#!/bin/bash
# File Reorganization Script for {Case Name}
# Generated: {Date}
# Based on: /projects/{case_name}/Reports/file_reorganization_map_{case_name}.md

set -e  # Exit on error
cd "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}"

echo "Starting file reorganization for {Case Name}..."
echo "Date: $(date)"
echo ""

# Create 8-bucket directory structure
echo "Creating directory structure..."
mkdir -p "Case Information"
mkdir -p "Client"
mkdir -p "Investigation"
mkdir -p "Medical Records"
mkdir -p "Insurance"
mkdir -p "Lien"
mkdir -p "Expenses"
mkdir -p "Negotiation Settlement"
mkdir -p "Litigation"
echo "✓ Directories created"
echo ""

# CASE INFORMATION (summaries only, NO original documents)
echo "Moving Case Information files..."
# Add mv commands here (if any)
echo ""

# CLIENT FILES
echo "Moving Client files..."
# IMPORTANT: For PDF+MD pairs, reunite scrambled .md with original PDF
# Example (scrambled .md with PDF from _pdf_originals):
# mv "doc_0001.md" "Client/YYYY-MM-DD - Client Name - Client - Originator - Description.md"
# mv "_pdf_originals/original/path/to/file.pdf" "Client/YYYY-MM-DD - Client Name - Client - Originator - Description.pdf"

# Health insurance cards (no date in filename)
# mv "insurance-front.jpg" "Client/Client Name - Client - Health Insurance Card Front.jpg"
# mv "insurance-back.jpg" "Client/Client Name - Client - Health Insurance Card Back.jpg"
echo ""

# INVESTIGATION FILES
echo "Moving Investigation files..."
# mv "doc_0002.md" "Investigation/YYYY-MM-DD - Client Name - Investigation - Originator - Description.md"
# mv "_pdf_originals/original/path/to/file.pdf" "Investigation/YYYY-MM-DD - Client Name - Investigation - Originator - Description.pdf"
echo ""

# MEDICAL RECORDS
echo "Moving Medical Records files..."
# mv "doc_0003.md" "Medical Records/YYYY-MM-DD - Client Name - Medical Record - Originator - Description.md"
# mv "_pdf_originals/original/path/to/file.pdf" "Medical Records/YYYY-MM-DD - Client Name - Medical Record - Originator - Description.pdf"
echo ""

# INSURANCE (NO demands)
echo "Moving Insurance files..."
# mv "doc_0004.md" "Insurance/YYYY-MM-DD - Client Name - Insurance - Originator - Description.md"
# mv "_pdf_originals/original/path/to/file.pdf" "Insurance/YYYY-MM-DD - Client Name - Insurance - Originator - Description.pdf"
echo ""

# LIEN
echo "Moving Lien files..."
# mv "doc_0005.md" "Lien/YYYY-MM-DD - Client Name - Lien - Originator - Description.md"
# mv "_pdf_originals/original/path/to/file.pdf" "Lien/YYYY-MM-DD - Client Name - Lien - Originator - Description.pdf"
echo ""

# EXPENSES
echo "Moving Expenses files..."
# mv "doc_0006.md" "Expenses/YYYY-MM-DD - Client Name - Expense - Originator - Description.md"
# mv "_pdf_originals/original/path/to/file.pdf" "Expenses/YYYY-MM-DD - Client Name - Expense - Originator - Description.pdf"
echo ""

# NEGOTIATION SETTLEMENT (demands, offers, settlements, releases)
echo "Moving Negotiation Settlement files..."
# mv "doc_0007.md" "Negotiation Settlement/YYYY-MM-DD - Client Name - Negotiation Settlement - Originator - Description.md"
# mv "_pdf_originals/original/path/to/file.pdf" "Negotiation Settlement/YYYY-MM-DD - Client Name - Negotiation Settlement - Originator - Description.pdf"
echo ""

# LITIGATION
echo "Moving Litigation files..."
# Discovery responses (PDF+MD pairs)
# mv "doc_0008.md" "Litigation/YYYY-MM-DD - Client Name - Litigation - Plaintiff - Plaintiff Answers IROG and RPD.md"
# mv "_pdf_originals/original/path/to/file.pdf" "Litigation/YYYY-MM-DD - Client Name - Litigation - Plaintiff - Plaintiff Answers IROG and RPD.pdf"

# Emails (both .eml and .md - NOT scrambled, these use original names)
# mv "old-email.eml" "Litigation/YYYY-MM-DD - Client Name - Litigation - BK to DC Re Discovery.eml"
# [ -f "old-email.md" ] && mv "old-email.md" "Litigation/YYYY-MM-DD - Client Name - Litigation - BK to DC Re Discovery.md"

# Court filing notices (NOT scrambled)
# mv "court-notice.eml" "Litigation/YYYY-MM-DD - Client Name - Litigation - Jefferson Circuit - Filing Confirmation Complaint.eml"
# [ -f "court-notice.md" ] && mv "court-notice.md" "Litigation/YYYY-MM-DD - Client Name - Litigation - Jefferson Circuit - Filing Confirmation Complaint.md"
echo ""

# DELETE DUPLICATES (if approved)
echo "Deleting approved duplicates..."
# For scrambled PDF+MD pairs:
# rm "doc_0099.md"
# rm "_pdf_originals/path/to/duplicate.pdf"
# For other files:
# rm "duplicate-email.eml"
# [ -f "duplicate-email.md" ] && rm "duplicate-email.md"
echo ""

# CLEANUP - Remove temporary directories
echo "Cleaning up temporary files..."
rm -rf "_pdf_originals"
rm -f "Reports/pdf_md_mapping_${case_name}.json"
echo "✓ Cleanup complete"
echo ""

echo "✅ Reorganization complete!"
echo "Completed: $(date)"

# EXPLANATION:
# [ -f "file.md" ] && mv ...
# This checks if the .md file exists before trying to move it.
# If the .md doesn't exist, it silently skips (no error).
# This ensures files and their markdown companions always have matching names.
```

### Script Generation Rules:

**1. PDF+MD Pairs (Scrambled Filenames) - MOST COMMON:**
```bash
# Step 1: Look up scrambled .md name in reorganization map (e.g., "doc_0001.md")
# Step 2: Look up PDF location in pdf_md_mapping_{case_name}.json
# Step 3: Move BOTH files to new proper names:

# Move scrambled .md to new proper name
mv "doc_0001.md" "BucketName/YYYY-MM-DD - Client - Category - Originator - Description.md"

# Move PDF from _pdf_originals to new proper name
mv "_pdf_originals/original/subfolder/original-name.pdf" "BucketName/YYYY-MM-DD - Client - Category - Originator - Description.pdf"
```

**2. Non-PDF Files (NOT Scrambled) - Images, Emails, etc.:**
```bash
# These files were NOT scrambled, use original names
mv "original-file.jpg" "BucketName/YYYY-MM-DD - Client - Category - Description.jpg"
[ -f "original-file.md" ] && mv "original-file.md" "BucketName/YYYY-MM-DD - Client - Category - Description.md"
```

**3. Email Files (.eml + .md) - NOT Scrambled:**
```bash
mv "email.eml" "Bucket/YYYY-MM-DD - Client - Category - From-To - Description.eml"
[ -f "email.md" ] && mv "email.md" "Bucket/YYYY-MM-DD - Client - Category - From-To - Description.md"
```

**4. Duplicate Deletion:**
```bash
# For scrambled PDF+MD pairs:
rm "doc_0099.md"  # Delete scrambled .md
rm "_pdf_originals/path/to/duplicate.pdf"  # Delete PDF from _pdf_originals

# For non-scrambled files:
rm "duplicate.jpg"
[ -f "duplicate.md" ] && rm "duplicate.md"
```

**5. Cleanup After Reorganization:**
```bash
# Remove temporary directories and mapping file
rm -rf "_pdf_originals"
rm -f "Reports/pdf_md_mapping_${case_name}.json"
```

**6. Group by Bucket:**
- Organize mv commands by destination folder
- Add echo statements for progress tracking
- Use comments to separate sections

**7. Error Handling:**
```bash
set -e  # Exit on error (at top of script)
```

**8. Absolute Paths:**
```bash
cd "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}"  # Use full absolute host path
```

---

## Step 3: Report Completion

After saving the script, inform the main agent:

```
Script generation complete!

Script saved to: /Tools/_generated/reorganize_{case_name}.sh

The main agent must now execute this script using the shell tool with absolute paths:

1. Main agent will read the script from virtual path: /Tools/_generated/reorganize_{case_name}.sh
2. Main agent will execute using absolute host path via shell tool
3. Execution log will be created at: /projects/{case_name}/Reports/reorganization_log_{case_name}.txt

Ready for main agent execution.
```

---

## Output File

### Bash Script: `/Tools/_generated/reorganize_{case_name}.sh`

**Location:** Virtual path (FilesystemBackend)
**Format:** Executable bash script with all file operations
**Contents:**
- Shebang: `#!/bin/bash`
- Error handling: `set -e`
- Absolute path cd command
- Directory creation (8 buckets)
- All mv commands for file moves
- All rm commands for duplicates
- Progress echo statements
- Completion message

---

## Important Notes

### File Operation Safety:

**DO:**
- ✅ Use absolute paths in cd command
- ✅ Read BOTH reorganization map AND pdf_md_mapping JSON file
- ✅ For PDF+MD pairs: Move scrambled .md AND PDF from `_pdf_originals/` to SAME proper name
- ✅ For non-PDF files: Use original filenames (NOT scrambled)
- ✅ Group commands by bucket for clarity
- ✅ Check for .md companion files with `[ -f ... ]` (for non-scrambled files only)
- ✅ Use proper quoting around filenames (handles spaces)
- ✅ Add progress echo statements
- ✅ Add cleanup commands to remove `_pdf_originals/` and mapping file
- ✅ Use `set -e` to exit on first error

**DON'T:**
- ❌ Execute mv commands one-by-one (use bash script)
- ❌ Forget to move BOTH .md AND PDF for scrambled pairs
- ❌ Forget to look up PDF location in mapping file
- ❌ Delete files without user approval
- ❌ Use relative paths (use absolute paths in cd command)
- ❌ Skip cleanup of temporary directories
- ❌ Skip error handling

### Bash Script Best Practices:

1. **Quoting:** Always quote filenames: `mv "file with spaces.pdf" "destination/new name.pdf"`
2. **Existence checks:** Use `[ -f "file" ]` before operating on optional files
3. **Comments:** Annotate sections for readability
4. **Logging:** Use echo statements for progress tracking
5. **Error handling:** Use `set -e` to stop on errors

### Why Bash Script Instead of Individual Commands:

- **Speed:** All operations execute in one batch
- **Atomic:** Either all succeed or script stops at first error
- **Reviewable:** User can review script before execution
- **Repeatable:** Can re-run if needed
- **Auditable:** Script saved for documentation
- **Undoable:** Can reverse operations if needed (with backup)

---

## Example Script Section:

**Example showing PDF+MD reunification from scrambled names:**

```bash
# MEDICAL RECORDS
echo "Moving Medical Records files..."

# Scrambled file: doc_0042.md
# From mapping.json: original PDF was at "medical_records/Baptist-Health-ER-Visit.pdf"
# New name determined by Phase 2 analysis of doc_0042.md content

# Move scrambled .md to proper name
mv "doc_0042.md" "Medical Records/2021-09-03 - Brenda Lang - Medical Records - Baptist Health Louisville - ER Visit Records.md"

# Move PDF from _pdf_originals to matching proper name
mv "_pdf_originals/medical_records/Baptist-Health-ER-Visit.pdf" "Medical Records/2021-09-03 - Brenda Lang - Medical Records - Baptist Health Louisville - ER Visit Records.pdf"

# Another example
mv "doc_0043.md" "Medical Records/2021-09-03 - Brenda Lang - Medical Records - Okolona Fire Protection District - Ambulance Run Sheet.md"
mv "_pdf_originals/medical_records/Okolona-Fire-Ambulance.pdf" "Medical Records/2021-09-03 - Brenda Lang - Medical Records - Okolona Fire Protection District - Ambulance Run Sheet.pdf"

echo "✓ Medical Records files moved"

# LITIGATION
echo "Moving Litigation files..."

# Scrambled PDF+MD pair
mv "doc_0089.md" "Litigation/2023-09-14 - Brenda Lang - Litigation - Plaintiff - Complaint for Personal Injury.md"
mv "_pdf_originals/litigation/complaint.pdf" "Litigation/2023-09-14 - Brenda Lang - Litigation - Plaintiff - Complaint for Personal Injury.pdf"

# Email (NOT scrambled - these kept original names)
mv "2025-02-07-court-filing.eml" "Litigation/2025-02-07 - Brenda Lang - Litigation - Jefferson Circuit - Filing Confirmation Complaint.eml"
[ -f "2025-02-07-court-filing.md" ] && mv "2025-02-07-court-filing.md" "Litigation/2025-02-07 - Brenda Lang - Litigation - Jefferson Circuit - Filing Confirmation Complaint.md"

echo "✓ Litigation files moved"
```

---

## Checklist Before Reporting to Main Agent

Before completing your task, verify:

- [ ] Read both `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md` AND `/projects/{case_name}/Reports/pdf_md_mapping_{case_name}.json`
- [ ] Bash script saved to `/Tools/_generated/reorganize_{case_name}.sh`
- [ ] Script has proper shebang: `#!/bin/bash`
- [ ] Script uses absolute path: `cd "/Volumes/X10 Pro/Roscoe/workspace_paralegal/projects/{case_name}"`
- [ ] Script has error handling: `set -e`
- [ ] All 8 bucket directories created via mkdir commands
- [ ] **PDF+MD pairs**: Both scrambled .md AND PDF from `_pdf_originals/` moved to same proper name
- [ ] **Non-PDF files**: Images, emails handled separately (NOT scrambled)
- [ ] Email pairs (.eml + .md) handled together with `[ -f ... ]` checks
- [ ] Duplicates deleted (both scrambled .md and PDF from `_pdf_originals/`, OR non-scrambled files)
- [ ] Cleanup commands added: `rm -rf "_pdf_originals"` and `rm -f "Reports/pdf_md_mapping_${case_name}.json"`
- [ ] Progress echo statements added
- [ ] All mv/rm commands use relative paths (after cd to case directory)

---

## What Happens Next

After you complete this sub-skill:

1. **Main agent reads** your script from `/Tools/_generated/reorganize_{case_name}.sh`
2. **Main agent executes** it using shell tool with absolute host paths
3. **Execution log** is created automatically via command redirection
4. **Phase 5** (Verification) begins after successful execution

---

**Remember:** This is file execution - be precise, be careful, use the bash script.
