# Knowledge Graph (FalkorDB)

## Architecture

Two-layer hybrid:
1. **Direct Cypher** - Structured entities, workflow state
2. **Graphiti** - Semantic search for episodes/notes

## Agent Tools

```python
# CREATE/UPDATE entities (40+ types)
write_entity(
    entity_type="Facility",
    name="UK Hospital",
    properties={"address": "123 Main St"},
    relationships=[
        {"type": "PART_OF", "target_type": "HealthSystem", "target_name": "UK Healthcare"}
    ],
    case_name="Wilson-MVA-2024"
)

# SEMANTIC SEARCH
query_case_graph(
    case_name="Wilson-MVA-2024",
    query="What medical providers treated the patient?"
)

# STRUCTURED QUERIES
graph_query(query_type="cases_by_provider", entity_name="Dr. Smith")

# Custom Cypher
graph_query(
    query_type="custom_cypher",
    custom_query="MATCH (c:Case)-[:HAS_CLAIM]->(claim:BIClaim) RETURN c.name, claim.claim_number"
)

# GET CASE STRUCTURE
get_case_structure(case_name="Wilson-MVA-2024", info_type="insurance")
```

## Entity Types

**Core:** Case, Client, Defendant, Organization
**Insurance:** Insurer, Adjuster, InsurancePolicy, BIClaim, PIPClaim, UMClaim
**Medical:** HealthSystem, Facility, Location, Doctor, MedicalProvider
**Court:** Court, CircuitJudge, DistrictJudge, Pleading
**Legal:** Attorney, LawFirm
**Financial:** Bill, Expense, Lien, Settlement
**Workflow:** Phase, Landmark, LandmarkStatus

## Key Relationships

```cypher
(Case)-[:HAS_CLIENT]->(Client)
(Case)-[:IN_PHASE]->(Phase)
(Case)-[:HAS_CLAIM]->(BIClaim|PIPClaim|UMClaim)
(Case)-[:HAS_LIEN]->(Lien)
(Location)-[:PART_OF]->(Facility)-[:PART_OF]->(HealthSystem)
(Client)-[:TREATED_AT]->(Location|Facility)
(Claim)-[:UNDER_POLICY]->(InsurancePolicy)-[:WITH_INSURER]->(Insurer)
(Case)-[:HAS_STATUS]->(LandmarkStatus)-[:FOR_LANDMARK]->(Landmark)
```

## Modules

| Module | Purpose |
|--------|---------|
| `graphiti_client.py` | Graphiti + direct Cypher queries |
| `graph_manager.py` | Structured entity creation helpers |
| `graph_state_computer.py` | Workflow state from graph |
