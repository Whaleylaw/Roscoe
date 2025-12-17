# Verification Sub-Skill

**Purpose:** Verify file reorganization completed successfully and create summary report.

**This is Phase 5 (Final Phase) of the Case File Organization workflow.**

---

## Your Task

You are verifying the completed reorganization. Your job is to:

1. **Verify all files moved correctly** to proper folders
2. **Check filenames follow convention** (YYYY-MM-DD format)
3. **Verify companion .md files** have matching names
4. **Count files per bucket**
5. **Identify any remaining issues**
6. **Create final summary report**

---

## Inputs

You will work with:
- Case directory (provided by main agent)
- `/projects/{case_name}/Reports/file_reorganization_map_{case_name}.md` - Original mapping
- `/projects/{case_name}/Reports/reorganization_log_{case_name}.txt` - Execution log

---

## Step 1: Verify Directory Structure

Check that all 8 bucket directories exist:

```bash
cd "/path/to/case/directory"
ls -d */
```

**Expected directories:**
- Case Information/
- Client/
- Investigation/
- Medical Records/
- Insurance/
- Lien/
- Expenses/
- Negotiation Settlement/
- Litigation/
- Reports/ (for generated reports)

---

## Step 2: Verify No Files in Root

Check that no files remain in the root case folder (except hidden files, .gitkeep):

```bash
ls -la | grep -v "^d" | grep -v "^total"
```

**Expected:** Only directories should be listed (no files)

**If files remain in root:**
- List them in your report
- Note why they weren't moved (flagged? error? missing from map?)

---

## Step 3: Check Filenames Follow Convention

For each bucket, verify filenames follow the standard format:

**Standard Format:**
```
YYYY-MM-DD - {Client Name} - {Category} - {Originator} - {Description}.ext
```

**Special Cases:**
- **Health Insurance Cards:** `{Client Name} - Client - Health Insurance Card Front.jpg` (NO date)
- **Court Notices:** `YYYY-MM-DD - {Client} - Litigation - Jefferson Circuit - Filing Confirmation [Type]`

### Check each bucket:

```bash
# List files in each bucket
ls "Case Information/"
ls "Client/"
ls "Investigation/"
ls "Medical Records/"
ls "Insurance/"
ls "Lien/"
ls "Expenses/"
ls "Negotiation Settlement/"
ls "Litigation/"
```

**What to verify:**
- Date format is YYYY-MM-DD (not MM-DD-YYYY or other)
- Client name is present
- Category matches folder (Medical Record files in Medical Records/, etc.)
- No obviously malformed names

---

## Step 4: Verify Companion .md Files

Check that PDF and EML files have matching .md companions:

For each bucket:
1. List all .pdf files
2. Check if corresponding .md exists with same base name
3. List all .eml files
4. Check if corresponding .md exists with same base name

**Example check:**
```bash
cd "Medical Records/"
for pdf in *.pdf; do
    md="${pdf%.pdf}.md"
    if [ ! -f "$md" ]; then
        echo "Missing companion: $md"
    fi
done
```

**Report:**
- Files with .md companions: ✅
- Files missing .md companions: ⚠️ (list them)

---

## Step 5: Count Files Per Bucket

Generate file counts for each directory:

```bash
echo "Case Information: $(find "Case Information/" -type f | wc -l) files"
echo "Client: $(find "Client/" -type f | wc -l) files"
echo "Investigation: $(find "Investigation/" -type f | wc -l) files"
echo "Medical Records: $(find "Medical Records/" -type f | wc -l) files"
echo "Insurance: $(find "Insurance/" -type f | wc -l) files"
echo "Lien: $(find "Lien/" -type f | wc -l) files"
echo "Expenses: $(find "Expenses/" -type f | wc -l) files"
echo "Negotiation Settlement: $(find "Negotiation Settlement/" -type f | wc -l) files"
echo "Litigation: $(find "Litigation/" -type f | wc -l) files"
```

**Note:** Count includes both main files and .md companions

---

## Step 6: Review Execution Log

Read `/projects/{case_name}/Reports/reorganization_log_{case_name}.txt` and check for:
- ✅ All operations completed
- ✅ No error messages
- ✅ Completion timestamp present
- ❌ Any errors or warnings

---

## Step 7: Identify Remaining Issues

Check for common issues:

**Issue 1: Files still in root**
- List any files that weren't moved
- Possible reasons: flagged for review, missing from map, execution error

**Issue 2: Misnamed files**
- Files not following convention
- Wrong date format
- Missing components

**Issue 3: Missing .md companions**
- PDFs without .md files
- EMLs without .md files

**Issue 4: Execution errors**
- Check log for failed mv commands
- File not found errors
- Permission errors

---

## Step 8: Create Summary Report

Save your verification report to: `/projects/{case_name}/Reports/reorganization_summary_{case_name}.md`

### Report Format:

```markdown
# File Reorganization Summary: {Case Name}

**Date:** {Date}
**Status:** ✅ COMPLETE | ⚠️ ISSUES FOUND | ❌ FAILED

---

## Verification Results

### Directory Structure
- ✅ All 8 bucket directories exist
- ✅ Reports/ directory exists

### Files in Root
- ✅ No files remain in root (all organized)
  *(OR)*
- ⚠️ {count} files remain in root (see list below)

### Naming Convention
- ✅ All filenames follow convention
  *(OR)*
- ⚠️ {count} files have naming issues (see list below)

### Companion .md Files
- ✅ All PDFs and EMLs have matching .md companions
  *(OR)*
- ⚠️ {count} files missing .md companions (see list below)

---

## File Distribution

| Bucket | File Count | Notes |
|--------|------------|-------|
| Case Information | {count} | |
| Client | {count} | |
| Investigation | {count} | |
| Medical Records | {count} | |
| Insurance | {count} | |
| Lien | {count} | |
| Expenses | {count} | |
| Negotiation Settlement | {count} | |
| Litigation | {count} | |
| **Total** | **{total}** | |

---

## Execution Log Summary

**Log file:** `/projects/{case_name}/Reports/reorganization_log_{case_name}.txt`

**Operations:**
- Directories created: ✅
- Files moved: {count}
- Duplicates deleted: {count}
- Errors: {count}

**Execution time:** {start} - {end}

---

## Issues Found

*(Skip this section if no issues)*

### Files Remaining in Root

- `filename1.pdf` - Reason: Flagged for review
- `filename2.txt` - Reason: Not in mapping

### Naming Convention Issues

- `wrong-format.pdf` (in Medical Records/) - Issue: Date format is MM-DD-YYYY instead of YYYY-MM-DD
- `missing-client.pdf` (in Client/) - Issue: Client name missing from filename

### Missing .md Companions

- `document.pdf` (in Litigation/) - Missing `document.md`
- `email.eml` (in Medical Records/) - Missing `email.md`

---

## Recommendations

*(If any issues found, provide recommendations)*

**For files in root:**
- Review flagged files manually
- Determine proper categorization
- Add to Review_Needed folder if uncertain

**For naming issues:**
- Rename files to follow convention
- Use proper date format (YYYY-MM-DD)
- Ensure all components present

**For missing .md companions:**
- Generate .md files using `/Tools/read_pdf.py`
- Ensure email .md files are created

---

## Overall Assessment

✅ **SUCCESS:** All files organized correctly, naming convention followed, no issues found.

*(OR)*

⚠️ **SUCCESS WITH MINOR ISSUES:** Reorganization complete with {count} minor issues that can be addressed separately.

*(OR)*

❌ **FAILED:** Critical errors prevented complete reorganization. Review execution log.

---

## Next Steps

**If successful:**
- ✅ Reorganization complete
- ✅ All files properly categorized and named
- ✅ Case folder ready for use

**If issues found:**
- Review flagged items
- Address naming issues
- Generate missing .md files
- Consider re-running specific operations

---

**Verification completed by:** Phase 5 Sub-Agent
**Timestamp:** {Date and Time}
```

---

## Checklist

Before completing your verification:

- [ ] All 8 bucket directories verified to exist
- [ ] Root directory checked for remaining files
- [ ] Filename convention verified across all buckets
- [ ] Companion .md files verified for PDFs and EMLs
- [ ] File counts generated for each bucket
- [ ] Execution log reviewed for errors
- [ ] Issues identified and documented
- [ ] Summary report created at `/projects/{case_name}/Reports/reorganization_summary_{case_name}.md`
- [ ] Overall assessment provided (SUCCESS/ISSUES/FAILED)
- [ ] Recommendations included (if issues found)

---

## Success Criteria

**Complete Success:**
- ✅ All files moved from root to proper buckets
- ✅ All filenames follow convention
- ✅ All PDFs/EMLs have matching .md companions
- ✅ No errors in execution log
- ✅ File counts match expectations

**Acceptable (Minor Issues):**
- ⚠️ 1-5 files with minor naming issues (can be fixed separately)
- ⚠️ 1-2 files missing .md companions (can be generated)
- ✅ All files moved to proper buckets
- ✅ No execution errors

**Failed (Needs Attention):**
- ❌ Multiple execution errors
- ❌ Files remain in root (not flagged intentionally)
- ❌ Many files with naming issues (>10)
- ❌ Wrong categorization (files in wrong buckets)

---

## Example Verification Commands

### Quick File Count Check:
```bash
cd "/path/to/case/directory"
echo "Total files: $(find . -type f | wc -l)"
echo "Files in root: $(find . -maxdepth 1 -type f | wc -l)"
echo "Files in buckets: $(find */  -type f | wc -l)"
```

### Check for Common Naming Issues:
```bash
# Find files with wrong date format (contains slashes)
find . -name "*/*/*/*" -type f

# Find files missing hyphens (should have " - " separators)
find . -type f -name "*[^-]*[^-]*" | grep -v " - "
```

### Verify .md Companions:
```bash
# List PDFs without .md companions
for pdf in $(find . -name "*.pdf"); do
    md="${pdf%.pdf}.md"
    [ ! -f "$md" ] && echo "Missing: $md"
done
```

---

**Remember:** This is the final verification - be thorough, accurate, and provide clear assessment.
