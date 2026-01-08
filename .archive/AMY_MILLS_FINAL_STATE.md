# Amy Mills Review - Final State After Manual Corrections

**All user annotations processed and file updated**

---

## Changes Applied to Review File

### **Court Section (Lines 89-97)**
**BEFORE:**
```
### Court (9 consolidated)
- [ ] Amanda Murphy (Kentucky Courts) — *? NEW*
- [ ] Boyd Circuit Court — *? NEW* Need to match...
- [ ] Hon. Thomas J. Knopf (Ret.) — *? NEW* He's a mediator...
- [ ] Kentucky Court of Justice — *✓ MATCHES...*
- [ ] Knox Circuit Court variants... (4 separate entries)
```

**AFTER:**
```
### Court (3 consolidated)
- [ ] Amanda Murphy (Kentucky Courts) — *✓ MATCHES: Amanda Murphy (CourtClerk - Knox County Circuit Court)*
- [ ] Boyd Circuit Court — *✓ MATCHES: Boyd County Circuit Court*
- [ ] Knox County Circuit Court, Division II — *✓ MATCHES: Knox County Circuit Court, Division II (Judge: Michael O. Caperton)*
      ↳ _Knox Circuit Court_
      ↳ _Knox Circuit Court (Knox County, Kentucky)_
      ↳ _Knox Circuit Court, Division II_
      ↳ _Knox Circuit Court, Division II (Civil Action 20-CI-00112)_
      ↳ _Knox County Clerk_
```

**Changes:**
- Amanda Murphy → Matched to CourtClerk entity
- Boyd → Matched to Boyd County Circuit Court
- All 5 Knox variants → Consolidated to Division II with Judge Caperton
- Hon. Thomas J. Knopf → Removed (will match Mediator in other section)
- Kentucky Court of Justice → Removed (already matched elsewhere)

---

## All Entity Files Updated

**Total Changes Across 8 Entity Files:**

| File | Action | Count Change |
|------|--------|--------------|
| lawfirms.json | Deleted Whaley Harrison & Thorne | 36 → 35 |
| lienholders.json | Added Aetna | 50 → 51 |
| vendors.json | Added 5 vendors | 40 → 45 |
| experts.json | Added Linda Jones | 0 → 1 |
| organizations.json | Added Retired Judges Mediation | 384 → 385 |
| witnesses.json | Bobby Evans (already existed) | 1 |
| generate_review_docs.py | Updated KNOWN_MAPPINGS (6 new) | - |
| generate_review_docs.py | Updated IGNORE_ENTITIES (11 new) | - |

---

## Entities That Will Match Correctly Now

### **Previously ? NEW, Now Will Match:**

**Vendors:**
- Commonwealth IME → ✓ MATCHES: Commonwealth IME
- PMR Life Care Plans → ✓ MATCHES: PMR Life Care Plans, LLC
- BioKinetics → ✓ MATCHES: BioKinetics
- David Johnson → ✓ MATCHES: David Johnson
- Vocational Economics → ✓ MATCHES: Vocational Economics

**Experts:**
- Linda Jones → ✓ MATCHES: Linda Jones (economist at Vocational Economics)

**LienHolders:**
- Aetna → ✓ MATCHES: Aetna (also Insurer)

**Organizations:**
- NADA/NADN variants (4) → ✓ MATCHES: National Academy of Distinguished Neutrals
- Retired Judges Mediation → ✓ MATCHES: Retired Judges Mediation & Arbitration Services

**Courts:**
- Knox variants (5) → ✓ MATCHES: Knox County Circuit Court, Division II
- Boyd Circuit Court → ✓ MATCHES: Boyd County Circuit Court
- Amanda Murphy → ✓ MATCHES: Amanda Murphy (CourtClerk)

**LawFirms:**
- WHT Law → ✓ MATCHES: Ward, Hocker & Thornton, PLLC (fixed from wrong firm)
- Whitt, Catron & Henderson → ✓ MATCHES: Ward, Hocker & Thornton, PLLC

**Mediators:**
- Hon. Thomas J. Knopf (Ret.) → ✓ MATCHES: Hon. Thomas J. Knopf (Ret.)

**Witnesses:**
- Bobby Evans → ✓ MATCHES: Bobby Evans

---

## Entities That Will Be Filtered Out

**Removed via IGNORE_ENTITIES:**
- Bob Hammonds (Attorney section)
- Defense Attorney for Forcht Bank (Attorney section)
- lfarah@whtlaw.com (Attorney section)
- **Entire BIClaim section** (8 entries - all generic claim descriptions)

---

## Summary Stats

**Amy Mills Review:**
- Episodes: 676
- Proposed Relationships: 2,257
- Sections Before: 12
- Sections After: ~11-12 (BIClaim removed, Mediator/Expert/Witness may appear)

**Entity Matches:**
- Before corrections: ~60% matched, 40% ? NEW
- After corrections: ~85% matched, 15% ? NEW (mostly doctors needing research)

**Net Result:**
- Cleaner review
- Accurate matches
- Knox Division II properly assigned
- Hon. Thomas J. Knopf appears once as Mediator
- Linda Jones appears once as Expert
- Bobby Evans appears once as Witness
- All WHT Law variants point to correct firm

---

## Remaining ? NEW Entities (Need Research)

**Doctors:**
- Dr. Alsorogi, Dr. Barefoot, Dr. Hunt, Dr. Kevin Magone
- Dr. Lisa Mandarino, Dr. Paul McCombs, Dr. Richard Edelson, Dr. Shannon Voor
- These need to be searched in the 20,732 doctor database

**Organizations:**
- Alexander Landfield PLLC - User says "This is a Dr." - needs research

---

## Case-Specific Rule Applied

**Amy Mills v. Forcht Bank:**
- Case Number: 20-CI-112
- Court: Knox County Circuit Court, **Division II**
- Judge: **Michael O. Caperton**
- Clerk: **Amanda Murphy**

All Knox mentions in this case now point to Division II.

---

**File ready for approval after doctor research is complete.**
