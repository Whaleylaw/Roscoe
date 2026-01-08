# Entities Added from Azaire-Lopez and Brenda-Lang Reviews

**Date:** December 30, 2025

---

## Entity JSON Files Updated

### **attorneys.json** (+3 attorneys)

1. **Chauncey Hiestand**
   - Role: defense_counsel
   - Firm: Winton & Hiestand Law Group
   - Contact: https://louisvillelawoffice.com/

2. **Gregory Scott Gowen**
   - Role: defense_counsel
   - Firm: Fulton, Maddox, Dickens & Stewart PLLC
   - Email: sgowen@fmdlegal.com
   - Contact: https://www.fmdlegal.com/people/scott-gowen/

3. **Allison L. Rief**
   - Role: defense_counsel
   - Firm: (unknown)
   - Note: From directory, need firm info

---

### **lawfirms.json** (+3 law firms)

1. **Dilbeck & Myers**
   - Website: https://www.dilbeckandmyers.com/

2. **Fulton, Maddox, Dickens & Stewart PLLC**
   - Aliases: ["FMD Legal"]
   - Website: https://www.fmdlegal.com/

3. **Isaacs and Isaacs Law Firm**
   - Aliases: ["Isaacs & Isaacs"]
   - Website: https://wewin.com/

---

### **vendors.json** (+1 vendor)

1. **Wendy McLaughlin**
   - Type: court_reporting
   - LinkedIn: https://www.linkedin.com/in/wendy-mclaughlin-792793a/

---

### **defendants.json** (+1 defendant)

1. **Marcus Hamlet**
   - Note: From directory, defendant in Brenda Lang case

---

### **organizations.json** (+3 organizations)

1. **Louisville Metro Government**
   - Type: government
   - Note: Louisville/Jefferson County consolidated government (defendant in TARC case)

2. **Louisville Metro Police Department**
   - Type: law_enforcement
   - Note: LMPD

3. **Jefferson County Attorney's Office**
   - Type: government
   - Note: Louisville City Attorney's Office / Jefferson County government legal office

---

## New KNOWN_MAPPINGS Added to Scripts

```python
# Law firm variants
"Winton and Hiestand": "Winton & Hiestand Law Group",
"Whaley & Whaley Law Firm": "The Whaley Law Firm",
"FMD Legal": "Fulton, Maddox, Dickens & Stewart PLLC",
"Isaacs & Isaacs": "Isaacs and Isaacs Law Firm",

# Vendor variants
"Kentuckiana Reporters Scheduling Department": "Kentuckiana Court Reporters",
"Kentuckiana Reporters": "Kentuckiana Court Reporters",

# Attorney variants
"Reif": "Allison L. Rief",
"Scott Gowen": "Gregory Scott Gowen",

# Organization variants (Louisville Metro)
"Lou Metro Gov": "Louisville Metro Government",
"Louisville Metro (Metro Government)": "Louisville Metro Government",
"Louisville Metropolitan Government": "Louisville Metro Government",
"Louisville/Jefferson County government": "Louisville Metro Government",
"Metro Government": "Louisville Metro Government",

# Organization variants (County Attorney)
"City of Louisville (Scott Gowen)": "Jefferson County Attorney's Office",
"Louisville City Attorney's Office": "Jefferson County Attorney's Office",

# Defendant variants
"M Hamlet": "Marcus Hamlet",
```

---

## New IGNORE_ENTITIES Added

```python
# From Azaire-Lopez/Brenda-Lang reviews
"CourtNet (envelope 6555977)", "CourtNet Envelope 6650387",
"DC (defense counsel)", "DC Lou Metro",
"AF Driver, Jeff", "AW & BK",
"mother (unnamed)", "Wendy Cotton",
"GoAnywhere", "Paubox", "20 Second Scheduler",
"OMB Medical Records Requests", "AdaptHealth", "Ventra Health",
"Microsoft Corporation",
"sgowen@fmdlegal.com (S. Gowen)",  # Email address, not entity
```

---

## Script Fixes Applied

### **Critical Bug Fixed:** Missing Entity Type Loading

**Problem:** `load_global_entities()` was only loading 10 out of 17 entity types

**Fixed:** Now loads ALL entity types:
- ✅ vendors.json (45 → 46 vendors)
- ✅ experts.json (1 expert)
- ✅ witnesses.json (1 witness)
- ✅ organizations.json (385 → 388 organizations)
- ✅ circuit_divisions.json (86 divisions)
- ✅ district_divisions.json (94 divisions)

### **Critical Bug Fixed:** Missing Matching Logic

**Problem:** No matching logic for 7 entity types (always showed as "? NEW")

**Fixed:** Added matching logic for:
- ✅ Client → checks clients.json
- ✅ Court → checks divisions first (circuit, district), then courts
- ✅ Vendor → checks vendors.json
- ✅ Expert → checks experts.json
- ✅ Witness → checks witnesses.json
- ✅ Mediator → checks mediators.json
- ✅ Organization → checks organizations.json

---

## Total Entity Counts (Updated)

| Entity Type | Count | Change |
|-------------|-------|--------|
| Attorneys | 44 | +3 |
| Law Firms | 42 | +3 |
| Vendors | 46 | +1 |
| Defendants | 14 | +1 |
| Organizations | 388 | +3 |
| **TOTAL** | **45,911+** | **+11** |

---

## Review Status

**Approved:** 7 of 138 (5%)
- Abby-Sitgraves, Abigail-Whaley, Alma-Cristobal, Amy-Mills
- Anella-Noble, Antonio-Lopez, Ashlee-Williams ✓

**Ready for Approval (pending entity additions):**
- ❌ Azaire-Lopez (needs client verification for multi-accident group)
- ❌ Brenda-Lang (entities now added, ready for next regeneration)

**Remaining:** 131 files

---

## Next Steps

1. Add missing client entities for multi-client accidents:
   - Antonio Lopez, A'zaire Lopez, Michae Guyton, Mi'ayla Lopez

2. Regenerate all non-approved reviews again to apply:
   - New entity matches (Chauncey Hiestand, Gregory Gowen, etc.)
   - New consolidations (Winton & Hiestand, FMD Legal, etc.)
   - New ignore patterns

3. Mark Azaire-Lopez and Brenda-Lang as approved

4. Continue with next batch of reviews
