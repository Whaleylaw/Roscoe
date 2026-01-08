# New Relationship Patterns - Complete List

**Date:** January 4, 2026
**Total New Relationships:** 40+ patterns

---

## Medical Provider Hierarchy (11 new)

### Hierarchy Relationships

**1. Location → Facility**
```cypher
(Location: "Norton Orthopedic Institute - Downtown")-[:PART_OF]->(Facility: "Norton Orthopedic Institute")
```

**2. Facility → HealthSystem**
```cypher
(Facility: "Norton Orthopedic Institute")-[:PART_OF]->(HealthSystem: "Norton Healthcare")
```

**3. Facility → Location (reverse)**
```cypher
(Facility)-[:HAS_LOCATION]->(Location)
```

**4. HealthSystem → Facility (reverse)**
```cypher
(HealthSystem)-[:HAS_FACILITY]->(Facility)
```

### Treatment Relationships (Multi-Level)

**5. Client → Location**
```cypher
(Client)-[:TREATED_AT {specific_location: true}]->(Location)
```

**6. Client → Facility**
```cypher
(Client)-[:TREATED_AT {specific_location: false}]->(Facility)  // When location unknown
```

**7. Case → Location**
```cypher
(Case)-[:TREATING_AT]->(Location)
```

**8. Case → Facility**
```cypher
(Case)-[:TREATING_AT]->(Facility)
```

### Multi-Role Relationships (NEW)

**9. Case → Location (Defendant)**
```cypher
(Case)-[:DEFENDANT {role: "premise"}]->(Location: "Norton Hospital")
```

**10. Case → Facility (Defendant)**
```cypher
(Case)-[:DEFENDANT]->(Facility)
```

**11. Case → Location/Facility (Vendor)**
```cypher
(Case)-[:VENDOR_FOR {service: "medical_chronology"}]->(Location)
```

### Staff Relationships

**12. Doctor → Location**
```cypher
(Doctor)-[:WORKS_AT]->(Location)
```

**13. Doctor → Facility**
```cypher
(Doctor)-[:AFFILIATED_WITH]->(Facility)  // Works at multiple locations
```

### Document Relationships

**14. Document → Location/Facility**
```cypher
(Document)-[:FROM]->(Location)
```

---

## Medical Visit Relationships (7 new)

**15. Case → MedicalVisit**
```cypher
(Case)-[:HAS_VISIT]->(MedicalVisit)
```

**16. MedicalVisit → Location**
```cypher
(MedicalVisit {visit_date: "2024-03-15"})-[:AT_LOCATION]->(Location)
```

**17. MedicalVisit → Facility**
```cypher
(MedicalVisit)-[:AT_LOCATION]->(Facility)  // When location unknown
```

**18. MedicalVisit → Bill**
```cypher
(MedicalVisit)-[:HAS_BILL]->(Bill)
```

**19. MedicalVisit → Document**
```cypher
(MedicalVisit)-[:HAS_DOCUMENT]->(Document: "norton_ortho_2024_03_15.pdf")
```

**20. MedicalVisit → Doctor**
```cypher
(MedicalVisit)-[:SEEN_BY]->(Doctor)
```

**21. Client → MedicalVisit**
```cypher
(Client)-[:HAD]->(MedicalVisit)
```

---

## Insurance Policy Relationships (9 new)

**22. Client → InsurancePolicy**
```cypher
(Client)-[:HAS_POLICY]->(InsurancePolicy)
```

**23. Defendant → InsurancePolicy**
```cypher
(Defendant)-[:HAS_POLICY]->(InsurancePolicy)
```

**24. InsurancePolicy → Insurer**
```cypher
(InsurancePolicy)-[:WITH_INSURER]->(Insurer)
```

**25-30. All Claim Types → InsurancePolicy**
```cypher
(PIPClaim)-[:UNDER_POLICY]->(InsurancePolicy)
(BIClaim)-[:UNDER_POLICY]->(InsurancePolicy)
(UMClaim)-[:UNDER_POLICY]->(InsurancePolicy)
(UIMClaim)-[:UNDER_POLICY]->(InsurancePolicy)
(WCClaim)-[:UNDER_POLICY]->(InsurancePolicy)
(MedPayClaim)-[:UNDER_POLICY]->(InsurancePolicy)
```

---

## Insurance Payment Relationships (7 new)

**31-35. All Claim Types → InsurancePayment**
```cypher
(PIPClaim)-[:MADE_PAYMENT]->(InsurancePayment)
(BIClaim)-[:MADE_PAYMENT]->(InsurancePayment)
(UMClaim)-[:MADE_PAYMENT]->(InsurancePayment)
(UIMClaim)-[:MADE_PAYMENT]->(InsurancePayment)
(WCClaim)-[:MADE_PAYMENT]->(InsurancePayment)
```

**36. InsurancePayment → Insurer**
```cypher
(InsurancePayment)-[:FROM]->(Insurer)
```

**37. InsurancePayment → Bill**
```cypher
(InsurancePayment)-[:PAID_BILL]->(Bill)  // Track which bills were paid
```

---

## Defendant Insurance Relationships (3 new)

**38. Defendant → Insurer**
```cypher
(Defendant)-[:HAS_INSURANCE]->(Insurer)
```

**39. Defendant → InsurancePolicy**
```cypher
(Defendant)-[:HAS_POLICY]->(InsurancePolicy)  // Duplicate of #23 above
```

**40. BIClaim → Defendant**
```cypher
(BIClaim)-[:COVERS_DEFENDANT]->(Defendant)
```

---

## Bill Relationship Updates (2 new)

**41. Bill → Location**
```cypher
(Bill)-[:BILLED_BY]->(Location)  // Replaces Bill → MedicalProvider
```

**42. Bill → Facility**
```cypher
(Bill)-[:BILLED_BY]->(Facility)
```

---

## Lien Relationship Additions (1 new)

**43. Lien → Bill (PaidBill)**
```cypher
(Lien)-[:PAID_BILL]->(Bill)  // Track what lien holder paid (vs ForBill for what lien covers)
```

---

## Law Firm Office Relationships (3 new)

**44. LawFirmOffice → LawFirm**
```cypher
(LawFirmOffice: "Louisville Office")-[:PART_OF]->(LawFirm: "Bryan Cave")
```

**45. Attorney → LawFirmOffice**
```cypher
(Attorney)-[:WORKS_AT]->(LawFirmOffice)  // Can work at office or firm directly
```

**46. CaseManager → LawFirmOffice**
```cypher
(CaseManager)-[:WORKS_AT]->(LawFirmOffice)
```

---

## Court Event Relationships (4 new)

**47. Case → CourtEvent**
```cypher
(Case)-[:HAS_EVENT]->(CourtEvent)
```

**48. CourtEvent → Court**
```cypher
(CourtEvent)-[:IN]->(Court)
```

**49. CourtEvent → CircuitDivision**
```cypher
(CourtEvent)-[:IN]->(CircuitDivision)
```

**50. CourtEvent → DistrictDivision**
```cypher
(CourtEvent)-[:IN]->(DistrictDivision)
```

---

## Pleading Relationship Additions (1 new)

**51. Pleading → Attorney**
```cypher
(Pleading)-[:FILED_BY]->(Attorney)  // Who filed this pleading
```

---

## Summary by Category

| Category | New Relationships | Key Use Cases |
|----------|-------------------|---------------|
| **Medical Hierarchy** | 14 | Three-tier structure, multi-role, progressive detail |
| **Medical Visits** | 7 | Chronology, lien negotiation |
| **Insurance Policy** | 9 | Policy tracking, multi-claim |
| **Insurance Payment** | 7 | Payment history, bill tracking |
| **Defendant Insurance** | 3 | BI claim linkage |
| **Bills** | 2 | Link to Facility/Location |
| **Liens** | 1 | Track payments |
| **Law Firm Offices** | 3 | Multi-office firms |
| **Court Events** | 4 | Calendar, hearings |
| **Pleadings** | 1 | Discovery organization |
| **TOTAL** | **51** | **Complete workflows** |

---

## Deprecated Relationships

**Being replaced:**
- `(Bill)-[:BILLED_BY]->(MedicalProvider)` → Use Location/Facility instead
- `(Doctor)-[:WORKS_AT]->(MedicalProvider)` → Use Location instead
- `(Client)-[:TREATED_AT]->(MedicalProvider)` → Use Facility/Location instead

**Kept for backward compatibility but should migrate to new structure**

---

## All Defined In

**File:** `/Volumes/X10 Pro/Roscoe/src/roscoe/core/graphiti_client.py`

**Section:** EDGE_TYPE_MAP (starting line ~1273)

**Total relationship patterns in schema:** ~100+ (including existing)
