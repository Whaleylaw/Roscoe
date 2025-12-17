# Sub-Phase 7.1: Complaint - Landmarks

## Landmark Summary

| ID | Landmark | Type | Scope | Workflow |
|----|----------|------|-------|----------|
| 7.1.1 | Complaint Drafted | Progress | Case | draft_file_complaint |
| 7.1.2 | Complaint Filed | Progress | Case | draft_file_complaint |
| 7.1.3 | Summons Issued | Progress | Case | draft_file_complaint |
| 7.1.4 | Defendant Served | **Per-Defendant** | Each defendant | serve_defendant |
| 7.1.5 | Answer/Default | **Per-Defendant** | Each defendant | process_answer |
| 7.1.6 | All Defendants Resolved | Progress | Case | process_answer |

---

## Landmark Definitions

### 7.1.1: Complaint Drafted

**Verification:** Complaint document exists with all required sections.

### 7.1.2: Complaint Filed

**Verification:** Case number assigned by court.

### 7.1.3: Summons Issued

**Verification:** Summons received for each defendant.

### 7.1.4: Defendant Served ⭐

**Per-Defendant Milestone**

**Verification (per defendant):** 
- `service_completed_date` is set
- Proof of service filed with court

**Effect:** Once a defendant is served, their individual track moves to Answer processing. Discovery can begin with that defendant once they answer (or default is sought).

### 7.1.5: Answer Received or Default Sought ⭐

**Per-Defendant Milestone**

**Verification (per defendant):** Answer documented OR default motion filed.

**Effect:** Triggers exit to 7.2 Discovery FOR THAT DEFENDANT. Other defendants may still be pending service.

### 7.1.6: All Defendants Resolved

**Verification:** Every defendant has either:
- Answered, OR
- Had default motion filed

---

## Exit to 7.2 Discovery

**Per-Defendant:** Discovery begins for each defendant individually upon:
- Service completed for that defendant, AND
- Answer received OR default sought for that defendant

**Sub-Phase 7.1 remains open** while service/answer is pending for any defendant. The case tracks multiple defendants in parallel:

```
Defendant A: Served → Answered → Discovery begins
Defendant B: Served → Answered → Discovery begins  
Defendant C: Service pending → (still in 7.1)
```

**Full Exit:** Sub-phase 7.1 closes when all defendants have reached 7.1.5 (Answer/Default).

