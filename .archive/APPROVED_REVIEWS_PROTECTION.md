# Approved Review Protection Mechanism

## Overview

Prevents manually-corrected review files from being overwritten during batch regeneration.

---

## Protected Files

The following 3 review files have been manually corrected with case-specific court divisions and are **LOCKED from regeneration**:

1. **review_Abby-Sitgraves-MVA-7-13-2024.md**
   - Jefferson County Circuit Court → **Division II** (Judge: Annie O'Connell)
   - All corrections: Division II, Unknown Driver added, Kentucky One Health removed, generic terms filtered

2. **review_Abigail-Whaley-MVA-10-24-2024.md**
   - Lynette Duncan added as adjuster
   - All matches verified

3. **review_Alma-Cristobal-MVA-2-15-2024.md**
   - Jefferson County Circuit Court → **Division III** (Judge: Mitch Perry)
   - District Court → Jefferson County District Court
   - All corrections: Division III consolidation, Aletha Thomas type correction, Alma Cristobal consolidation, Louisville Metro Police separated

---

## How It Works

### **Approval File:**
`/json-files/memory-cards/episodes/reviews/APPROVED_REVIEWS.txt`

Contains list of approved filenames (one per line):
```
# Approved Review Files - DO NOT REGENERATE
review_Abby-Sitgraves-MVA-7-13-2024.md
review_Abigail-Whaley-MVA-10-24-2024.md
review_Alma-Cristobal-MVA-2-15-2024.md
```

### **Regeneration Script Updates:**
`regenerate_all_reviews.py` now:
1. Loads APPROVED_REVIEWS.txt at startup
2. Skips any files in the approved list
3. Reports how many were skipped
4. Only regenerates the remaining ~135 files

### **Output Example:**
```
⚠️  Skipping 3 approved reviews (will not regenerate)
     - review_Abby-Sitgraves-MVA-7-13-2024.md
     - review_Abigail-Whaley-MVA-10-24-2024.md
     - review_Alma-Cristobal-MVA-2-15-2024.md

Loading global entities...
...

✅ Regenerated 135 review documents
   Skipped 3 approved reviews (protected from regeneration)
```

---

## Adding More Approved Files

As you review and approve more files, simply add them to APPROVED_REVIEWS.txt:

```bash
echo "review_Amy-Mills-Premise-04-26-2019.md" >> APPROVED_REVIEWS.txt
```

Or edit the file directly.

---

## Why This Matters

**Problem:** Court divisions are case-specific and manually assigned:
- Abby case → Division II
- Alma case → Division III
- Each must be researched from case numbers and docket info

**Without Protection:**
- Regeneration runs matching algorithm
- Algorithm doesn't know Division II vs III (it's context-dependent)
- Overwrites manual corrections ❌

**With Protection:**
- Approved files are SKIPPED entirely
- Manual corrections preserved ✓
- You build approved list incrementally as you review

---

## Current Status

**Approved (3 files):**
- ✅ Abby-Sitgraves
- ✅ Abigail-Whaley
- ✅ Alma-Cristobal

**Pending Review (135 files):**
- These will be regenerated with updated entity databases
- As you approve each batch, add to APPROVED_REVIEWS.txt
- Eventually all 138 will be approved

---

## Workflow Going Forward

1. **Regenerate** remaining 135 reviews with latest entity data
2. **You review** next batch (e.g., Amy-Mills through Azaire-Lopez)
3. **Add inline annotations** for corrections needed
4. **I manually apply** your corrections (NO automatic scripts)
5. **You approve** → Add to APPROVED_REVIEWS.txt
6. **Repeat** until all 138 approved

**This prevents the regeneration loop that was losing your corrections!**
