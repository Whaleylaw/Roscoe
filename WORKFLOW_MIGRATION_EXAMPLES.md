# Workflow Migration Examples

This document shows specific before/after examples from the workflow migration.

---

## Example 1: Insurance BI Claim Workflow

**File:** `phase_1_file_setup/workflows/insurance_bi_claim/workflow.md`

### Before

```markdown
### Step 1: Identify At-Fault Party Insurance

**Actions:**
1. If police report exists → Extract at-fault driver insurance using `police-report-analysis` skill
2. If no police report → Ask user for at-fault party insurance information
3. Create insurance entry in `insurance.json`
4. Create contact entry for at-fault party in `contacts.json`
```

### After

```markdown
> **⚠️ Migration Note (Jan 2026):** This workflow has been updated to use the knowledge graph instead of JSON files.
> Case data is now stored in FalkorDB and accessed via graph queries. See `KNOWLEDGE_GRAPH_SCHEMA.md` for entity types and relationships.

### Step 1: Identify At-Fault Party Insurance

**Actions:**
1. If police report exists → Extract at-fault driver insurance using `police-report-analysis` skill
2. If no police report → Ask user for at-fault party insurance information
3. Create insurance entry in the graph (query InsurancePolicy/BIClaim/PIPClaim nodes)
4. Create contact entry for at-fault party in the graph (query Client/Attorney/Adjuster nodes)
```

**Changes:**
- Added migration notice at top of file
- `in insurance.json` → `in the graph (query InsurancePolicy/BIClaim/PIPClaim nodes)`
- `in contacts.json` → `in the graph (query Client/Attorney/Adjuster nodes)`

---

## Example 2: Medical Provider Status Workflow

**File:** `phase_2_treatment/workflows/medical_provider_status/workflow.md`

### Before

```markdown
### Step 1: Review Current Provider List

**Action:**
Review all providers in `medical_providers.json` and their current status.

**Updates to `medical_providers.json`:**
```json
{
  "treatment": {
    "status": "{{new_status}}",
    "last_visit": "{{date}}",
    "status_updated": "{{today}}",
    "notes": "{{status_notes}}"
  }
}
```
```

### After

```markdown
> **⚠️ Migration Note (Jan 2026):** This workflow has been updated to use the knowledge graph instead of JSON files.
> Case data is now stored in FalkorDB and accessed via graph queries. See `KNOWLEDGE_GRAPH_SCHEMA.md` for entity types and relationships.

### Step 1: Review Current Provider List

**Action:**
Query all medical providers from graph (use graph_query tool or query_case_graph) and their current status.

**Updates to the graph using write_entity():**
```json
{
  "treatment": {
    "status": "{{new_status}}",
    "last_visit": "{{date}}",
    "status_updated": "{{today}}",
    "notes": "{{status_notes}}"
  }
}
```
```

**Changes:**
- Added migration notice
- `Review all providers in medical_providers.json` → `Query all medical providers from graph (use graph_query tool or query_case_graph)`
- `Updates to medical_providers.json` → `Updates to the graph using write_entity()`

---

## Example 3: Case Setup Workflow

**File:** `phase_0_onboarding/workflows/case_setup/workflow.md`

### Before

```markdown
**Deliverables:**
- Complete case folder structure created
- All JSON files initialized
- `workflow_state.json` set to Phase 0 with pending documents list
```

### After

```markdown
> **⚠️ Migration Note (Jan 2026):** This workflow has been updated to use the knowledge graph instead of JSON files.
> Case data is now stored in FalkorDB and accessed via graph queries. See `KNOWLEDGE_GRAPH_SCHEMA.md` for entity types and relationships.

**Deliverables:**
- Complete case folder structure created
- All Graph entities initialized
- `workflow_state.json` set to Phase 0 with pending documents list
```

**Changes:**
- Added migration notice
- `All JSON files initialized` → `All Graph entities initialized`

---

## Example 4: Referral New Provider Workflow

**File:** `phase_2_treatment/workflows/referral_new_provider/workflow.md`

### Before

```markdown
**Step 3: Add Provider to Medical Providers List**

Update `medical_providers.json`:
- Add new provider entry
- Include referral source
- Status: "pending_first_visit"
```

### After

```markdown
**Step 3: Add Provider to Medical Providers List**

Update the graph using write_entity():
- Add new provider entry
- Include referral source
- Status: "pending_first_visit"
```

**Changes:**
- `Update medical_providers.json` → `Update the graph using write_entity()`

---

## Example 5: LOR Generator Skill

**File:** `phase_1_file_setup/workflows/insurance_bi_claim/skills/lor-generator/skill.md`

### Before

```markdown
The template uses data from:
- `insurance.json` - Adjuster name, company address, claim number
- `overview.json` - Client name, incident date
- `contacts.json` - Attorney name
```

### After

```markdown
The template uses data from:
- the graph (query InsurancePolicy/BIClaim/PIPClaim nodes) - Adjuster name, company address, claim number
- the graph (query Case node) - Client name, incident date
- the graph (query Client/Attorney/Adjuster nodes) - Attorney name
```

**Changes:**
- All JSON file references replaced with graph query instructions
- Specific entity types provided for clarity

---

## Key Patterns

### Pattern 1: Data Source References

**Before:** `in [filename].json`
**After:** `in the graph (query [EntityType] nodes)`

### Pattern 2: Update Operations

**Before:** `Update [filename].json with`
**After:** `Update graph entity using write_entity() with`

### Pattern 3: Create Operations

**Before:** `Create entry in [filename].json`
**After:** `Create entity in graph using write_entity(entity_type="...", ...)`

### Pattern 4: Initialization Text

**Before:** `JSON files initialized`
**After:** `Graph entities initialized`

### Pattern 5: Field Path References

**Before:** `insurance.adjuster.name` (JSON path)
**After:** `graph field (see InsurancePolicy/Claim schema)` (graph property)

---

## Entity Type Mapping Reference

For workflow authors updating additional files:

| Old Reference | Graph Entity Type | Example Query |
|---------------|-------------------|---------------|
| `medical_providers.json` | `Facility` or `Location` | `MATCH (f:Facility)-[:TREATED_AT]-(c:Client {name: "John Doe"}) RETURN f` |
| `insurance.json` | `InsurancePolicy`, `BIClaim`, `PIPClaim` | `MATCH (c:Case)-[:HAS_CLAIM]->(claim:BIClaim) RETURN claim` |
| `contacts.json` | `Client`, `Attorney`, `Adjuster` | `MATCH (a:Attorney)-[:REPRESENTS]->(c:Client) RETURN a` |
| `liens.json` | `Lien`, `LienHolder` | `MATCH (lien:Lien)-[:AGAINST_CASE]->(case:Case) RETURN lien` |
| `overview.json` | `Case` | `MATCH (case:Case {name: "John-Doe-MVA-01-15-2025"}) RETURN case` |
| `notes.json` | `Episode` | `MATCH (e:Episode)-[:RELATES_TO]->(case:Case) RETURN e` |

---

## Migration Notice Template

For any additional workflow files that need updating:

```markdown
> **⚠️ Migration Note (Jan 2026):** This workflow has been updated to use the knowledge graph instead of JSON files.
> Case data is now stored in FalkorDB and accessed via graph queries. See `KNOWLEDGE_GRAPH_SCHEMA.md` for entity types and relationships.
```

Place this notice:
- After YAML frontmatter (`---`)
- Before the main heading (`# Workflow Name`)
- Only in primary `workflow.md` files (not skills or templates)

---

## Validation Checklist

When reviewing migrated workflows:

- [ ] Migration notice added to main workflow.md files
- [ ] All `in [file].json` references updated to graph queries
- [ ] All `Update [file].json` operations use `write_entity()`
- [ ] Entity types specified (Facility, Location, InsurancePolicy, etc.)
- [ ] References to KNOWLEDGE_GRAPH_SCHEMA.md included
- [ ] Original workflow intent preserved
- [ ] No broken links or invalid references
- [ ] JSON template files (`.docx`, `.pdf`) NOT changed (those are fine)

---

**Document Version:** 1.0
**Last Updated:** January 4, 2026
**Purpose:** Reference examples for workflow migration review
