# Whaley Law Firm Knowledge Graph Schema

**Graph Name:** `whaley_law_firm`
**Backend:** FalkorDB (Redis-based graph database)
**Purpose:** Firm-wide knowledge graph for cross-case entities, relationships, and temporal state tracking
**Last Updated:** December 21, 2025

---

## Overview

The `whaley_law_firm` graph is the **primary firm-wide knowledge graph** that stores entities and episodes that span multiple cases or represent firm-level data. This is distinct from case-specific graphs which are created per case.

### Current State

- **24 Episodic nodes** (events/episodes)
- **44 Entity nodes** (people, organizations, concepts)
- **222 relationships** (123 MENTIONS + 99 RELATES_TO)

---

## Node Types

### 1. Episodic Nodes

**Label:** `Episodic`

**Purpose:** Represent time-ordered events, case notes, status changes, communications, and other temporal occurrences.

**Properties:**

| Property | Type | Description | Required | Example |
|----------|------|-------------|----------|---------|
| `uuid` | string | Unique identifier (UUID v4) | Yes | `b0c23809-877e-4847-b9f2-3bc8c68c40b2` |
| `name` | string | Human-readable episode name | Yes | `"Test: Caryn McCay intake"` |
| `group_id` | string | Graph/namespace identifier | Yes | `"whaley_law_firm"` |
| `source_description` | string | Origin of the episode | Yes | `"test script"`, `"migration"`, `"user_note"` |
| `content` | string | Full text content of the episode | Yes | Detailed narrative of the event |
| `created_at` | ISO 8601 datetime | Creation timestamp | Yes | `"2025-12-20T03:08:13.979468+00:00"` |
| `valid_at` | ISO 8601 datetime | Event occurrence timestamp | No | `"2023-09-21T00:00:00"` |
| `embedding` | float[] | 384-dim vector (sentence-transformers) | Yes | For semantic search |

**Episodic Node Examples:**
- `"Case note (insurance_note): Caryn-McCay-MVA-7-30-2023 - 2023-09-28"`
- `"Case note (status_change): Caryn-McCay-MVA-7-30-2023 - 2023-09-21"`
- `"Test: Caryn McCay intake"`
- `"Treatment Update"` (for Abby Sitgraves case)

**Source Types:**
- `test` - Test/demo episodes
- `migration` - Historical data migrated from JSON files
- `test script` - Episodes created by testing scripts
- `user_note` - User-created notes
- `case_update` - Case status updates
- `source_type` values from `update_case_data()` tool

---

### 2. Entity Nodes

**Label:** `Entity`

**Purpose:** Represent people, organizations, concepts, documents, claims, or any identifiable entity.

**Properties:**

| Property | Type | Description | Required | Example |
|----------|------|-------------|----------|---------|
| `uuid` | string | Unique identifier (UUID v4) | Yes | `644472fd-be2a-4987-b7d8-699f7c8d0d83` |
| `name` | string | Entity name | Yes | `"Caryn McCay"`, `"Allstate Insurance"` |
| `entity_type` | string | Type classification (optional) | No | `"person"`, `"organization"`, `"claim"` |
| `group_id` | string | Graph/namespace identifier | Yes | `"whaley_law_firm"` |
| `summary` | text | Contextual summary | Yes | Relationships and key facts |
| `created_at` | ISO 8601 datetime | Creation timestamp | Yes | `"2025-12-19T22:00:09.801823+00:00"` |
| `embedding` | float[] | 384-dim vector (sentence-transformers) | Yes | For semantic search |

**Entity Examples:**
- **People**: `"Caryn McCay"`, `"Abby Sitgraves"`, `"Justin"`, `"Coleen Thea Madayag"`
- **Organizations**: `"Allstate Insurance"`, `"State Farm Insurance Company"`, `"Allstar Chiropractic"`, `"National Indemnity Company"`, `"Whaley Law Firm"`
- **Claims**: `"PIP claim"`, `"Bodily Injury (BI) claim"`, `"Personal Injury Protection (PIP)"`
- **Documents**: `"medical records"`, `"Police report"`, `"Photos of injuries"`, `"Health insurance card"`
- **Concepts**: `"MVA"` (motor vehicle accident), `"LOR"` (letter of representation), `"File Setup"`
- **Case References**: `"Caryn-McCay-MVA-7-30-2023"`, `"Case update for Abby-Sitgraves-MVA-7-13-2024"`
- **Contact Info**: Phone numbers (`"0723447272"`, `"(608) 373-7383"`), policy numbers (`"1756L980M"`)

**Entity Type Values** (optional field):
- Currently, most entities have empty `entity_type` field
- This field is available for future classification (e.g., `"person"`, `"organization"`, `"claim"`, `"document"`, etc.)

---

## Relationship Types

### 1. MENTIONS

**Direction:** `Episodic → Entity`

**Count:** 123 relationships

**Purpose:** Links episodes to entities mentioned within them.

**Properties:** None currently defined

**Example:**
```cypher
(e:Episodic {name: "Test: Caryn McCay intake"})
  -[:MENTIONS]->
(ent:Entity {name: "Caryn McCay"})
```

**Use Case:** When an episode references a person, organization, claim, or document, a MENTIONS relationship is created.

---

### 2. RELATES_TO

**Direction:** `Entity → Entity`

**Count:** 99 relationships

**Purpose:** Links entities that have semantic relationships (client-provider, claim-insurer, case-document, etc.).

**Properties:** None currently defined

**Example:**
```cypher
(client:Entity {name: "Caryn McCay"})
  -[:RELATES_TO]->
(provider:Entity {name: "Allstar Chiropractic"})
```

**Use Cases:**
- Client relationships with family members, providers, insurers
- Insurance companies linked to claims and adjusters
- Cases linked to involved parties
- Documents associated with cases or entities

---

## Graph Group ID

**`group_id`:** `"whaley_law_firm"`

All nodes in this graph share the same `group_id` value to distinguish them from case-specific graphs.

---

## Embedding Model

**Model:** `sentence-transformers/all-MiniLM-L6-v2`
**Dimensions:** 384
**Purpose:** Semantic search and similarity matching

Both Episodic and Entity nodes include embedding vectors for:
- Natural language queries (`query_case_graph` tool)
- Finding related entities
- Temporal semantic search

---

## Data Sources

### Current Episode Sources:

1. **Migration** - Historical notes from Caryn McCay case (September 2023)
   - Insurance notes
   - Status change notes
   - Client contact notes
   - General case notes

2. **Test Scripts** - Development testing episodes
   - Intake simulations
   - Case update tests

3. **Case Updates** - Abby Sitgraves MVA case
   - Treatment updates from Allstar Chiropractic
   - Insurance claim tracking (National Indemnity Company)

---

## Sample Queries

### Count nodes by type
```cypher
GRAPH.QUERY whaley_law_firm "
  MATCH (n)
  RETURN labels(n) AS type, COUNT(n) AS count
"
```

### Get recent episodes
```cypher
GRAPH.QUERY whaley_law_firm "
  MATCH (e:Episodic)
  RETURN e.name, e.source_description, e.created_at
  ORDER BY e.created_at DESC
  LIMIT 10
"
```

### Find entities by name
```cypher
GRAPH.QUERY whaley_law_firm "
  MATCH (e:Entity)
  WHERE e.name CONTAINS 'Insurance'
  RETURN e.name, e.summary
"
```

### Get entity relationships
```cypher
GRAPH.QUERY whaley_law_firm "
  MATCH (a:Entity {name: 'Caryn McCay'})-[r:RELATES_TO]->(b:Entity)
  RETURN a.name AS from, b.name AS to
"
```

### Find episodes mentioning an entity
```cypher
GRAPH.QUERY whaley_law_firm "
  MATCH (ep:Episodic)-[:MENTIONS]->(e:Entity {name: 'Caryn McCay'})
  RETURN ep.name, ep.created_at
  ORDER BY ep.created_at
"
```

---

## Integration with Roscoe Agent

### Tools that Write to Graph

1. **`update_case_data(case_name, data, source_type, source_id)`**
   - Creates Episodic nodes for case updates
   - Extracts entities from data
   - Creates MENTIONS relationships
   - Adds to `whaley_law_firm` graph if firm-wide data

2. **`associate_document(case_name, document_path, entity_ids)`**
   - Links documents to entities via RELATES_TO

### Tools that Read from Graph

1. **`query_case_graph(case_name, query)`**
   - Natural language search using embeddings
   - Returns relevant episodes and entities

2. **`graph_query(query_name, params)`**
   - Pre-defined Cypher queries
   - Structural lookups (e.g., cases_by_provider)

---

## Design Patterns

### Firm-Wide vs Case-Specific

**Firm-Wide Graph (`whaley_law_firm`):**
- Cross-case entities (providers, insurers, attorneys)
- Firm processes and workflows
- Shared contacts and resources
- Test/development data

**Case-Specific Graphs (e.g., `Elizabeth-Lindsey-MVA-12-01-2024`):**
- Case-specific episodes (intake, medical visits, negotiations)
- Case-specific entities (client, family, providers unique to case)
- Isolated for performance and data segmentation

**Note:** Individual case graphs have been deleted during cleanup (December 21, 2025). The architecture supports both patterns, but current deployment uses only `roscoe_graph` (workflow definitions) and `whaley_law_firm` (firm-wide knowledge).

---

## Future Enhancements

### Potential Additions:

1. **Entity Types** - Populate `entity_type` field for better classification
2. **Relationship Properties** - Add metadata to MENTIONS and RELATES_TO (dates, confidence scores)
3. **Additional Relationship Types**:
   - `TREATED_BY` (client → provider)
   - `INSURED_BY` (client → insurance company)
   - `REPRESENTS` (attorney → client)
   - `EMPLOYED_BY` (person → organization)

4. **Temporal Queries** - Leverage `valid_at` timestamps for historical state reconstruction
5. **Entity Resolution** - Merge duplicate entities (e.g., "Caryn McCay" vs "Carmen McCay")
6. **Schema Validation** - Enforce required properties and data types

---

## Maintenance

### Cleanup Operations

```bash
# Delete all individual case graphs (keep only firm-wide graphs)
for graph in $(sudo docker exec roscoe-graphdb redis-cli -p 6379 'GRAPH.LIST' | grep -v '^roscoe_graph$' | grep -v '^whaley_law_firm$'); do
  sudo docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.DELETE $graph
done

# Delete specific graph
sudo docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.DELETE roscoe_graph_v2
```

### Health Checks

```bash
# Test FalkorDB connection
sudo docker exec roscoe-graphdb redis-cli -p 6379 PING

# List all graphs
sudo docker exec roscoe-graphdb redis-cli -p 6379 'GRAPH.LIST'

# Check graph stats
sudo docker exec roscoe-graphdb redis-cli -p 6379 'GRAPH.QUERY' 'whaley_law_firm' 'MATCH (n) RETURN labels(n), COUNT(n)'
```

---

## References

- **Graphiti Documentation:** https://github.com/getzep/graphiti
- **FalkorDB Documentation:** https://docs.falkordb.com/
- **Roscoe Graphiti Client:** `src/roscoe/core/graphiti_client.py`
- **Workflow State Computer:** `src/roscoe/core/workflow_state_computer.py`
- **Agent Tools:** `src/roscoe/agents/paralegal/tools.py` (update_case_data, query_case_graph, graph_query)

---

## Schema Version

**Version:** 1.0
**Last Updated:** December 21, 2025
**Status:** Active Production Schema
