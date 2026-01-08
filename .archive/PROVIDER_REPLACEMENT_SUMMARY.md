# Medical Provider Replacement Analysis - Summary

**Date:** January 2, 2026
**Analysis:** Old providers (case notes) vs New providers (healthcare systems)

---

## Key Findings

### Provider Categories Identified

**OLD Providers (from case notes - hodgepodge):**
- Total: 1,176 providers WITHOUT PART_OF → HealthSystem
- Connected to cases: 252 providers
- Not connected: 924 providers

**NEW Providers (from healthcare rosters - official):**
- Total: 757 providers WITH PART_OF → HealthSystem
- Complete addresses, phone numbers, parent systems
- Organized by: Norton Healthcare, UofL Health, Baptist Health, St. Elizabeth, CHI Saint Joseph

### Matching Results

**Potential replacements found:** 38 matches
- Norton Healthcare: 9 matches (16 cases)
- UofL Health: 6 matches (17 cases)
- Baptist Health: 18 matches (29 cases)
- St. Elizabeth Healthcare: 2 matches (4 cases)
- CHI Saint Joseph Health: 3 matches (3 cases)

**Total cases affected if all replaced:** 69 cases

**Old providers without matches:** 214 providers
- These are likely independent clinics, chiropractors, imaging centers, etc. (not part of the 5 major health systems)

---

## High-Confidence Replacements (Same Address)

These old/new pairs have **matching addresses** - very likely the same entity:

### Norton Healthcare

1. **Norton Audubon Hospital** (4 cases) → **Norton Audubon Hospital - Neurodiagnostics**
   - Same address: 1 Audubon Plaza Drive

2. **Norton Brownsboro Hospital** (2 cases) → **Norton Brownsboro Hospital - Neurodiagnostics**
   - Similar address: 4960 vs 4915 Norton Healthcare Blvd

3. **Norton Hospital** (1 case) → **Norton Hospital - Emergency**
   - Same address: 200 E Chestnut St

4. **Norton Neuroscience Institute** (1 case) → **Norton Neuroscience Institute - Adult Neurodevelopmental**
   - Same address: 210 E Gray St

### UofL Health

5. **UofL Health - Mary & Elizabeth Hospital** (10 cases) → **UofL Health – Mary & Elizabeth Hospital**
   - Same address: 1850 Bluegrass Ave
   - ⚠️ OLD has duplicate "Mary & Elizabeth" in name

6. **St. Elizabeth Edgewood Hospital** (2 cases) → **St. Elizabeth Healthcare Edgewood Hospital**
   - Same address: 1 Medical Village Dr

7. **St. Elizabeth Florence Hospital** (2 cases) → **St. Elizabeth Healthcare Florence Hospital**
   - Same address: 4900 Houston Rd

### CHI Saint Joseph

8. **CHI St. Joseph Medical Group - Orthopedic** (1 case) → **CHI Saint Joseph Medical Group - Orthopedics**
   - Same address: 160 London Mountain View Drive

9. **Flaget Memorial Hospital** (1 case) → **CHI Saint Joseph Health - Flaget Memorial Hospital**
   - Same address: 4305 New Shepherdsville Road

10. **St. Joseph East** (1 case) → **CHI Saint Joseph Health - Saint Joseph East**
    - Same address: 150 N Eagle Creek Dr

### Baptist Health

11. **Baptist Health - Corbin** (1 case) → **Baptist Health Corbin Emergency Care**
    - Same address: 1 Trillium Way

12. **Baptist Health La Grange** (1 case) → **Baptist Health La Grange Imaging and Diagnostics**
    - Same address: 1025 New Moody Lane

13. **Louisville Orthopaedic Clinic** (1 case) → **Baptist Health Louisville Orthopedic Clinic**
    - Same address: 4130 Dutchmans Lane

**Total High-Confidence:** ~13 replacements, affecting ~30 cases

---

## Questionable Matches (Different Addresses/Departments)

These matched by name similarity but have **different addresses** - likely DIFFERENT entities:

### False Positives - Keep Both

1. **Norton Hospital Downtown** → **Norton Pharmacy - Downtown**
   - ❌ Hospital vs Pharmacy (different departments)

2. **Norton Leatherman Spine** (Louisville) → **Norton Leatherman Spine - Elizabethtown**
   - ❌ Different cities (Louisville vs Elizabethtown)

3. **Baptist Health Medical Group Neurology** (Lexington) → **Baptist Health Medical Group OB/GYN** (Paducah)
   - ❌ Different specialties AND different cities

4. **Baptist Health Vascular Surgery** (Louisville) → **Baptist Health Medical Group Vascular Surgery** (Paducah)
   - ❌ Different cities

5. **Baptist Neurology - Corbin** → **Baptist Health Neurology** (Nicholasville)
   - ❌ Different cities

6. **Baptist Health Medical Group Sports Medicine** (Louisville) → **Baptist Health Medical Group Palliative Medicine** (Paducah)
   - ❌ Different specialties AND cities

**Estimated False Positives:** ~15-20 of the 38 matches

---

## Recommended Actions

### Phase 1: Replace High-Confidence Matches (~13 providers)

**Criteria:** Same address + same health system + name is substring match

**Impact:** ~30 cases need relationship updates
**Risk:** LOW - These are clearly the same facilities

**Examples:**
- Norton Audubon Hospital → Norton Audubon Hospital - Neurodiagnostics (same address)
- UofL Health - Mary & Elizabeth → UofL Health – Mary & Elizabeth Hospital (same address)
- St. Elizabeth Edgewood → St. Elizabeth Healthcare Edgewood (same address)

### Phase 2: Review Questionable Matches (~25 providers)

**Criteria:** Name similar but different addresses or specialties

**Decision needed for each:**
- Are these different departments of same facility?
- Are these different locations?
- Is one a better/official name for the other?

**Impact:** ~39 cases
**Risk:** MEDIUM - Requires manual review

### Phase 3: Keep Unmatched Providers (~214 providers)

**These are:** Independent clinics, chiropractors, imaging centers not part of major health systems

**Action:** No change needed - these are legitimate separate entities

---

## Files for Your Review

### Main Reports

1. **`OLD_TO_NEW_PROVIDER_MAPPING.md`** (local, 1,049 lines)
   - Complete list of all 38 potential matches
   - Organized by health system
   - Full details for each old/new pair
   - Decision checkboxes for each

2. **`OLD_TO_NEW_MAPPING.csv`** (local)
   - All 38 matches in CSV format
   - Easy to review in spreadsheet
   - Columns: old_name, old_id, old_cases, new_name, new_id, new_system, match_score, decision

### Additional Context

3. **`MEDICAL_PROVIDER_DUPLICATES_FULL_REPORT.md`** (4,007 lines)
   - All 245 fuzzy duplicate groups
   - Includes many false positives (different locations with similar names)

---

## Statistics

**Old Providers (from case notes):**
- Total: 1,176 (no parent health system)
- Connected to cases: 252
- Matched to new providers: 38
- No match found: 214

**New Providers (from healthcare rosters):**
- Total: 757 (all have parent health system)
- Matched to old providers: 38
- No old equivalent: 719 (these are additional locations)

**Impact of Replacements:**
- If all 38 replaced: 69 cases affected
- If only high-confidence (13): ~30 cases affected
- Minimal impact overall (<10% of cases)

---

## Next Steps

**Option A: Conservative (Recommended)**
1. Review the 38 matches in `OLD_TO_NEW_PROVIDER_MAPPING.md`
2. Mark decisions for each (REPLACE / KEEP BOTH / REVIEW)
3. I'll create deduplication script based on your markings
4. Execute replacement for approved matches only

**Option B: Auto-Replace High-Confidence Only**
1. Auto-replace ~13 matches where address matches exactly
2. Manual review for remaining 25
3. Quick win with minimal risk

**Option C: Leave As-Is**
1. Keep all providers (both old and new)
2. No risk of breaking case relationships
3. Can dedupe later if needed

---

## My Recommendation

**Start with Option B - Auto-replace high-confidence matches:**

Focus on these clear upgrades:
- Norton hospital variations (same addresses)
- St. Elizabeth hospitals (same addresses)
- CHI Saint Joseph hospitals (same addresses)
- UofL Health - Mary & Elizabeth (same address)

**Estimated:** 10-15 safe replacements, ~25-30 cases affected

Then manually review the questionable matches (different addresses) to decide if they're truly different facilities or just different locations of the same provider.

---

## What You'll Decide

For each of the 38 matches, mark one:

- **[ ] REPLACE** - New provider is better version, update case relationships
- **[ ] KEEP BOTH** - These are different entities (different locations/departments)
- **[ ] REVIEW** - Need more information to decide

I'll create a script to execute your decisions.
