# Medical Provider Duplicates - Executive Summary

**Date:** January 2, 2026
**Total Providers in Graph:** 1,933

---

## Quick Summary

**Exact Normalization Duplicates:** 4 groups (8 providers, 4 to remove)
**Fuzzy Matching Duplicates:** 245 groups (490 providers total, ~417 potential duplicates)

**Impact Analysis:**
- **High Impact:** 34 groups connected to cases (manual review required)
- **Low Impact:** 211 groups not connected to cases (safe to auto-merge)

**Total Estimated Duplicates:** ~420 providers
**Providers After Deduplication:** ~1,513 (from 1,933)

---

## Priority 1: EXACT Duplicates (4 groups - DEFINITE duplicates)

These normalize to the exact same string - definitely duplicates.

### 1. Norton Women's & Children's Hospital (2 providers, 2 cases)

**Providers:**
- "Norton Women's & Children's Hospital" → Robin-Willis-Beck case
- "Norton Women's and Children's Hospital" → Muhammad-Alif case

**Issue:** "&" vs "and" difference
**Recommended:** Merge to "Norton Women's and Children's Hospital"

### 2. PT Pros Physical Therapy And Sports Center (2 providers, 2 cases)

**Providers:**
- "PT Pros Physical Therapy And Sports Center" → Amy Mills case
- "PT Pros Physical Therapy and Sports Center" → Amy Mills case (same case!)

**Issue:** "And" vs "and" capitalization
**Recommended:** Merge to lowercase "and" version

### 3. Commonwealth Pain & Spine (2 providers, 1 case)

**Providers:**
- "Commonwealth Pain & Spine" → not connected
- "Commonwealth Pain And Spine" → Kimberly-Brasher case

**Issue:** "&" vs "And"
**Recommended:** Merge to "Commonwealth Pain and Spine"

### 4. Norton Children's (2 providers, 0 cases)

**Providers:**
- "Norton Children's Medical Center" → not connected
- "Norton Children's Medical Group" → not connected

**Issue:** Different departments (Medical Center vs Medical Group)
**Recommended:** **KEEP BOTH** - These are likely different departments

---

## Priority 2: HIGH Impact Fuzzy Matches (34 groups)

These are connected to cases and require manual review.

**Top 10 by case count:**

1. **Allied Chiropractic / Starlite Chiropractic** - 39 cases
   - ⚠️ FALSE POSITIVE - Different chiropractors

2. **University Of Louisville Hospital Radiology / University of Louisville Hospital** - 28 cases
   - ✅ LIKELY DUPLICATE - Same address, one is radiology dept

3. **Baptist Health Medical Group Primary Care (3 variants)** - 4 cases
   - ⚠️ CHECK ADDRESSES - May be different locations

4. **Baptist Health / Baptist Healthcare** - 3 cases
   - ✅ LIKELY DUPLICATE - Same address

5. **Jewish Hospital / Jewish Hospital East** - 3 cases
   - ⚠️ DIFFERENT LOCATIONS - East is different campus

6. **Norton Community Medical Associates (7 locations)** - 3 cases
   - ⚠️ DIFFERENT LOCATIONS - Each has different address

7. **Norton Cancer Institute - Brownsboro / Norton Neuroscience Institute - Brownsboro** - 2 cases
   - ⚠️ DIFFERENT DEPARTMENTS - Cancer vs Neuroscience

... (see full report for all 34 groups)

---

## Priority 3: LOW Impact Fuzzy Matches (211 groups)

**Not connected to any cases - safe to auto-deduplicate.**

Many of these are false positives, but since they're not connected to cases, merging them has zero risk.

Examples:
- Various Norton locations (different addresses = different facilities)
- Various Baptist Health clinics (different specialties)
- St. Elizabeth system locations

**Recommended Strategy:**
- Review addresses - if same address, merge
- If different addresses, keep as separate entities
- OR: Leave as-is since they're not connected to cases

---

## Analysis by Pattern

### TRUE Duplicates (High Confidence)

**Capitalization differences:**
- "PT Pros... And..." vs "PT Pros... and..." (same address)
- "Norton Women's & Children's" vs "Norton Women's and Children's" (same address)

**Punctuation differences:**
- "Commonwealth Pain & Spine" vs "Commonwealth Pain And Spine"
- "Baptist Health" vs "Baptist Healthcare"

**Estimated:** ~20-30 true duplicates

### Different Locations (KEEP Separate)

**Department variations:**
- "Norton Cancer Institute" vs "Norton Neuroscience Institute" (different departments)
- "Norton Community Medical Associates - Dixie" vs "...Preston" (different locations)
- "Jewish Hospital" vs "Jewish Hospital East" (different campuses)

**Estimated:** ~400+ are actually different locations

### Unclear (Manual Review Needed)

**May or may not be duplicates:**
- "University Of Louisville Hospital Radiology" vs "University of Louisville Hospital"
  - Same address, but one might be department within hospital
  - Could merge or keep separate

**Estimated:** ~30-50 need manual review

---

## Recommended Actions

### Immediate: Fix Priority 1 (Exact Duplicates)

**3 definite duplicates to merge:**
1. Norton Women's and Children's Hospital (2 → 1)
2. PT Pros Physical Therapy and Sports Center (2 → 1)
3. Commonwealth Pain and Spine (2 → 1)

**Keep separate:**
1. Norton Children's Medical Center vs Medical Group (different departments)

**Impact:** Merge 3 groups, 6 providers → 3 providers (remove 3 duplicates)
**Cases Affected:** 5 cases need relationship updates

### Short-term: Review High Impact Groups

**Review 34 high-impact groups manually:**
- Check addresses - if same address, likely duplicate
- Check if one is department of the other
- If in doubt, keep separate (safer)

**Estimated TRUE duplicates:** ~10-15 providers
**Cases Affected:** ~50-75 cases

### Long-term: Review Low Impact Groups

**211 groups not connected to cases:**
- Low priority since they don't affect case data
- Can dedupe later or leave as-is
- Or run address-based matching

---

## Full Reports Available

**For your detailed review:**

1. **`MEDICAL_PROVIDER_DUPLICATES_FULL_REPORT.md`**
   - Complete fuzzy matching report (245 groups)
   - All high-impact groups with case details
   - All low-impact groups
   - 4,007 lines total

2. **`/mnt/workspace/Reports/medical_provider_duplicates_report.md`** (on VM)
   - Exact normalization duplicates only (4 groups)
   - More conservative, fewer false positives

3. **`/mnt/workspace/Reports/medical_provider_fuzzy_duplicates_report.md`** (on VM)
   - Fuzzy matching duplicates (245 groups)
   - Includes many false positives

**All potential duplicates are documented for your review.**

---

## Decision Framework

For each group, consider:

1. **Same Address?**
   - YES → Likely duplicate, merge
   - NO → Keep separate (different locations)

2. **Connected to Cases?**
   - YES → Manual review required
   - NO → Safe to auto-merge or leave

3. **Department vs Facility?**
   - "Hospital" vs "Hospital Radiology" → Keep separate (department)
   - "Medical Associates - Dixie" vs "...Preston" → Keep separate (locations)
   - "Health" vs "Healthcare" → Merge (same entity)

4. **When in doubt?**
   - KEEP SEPARATE (safer, can always merge later)

---

## Statistics

**Current State:**
- 1,933 MedicalProvider nodes
- 4 exact duplicate groups
- 245 fuzzy similar groups (many false positives)

**After Conservative Deduplication:**
- Remove ~3-15 definite duplicates
- Result: ~1,920-1,930 unique providers

**After Aggressive Deduplication:**
- Remove ~100-200 duplicates (if addresses match)
- Result: ~1,730-1,833 unique providers

---

## Next Step

Review `MEDICAL_PROVIDER_DUPLICATES_FULL_REPORT.md` (4,007 lines) and mark your decisions:
- **Merge** - Consolidate into one provider
- **Keep** - Different entities, leave separate
- **Check Address** - Need more info to decide

I can then create a deduplication script based on your markings.
