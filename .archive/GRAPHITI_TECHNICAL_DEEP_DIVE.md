# Graphiti Technical Deep Dive

**A Complete Step-by-Step Analysis of How Graphiti Ingests Episodes and Searches Content**

Version: Based on Graphiti codebase analysis (December 2024)

---

## Table of Contents

1. [Overview](#overview)
2. [Episode Ingestion: Complete Flow](#episode-ingestion-complete-flow)
3. [Node Extraction Process](#node-extraction-process)
4. [Node Deduplication Process](#node-deduplication-process)
5. [Edge Extraction Process](#edge-extraction-process)
6. [Edge Deduplication Process](#edge-deduplication-process)
7. [Edge Invalidation Process](#edge-invalidation-process)
8. [Attribute & Summary Extraction](#attribute--summary-extraction)
9. [Search Flow](#search-flow)
10. [All LLM Prompts](#all-llm-prompts)
11. [Key Implementation Details](#key-implementation-details)

---

## Overview

### What is Graphiti?

Graphiti is a **temporally-aware knowledge graph framework** that builds graphs from conversational or textual episodes. Unlike traditional RAG (Retrieval-Augmented Generation), Graphiti:

- **Incrementally updates** the graph without batch reprocessing
- **Tracks temporal state** with bi-temporal data (when events occurred vs when they were recorded)
- **Automatically deduplicates** entities and relationships
- **Invalidates contradicting facts** based on temporal ordering
- **Uses hybrid search** (semantic embeddings + keyword/BM25 + graph traversal)

### Core Architecture

```
Episode (Raw Content)
    ↓
1. Extract Nodes (Entities)
    ↓
2. Deduplicate Nodes (via similarity + LLM)
    ↓
3. Extract Edges (Relationships)
    ↓
4. Deduplicate Edges (via similarity + LLM)
    ↓
5. Invalidate Contradicting Edges (temporal logic)
    ↓
6. Extract Attributes & Summaries
    ↓
7. Generate Embeddings
    ↓
8. Save to Graph Database
```

**Key Files:**
- Main orchestration: `graphiti_core/graphiti.py`
- Node operations: `graphiti_core/utils/maintenance/node_operations.py`
- Edge operations: `graphiti_core/utils/maintenance/edge_operations.py`
- Search: `graphiti_core/search/search.py`
- Prompts: `graphiti_core/prompts/*.py`

---

## Episode Ingestion: Complete Flow

### Entry Point: `add_episode()` (graphiti.py:616)

**Function Signature:**
```python
async def add_episode(
    name: str,
    episode_body: str,
    source_description: str,
    reference_time: datetime,
    source: EpisodeType = EpisodeType.message,
    group_id: str | None = None,
    uuid: str | None = None,
    update_communities: bool = False,
    entity_types: dict[str, type[BaseModel]] | None = None,
    excluded_entity_types: list[str] | None = None,
    previous_episode_uuids: list[str] | None = None,
    edge_types: dict[str, type[BaseModel]] | None = None,
    edge_type_map: dict[tuple[str, str], list[str]] | None = None,
) -> AddEpisodeResults
```

### Step-by-Step Execution

#### **Step 1: Retrieve Previous Episodes (Context)**
```python
# Line 707-716
previous_episodes = (
    await self.retrieve_episodes(
        reference_time,
        last_n=RELEVANT_SCHEMA_LIMIT,
        group_ids=[group_id],
        source=source,
    )
    if previous_episode_uuids is None
    else await EpisodicNode.get_by_uuids(self.driver, previous_episode_uuids)
)
```
- **Purpose:** Get recent episodes for context (used in prompts)
- **Default:** Last 10 episodes (RELEVANT_SCHEMA_LIMIT=10)
- **Order:** Most recent first

#### **Step 2: Create Episode Node**
```python
# Line 719-732
episode = EpisodicNode(
    name=name,
    group_id=group_id,
    labels=[],
    source=source,  # message, text, or json
    content=episode_body,
    source_description=source_description,
    created_at=now,
    valid_at=reference_time,
)
```

#### **Step 3: Extract Nodes (Entities)**
```python
# Line 742-744
extracted_nodes = await extract_nodes(
    self.clients, episode, previous_episodes, entity_types, excluded_entity_types
)
```
- **Function:** `node_operations.py:extract_nodes()`
- **LLM Call:** Extracts entity names and types from episode content
- **Reflexion Loop:** Re-runs if entities are missed (up to MAX_REFLEXION_ITERATIONS=3)
- **Output:** List of `EntityNode` objects with names and labels

**See [Node Extraction Process](#node-extraction-process) for details.**

#### **Step 4: Resolve Extracted Nodes (Deduplication)**
```python
# Line 746-752
nodes, uuid_map, _ = await resolve_extracted_nodes(
    self.clients,
    extracted_nodes,
    episode,
    previous_episodes,
    entity_types,
)
```
- **Function:** `node_operations.py:resolve_extracted_nodes()`
- **Process:**
  1. Search graph for similar nodes (hybrid search)
  2. Deterministic similarity matching (exact name match)
  3. LLM-based deduplication for ambiguous cases
- **Output:**
  - `nodes`: Deduplicated list of nodes
  - `uuid_map`: Maps extracted node UUIDs to canonical UUIDs

**See [Node Deduplication Process](#node-deduplication-process) for details.**

#### **Step 5: Extract Edges (Relationships)**
```python
# Line 755-764
resolved_edges, invalidated_edges = await self._extract_and_resolve_edges(
    episode,
    extracted_nodes,
    previous_episodes,
    edge_type_map or edge_type_map_default,
    group_id,
    edge_types,
    nodes,
    uuid_map,
)
```
- **Extracts relationships** between entities
- **Resolves duplicates** against existing edges
- **Identifies contradictions** (edges to invalidate)

**See [Edge Extraction](#edge-extraction-process) and [Edge Deduplication](#edge-deduplication-process) for details.**

#### **Step 6: Extract Node Attributes & Summaries**
```python
# Line 767-769
hydrated_nodes = await extract_attributes_from_nodes(
    self.clients, nodes, episode, previous_episodes, entity_types
)
```
- **For each node:**
  - Extract custom attributes (if entity_type has Pydantic fields)
  - Generate/update summary

**See [Attribute & Summary Extraction](#attribute--summary-extraction) for details.**

#### **Step 7: Build Episodic Edges**
```python
# Line 774-776
episodic_edges, episode = await self._process_episode_data(
    episode, hydrated_nodes, entity_edges, now
)
```
- **Creates edges** from Episode → Entities (MENTIONS relationship)
- **Purpose:** Track which episode mentioned which entities

#### **Step 8: Generate Embeddings**
```python
# Within add_nodes_and_edges_bulk
await create_entity_node_embeddings(embedder, nodes)
await create_entity_edge_embeddings(embedder, edges)
```
- **Node embeddings:** Based on node name
- **Edge embeddings:** Based on fact text

#### **Step 9: Save to Graph Database**
```python
await add_nodes_and_edges_bulk(
    self.driver,
    [episode],
    episodic_edges,
    nodes,
    entity_edges,
    self.embedder,
)
```
- **Saves:**
  - Episode node
  - Episodic edges (Episode → Entity)
  - Entity nodes
  - Entity edges (Entity → Entity)

#### **Step 10: Optional Community Update**
```python
# Line 781-788 (if update_communities=True)
communities, community_edges = await semaphore_gather(
    *[
        update_community(self.driver, self.llm_client, self.embedder, node)
        for node in nodes
    ]
)
```
- **Uses community detection** algorithms (e.g., Louvain)
- **Generates community summaries** via LLM

---

## Node Extraction Process

**Location:** `graphiti_core/utils/maintenance/node_operations.py:extract_nodes()`

### Algorithm Flow

```
1. Build entity type context (Entity + custom types)
2. Run LLM extraction (different prompts for message/text/json)
3. Reflexion loop: Check if entities were missed
4. If missed: Re-run with custom prompt listing missed entities
5. Filter out excluded entity types
6. Create EntityNode objects
```

### Step-by-Step

#### **1. Prepare Entity Types Context**
```python
# Line 102-121
entity_types_context = [
    {
        'entity_type_id': 0,
        'entity_type_name': 'Entity',
        'entity_type_description': 'Default entity classification...',
    }
]

entity_types_context += [
    {
        'entity_type_id': i + 1,
        'entity_type_name': type_name,
        'entity_type_description': type_model.__doc__,
    }
    for i, (type_name, type_model) in enumerate(entity_types.items())
]
```
- **Default type:** Always includes "Entity" as type 0
- **Custom types:** Numbered 1, 2, 3... with their docstrings as descriptions

#### **2. Initial LLM Extraction**
```python
# Line 133-153
if episode.source == EpisodeType.message:
    llm_response = await llm_client.generate_response(
        prompt_library.extract_nodes.extract_message(context),
        response_model=ExtractedEntities,
        group_id=episode.group_id,
        prompt_name='extract_nodes.extract_message',
    )
elif episode.source == EpisodeType.text:
    # Uses extract_text prompt
elif episode.source == EpisodeType.json:
    # Uses extract_json prompt
```
- **Different prompts** for different episode types
- **Structured output:** Returns `ExtractedEntities` (list of name + type_id)

**See [LLM Prompts: Node Extraction](#node-extraction-prompts) for exact prompts.**

#### **3. Reflexion Loop (Up to 3 iterations)**
```python
# Line 132-174
while entities_missed and reflexion_iterations <= MAX_REFLEXION_ITERATIONS:
    # Extract entities
    llm_response = await llm_client.generate_response(...)

    # Check if any were missed
    if reflexion_iterations < MAX_REFLEXION_ITERATIONS:
        missing_entities = await extract_nodes_reflexion(
            llm_client, episode, previous_episodes,
            [entity.name for entity in extracted_entities],
            episode.group_id,
        )

        entities_missed = len(missing_entities) != 0

        # If missed, add to custom_prompt for next iteration
        custom_prompt = 'Make sure that the following entities are extracted: '
        for entity in missing_entities:
            custom_prompt += f'\n{entity},'
```

**Reflexion prompt:**
```python
# prompts/extract_nodes.py:reflexion()
Given:
- PREVIOUS MESSAGES
- CURRENT MESSAGE
- EXTRACTED ENTITIES

Determine if any entities haven't been extracted.
```

#### **4. Filter Excluded Types**
```python
# Line 189-192
if excluded_entity_types and entity_type_name in excluded_entity_types:
    logger.debug(f'Excluding entity "{extracted_entity.name}" of type "{entity_type_name}"')
    continue
```

#### **5. Create EntityNode Objects**
```python
# Line 196-203
new_node = EntityNode(
    name=extracted_entity.name,
    group_id=episode.group_id,
    labels=list({'Entity', str(entity_type_name)}),
    summary='',
    created_at=utc_now(),
)
```
- **UUID:** Auto-generated
- **Labels:** Always includes "Entity" + custom type
- **Summary:** Initially empty (filled later)

---

## Node Deduplication Process

**Location:** `graphiti_core/utils/maintenance/node_operations.py:resolve_extracted_nodes()`

### Algorithm Flow

```
1. Search graph for candidate nodes (hybrid search on each node name)
2. Build candidate indexes (by name similarity)
3. Deterministic resolution (exact name match)
4. LLM-based resolution (for ambiguous cases)
5. Return deduplicated nodes + UUID mapping
```

### Step-by-Step

#### **1. Collect Candidate Nodes**
```python
# Line 211-243: _collect_candidate_nodes()
search_results = await semaphore_gather(
    *[
        search(
            clients=clients,
            query=node.name,
            group_ids=[node.group_id],
            search_filter=SearchFilters(),
            config=NODE_HYBRID_SEARCH_RRF,
        )
        for node in extracted_nodes
    ]
)

candidate_nodes = [node for result in search_results for node in result.nodes]
```
- **Performs hybrid search** for each extracted node name
- **Returns top-N similar nodes** from the graph
- **Deduplicates candidates** by UUID

#### **2. Build Candidate Indexes**
```python
# dedup_helpers.py:_build_candidate_indexes()
def _build_candidate_indexes(existing_nodes: list[EntityNode]) -> DedupCandidateIndexes:
    uuid_to_idx: dict[str, int] = {}
    name_to_indices: dict[str, list[int]] = defaultdict(list)
    normalized_name_to_indices: dict[str, list[int]] = defaultdict(list)

    for idx, node in enumerate(existing_nodes):
        uuid_to_idx[node.uuid] = idx
        name_to_indices[node.name].append(idx)
        normalized = _normalize_string_exact(node.name)
        normalized_name_to_indices[normalized].append(idx)

    return DedupCandidateIndexes(...)
```
- **Purpose:** Fast lookup by exact name or normalized name

#### **3. Deterministic Similarity Resolution**
```python
# dedup_helpers.py:_resolve_with_similarity()
def _resolve_with_similarity(
    extracted_nodes: list[EntityNode],
    indexes: DedupCandidateIndexes,
    state: DedupResolutionState,
) -> None:
    for idx, extracted_node in enumerate(extracted_nodes):
        normalized_name = _normalize_string_exact(extracted_node.name)

        # Exact normalized match?
        if normalized_name in indexes.normalized_name_to_indices:
            candidate_indices = indexes.normalized_name_to_indices[normalized_name]
            best_idx = candidate_indices[0]
            resolved_node = indexes.existing_nodes[best_idx]

            state.resolved_nodes[idx] = resolved_node
            state.uuid_map[extracted_node.uuid] = resolved_node.uuid
            state.duplicate_pairs.append((extracted_node, resolved_node))
        else:
            # Leave unresolved for LLM
            state.unresolved_indices.append(idx)
```

**Normalization:**
```python
def _normalize_string_exact(s: str) -> str:
    return s.strip().lower()
```

#### **4. LLM-Based Resolution (for ambiguous cases)**
```python
# node_operations.py:_resolve_with_llm()
# Line 246-393

# Build context with unresolved nodes
extracted_nodes_context = [
    {
        'id': i,
        'name': node.name,
        'entity_type': node.labels,
        'entity_type_description': entity_types_dict.get(...).__doc__,
    }
    for i, node in enumerate(llm_extracted_nodes)
]

existing_nodes_context = [
    {
        'idx': i,
        'name': candidate.name,
        'entity_types': candidate.labels,
        **candidate.attributes,  # Include all custom attributes
    }
    for i, candidate in enumerate(indexes.existing_nodes)
]

# Call LLM
llm_response = await llm_client.generate_response(
    prompt_library.dedupe_nodes.nodes(context),
    response_model=NodeResolutions,
    prompt_name='dedupe_nodes.nodes',
)

# Process resolutions
for resolution in node_resolutions:
    relative_id = resolution.id
    duplicate_idx = resolution.duplicate_idx

    if duplicate_idx == -1:
        # No duplicate found
        resolved_node = extracted_node
    elif 0 <= duplicate_idx < len(indexes.existing_nodes):
        # Duplicate found
        resolved_node = indexes.existing_nodes[duplicate_idx]

    state.resolved_nodes[original_index] = resolved_node
    state.uuid_map[extracted_node.uuid] = resolved_node.uuid
```

**LLM Prompt:**
```python
# prompts/dedupe_nodes.py:nodes()
Given:
- PREVIOUS MESSAGES (context)
- CURRENT MESSAGE
- ENTITIES (extracted, with id, name, entity_type, entity_type_description)
- EXISTING ENTITIES (candidates, with idx, name, entity_types, attributes)

For each ENTITY:
  Determine if it's a duplicate of any EXISTING ENTITY.

Rules:
- Entities are duplicates if they refer to the *same real-world object or concept*
- Do NOT mark as duplicates if they are related but distinct
- Semantic equivalence: "John's company" vs "Acme Corp" can be duplicates if context confirms

Response format:
{
  "entity_resolutions": [
    {
      "id": <entity id from ENTITIES>,
      "name": <best full name>,
      "duplicate_idx": <idx from EXISTING ENTITIES, or -1>,
      "duplicates": [<all duplicate idx values>]
    }
  ]
}
```

**See [LLM Prompts: Node Deduplication](#node-deduplication-prompts) for full prompt.**

#### **5. Return Results**
```python
return (
    [node for node in state.resolved_nodes if node is not None],
    state.uuid_map,  # Maps extracted UUID → canonical UUID
    new_node_duplicates,  # List of (extracted, canonical) pairs
)
```

---

## Edge Extraction Process

**Location:** `graphiti_core/utils/maintenance/edge_operations.py:extract_edges()`

### Algorithm Flow

```
1. Prepare edge type context (custom fact types)
2. Run LLM extraction (extract facts between entities)
3. Reflexion loop: Check if facts were missed
4. Validate entity IDs
5. Parse temporal information (valid_at, invalid_at)
6. Create EntityEdge objects
```

### Step-by-Step

#### **1. Prepare Edge Types Context**
```python
# Line 103-120
edge_type_signature_map = {
    edge_type: signature
    for signature, edge_types in edge_type_map.items()
    for edge_type in edge_types
}

edge_types_context = [
    {
        'fact_type_name': type_name,
        'fact_type_signature': edge_type_signature_map.get(type_name, ('Entity', 'Entity')),
        'fact_type_description': type_model.__doc__,
    }
    for type_name, type_model in edge_types.items()
]
```

**Example:**
```python
edge_type_map = {
    ('Person', 'Company'): ['WORKS_AT', 'FOUNDED'],
    ('Person', 'Person'): ['KNOWS', 'MARRIED_TO'],
}
```

#### **2. Prepare Node Context**
```python
# Line 122-133
context = {
    'episode_content': episode.content,
    'nodes': [
        {'id': idx, 'name': node.name, 'entity_types': node.labels}
        for idx, node in enumerate(nodes)
    ],
    'previous_episodes': [ep.content for ep in previous_episodes],
    'reference_time': episode.valid_at,
    'edge_types': edge_types_context,
    'custom_prompt': '',
}
```

#### **3. LLM Extraction with Reflexion**
```python
# Line 137-168
while facts_missed and reflexion_iterations <= MAX_REFLEXION_ITERATIONS:
    # Extract edges
    llm_response = await llm_client.generate_response(
        prompt_library.extract_edges.edge(context),
        response_model=ExtractedEdges,
        max_tokens=extract_edges_max_tokens,
        group_id=group_id,
        prompt_name='extract_edges.edge',
    )
    edges_data = ExtractedEdges(**llm_response).edges

    # Check if any facts were missed
    if reflexion_iterations < MAX_REFLEXION_ITERATIONS:
        reflexion_response = await llm_client.generate_response(
            prompt_library.extract_edges.reflexion(context),
            response_model=MissingFacts,
            ...
        )

        missing_facts = reflexion_response.get('missing_facts', [])

        if missing_facts:
            custom_prompt = 'The following facts were missed: '
            for fact in missing_facts:
                custom_prompt += f'\n{fact},'
            context['custom_prompt'] = custom_prompt
```

**Extracted Edge Structure:**
```python
class Edge(BaseModel):
    relation_type: str  # e.g., "WORKS_AT"
    source_entity_id: int  # Index in nodes list
    target_entity_id: int  # Index in nodes list
    fact: str  # Natural language description
    valid_at: str | None  # ISO 8601 datetime
    invalid_at: str | None  # ISO 8601 datetime
```

**See [LLM Prompts: Edge Extraction](#edge-extraction-prompts) for exact prompt.**

#### **4. Validate Entity IDs**
```python
# Line 188-201
source_node_idx = edge_data.source_entity_id
target_node_idx = edge_data.target_entity_id

if not (0 <= source_node_idx < len(nodes) and 0 <= target_node_idx < len(nodes)):
    logger.warning(
        f'Invalid entity IDs in edge extraction for {edge_data.relation_type}. '
        f'source_entity_id: {source_node_idx}, target_entity_id: {target_node_idx}, '
        f'but only {len(nodes)} entities available (valid range: 0-{len(nodes) - 1})'
    )
    continue
```

#### **5. Parse Temporal Information**
```python
# Line 205-219
if valid_at:
    try:
        valid_at_datetime = ensure_utc(
            datetime.fromisoformat(valid_at.replace('Z', '+00:00'))
        )
    except ValueError as e:
        logger.warning(f'Error parsing valid_at date: {e}. Input: {valid_at}')

if invalid_at:
    try:
        invalid_at_datetime = ensure_utc(
            datetime.fromisoformat(invalid_at.replace('Z', '+00:00'))
        )
    except ValueError as e:
        logger.warning(f'Error parsing invalid_at date: {e}. Input: {invalid_at}')
```

#### **6. Create EntityEdge Objects**
```python
# Line 220-235
edge = EntityEdge(
    source_node_uuid=source_node_uuid,
    target_node_uuid=target_node_uuid,
    name=edge_data.relation_type,
    group_id=group_id,
    fact=edge_data.fact,
    episodes=[episode.uuid],
    created_at=utc_now(),
    valid_at=valid_at_datetime,
    invalid_at=invalid_at_datetime,
)
edges.append(edge)
```

---

## Edge Deduplication Process

**Location:** `graphiti_core/utils/maintenance/edge_operations.py:resolve_extracted_edges()`

### Algorithm Flow

```
1. Fast deduplication (exact fact match within extracted edges)
2. Generate embeddings for all edges
3. Search for related edges (between same nodes)
4. Search for edge invalidation candidates (semantic search)
5. LLM-based resolution (dedupe + contradiction detection)
6. Apply temporal invalidation logic
7. Extract edge attributes (if custom edge types)
```

### Step-by-Step

#### **1. Fast Path: Exact Deduplication**
```python
# Line 249-263
seen: dict[tuple[str, str, str], EntityEdge] = {}
deduplicated_edges: list[EntityEdge] = []

for edge in extracted_edges:
    key = (
        edge.source_node_uuid,
        edge.target_node_uuid,
        _normalize_string_exact(edge.fact),
    )
    if key not in seen:
        seen[key] = edge
        deduplicated_edges.append(edge)
```
- **Purpose:** Eliminate exact duplicates within the same extraction batch

#### **2. Generate Embeddings**
```python
# Line 268
await create_entity_edge_embeddings(embedder, extracted_edges)
```
- **Embeddings based on:** `edge.fact` (the natural language description)

#### **3. Search for Related Edges**
```python
# Line 270-290
# Get edges between same nodes
valid_edges_list = await semaphore_gather(
    *[
        EntityEdge.get_between_nodes(driver, edge.source_node_uuid, edge.target_node_uuid)
        for edge in extracted_edges
    ]
)

# Semantic search within those edges
related_edges_results = await semaphore_gather(
    *[
        search(
            clients,
            extracted_edge.fact,
            group_ids=[extracted_edge.group_id],
            config=EDGE_HYBRID_SEARCH_RRF,
            search_filter=SearchFilters(edge_uuids=[edge.uuid for edge in valid_edges]),
        )
        for extracted_edge, valid_edges in zip(extracted_edges, valid_edges_list)
    ]
)
```
- **Purpose:** Find edges between same source/target nodes that might be duplicates

#### **4. Search for Invalidation Candidates**
```python
# Line 292-307
edge_invalidation_candidate_results = await semaphore_gather(
    *[
        search(
            clients,
            extracted_edge.fact,
            group_ids=[extracted_edge.group_id],
            config=EDGE_HYBRID_SEARCH_RRF,
            search_filter=SearchFilters(),  # No filter - search all edges
        )
        for extracted_edge in extracted_edges
    ]
)
```
- **Purpose:** Find edges that might contradict the new edge

#### **5. Resolve Each Edge**
```python
# Line 364-385
results = await semaphore_gather(
    *[
        resolve_extracted_edge(
            llm_client,
            extracted_edge,
            related_edges,
            existing_edges,
            episode,
            extracted_edge_types,
            custom_type_names,
        )
        for extracted_edge, related_edges, existing_edges, extracted_edge_types
        in zip(extracted_edges, related_edges_lists, edge_invalidation_candidates, edge_types_lst)
    ]
)
```

**See [resolve_extracted_edge()](#resolve_extracted_edge-function) below.**

---

### `resolve_extracted_edge()` Function

**Location:** `edge_operations.py:444`

#### Fast Path: Exact Match
```python
# Line 482-493
normalized_fact = _normalize_string_exact(extracted_edge.fact)
for edge in related_edges:
    if (
        edge.source_node_uuid == extracted_edge.source_node_uuid
        and edge.target_node_uuid == extracted_edge.target_node_uuid
        and _normalize_string_exact(edge.fact) == normalized_fact
    ):
        resolved = edge
        if episode.uuid not in resolved.episodes:
            resolved.episodes.append(episode.uuid)
        return resolved, [], []
```
- **If exact match found:** Reuse existing edge, just add episode UUID

#### LLM-Based Resolution
```python
# Prepare context
related_edges_context = [{'idx': i, 'fact': edge.fact} for i, edge in enumerate(related_edges)]
existing_edges_context = [{'idx': i, 'fact': edge.fact} for i, edge in enumerate(existing_edges)]

edge_types_context = [
    {
        'fact_type_name': type_name,
        'fact_type_description': type_model.__doc__,
    }
    for type_name, type_model in edge_type_candidates.items()
]

context = {
    'new_edge': {'fact': extracted_edge.fact},
    'existing_edges': related_edges_context,
    'edge_invalidation_candidates': existing_edges_context,
    'edge_types': edge_types_context,
}

# Call LLM
llm_response = await llm_client.generate_response(
    prompt_library.dedupe_edges.resolve_edge(context),
    response_model=EdgeDuplicate,
    prompt_name='dedupe_edges.resolve_edge',
)

# Process response
duplicate_facts = llm_response.get('duplicate_facts', [])
contradicted_facts = llm_response.get('contradicted_facts', [])
fact_type = llm_response.get('fact_type', 'DEFAULT')
```

**Response Structure:**
```python
class EdgeDuplicate(BaseModel):
    duplicate_facts: list[int]  # Indices in related_edges
    contradicted_facts: list[int]  # Indices in existing_edges
    fact_type: str  # Classified fact type or 'DEFAULT'
```

**If duplicate found:**
```python
if duplicate_facts:
    resolved_edge = related_edges[duplicate_facts[0]]
    if episode.uuid not in resolved_edge.episodes:
        resolved_edge.episodes.append(episode.uuid)
```

**If no duplicate:**
```python
else:
    resolved_edge = extracted_edge
    if fact_type in edge_type_candidates:
        resolved_edge.name = fact_type
```

**Process contradictions:**
```python
invalidation_candidates = [existing_edges[i] for i in contradicted_facts]
invalidated_edges = resolve_edge_contradictions(resolved_edge, invalidation_candidates)
```

**See [Edge Invalidation](#edge-invalidation-process) for contradiction logic.**

**Extract edge attributes (if custom type):**
```python
if edge_type_candidates and resolved_edge.name in edge_type_candidates:
    edge_type = edge_type_candidates[resolved_edge.name]

    if len(edge_type.model_fields) > 0:
        attributes_context = {
            'fact': {'fact': resolved_edge.fact, 'attributes': resolved_edge.attributes},
            'episode_content': episode.content,
            'reference_time': episode.valid_at,
        }

        llm_response = await llm_client.generate_response(
            prompt_library.extract_edges.extract_attributes(attributes_context),
            response_model=edge_type,
            ...
        )

        resolved_edge.attributes.update(llm_response)
```

---

## Edge Invalidation Process

**Location:** `edge_operations.py:resolve_edge_contradictions()`

### Temporal Invalidation Logic

```python
def resolve_edge_contradictions(
    resolved_edge: EntityEdge,
    invalidation_candidates: list[EntityEdge]
) -> list[EntityEdge]:

    invalidated_edges: list[EntityEdge] = []

    for edge in invalidation_candidates:
        edge_invalid_at = edge.invalid_at
        resolved_edge_valid_at = resolved_edge.valid_at
        edge_valid_at = edge.valid_at
        resolved_edge_invalid_at = resolved_edge.invalid_at

        # Skip if temporal ranges don't overlap
        if (
            # Edge already ended before new edge starts
            (edge_invalid_at is not None and resolved_edge_valid_at is not None
             and edge_invalid_at <= resolved_edge_valid_at)
            or
            # New edge ended before old edge starts
            (edge_valid_at is not None and resolved_edge_invalid_at is not None
             and resolved_edge_invalid_at <= edge_valid_at)
        ):
            continue

        # New edge invalidates old edge
        if (
            edge_valid_at is not None
            and resolved_edge_valid_at is not None
            and edge_valid_at < resolved_edge_valid_at
        ):
            edge.invalid_at = resolved_edge.valid_at
            edge.expired_at = edge.expired_at if edge.expired_at else utc_now()
            invalidated_edges.append(edge)

    return invalidated_edges
```

### Invalidation Rules

1. **Skip if non-overlapping:**
   - Edge ended before new edge started
   - New edge ended before old edge started

2. **Invalidate if:**
   - Old edge started before new edge
   - Temporal ranges overlap
   - LLM marked as contradicting

3. **Set `invalid_at`:** To the `valid_at` of the new edge
4. **Set `expired_at`:** To current time (when it was detected as invalid)

---

## Attribute & Summary Extraction

**Location:** `node_operations.py:extract_attributes_from_nodes()`

### For Each Node

#### **1. Extract Custom Attributes**
```python
# Only if entity_type has Pydantic fields
if entity_type is not None and len(entity_type.model_fields) > 0:
    attributes_context = {
        'node': {
            'name': node.name,
            'entity_types': node.labels,
            'attributes': node.attributes,
        },
        'episode_content': episode.content,
        'previous_episodes': [ep.content for ep in previous_episodes],
    }

    llm_response = await llm_client.generate_response(
        prompt_library.extract_nodes.extract_attributes(attributes_context),
        response_model=entity_type,
        model_size=ModelSize.small,
        ...
    )

    node.attributes.update(llm_response)
```

**Prompt:**
```python
# prompts/extract_nodes.py:extract_attributes()
Given the MESSAGES and the following ENTITY, update any of its attributes
based on the information provided in MESSAGES.

Guidelines:
1. Do not hallucinate entity property values if they cannot be found
2. Only use the provided MESSAGES and ENTITY to set attribute values

<MESSAGES>
...
</MESSAGES>

<ENTITY>
{node with current attributes}
</ENTITY>
```

#### **2. Extract/Update Summary**
```python
summary_context = {
    'node': {
        'name': node.name,
        'summary': truncate_at_sentence(node.summary, MAX_SUMMARY_CHARS),
        'entity_types': node.labels,
        'attributes': node.attributes,
    },
    'episode_content': episode.content,
    'previous_episodes': [ep.content for ep in previous_episodes],
}

summary_response = await llm_client.generate_response(
    prompt_library.extract_nodes.extract_summary(summary_context),
    response_model=EntitySummary,
    model_size=ModelSize.small,
    ...
)

node.summary = truncate_at_sentence(summary_response.get('summary', ''), MAX_SUMMARY_CHARS)
```

**Prompt:**
```python
# prompts/extract_nodes.py:extract_summary()
Given the MESSAGES and the ENTITY, update the summary that combines
relevant information about the entity from the messages and relevant
information from the existing summary.

{summary_instructions}

<MESSAGES>
...
</MESSAGES>

<ENTITY>
{node with current summary}
</ENTITY>
```

---

## Search Flow

**Location:** `graphiti_core/search/search.py`

### Hybrid Search Architecture

Graphiti uses a **3-layer hybrid search**:

1. **Semantic Search** (Cosine Similarity)
2. **Keyword Search** (BM25 / Fulltext)
3. **Graph Traversal** (BFS from origin nodes)

### Search Configuration

```python
class SearchConfig:
    edge_config: EdgeSearchConfig | None
    node_config: NodeSearchConfig | None
    episode_config: EpisodeSearchConfig | None
    community_config: CommunitySearchConfig | None
    limit: int
    reranker_min_score: float
```

**Example Config (from `search_config_recipes.py`):**
```python
EDGE_HYBRID_SEARCH_RRF = SearchConfig(
    edge_config=EdgeSearchConfig(
        search_methods=[
            EdgeSearchMethod.cosine_similarity,
            EdgeSearchMethod.bm25,
        ],
        reranker=EdgeReranker.rrf,  # Reciprocal Rank Fusion
    ),
    limit=10,
)
```

### Search Methods

#### 1. **Cosine Similarity Search**
```python
# search_utils.py:edge_similarity_search()
async def edge_similarity_search(
    driver: GraphDriver,
    query_vector: list[float],
    group_ids: list[str] | None,
    search_filter: SearchFilters,
    limit: int,
) -> list[tuple[EntityEdge, float]]:

    # Cypher query (example for Neo4j)
    query = """
    MATCH (e:Entity)-[r:RELATES_TO]->(t:Entity)
    WHERE r.fact_embedding IS NOT NULL
      AND ($group_ids IS NULL OR r.group_id IN $group_ids)
    WITH r,
         vector.similarity.cosine(r.fact_embedding, $query_vector) AS score
    WHERE score > 0
    ORDER BY score DESC
    LIMIT $limit
    RETURN r, score
    """

    results = await driver.execute_query(
        query,
        query_vector=query_vector,
        group_ids=group_ids,
        limit=limit,
    )

    return [(EntityEdge.from_db_record(record['r']), record['score'])
            for record in results]
```

#### 2. **BM25 / Fulltext Search**
```python
# search_utils.py:edge_fulltext_search()
async def edge_fulltext_search(
    driver: GraphDriver,
    query: str,
    group_ids: list[str] | None,
    search_filter: SearchFilters,
    limit: int,
) -> list[tuple[EntityEdge, float]]:

    # Cypher query with fulltext index
    query_cypher = """
    CALL db.index.fulltext.queryRelationships('edge_fact_index', $query)
    YIELD relationship, score
    WHERE ($group_ids IS NULL OR relationship.group_id IN $group_ids)
    RETURN relationship, score
    ORDER BY score DESC
    LIMIT $limit
    """

    results = await driver.execute_query(
        query_cypher,
        query=query,
        group_ids=group_ids,
        limit=limit,
    )

    return [(EntityEdge.from_db_record(record['relationship']), record['score'])
            for record in results]
```

#### 3. **Graph Traversal (BFS)**
```python
# search_utils.py:edge_bfs_search()
async def edge_bfs_search(
    driver: GraphDriver,
    origin_node_uuids: list[str],
    group_ids: list[str] | None,
    search_filter: SearchFilters,
    limit: int,
) -> list[tuple[EntityEdge, float]]:

    # BFS from origin nodes up to 3 hops
    query = """
    MATCH path = (origin:Entity)-[:RELATES_TO*1..3]-(related:Entity)
    WHERE origin.uuid IN $origin_uuids
      AND ($group_ids IS NULL OR ALL(r IN relationships(path) WHERE r.group_id IN $group_ids))
    WITH relationships(path) AS edges, length(path) AS distance
    UNWIND edges AS edge
    WITH DISTINCT edge, MIN(distance) AS min_distance
    WITH edge, 1.0 / (min_distance + 1) AS score
    ORDER BY score DESC
    LIMIT $limit
    RETURN edge, score
    """

    results = await driver.execute_query(
        query,
        origin_uuids=origin_node_uuids,
        group_ids=group_ids,
        limit=limit,
    )

    return [(EntityEdge.from_db_record(record['edge']), record['score'])
            for record in results]
```

### Reranking Strategies

#### 1. **RRF (Reciprocal Rank Fusion)**
```python
# search_utils.py:rrf()
def rrf(
    results_lists: list[list[tuple[T, float]]],
    k: int = 60,
) -> list[tuple[T, float]]:
    """
    Combine multiple ranked lists using Reciprocal Rank Fusion.

    RRF formula: score(item) = Σ 1 / (k + rank_i)
    where rank_i is the rank of the item in list i
    """
    scores: dict[str, float] = defaultdict(float)
    items: dict[str, T] = {}

    for results in results_lists:
        for rank, (item, _) in enumerate(results, start=1):
            item_id = item.uuid
            scores[item_id] += 1.0 / (k + rank)
            items[item_id] = item

    # Sort by combined score
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [(items[item_id], score) for item_id, score in sorted_items]
```

**Why RRF?**
- Combines different ranking methods (semantic + keyword)
- Doesn't require score normalization
- Proven effective in information retrieval

#### 2. **MMR (Maximal Marginal Relevance)**
```python
# search_utils.py:maximal_marginal_relevance()
async def maximal_marginal_relevance(
    query_embedding: list[float],
    embedding_list: list[list[float]],
    lambda_mult: float = 0.5,
    k: int = 10,
) -> list[int]:
    """
    Select diverse results using MMR.

    Formula: MMR = λ * Sim(query, doc) - (1-λ) * max(Sim(doc, selected))
    """
    selected_indices: list[int] = []

    # Compute similarity to query
    query_similarities = [
        cosine_similarity(query_embedding, emb)
        for emb in embedding_list
    ]

    while len(selected_indices) < k:
        best_score = -float('inf')
        best_idx = -1

        for idx, emb in enumerate(embedding_list):
            if idx in selected_indices:
                continue

            # Similarity to query
            query_sim = query_similarities[idx]

            # Max similarity to already selected
            if selected_indices:
                max_selected_sim = max(
                    cosine_similarity(emb, embedding_list[sel_idx])
                    for sel_idx in selected_indices
                )
            else:
                max_selected_sim = 0

            # MMR score
            score = lambda_mult * query_sim - (1 - lambda_mult) * max_selected_sim

            if score > best_score:
                best_score = score
                best_idx = idx

        selected_indices.append(best_idx)

    return selected_indices
```

**Why MMR?**
- Reduces redundancy in results
- Balances relevance and diversity

#### 3. **Node Distance Reranker**
```python
# search_utils.py:node_distance_reranker()
async def node_distance_reranker(
    driver: GraphDriver,
    edges: list[EntityEdge],
    center_node_uuid: str,
) -> list[float]:
    """
    Rerank edges by their graph distance from a center node.

    Score = 1 / (distance + 1)
    """
    # Cypher query to find shortest path distances
    query = """
    UNWIND $edge_uuids AS edge_uuid
    MATCH (center:Entity {uuid: $center_uuid})
    MATCH (e:Entity)-[r {uuid: edge_uuid}]->(t:Entity)
    WITH r,
         shortestPath((center)-[*..5]-(e)) AS path1,
         shortestPath((center)-[*..5]-(t)) AS path2
    WITH r,
         CASE WHEN path1 IS NULL THEN 999 ELSE length(path1) END AS dist1,
         CASE WHEN path2 IS NULL THEN 999 ELSE length(path2) END AS dist2
    WITH r, CASE WHEN dist1 < dist2 THEN dist1 ELSE dist2 END AS min_distance
    RETURN r.uuid AS edge_uuid, 1.0 / (min_distance + 1) AS score
    ORDER BY score DESC
    """

    results = await driver.execute_query(
        query,
        edge_uuids=[e.uuid for e in edges],
        center_uuid=center_node_uuid,
    )

    # Map scores back to edges
    score_map = {r['edge_uuid']: r['score'] for r in results}
    return [score_map.get(e.uuid, 0.0) for e in edges]
```

### Complete Search Flow

```python
# search.py:search()
async def search(
    clients: GraphitiClients,
    query: str,
    group_ids: list[str] | None,
    config: SearchConfig,
    search_filter: SearchFilters,
    center_node_uuid: str | None = None,
    bfs_origin_node_uuids: list[str] | None = None,
    query_vector: list[float] | None = None,
) -> SearchResults:

    # Generate query embedding
    if query_vector is None:
        search_vector = await embedder.create(input_data=[query.replace('\n', ' ')])

    # Search each layer in parallel
    (edges, edge_scores), (nodes, node_scores), (episodes, episode_scores), (communities, community_scores) = await semaphore_gather(
        edge_search(...),
        node_search(...),
        episode_search(...),
        community_search(...),
    )

    return SearchResults(
        edges=edges,
        edge_reranker_scores=edge_scores,
        nodes=nodes,
        node_reranker_scores=node_scores,
        episodes=episodes,
        episode_reranker_scores=episode_scores,
        communities=communities,
        community_reranker_scores=community_scores,
    )
```

---

## All LLM Prompts

### Node Extraction Prompts

#### 1. **extract_message** (for conversational episodes)

**Location:** `prompts/extract_nodes.py:extract_message()`

**System Prompt:**
```
You are an AI assistant that extracts entity nodes from conversational messages.
Your primary task is to extract and classify the speaker and other significant
entities mentioned in the conversation.
```

**User Prompt:**
```
<ENTITY TYPES>
[
  {"entity_type_id": 0, "entity_type_name": "Entity", "entity_type_description": "Default..."},
  {"entity_type_id": 1, "entity_type_name": "Person", "entity_type_description": "..."},
  ...
]
</ENTITY TYPES>

<PREVIOUS MESSAGES>
[Previous episode contents for context]
</PREVIOUS MESSAGES>

<CURRENT MESSAGE>
John: Hey, I'm meeting with Sarah at Acme Corp tomorrow about the Q3 project.
</CURRENT MESSAGE>

Instructions:

You are given a conversation context and a CURRENT MESSAGE. Your task is to extract
**entity nodes** mentioned **explicitly or implicitly** in the CURRENT MESSAGE.

Pronoun references such as he/she/they or this/that/those should be disambiguated
to the names of the reference entities. Only extract distinct entities from the
CURRENT MESSAGE. Don't extract pronouns like you, me, he/she/they, we/us as entities.

1. **Speaker Extraction**: Always extract the speaker (the part before the colon `:`)
   as the first entity node.
   - If the speaker is mentioned again in the message, treat both mentions as a
     **single entity**.

2. **Entity Identification**:
   - Extract all significant entities, concepts, or actors that are **explicitly
     or implicitly** mentioned in the CURRENT MESSAGE.
   - **Exclude** entities mentioned only in the PREVIOUS MESSAGES.

3. **Entity Classification**:
   - Use the descriptions in ENTITY TYPES to classify each extracted entity.
   - Assign the appropriate `entity_type_id` for each one.

4. **Exclusions**:
   - Do NOT extract entities representing relationships or actions.
   - Do NOT extract dates, times, or other temporal information.

5. **Formatting**:
   - Be **explicit and unambiguous** in naming entities (e.g., use full names).
```

**Response Model:**
```python
class ExtractedEntities(BaseModel):
    extracted_entities: list[ExtractedEntity]

class ExtractedEntity(BaseModel):
    name: str
    entity_type_id: int
```

**Example Response:**
```json
{
  "extracted_entities": [
    {"name": "John", "entity_type_id": 1},
    {"name": "Sarah", "entity_type_id": 1},
    {"name": "Acme Corp", "entity_type_id": 2},
    {"name": "Q3 project", "entity_type_id": 3}
  ]
}
```

#### 2. **extract_text** (for text episodes)

**User Prompt:**
```
<ENTITY TYPES>
[...]
</ENTITY TYPES>

<TEXT>
The CEO of Acme Corp, John Smith, announced a new partnership with TechVentures Inc.
The deal, valued at $50M, will focus on AI development.
</TEXT>

Given the above text, extract entities from the TEXT that are explicitly or
implicitly mentioned.

For each entity extracted, also determine its entity type based on the provided
ENTITY TYPES and their descriptions.

Guidelines:
1. Extract significant entities, concepts, or actors mentioned in the conversation.
2. Avoid creating nodes for relationships or actions.
3. Avoid creating nodes for temporal information like dates, times or years.
4. Be as explicit as possible in your node names, using full names and avoiding
   abbreviations.
```

#### 3. **extract_json** (for JSON episodes)

**User Prompt:**
```
<ENTITY TYPES>
[...]
</ENTITY TYPES>

<SOURCE DESCRIPTION>:
User profile from CRM system
</SOURCE DESCRIPTION>

<JSON>
{
  "user": "john.smith@acme.com",
  "company": "Acme Corp",
  "role": "CEO",
  "joined_date": "2020-01-15"
}
</JSON>

Given the above source description and JSON, extract relevant entities from the
provided JSON.

Guidelines:
1. Extract all entities that the JSON represents (e.g., "name" or "user" fields)
2. Extract all entities mentioned in other properties throughout the JSON
3. Do NOT extract any properties that contain dates
```

#### 4. **reflexion** (self-check for missed entities)

**User Prompt:**
```
<PREVIOUS MESSAGES>
[...]
</PREVIOUS MESSAGES>

<CURRENT MESSAGE>
[...]
</CURRENT MESSAGE>

<EXTRACTED ENTITIES>
["John", "Sarah", "Acme Corp"]
</EXTRACTED ENTITIES>

Given the above previous messages, current message, and list of extracted entities;
determine if any entities haven't been extracted.
```

**Response Model:**
```python
class MissedEntities(BaseModel):
    missed_entities: list[str]
```

---

### Node Deduplication Prompts

#### 1. **nodes** (batch deduplication)

**Location:** `prompts/dedupe_nodes.py:nodes()`

**System Prompt:**
```
You are a helpful assistant that determines whether or not ENTITIES extracted
from a conversation are duplicates of existing entities.
```

**User Prompt:**
```
<PREVIOUS MESSAGES>
[...]
</PREVIOUS MESSAGES>

<CURRENT MESSAGE>
John: I met with the CEO of Acme yesterday.
</CURRENT MESSAGE>

Each of the following ENTITIES were extracted from the CURRENT MESSAGE:

<ENTITIES>
[
  {"id": 0, "name": "John", "entity_type": ["Entity", "Person"],
   "entity_type_description": "A human being"},
  {"id": 1, "name": "CEO of Acme", "entity_type": ["Entity", "Person"],
   "entity_type_description": "A human being"}
]
</ENTITIES>

<EXISTING ENTITIES>
[
  {"idx": 0, "name": "John Smith", "entity_types": ["Entity", "Person"],
   "summary": "Software engineer at TechCorp"},
  {"idx": 1, "name": "Sarah Johnson", "entity_types": ["Entity", "Person"],
   "summary": "CEO of Acme Corp since 2020"},
  {"idx": 2, "name": "Acme Corp", "entity_types": ["Entity", "Company"]}
]
</EXISTING ENTITIES>

For each of the above ENTITIES, determine if the entity is a duplicate of any
of the EXISTING ENTITIES.

Entities should only be considered duplicates if they refer to the *same
real-world object or concept*.

Do NOT mark entities as duplicates if:
- They are related but distinct.
- They have similar names or purposes but refer to separate instances or concepts.

Task:
ENTITIES contains 2 entities with IDs 0 through 1.
Your response MUST include EXACTLY 2 resolutions with IDs 0 through 1.
Do not skip or add IDs.

For every entity, return an object with the following keys:
{
  "id": <integer id from ENTITIES>,
  "name": <the best full name for the entity>,
  "duplicate_idx": <idx from EXISTING ENTITIES, or -1 if no duplicate>,
  "duplicates": <sorted list of all duplicate idx values, or [] if none>
}

- Only use idx values that appear in EXISTING ENTITIES.
- Set duplicate_idx to the smallest idx you collected, or -1 if duplicates is empty.
- Never fabricate entities or indices.
```

**Response Model:**
```python
class NodeResolutions(BaseModel):
    entity_resolutions: list[NodeDuplicate]

class NodeDuplicate(BaseModel):
    id: int
    duplicate_idx: int
    name: str
    duplicates: list[int]
```

**Example Response:**
```json
{
  "entity_resolutions": [
    {"id": 0, "name": "John Smith", "duplicate_idx": 0, "duplicates": [0]},
    {"id": 1, "name": "Sarah Johnson", "duplicate_idx": 1, "duplicates": [1]}
  ]
}
```

---

### Edge Extraction Prompts

#### 1. **edge** (extract relationships)

**Location:** `prompts/extract_edges.py:edge()`

**System Prompt:**
```
You are an expert fact extractor that extracts fact triples from text.
1. Extracted fact triples should also be extracted with relevant date information.
2. Treat the CURRENT TIME as the time the CURRENT MESSAGE was sent. All temporal
   information should be extracted relative to this time.
```

**User Prompt:**
```
<FACT TYPES>
[
  {"fact_type_name": "WORKS_AT",
   "fact_type_signature": ("Person", "Company"),
   "fact_type_description": "Employment relationship"},
  {"fact_type_name": "FOUNDED",
   "fact_type_signature": ("Person", "Company"),
   "fact_type_description": "Founding relationship"}
]
</FACT TYPES>

<PREVIOUS_MESSAGES>
[...]
</PREVIOUS_MESSAGES>

<CURRENT_MESSAGE>
John Smith joined Acme Corp as CEO in January 2020.
</CURRENT_MESSAGE>

<ENTITIES>
[
  {"id": 0, "name": "John Smith", "entity_types": ["Entity", "Person"]},
  {"id": 1, "name": "Acme Corp", "entity_types": ["Entity", "Company"]}
]
</ENTITIES>

<REFERENCE_TIME>
2024-12-26T00:00:00Z
</REFERENCE_TIME>

# TASK
Extract all factual relationships between the given ENTITIES based on the
CURRENT MESSAGE.

Only extract facts that:
- involve two DISTINCT ENTITIES from the ENTITIES list,
- are clearly stated or unambiguously implied in the CURRENT MESSAGE,
- can be represented as edges in a knowledge graph.
- Facts should include entity names rather than pronouns whenever possible.
- The FACT TYPES provide a list of important types, make sure to extract facts
  of these types.
- FACT TYPES are not exhaustive, extract all facts even if they don't fit.

You may use PREVIOUS MESSAGES only to disambiguate references or support continuity.

# EXTRACTION RULES

1. **Entity ID Validation**: source_entity_id and target_entity_id must use only
   the `id` values from the ENTITIES list.
2. Each fact must involve two **distinct** entities.
3. Use a SCREAMING_SNAKE_CASE string as the `relation_type` (e.g., WORKS_AT).
4. Do not emit duplicate or semantically redundant facts.
5. The `fact` should closely paraphrase the original source sentence(s).
6. Use `REFERENCE_TIME` to resolve vague or relative temporal expressions
   (e.g., "last week").
7. Do **not** hallucinate or infer temporal bounds from unrelated events.

# DATETIME RULES

- Use ISO 8601 with "Z" suffix (UTC) (e.g., 2025-04-30T00:00:00Z).
- If the fact is ongoing (present tense), set `valid_at` to REFERENCE_TIME.
- If a change/termination is expressed, set `invalid_at` to the relevant timestamp.
- Leave both fields `null` if no explicit or resolvable time is stated.
- If only a date is mentioned (no time), assume 00:00:00.
- If only a year is mentioned, use January 1st at 00:00:00.
```

**Response Model:**
```python
class ExtractedEdges(BaseModel):
    edges: list[Edge]

class Edge(BaseModel):
    relation_type: str
    source_entity_id: int
    target_entity_id: int
    fact: str
    valid_at: str | None
    invalid_at: str | None
```

**Example Response:**
```json
{
  "edges": [
    {
      "relation_type": "WORKS_AT",
      "source_entity_id": 0,
      "target_entity_id": 1,
      "fact": "John Smith joined Acme Corp as CEO",
      "valid_at": "2020-01-01T00:00:00Z",
      "invalid_at": null
    }
  ]
}
```

#### 2. **reflexion** (self-check for missed facts)

**User Prompt:**
```
<PREVIOUS MESSAGES>
[...]
</PREVIOUS MESSAGES>

<CURRENT MESSAGE>
[...]
</CURRENT MESSAGE>

<EXTRACTED ENTITIES>
[...]
</EXTRACTED ENTITIES>

<EXTRACTED FACTS>
["John Smith joined Acme Corp as CEO"]
</EXTRACTED FACTS>

Given the above MESSAGES, list of EXTRACTED ENTITIES, and list of EXTRACTED FACTS;
determine if any facts haven't been extracted.
```

**Response Model:**
```python
class MissingFacts(BaseModel):
    missing_facts: list[str]
```

---

### Edge Deduplication Prompts

#### 1. **resolve_edge** (dedupe + contradiction detection)

**Location:** `prompts/dedupe_edges.py:resolve_edge()`

**System Prompt:**
```
You are a helpful assistant that de-duplicates facts from fact lists and
determines which existing facts are contradicted by the new fact.
```

**User Prompt:**
```
Task:
You will receive TWO separate lists of facts. Each list uses 'idx' as its index
field, starting from 0.

1. DUPLICATE DETECTION:
   - If the NEW FACT represents identical factual information as any fact in
     EXISTING FACTS, return those idx values in duplicate_facts.
   - Facts with similar information that contain key differences should NOT be
     marked as duplicates.
   - Return idx values from EXISTING FACTS.
   - If no duplicates, return an empty list for duplicate_facts.

2. FACT TYPE CLASSIFICATION:
   - Given the predefined FACT TYPES, determine if the NEW FACT should be
     classified as one of these types.
   - Return the fact type as fact_type or DEFAULT if not one of the FACT TYPES.

3. CONTRADICTION DETECTION:
   - Based on FACT INVALIDATION CANDIDATES and NEW FACT, determine which facts
     the new fact contradicts.
   - Return idx values from FACT INVALIDATION CANDIDATES.
   - If no contradictions, return an empty list for contradicted_facts.

IMPORTANT:
- duplicate_facts: Use ONLY 'idx' values from EXISTING FACTS
- contradicted_facts: Use ONLY 'idx' values from FACT INVALIDATION CANDIDATES
- These are two separate lists with independent idx ranges starting from 0

Guidelines:
1. Some facts may be very similar but will have key differences, particularly
   around numeric values. Do not mark these facts as duplicates.

<FACT TYPES>
[
  {"fact_type_name": "WORKS_AT", "fact_type_description": "..."},
  {"fact_type_name": "FOUNDED", "fact_type_description": "..."}
]
</FACT TYPES>

<EXISTING FACTS>
[
  {"idx": 0, "fact": "John Smith works at Acme Corp as CEO"},
  {"idx": 1, "fact": "Sarah Johnson founded TechVentures Inc in 2015"}
]
</EXISTING FACTS>

<FACT INVALIDATION CANDIDATES>
[
  {"idx": 0, "fact": "John Smith was employed at OldCorp"},
  {"idx": 1, "fact": "John Smith retired from Acme Corp"}
]
</FACT INVALIDATION CANDIDATES>

<NEW FACT>
{"fact": "John Smith joined Acme Corp as CEO in January 2020"}
</NEW FACT>
```

**Response Model:**
```python
class EdgeDuplicate(BaseModel):
    duplicate_facts: list[int]  # Indices from EXISTING FACTS
    contradicted_facts: list[int]  # Indices from INVALIDATION CANDIDATES
    fact_type: str  # Classified type or 'DEFAULT'
```

**Example Response:**
```json
{
  "duplicate_facts": [0],
  "contradicted_facts": [0],
  "fact_type": "WORKS_AT"
}
```

---

### Attribute Extraction Prompts

#### 1. **extract_attributes** (for nodes)

**Location:** `prompts/extract_nodes.py:extract_attributes()`

**System Prompt:**
```
You are a helpful assistant that extracts entity properties from the provided text.
```

**User Prompt:**
```
Given the MESSAGES and the following ENTITY, update any of its attributes based
on the information provided in MESSAGES. Use the provided attribute descriptions
to better understand how each attribute should be determined.

Guidelines:
1. Do not hallucinate entity property values if they cannot be found in the
   current context.
2. Only use the provided MESSAGES and ENTITY to set attribute values.

<MESSAGES>
[Previous episode contents]
[Current episode content]
</MESSAGES>

<ENTITY>
{
  "name": "John Smith",
  "entity_types": ["Entity", "Person"],
  "attributes": {
    "age": 45,
    "occupation": "CEO"
  }
}
</ENTITY>
```

**Response Model:** Dynamic (based on entity_type Pydantic model)

**Example (if entity_type is Person with fields: age, occupation, location):**
```json
{
  "age": 46,
  "occupation": "CEO",
  "location": "San Francisco"
}
```

#### 2. **extract_summary** (for nodes)

**Location:** `prompts/extract_nodes.py:extract_summary()`

**System Prompt:**
```
You are a helpful assistant that extracts entity summaries from the provided text.
```

**User Prompt:**
```
Given the MESSAGES and the ENTITY, update the summary that combines relevant
information about the entity from the messages and relevant information from
the existing summary.

{summary_instructions}

<MESSAGES>
[Previous episode contents]
[Current episode content]
</MESSAGES>

<ENTITY>
{
  "name": "John Smith",
  "summary": "CEO of Acme Corp since 2020. Background in software engineering.",
  "entity_types": ["Entity", "Person"],
  "attributes": {...}
}
</ENTITY>
```

**Summary Instructions (from `snippets.py`):**
```
Guidelines for summaries:
1. Keep summaries concise (under 500 characters)
2. Include the most important and recent information
3. Combine new information with existing summary
4. Use complete sentences
5. Focus on facts, not speculation
```

**Response Model:**
```python
class EntitySummary(BaseModel):
    summary: str  # Under MAX_SUMMARY_CHARS (500)
```

#### 3. **extract_attributes** (for edges)

**Location:** `prompts/extract_edges.py:extract_attributes()`

**User Prompt:**
```
<MESSAGE>
[Episode content]
</MESSAGE>

<REFERENCE TIME>
2024-12-26T00:00:00Z
</REFERENCE TIME>

Given the above MESSAGE, its REFERENCE TIME, and the following FACT, update
any of its attributes based on the information provided in MESSAGE.

Guidelines:
1. Do not hallucinate property values if they cannot be found
2. Only use the provided MESSAGE and FACT to set attribute values

<FACT>
{
  "fact": "John Smith joined Acme Corp as CEO",
  "attributes": {
    "salary": "$500,000",
    "department": "Executive"
  }
}
</FACT>
```

---

## Key Implementation Details

### 1. Reflexion Loops

**Purpose:** Iteratively improve extraction quality by checking for missed entities/facts.

**Pattern:**
```python
MAX_REFLEXION_ITERATIONS = 3

items_missed = True
reflexion_iterations = 0

while items_missed and reflexion_iterations <= MAX_REFLEXION_ITERATIONS:
    # Initial extraction
    extracted_items = await extract(...)

    # Check if any missed
    reflexion_iterations += 1
    if reflexion_iterations < MAX_REFLEXION_ITERATIONS:
        missing_items = await check_missing(extracted_items)
        items_missed = len(missing_items) != 0

        if items_missed:
            # Add to custom prompt for next iteration
            custom_prompt = f"Make sure to extract: {missing_items}"
```

**Trade-off:**
- **Benefit:** Higher recall (fewer missed items)
- **Cost:** 2-3x LLM calls per extraction

### 2. Embeddings

**Node Embeddings:**
```python
# Based on node name
await node.generate_name_embedding(embedder)
# Stores in: node.name_embedding (list[float], typically 1536 dimensions)
```

**Edge Embeddings:**
```python
# Based on fact text
await edge.generate_embedding(embedder)
# Stores in: edge.fact_embedding (list[float])
```

**Embedding Model:**
- Default: OpenAI `text-embedding-ada-002` (1536 dimensions)
- Configurable via `EmbedderClient`

### 3. Similarity Matching

**Exact String Normalization:**
```python
def _normalize_string_exact(s: str) -> str:
    return s.strip().lower()
```

**Cosine Similarity:**
```python
def cosine_similarity(a: list[float], b: list[float]) -> float:
    import numpy as np
    a_arr = np.array(a)
    b_arr = np.array(b)
    return np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr))
```

### 4. UUID Mapping

**Why?**
- Extracted nodes get temporary UUIDs
- After deduplication, they might map to existing nodes
- UUID map tracks: `extracted_uuid → canonical_uuid`

**Usage:**
```python
# After node deduplication
nodes, uuid_map, duplicates = await resolve_extracted_nodes(...)

# When creating edges
edge.source_node_uuid = uuid_map.get(edge.source_node_uuid, edge.source_node_uuid)
edge.target_node_uuid = uuid_map.get(edge.target_node_uuid, edge.target_node_uuid)
```

### 5. Parallel Processing

**Pattern:**
```python
from graphiti_core.helpers import semaphore_gather

# Process items in parallel with concurrency limit
results = await semaphore_gather(
    *[process_item(item) for item in items],
    max_coroutines=10,  # Configurable via SEMAPHORE_LIMIT env var
)
```

**Semaphore Implementation:**
```python
async def semaphore_gather(
    *tasks: Awaitable[T],
    max_coroutines: int | None = None,
) -> list[T]:
    semaphore = asyncio.Semaphore(max_coroutines or SEMAPHORE_LIMIT)

    async def bounded_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*[bounded_task(task) for task in tasks])
```

**Default:** `SEMAPHORE_LIMIT = 10` (to avoid LLM rate limits)

### 6. Bulk Ingestion

**Location:** `graphiti.py:add_episode_bulk()`

**Optimizations:**
1. **Extract all nodes/edges first**
2. **Deduplicate in-memory** (before hitting DB)
3. **Resolve all against graph in parallel**
4. **Single bulk save operation**

**Trade-offs:**
- ✅ Much faster for large batches
- ❌ No edge invalidation (temporal contradictions not handled)
- ❌ No date extraction

**Use when:** Processing historical data that won't contradict itself.

### 7. Community Detection

**Algorithm:** Louvain community detection (via graph database)

**Process:**
1. Run community detection algorithm on entity graph
2. Group entities into communities
3. Generate community summaries via LLM
4. Create `CommunityNode` objects
5. Link entities to communities via `CommunityEdge`

**Prompt (from `prompts/summarize_nodes.py`):**
```python
Given the following entities and their summaries:

<ENTITIES>
[List of entity names and summaries in the community]
</ENTITIES>

Create a concise summary (2-3 sentences) that describes the common theme
or relationships among these entities.
```

---

## Appendix: File Reference

### Core Files

| File | Purpose |
|------|---------|
| `graphiti_core/graphiti.py` | Main orchestration: `add_episode()`, `search()` |
| `graphiti_core/nodes.py` | Node models: `EpisodicNode`, `EntityNode`, `CommunityNode` |
| `graphiti_core/edges.py` | Edge models: `EpisodicEdge`, `EntityEdge`, `CommunityEdge` |

### Utilities

| File | Purpose |
|------|---------|
| `utils/maintenance/node_operations.py` | Node extraction, deduplication, attribute extraction |
| `utils/maintenance/edge_operations.py` | Edge extraction, deduplication, invalidation |
| `utils/maintenance/graph_data_operations.py` | Episode retrieval, temporal queries |
| `utils/bulk_utils.py` | Bulk ingestion optimizations |

### Prompts

| File | Purpose |
|------|---------|
| `prompts/extract_nodes.py` | Entity extraction prompts |
| `prompts/extract_edges.py` | Relationship extraction prompts |
| `prompts/dedupe_nodes.py` | Entity deduplication prompts |
| `prompts/dedupe_edges.py` | Relationship deduplication prompts |
| `prompts/invalidate_edges.py` | Contradiction detection prompts |
| `prompts/summarize_nodes.py` | Community summarization prompts |

### Search

| File | Purpose |
|------|---------|
| `search/search.py` | Main search orchestration |
| `search/search_utils.py` | Search methods: semantic, keyword, BFS, rerankers |
| `search/search_config.py` | Search configuration models |
| `search/search_config_recipes.py` | Pre-built search configurations |

---

## Summary: Key Takeaways for Your Implementation

### 1. **Extraction Strategy**
- Use **separate prompts** for messages, text, and JSON
- Implement **reflexion loops** to catch missed items (2-3 iterations)
- **Classify entities** into types immediately during extraction

### 2. **Deduplication Strategy**
- **Two-phase approach:**
  1. Fast deterministic matching (exact name normalization)
  2. LLM-based resolution for ambiguous cases
- **Always provide context** (previous episodes, episode content)
- **Return mapping** of extracted UUIDs to canonical UUIDs

### 3. **Temporal Invalidation**
- Track `valid_at` and `invalid_at` on every edge
- **Invalidate old edge if:**
  - New edge contradicts it (per LLM)
  - Old edge started before new edge
  - Temporal ranges overlap
- Set `invalid_at` to new edge's `valid_at`

### 4. **Search Strategy**
- **Hybrid approach:**
  - Semantic (cosine similarity on embeddings)
  - Keyword (BM25 fulltext)
  - Graph traversal (BFS from origin nodes)
- **Combine with RRF** (Reciprocal Rank Fusion)
- **Optional reranking:**
  - MMR (diversity)
  - Node distance (graph proximity)
  - Cross-encoder (LLM-based)

### 5. **Optimization Techniques**
- **Parallel processing** with semaphore (limit concurrency)
- **Bulk operations** for historical data
- **Embedding generation** in batch
- **Fast paths:** Exact string matching before LLM calls

### 6. **Prompt Engineering Tips**
- **Be explicit** about index ranges (0-N)
- **Validate LLM output** (check IDs are in range)
- **Handle malformed responses** gracefully
- **Separate lists** for different purposes (related vs invalidation candidates)
- **Include examples** in prompts when possible

---

## Conclusion

Graphiti's ingestion and search system is built on a sophisticated pipeline that:

1. **Extracts** entities and relationships with high accuracy via reflexion
2. **Deduplicates** intelligently using similarity + LLM
3. **Invalidates** contradictions via temporal logic
4. **Searches** efficiently via hybrid methods
5. **Scales** via parallelization and bulk operations

The key insight is the **two-phase approach** at every step:
- Fast deterministic methods first
- LLM-based resolution for ambiguous cases

This allows Graphiti to maintain **high quality** while staying **performant**.

---

**End of Document**
