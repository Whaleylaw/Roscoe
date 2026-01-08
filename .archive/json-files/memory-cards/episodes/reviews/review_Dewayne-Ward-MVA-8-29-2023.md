# Relationship Review: Dewayne-Ward-MVA-8-29-2023

**Total Episodes:** 137

**Total Proposed Relationships:** 401


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (3)
- AmeriPro EMS Of Kentucky & Indiana
- Starlite Chiropractic (chiropractic)
- Norton Audubon Hospital (hospital)

### Insurance Claims (3)
- **BIClaim**: State Farm Insurance Company
  - Adjuster: Aaron Lovato
- **PIPClaim**: Liberty Mutual Insurance Company
  - Adjuster: Robert Elliott
- **BIClaim**: Elco Insurance

### Liens (1)
- Conduent

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (4 consolidated)
- [ ] Aaron Lovato — *✓ MATCHES: Aaron Lovato*
- [ ] Ebon I. Moore — *✓ MATCHES: Ebon Moore*
- [ ] Robert Elliott — *✓ MATCHES: Robert Elliott*
- [ ] Steven Flynn — *✓ MATCHES: Steven Flynn (from adjusters)*

### Attorney (11 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Betsy R. Catron — *✓ MATCHES: Betsy R. Catron*
- [ ] Dennis Cantrell — *✓ MATCHES: Dennis Cantrell*
- [ ] Janet Weile — *✓ MATCHES: Janet Weile*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Jessica Bottorff — *✓ MATCHES: Jessica Bottorff (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Sarena Tuttle — *✓ MATCHES: Sarena Tuttle (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] W. Bryce Koon, Esq. — *✓ MATCHES: Bryce Koon (WHALEY ATTORNEY, not Attorney)*
- [ ] Zachary Reichle — *✓ MATCHES: Zachary Reichle, Esq.*
- [ ] defendants' attorney — *IGNORED - generic term*

### BIClaim (5 consolidated)
- [ ] Elco Insurance — *✓ MATCHES: Elco Insurance*
- [ ] Elco Insurance - Claim 20091551 — *✓ MATCHES: Elco Insurance*
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm Insurance Company (Adjuster: Aaron Lovato) — *✓ MATCHES: State Farm Insurance Company*
- [ ] State Farm Insurance Company (BI claim) — *✓ MATCHES: State Farm Insurance Company*

### Client (6 consolidated)
- [ ] Ashlee Williams — *✓ MATCHES: Ashlee K. Williams*
- [ ] Dannin Turner — *IGNORED - non-client reference*
- [ ] Dewayne Ward — *✓ MATCHES: Dewayne Ward*
- [ ] Duquan Graham — *✓ MATCHES: Daquan Graham*
- [ ] Frank Adkins — *IGNORED - non-client reference*
- [ ] Julmonzhae Moore — *✓ MATCHES: Julmonzhae Moore*

### Court (5 consolidated)
- [ ] Floyd Circuit Court — *✓ MATCHES: Floyd County Circuit Court, Division I*
- [ ] Floyd Circuit Court (Floyd 22D03-2501-CT-000157) — *✓ MATCHES: Floyd County Circuit Court, Division I*
- [ ] Floyd Co. Indiana Circuit Court — *IGNORED - Indiana court, not Kentucky*
- [ ] Floyd County — *✓ MATCHES: Floyd County Circuit Court, Division I*
- [ ] Floyd County Court — *✓ MATCHES: Floyd County Circuit Court, Division I*

### Defendant (3 consolidated)
- [ ] Naomi Robinson — *✓ MATCHES: Naomi Robinson*
- [ ] Robinson — *✓ MATCHES: Naomi Robinson*
- [ ] defendants — *IGNORED - generic term*

### Insurer (3 consolidated)
- [ ] Elco Insurance — *✓ MATCHES: Elco Insurance*
- [ ] Liberty Mutual Personal Insurance Company — *✓ MATCHES: Liberty Mutual Insurance Company*
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

### LawFirm (2 consolidated)
- [ ] Stoll Keenon Ogden PLLC — *✓ MATCHES: Stoll Keenon Ogden PLLC*
- [ ] The Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### MedicalProvider (3 consolidated)
- [ ] AmeriPro EMS Of Kentucky & Indiana — *✓ MATCHES: AmeriPro EMS Of Kentucky & Indiana*
- [ ] Starlite Chiropractic — *✓ MATCHES: Starlite Chiropractic*
- [ ] Norton Audubon Hospital — *✓ MATCHES: Norton Audubon Hospital*

### Organization (3 consolidated)
- [ ] EHI — *IGNORED - abbreviation only*
- [ ] Evenup — *✓ MATCHES: EvenUP (from vendors)*
- [ ] New Albany Police Department — *✓ MATCHES: New Albany Police Department*

### PIPClaim (6 consolidated)
- [ ] Liberty Mutual Claim #054658453-07 — *✓ MATCHES: Liberty Mutual Insurance Company*
- [ ] Liberty Mutual Insurance Company (PIPClaim) — *✓ MATCHES: Liberty Mutual Insurance Company*
- [ ] Liberty Mutual Insurance Company (PIPClaim, Adjuster: Robert Elliott) — *✓ MATCHES: Liberty Mutual Insurance Company*
- [ ] Liberty Mutual Insurance Company - Claim 054658453 — *✓ MATCHES: Liberty Mutual Insurance Company*
- [ ] PIP claim (Liberty Mutual) — *✓ MATCHES: Liberty Mutual Insurance Company*
- [ ] PIP claim - Liberty Mutual Insurance Company — *✓ MATCHES: Liberty Mutual Insurance Company*

### Vendor (2 consolidated)
- [ ] Axon / Evidence.com — *IGNORED - software/service*
- [ ] Brandon French — *IGNORED - person name only*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships