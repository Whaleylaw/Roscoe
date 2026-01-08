# Relationship Review: Rayshawn-Wilson-MVA-4-10-2025

**Total Episodes:** 9

**Total Proposed Relationships:** 19


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (4)
- Foundation Radiology Group, PC (radiology)
- Southeastern Emergency Services, LLC
- Starlite Chiropractic (chiropractic)
- UofL Health – Brown Cancer Center – Medical Oncology - Mary & Elizabeth UofL Health – Brown Cancer Center – Medical Oncology – Mary & Elizabeth Hospital (hospital)

### Insurance Claims (1)
- **PIPClaim**: Progressive Insurance Company

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Attorney (2 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*

### Client (1 consolidated)
- [ ] Rayshawn Wilson — *✓ MATCHES: Rayshawn Wilson*

### Defendant (1 consolidated)
- [ ] Quintez Massey — *? NEW* Ignore.

### Insurer (1 consolidated)
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*

### LawFirm (1 consolidated)
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### MedicalProvider (1 consolidated)
- [ ] St. Mary's Medical Center ER — *? NEW* Should be St. Mary and Elizabeth Hospital.

### PIPClaim (2 consolidated)
- [ ] PIP claim - Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships