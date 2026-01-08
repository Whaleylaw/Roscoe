# Relationship Review: Taylor-Thompson-MVA-12-06-2024

**Total Episodes:** 11

**Total Proposed Relationships:** 30


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Attorney (5 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] John Smith — *✓ MATCHES: Dr. John C. Smith (licensed KY doctor), not Attorney*
- [ ] Justin Chumbley — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Kelsey Browning — *IGNORED - need more info*
- [ ] Morgan & Morgan attorney — *IGNORED - generic reference*

### Client (1 consolidated)
- [ ] Taylor Thompson — *✓ MATCHES: Taylor Thompson*

### Insurer (1 consolidated)
- [ ] Medicaid — *IGNORED - government program*

### LawFirm (2 consolidated)
- [ ] Morgan and Morgan — *✓ MATCHES: Morgan and Morgan*
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### LienHolder (1 consolidated)
- [ ] Claims Angel — *IGNORED - service provider*

### MedicalProvider (1 consolidated)
- [ ] Aptiva Health — *✓ MATCHES: Aptiva Health Health*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships