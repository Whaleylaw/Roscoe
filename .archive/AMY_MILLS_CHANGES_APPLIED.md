# Amy Mills Review - Changes Applied

**Status:** 5 of 8 tasks complete

---

## ✅ Completed

### **1. Deleted Incorrect Law Firm**
- ❌ Removed "Whaley Harrison & Thorne, PLLC" from lawfirms.json
- **Reason:** User confirmed this law firm does not exist
- **Impact:** Law firms: 36 → 35

### **2. Fixed WHT Law Mapping**
- **Old:** WHT Law → Whaley Harrison & Thorne, PLLC
- **New:** WHT Law → Ward, Hocker & Thornton, PLLC
- **Also added:** Whitt, Catron & Henderson → Ward, Hocker & Thornton
- **File:** generate_review_docs.py lines 475-482

### **3. Bobby Evans - Witness**
- Already exists in witnesses.json ✓
- Marked as bank employee witness

### **4. Added Aetna as LienHolder**
- Aetna can be both Insurer AND LienHolder
- Added to lienholders.json
- lien_type: ERISA
- Total lienholders: 50 → 51

### **5. Added 5 Vendors**
Added to vendors.json:
- Commonwealth IME (independent_medical_examination)
- PMR Life Care Plans, LLC (life_care_planner)
- BioKinetics (biomechanics_expert)
- David Johnson (expert_witness)
- Vocational Economics (vocational_expert)

**Note:** National Academy of Distinguished Neutrals (NADN) already existed
**Total vendors:** 40 → 45

---

## ⏳ In Progress

### **6. Knox Court Consolidation**
**Need to match:**
- Knox Circuit Court (Knox County, Kentucky) → Knox County Circuit Court
- Knox Circuit Court, Division II → Knox County Circuit Court, Division II
- Knox County Clerk → (need to find in court_clerks.json)

**Current mappings exist but need verification against new court directory**

### **7. NADN Variants Consolidation**
**Need to add to KNOWN_MAPPINGS:**
```python
"NADA": "National Academy of Distinguished Neutrals",
"NADN": "National Academy of Distinguished Neutrals",
"NADN (America's Premier Mediators & Arbitrators)": "National Academy of Distinguished Neutrals",
"National Arbitration and Dispute Association": "National Academy of Distinguished Neutrals",
```

### **8. Additional Mappings**
**Add to KNOWN_MAPPINGS:**
```python
"Sarena (Whaley Law Firm)": "Sarena Tuttle",
```

**Add to IGNORE_ENTITIES:**
```python
"Bob Hammonds",
"Defense Attorney for Forcht Bank",
"lfarah@whtlaw.com",
# All BIClaim generic terms
"Amy Mills - personal injury claim",
"Bodily Injury (TBI, surgeries, lost income)",
"Bodily Injury claim",
"Impairment of future earning capacity claim",
"Personal Injury Claim",
```

---

## 📝 Additional Entities Needed

### **Expert:**
- **Linda Jones** (economist expert witness)
  - Works at: Vocational Economics
  - expert_type: "economist"
  - Need to create Expert entity and link to Vocational Economics

### **Organization:**
- **Retired Judges Mediation & Arbitration Services, Inc.**
  - Related to: Hon. Thomas J. Knopf (Ret.)
  - org_type: "mediation_service"

---

## 🔍 Items Needing Research

### **1. Alexander Landfield PLLC**
User says: "This is a Dr."
- Currently in organizations
- Need to determine: Is this Dr. Alexander Landfield (person) or a medical practice?

### **2. Knox County Clerk**
User says: "This should match with the new court directory"
- Need to find clerk name in court_clerks.json
- Likely matches to specific clerk for Knox County Circuit Court

### **3. Amanda Murphy**
User annotation: (no specific instruction, line 90)
- Need to check if she's in court_clerks.json
- Likely Knox County court clerk

---

## Next Steps

1. Add NADN variants to KNOWN_MAPPINGS
2. Add ignore patterns to IGNORE_ENTITIES
3. Create Linda Jones as Expert entity
4. Create Retired Judges Mediation as Organization
5. Research Alexander Landfield
6. Match Knox courts/clerks to new court directory
7. Update Amy Mills review file with corrections
8. Document all changes

---

**Ready to continue with remaining 3 tasks?**
