# Manual Corrections for Review - Awaiting Approval

## Review Files with Annotations:
1. Abby-Sitgraves-MVA-7-13-2024
2. Abigail-Whaley-MVA-10-24-2024
3. Alma-Cristobal-MVA-2-15-2024

---

## Abby-Sitgraves-MVA-7-13-2024

### Changes to Make:

| Line | Entity | Current Status | Your Annotation | Proposed Action |
|------|--------|----------------|-----------------|-----------------|
| 56-58 | Jefferson court variants (3 entries) | ✓ MATCHES: Jefferson County Circuit Court | "Should be Division II" | Update all 3 to: ✓ MATCHES: Jefferson County Circuit Court, **Division II** |
| 62 | Unknown Driver | ✓ MATCHES: Unknown Driver (from directory) | "Needs to be added as a defendant" | Add to defendants.json, update to: ✓ MATCHES: Unknown Driver |
| 63 | limousine company | ? NEW | "Ignore" | Remove from review (add to IGNORE_ENTITIES) |
| 67 | Kentucky One Health | ✓ MATCHES: KENTUCKY ONE HEALTH ORTHOPEDIC ASSOCIATES | "No, it's not. Probably need to see the context" | Context shows it's a health insurer. Update to: ? NEW (health insurer, not the orthopedic provider) |
| 96-97 | Uninsured motorist claims (2 entries) | ? NEW | "Ignore" | Remove both from review (add to IGNORE_ENTITIES) |

**✅ Status:** Abby corrections APPLIED

---

## Abigail-Whaley-MVA-10-24-2024

### Changes to Make:

| Line | Entity | Current Status | Your Annotation | Proposed Action |
|------|--------|----------------|-----------------|-----------------|
| 37 | Lynette Duncan | ? NEW | "Add as an adjuster, and if you look in the context, her contact information is in there as well. And the insurance company she's associated with" | Add to adjusters.json with insurer from context, update to: ✓ MATCHES: Lynette Duncan |

**🔄 Status:** Need to extract context for Lynette Duncan to get insurer

---

## Alma-Cristobal-MVA-2-15-2024

### Changes to Make:

| Line | Entity | Current Status | Your Annotation | Proposed Action |
|------|--------|----------------|-----------------|-----------------|
| 57 | Crete Carrier Corporation (BIClaim) | ? NEW | "This is Crete Carrier Corporation. The same as the other three" | Consolidate - show as variant of main entry |
| 62 | Aletha N. Thomas (Client section) | ? NEW | "She's an attorney, not a client, and it should match" | Remove from Client section (she's correctly in Attorney section line 43) |
| 63 | Alma Cristobal (Client section) | ? NEW | "This is the client" | Update to: ✓ MATCHES: Alma Cristobal (need to add to clients.json) |
| 67 | District Court | ✓ MATCHES: Christian County District Court | "Now, this is Jefferson County District Court" | Update to: ✓ MATCHES: Jefferson County District Court |
| 68-74 | Jefferson court variants (6 entries) | Various | "This is Jefferson County Circuit Court Division III" | Update ALL to: Jefferson County Circuit Court, **Division III** |
| 80 | Defendant (generic) | ? NEW | "Ignore" | Remove from review |
| 82 | Hamilton & Crete Carrier | ? NEW | "This is Roy Hamilton and Crete Carrier Corporation" | This is a consolidation - both defendants exist separately |
| 91 | Sarena Whaley Law Firm | ? NEW | "That's Serena, the employee, Serena Tuttle" | Remove from review (add to IGNORE_ENTITIES) |
| 98 | Louisville LMEMS | ? NEW | "This is Louisville Metro EMS" | Create medical provider entity, update to: ✓ MATCHES: Louisville Metro EMS |
| 103 | UofL Health - Mary & Elizabeth | ✓ MATCHES: University of Louisville Hospital | "This is St. Mary and Elizabeth Hospital" | Update to: ✓ MATCHES: Saint Mary and Elizabeth Hospital |
| 107, 113 | Franklin County OH Sheriff, MetroSafe | ? NEW | "Add as organization" | Already added - update to: ✓ MATCHES |
| 121-122 | KY Court Reporters, Kentuckiana Reporters | ✓ MATCHES (from directory) | (implicit: add as vendors) | Add to vendors.json, update to: ✓ MATCHES |

**🔄 Status:** Corrections in progress

---

## Case-Specific Court Division Rules

### Abby-Sitgraves:
- ALL Jefferson County Circuit Court mentions → **Division II**

### Alma-Cristobal:
- ALL Jefferson County Circuit Court mentions → **Division III**
- District Court → Jefferson County **District** Court (not Christian County)

---

## Entities to Add to JSON Files

### Defendants:
- [x] Unknown Driver (from Abby case)

### Adjusters:
- [ ] Lynette Duncan (from Abigail case - need to extract insurer from context)

### Clients:
- [ ] Alma Cristobal (from Alma case)

### Medical Providers:
- [ ] Louisville Metro EMS (from Alma case)

### Vendors:
- [ ] KY Court Reporters (from directory → vendors.json)
- [ ] Kentuckiana Court Reporters (from directory → vendors.json)

---

## Ignore Patterns to Add:

- limousine company
- Uninsured motorist demand(s)
- uninsured motorist claim
- Sarena Whaley Law Firm (it's a person, not a firm)
- Defendant (generic term)
- Hamilton & Crete Carrier (consolidation, both exist separately)

---

## Questions / Need Approval:

1. **Aletha N. Thomas in Client section** - Remove entirely since she's an attorney?
2. **Hamilton & Crete Carrier** - Is this a multi-defendant entry or should it be consolidated?
3. **Alma Cristobal** - Should I create a new client entity or is this a matching issue?

**Please review and approve before I proceed with execution.**
