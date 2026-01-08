# Relationship Review: Corey-Todd-MVA-WC-8-2-2025

**Total Episodes:** 7

**Total Proposed Relationships:** 21


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Attorney (1 consolidated)
- [ ] Justin — *✓ MATCHES: Justin Chumbley (WHALEY STAFF → should be CaseManager, not Attorney)*

### BIClaim (4 consolidated)
- [ ] Motor Vehicle Accident (MVA) / bodily injury claim — *IGNORED - generic claim description*
- [ ] Motor vehicle accident (MVA) component — *IGNORED - generic description*
- [ ] Motor vehicle accident / BI claim (Corey-Todd-MVA-WC-8-2-2025) — *IGNORED - case reference*
- [ ] Motor vehicle accident bodily injury claim (Aug 2, 2025) — *IGNORED - generic description*

### Client (1 consolidated)
- [ ] Corey Todd — *✓ MATCHES: Corey Todd*

### LawFirm (1 consolidated)
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### WCClaim (5 consolidated)
- [ ] Corey-Todd-MVA-WC-8-2-2025 — *IGNORED - case name reference*
- [ ] Workers' Compensation claim — *IGNORED - generic claim description*
- [ ] Workers' Compensation claim (Aug 2, 2025) — *IGNORED - generic description*
- [ ] Workers' compensation (WC) component — *IGNORED - generic description*
- [ ] Workers' compensation claim (Corey-Todd-MVA-WC-8-2-2025) — *IGNORED - case reference*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships
