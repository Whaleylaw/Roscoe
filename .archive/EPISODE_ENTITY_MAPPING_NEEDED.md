# Episode Entity Name Mapping - URGENT

**Date:** January 4, 2026
**Issue:** Episode review files reference old MedicalProvider names that no longer exist in graph

---

## Problem

**Episode review files** (138 total, 3 approved) contain entity names like:
- "Jewish Hospital"
- "Foundation Radiology"
- "UofL Physicians - Orthopedics"

**These were MedicalProvider node names** - we just deleted all 1,998 MedicalProvider nodes!

**New graph has:**
- Facility nodes: "UofL Health – Jewish Hospital"
- Location nodes: "UofL Health – Jewish Hospital - Main" (if created)

**Entity names don't match!**

---

## Abby Sitgraves Example

**Review file says:**
```markdown
### MedicalProvider (4 consolidated)
- Foundation Radiology
- Jewish Hospital
- UofL Health - Mary & Elizabeth Hospital
- UofL Physicians - Orthopedics
```

**New graph has (Facilities):**
- "Foundation Radiology" ✓ (same name - OK!)
- "UofL Health – Jewish Hospital" ❌ (different - PROBLEM!)
- "UofL Health – Mary & Elizabeth Hospital" ~ (dash difference)
- "UofL Physicians – Orthopedics" ~ (dash difference)

---

## Impact

**When episodes are ingested:**
```cypher
// Episode says client treated at "Jewish Hospital"
(Episode)-[:ABOUT]->(entity_name: "Jewish Hospital")

// But graph has:
(Facility: "UofL Health – Jewish Hospital")

// Relationship creation will FAIL - no match!
```

**Result:** Episodes won't link to providers correctly

---

## What Needs to Be Updated

### 1. Episode Review Files (138 files)

**Location:** `/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/reviews/`

**Files:** `review_*.md` (all 138)

**Update:** MedicalProvider entity names to match new Facility names

### 2. Merged Episode Files (3 files)

**Location:** `/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/`

**Files:** `merged_*.json` (Abby Sitgraves, Abigail Whaley, Alma Cristobal)

**Update:** Entity names in `proposed_relationships.about` sections

### 3. Processed Episode Files (138 files)

**Location:** `/Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/`

**Files:** `processed_*.json` (all 138)

**Update:** Entity names if these will be used

---

## Mapping Old → New Names

**Common patterns:**

### Health System Providers Need Prefix

**Old:** "Jewish Hospital"
**New:** "UofL Health – Jewish Hospital"

**Old:** "Mary & Elizabeth Hospital"
**New:** "UofL Health – Mary & Elizabeth Hospital"

**Old:** "Norton Hospital"
**New:** "Norton Hospital" (if standalone) OR "Norton Hospital" Facility exists

### Dash Character Differences

**Old:** "UofL Physicians - Orthopedics" (regular dash)
**New:** "UofL Physicians – Orthopedics" (em-dash)

**This will cause match failures!**

### Independent Providers Usually Same

**Old:** "Foundation Radiology"
**New:** "Foundation Radiology" ✓

**Old:** "Starlite Chiropractic"
**New:** "Starlite Chiropractic" ✓

---

## Two Options

### Option A: Update Episode Files to Match New Names

**Process:**
1. Create mapping of old → new names
2. Update all 138 review files
3. Update 3 merged files
4. Ensure entity names match graph

**Pros:**
- Episodes will link correctly
- Clean data

**Cons:**
- Must update 138+ files
- Time-consuming

### Option B: Create Entity Aliases in Graph

**Process:**
1. Keep episode files as-is with old names
2. Create secondary index/mapping in graph
3. Map "Jewish Hospital" → "UofL Health – Jewish Hospital"
4. Episode ingestion uses mapping

**Pros:**
- Don't have to update 138 files
- Flexible

**Cons:**
- More complex ingestion logic
- Aliases to maintain

---

## Recommended Approach: Option A with Script

**Create automated mapping:**

1. **Build mapping file** (old MedicalProvider → new Facility)
   - "Jewish Hospital" → "UofL Health – Jewish Hospital"
   - "UofL Physicians - Orthopedics" → "UofL Physicians – Orthopedics"
   - Etc.

2. **Script to update review files**
   - Parse all review_*.md files
   - Replace old names with new names
   - Preserve all other content

3. **Script to update merged files**
   - Parse merged_*.json files
   - Replace entity names in proposed_relationships
   - Maintain structure

4. **Verification**
   - Check all entity names exist in graph
   - Before episode ingestion

---

## Immediate Action Needed

**Before proceeding with episode ingestion:**

1. ✅ Graph migration complete (done)
2. ⚠️ **Map old provider names → new Facility/Location names** (TO DO)
3. ⚠️ **Update episode review files** (138 files)
4. ⚠️ **Update merged episode files** (3 files)
5. ✅ Then proceed with episode ingestion

---

## Next Steps

**Create:**
1. Provider name mapping file (old → new)
2. Script to update review files
3. Script to update merged files
4. Verification script (check all names exist)

**Would you like me to create these scripts now?**

This is critical before episode ingestion can proceed!
