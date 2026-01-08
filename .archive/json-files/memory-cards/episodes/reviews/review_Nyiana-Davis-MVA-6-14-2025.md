# Relationship Review: Nyiana-Davis-MVA-6-14-2025

**Total Episodes:** 23

**Total Proposed Relationships:** 44


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (2)
- Starlite Chiropractic (chiropractic)
- Norton Audubon Hospital (hospital)

### Insurance Claims (4)
- **BIClaim**: Progressive Insurance Company
  - Adjuster: Kim Francis
- **BIClaim**: Mobilitas Insurance Company
  - Adjuster: Martin Trujillo
- **PIPClaim**: Progressive Insurance Company
  - Adjuster: Kim Francis
- **PIPClaim**: Mobilitas Insurance Company
  - Adjuster: Brandon Igbo-Nwoke

### Liens (1)
- None

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (1 consolidated)
- [ ] Martin Trujillo — *✓ MATCHES: Martin Trujillo*

### Attorney (1 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*

### BIClaim (1 consolidated)
- [ ] BIClaim - Mobilitas Insurance Company — *✓ MATCHES: Mobilitas Insurance Company*

### Client (1 consolidated)
- [ ] Nyiana Davis — *✓ MATCHES: Nyiana Davis*

### Defendant (1 consolidated)
- [ ] Justice Akubia — *? NEW* Ignore

### Insurer (2 consolidated)
- [ ] Anthem — *✓ MATCHES: Anthem (from directory)*
- [ ] Mobilitas Insurance Company — *✓ MATCHES: Mobilitas Insurance Company*

### LawFirm (1 consolidated)
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### MedicalProvider (2 consolidated)
- [ ] Starlite Chiropractic — *✓ MATCHES: Starlite Chiropractic*
- [ ] Norton Audubon Hospital — *✓ MATCHES: Norton Audubon Hospital*

### Organization (1 consolidated)
- [ ] Lyft — *✓ MATCHES: Lyft*

### PIPClaim (4 consolidated)
- [ ] Mobilitas Insurance Company — *✓ MATCHES: Mobilitas Insurance Company*
- [ ] PIPClaim: Mobilitas Insurance Company (Adjuster: Brandon Igbo-Nwoke) — *✓ MATCHES: Mobilitas Insurance Company*
- [ ] PIPClaim: Progressive Insurance Company (Adjuster: Kim Francis) — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships