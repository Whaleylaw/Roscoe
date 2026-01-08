# Court Division Entity Structure - Complete

## Overview

Created 192 division/district entities as first-class graph nodes, enabling division-specific queries, judge tracking, and case analytics.

---

## Entity Counts

| Type | Count | Description |
|------|-------|-------------|
| CircuitDivision | 86 | Circuit court divisions across KY counties |
| DistrictDivision | 94 | District court divisions across KY counties |
| SupremeCourtDistrict | 7 | KY Supreme Court geographic districts |
| AppellateDistrict | 5 | Court of Appeals regional offices |
| **TOTAL** | **192** | All court divisions/districts |

---

## Graph Structure

### **Circuit Court (Example: Jefferson County)**

```
(Court {name: "Jefferson County Circuit Court"})
  ↑ [PART_OF]
(CircuitDivision {name: "Jefferson County Circuit Court, Division II", number: "02"})
  ↑ [PRESIDES_OVER]
(CircuitJudge {name: "Annie O'Connell"})

(Case {name: "Abby-Sitgraves"})-[:FILED_IN]->(CircuitDivision)
(Episode)-[:ABOUT]->(CircuitDivision)
```

### **All Court Types:**

```
Supreme Court
  ├─ District 1 (Western KY) → Justice Nickell
  ├─ District 2 (Louisville) → Justice Bisig
  ├─ District 3 (Northern KY) → Justice Keller
  ├─ District 4 (Lexington) → Justice Goodwine
  ├─ District 5 (Eastern KY) → Justice Conley
  ├─ District 6 (South Central)
  └─ District 7 (Frankfort) → Chief Justice Lambert, Justice Thompson, Katie Bing

Court of Appeals
  ├─ Lexington Office → 2 judges
  ├─ Louisville Office → 2 judges
  ├─ Covington Office → 2 judges
  ├─ Frankfort Office → 9 judges
  └─ Paducah Office → 0 judges

Jefferson County Circuit Court
  ├─ Division I → Judge Eric J. Haner
  ├─ Division II → Judge Annie O'Connell
  ├─ Division III → Judge Mitch Perry
  ├─ Division IV → Judge Julie Kaelin
  ├─ Division V → Judge Tracy E. Davis
  ├─ Division VI → Judge Jessica E. Green
  ├─ Division VII → Judge Melissa Logan Bellows
  ├─ Division VIII → Judge Jennifer Bryant Wilcox
  ├─ Division IX → Judge Sarah E. Clay
  ├─ Division X → Judge Patricia "Tish" Morris
  ├─ Division XI → Judge Brian C. Edwards
  ├─ Division XII → Judge Susan Schultz Gibson
  └─ Division XIII → Judge Ann Bailey Smith

Jefferson County District Court
  ├─ Division 1 → Judge Anthony Jones
  ├─ Division 2 → Judge Amber B. Wolf
  ├─ Division 3 → Judge Kristina Garvey
  ... (16 total divisions)
```

---

## Relationship Patterns

### **Case Filed in Division:**
```cypher
(Case)-[:FILED_IN]->(CircuitDivision)-[:PART_OF]->(Court)
```

### **Judge Presides Over Division:**
```cypher
(CircuitJudge)-[:PRESIDES_OVER]->(CircuitDivision)-[:PART_OF]->(Court)
```

### **Complete Chain:**
```
Case → [FILED_IN] → Division → [PART_OF] → Court
                        ↑
                   [PRESIDES_OVER]
                        |
                      Judge
```

---

## Powerful Queries

### **1. All cases in a specific division:**
```cypher
MATCH (c:Case)-[:FILED_IN]->(d:CircuitDivision {name: "Jefferson County Circuit Court, Division II"})
RETURN c.name, c.status, c.filing_date
ORDER BY c.filing_date DESC
```

### **2. Judge presiding over a case:**
```cypher
MATCH (c:Case {name: "Abby-Sitgraves"})-[:FILED_IN]->(d:CircuitDivision)
      <-[:PRESIDES_OVER]-(j:CircuitJudge)
RETURN j.name, d.name
```

### **3. All cases before Judge Annie O'Connell:**
```cypher
MATCH (c:Case)-[:FILED_IN]->(d:CircuitDivision)<-[:PRESIDES_OVER]-(j:CircuitJudge {name: "Annie O'Connell"})
RETURN c.name, c.filing_date, c.status
```

### **4. Settlement analytics by judge:**
```cypher
MATCH (c:Case)-[:FILED_IN]->(d:CircuitDivision)<-[:PRESIDES_OVER]-(j:CircuitJudge {name: "Annie O'Connell"})
MATCH (c)-[:SETTLED_WITH]->(s:Settlement)
RETURN
  j.name,
  d.name,
  count(c) as total_settlements,
  avg(s.amount) as avg_settlement,
  percentile_cont(s.amount, 0.5) as median_settlement
```

### **5. Division-specific rules and preferences:**
```cypher
MATCH (d:CircuitDivision {name: "Jefferson County Circuit Court, Division II"})
RETURN
  d.local_rules,
  d.scheduling_preferences,
  d.mediation_required
```

### **6. Set division-specific attributes:**
```cypher
MATCH (d:CircuitDivision {name: "Jefferson County Circuit Court, Division II"})
SET d.local_rules = "Judge O'Connell requires mediation within 60 days of answer"
SET d.scheduling_preferences = "Prefers Thursday motion hours"
SET d.mediation_required = true
SET d.average_time_to_trial_days = 180
```

### **7. Find all divisions for a county:**
```cypher
MATCH (d:CircuitDivision)-[:PART_OF]->(c:Court {name: "Jefferson County Circuit Court"})
MATCH (j:CircuitJudge)-[:PRESIDES_OVER]->(d)
RETURN d.name, j.name
ORDER BY d.division_number
```

### **8. Track judge changes over time:**
```cypher
// When new judge elected to Division II
MATCH (old:CircuitJudge)-[r:PRESIDES_OVER]->(d:CircuitDivision {name: "Jefferson County Circuit Court, Division II"})
MATCH (new:CircuitJudge {name: "New Judge Name"})
DELETE r
CREATE (new)-[:PRESIDES_OVER]->(d)
CREATE (change:JudgeChange {
  division: d.name,
  old_judge: old.name,
  new_judge: new.name,
  change_date: date()
})
```

---

## Files Created

### **Division Entity Files:**
1. `circuit_divisions.json` - 86 circuit court divisions
2. `district_divisions.json` - 94 district court divisions
3. `supreme_court_districts.json` - 7 Supreme Court districts
4. `appellate_districts.json` - 5 Court of Appeals regional offices
5. `judge_division_mappings.json` - Maps judges to their divisions

### **Pydantic Models Added:**
- `CircuitDivision` (line 288)
- `DistrictDivision` (line 298)
- `AppellateDistrict` (line 305)
- `SupremeCourtDistrict` (line 312)

### **Relationship Types:**
- Division -[PART_OF]-> Court
- Judge -[PRESIDES_OVER]-> Division
- Case -[FILED_IN]-> Division
- Episode -[ABOUT]-> Division

---

## Review File Impact

**Before:**
```
- [ ] Jefferson Circuit Court — *✓ MATCHES: Jefferson County Circuit Court*
```

**After:**
```
- [ ] Jefferson County Circuit Court, Division II — *✓ MATCHES: CircuitDivision entity*
```

---

## Use Cases Enabled

### **1. Judge Performance Tracking**
- Query all cases before specific judge
- Calculate settlement rates per judge
- Track time-to-resolution by judge
- Compare outcomes across judges

### **2. Division-Specific Rules**
- Store local rules per division
- Track judge preferences (mediation, scheduling, etc.)
- Document division-specific procedures

### **3. Case Strategy**
- "Which divisions settle faster?"
- "What's the average verdict in Division III?"
- "Which judges favor plaintiff/defendant?"

### **4. Workflow Automation**
- Auto-populate division-specific forms
- Suggest best division for filing
- Alert when judge changes

### **5. Historical Analysis**
- Track judge changes over elections
- Compare outcomes before/after judge change
- Analyze division workload distribution

---

## Total Entity Count: ~43,500

| Category | Count |
|----------|-------|
| Doctors | 20,732 |
| Court Divisions | 192 |
| Courts | 106 |
| Circuit Judges | 101 |
| District Judges | 94 |
| Organizations | 384 |
| Medical Providers | 773 |
| Court Clerks | 121 |
| Master Commissioners | 114 |
| Insurers | 99 |
| Vendors | 40 |
| Attorneys | 34 |
| Law Firms | 36 |
| Appellate Judges | 15 |
| Defendants | 11 |
| Supreme Court Justices | 8 |
| Court Administrators | 7 |
| Clients | 105 |
| Mediators | 2 |
| Witnesses | 1 |

**All with proper division/district granularity for precise queries!**
