# Relationship Review: Jaysha-Aponte-MVA-3-15-2025

**Total Episodes:** 46

**Total Proposed Relationships:** 122


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (6)
- East Broadway Family Health Center
- Family Health Centers - Portland
- Louisville Metro EMS (emergency medical services)
- Starlite Chiropractic (chiropractic)
- ULP Emergency
- Norton Audubon Hospital (hospital)

### Insurance Claims (3)
- **BIClaim**: Mobilitas Insurance Company
  - Adjuster: Hannah Snow
- **BIClaim**: Geico Insurance Company
  - Adjuster: Myderia Pittman
- **PIPClaim**: Progressive Insurance Company
  - Adjuster: Monica Jones

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (7 consolidated)
- [ ] Amanda L Clemons — *✓ MATCHES: Amanda Clemons*
- [ ] Andrew Cheers — *✓ MATCHES: Andrew Cheers (from adjusters)*
- [ ] Hannah Snow — *✓ MATCHES: Hannah Snow*
- [ ] Joseph — *✓ MATCHES: Joseph Dedeyn*
- [ ] Monica Jones — *✓ MATCHES: Monica Jones*
- [ ] Myderia Pittman — *✓ MATCHES: Myderia Pittman*
- [ ] assigned adjuster — *IGNORED - generic term*

### Attorney (4 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Jessa Galosmo — *✓ MATCHES: Jessa Galosmo (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*

### BIClaim (5 consolidated)
- [ ] Geico Insurance Company — *✓ MATCHES: Geico Insurance Company*
- [ ] Geico Insurance Company - BI #8838008180000001 — *✓ MATCHES: Geico Insurance Company*
- [ ] Mobilitas Insurance Company — *✓ MATCHES: Mobilitas Insurance Company*
- [ ] Mobilitas Insurance Company (BI claim) — *✓ MATCHES: Mobilitas Insurance Company*
- [ ] Mobilitas Insurance Company - BI #250-068-9702 — *✓ MATCHES: Mobilitas Insurance Company*

### Client (1 consolidated)
- [ ] Jaysha Aponte — *✓ MATCHES: Jaysha Aponte*

### Defendant (1 consolidated)
- [ ] Yusneiry Cruz Torres — *✓ MATCHES: Yusneiry Cruz Torres (from defendants)*

### Insurer (6 consolidated)
- [ ] At-fault insurer (Claim #250-068-9702) — *IGNORED - generic reference*
- [ ] Geico Insurance Company — *✓ MATCHES: Geico Insurance Company*
- [ ] Mobilitas Insurance Company — *✓ MATCHES: Mobilitas Insurance Company*
- [ ] Progressive Group of Insurance Companies — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] at-fault party's insurance — *IGNORED - generic term*

### LawFirm (1 consolidated)
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### MedicalProvider (6 consolidated)
- [ ] East Broadway Family Health Center — *✓ MATCHES: East Broadway Family Health Center*
- [ ] Family Health Centers - Portland — *✓ MATCHES: Family Health Centers - Portland*
- [ ] Louisville Metro EMS — *✓ MATCHES: Louisville Metro EMS*
- [ ] Starlite Chiropractic — *✓ MATCHES: Starlite Chiropractic*
- [ ] ULP Emergency — *✓ MATCHES: ULP Emergency*
- [ ] Norton Audubon Hospital — *✓ MATCHES: Norton Audubon Hospital*

### Organization (2 consolidated)
- [ ] CSAA — *IGNORED - insurance abbreviation*
- [ ] Suburban Towing — *✓ MATCHES: Suburban Towing (from vendors)*

### PIPClaim (4 consolidated)
- [ ] PIPClaim: Progressive Insurance Company (Adjuster: Monica Jones) — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company - PIP #25-311A13973 — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company PIP claim (Jaysha Aponte) — *✓ MATCHES: Progressive Insurance Company*

### UMClaim (1 consolidated)
- [ ] Uninsured motorist coverage — *IGNORED - generic term*

### Vendor (1 consolidated)
- [ ] Suburban Towing — *✓ MATCHES: Suburban Towing*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships