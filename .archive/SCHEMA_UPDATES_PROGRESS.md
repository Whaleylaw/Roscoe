# Schema Updates - Progress Report

## ✅ Completed

### **Entity Changes:**
1. ✅ Removed `Note` entity (line 72)
2. ✅ Removed `raw_content` property from Episode
3. ✅ Created `Bill` entity (line 437)
4. ✅ Created `Negotiation` entity (line 449)
5. ✅ Kept `Settlement` entity (different from Negotiation - final breakdown vs negotiation process)
6. ✅ Created 5 Document subtypes:
   - MedicalRecords (line 265)
   - MedicalBills (line 273)
   - MedicalRecordsRequest (line 281)
   - LetterOfRepresentation (line 290)
   - InsuranceDocument (line 299)
   - CorrespondenceDocument (line 306)
7. ✅ Created `Community` entity (line 81)
8. ✅ Updated `MedicalProvider` - added medical_records_endpoint, billing_endpoint (lines 219-220)
9. ✅ Updated `LienHolder.lien_type` - added "case_funding" and "other" options (line 246)

**New Entity Count:** +9 entities (Bill, Negotiation, 5 document types, Community, minus Note = +8 net)

---

## 🔄 In Progress

### **Relationship Updates Needed:**

**Files to Update:**
- `/src/roscoe/core/graphiti_client.py` - ENTITY_TYPES list and EDGE_TYPE_MAP

**Changes Required:**

**1. Update ENTITY_TYPES List:**
- ❌ Remove: Note
- ➕ Add: Bill, Negotiation, MedicalRecords, MedicalBills, MedicalRecordsRequest, LetterOfRepresentation, InsuranceDocument, CorrespondenceDocument, Community

**2. Fix Relationship Directions:**
- Change: `("MedicalProvider", "Client"): ["TreatedBy"]`
- To: `("MedicalProvider", "Client"): ["HasTreated"]`
- Add bidirectional: `("Client", "MedicalProvider"): ["TreatedBy"]`

**3. Remove Relationships:**
- ❌ `("Lien", "LienHolder"): ["HeldBy"]`
- ❌ `("LienHolder", "Lien"): ["Holds"]`
- ❌ All NotedOn relationships

**4. Add New Relationships:**

**Bill:**
```python
("Bill", "MedicalProvider"): ["BilledBy"],
("Bill", "Vendor"): ["BilledBy"],
("Bill", "Attorney"): ["BilledBy"],
("Lien", "Bill"): ["ForBill"],  # Lien is for specific bill
("Case", "Bill"): ["HasBill"],
```

**Client-Insurance:**
```python
("Client", "Insurer"): ["HasInsurance"],
("Client", "PIPClaim"): ["FiledClaim"], # Also for other claim types
("Client", "BIClaim"): ["FiledClaim"],
("Client", "UMClaim"): ["FiledClaim"],
("Client", "UIMClaim"): ["FiledClaim"],
("Client", "WCClaim"): ["FiledClaim"],
("PIPClaim", "Client"): ["Covers"],  # Also for other claim types
("BIClaim", "Client"): ["Covers"],
# etc for all claim types
```

**Negotiation:**
```python
("Negotiation", "PIPClaim"): ["ForClaim"],  # Also other claim types
("Negotiation", "BIClaim"): ["ForClaim"],
("Case", "Negotiation"): ["HasNegotiation"],
```

**Document:**
```python
("MedicalRecords", "MedicalProvider"): ["ReceivedFrom"],
("MedicalBills", "MedicalProvider"): ["ReceivedFrom"],
("MedicalRecordsRequest", "MedicalProvider"): ["SentTo"],
("LetterOfRepresentation", "Insurer"): ["SentTo"],
("LetterOfRepresentation", "MedicalProvider"): ["SentTo"],
("Document", "Case"): ["Regarding"],
("Document", "Client"): ["Regarding"],
("Document", "Claim"): ["Regarding"],
("Case", "Document"): ["HasDocument"],  # Already exists
```

**Community:**
```python
("Community", "Entity"): ["HasMember"],  # Generic - can be any entity
("MedicalProvider", "Community"): ["MemberOf"],
("Attorney", "Community"): ["MemberOf"],
("Case", "Community"): ["MemberOf"],
# Add for all entity types that can be in communities
```

---

## ⏳ Remaining Tasks

1. Update ENTITY_TYPES list (remove Note, add 8 new)
2. Update EDGE_TYPE_MAP with all relationship changes
3. Update Episode ABOUT relationships to include new document types
4. Test that schema still loads without errors
5. Update GRAPH_SCHEMA_COMPLETE.md with all changes
6. Update CLAUDE_GRAPH.md to reflect new structure

**Estimated Time Remaining:** 30-45 minutes

**Next:** Update ENTITY_TYPES list and EDGE_TYPE_MAP

---

## Notes

**Negotiation vs Settlement:**
- **Negotiation** = Active process (demand → offer → counter → agreement)
- **Settlement** = Final result (gross → fees → liens → net to client)
- Both are needed - kept both entities

**Doctors WORKS_AT Multiple Providers:**
- Yes - Cypher supports multiple WORKS_AT relationships
- Dr. Smith can work at both Norton Downtown and Norton Brownsboro
- Query: `MATCH (d:Doctor {name: "Dr. Smith"})-[:WORKS_AT]->(p) RETURN p.name`
