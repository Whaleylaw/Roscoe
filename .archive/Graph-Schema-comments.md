Graph-Schema-comments

LawFirm: Possibly need a deep research on all of the law firms we have contacts for and get a roster and then create attorney cards for all of them.
Settlement: There's no relationship for settlement.And in fact, it should probably be called negotiation.And then have relationships to whatever claim that it's negotiating.
Phase: These are wrong. Look in the Google Cloud bucket here for the phase names.whaley_law_firm/workflows
SubPhase: These are wrong. Look here in the Google Cloud bucket for the phase name. whaley_law_firm/workflows/phase_7_litigation/subphases
`WorkflowDef`, `WorkflowStep`, `WorkflowChecklist`, `WorkflowSkill`, `WorkflowTemplate`, `WorkflowTool`: Please add the properties of these so I can see.
Relationship
**`TREATED_BY`**: (MedicalProvider/Doctor)-[TREATED_BY]->(Client): This seems backwards.
**`HELD_BY`**: (Lien)-[HELD_BY]->(LienHolder or MedicalProvider): We don't need this.
**`HOLDS`**: (LienHolder)-[HOLDS]->(Lien): We don't need this. But there probably needs to be a relationship though to their bill, which is different than a lien.
**Insurance Relationships (7)**: Where is the relationship to the client? Like client has claim or insurance covers client, something.
**`HAS_MEMBER`**: (Community)-[HAS_MEMBER]->(Entity) - Graphiti communities: We aren't using Graphiti, but maybe we can recreate because I like the idea of the communities.

Document: This doesn't have any relationships.We have one specific type of document in pleading, should we have more? Like, have medical records type, medical bills type, medical record request or medical requests type, and then you could link those with a relationship to the provider.You could have:
- Insurance documents
- Letter of rep
- Acknowledgement of letter of rep
- Deck page
- Settlement offer
- CorrespondenceI

I don't know how granular to get in the entity and relationships, but there definitely needs to be something so that we can attach or link documents to the node in the graph that it corresponds to.We need that at a minimum, so that if I wanted to see if we send medical records requests or if we have received medical bills or medical records for a provider, you could go to the graph and go, no, we don't have any linked medical records.Or if you had a linked request, like we had sent out a second request for example. You could see that we have the second medical request, you could see the date it was sent, and then you could look in the graph and look at that provider to see if we had medical records received after that date.You could see date demand sent and, you know, if you were looking at a settlement negotiation with for an insurance company, and then you could see whether or not we have a response.