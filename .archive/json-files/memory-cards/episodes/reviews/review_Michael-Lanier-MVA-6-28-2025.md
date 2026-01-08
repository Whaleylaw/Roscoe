# Relationship Review: Michael-Lanier-MVA-6-28-2025

**Total Episodes:** 7

**Total Proposed Relationships:** 18


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (1)
- Allstar Chiropractic (chiropractic)

### Insurance Claims (2)
- **PIPClaim**: None
- **BIClaim**: Progressive Insurance Company

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### BIClaim (2 consolidated)
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] Progressive Insurance Company (Claim 25-471551085) — *✓ MATCHES: Progressive Insurance Company*

### Client (4 consolidated)
- [ ] Christopher Lanier — *✓ MATCHES: Christopher Lanier*
- [ ] James Lanier — *✓ MATCHES: James Lanier*
- [ ] Michael Lanier — *✓ MATCHES: Michael Lanier*
- [ ] Rebecca Lanier — *✓ MATCHES: Rebecca Lanier*

### Insurer (2 consolidated)
- [ ] Progressive Insurance Company — *✓ MATCHES: Progressive Insurance Company*
- [ ] State Farm — *✓ MATCHES: State Farm Insurance Company*

### MedicalProvider (1 consolidated)
- [ ] Allstar Chiropractic — *✓ MATCHES: Allstar Chiropractic*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships