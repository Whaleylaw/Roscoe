# Relationship Review: Abigail-Whaley-MVA-10-24-2024

**Total Episodes:** 21

**Total Proposed Relationships:** 46


---

## 1. Existing Entities in Graph

*(These are already in the graph for this case)*


### Medical Providers (4)
- Baptist Health Breckenridge Imaging Medical Group Neurology (neurology)
- Norton Brownsboro Hospital (hospital)
- ProRehab Prospect (physical therapy)
- William Haney

### Insurance Claims (2)
- **BIClaim**: American Family Insurance
  - Adjuster: Laura Zahringer
- **PIPClaim**: SafeCo Insurance Company
  - Adjuster: Lauren Smith

---

## 2. Proposed Entity Mentions (from LLM extraction)

*(Consolidated duplicates, showing matches to existing entities)*


### Adjuster (2 consolidated)
- [ ] Laura Zahringer — *✓ MATCHES: Laura Zahringer*
- [ ] Lauren Smith — *✓ MATCHES: Lauren Smith*

### Attorney (1 consolidated)
- [ ] Aaron Whaley — *✓ MATCHES: Aaron G. Whaley (WHALEY ATTORNEY, not Attorney)*

### BIClaim (2 consolidated)
- [ ] American Family Insurance — *✓ MATCHES: American Family Insurance*
- [ ] BIClaim - American Family Insurance — *✓ MATCHES: American Family Insurance*

### Client (1 consolidated)
- [ ] Abigail Whaley — *✓ MATCHES: Abigail Whaley*

### Insurer (3 consolidated)
- [ ] American Family Insurance — *✓ MATCHES: American Family Insurance*
- [ ] SafeCo — *✓ MATCHES: SafeCo Insurance Company*
- [ ] SafeCo Insurance Company — *✓ MATCHES: SafeCo Insurance Company*

### LawFirm (1 consolidated)
- [ ] Whaley Law Firm — *✓ MATCHES: The Whaley Law Firm*

### MedicalProvider (4 consolidated)
- [ ] Baptist Health Breckenridge Imaging Medical Group Neurology — *✓ MATCHES: Baptist Health Breckenridge Imaging Medical Group Neurology*
- [ ] Norton Brownsboro Hospital — *✓ MATCHES: Norton Brownsboro Hospital*
- [ ] ProRehab Prospect — *✓ MATCHES: ProRehab Prospect*
- [ ] William Haney — *✓ MATCHES: William Haney*

### PIPClaim (3 consolidated)
- [ ] PIPClaim - SafeCo Insurance Company — *✓ MATCHES: SafeCo Insurance Company*
- [ ] SafeCo Insurance Company — *✓ MATCHES: SafeCo Insurance Company*
- [ ] SafeCo Insurance Company (Adjuster: Lauren Smith) — *✓ MATCHES: SafeCo Insurance Company*

---

## 3. Review Actions


**For each proposed entity marked '? NEW':**
- [ ] **Map to existing** (name mismatch - e.g., 'State Farm' vs 'State Farm Insurance')
- [ ] **Ignore** (not relevant - e.g., mentions of staff, general terms)
- [ ] **Create new** (valid entity not yet in graph)

**After review:**
- Run ingestion script to create Episode nodes and ABOUT relationships