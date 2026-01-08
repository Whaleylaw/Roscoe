# Relationship Review: Malcom-Glass-Jones-MVA-10-2-2024

**Total Episodes:** 86

**Total Proposed Relationships:** 174


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (1)
- Starlite Chiropractic (chiropractic)

### Insurance Claims (3)
- **BIClaim**: Kentucky Farm Bureau
  - Adjuster: Pat Hargadon
- **BIClaim**: Shelter Insurance
  - Adjuster: Cole Barnes
- **PIPClaim**: Shelter Insurance
  - Adjuster: Emily Friedrich

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (3 consolidated)
- [ ] Cole Barnes — *✓ MATCHES: Cole Barnes*
- [ ] Emily Friedrich — *✓ MATCHES: Emily Friedrich*
- [ ] Pat Hargadon — *✓ MATCHES: Pat Hargadon*

### Attorney (3 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*
- [ ] Aries — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Attorney)*
- [ ] Aries Paul Peñaflor — *✓ MATCHES: Aries Penaflor (WHALEY STAFF → should be CaseManager, not Attorney)*

### BIClaim (4 consolidated)
- [ ] BIClaim - Shelter Insurance — *✓ MATCHES: Shelter Insurance*
- [ ] Kentucky Farm Bureau — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] Shelter Insurance BI claim — *✓ MATCHES: Shelter Insurance*
- [ ] Shelter Insurance Claim 3753979 — *✓ MATCHES: Shelter Insurance*

### Client (1 consolidated)
- [ ] Malcom Glass Jones — *✓ MATCHES: Malcom Glass-Jones*

### Defendant (1 consolidated)
- [ ] G'Asia Huffman — *IGNORED - defendant name only*

### Insurer (3 consolidated)
- [ ] Commonwealth of Kentucky — *✓ MATCHES: Commonwealth of Kentucky Dept. for Community Based Services (from directory)*
- [ ] Kentucky Farm Bureau — *✓ MATCHES: Kentucky Farm Bureau*
- [ ] Shelter Insurance — *✓ MATCHES: Shelter Insurance*

### LawFirm (1 consolidated)
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### MedicalProvider (1 consolidated)
- [ ] Starlite Chiropractic — *✓ MATCHES: Starlite Chiropractic*

### Organization (1 consolidated)
- [ ] Shelbyville County Sheriff's Office — *✓ MATCHES: Shelby County Sheriff Office*

### PIPClaim (3 consolidated)
- [ ] PIP AT3753979 — *IGNORED - claim number only*
- [ ] PIPClaim: Shelter Insurance — *✓ MATCHES: Shelter Insurance*
- [ ] PIPClaim: Shelter Insurance (Adjuster: Emily Friedrich) — *✓ MATCHES: Shelter Insurance*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships