# Medical Provider Duplicates - For Review

**Date:** January 2, 2026
**Total Providers:** 1,933
**Analysis Method:** Exact normalization + Fuzzy matching (85% threshold)

---

## Summary

**Detection Results:**
- **Exact Duplicates:** 4 groups (8 providers)
- **Fuzzy Similar:** 245 groups (490 providers)
- **Total Groups:** 249 groups to review

**Impact Classification:**
- **High Impact:** 37 groups (connected to active cases) - **Manual review required**
- **Low Impact:** 212 groups (not connected to cases) - **Low priority**

**Estimated TRUE Duplicates:** ~20-50 providers (most fuzzy matches are false positives)

---

## PRIORITY 1: Definite Duplicates (4 groups)

These normalize to identical strings - almost certainly duplicates.

### ✅ MERGE These (3 groups)

| Group | Providers | Cases | Recommended Action |
|-------|-----------|-------|-------------------|
| **Norton Women's and Children's** | 2 | 2 | Merge to "Norton Women's and Children's Hospital" |
| **PT Pros Physical Therapy and Sports Center** | 2 | 1 | Merge to "PT Pros Physical Therapy and Sports Center" |
| **Commonwealth Pain and Spine** | 2 | 1 | Merge to "Commonwealth Pain and Spine" |

**Total to merge:** 3 groups (6 providers → 3 providers)
**Cases affected:** 4 cases (will need relationship updates)

### ⚠️ REVIEW This (1 group)

| Group | Providers | Cases | Issue |
|-------|-----------|-------|-------|
| **Norton Children's** | Medical Center, Medical Group | 0 | Different departments? Check if same facility |

---

## PRIORITY 2: High-Impact Fuzzy Matches (34 groups, 70+ cases affected)

**Review strategy:** For each group, check if:
1. **Same address** → Likely duplicate, merge
2. **Different address** → Different locations, keep separate
3. **One is department of other** → May keep separate

### Top 10 Groups by Case Count

| # | Provider Names | Providers | Cases | Likely Duplicate? |
|---|----------------|-----------|-------|-------------------|
| 1 | Allied Chiropractic / Starlite Chiropractic | 2 | 39 | ❌ NO - Different chiropractors |
| 2 | University Of Louisville Hospital Radiology / University of Louisville Hospital | 2 | 28 | ⚠️ MAYBE - Same address, check if dept vs facility |
| 3 | Baptist Health Medical Group Primary Care (3 variants) | 3 | 4 | ⚠️ CHECK - Different addresses in group |
| 4 | Baptist Health / Baptist Healthcare | 2 | 3 | ✅ YES - Same address |
| 5 | Jewish Hospital / Jewish Hospital East | 2 | 3 | ❌ NO - Different campuses |
| 6 | Norton Community Medical Associates (7 locations) | 7 | 3 | ❌ NO - Different addresses |
| 7 | Norton Cancer/Neuroscience Institute - Brownsboro | 2 | 2 | ❌ NO - Different departments |
| 8 | UL Health Medical Center South / UofL Health Medical Center Southwest | 2 | 2 | ⚠️ MAYBE - Check addresses |
| 9 | Various "Chiropractic Center" matches | 4 | 1 | ❌ NO - Different chiropractors |
| 10 | Various "Family Medical Center" matches | 3 | 1 | ❌ NO - Different clinics |

---

## PRIORITY 3: Low-Impact Fuzzy Matches (211 groups, 0 cases)

**Not connected to any cases - low priority.**

Since these aren't connected to cases, merging them has zero impact on case data. However, many are false positives (different facilities that happen to have similar names).

**Recommended:** Leave as-is unless address matching shows they're duplicates.

---

## Detailed Reports Location

**Full data for review:**

1. **`MEDICAL_PROVIDER_DUPLICATES_FULL_REPORT.md`** (local)
   - Complete fuzzy matching analysis
   - All 245 groups with full details
   - 4,007 lines

2. **`/mnt/workspace/Reports/medical_provider_duplicates_report.md`** (VM)
   - Exact normalization only (4 groups)
   - Conservative, high-confidence duplicates

3. **`/mnt/workspace/Reports/medical_provider_fuzzy_duplicates_report.md`** (VM)
   - Fuzzy matching (245 groups)
   - Includes many false positives

---

## Decision Matrix

For each group in the reports, decide:

**✅ MERGE** - Same entity, name variation
- Same address
- Minor punctuation/capitalization difference
- One is abbreviation of the other

**⚠️ CHECK** - Need more information
- Similar names but need address comparison
- May be department vs parent facility

**❌ KEEP SEPARATE** - Different entities
- Different addresses
- Different departments (Cancer vs Neuroscience)
- Different locations (Dixie vs Preston)
- Different businesses (Allied vs Starlite)

---

## Impact Assessment

### If We Merge All Exact Duplicates (Conservative)

**Changes:**
- Remove: 3 duplicate providers
- Update: 4 case relationships
- Result: 1,930 unique providers (from 1,933)

**Risk:** MINIMAL - Only fixing obvious capitalization/punctuation differences

### If We Also Merge Likely Fuzzy Duplicates (Moderate)

**Changes:**
- Remove: ~20-30 duplicate providers
- Update: ~30-50 case relationships
- Result: ~1,903-1,913 unique providers

**Risk:** LOW - Requires address verification first

### If We Merge All Fuzzy Matches (Aggressive)

**Changes:**
- Remove: ~400+ providers
- Update: ~200+ case relationships
- Result: ~1,500 unique providers

**Risk:** HIGH - Would merge many different locations incorrectly

---

## My Recommendation

### Phase 1: Merge Exact Duplicates Only (3 groups)

**Safe and certain:**
- Norton Women's and Children's Hospital
- PT Pros Physical Therapy and Sports Center
- Commonwealth Pain and Spine

**Benefits:**
- Zero risk (these are definitely duplicates)
- Cleans up obvious issues
- Tests merge process

### Phase 2: Manual Review of Top 20 High-Impact

**Review by address:**
- Same address + similar name = merge
- Different address = keep separate
- Department relationship = decide case-by-case

**Estimated:** Find ~10-15 more true duplicates

### Phase 3: Ignore Low-Impact for Now

**Rationale:**
- Not connected to cases
- Many are false positives
- Can address later if needed

---

## Files for Your Review

✅ **`MEDICAL_PROVIDER_DUPLICATES_FULL_REPORT.md`** - Downloaded locally (4,007 lines)
- Contains all 245 fuzzy match groups
- Organized by impact (high-impact first)
- Full details for each provider

✅ **`PROVIDER_DUPLICATES_FOR_REVIEW.md`** - This summary document

**Next:** Review the reports and let me know which duplicates you want to merge. I can create a deduplication script based on your decisions.
