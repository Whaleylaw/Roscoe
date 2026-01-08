# Relationship Review: Forrest-Muss-MVA-07-20-2025

**Total Episodes:** 6

**Total Proposed Relationships:** 11


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (1)
- Little Clinic

### Insurance Claims (1)
- **BIClaim**: North American Risk Services

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### BIClaim (1 consolidated)
- [ ] North American Risk Services — *✓ MATCHES: North American Risk Services*

### Client (1 consolidated)
- [ ] Forrest Muss — *✓ MATCHES: Forrest Muss*

### MedicalProvider (1 consolidated)
- [ ] Little Clinic — *✓ MATCHES: Little Clinic*

### Organization (2 consolidated)
- [ ] McDonald's Corporation — *✓ MATCHES: McDonald's (from directory)*
- [ ] McDonald's Store #12096 — *✓ MATCHES: McDonald's (from directory)*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships