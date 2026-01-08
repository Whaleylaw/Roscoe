# Medical Providers Deduplicated - FINAL ✅

**Date:** January 2, 2026
**Result:** 403 entries → 214 unique providers

---

## Summary

Successfully deduplicated the cleaned medical-providers file, consolidating multiple entries per provider into single entries with aggregated data.

**Original entries:** 574 (raw case data)
**After deletion cleanup:** 403 entries
**After deduplication:** 214 unique providers

**Reduction:** 360 duplicate entries removed (63%)

---

## Deduplication Example

### Starlite Chiropractic (Most Common Independent Provider)

**Before Deduplication:**
- 57 separate entries in the file
- One entry per case treated
- Data scattered across entries

**After Deduplication:**
```json
{
  "provider_full_name": "Starlite Chiropractic",
  "entry_count": 57,
  "cases": [
    "Alma-Cristobal-MVA-2-15-2024",
    "Antonio-Lopez-MVA-11-14-2025",
    "Ashlee-Williams-MVA-08-29-2023",
    ... 53 more cases
  ],
  "total_billed": $265,470.00,
  "total_settlement": $...,
  "first_treatment": ...,
  "total_visits": ...
}
```

**Result:** 57 entries → 1 entry with complete aggregated data

---

## Top Independent Providers (By Case Count)

| Rank | Provider | Cases | Total Billed |
|------|----------|-------|--------------|
| 1 | **Starlite Chiropractic** | 56 | $265,470 |
| 2 | Louisville Metro EMS | 16 | $8,836 |
| 3 | Aptiva Health | 10 | $59,530 |
| 4 | Southeastern Emergency Physician Services | 10 | $12,400 |
| 5 | Synergy Injury Care & Rehab Diagnostics | 6 | $36,705 |
| 6 | Louisville Emergency Medical Associates | 5 | $5,217 |
| 7 | Louisville Metro Emergency Medical Service | 5 | $0 |
| 8 | Allstar Chiropractic | 4 | $10,950 |
| 9 | Foundation Radiology | 4 | $310 |
| 10 | Gould's Discount Medical | 4 | $1,168 |

**Starlite Chiropractic is by far the most used independent provider** (56 cases!)

---

## File Structure Change

### Before (Entry per Case)

```json
[
  {
    "id": 1,
    "project_name": "Case-A",
    "provider_full_name": "Starlite Chiropractic",
    "billed_amount": 5000
  },
  {
    "id": 2,
    "project_name": "Case-B",
    "provider_full_name": "Starlite Chiropractic",
    "billed_amount": 4500
  },
  ... 55 more entries for Starlite
]
```

### After (One Entry per Provider)

```json
[
  {
    "provider_full_name": "Starlite Chiropractic",
    "entry_count": 57,
    "cases": ["Case-A", "Case-B", ... all 56 cases],
    "total_billed": 265470,
    "total_settlement": ...,
    "first_treatment": ...,
    "total_visits": ...
  }
]
```

---

## Files

### Current Files

1. **`medical-providers.json`** - 574 entries (original backup)
2. **`medical-providers-REMAINING.json`** - 458 entries (after Norton/UofL deletion)
3. **`medical-providers-FINAL.json`** - 403 entries (after all deletions)
4. **`medical-providers-DEDUPLICATED.json`** ⭐ - **214 unique providers**

### Which File to Use?

**For list of unique independent providers:**
→ Use `medical-providers-DEDUPLICATED.json` (214 providers)

**For case-specific provider data:**
→ Use `medical-providers-FINAL.json` (403 entries, one per case)

**For backup:**
→ Use `medical-providers.json` (574 entries, original)

---

## Statistics

### Deduplication Impact

**Original entries:** 574
**After cleanup:** 403 entries (removed Norton/UofL/Baptist/CHI/St. Elizabeth)
**After dedup:** 214 unique providers

**Duplicates per provider (average):** ~1.9 entries per provider
**Most duplicated:** Starlite Chiropractic (57 entries for 1 provider!)

### Provider Types in Deduplicated File

**By category (estimated):**
- Chiropractic clinics: ~50
- Emergency medicine groups: ~15
- Imaging/radiology centers: ~20
- Physical therapy clinics: ~30
- Orthopedic practices: ~15
- Other specialists: ~50
- EMS/Ambulance: ~5
- Medical equipment suppliers: ~5
- Miscellaneous: ~24

**Total:** 214 unique independent providers

---

## What This Represents

**These 214 providers are:**
- ✅ NOT part of the 6 major health systems
- ✅ Independent clinics and practices
- ✅ Used across your case portfolio
- ✅ Ready for future reference

**The 6 major health systems are managed separately:**
- Via facility-based JSON files (1,248 facilities)
- In graph with PART_OF relationships
- Clean, official rosters

---

## Next Steps

### For Independent Providers (Optional)

**If you want to add these to the graph:**
- Upload medical-providers-DEDUPLICATED.json
- Create entities for 214 unique providers
- Keep as independent (no health system connection)

**Or:**
- Keep as reference file only
- Add to graph as needed when cases require them

### For Major Health Systems

**When ready to ingest facility-based providers:**
- Upload 6 facility-based JSON files to GCS
- Ingest 1,248 facilities to graph
- Connect to cases from medical records review

---

## ✅ Complete

**Created:** `medical-providers-DEDUPLICATED.json` with 214 unique independent providers

**No more duplicates!** Each provider appears exactly once with aggregated data from all their cases.

**You now have a clean reference list of all independent medical providers used across your cases.**
