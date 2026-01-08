"""
Memory Card Schema Definitions

Pydantic models defining the structure for Entity Cards, Relationship Cards, 
and Episode Cards used in the Graphiti ingestion pipeline.
"""

from datetime import date, datetime
from typing import Optional, Literal, Any
from pydantic import BaseModel, Field


# =============================================================================
# Entity Card Schema
# =============================================================================

class EntityCard(BaseModel):
    """
    An Entity Card represents a single entity to be created in the graph.
    
    Entity types match the Pydantic models in graphiti_client.py:
    - Case, Client, Defendant
    - DirectoryEntry, Organization
    - PIPClaim, BIClaim, UMClaim, UIMClaim, WCClaim, MedPayClaim
    - Insurer, Adjuster
    - MedicalProvider, Lien, LienHolder
    - Attorney, LawFirm, Court, Pleading
    - Document, Expense, Settlement
    - Phase, Landmark, WorkflowDef, WorkflowStep, etc.
    """
    card_type: Literal["entity"] = "entity"
    entity_type: str = Field(..., description="Type from graphiti_client.py entity types")
    name: str = Field(..., description="Entity name (becomes the node name in graph)")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Entity-specific attributes")
    source_id: Optional[str] = Field(default=None, description="Original ID from source data")
    source_file: Optional[str] = Field(default=None, description="Source JSON file")


# =============================================================================
# Relationship Card Schema
# =============================================================================

class EntityRef(BaseModel):
    """Reference to an entity for relationship endpoints."""
    entity_type: str
    name: str


class RelationshipCard(BaseModel):
    """
    A Relationship Card represents an edge between two entities.
    
    Edge types match the Pydantic models in graphiti_client.py:
    - TreatingAt, TreatedBy, HasClaim, HasClient, HasLien, HasDefendant
    - InsuredBy, AssignedAdjuster, HandlesInsuranceClaim
    - PlaintiffIn, RepresentsClient, DefenseCounsel, FiledIn
    - WorksAt, InDirectory, PartOf, HeldBy
    - InPhase, LandmarkStatus, AchievedBy
    - And more...
    """
    card_type: Literal["relationship"] = "relationship"
    edge_type: str = Field(..., description="Relationship type from graphiti_client.py edge types")
    source: EntityRef = Field(..., description="Source entity")
    target: EntityRef = Field(..., description="Target entity")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Relationship-specific attributes")
    context: Optional[str] = Field(default=None, description="Case/project context for this relationship")


# =============================================================================
# Episode Card Schema
# =============================================================================

class EntityMention(BaseModel):
    """An entity mentioned in an episode."""
    type: str = Field(..., description="Entity type")
    name: str = Field(..., description="Entity name")
    role: Optional[str] = Field(default=None, description="Role in this context (e.g., 'caller', 'recipient')")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Additional attributes discovered")


class EdgeMention(BaseModel):
    """A relationship inferred from the episode."""
    type: str = Field(..., description="Edge type")
    from_entity: str = Field(..., alias="from", description="Source entity name")
    to_entity: str = Field(..., alias="to", description="Target entity name")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence score 0-1")


class EpisodeCard(BaseModel):
    """
    An Episode Card represents a summarized note/event ready for Graphiti ingestion.
    
    Episodes are temporal facts that connect entities and capture case history.
    """
    card_type: Literal["episode"] = "episode"
    case: str = Field(..., description="Case/project name")
    date: str = Field(..., description="Date of the episode (YYYY-MM-DD)")
    summary: str = Field(..., description="Natural language summary of what happened")
    
    # Entities and relationships mentioned
    entities: list[EntityMention] = Field(default_factory=list, description="Entities mentioned in this episode")
    edges: list[EdgeMention] = Field(default_factory=list, description="Relationships inferred from this episode")
    
    # Metadata
    author: Optional[str] = Field(default=None, description="Who created/authored this (staff name or 'ai')")
    author_type: Optional[str] = Field(default=None, description="staff, ai, integration, or unknown")
    note_source: Optional[str] = Field(default=None, description="voicemail, email, outbound_call, etc.")
    original_note_id: Optional[int] = Field(default=None, description="ID from source notes.json")
    
    class Config:
        populate_by_name = True  # Allow using 'from' alias


# =============================================================================
# Entity Type Definitions (for reference)
# =============================================================================

# Core case entities
CASE_ENTITY_TYPES = [
    "Case",
    "Client", 
    "Defendant",
]

# Directory/Organization entities
DIRECTORY_ENTITY_TYPES = [
    "DirectoryEntry",
    "Organization",
]

# Insurance entities
INSURANCE_ENTITY_TYPES = [
    "PIPClaim",
    "BIClaim",
    "UMClaim",
    "UIMClaim",
    "WCClaim",
    "MedPayClaim",
    "Insurer",
    "Adjuster",
]

# Medical entities
MEDICAL_ENTITY_TYPES = [
    "MedicalProvider",
    "Lien",
    "LienHolder",
]

# Legal entities
LEGAL_ENTITY_TYPES = [
    "LawFirm",
    "Attorney",
    "Court",
    "Pleading",
]

# Document/Financial entities
DOCUMENT_ENTITY_TYPES = [
    "Document",
    "Expense",
    "Settlement",
]

# Workflow entities
WORKFLOW_ENTITY_TYPES = [
    "Phase",
    "Landmark",
    "WorkflowDef",
    "WorkflowStep",
    "WorkflowChecklist",
    "WorkflowSkill",
    "WorkflowTemplate",
    "WorkflowTool",
]

ALL_ENTITY_TYPES = (
    CASE_ENTITY_TYPES + 
    DIRECTORY_ENTITY_TYPES + 
    INSURANCE_ENTITY_TYPES + 
    MEDICAL_ENTITY_TYPES + 
    LEGAL_ENTITY_TYPES + 
    DOCUMENT_ENTITY_TYPES +
    WORKFLOW_ENTITY_TYPES
)


# =============================================================================
# Edge Type Definitions (for reference)
# =============================================================================

# Case relationships
CASE_EDGE_TYPES = [
    "HasClient",
    "HasDefendant",
    "HasClaim",
    "HasLien",
    "HasLienFrom",
    "HasDocument",
    "HasExpense",
    "SettledWith",
    "InPhase",
    "LandmarkStatus",
]

# Treatment relationships
TREATMENT_EDGE_TYPES = [
    "TreatingAt",
    "TreatedBy",
]

# Insurance relationships
INSURANCE_EDGE_TYPES = [
    "InsuredBy",
    "AssignedAdjuster",
    "HandlesInsuranceClaim",
]

# Legal relationships
LEGAL_EDGE_TYPES = [
    "PlaintiffIn",
    "RepresentsClient",
    "RepresentedBy",
    "DefenseCounsel",
    "FiledIn",
]

# Organization relationships
ORG_EDGE_TYPES = [
    "WorksAt",
    "InDirectory",
    "HasContact",
    "PartOf",
]

# Lien relationships
LIEN_EDGE_TYPES = [
    "HeldBy",
    "Holds",
]

# Workflow relationships
WORKFLOW_EDGE_TYPES = [
    "BelongsToPhase",
    "HasLandmark",
    "HasSubLandmark",
    "AchievedBy",
    "Achieves",
    "DefinedInPhase",
    "HasWorkflow",
    "HasStep",
    "StepOf",
    "NextPhase",
    "CanSkipTo",
]

# Generic relationships
GENERIC_EDGE_TYPES = [
    "Mentions",
    "RelatesTo",
]

ALL_EDGE_TYPES = (
    CASE_EDGE_TYPES +
    TREATMENT_EDGE_TYPES +
    INSURANCE_EDGE_TYPES +
    LEGAL_EDGE_TYPES +
    ORG_EDGE_TYPES +
    LIEN_EDGE_TYPES +
    WORKFLOW_EDGE_TYPES +
    GENERIC_EDGE_TYPES
)


# =============================================================================
# Source File Mappings
# =============================================================================

# Which entity types come from which source files
SOURCE_TO_ENTITY_TYPES = {
    "overview.json": ["Case", "Client"],
    "directory.json": ["DirectoryEntry", "Organization", "Attorney", "LawFirm"],
    "insurance.json": ["PIPClaim", "BIClaim", "UMClaim", "UIMClaim", "WCClaim", "MedPayClaim", "Insurer", "Adjuster"],
    "medical-providers.json": ["MedicalProvider"],
    "liens.json": ["Lien", "LienHolder"],
    "litigation_contacts.json": ["Attorney", "Court"],
    "pleadings.json": ["Pleading"],
}


# =============================================================================
# Validation Helpers
# =============================================================================

def validate_entity_type(entity_type: str) -> bool:
    """Check if entity type is valid."""
    return entity_type in ALL_ENTITY_TYPES


def validate_edge_type(edge_type: str) -> bool:
    """Check if edge type is valid."""
    return edge_type in ALL_EDGE_TYPES


def create_entity_card(
    entity_type: str,
    name: str,
    attributes: dict = None,
    source_id: str = None,
    source_file: str = None,
) -> EntityCard:
    """Helper to create an EntityCard."""
    return EntityCard(
        entity_type=entity_type,
        name=name,
        attributes=attributes or {},
        source_id=source_id,
        source_file=source_file,
    )


def create_relationship_card(
    edge_type: str,
    source_type: str,
    source_name: str,
    target_type: str,
    target_name: str,
    attributes: dict = None,
    context: str = None,
) -> RelationshipCard:
    """Helper to create a RelationshipCard."""
    return RelationshipCard(
        edge_type=edge_type,
        source=EntityRef(entity_type=source_type, name=source_name),
        target=EntityRef(entity_type=target_type, name=target_name),
        attributes=attributes or {},
        context=context,
    )


def create_episode_card(
    case: str,
    date: str,
    summary: str,
    entities: list[dict] = None,
    edges: list[dict] = None,
    author: str = None,
    author_type: str = None,
    note_source: str = None,
    original_note_id: int = None,
) -> EpisodeCard:
    """Helper to create an EpisodeCard."""
    entity_mentions = [EntityMention(**e) for e in (entities or [])]
    edge_mentions = [EdgeMention(**e) for e in (edges or [])]
    
    return EpisodeCard(
        case=case,
        date=date,
        summary=summary,
        entities=entity_mentions,
        edges=edge_mentions,
        author=author,
        author_type=author_type,
        note_source=note_source,
        original_note_id=original_note_id,
    )


if __name__ == "__main__":
    # Test the schema
    print("Testing Memory Card Schema...")
    
    # Test EntityCard
    entity = create_entity_card(
        entity_type="MedicalProvider",
        name="Baptist Health Medical Group Neurology",
        attributes={"specialty": "neurology", "phone": "502-899-6800"},
        source_id="provider_123",
        source_file="medical-providers.json",
    )
    print(f"\nEntityCard:\n{entity.model_dump_json(indent=2)}")
    
    # Test RelationshipCard
    relationship = create_relationship_card(
        edge_type="TreatingAt",
        source_type="Client",
        source_name="Cynthia Gibson",
        target_type="MedicalProvider",
        target_name="Baptist Health Physical Therapy",
        attributes={"start_date": "2025-09-18"},
        context="Cynthia-Gibson-MVA-7-9-2025",
    )
    print(f"\nRelationshipCard:\n{relationship.model_dump_json(indent=2)}")
    
    # Test EpisodeCard
    episode = create_episode_card(
        case="Cynthia-Gibson-MVA-7-9-2025",
        date="2025-09-17",
        summary="Client Cynthia Gibson left voicemail for Attorney Aaron Whaley confirming PT appointment.",
        entities=[
            {"type": "Client", "name": "Cynthia Gibson"},
            {"type": "Attorney", "name": "Aaron Whaley"},
        ],
        edges=[
            {"type": "TreatingAt", "from": "Cynthia Gibson", "to": "Baptist Health PT"},
        ],
        author="Justin Chumley",
        author_type="staff",
        note_source="voicemail",
        original_note_id=21170,
    )
    print(f"\nEpisodeCard:\n{episode.model_dump_json(indent=2, by_alias=True)}")
    
    print("\n✅ All schema tests passed!")
