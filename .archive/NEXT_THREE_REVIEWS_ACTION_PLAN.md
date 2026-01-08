# Next Three Reviews - Action Plan

**Files:** Anella-Noble, Antonio-Lopez, Ashlee-Williams

---

## Anella-Noble-MVA-01-03-2021

### **Actions Needed:**

**Attorneys:**
1. David Klapheke - ? NEW → Research and add (need contact info)

**Court:**
1. Jefferson Circuit Court (21-CI-004985) → **Jefferson County Circuit Court, Division V**
   - User annotation: "Jarrison Circuit Court, Division 5" (typo for Jefferson)

**Defendants:**
1. Estate of DeShawn Ford - ? NEW → Add to defendants.json
2. Virginia Sewell - from directory → Add to defendants.json

**Insurers:**
1. Aetna Life, Anthem Medicaid - from directory → Verify in insurers.json

**PIPClaim:**
1. "Liberty Mutual PIP log" → Ignore (add to IGNORE_ENTITIES)

---

## Antonio-Lopez-MVA-11-14-2025

### **CRITICAL - Related Cases:**

**User Note:** "They're all in the same accident. We need to create a relationship that can relate cases."

**4 Clients in Same Accident:**
1. Antonio Lopez
2. A'zaire Lopez
3. Michae Guyton
4. Mi'ayla Lopez

**Action:**
- Check if these exist in clients.json
- If they exist as separate cases, create RELATED_ACCIDENT relationship
- This is a NEW relationship type we need to add to schema

### **Wrong Medical Provider Matches:**
1. "UofL Hospital" → Matched to "ARH McDowell Clinic" - WRONG!
2. "UofL downtown" → Matched to "Norton Hospital Downtown" - WRONG!

**Should match:** UofL Health - UofL Hospital or similar

### **Organization:**
1. "New Albany Police Department" → User says "I had this" (should match)
2. Kentucky PLLC, University of Louisville, UofL Health Inc. → All "Ignore"

### **UIMClaim:**
1. "Underinsured motorist coverage..." → Ignore

---

## Ashlee-Williams-MVA-08-29-2023

### **CRITICAL - Related Cases (Same as Antonio-Lopez):**

**User Note:** "We have a case for Duane Ward as well. We need to use the new relationship to link cases."
**Also:** "Ashley, Dwayne, and Julmonzhae, all link together"

**3 Clients/Cases to Link:**
1. Ashlee K. Williams (this case)
2. Dewayne Ward (separate case exists)
3. Julmonzhae Moore (separate case exists)

**Action:** Same RELATED_ACCIDENT relationship needed

### **Attorneys to Add:**

**With Contact Info Provided:**
1. **Dennis Cantrell** - Stoll Keenon Ogden PLLC
   - 334 North Senate Avenue, Indianapolis, IN 46204
   - P: 317-464-1100
   - Email: Dennis.cantrell@skofirm.com

2. **James Kamensky, Esq.** - From https://kpattorney.com/

3. **Scott Stout** - Stout & Heuke Law Office
   - 300 High Rise Drive, Suite 292, Louisville, KY 40213
   - P: 502-966-3347
   - F: 502-966-9394

4. **Zachary Reichle, Esq.** - Stoll Keenon Ogden PLLC
   - 334 North Senate Avenue, Indianapolis, IN 46204
   - P: 317-224-2473

**Paralegals (CaseManager):**
1. **Janet Weile** - Paralegal at Stoll Keenon Ogden
2. **Lexi Graham** - Paralegal (also appears as "L. Graham")
   - Email: lgraham@kpattorney.com

**Mediator:**
1. **Larry Church** - https://www.nadn.org/larry-church

### **Law Firms to Add:**
1. **Kamensky & Patteson, LLP**
2. **Stoll Keenon Ogden PLLC** (also known as "Skofirm")
   - 334 North Senate Avenue, Indianapolis, IN 46204
3. **Stout & Heuke Law Office** (also "Stout & Heuke")
   - 300 High Rise Drive, Suite 292, Louisville, KY 40213

### **Consolidations:**
1. Atty. Whaley → Aaron G. Whaley
2. Scott Stout / Scott Stoutheukelaw → Scott Stout
3. L. Graham / Lexi Graham → Lexi Graham
4. Skofirm / Stoll Keenon Ogden PLLC → Stoll Keenon Ogden PLLC
5. Stout & Heuke / Stout & Heuke Law Office → Stout & Heuke Law Office

### **Adjusters:**
1. **Carolyn Hudson** - Liberty Mutual PIP adjuster
   - Phone: 317-975-6696
2. **Ebon I. Moore** - from directory, Liberty Mutual adjuster

### **Clients:**
1. **Daquan Graham** - Co-plaintiff
   - Phone: 502-909-5533

### **Defendants:**
1. **Naomi Robinson** - Already added earlier

### **Court:**
All 6 Floyd variants → **Floyd County Circuit Court** (Indiana, not Kentucky)
- Need to determine division from case number 22D03-2501-CT-000157

### **Ignore:**
1. "Naomi Richardson's attorney"
2. "Louisville Accident Law Firm"
3. "BI Claim #054658453-01 (Liberty Mutual)"
4. "Underinsured motorist coverage..."
5. Organization wrong matches

---

## NEW Relationship Type Needed

### **RELATED_ACCIDENT**

**Purpose:** Link multiple cases from same accident event

**Structure:**
```cypher
(Case {name: "Ashlee-Williams-MVA-08-29-2023"})-[:RELATED_ACCIDENT {
  accident_date: "2023-08-29",
  accident_type: "same_incident"
}]->(Case {name: "Dewayne-Ward-MVA-8-29-2023"})

(Case {name: "Ashlee-Williams"})-[:RELATED_ACCIDENT]->(Case {name: "Julmonzhae-Moore-MVA-8-29-2023"})
```

**Use Case:**
- Query all cases from same accident
- Aggregate damages across related cases
- Track multi-plaintiff litigation

**Need to add to:**
- EDGE_TYPE_MAP in graphiti_client.py
- Case relationship definitions

---

## Summary

**Entities to Add: ~15**
- 1 Attorney (David Klapheke - research needed)
- 4 Attorneys with full contact info
- 2 Paralegals (CaseManager)
- 1 Mediator (Larry Church)
- 3 Law Firms
- 2 Adjusters
- 2-3 Defendants
- 1 Client (Daquan Graham)

**Court Corrections: 2 cases**
- Anella-Noble → Jefferson Division V
- Ashlee-Williams → Floyd County Circuit Court (all 6 variants)

**Wrong Matches to Fix: 2**
- UofL Hospital → (not ARH McDowell)
- UofL downtown → (not Norton)

**New Relationship Type:**
- RELATED_ACCIDENT (Case → Case)

**Ignore Patterns: 7 new**

---

**Ready to apply these changes manually?**
