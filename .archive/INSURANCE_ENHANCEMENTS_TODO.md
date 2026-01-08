# Insurance Schema Enhancements - TODO

**Status:** Partially complete - need to finish

---

## Completed ✅

1. ✅ Added `InsurancePolicy` class (line 106)
2. ✅ Added `InsurancePayment` class (line 132)
3. ✅ Added denial/appeal fields to `PIPClaim` (lines 161-166)

---

## Still Need to Complete

### 1. Add Denial/Appeal Fields to Other Claim Types

**Add to BIClaim, UMClaim, UIMClaim, WCClaim (same fields as PIPClaim):**
```python
# Denial and appeal tracking
denial_reason: Optional[str] = Field(default=None, description="Reason for denial if coverage denied")
denial_date: Optional[date] = Field(default=None, description="Date of denial")
appeal_filed: Optional[bool] = Field(default=None, description="Whether appeal was filed")
appeal_date: Optional[date] = Field(default=None, description="Date appeal filed")
appeal_outcome: Optional[str] = Field(default=None, description="granted | denied | pending")
```

**Classes to update:**
- BIClaim (line ~169)
- UMClaim (line ~180)
- UIMClaim (line ~195)
- WCClaim (line ~212)

### 2. Add InsurancePolicy and InsurancePayment to ENTITY_TYPES

**Location:** ENTITY_TYPES list (~line 788)

**Add after Adjuster:**
```python
Adjuster,         # Insurance adjuster
InsurancePolicy,  # Insurance policy (NEW)
InsurancePayment, # Individual payment from insurer (NEW)
```

### 3. Add InsurancePolicy Relationships to EDGE_TYPE_MAP

**Location:** EDGE_TYPE_MAP (~line 1260)

**Add new section:**
```python
# =========================================================================
# Insurance Policy relationships (NEW)
# =========================================================================
("Client", "InsurancePolicy"): ["HasPolicy"],
("Defendant", "InsurancePolicy"): ["HasPolicy"],
("InsurancePolicy", "Insurer"): ["WithInsurer"],
("PIPClaim", "InsurancePolicy"): ["UnderPolicy"],
("BIClaim", "InsurancePolicy"): ["UnderPolicy"],
("UMClaim", "InsurancePolicy"): ["UnderPolicy"],
("UIMClaim", "InsurancePolicy"): ["UnderPolicy"],
("WCClaim", "InsurancePolicy"): ["UnderPolicy"],
("MedPayClaim", "InsurancePolicy"): ["UnderPolicy"],
```

### 4. Add InsurancePayment Relationships to EDGE_TYPE_MAP

**Add:**
```python
# Insurance Payment relationships (NEW)
("PIPClaim", "InsurancePayment"): ["MadePayment"],
("BIClaim", "InsurancePayment"): ["MadePayment"],
("UMClaim", "InsurancePayment"): ["MadePayment"],
("UIMClaim", "InsurancePayment"): ["MadePayment"],
("WCClaim", "InsurancePayment"): ["MadePayment"],
("InsurancePayment", "Insurer"): ["From"],
("InsurancePayment", "Bill"): ["PaidBill"],  // Track which bills were paid
```

### 5. Add Defendant Insurance Links

**Add to existing defendant relationships:**
```python
("Defendant", "Insurer"): ["HasInsurance"],
("Defendant", "InsurancePolicy"): ["HasPolicy"],
("BIClaim", "Defendant"): ["CoversDefendant"],
```

### 6. Update LienHolder.lien_type Description

**Location:** LienHolder class (~line 332)

**Change:**
```python
lien_type: Optional[str] = Field(default=None, description="medical, ERISA, Medicare, Medicaid, child_support, case_funding, workers_comp, collection, other")
```

**Add "workers_comp" to the list**

---

## Why These Changes Matter

**InsurancePolicy:**
- One auto policy → PIP claim + UM claim + UIM claim (all from same policy)
- Track policy limits separately
- Know when policy expires

**InsurancePayment:**
- PIP pays $2K (advance 1)
- PIP pays $3K (advance 2)
- PIP pays $5K (final payment)
- Track payment history, not just final total

**Denial/Appeal:**
- Coverage denied on 2024-03-15
- Appeal filed 2024-03-20
- Appeal granted 2024-04-10
- Track dispute timeline

**Defendant Insurance:**
- Defendant has State Farm policy #123
- BI claim against that specific policy
- Clear linkage

---

## Next Steps

1. Finish adding denial/appeal fields to remaining claim types
2. Add InsurancePolicy and InsurancePayment to ENTITY_TYPES
3. Add all new relationships to EDGE_TYPE_MAP
4. Update LienHolder lien_type
5. Test schema loads without errors

**Estimated time:** 10 minutes to complete

Would you like me to finish these remaining changes now?
