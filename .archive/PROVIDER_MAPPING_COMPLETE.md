# Provider Mapping Documents - COMPLETE ✅

**Date:** January 2, 2026
**Purpose:** Side-by-side comparison of old providers (case data) vs new providers (official rosters)

---

## Files Generated

### Location: `/Volumes/X10 Pro/Roscoe/provider-mappings/`

**5 Mapping Documents (one per health system):**

1. **`NORTON_MAPPING.md`**
   - 20 old Norton providers
   - 368 new Norton locations from official roster
   - Top 5 matches shown for each old provider

2. **`UOFL_MAPPING.md`**
   - 15 old UofL/Jewish providers
   - 345 new UofL Health locations
   - Includes Jewish Hospital, Mary & Elizabeth, UofL Physicians

3. **`BAPTIST_MAPPING.md`**
   - 23 old Baptist providers
   - 467 new Baptist Health locations
   - Includes Baptist Louisville, Lexington, Medical Groups

4. **`CHI_MAPPING.md`**
   - 7 old CHI/St. Joseph providers
   - 152 new CHI Saint Joseph Health locations
   - Includes Flaget, St. Joseph East

5. **`STELIZABETH_MAPPING.md`**
   - 6 old St. Elizabeth providers
   - 419 new St. Elizabeth Healthcare locations
   - Includes Edgewood, Florence, Ft. Thomas hospitals

**Summary:**
- **`_MAPPING_SUMMARY.md`** - Overview of all 5 systems

---

## Document Format

Each mapping document shows:

```markdown
## X. OLD: [Provider Name]

**Entries:** [Number of times appears in case data]
**Cases ([Count]):**
- Case 1
- Case 2
...
**Total Billed:** $X,XXX.XX

**Top 5 Matches from New Roster:**

1. **[New Provider Name]** ([Score]% match)
   - Address: [Full Address]
   - Phone: [Phone Number]
   - Match breakdown: Ratio=X%, Partial=Y%, TokenSort=Z%

2. [Next best match...]

**DECISION:**
- [ ] REPLACE with match #___ (specify which one above)
- [ ] KEEP OLD (no good match)
- [ ] DELETE (duplicate)

**Notes:**
```

---

## Statistics

### Total Providers to Review

| Health System | Old Providers | New Roster Size | Mapping Required |
|---------------|---------------|-----------------|------------------|
| **Norton Healthcare** | 20 | 368 | ✓ |
| **UofL Health** | 15 | 345 | ✓ |
| **Baptist Health** | 23 | 467 | ✓ |
| **CHI Saint Joseph** | 7 | 152 | ✓ |
| **St. Elizabeth** | 6 | 419 | ✓ |
| **TOTAL** | **71** | **1,751** | **5 files** |

**Total cases affected:** ~60-80 cases (if all 71 providers replaced)

---

## Matching Quality Examples

### Perfect Matches (100% - Same Facility)

**Norton Audubon Hospital:**
- OLD: "Norton Audubon Hospital" (9 cases, $345K billed)
- NEW: "Norton Audubon Hospital" (exact match!)
- Address: 1 Audubon Plaza Drive (same)
- **Recommendation:** REPLACE with match #1

**Norton Community Medical Associates - Preston:**
- OLD: "Norton Community Medical Associates - Preston" (2 cases)
- NEW: "Norton Community Medical Associates - Preston" (100% match)
- Address: 7430 Jefferson Boulevard (same)
- **Recommendation:** REPLACE with match #1

**Norton Women's and Children's Hospital:**
- OLD: "Norton Women's and Children's Hospital" (2 cases)
- NEW: "Norton Women's and Children's Hospital" (100% match)
- Address: 4001 Dutchmans Lane (same)
- **Recommendation:** REPLACE with match #2

### Good Matches (90%+ - Likely Same Facility)

**Norton Brownsboro Hospital:**
- OLD: "Norton Brownsboro Hospital" (3 cases, $287K)
- NEW: "Norton Brownsboro Hospital" (100% match) or "Norton Brownsboro Hospital - Emergency"
- Address: 4960 Norton Healthcare Blvd (same)
- **Recommendation:** REPLACE with match #1 (main hospital) or #3 (emergency dept)

**Norton Leatherman Spine:**
- OLD: "Norton Leatherman Spine" (2 cases)
- NEW: Multiple Norton Leatherman Spine locations (St. Matthews, Angies Way, Downtown, Elizabethtown)
- **Recommendation:** Review addresses to pick correct location

### Questionable Matches (<85% - Review Needed)

**Norton Hospital Downtown:**
- OLD: "Norton Hospital Downtown" (3 cases, $130K)
- NEW: "Norton Hospital" (100% match) but different specificity
- Address: 200 E Chestnut (same)
- **Recommendation:** REPLACE with match #2 (Norton Hospital - exact match on address)

**Norton Neurology Services-Downtown:**
- OLD: "Norton Neurology Services-Downtown" (3 cases)
- NEW: Best match is "Norton Neuroscience Institute - Neurology - Downtown" (73%)
- **Recommendation:** REVIEW - May be correct match despite lower score

---

## Decision Guide

### ✅ REPLACE - Use When:

- **Same address** (most important indicator!)
- Match score 100% with exact or near-exact name
- New provider has more complete info (phone, address details)
- Old name is generic, new is specific department

**Example:**
- OLD: "Norton Audubon Hospital"
- NEW: "Norton Audubon Hospital" (same address) → **REPLACE**

### ⚠️ KEEP OLD - Use When:

- **Different address** than all suggested matches
- Old provider is independent clinic (not actually part of this health system)
- No good match found (all scores <70%)
- Need to preserve old provider for historical accuracy

**Example:**
- OLD: "Norton Hospital Downtown"
- NEW: Best match is "Norton Pharmacy - Downtown" (different department) → **KEEP OLD** (or find better match)

### 🗑️ DELETE - Use When:

- Old provider is duplicate of another old provider
- Misspelled or data entry error
- Can be merged with another old provider
- Not actually used (0 cases)

**Example:**
- OLD: "Norton Women's & Children's Hospital" (apostrophe)
- ALSO: "Norton Women's and Children's Hospital" (no apostrophe)
- One should be deleted (duplicate)

---

## High-Confidence Replacements (Same Address)

Based on the Norton mapping, here are clear replacements:

### Exact Matches (Address + Name)

1. **Norton Audubon Hospital** → Norton Audubon Hospital (match #1)
2. **Norton Brownsboro Hospital** → Norton Brownsboro Hospital (match #1)
3. **Norton Community Medical Associates - Preston** → Same (match #1)
4. **Norton Community Medical Associates - Dixie** → Same (match #1)
5. **Norton Orthopedic Institute - Audubon** → Same (match #1)
6. **Norton Women's and Children's Hospital** → Same (match #2)

**Similar pattern expected for other systems (UofL, Baptist, CHI, St. Elizabeth)**

---

## Workflow

### Step 1: Review Each Mapping File

**Start with Norton (20 providers):**
- Open `NORTON_MAPPING.md`
- For each old provider:
  - Compare addresses with top matches
  - If address matches → REPLACE
  - If no address match → KEEP OLD or review further
  - Mark decision in checkbox

### Step 2: Repeat for Other Systems

- `UOFL_MAPPING.md` (15 providers)
- `BAPTIST_MAPPING.md` (23 providers)
- `CHI_MAPPING.md` (7 providers)
- `STELIZABETH_MAPPING.md` (6 providers)

### Step 3: Return Marked Files

Once you've marked all decisions, I'll create a script to:
1. Read your marked decisions
2. Update case relationships (OLD provider → NEW provider)
3. Delete OLD providers (if marked for deletion)
4. Generate verification report

---

## Impact Assessment

### Conservative (Only Perfect Matches)

**If you replace ~30-40 providers with 100% name + address matches:**
- Cases affected: ~40-50
- Risk: MINIMAL (these are clearly the same facilities)
- Benefit: Better data (complete addresses, phones, parent system links)

### Moderate (90%+ Matches with Same Address)

**If you also replace ~20-30 providers with 90%+ match + same address:**
- Cases affected: ~60-70 total
- Risk: LOW (verified by address matching)
- Benefit: Comprehensive upgrade to official roster data

### Aggressive (All 71 Providers)

**If you replace all old providers:**
- Cases affected: ~80-100
- Risk: MEDIUM (some false matches possible)
- Benefit: Complete migration to official rosters

---

## Recommended Approach

**Phase 1: Auto-Replace Perfect Matches**
- 100% match + same address
- Estimated: ~20-30 providers
- No manual review needed
- Can script this automatically

**Phase 2: Manual Review of Good Matches**
- 90%+ match but need to verify correct location
- Estimated: ~20-30 providers
- Review addresses in mapping docs
- Mark decisions

**Phase 3: Keep or Delete Questionable**
- <90% match or no good match
- Estimated: ~20 providers
- Decide if independent (keep) or duplicate (delete)

---

## Next Steps

1. **Review the 5 mapping files** (total: 71 old providers)
2. **Mark your decisions** in each file
3. **Return marked files** or let me know which to auto-replace
4. **I'll create replacement script** based on your decisions

---

## Files Ready for Your Review

✅ **`provider-mappings/NORTON_MAPPING.md`** (20 providers)
✅ **`provider-mappings/UOFL_MAPPING.md`** (15 providers)
✅ **`provider-mappings/BAPTIST_MAPPING.md`** (23 providers)
✅ **`provider-mappings/CHI_MAPPING.md`** (7 providers)
✅ **`provider-mappings/STELIZABETH_MAPPING.md`** (6 providers)

**All providers from the 5 major health systems are documented side-by-side with their official roster matches!**
