# Amy Mills - Doctor Research Results

**Researched 8 doctors + Alexander Landfield in 20,732 KY doctor database**

---

## ✅ Found and Matched (4 doctors + 1 practice)

### **1. Dr. Alsorogi**
- **Match:** Dr. Mohammad S. Alsorogi
- **Specialty:** Neurology
- **Status:** Active Physician
- **Action:** Added to KNOWN_MAPPINGS

### **2. Dr. Kevin Magone, MD**
- **Match:** Dr. Kevin Magone
- **Specialty:** Orthopedic
- **Status:** Active Physician
- **Action:** Added to KNOWN_MAPPINGS

### **3. Dr. Shannon Voor**
- **Match:** Dr. Tyler John Van De Voort
- **Specialty:** Surgery
- **Status:** Inactive Physician
- **Note:** Close fuzzy match (Voor = Van De Voort)
- **Action:** Added to KNOWN_MAPPINGS

### **4. Alexander Landfield PLLC**
- **Match:** Dr. Alexander David Landfield
- **Specialty:** Neurology
- **Status:** Active Physician
- **Note:** User correct - it's both a doctor AND his practice
- **Action:** Added to KNOWN_MAPPINGS

---

## ⚠️ Ambiguous or Not Found (4 doctors)

### **1. Dr. Barefoot**
**Found 3 possibilities:**
- Dr. Jennifer A. Barefoot (General Medicine, Active)
- Dr. Julius J. Barefoot III (Addiction Medicine, Active)
- Dr. Robert Allen Barefoot Jr. (Family Medicine, Active)

**Need:** Episode context to determine which doctor

### **2. Dr. Hunt**
**Found 20+ possibilities including:**
- Dr. Alexandra Hunt (Emergency Medicine, Active)
- Dr. Philip G. Hunt (Orthopedic, Active)
- Dr. G. Jason Hunt (Orthopedic, Active)
- Dr. David E. Hunt (Pathology, Active)
- Dr. Drema K. Hunt (Family Medicine, Active)
- ... 15+ more

**Need:** Episode context to determine which doctor (specialty would help)

### **3. Dr. Lisa Manderino / Dr. Lisa Mandarino**
**Not found in KY database**
**User note:** "Dr. Lisa Mandarino works for Aptiva"

**Possibilities:**
- Name misspelled in episodes
- Licensed in another state (Aptiva has multi-state locations)
- Not a physician (NP, PA, or other provider)

**Need:** Verify spelling and credentials

### **4. Dr. Paul McCombs**
**Found:** Dr. Ricky J. McCombs (Gastroenterology, Active)
**Issue:** Different first name (Paul vs Ricky)

**Possibilities:**
- Paul is middle name (Ricky Paul McCombs)
- Different doctor
- Name error in episode extraction

**Need:** Verify first name

### **5. Dr. Richard Edelson**
**Not found in KY database**

**Possibilities:**
- Licensed in another state
- Name variation (Edelstein, Adelson, etc.)
- Not a physician

**Need:** Verify spelling and state

---

## Updated in Amy Mills Review

### **MedicalProvider Section (Lines 133-143):**

**Now Shows:**
```
- [ ] Dr. Alsorogi — *✓ MATCHES: Dr. Mohammad S. Alsorogi (licensed KY doctor - neurology)*
- [ ] Dr. Barefoot — *? NEW* (3 possible matches in KY database - need context)
- [ ] Dr. Hunt — *? NEW* (20+ possible matches in KY database - need context)
- [ ] Dr. Kevin Magone, MD — *✓ MATCHES: Dr. Kevin Magone (licensed KY doctor - orthopedic)*
- [ ] Dr. Lisa Manderino — *? NEW* (not in KY database - may practice in another state)
- [ ] Dr. Paul McCombs — *? NEW* (found Dr. Ricky J. McCombs - different first name)
- [ ] Dr. Richard Edelson — *? NEW* (not in KY database)
- [ ] Dr. Shannon Voor — *✓ MATCHES: Dr. Tyler John Van De Voort (licensed KY doctor - surgery, inactive)*
```

### **Organization Section (Line 162):**

**Now Shows:**
```
- [ ] Alexander Landfield PLLC — *✓ MATCHES: Dr. Alexander David Landfield (medical practice - neurologist)*
```

---

## Summary

**Matched:** 4 of 8 doctors (50%)
- Dr. Alsorogi ✓
- Dr. Magone ✓
- Dr. Voor ✓
- Alexander Landfield ✓

**Need Context:** 2 doctors
- Dr. Barefoot (3 options)
- Dr. Hunt (20+ options)

**Not in KY Database:** 3 doctors
- Dr. Lisa Manderino (works for Aptiva - may be out of state)
- Dr. Paul McCombs (found Ricky McCombs)
- Dr. Richard Edelson

**Next Steps:**
1. Check episode context for Dr. Barefoot and Dr. Hunt to determine specialty
2. Verify Dr. Lisa Manderino's credentials (NP vs MD, state license)
3. Verify Dr. Paul McCombs first name
4. Research Dr. Richard Edelson (spelling, state license)

**File Status:** Amy Mills review updated with all matches found. Clean and ready except for 4 ambiguous doctors needing context.
