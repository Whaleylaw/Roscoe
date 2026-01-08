# Abby-Sitgraves-MVA-7-13-2024 - Manual Corrections

## Original Annotations & Correct Actions

### Line 56 - Court
**Original:** `- [ ] Jefferson (25-CI-000133) — *✓ MATCHES: Jefferson County Circuit Court* Should be Jefferson County Circuit Court Division II.`

**User Intent:** The match is close but needs division specified

**Correct Action:**
1. This case is in Division II
2. Update line to: `- [ ] Jefferson (25-CI-000133) — *✓ MATCHES: Jefferson County Circuit Court, Division II*`
3. Apply Division II to ALL Jefferson County Circuit Court mentions in THIS case only

---

### Line 57-58 - Court (other Jefferson mentions)
**Current:** `- [ ] Jefferson Circuit Court — *✓ MATCHES: Jefferson County Circuit Court*`
**Current:** `- [ ] Jefferson County (25-CI-00133) — *✓ MATCHES: Jefferson County Circuit Court*`

**Correct Action:**
Since this case is Division II, update both to:
- `- [ ] Jefferson Circuit Court — *✓ MATCHES: Jefferson County Circuit Court, Division II*`
- `- [ ] Jefferson County (25-CI-00133) — *✓ MATCHES: Jefferson County Circuit Court, Division II*`

---

### Line 62 - Defendant
**Original:** `- [ ] Unknown Driver — *✓ MATCHES: Unknown Driver (from directory)* Needs to be added as a defendant.`

**User Intent:** "Unknown Driver" exists in directory.json but NOT in defendants.json - need to add it

**Correct Action:**
1. Add "Unknown Driver" to defendants.json
2. Update line to: `- [ ] Unknown Driver — *✓ MATCHES: Unknown Driver*`
3. Remove "(from directory)" since it's now in defendants.json

---

### Line 63 - Defendant
**Original:** `- [ ] limousine company — *? NEW* Ignore.`

**Correct Action:**
1. Add "limousine company" to IGNORE_ENTITIES set
2. Remove line entirely from future reviews (filtered during consolidation)
3. For this diff, mark as: `- [ ] limousine company — *✓ WILL BE FILTERED*`

---

### Line 67 - Insurer
**Original:** `- [ ] Kentucky One Health — *✓ MATCHES: KENTUCKY ONE HEALTH ORTHOPEDIC ASSOCIATES (from directory)*No, it's not.Probably need to see the context.`

**User Intent:** The match is WRONG. "Kentucky One Health" (insurer) should not match "KENTUCKY ONE HEALTH ORTHOPEDIC ASSOCIATES" (medical provider)

**Correct Action:**
1. Add episode context to understand what "Kentucky One Health" actually is
2. Mark as: `- [ ] Kentucky One Health — *? NEEDS REVIEW - wrong match, need context*`
3. OR remove the incorrect match and leave as `*? NEW*` with context added

---

### Lines 96-97 - UMClaim
**Original:**
- `- [ ] Uninsured motorist demand(s) — *? NEW* Ignore`
- `- [ ] uninsured motorist claim — *? NEW* Ignore`

**Correct Action:**
1. Add both to IGNORE_ENTITIES
2. These will be filtered out in future reviews
3. For this diff, mark as: `*✓ WILL BE FILTERED*`

---

## Summary of Actions

### Entities to Add:
- [x] Unknown Driver → defendants.json

### Entities to Ignore (filter in future):
- [x] limousine company
- [x] Uninsured motorist demand(s)
- [x] uninsured motorist claim

### Corrections to Make:
- [x] Jefferson (25-CI-000133) → Add ", Division II"
- [x] Jefferson Circuit Court → Add ", Division II"
- [x] Jefferson County (25-CI-00133) → Add ", Division II"

### Needs Further Review:
- [ ] Kentucky One Health - WRONG MATCH, need episode context to determine correct entity

---

## Case-Specific Rules

**For Abby-Sitgraves case ONLY:**
- Jefferson County Circuit Court → Jefferson County Circuit Court, Division II
