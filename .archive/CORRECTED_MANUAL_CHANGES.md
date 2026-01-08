# Corrected Manual Changes - Based on User Clarifications

## Alma-Cristobal Corrections

### Client Section - Line 62-63:
**Current:**
```
- [ ] Aletha N. Thomas — ✓ TYPE CORRECTED: Attorney (was Client)
- [ ] Alma Cristobal — ✓ CORRECTED: the client
```

**CORRECT Changes:**
```
- [ ] Aletha N. Thomas — *✓ SEE Attorney Section - line 43*
- [ ] **Alma Socorro Cristobal Avendao** — *✓ MATCHES: Alma Socorro Cristobal Avendao*
      ↳ _Alma Cristobal_
      ↳ _Alma Socorro Cristobal Avenda o_
```

**Explanation:**
- Aletha Thomas: Don't remove, just cross-reference to Attorney section where she's correctly listed
- Alma Cristobal: Match to existing client "Alma Socorro Cristobal Avendao" (short name variant)

---

### LawFirm Section - Line 91:
**Current:**
```
- [ ] Sarena Whaley Law Firm — *? NEW*
```

**CORRECT Change:**
```
- [ ] Sarena Whaley Law Firm — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF - misclassified as law firm)*
```

**Explanation:** Not a law firm to ignore, it's Sarena Tuttle (case manager) that was incorrectly extracted as a law firm name

---

### MedicalProvider Section - Line 98:
**Current:**
```
- [ ] Louisville LMEMS — ✓ CORRECTED: Louisville Metro EMS
```

**CORRECT Change:**
```
- [ ] Louisville LMEMS — *✓ MATCHES: Louisville Metro EMS*
```

**Explanation:** Entity already exists in medical_providers.json, no need to add - just match to it

---

### MedicalProvider Section - Line 103:
**Current:**
```
- [ ] UofL Health - Mary & Elizabeth Mary & Elizabeth Hospital — ✓ CORRECTED: St
```

**CORRECT Change:**
```
- [ ] UofL Health - Mary & Elizabeth Mary & Elizabeth Hospital — *✓ MATCHES: Saint Mary and Elizabeth Hospital*
```

**Explanation:** Match to existing entity, don't truncate to "St"

---

### Court Section - Lines 67-74:
**Current:** Mix of ✓ CORRECTED and ✓ MATCHES

**CORRECT Changes:**
```
- [ ] **Jefferson 24-CI-004728** — *✓ MATCHES: Jefferson County Circuit Court, Division III*
      ↳ _Jefferson Circuit Court_
      ↳ _Jefferson County (24-CI-004728)_
      ↳ _Jefferson County (Case 24-CI-004728)_
      ↳ _Jefferson County (Jefferson 24-CI-004728)_
      ↳ _Jefferson County - Docket 24-CI-004728_
      ↳ _Kentucky Court of Justice_
- [ ] District Court — *✓ MATCHES: Jefferson County District Court*
```

**Explanation:**
- Consolidate all 6 Jefferson mentions into one entry with variants
- All point to Division III (case-specific)
- District Court → Jefferson County District Court (not Christian)

---

### Defendant Section - Line 82:
**Current:**
```
- [ ] Hamilton & Crete Carrier — ✓ CORRECTED: Roy Hamilton and Crete Carrier Corporation
```

**CORRECT Change:**
```
- [ ] Hamilton & Crete Carrier — *✓ Both defendants in case: Roy Hamilton & Crete Carrier Corporation*
```

**Explanation:** This entry refers to both defendants together, keep as multi-defendant reference

---

### Organization Section - Lines 107, 113:
**Current:**
```
- [ ] Franklin County, Ohio Sheriff's Office — ✓ Already added
- [ ] MetroSafe — ✓ Already added
```

**CORRECT Change:**
```
- [ ] Franklin County, Ohio Sheriff's Office — *✓ MATCHES: Franklin County, Ohio Sheriff's Office*
- [ ] MetroSafe — *✓ MATCHES: MetroSafe*
```

**Explanation:** They've been added to organizations.json, so now they MATCH (not "already added")

---

### Vendor Section - Lines 121-122:
**Current:**
```
- [ ] KY Court Reporters — *✓ MATCHES: Kentucky Court Reporters (from directory)*
- [ ] Kentuckiana Reporters — *✓ MATCHES: Kentuckiana Court Reporters (from directory)*
```

**ACTION NEEDED:**
1. Add both to vendors.json (from directory.json)
2. Then update to:
```
- [ ] KY Court Reporters — *✓ MATCHES: Kentucky Court Reporters*
- [ ] Kentuckiana Reporters — *✓ MATCHES: Kentuckiana Court Reporters*
```

---

## Case-Specific Rules

### Alma-Cristobal-MVA-2-15-2024:
- ALL Jefferson County Circuit Court mentions → **Division III**
- District Court → **Jefferson County District Court**

---

## Entities to Add (from directory → JSON files):

### Vendors:
- [ ] Kentucky Court Reporters (from directory.json)
- [ ] Kentuckiana Court Reporters (from directory.json)

---

## Summary

**Total Corrections for Alma-Cristobal:**
- 1 consolidation (6 Jefferson court variants → 1 entry)
- 1 client consolidation (3 variants → 1)
- 1 BI claim consolidation (4 variants → 1)
- 2 type corrections (Aletha cross-ref, Sarena Law Firm → Sarena Tuttle)
- 3 match corrections (Louisville LMEMS, UofL Mary & Elizabeth, District Court)
- 2 entities to add from directory (vendors)
- 1 multi-defendant notation

**Approved and ready to execute?**
