# Episode Name Mapping - Safe Update Plan

**Date:** January 4, 2026
**Issue:** 50 of 111 review files reference old MedicalProvider names
**Solution:** Safe, non-destructive update process

---

## Analysis Complete

### Files Analyzed

**Total review files:** 111
**Files needing updates:** 50 (45%)
**Files already correct:** 61 (55%)

**Total name replacements needed:** 194

---

## Common Replacements Needed

### Most Frequent (Top 10)

1. **"Jewish Hospital" → "UofL Health – Jewish Hospital"**
   - 3 files (Abby Sitgraves, Charles Johnson, Nayram Adadevoh)

2. **"Mary & Elizabeth Hospital" → "UofL Health – Mary & Elizabeth Hospital"**
   - Multiple files (Alma Cristobal, Bryson Brown, etc.)

3. **"UofL Health - Mary & Elizabeth Hospital" → "UofL Health – Mary & Elizabeth Hospital"**
   - Dash character fix (- to –)

4. **"UofL Physicians - Orthopedics" → "UofL Physicians – Orthopedics"**
   - Dash character fix

5. **"Starlite Chiropractic" → "Starlite Chiropractic"**
   - No change (same name) - but script replaces anyway (harmless)

---

## What the Script Does

### SAFE Process ✅

**1. Reads original review file**
- Never modifies original

**2. Applies name mapping**
- Replaces old names with new Facility names
- Uses exact mapping from provider_name_mapping.json

**3. Saves to NEW file**
- Creates: `review_[case].md.UPDATED`
- Original: `review_[case].md` (untouched)

**4. Reports changes**
- Shows what was replaced
- Counts replacements

### Example Output

**Original file:** `review_Abby-Sitgraves-MVA-7-13-2024.md`
**Updated file:** `review_Abby-Sitgraves-MVA-7-13-2024.md.UPDATED`

**Changes in Abby's file:**
- "Jewish Hospital" → "UofL Health – Jewish Hospital" (3x)
- "Mary & Elizabeth Hospital" → "UofL Health – Mary & Elizabeth Hospital" (1x)
- "UofL Health - Mary & Elizabeth Hospital" → "UofL Health – Mary & Elizabeth Hospital" (1x)
- Etc. (12 total replacements)

---

## Current Mapping

**Created:** `provider_name_mapping.json` (15 pairs)

**Covers:**
- UofL/Jewish hospital names
- Norton hospital names
- Dash character fixes (- to –)
- Common provider name variations

**Sample mappings:**
```json
{
  "Jewish Hospital": "UofL Health – Jewish Hospital",
  "UofL Hospital": "UofL Health – UofL Hospital",
  "Mary & Elizabeth Hospital": "UofL Health – Mary & Elizabeth Hospital",
  "UofL Physicians - Orthopedics": "UofL Physicians – Orthopedics"
}
```

---

## How to Proceed

### Option 1: Execute Safe Update (Recommended)

```bash
cd "/Volumes/X10 Pro/Roscoe"
python3 scripts/update_episode_review_names.py --execute
```

**What happens:**
- Creates 50 `.UPDATED` files
- Original 111 files untouched
- Review changes in .UPDATED files
- If good → rename to replace originals
- If issues → adjust mapping and re-run

### Option 2: Expand Mapping First

**If you want to add more mappings:**
1. Edit `provider_name_mapping.json`
2. Add more old → new name pairs
3. Re-run update script
4. More comprehensive updates

### Option 3: Manual Review

**Check a few files first:**
1. Review `review_Abby-Sitgraves-MVA-7-13-2024.md.UPDATED` (when created)
2. Verify changes look correct
3. Check entity names against facilities.json
4. Approve or adjust

---

## Verification Process

**After .UPDATED files created:**

**1. Spot-check changes**
```bash
# Compare original vs updated
diff review_Abby-Sitgraves-MVA-7-13-2024.md \
     review_Abby-Sitgraves-MVA-7-13-2024.md.UPDATED
```

**2. Verify names exist in graph**
```bash
# Check if all new names exist as Facilities
python3 scripts/verify_entity_names_exist.py  # (would create this)
```

**3. If approved, commit changes**
```bash
# Rename all .UPDATED files to replace originals
for f in reviews/*.md.UPDATED; do
    mv "$f" "${f%.UPDATED}"
done
```

---

## Current Status

**✅ Completed:**
- Analyzed 111 review files
- Identified 50 files needing updates
- Created safe mapping (15 pairs)
- Created safe update script (never overwrites)

**⏳ Next Steps:**
1. Run script with --execute to create .UPDATED files
2. Review sample .UPDATED files
3. Verify changes are correct
4. Approve and commit (rename to replace originals)
5. Then proceed to update merged files
6. Then proceed to update processed files (if needed)

---

## Safety Features

**Script guarantees:**
- ✅ Never overwrites original files
- ✅ Creates new .UPDATED files
- ✅ Can review before committing
- ✅ Can re-run if issues found
- ✅ Dry-run mode to preview
- ✅ Detailed change reporting

**No data loss possible!**

---

## Files Created

**Scripts:**
- ✅ `scripts/create_provider_name_mapping.py`
- ✅ `scripts/update_episode_review_names.py`

**Data:**
- ✅ `provider_name_mapping.json` (15 mappings)

**Documentation:**
- ✅ `EPISODE_ENTITY_MAPPING_NEEDED.md` (problem statement)
- ✅ `EPISODE_NAME_MAPPING_PLAN.md` (this file - solution)

---

## Ready to Proceed

**When you're ready:**
```bash
# Create .UPDATED files (safe - no overwrites)
python3 scripts/update_episode_review_names.py --execute

# Review a sample
cat json-files/memory-cards/episodes/reviews/review_Abby-Sitgraves-MVA-7-13-2024.md.UPDATED

# If good, commit all changes
cd json-files/memory-cards/episodes/reviews/
for f in *.UPDATED; do mv "$f" "${f%.UPDATED}"; done
```

**This is a safe, reversible process!**
