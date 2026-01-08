# UofL Health Mapping - Regenerated with Facility Structure ✅

**Date:** January 2, 2026
**New File:** `provider-mappings/UOFL_MAPPING_FACILITY_BASED.md`

---

## What Changed

### Old Mapping (Location-Based)
- **Matching against:** 345 individual location nodes
- **Result:** Many similar-sounding locations made matching confusing
- **Example:** "University of Louisville Hospital" matched against dozens of "UofL Hospital - [Department] - [Location]" variations

### New Mapping (Facility-Based) ⭐
- **Matching against:** 169 facility nodes
- **Result:** Much clearer matches with location counts shown
- **Example:** "Jewish Hospital" → "UofL Health – Jewish Hospital" (100% match, 1 location)

**Reduction:** 51% fewer nodes to match against (345 → 169)

---

## Key Improvements

### Example 1: UofL Physicians - Orthopedics

**OLD Mapping (Location-Based):**
- Matched against many individual orthopedic locations
- Hard to tell which one is correct

**NEW Mapping (Facility-Based):**
```
Match #1: UofL Physicians – Orthopedics (96% match)
  - Locations: 19
  - Shows first 3 locations with addresses
  - ... and 16 more locations
```

**Benefit:** One facility node contains all 19 orthopedic locations!

### Example 2: Jewish Hospital

**OLD Mapping:**
- Matched against "UofL Health – Heart Hospital, A Part of Jewish Hospital"
- Confusing - is it Heart Hospital or Jewish Hospital?

**NEW Mapping:**
```
Match #2: UofL Health – Jewish Hospital (100% match)
  - Locations: 1
  - Main: 200 Abraham Flexner Way, Louisville, KY 40202
```

**Benefit:** Clear match to main Jewish Hospital facility

### Example 3: Mary & Elizabeth Hospital

**OLD:**
- "UofL Health - Mary & Elizabeth Mary & Elizabeth Hospital" (duplicate name)
- Matched against many M&E departments

**NEW:**
```
Match #1: UofL Health – Mary & Elizabeth Hospital (92% match)
  - Locations: 1
  - Main: 1850 Bluegrass Avenue, Louisville, KY 40215
```

**Benefit:** Clear match to main hospital, can see it's a single location

---

## UofL Providers to Map

**Total:** 15 old providers from case data

**Top by impact:**

1. **University of Louisville Hospital** - 32 cases, $538K
2. **University of Louisville Physicians** - 12 cases
3. **UofL Health - Mary & Elizabeth Hospital** - 11 cases, $35K
4. **University Of Louisville Hospital Radiology** - 6 cases
5. **Jewish Hospital** - 4 cases, $14K (includes Abby Sitgraves!)
6. ... and 10 more

---

## Matching Quality

**Excellent matches (90%+):**
- UofL Physicians - Orthopedics → UofL Physicians – Orthopedics (96%)
- UofL Physicians - Podiatric Medicine & Surgery → UofL Physicians – Podiatric Medicine & Surgery (97%)
- UofL Health - Medical Center Southwest → UofL Health – Medical Center Southwest (94%)
- UofL Health - Mary & Elizabeth → UofL Health – Mary & Elizabeth Hospital (92%)

**Good matches (75-89%):**
- Jewish Hospital → UofL Health – Jewish Hospital (100% partial match, 77% ratio)
- U of L Health Urgent Care Buechel → UofL Health – Urgent Care Plus – Buechel (75%)

**Lower matches (need review):**
- University of Louisville Hospital → Many 100% partial matches but low ratio scores
- University of Louisville School of Dentistry → Low matches (may not be in roster)

---

## File Structure

**Each entry shows:**

```markdown
## N. OLD: [Provider Name]

**Cases:** [List of all cases]
**Total Billed:** $X,XXX

**Top 5 Facility Matches:**

1. **[Facility Name]** (XX% match)
   - Locations: N
   - [First 3 location addresses]
   - ... and N more locations (if applicable)
   - Match breakdown: Ratio=X%, Partial=Y%, TokenSort=Z%

**DECISION:**
- [ ] REPLACE with match #___
- [ ] KEEP OLD
- [ ] DELETE
```

---

## Benefits of Facility-Based Matching

### 1. Clearer Matches
- Facility names are more distinctive
- Fewer false positives from location variations

### 2. Location Information Visible
- Can see how many locations each facility has
- Sample addresses shown for verification
- Full location list available in facility properties

### 3. Better Semantic Matching
- "UofL Physicians - Orthopedics" clearly matches "UofL Physicians – Orthopedics"
- Not confused by individual location names

### 4. Easier Decisions
- Can see if facility has the location you need
- Location count helps determine if it's the right match

---

## Next Steps

1. **Review** `UOFL_MAPPING_FACILITY_BASED.md` (15 providers)
2. **Mark decisions** for each old provider
3. **I'll execute** replacements based on your markings

**This mapping should be MUCH easier to work with than the location-based version!**

---

## Files

**New mapping:** `/Volumes/X10 Pro/Roscoe/provider-mappings/UOFL_MAPPING_FACILITY_BASED.md`

**Old mapping (deprecated):** `UOFL_MAPPING.md` (can ignore)

---

## ✅ UofL Mapping Regenerated

The new facility-based mapping provides much clearer matches for the 15 old UofL providers, making it easier to make replacement decisions!
