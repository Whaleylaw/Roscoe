Brainstorming: Episode-Centric Knowledge Graph Architecture

  Core Concept Understanding

  The Vision:
  - Graph = "What" (current state snapshot - entities, relationships)
  - Episodes = "Why/How" (narrative, timeline, process documentation)
  - Links connect narrative to structure (episodes → entities they discuss)

  Key Requirements Identified

  1. Episode Model Structure:
  Episode node contains:
  - Content (the note text)
  - Timestamp
  - Author/source
  - Episode type (call, email, fax, meeting, document)
  - Default relationship: Episode → Case
  - Additional relationships: Episode → related entities
  - Relationships to other episodes (same topic/workflow)

  2. Multi-level Relationships:
  Episode about "State Farm coverage confirmation call":
  ├─ ABOUT → State Farm Insurer entity
  ├─ ABOUT → BIClaim entity (specific claim)
  ├─ RELATES_TO_CASE → Amy-Mills case
  ├─ PART_OF_WORKFLOW → "insurance_setup" workflow
  └─ FOLLOWS → Previous episode about same coverage issue

  3. Relationship Schema Questions:

  Q1: How do we determine which entities an episode links to? For the nodes_as_episodes that currently exist, that will be manually set during ingestion because that's already in the information.Going forward, It'll be hybrid, so the user may explicitly state here, "Create an episode" or something, and they may state specifically what tag or so forth that it has. But it could also just be auto-detected because if the user and the LLM were just working on a medical record request for example, and the agent created a medical record request, and the user said, "Okay, document what we just did in a node or an episode", it'll be pretty obvious for an auto-detect to determine what episode.I could also envision a background agent that goes through all of the threads and perhaps creates summaries or looks for any important items that should be a node or an episode and that hasn't been created, and then creates those as kind of a background memory agent.But that might have to be a separate implementation, probably.
  - Option A: Parse episode text with LLM to extract mentioned entities
  - Option B: User explicitly tags entities when creating notes
  - Option C: Hybrid - auto-detect + allow manual tagging

  Q2: How do we link related episodes together? Probably some version of D, all of the above.When an episode is ingested, the workflow of the ingestion should be to determine first what case it's about and what nodes that exist it needs to be about. That should be easy from the context to say, "Okay, this is about the BI claim State Farm for Abby Sitgraves or whatever it is." And so the agent would go to that node in the graph and look and see if there are any related episodes about whatever the topic is. If it finds it, it would then read it, add the relationship. Another way, since we're doing embeddings, is it could run the node with the baseline or the episode with the baseline relationships for the case and for the insurance or medical provider or litigation or whatever nodes it's going to be obviously attached to. Then run the content through the semantic embeddings search. If it comes up with something that is sufficiently semantically similar, the agent can then look at those and then not automatically relate them but make the call to see if this is related.
  - Option A: Topic/theme classification (all "coverage" episodes link)
  - Option B: Workflow-based (episodes for same workflow step link)
  - Option C: Temporal chains (FOLLOWS relationship for sequential notes)
  - Option D: All of the above

  Q3: What embedding strategy? My gut reaction is C. So that we get more rich embeddings.Unless there's some drawback to it.
  - Option A: Embed episode content only
  - Option B: Embed episode + its relationships (richer context)
  - Option C: Embed episode + first-hop entities (includes claim details, provider names)

  Q4: How to handle episode → episode relationships? Well, in that scenario of those three episodes, on the very first one called "State Farm No Answer", the ingestion process would automatically add the case or the project and insurance. And let's say that was for bodily injury coverage. And so it would, and we already had State Farm in the graph, then that first one would be, hopefully, there's more to it than called "State Farm No Answer". Like you called State Farm to check coverage. "No answer" would be a much more appropriate node to create. And then that will be the first one. It will be linked to the project or case and insurance and you know the bi claim state farm, so it'll be linked to all of those.The second one would be to leave a voicemail for State Farm checking coverage. When the agent goes to ingest that node or create that node, they would first look at the State Farm node in the graph and should see the other episode that's attached to it. It should be able to see that and know to attach it to that one. If we're doing the semantic embeddings, then if it just did a search, that other node episode should almost certainly come up, and so that would be the first kind of pass of how it would determine it.And the same for the third. So it's really a two-prong approach for searching:
1. Just checking to see if there are any semantic search or the vector search comes back with any nodes or episodes that would relate. Then it would relate it to those.
2. If it doesn't, then the graph search would check.
  Episode 1: "Called State Farm - no answer"
  Episode 2: "Left voicemail for adjuster"
  Episode 3: "Adjuster called back - coverage confirmed"

  Should these auto-link? How?

  4. Search Use Cases:

  Semantic Search Examples:
  - "Why was coverage denied?" → Episodes about denial
  - "What happened with medical records?" → Episodes tagged to providers
  - "Coverage confirmation timeline" → Sequential episodes about coverage

  Graph Traversal Examples:
  - "Show all activity for State Farm claim" → Episode →ABOUT→ BIClaim
  - "What medical providers have outstanding records?" → Check episodes linked to each provider

  Technical Design Questions

  Schema Design:
  1. Episode entity properties?
    - content, timestamp, author, episode_type, case_name? I would also borrow from Graphiti and add the `valid_at` and `invalid_at` properties.So maybe the timestamp is just the "validAt" property. I'm not a hundred percent sure that the invalid at will ever be relevant for these types of nodes or episodes, but I don't think it hurts us by having that property even if it's always blank or null.
  2. Relationship types needed? That's a good start. I don't know. Probably when we do the initial ingestion, we may based upon the content of the 13,000 or so episodes that we're going to ingest, we may come up with some other ones.
    - RELATES_TO_CASE (default)
    - ABOUT_ENTITY (episode discusses entity)
    - FOLLOWS (sequential episodes)
    - PART_OF_WORKFLOW (episode is part of workflow execution)
    - Others?
  3. How to embed? I would use the OpenAI Text Embedding 3 Small for all the episode content, as well as the other nodes and relationships we have.And any change to a node should trigger a re-embedding.
    - OpenAI text-embedding-3-small for all episode content?
    - Store as vecf32 in FalkorDB?
    - Re-embed when relationships change?
  4. Existing entity embeddings? I think they should only because while they are structured, their relationships are variable.So if you have an embedding for a case and an embedding for a medical provider, then the relationship if it has an embedding would be a different place on the retreat on the semantic map. The notes that are created for that particular provider for that case would have relationships near the embeddings for the provider as it exists in that case, and that would make them distinct from embeddings about that provider in another case. So when we do semantic search, no episodes that relate to the providers and insurance companies and all that stuff that relates to that case would be farther away in the semantic retrieval, so there would be less noise to have to filter out.At least that's what I understand, or that's based upon my understanding of vector embeddings and semantic search.At the end of the day, I don't think we lose anything by adding the embeddings for those nodes.
    - Should Case, Provider, Insurance also have embeddings?
    - For what purpose? (they're structured, not semantic)

  Ingestion Strategy:
  1. From existing episode JSON files: We ingest from this JSON file. /Volumes/X10 Pro/Roscoe/json-files/memory-cards/episodes/notes_as_episodes.json And we probably need to do a bit of cleaning on it before we ingest.
    - 13,789 episodes already have case_name
    - Need to extract entity mentions
    - How to determine relationships?
  2. Going forward (new episodes): Well for a new episode, we create the episode with the tool that has the content, and then the case name and the related entities and episode type. And then do a semantic search. With that created episode as it exists so far to find more relationships, related episodes, and so forth.And then do a quick graph search since it will already know, for example, that it's related to the State Farm BI claim (again to use that example) to see if there are any episodes related to the content that it's getting ready to ingest.And then after it's found all of the episodes (or none) that it needs to relate to, and all the entities it needs to relate to (again, it could be more than one)Then it creates those relationships and generates an embedding, but only the final embedding gets generated after all of the relationships are created because I want the embedding to take into consideration all of those relationships.
    - Agent creates episode with create_episode() tool
    - Tool takes: content, case_name, related_entities[], episode_type
    - Auto-generates embedding
    - Creates relationships

  Open Questions for User:

  1. Should ALL episodes link to specific entities, or just some? The answer to that is yes. And that's part of, for past episodes, what we're going to have to clean up and get rid of so that we don't have those issues.And going forward, there's no reason to ever have an episode that just says "need to follow up" that just appears out of nowhere.
    - Example: General case note "Need to follow up" - what does it link to?
  2. Episode clustering - how granular?In your example, all coverage episodes for the particular insurance company would all link together.Regardless of if they're in the same thread or not, or sequential.
    - All "coverage" episodes link together?
    - Or just sequential episodes in same conversation thread?
  3. Should embeddings include relationship context?Absolutely!
    - Just episode text: "Called State Farm"
    - Or enriched: "Called State Farm (BIClaim #12345, Adjuster: John Smith)"
  4. Historical episodes from JSON - how to auto-link?We're going to use LLM to extract, and we're going to follow the guidance of how Graphiti does it and probably borrow from their prompting.
    - Run LLM to extract entity mentions?
    - Or simpler heuristics (text contains "State Farm" → link to State Farm entity)?
  5. Episode types - what categories?I don't know. What I'd like to do is work on cleaning the @notes_as_episodes.json   and then go over that because I think that is gonna give us a good idea of what episode types we're gonna want.
    - Call, Email, Fax, Meeting, Document, Internal Note?
    - Or more specific: Coverage_Call, Records_Request, Lien_Negotiation?

  Shall I continue exploring these questions or would you like to answer some to narrow down the design?