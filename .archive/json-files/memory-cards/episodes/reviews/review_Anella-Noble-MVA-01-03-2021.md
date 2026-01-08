# Relationship Review: Anella-Noble-MVA-01-03-2021

**Total Episodes:** 1

**Total Proposed Relationships:** 14


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Attorney (2 consolidated)
- [ ] David Klapheke — *? NEW - PENDING RESEARCH* (Need contact info and law firm) He's at Dinsmore & Shohl LLP 101 South Fifth Street Suite 2500 Louisville, KY 40202 Ph: 502-540-2539 Email: david.klapheke@dinsmore.com
- [ ] Renee Hoskins — *✓ MATCHES: Renee Hoskins*

### Client (1 consolidated)
- [ ] Anella Noble — *✓ MATCHES: Anella Noble*

### Court (1 consolidated)
- [ ] Jefferson Circuit Court (21-CI-004985) — *✓ MATCHES: Jefferson County Circuit Court, Division V*

### Defendant (2 consolidated)
- [ ] Estate of DeShawn Ford — *✓ ADDED to defendants.json*
- [ ] Virginia Sewell — *✓ ADDED to defendants.json (from Virginia P. Sewell in directory)*

### Insurer (5 consolidated)
- [ ] Aetna Life — *✓ MATCHES: Aetna Life Insurance Company (from directory)*
- [ ] Anthem Medicaid — *✓ MATCHES: Anthem (from directory)*
- [ ] Liberty Mutual — *✓ MATCHES: Liberty Mutual Insurance Company*
- [ ] Safeco — *✓ MATCHES: SafeCo Insurance Company*
- [ ] State Farm — *✓ MATCHES: State Farm Insurance Company*

### LawFirm (1 consolidated)
- [ ] Smith & Hoskins — *✓ MATCHES: Smith & Hoskins PLLC*

### PIPClaim (1 consolidated)
- [ ] Liberty Mutual PIP log — *IGNORED - generic claim reference*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships
