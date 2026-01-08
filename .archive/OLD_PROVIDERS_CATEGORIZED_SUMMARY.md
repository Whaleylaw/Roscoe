# Old Medical Providers - Categorized by Health System ✅

**Date:** January 2, 2026
**Source:** `json-files/medical-providers.json` (case data providers)
**Total Providers:** 574 entries (71 unique provider names)

---

## Summary by Health System

| Health System | Unique Providers | Total Entries | Cases |
|---------------|------------------|---------------|-------|
| **Norton Healthcare** | 20 | 42 | ~15 |
| **UofL Health** | 15 | 78 | ~20 |
| **Baptist Health** | 23 | 40 | ~15 |
| **CHI Saint Joseph Health** | 7 | 7 | ~5 |
| **St. Elizabeth Healthcare** | 6 | 9 | ~5 |
| **Other (Independent)** | ~400 | 397 | ~140 |
| **TOTAL** | **~470** | **574** | **~200** |

**Note:** "Other" includes independent clinics, chiropractors, imaging centers, therapy clinics not part of the 5 major systems.

---

## Files Generated

### Location: `/Volumes/X10 Pro/Roscoe/old-providers-by-system/`

**5 Health System Files:**

1. **`norton_healthcare_old_providers.md`**
   - 20 unique Norton providers
   - 42 total entries
   - Examples: Norton Audubon Hospital, Norton Hospital Downtown, Norton Neuroscience Institute

2. **`uofl_health_old_providers.md`**
   - 15 unique UofL providers
   - 78 total entries
   - Examples: Jewish Hospital, UofL Hospital, UofL Physicians - Orthopedics, Mary & Elizabeth Hospital

3. **`baptist_health_old_providers.md`**
   - 23 unique Baptist providers
   - 40 total entries
   - Examples: Baptist Health Louisville, Baptist Health Hardin, Baptist Health Medical Group variants

4. **`chi_saint_joseph_health_old_providers.md`**
   - 7 unique CHI providers
   - 7 total entries
   - Examples: CHI St. Joseph Medical Group, Flaget Memorial Hospital, St. Joseph East

5. **`st._elizabeth_healthcare_old_providers.md`**
   - 6 unique St. Elizabeth providers
   - 9 total entries
   - Examples: St. Elizabeth Edgewood Hospital, St. Elizabeth Florence Hospital

**Summary File:**
- `_SUMMARY.md` - Overview of all 5 systems

---

## Key Insights

### Norton Healthcare (20 providers)

**Most Common:**
- Norton Audubon Hospital (9 entries, ~9 cases)
- Norton Hospital Downtown (3 entries, 3 cases)
- Norton Brownsboro Hospital (3 entries, 3 cases)
- Norton Neuroscience variants (multiple)
- Norton Orthopedic variants (multiple)

**Pattern:** Mostly hospitals and specialty institutes (neuroscience, orthopedic, cancer)

### UofL Health (15 providers)

**Most Common:**
- Jewish Hospital entries (multiple)
- UofL Hospital variants (multiple)
- UofL Health - Mary & Elizabeth (multiple entries)
- UofL Physicians - various specialties

**Pattern:** Mix of hospitals (Jewish, UofL, Mary & Elizabeth) and physician specialty clinics

### Baptist Health (23 providers)

**Most Common:**
- Baptist Health Medical Group - various specialties (Primary Care, Neurology, Orthopedics, Sports Medicine)
- Baptist Health Louisville/Lexington/Hardin (regional hospitals)
- 1st Diagnostics (3 entries) - may be Baptist-affiliated

**Pattern:** Heavy on Medical Group specialty clinics, plus regional hospitals

### CHI Saint Joseph Health (7 providers)

**Smaller system, fewer entries:**
- CHI St. Joseph Medical Group - Orthopedic
- Flaget Memorial Hospital
- St. Joseph East
- St. Joseph Hospital

### St. Elizabeth Healthcare (6 providers)

**Northern KY focused:**
- St. Elizabeth Edgewood Hospital
- St. Elizabeth Florence Hospital
- St. Elizabeth Fort Thomas Hospital
- St. Elizabeth Physicians - variants

---

## Comparison to New Provider Data

### Norton Healthcare

**OLD (from cases):** 20 unique names
**NEW (from roster):** ~368 locations
**Overlap:** ~9-15 providers are likely the same facilities

**Examples of Old → New matches:**
- "Norton Audubon Hospital" → "Norton Audubon Hospital - Neurodiagnostics"
- "Norton Hospital Downtown" → Multiple Norton Downtown departments
- "Norton Neuroscience Institute" → Multiple neuroscience departments

### UofL Health

**OLD (from cases):** 15 unique names
**NEW (from roster):** ~345 locations
**Overlap:** ~6-10 providers are likely the same facilities

**Examples of Old → New matches:**
- "Jewish Hospital" → "UofL Health – Heart Hospital, A Part of Jewish Hospital" or main Jewish Hospital
- "UofL Health - Mary & Elizabeth Mary & Elizabeth Hospital" → "UofL Health – Mary & Elizabeth Hospital"
- "UofL Physicians - Orthopedics" → Specific UofL Physicians orthopedic departments

### Baptist Health

**OLD (from cases):** 23 unique names
**NEW (from roster):** ~467 locations
**Overlap:** ~15-20 providers are likely the same facilities

**Examples:**
- "Baptist Health Louisville" → Multiple Baptist Louisville departments
- "Baptist Health Medical Group Primary Care" → Specific Primary Care locations

### CHI Saint Joseph Health

**OLD (from cases):** 7 unique names
**NEW (from roster):** ~152 locations
**Overlap:** ~3-5 providers match

### St. Elizabeth Healthcare

**OLD (from cases):** 6 unique names
**NEW (from roster):** ~419 locations
**Overlap:** ~2-4 providers match

---

## What This Tells Us

### Pattern 1: Old = Generic, New = Specific

**OLD:** "Norton Hospital Downtown"
**NEW:** "Norton Hospital - Emergency", "Norton Hospital - Surgery", "Norton Pharmacy - Downtown", etc.

**Insight:** Case notes recorded generic facility names. New roster has department-level detail.

### Pattern 2: Name Variations

**OLD:** "Norton Women's & Children's Hospital" vs "Norton Women's and Children's Hospital"
**NEW:** One official name "Norton Women's and Children's Hospital"

**Insight:** Inconsistent data entry created duplicates

### Pattern 3: Missing Coverage

**OLD providers:** Only captured 20 of Norton's 368 locations
**NEW providers:** Complete roster of all Norton facilities

**Insight:** Old data only had providers our cases actually treated at. New data has complete system coverage.

---

## Next Steps

### For Each Health System File:

**Review and decide:**

1. **Which old providers should be REPLACED with new ones?**
   - Same facility, new entry has better data
   - Example: "Norton Audubon Hospital" → "Norton Audubon Hospital - Neurodiagnostics"

2. **Which old providers should be KEPT?**
   - Truly different location/department
   - Old entry has unique information not in new roster

3. **Which old providers can be DELETED?**
   - Duplicates with no unique value
   - Example: One of the two "Norton Women's and Children's Hospital" entries

---

## Recommended Workflow

**For each of the 5 files:**

1. **Open the file** (e.g., `norton_healthcare_old_providers.md`)

2. **For each provider, mark decision:**
   ```markdown
   ### Norton Audubon Hospital
   **Decision:** REPLACE with "Norton Audubon Hospital - Neurodiagnostics" (ID: 12381)
   **Reason:** Same facility, new entry has complete address + phone
   ```

3. **I'll create replacement script** based on your markings

4. **Execute replacements** to update case relationships

---

## Files Location

**All files in:** `/Volumes/X10 Pro/Roscoe/old-providers-by-system/`

1. `norton_healthcare_old_providers.md` (20 providers)
2. `uofl_health_old_providers.md` (15 providers)
3. `baptist_health_old_providers.md` (23 providers)
4. `chi_saint_joseph_health_old_providers.md` (7 providers)
5. `st._elizabeth_healthcare_old_providers.md` (6 providers)
6. `_SUMMARY.md` (overview)

**Total:** 71 unique old provider names across the 5 major health systems to review

---

## Cross-Reference Available

You can cross-reference with:

**`OLD_TO_NEW_PROVIDER_MAPPING.md`** - Shows the 38 suggested matches I found automatically
- Use this as a starting point for decisions
- Providers with same address are high-confidence replacements
- Providers with different addresses may need to be kept separate

---

## Example Review Process

**Norton Audubon Hospital (9 cases, $345K billed):**

1. Check `OLD_TO_NEW_PROVIDER_MAPPING.md` → Suggests "Norton Audubon Hospital - Neurodiagnostics"
2. Verify addresses match → Yes, both 1 Audubon Plaza Drive
3. Decision: **REPLACE** - Same facility, new has better data
4. Mark in file for scripting

**Norton Community Medical Associates - Dixie (1 case):**

1. Check new roster → Probably has specific "Norton Community - Dixie" location
2. Verify address matches
3. Decision: **REPLACE** if address matches, **KEEP** if different

---

## Impact Assessment

**If all 71 providers replaced:**
- ~60-80 cases affected (need relationship updates)
- Old providers deleted from graph
- Cases relinked to new providers

**If only high-confidence replacements:**
- ~30-40 cases affected
- Clear upgrades (same address, better data)
- Lower risk

**Risk Mitigation:**
- Script will verify case counts match
- Backup old relationships before replacement
- Rollback capability if issues arise

---

## Ready for Your Review!

**Next:** Review each of the 5 health system files and mark your replacement decisions. I'll create the deduplication script based on your markings.
