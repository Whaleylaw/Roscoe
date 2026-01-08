# Relationship Review: Bryson-Brown-MVA-6-29-2025

**Total Episodes:** 16

**Total Proposed Relationships:** 31


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (2)
- Synergy Injury Care & Rehab Diagnostics Injury Care & Rehab Diagnostics (physical therapy)
- UofL Health – Brown Cancer Center – Medical Oncology - Mary & Elizabeth UofL Health – Brown Cancer Center – Medical Oncology – Mary & Elizabeth Hospital (hospital)

### Insurance Claims (2)
- **PIPClaim**: Allstate Insurance
  - Adjuster: Guillermo Callejas
- **BIClaim**: State Farm Insurance Company

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (1 consolidated)
- [ ] Guillermo Callejas — *✓ MATCHES: Guillermo Callejas*

### BIClaim (1 consolidated)
- [ ] State Farm Insurance Company (Claim #1787F478S) — *✓ MATCHES: State Farm Insurance Company*

### Client (2 consolidated)
- [ ] Bryson Brown — *✓ MATCHES: Bryson Brown*
- [ ] Tymon Brown — *IGNORED - not client*

### Insurer (2 consolidated)
- [ ] Allstate Insurance — *✓ MATCHES: Allstate Insurance*
- [ ] State Farm Insurance Company — *✓ MATCHES: State Farm Insurance Company*

### MedicalProvider (2 consolidated)
- [ ] St. Mary Hospital — *✓ MATCHES: Norton Audubon Hospital (UofL Mary & Elizabeth)*
- [ ] Synergy Injury Care & Rehab Diagnostics Injury Care & Rehab Diagnostics — *✓ MATCHES: Synergy Injury Care & Rehab Diagnostics Injury Care & Rehab Diagnostics*

### PIPClaim (2 consolidated)
- [ ] Allstate Insurance PIPClaim — *✓ MATCHES: Allstate Insurance*
- [ ] Allstate PIP #0799220033 — *✓ MATCHES: Allstate Insurance (generic claim reference)*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships
