# Relationship Files vs Graphiti Schema

**Last Updated:** December 21, 2025

---

## Alignment Status

### ✅ Relationship Files that Match Schema

These relationship JSON files correspond to edge types defined in `graphiti_client.py`:

| File | Edge Type | Count | Schema Status |
|------|-----------|-------|---------------|
| `hasclient_relationships.json` | HasClient | 106 | ✅ In schema |
| `plaintiffin_relationships.json` | PlaintiffIn | 106 | ✅ In schema |
| `hasclaim_relationships.json` | HasClaim | 260 | ✅ In schema |
| `insuredby_relationships.json` | InsuredBy | 254 | ✅ In schema |
| `assignedadjuster_relationships.json` | AssignedAdjuster | 212 | ✅ In schema |
| `handlesinsuranceclaim_relationships.json` | HandlesInsuranceClaim | 212 | ✅ In schema |
| `worksat_relationships.json` | WorksAt | 212 | ✅ In schema |
| `treatingat_relationships.json` | TreatingAt | 573 | ✅ In schema |
| `treatedby_relationships.json` | TreatedBy | 573 | ✅ In schema |
| `haslien_relationships.json` | HasLien | 103 | ✅ In schema |
| `haslienfrom_relationships.json` | HasLienFrom | 103 | ✅ In schema |
| `heldby_relationships.json` | HeldBy | 103 | ✅ In schema |
| `holds_relationships.json` | Holds | 103 | ✅ In schema |

**Total:** 2,920 relationships across 13 types

---

## Edge Types in Schema (Not in Files)

These are defined in `graphiti_client.py` but don't have pre-generated JSON files.
This is expected - they'll be created dynamically as the graph is populated:

### **Not Yet Generated (Will Be Created Dynamically):**

- **Case relationships:** HasDefendant, HasDocument, HasExpense, SettledWith
- **Legal relationships:** RepresentsClient, RepresentedBy, DefenseCounsel, FiledIn
- **Organization relationships:** PartOf
- **Workflow state:** InPhase, LandmarkStatus
- **Workflow structure:** BelongsToPhase, HasLandmark, HasSubLandmark, AchievedBy, Achieves, DefinedInPhase, HasWorkflow, HasStep, StepOf, NextPhase, CanSkipTo
- **Note relationships:** HasNote, NotedOn (NEW - not yet in data)
- **Generic:** Mentions, RelatesTo

---

## Removed from Schema

These were removed because DirectoryEntry entity was deleted (redundant):

- ~~InDirectory~~ - No longer valid
- ~~HasContact~~ - No longer valid

---

## Relationship File Purpose

These JSON files contain **pre-generated relationships** from the original SQL database migration. They represent:

1. **Case → Client** relationships (HasClient, PlaintiffIn)
2. **Case → Claim** relationships (HasClaim)
3. **Claim → Insurer → Adjuster** chain (InsuredBy, AssignedAdjuster, HandlesInsuranceClaim, WorksAt)
4. **Case/Client → MedicalProvider** (TreatingAt, TreatedBy)
5. **Case → Lien → LienHolder** chain (HasLien, HasLienFrom, HeldBy, Holds)

---

## Graph Structure Example

```
Case: "Elizabeth-Lindsey-MVA-12-01-2024"
  |
  ├─[HasClient]─> Client: "Elizabeth Lindsey"
  │                 └─[PlaintiffIn]─> Case (bidirectional)
  |
  ├─[HasClaim]─> PIPClaim: "Elizabeth-Lindsey-...-PIP-300-793616-2024"
  │                 ├─[InsuredBy]─> Insurer: "Auto Owners Insurance"
  │                 └─[AssignedAdjuster]─> Adjuster: "Courtny Wolfe"
  │                                          └─[HandlesInsuranceClaim]─> PIPClaim
  │                                          └─[WorksAt]─> Insurer
  |
  ├─[TreatingAt]─> MedicalProvider: "Aptiva Health"
  │                   └─[TreatedBy]─> Client (bidirectional)
  |
  └─[HasLien]─> Lien: "Elizabeth-Lindsey-...-Rawlings Company"
                   ├─[HasLienFrom]─> Case (bidirectional)
                   └─[HeldBy]─> LienHolder: "Rawlings Company"
                                   └─[Holds]─> Lien (bidirectional)
```

---

## Usage

### Loading Relationships into Graph

These files can be used to populate the initial graph structure:

```python
import json

# Load relationships
with open('relationships/hasclient_relationships.json') as f:
    has_client_rels = json.load(f)

# Each relationship has:
# - source: {entity_type, name}
# - target: {entity_type, name}
# - edge_type: relationship type
# - attributes: relationship properties
# - context: additional context
```

### All Relationships File

`all_relationships.json` contains all 2,920 relationships merged together for bulk operations.

---

## Schema Version

**Version:** 2.0
**Compatibility:** ✅ All relationship files align with updated schema
**Missing Relationships:** InDirectory, HasContact (removed with DirectoryEntry)
