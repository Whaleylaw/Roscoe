# Graph Process Clarification

## What We're Actually Doing (NOT using Graphiti)

### **The Confusion:**
- File named `graphiti_client.py` suggests we're using Graphiti
- We started with Graphiti but abandoned it for episodes
- File name kept for historical reasons

### **The Reality:**

**What `graphiti_client.py` Actually Contains:**
- ✅ Pydantic schema definitions (58 entity types, 71 relationship types)
- ✅ EDGE_TYPE_MAP validation rules
- ✅ Entity and relationship type checking
- ❌ NO Graphiti automatic ingestion
- ❌ NO Graphiti entity extraction
- ❌ NO auto-generated names

**What We're Actually Using:**
1. **GPT-5** for entity extraction (not Graphiti)
2. **Manual review** for relationship approval (not automatic)
3. **Custom ingestion scripts** (not Graphiti's add_episode)
4. **Explicit entity names** from approved data (not auto-generated)

---

## The Manual Review Process

### **Purpose:**
The 138 review files in `/json-files/memory-cards/episodes/reviews/` are the **core of our new process**. This is how we create accurate, verified relationships before graph ingestion.

### **What Review Files Do:**

**1. Show Proposed Relationships:**
```markdown
### Attorney (11 consolidated)
- [ ] Aletha N. Thomas, Esq. — *✓ MATCHES: Aletha N. Thomas, Esq.*
- [ ] Kaleb J. Noblett — *✓ MATCHES: Kaleb J. Noblett*
```

This means:
- GPT-5 extracted "Aletha N. Thomas" from episodes
- Our matching logic found her in attorneys.json
- When ingested: `(Episode)-[:ABOUT]->(Attorney {name: "Aletha N. Thomas, Esq."})`

**2. Enable Case-Specific Corrections:**
```markdown
- [ ] Jefferson County Circuit Court, Division III — *✓ MATCHES: Jefferson County Circuit Court, Division III (Judge: Mitch Perry)*
```

This means:
- User manually determined this case is in Division III (from case number research)
- When ingested: `(Episode)-[:ABOUT]->(CircuitDivision {name: "..., Division III"})`
- Division III is case-specific - other cases may be Division II, Division V, etc.

**3. Catch Wrong Matches:**
```markdown
### Client (1 consolidated)
- [ ] Alma Socorro Cristobal Avendao — *✓ MATCHES: Alma Socorro Cristobal Avendao*
      ↳ _Alma Cristobal_
      ↳ _Aletha N. Thomas_ (misclassified - see Attorney section)
```

This means:
- GPT-5 extracted "Aletha N. Thomas" as a client (wrong!)
- User corrected: She's an attorney (line 43)
- Won't create: `(Episode)-[:ABOUT]->(Client {name: "Aletha"})`
- Will create: `(Episode)-[:ABOUT]->(Attorney {name: "Aletha N. Thomas"})`

---

## The Three-Phase Ingestion Strategy

### **Phase 1: Structured Entities (Direct Cypher - Already Done)**

**What's in graph now:**
- Cases (111), Clients, Defendants
- Insurance claims, Insurers, Adjusters
- Medical Providers (773, about to be 2,159)
- Liens, LienHolders
- Attorneys, Law Firms
- Courts, Pleadings
- Workflow State (Phases, Landmarks, LandmarkStatus = 9,102 nodes)

**How created:**
- Direct Cypher CREATE statements
- Data from case JSON files
- Module: `graph_manager.py` (not graphiti_client.py)

### **Phase 2: Manual Review (Current Work)**

**Input:**
- 138 processed_*.json files (GPT-5 entity extraction)
- 40,605 proposed ABOUT relationships

**Process:**
1. Review proposed relationships in batches
2. User adds inline corrections/annotations
3. Developer manually applies corrections
4. Mark files as approved (APPROVED_REVIEWS.txt)
5. Repeat until all 138 approved

**Output:**
- 138 approved review files
- ~45,900 entity cards in JSON files
- Verified relationship proposals ready for ingestion

### **Phase 3: Custom Episode Ingestion (After All Reviews Approved)**

**What we'll ingest:**
- 13,491 Episode nodes
- 40,605 ABOUT relationships (verified)
- ~10,000 FOLLOWS relationships (topical/sequential links)
- 21,500+ WORKS_AT/PRESIDES_OVER relationships (professional)
- 1,300+ PART_OF relationships (hierarchies)

**How we'll do it:**
```python
# Custom ingestion script (NOT Graphiti)
for approved_review in approved_reviews:
    for episode in review['episodes']:
        # Create Episode node
        graph.query("""
            CREATE (ep:Episode {
                name: $name,
                content: $content,
                valid_at: $valid_at,
                author: $author,
                case_name: $case_name,
                embedding: vecf32($embedding)
            })
        """, episode_data)

        # Create ABOUT relationships
        for relationship in episode['proposed_relationships']['about']:
            if relationship_approved:  # From review file
                graph.query("""
                    MATCH (ep:Episode {name: $episode_name})
                    MATCH (entity {name: $entity_name})
                    WHERE $entity_type IN labels(entity)
                    CREATE (ep)-[:ABOUT {relevance: $relevance}]->(entity)
                """, relationship_data)
```

---

## File Purposes Clarified

### **Schema Definition:**
- `graphiti_client.py` - Pydantic models for all entity types, EDGE_TYPE_MAP
- **Purpose:** Schema validation, type checking, relationship rules
- **NOT:** Graphiti ingestion code

### **Entity Data:**
- `/json-files/memory-cards/entities/*.json` - 45,900 entity cards
- **Purpose:** Source of truth for all entities
- **How created:** Imports (doctors, courts, etc.) + manual review approval

### **Episode Data:**
- `/json-files/memory-cards/episodes/processed_*.json` - 138 files with GPT-5 extractions
- **Purpose:** Proposed relationships waiting for approval
- **NOT yet in graph:** Pending manual review

### **Review Files:**
- `/json-files/memory-cards/episodes/reviews/review_*.md` - 138 review documents
- **Purpose:** Manual approval interface for relationships
- **Process:** User reviews → adds annotations → developer applies → marks approved

### **Graph Ingestion:**
- Custom scripts (to be written) - NOT Graphiti
- **Purpose:** Ingest approved episodes and relationships
- **When:** After all 138 reviews approved

---

## Why This Matters

**What We're Building:**
A knowledge graph with 100% verified relationships through manual review, not automated Graphiti ingestion.

**The Review Files Are Critical:**
They are the human-in-the-loop approval system ensuring:
- Correct entity matches (not "Kentucky One Health" orthopedic provider when it's a health insurer)
- Case-specific context (Division II vs Division III based on case numbers)
- Type corrections (Aletha Thomas is attorney, not client)
- Consolidations (Alma Cristobal = Alma Socorro Cristobal Avendao)

**After Review Complete:**
We'll have 40,605 VERIFIED relationships ready to ingest with confidence, not 40,605 auto-generated guesses.

---

## Current Status

**Schema Definition:** ✅ Complete (58 entities, 71 relationships in graphiti_client.py)
**Entity Import:** ✅ Complete (45,900 entities in JSON files)
**GPT-5 Extraction:** ✅ Complete (138 processed files)
**Manual Review:** ⏳ 3 of 138 approved (2%)
**Graph Ingestion:** ⏳ Pending review completion

**Next:** Continue manual review process until all 138 files approved, then write custom ingestion scripts.
