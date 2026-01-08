# Relationship Review: Torrey-Green-MVA-9-3-2025

**⚠️ CONSOLIDATED INTO PRIMARY FILE: review_Torrey-Green-MVA-9-03-2025.md**

**Total Episodes:** 13

**Total Proposed Relationships:** 19


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (1 consolidated)
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Adjuster)*

### Client (1 consolidated)
- [ ] Torrey Green — *✓ MATCHES: Torrey Green*

### Defendant (1 consolidated)
- [ ] Cory Stephenson — *IGNORED - not defendant (client in different case)*

### Insurer (1 consolidated)
- [ ] Elco Insurance — *✓ MATCHES: Elco Insurance* 

### MedicalProvider (1 consolidated)
- [ ] Starlite — *✓ MATCHES: Starlite Chiropractic*

### PIPClaim (1 consolidated)
- [ ] PIP claim (Elco Insurance) — *✓ MATCHES: Elco Insurance (Insurer, not PIPClaim)*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships