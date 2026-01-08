# Relationship Review: Carmelita-Wilson-MVA-10-12-2025

**Total Episodes:** 12

**Total Proposed Relationships:** 17


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Attorney (1 consolidated)
- [ ] Justin — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*

### Client (1 consolidated)
- [ ] Carmelita Wilson — *CHECK clients.json - should exist as client*

### LawFirm (1 consolidated)
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### MedicalProvider (1 consolidated)
- [ ] Terrence Donahue — *✓ MATCHES: Dr. Terrence P. Donohue (licensed KY doctor, valid MedicalProvider)*

### Vendor (1 consolidated)
- [ ] Vinesign — *IGNORED - e-signature software*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships
