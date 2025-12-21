"""
Graphiti Knowledge Graph Client

Provides a singleton Graphiti client for the Roscoe platform, configured with:
- FalkorDB as the graph database backend
- Gemini 3 Flash as the LLM for entity/relationship extraction
- Custom entity types for legal case management
"""

import os
from typing import Optional
from datetime import date, datetime, timezone
from pydantic import BaseModel, Field

# Graphiti imports
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient
from graphiti_core.driver.falkordb_driver import FalkorDriver
from graphiti_core.nodes import EpisodeType

# =============================================================================
# SCOPE: This module is for UNSTRUCTURED data operations only
# =============================================================================
# USE THIS FOR:
# - Adding notes (add_case_episode)
# - Searching notes (search_case)
# - Generating case summaries (generate_case_summary)
#
# DO NOT USE FOR:
# - Creating structured entities (Case, Client, Claim) - use graph_manager.py
# - Workflow state management - use graph_manager.py
# - Deterministic relationships - use graph_manager.py
# =============================================================================

# =============================================================================
# Entity Type Definitions (Pydantic Models)
# =============================================================================

# --- Core Case Entities ---
# NOTE: 'name' is a protected attribute in Graphiti - it's added automatically.
# Do NOT include 'name' fields in these models.

class Case(BaseModel):
    """A personal injury case - immutable facts only. Name is auto-set by Graphiti (e.g., 'Christopher-Lanier-MVA-6-28-2025')."""
    case_type: Optional[str] = Field(default=None, description="Type: MVA, Premise, WC, Med-Mal, Dog-Bite, Slip-Fall")
    accident_date: Optional[date] = Field(default=None, description="Date of accident/incident")
    sol_date: Optional[date] = Field(default=None, description="Statute of limitations deadline")
    # Everything else (phase, client, totals, status) is relationships or computed from graph


class Client(BaseModel):
    """A client/plaintiff in a personal injury case. Name is auto-set by Graphiti."""
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    address: Optional[str] = Field(default=None, description="Mailing address")
    date_of_birth: Optional[date] = Field(default=None, description="Date of birth")


class Defendant(BaseModel):
    """The at-fault party in a case. Name is auto-set by Graphiti."""
    insurer: Optional[str] = Field(default=None, description="Defendant's insurance company")
    policy_number: Optional[str] = Field(default=None, description="Policy number for defendant's coverage")
    driver_license: Optional[str] = Field(default=None, description="Driver's license number")
    phone: Optional[str] = Field(default=None, description="Phone number")
    address: Optional[str] = Field(default=None, description="Address")
    project_name: Optional[str] = Field(default=None, description="Associated case name")


class Note(BaseModel):
    """A timestamped note attached to any entity (case, claim, provider, etc.). Name is auto-set by Graphiti."""
    note_date: Optional[date] = Field(default=None, description="Date of note (when event occurred)")
    content: Optional[str] = Field(default=None, description="Note content - narrative text")
    author: Optional[str] = Field(default=None, description="Author: staff name (e.g., 'Coleen Madayag', 'Justin Chumbley') or 'agent'")
    category: Optional[str] = Field(default=None, description="Type: insurance_note, medical_note, client_contact, status_change, litigation_note, general")
    project_name: Optional[str] = Field(default=None, description="Associated case name")
    source_file: Optional[str] = Field(default=None, description="Source document if note was imported from file")


class Organization(BaseModel):
    """A generic organization not fitting other specific types. Name is auto-set by Graphiti."""
    org_type: Optional[str] = Field(default=None, description="Type: law_firm, medical_practice, insurance_company, government, vendor, trucking, other")
    phone: Optional[str] = Field(default=None, description="Main phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Address")


# --- Insurance Entities ---

class Insurer(BaseModel):
    """An insurance company. Name is auto-set by Graphiti (e.g., State Farm, Progressive)."""
    phone: Optional[str] = Field(default=None, description="Main phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Mailing address")


class Adjuster(BaseModel):
    """An insurance adjuster handling a claim. Name is auto-set by Graphiti."""
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")


class PIPClaim(BaseModel):
    """A Personal Injury Protection (PIP) insurance claim - first-party no-fault coverage."""
    claim_number: Optional[str] = Field(default=None, description="PIP claim number")
    insurer_name: Optional[str] = Field(default=None, description="Insurance company name")
    adjuster_name: Optional[str] = Field(default=None, description="Assigned adjuster name")
    policy_limit: Optional[float] = Field(default=None, description="PIP policy limit amount")
    amount_paid: Optional[float] = Field(default=None, description="Amount paid out so far")
    exhausted: Optional[bool] = Field(default=None, description="Whether PIP benefits are exhausted")
    lor_sent_date: Optional[date] = Field(default=None, description="Date letter of representation was sent")
    coverage_confirmation: Optional[str] = Field(default=None, description="Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'")
    project_name: Optional[str] = Field(default=None, description="Associated case name")


class BIClaim(BaseModel):
    """A Bodily Injury (BI) liability insurance claim - third-party claim against at-fault driver."""
    claim_number: Optional[str] = Field(default=None, description="BI claim number")
    insurer_name: Optional[str] = Field(default=None, description="Insurance company name")
    adjuster_name: Optional[str] = Field(default=None, description="Assigned adjuster name")
    policy_limit: Optional[float] = Field(default=None, description="BI policy limit amount")
    demand_amount: Optional[float] = Field(default=None, description="Amount demanded")
    demand_sent_date: Optional[date] = Field(default=None, description="Date demand was sent")
    current_offer: Optional[float] = Field(default=None, description="Current settlement offer")
    settlement_amount: Optional[float] = Field(default=None, description="Final settlement amount")
    settlement_date: Optional[date] = Field(default=None, description="Date of settlement")
    lor_sent_date: Optional[date] = Field(default=None, description="Date letter of representation was sent")
    coverage_confirmation: Optional[str] = Field(default=None, description="Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'")
    is_active_negotiation: Optional[bool] = Field(default=None, description="Whether actively negotiating settlement")
    project_name: Optional[str] = Field(default=None, description="Associated case name")


class UMClaim(BaseModel):
    """An Uninsured Motorist (UM) insurance claim - when at-fault driver has no insurance."""
    claim_number: Optional[str] = Field(default=None, description="UM claim number")
    insurer_name: Optional[str] = Field(default=None, description="Client's insurance company name")
    adjuster_name: Optional[str] = Field(default=None, description="Assigned adjuster name")
    policy_limit: Optional[float] = Field(default=None, description="UM policy limit amount")
    demand_amount: Optional[float] = Field(default=None, description="Amount demanded")
    demand_sent_date: Optional[date] = Field(default=None, description="Date demand was sent")
    current_offer: Optional[float] = Field(default=None, description="Current settlement offer")
    settlement_amount: Optional[float] = Field(default=None, description="Final settlement amount")
    settlement_date: Optional[date] = Field(default=None, description="Date of settlement")
    coverage_confirmation: Optional[str] = Field(default=None, description="Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'")
    is_active_negotiation: Optional[bool] = Field(default=None, description="Whether actively negotiating settlement")
    project_name: Optional[str] = Field(default=None, description="Associated case name")


class UIMClaim(BaseModel):
    """An Underinsured Motorist (UIM) insurance claim - when at-fault driver's coverage is insufficient."""
    claim_number: Optional[str] = Field(default=None, description="UIM claim number")
    insurer_name: Optional[str] = Field(default=None, description="Client's insurance company name")
    adjuster_name: Optional[str] = Field(default=None, description="Assigned adjuster name")
    policy_limit: Optional[float] = Field(default=None, description="UIM policy limit amount")
    bi_settlement: Optional[float] = Field(default=None, description="Amount recovered from BI claim")
    demand_amount: Optional[float] = Field(default=None, description="Amount demanded")
    demand_sent_date: Optional[date] = Field(default=None, description="Date demand was sent")
    current_offer: Optional[float] = Field(default=None, description="Current settlement offer")
    settlement_amount: Optional[float] = Field(default=None, description="Final settlement amount")
    settlement_date: Optional[date] = Field(default=None, description="Date of settlement")
    coverage_confirmation: Optional[str] = Field(default=None, description="Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'")
    is_active_negotiation: Optional[bool] = Field(default=None, description="Whether actively negotiating settlement")
    project_name: Optional[str] = Field(default=None, description="Associated case name")


class WCClaim(BaseModel):
    """A Workers Compensation (WC) insurance claim - workplace injury coverage."""
    claim_number: Optional[str] = Field(default=None, description="WC claim number")
    insurer_name: Optional[str] = Field(default=None, description="Workers comp insurance company name")
    adjuster_name: Optional[str] = Field(default=None, description="Assigned adjuster name")
    employer_name: Optional[str] = Field(default=None, description="Employer name")
    injury_date: Optional[date] = Field(default=None, description="Date of workplace injury")
    ttd_rate: Optional[float] = Field(default=None, description="Temporary Total Disability weekly rate")
    medical_paid: Optional[float] = Field(default=None, description="Medical expenses paid by WC")
    settlement_amount: Optional[float] = Field(default=None, description="Final settlement amount")
    settlement_date: Optional[date] = Field(default=None, description="Date of settlement")
    coverage_confirmation: Optional[str] = Field(default=None, description="Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'")
    is_active_negotiation: Optional[bool] = Field(default=None, description="Whether actively negotiating settlement")
    project_name: Optional[str] = Field(default=None, description="Associated case name")


class MedPayClaim(BaseModel):
    """A Medical Payments (MedPay) insurance claim - first-party medical expense coverage."""
    claim_number: Optional[str] = Field(default=None, description="MedPay claim number")
    insurer_name: Optional[str] = Field(default=None, description="Insurance company name")
    adjuster_name: Optional[str] = Field(default=None, description="Assigned adjuster name")
    policy_limit: Optional[float] = Field(default=None, description="MedPay policy limit amount")
    amount_paid: Optional[float] = Field(default=None, description="Amount paid out so far")
    exhausted: Optional[bool] = Field(default=None, description="Whether MedPay benefits are exhausted")
    coverage_confirmation: Optional[str] = Field(default=None, description="Coverage status: 'Coverage Confirmed', 'Coverage Pending', 'Coverage Denied'")
    project_name: Optional[str] = Field(default=None, description="Associated case name")


# --- Medical Entities ---

class MedicalProvider(BaseModel):
    """A medical provider treating a client. Name is auto-set by Graphiti."""
    specialty: Optional[str] = Field(default=None, description="Medical specialty: chiropractic, orthopedic, PT, pain management, primary care, ER, imaging, etc.")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Address")


class Lien(BaseModel):
    """A lien on a specific case. Name is auto-set by Graphiti. Lienholder identified via HELD_BY relationship."""
    amount: Optional[float] = Field(default=None, description="Original lien amount")
    account_number: Optional[str] = Field(default=None, description="Account or reference number")
    project_name: Optional[str] = Field(default=None, description="Associated case name")
    date_notice_received: Optional[date] = Field(default=None, description="When lien notice was received")
    date_lien_paid: Optional[date] = Field(default=None, description="When lien was satisfied")
    reduction_amount: Optional[float] = Field(default=None, description="Negotiated reduction amount")
    # lien_type removed - that's on LienHolder entity (via HELD_BY relationship)
    # lienholder_name removed - that's the HELD_BY relationship target


class LienHolder(BaseModel):
    """An entity holding a lien (hospital, ERISA plan, Medicare, collection agency, etc.). Name is auto-set by Graphiti."""
    lien_type: Optional[str] = Field(default=None, description="Primary lien type: medical, ERISA, Medicare, Medicaid, child_support, collection")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Address")


# --- Document Entity ---

class Document(BaseModel):
    """A document in the case file system. Name is auto-set by Graphiti (filename)."""
    path: Optional[str] = Field(default=None, description="Path relative to case folder")
    document_type: Optional[str] = Field(default=None, description="Type: letter_of_rep, demand_package, medical_records, medical_bills, records_request, hipaa, retainer, pleading, discovery, correspondence, evidence")
    file_type: Optional[str] = Field(default=None, description="File extension: pdf, docx, jpg, etc.")
    description: Optional[str] = Field(default=None, description="Brief description of document contents")


# --- Legal/Litigation Entities ---

class LawFirm(BaseModel):
    """A law firm. Name is auto-set by Graphiti."""
    phone: Optional[str] = Field(default=None, description="Main phone number")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Address")


class Attorney(BaseModel):
    """An attorney on a case. Name is auto-set by Graphiti."""
    role: Optional[str] = Field(default=None, description="Role: plaintiff_counsel, defense_counsel, co_counsel, referring_attorney")
    bar_number: Optional[str] = Field(default=None, description="State bar number")
    firm_name: Optional[str] = Field(default=None, description="Law firm name")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")


class Court(BaseModel):
    """A court where a case is filed. Name is auto-set by Graphiti."""
    county: Optional[str] = Field(default=None, description="County")
    state: Optional[str] = Field(default=None, description="State")
    case_number: Optional[str] = Field(default=None, description="Court case number")
    division: Optional[str] = Field(default=None, description="Division: civil, circuit, district, etc.")
    phone: Optional[str] = Field(default=None, description="Court clerk phone number")
    email: Optional[str] = Field(default=None, description="Court clerk email")
    address: Optional[str] = Field(default=None, description="Court mailing address")


class Pleading(BaseModel):
    """A litigation pleading or court filing. Name is auto-set by Graphiti (title)."""
    pleading_type: Optional[str] = Field(default=None, description="Type: complaint, answer, motion, discovery_request, discovery_response, subpoena, order, judgment")
    filed_date: Optional[date] = Field(default=None, description="Date filed")
    due_date: Optional[date] = Field(default=None, description="Response due date if applicable")
    filed_by: Optional[str] = Field(default=None, description="Who filed it: plaintiff, defendant")


# --- Vendor Entities ---

class Vendor(BaseModel):
    """A vendor/service provider used in case management. Name is auto-set by Graphiti."""
    vendor_type: Optional[str] = Field(default=None, description="Type: towing, court_reporting, investigation, moving, records_retrieval, process_server, expert_witness, mediation, litigation_funding, medical_equipment, claims_services, legal_software, other")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Address")


# --- Financial Entities ---

class Expense(BaseModel):
    """A case expense. Name is auto-set by Graphiti (description)."""
    amount: Optional[float] = Field(default=None, description="Amount in dollars")
    expense_date: Optional[date] = Field(default=None, description="Date of expense")
    category: Optional[str] = Field(default=None, description="Category: filing_fee, service_fee, medical_records, expert, travel, other")
    vendor: Optional[str] = Field(default=None, description="Vendor/payee name")


class Settlement(BaseModel):
    """Settlement details for a resolved case. Name is auto-set by Graphiti."""
    gross_amount: Optional[float] = Field(default=None, description="Gross settlement amount")
    attorney_fee: Optional[float] = Field(default=None, description="Attorney fee amount")
    expenses_total: Optional[float] = Field(default=None, description="Total case expenses")
    liens_total: Optional[float] = Field(default=None, description="Total liens paid")
    net_to_client: Optional[float] = Field(default=None, description="Net amount to client")
    settlement_date: Optional[date] = Field(default=None, description="Date of settlement")


# =============================================================================
# Workflow Definition Entities
# =============================================================================
# These entities represent the workflow structure itself, not case data.
# They are ingested once from workflow_engine/ and workflows/ folders.
# NOTE: 'name' is a protected Graphiti attribute - do NOT include it.

class Phase(BaseModel):
    """A case lifecycle phase (e.g., file_setup, treatment, negotiation). Name is auto-set."""
    display_name: Optional[str] = Field(default=None, description="Human-readable phase name")
    description: Optional[str] = Field(default=None, description="Description of the phase")
    order: Optional[int] = Field(default=None, description="Phase order in lifecycle (1-12)")
    track: Optional[str] = Field(default=None, description="Track: pre_litigation, litigation, terminal")
    next_phase: Optional[str] = Field(default=None, description="Default next phase name")


class Landmark(BaseModel):
    """A checkpoint within a phase that must be verified before advancing. Name is auto-set."""
    # Basic info
    landmark_id: Optional[str] = Field(default=None, description="Unique landmark identifier (e.g., 'retainer_signed')")
    display_name: Optional[str] = Field(default=None, description="Human-readable name")
    phase: Optional[str] = Field(default=None, description="Phase this landmark belongs to")
    description: Optional[str] = Field(default=None, description="What this landmark verifies")
    landmark_type: Optional[str] = Field(default=None, description="Type: document, entity, communication, verification")

    # Blocking behavior
    is_hard_blocker: Optional[bool] = Field(default=None, description="If true, MUST complete before advancing phase")
    can_override: Optional[bool] = Field(default=None, description="If true, user can manually override if stuck")

    # AUTO-VERIFICATION
    verification_method: Optional[str] = Field(default=None, description="How to verify: 'graph_query', 'manual', 'hybrid'")
    verification_entities: Optional[str] = Field(default=None, description="JSON list of entity types that satisfy this landmark")
    verification_relationships: Optional[str] = Field(default=None, description="JSON list of required relationships")
    verification_query: Optional[str] = Field(default=None, description="Cypher query to verify completion (must return 'verified' boolean)")
    auto_verify: Optional[bool] = Field(default=None, description="If true, system auto-updates status when verification query passes")

    # SUB-STEPS
    sub_steps: Optional[str] = Field(default=None, description="JSON dict of sub-steps {step_name: description}")
    parent_landmark: Optional[str] = Field(default=None, description="Parent landmark ID for sub-landmarks")

    # Legacy fields (keep for compatibility)
    mandatory: Optional[bool] = Field(default=None, description="DEPRECATED: Use is_hard_blocker instead")
    verification_fields: Optional[str] = Field(default=None, description="DEPRECATED: Use verification_query instead")


class WorkflowDef(BaseModel):
    """A workflow definition within a phase. Name is auto-set."""
    display_name: Optional[str] = Field(default=None, description="Human-readable workflow name")
    phase: Optional[str] = Field(default=None, description="Phase this workflow belongs to")
    description: Optional[str] = Field(default=None, description="What this workflow accomplishes")
    trigger: Optional[str] = Field(default=None, description="When this workflow is triggered")
    prerequisites: Optional[str] = Field(default=None, description="What must be complete before starting")
    instructions_path: Optional[str] = Field(default=None, description="Path to workflow.md with detailed instructions")


class WorkflowStep(BaseModel):
    """A step within a workflow. Name is auto-set."""
    step_id: Optional[str] = Field(default=None, description="Step identifier within workflow")
    workflow: Optional[str] = Field(default=None, description="Parent workflow name")
    description: Optional[str] = Field(default=None, description="What this step does")
    owner: Optional[str] = Field(default=None, description="Who executes: 'agent' or 'user'")
    can_automate: Optional[bool] = Field(default=None, description="Whether agent can execute without user")
    prompt_user: Optional[str] = Field(default=None, description="Question to ask user if needed")
    completion_check: Optional[str] = Field(default=None, description="Condition to verify step completion")
    order: Optional[int] = Field(default=None, description="Step order within workflow")


class WorkflowChecklist(BaseModel):
    """A procedural checklist for completing a task. Name is auto-set."""
    path: Optional[str] = Field(default=None, description="Path to checklist file")
    when_to_use: Optional[str] = Field(default=None, description="When to use this checklist")
    related_workflow: Optional[str] = Field(default=None, description="Associated workflow name")


class WorkflowSkill(BaseModel):
    """An agent skill that can be used in workflows. Name is auto-set."""
    path: Optional[str] = Field(default=None, description="Path to skill.md file")
    description: Optional[str] = Field(default=None, description="What this skill does")
    capabilities: Optional[str] = Field(default=None, description="List of capabilities")
    agent_ready: Optional[bool] = Field(default=None, description="Whether skill is ready for agent use")
    quality_score: Optional[float] = Field(default=None, description="Quality score 0-5")


class WorkflowTemplate(BaseModel):
    """A document template used in workflows. Name is auto-set."""
    path: Optional[str] = Field(default=None, description="Path to template file")
    purpose: Optional[str] = Field(default=None, description="What this template is for")
    file_type: Optional[str] = Field(default=None, description="File type: docx, pdf, md")
    placeholders: Optional[str] = Field(default=None, description="Placeholder fields in template")


class WorkflowTool(BaseModel):
    """A Python tool used in workflows. Name is auto-set."""
    path: Optional[str] = Field(default=None, description="Path to Python script")
    purpose: Optional[str] = Field(default=None, description="What this tool does")


# =============================================================================
# All Entity Types for Graphiti
# =============================================================================

ENTITY_TYPES = [
    # Core case entities
    Case,
    Client,
    Defendant,       # At-fault party
    Note,            # Timestamped notes attached to any entity
    Organization,    # Generic organizations
    # Insurance claim types (each is distinct)
    PIPClaim,        # Personal Injury Protection - first-party no-fault
    BIClaim,         # Bodily Injury - third-party liability
    UMClaim,         # Uninsured Motorist
    UIMClaim,        # Underinsured Motorist
    WCClaim,         # Workers Compensation
    MedPayClaim,     # Medical Payments coverage
    Insurer,         # Insurance company
    Adjuster,        # Insurance adjuster
    # Medical entities
    MedicalProvider,
    Lien,
    LienHolder,      # Entity holding a lien
    # Document tracking
    Document,
    # Legal/litigation entities
    LawFirm,
    Attorney,
    Court,
    Pleading,
    # Vendor types
    Vendor,
    # Financial
    Expense,
    Settlement,
    # Workflow definition entities (structural, not case data)
    Phase,
    Landmark,
    WorkflowDef,
    WorkflowStep,
    WorkflowChecklist,
    WorkflowSkill,
    WorkflowTemplate,
    WorkflowTool,
]

# =============================================================================
# Entity and Edge Type Dictionaries for Graphiti add_episode
# =============================================================================

# Convert ENTITY_TYPES list to dictionary for Graphiti
ENTITY_TYPES_DICT = {cls.__name__: cls for cls in ENTITY_TYPES}


# Edge types for relationships (Pydantic models)
class TreatingAt(BaseModel):
    """Client treating at a medical provider."""
    start_date: Optional[date] = Field(default=None, description="First treatment date")
    end_date: Optional[date] = Field(default=None, description="Last treatment date or ongoing")
    treatment_type: Optional[str] = Field(default=None, description="Type: chiropractic, PT, orthopedic, etc.")


class TreatedBy(BaseModel):
    """Medical provider treated a client (reverse of TreatingAt)."""
    start_date: Optional[date] = Field(default=None, description="First treatment date")
    end_date: Optional[date] = Field(default=None, description="Last treatment date or ongoing")
    treatment_type: Optional[str] = Field(default=None, description="Type: chiropractic, PT, orthopedic, etc.")


class HasClaim(BaseModel):
    """Case has an insurance claim."""
    claim_number: Optional[str] = Field(default=None, description="Claim number")
    claim_type: Optional[str] = Field(default=None, description="Type: PIP, BI, UM, UIM, WC, MedPay")
    status: Optional[str] = Field(default=None, description="Claim status")


class HasClient(BaseModel):
    """Case has a client/plaintiff."""
    role: Optional[str] = Field(default=None, description="Client role: primary, co-plaintiff")
    engagement_date: Optional[date] = Field(default=None, description="Date client engaged")


class HasLien(BaseModel):
    """Case has a medical lien."""
    amount: Optional[float] = Field(default=None, description="Lien amount")
    status: Optional[str] = Field(default=None, description="Lien status: pending, negotiated, satisfied")


class HasDefendant(BaseModel):
    """Case has a defendant (at-fault party)."""
    role: Optional[str] = Field(default=None, description="Defendant role: primary, co-defendant")


class RepresentsClient(BaseModel):
    """Attorney represents client in case."""
    engagement_date: Optional[date] = Field(default=None, description="Date representation began")
    fee_agreement: Optional[str] = Field(default=None, description="Fee agreement type: contingency, hourly")


class FiledIn(BaseModel):
    """Case filed in court."""
    filing_date: Optional[date] = Field(default=None, description="Date case was filed")
    case_number: Optional[str] = Field(default=None, description="Court case number")


class WorksAt(BaseModel):
    """Person works at organization."""
    position: Optional[str] = Field(default=None, description="Job title or position")


class HandlesInsuranceClaim(BaseModel):
    """Adjuster handles insurance claim."""
    assigned_date: Optional[date] = Field(default=None, description="Date assigned to claim")


class InPhase(BaseModel):
    """Case is in a workflow phase."""
    entered_at: Optional[datetime] = Field(default=None, description="When case entered this phase")
    previous_phase: Optional[str] = Field(default=None, description="Previous phase name")


class LandmarkStatus(BaseModel):
    """Case has a landmark with a status."""
    status: Optional[str] = Field(default=None, description="Status: complete, incomplete, in_progress, not_applicable")
    completed_at: Optional[datetime] = Field(default=None, description="When landmark was completed")
    notes: Optional[str] = Field(default=None, description="Notes about completion")


class AchievedBy(BaseModel):
    """Landmark is achieved by completing a workflow."""
    pass  # No additional attributes needed


class PartOf(BaseModel):
    """Entity is part of a larger entity (organizational hierarchy)."""
    relationship_type: Optional[str] = Field(default=None, description="Type: subsidiary, department, branch, division")


class HeldBy(BaseModel):
    """Lien is held by a lien holder."""
    pass  # Attributes on the Lien entity itself


class Holds(BaseModel):
    """Lien holder holds a lien (reverse of HeldBy)."""
    pass


class HasLienFrom(BaseModel):
    """Case has a lien from a lien holder."""
    amount: Optional[float] = Field(default=None, description="Lien amount")
    status: Optional[str] = Field(default=None, description="Lien status")


class AssignedAdjuster(BaseModel):
    """Claim has an assigned adjuster."""
    assigned_date: Optional[date] = Field(default=None, description="Date assigned")


class InsuredBy(BaseModel):
    """Claim is insured by an insurance company."""
    policy_number: Optional[str] = Field(default=None, description="Policy number")


class PlaintiffIn(BaseModel):
    """Client is a plaintiff in a case."""
    role: Optional[str] = Field(default=None, description="Role: primary, co-plaintiff")


class DefenseCounsel(BaseModel):
    """Attorney is defense counsel for a case."""
    firm_name: Optional[str] = Field(default=None, description="Defense firm name")


class RepresentedBy(BaseModel):
    """Case is represented by an attorney."""
    role: Optional[str] = Field(default=None, description="Role: plaintiff_counsel, co_counsel")


class HasDocument(BaseModel):
    """Case has a document."""
    document_type: Optional[str] = Field(default=None, description="Type of document")
    added_date: Optional[date] = Field(default=None, description="Date added to case")


class HasExpense(BaseModel):
    """Case has an expense."""
    category: Optional[str] = Field(default=None, description="Expense category")


class SettledWith(BaseModel):
    """Case settled with settlement details."""
    settlement_date: Optional[date] = Field(default=None, description="Date of settlement")


class Achieves(BaseModel):
    """Workflow achieves a landmark (reverse of AchievedBy)."""
    pass


class HasWorkflow(BaseModel):
    """Phase has a workflow."""
    order: Optional[int] = Field(default=None, description="Workflow order in phase")


class HasStep(BaseModel):
    """Workflow has a step."""
    order: Optional[int] = Field(default=None, description="Step order in workflow")


class BelongsToPhase(BaseModel):
    """Landmark belongs to a phase."""
    order: Optional[int] = Field(default=None, description="Landmark order in phase")


class HasLandmark(BaseModel):
    """Phase has a landmark."""
    order: Optional[int] = Field(default=None, description="Landmark order")


class HasSubLandmark(BaseModel):
    """Landmark has a sub-landmark."""
    order: Optional[int] = Field(default=None, description="Sub-landmark order")


class NextPhase(BaseModel):
    """Phase leads to next phase."""
    is_default: Optional[bool] = Field(default=True, description="Is default progression")


class CanSkipTo(BaseModel):
    """Phase can skip to another phase (e.g., settlement)."""
    condition: Optional[str] = Field(default=None, description="Condition for skip")


class StepOf(BaseModel):
    """Step belongs to a workflow."""
    order: Optional[int] = Field(default=None, description="Step order")


class DefinedInPhase(BaseModel):
    """Workflow is defined in a phase."""
    pass


class Mentions(BaseModel):
    """Episode or entity mentions another entity (Graphiti built-in)."""
    context: Optional[str] = Field(default=None, description="Context of mention")


class RelatesTo(BaseModel):
    """Generic relationship between entities (fallback)."""
    relationship_type: Optional[str] = Field(default=None, description="Type of relationship")


class HasNote(BaseModel):
    """Entity has an associated note."""
    added_at: Optional[datetime] = Field(default=None, description="When note was added to system")


class NotedOn(BaseModel):
    """Note is about an entity (reverse of HasNote)."""
    relevance: Optional[str] = Field(default=None, description="How note relates to entity")


EDGE_TYPES_DICT = {
    # Core case relationships
    "TreatingAt": TreatingAt,
    "TreatedBy": TreatedBy,
    "HasClaim": HasClaim,
    "HasClient": HasClient,
    "HasLien": HasLien,
    "HasLienFrom": HasLienFrom,
    "HasDefendant": HasDefendant,
    "HasDocument": HasDocument,
    "HasExpense": HasExpense,
    "SettledWith": SettledWith,
    # Insurance relationships
    "InsuredBy": InsuredBy,
    "AssignedAdjuster": AssignedAdjuster,
    "HandlesInsuranceClaim": HandlesInsuranceClaim,
    # Legal relationships
    "PlaintiffIn": PlaintiffIn,
    "RepresentsClient": RepresentsClient,
    "RepresentedBy": RepresentedBy,
    "DefenseCounsel": DefenseCounsel,
    "FiledIn": FiledIn,
    # Organization relationships
    "WorksAt": WorksAt,
    "PartOf": PartOf,
    # Lien relationships
    "HeldBy": HeldBy,
    "Holds": Holds,
    # Workflow state relationships
    "InPhase": InPhase,
    "LandmarkStatus": LandmarkStatus,
    # Workflow structure relationships
    "BelongsToPhase": BelongsToPhase,
    "HasLandmark": HasLandmark,
    "HasSubLandmark": HasSubLandmark,
    "AchievedBy": AchievedBy,
    "Achieves": Achieves,
    "DefinedInPhase": DefinedInPhase,
    "HasWorkflow": HasWorkflow,
    "HasStep": HasStep,
    "StepOf": StepOf,
    "NextPhase": NextPhase,
    "CanSkipTo": CanSkipTo,
    # Note relationships
    "HasNote": HasNote,
    "NotedOn": NotedOn,
    # Generic relationships
    "Mentions": Mentions,
    "RelatesTo": RelatesTo,
}

# Edge type map: which edge types are valid between which entity types
EDGE_TYPE_MAP = {
    # =========================================================================
    # Case relationships (Case as source)
    # =========================================================================
    ("Case", "Client"): ["HasClient"],
    ("Case", "Defendant"): ["HasDefendant"],
    ("Case", "Phase"): ["InPhase"],
    ("Case", "Landmark"): ["LandmarkStatus"],
    ("Case", "MedicalProvider"): ["TreatingAt"],
    ("Case", "Lien"): ["HasLien"],
    ("Case", "Court"): ["FiledIn"],
    ("Case", "Document"): ["HasDocument"],
    ("Case", "Expense"): ["HasExpense"],
    ("Case", "Settlement"): ["SettledWith"],
    # Case to insurance claims
    ("Case", "PIPClaim"): ["HasClaim"],
    ("Case", "BIClaim"): ["HasClaim"],
    ("Case", "UMClaim"): ["HasClaim"],
    ("Case", "UIMClaim"): ["HasClaim"],
    ("Case", "WCClaim"): ["HasClaim"],
    ("Case", "MedPayClaim"): ["HasClaim"],
    
    # =========================================================================
    # Client relationships (bidirectional where needed)
    # =========================================================================
    ("Client", "Case"): ["PlaintiffIn"],
    ("Client", "MedicalProvider"): ["TreatingAt"],
    
    # =========================================================================
    # Medical Provider relationships (bidirectional)
    # =========================================================================
    ("MedicalProvider", "Client"): ["TreatedBy"],
    ("MedicalProvider", "Case"): ["TreatedBy"],
    
    # =========================================================================
    # Insurance claim relationships
    # =========================================================================
    ("PIPClaim", "Insurer"): ["InsuredBy"],
    ("BIClaim", "Insurer"): ["InsuredBy"],
    ("UMClaim", "Insurer"): ["InsuredBy"],
    ("UIMClaim", "Insurer"): ["InsuredBy"],
    ("WCClaim", "Insurer"): ["InsuredBy"],
    ("MedPayClaim", "Insurer"): ["InsuredBy"],
    # Insurer to claims (bidirectional)
    ("Insurer", "PIPClaim"): ["HasClaim"],
    ("Insurer", "BIClaim"): ["HasClaim"],
    ("Insurer", "UMClaim"): ["HasClaim"],
    ("Insurer", "UIMClaim"): ["HasClaim"],
    ("Insurer", "WCClaim"): ["HasClaim"],
    ("Insurer", "MedPayClaim"): ["HasClaim"],
    
    # =========================================================================
    # Adjuster relationships
    # =========================================================================
    ("Adjuster", "Insurer"): ["WorksAt"],
    ("Adjuster", "PIPClaim"): ["HandlesInsuranceClaim"],
    ("Adjuster", "BIClaim"): ["HandlesInsuranceClaim"],
    ("Adjuster", "UMClaim"): ["HandlesInsuranceClaim"],
    ("Adjuster", "UIMClaim"): ["HandlesInsuranceClaim"],
    ("Adjuster", "WCClaim"): ["HandlesInsuranceClaim"],
    ("Adjuster", "MedPayClaim"): ["HandlesInsuranceClaim"],
    # Claims to adjuster (bidirectional)
    ("PIPClaim", "Adjuster"): ["AssignedAdjuster"],
    ("BIClaim", "Adjuster"): ["AssignedAdjuster"],
    ("UMClaim", "Adjuster"): ["AssignedAdjuster"],
    ("UIMClaim", "Adjuster"): ["AssignedAdjuster"],
    
    # =========================================================================
    # Lien relationships
    # =========================================================================
    ("Lien", "LienHolder"): ["HeldBy"],
    ("Lien", "MedicalProvider"): ["HeldBy"],
    ("LienHolder", "Lien"): ["Holds"],
    ("Case", "LienHolder"): ["HasLienFrom"],
    
    # =========================================================================
    # Legal/litigation relationships
    # =========================================================================
    ("Attorney", "Case"): ["RepresentsClient"],
    ("Attorney", "LawFirm"): ["WorksAt"],
    ("Case", "Attorney"): ["DefenseCounsel", "RepresentedBy"],
    ("Pleading", "Case"): ["FiledFor"],
    ("Pleading", "Court"): ["FiledIn"],
    
    # =========================================================================
    # Organization relationships
    # =========================================================================
    ("Organization", "Organization"): ["PartOf"],  # Hierarchies
    ("MedicalProvider", "Organization"): ["PartOf"],  # Provider belongs to health system
    ("LawFirm", "Organization"): ["PartOf"],
    
    # =========================================================================
    # Workflow relationships (structural)
    # =========================================================================
    ("Phase", "Landmark"): ["HasLandmark"],
    ("Landmark", "Phase"): ["BelongsToPhase"],
    ("Landmark", "WorkflowDef"): ["AchievedBy"],
    ("WorkflowDef", "Landmark"): ["Achieves"],
    ("WorkflowDef", "Phase"): ["DefinedInPhase"],
    ("Phase", "WorkflowDef"): ["HasWorkflow"],
    ("WorkflowStep", "WorkflowDef"): ["StepOf"],
    ("WorkflowDef", "WorkflowStep"): ["HasStep"],
    ("Landmark", "Landmark"): ["HasSubLandmark"],
    ("Phase", "Phase"): ["NextPhase", "CanSkipTo"],

    # =========================================================================
    # Note relationships (Notes can attach to any entity)
    # =========================================================================
    ("Case", "Note"): ["HasNote"],
    ("Client", "Note"): ["HasNote"],
    ("PIPClaim", "Note"): ["HasNote"],
    ("BIClaim", "Note"): ["HasNote"],
    ("UMClaim", "Note"): ["HasNote"],
    ("UIMClaim", "Note"): ["HasNote"],
    ("WCClaim", "Note"): ["HasNote"],
    ("MedPayClaim", "Note"): ["HasNote"],
    ("MedicalProvider", "Note"): ["HasNote"],
    ("Insurer", "Note"): ["HasNote"],
    ("Adjuster", "Note"): ["HasNote"],
    ("Lien", "Note"): ["HasNote"],
    ("LienHolder", "Note"): ["HasNote"],
    ("Defendant", "Note"): ["HasNote"],
    ("Court", "Note"): ["HasNote"],
    ("Attorney", "Note"): ["HasNote"],
    ("LawFirm", "Note"): ["HasNote"],
    ("Vendor", "Note"): ["HasNote"],
    ("Organization", "Note"): ["HasNote"],
    ("Pleading", "Note"): ["HasNote"],
    ("Document", "Note"): ["HasNote"],
    # Reverse (Note to Entity)
    ("Note", "Case"): ["NotedOn"],
    ("Note", "Client"): ["NotedOn"],
    ("Note", "PIPClaim"): ["NotedOn"],
    ("Note", "BIClaim"): ["NotedOn"],
    ("Note", "UMClaim"): ["NotedOn"],
    ("Note", "UIMClaim"): ["NotedOn"],
    ("Note", "WCClaim"): ["NotedOn"],
    ("Note", "MedPayClaim"): ["NotedOn"],
    ("Note", "MedicalProvider"): ["NotedOn"],
    ("Note", "Insurer"): ["NotedOn"],
    ("Note", "Adjuster"): ["NotedOn"],
    ("Note", "Lien"): ["NotedOn"],
    ("Note", "Defendant"): ["NotedOn"],
    ("Note", "Court"): ["NotedOn"],
    ("Note", "Attorney"): ["NotedOn"],

    # =========================================================================
    # Fallback for any entity pair not explicitly mapped
    # =========================================================================
    ("Entity", "Entity"): ["RelatesTo", "Mentions"],
}


# =============================================================================
# Graphiti Client Singleton
# =============================================================================

_graphiti_instance: Optional[Graphiti] = None


async def get_graphiti() -> Graphiti:
    """
    Get or create the singleton Graphiti client.
    
    Configured with:
    - FalkorDB backend (Redis-compatible graph database)
    - Gemini 3 Flash for LLM extraction
    - Gemini embedding model
    - Custom entity types for legal case management
    """
    global _graphiti_instance
    
    if _graphiti_instance is not None:
        return _graphiti_instance
    
    # Get configuration from environment
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required for Graphiti")
    
    falkordb_host = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
    falkordb_port = int(os.getenv("FALKORDB_PORT", "6379"))
    
    # Configure Gemini 3 Flash as the LLM (released Dec 2025)
    llm_config = LLMConfig(
        api_key=google_api_key,
        model="gemini-3-flash-preview",
    )
    
    llm_client = GeminiClient(config=llm_config)
    
    # Configure Gemini embedder
    embedder_config = GeminiEmbedderConfig(
        api_key=google_api_key,
        embedding_model="text-embedding-004",  # Latest Gemini embedding model
    )
    embedder = GeminiEmbedder(config=embedder_config)
    
    # Configure Gemini reranker
    reranker = GeminiRerankerClient(config=llm_config)
    
    # Initialize FalkorDB driver
    falkor_driver = FalkorDriver(
        host=falkordb_host,
        port=falkordb_port,
        database="roscoe_graph",
    )
    
    # Initialize Graphiti with FalkorDB driver
    _graphiti_instance = Graphiti(
        graph_driver=falkor_driver,
        llm_client=llm_client,
        embedder=embedder,
        cross_encoder=reranker,
    )
    
    # Build indices and constraints
    await _graphiti_instance.build_indices_and_constraints()
    
    return _graphiti_instance


async def close_graphiti():
    """Close the Graphiti client connection."""
    global _graphiti_instance
    if _graphiti_instance is not None:
        await _graphiti_instance.close()
        _graphiti_instance = None


# =============================================================================
# Helper Functions for Common Operations
# =============================================================================

async def add_case_episode(
    case_name: str,
    episode_name: str,
    episode_body: str,
    source: str = "agent",
    reference_time: Optional[datetime] = None,
    use_custom_types: bool = True,
) -> None:
    """
    Add an episode to the unified case knowledge graph.
    
    All case data uses a single group_id (CASE_DATA_GROUP_ID) to enable:
    - Entity deduplication across cases (shared providers, insurers, etc.)
    - Cross-case queries and analytics
    - Proper graph relationships
    
    The case_name should be included in the episode_body text so Graphiti's
    LLM creates proper relationships between Case entities and other entities.
    
    Args:
        case_name: The case folder name (included in episode for context, NOT used as group_id)
        episode_name: Brief name for the episode
        episode_body: Natural language description - MUST mention case_name for proper linking
        source: Source of the episode (agent, user, migration, etc.)
        reference_time: When the event occurred (defaults to now)
        use_custom_types: Whether to use custom entity/edge types (default True)
    """
    graphiti = await get_graphiti()
    
    # Build kwargs for add_episode
    kwargs = {
        "name": episode_name,
        "episode_body": episode_body,
        "source": EpisodeType.text,
        "source_description": source,
        "reference_time": reference_time or datetime.now(),
        "group_id": CASE_DATA_GROUP_ID,
    }
    
    # Add custom types if enabled
    if use_custom_types:
        kwargs["entity_types"] = ENTITY_TYPES_DICT
        kwargs["edge_types"] = EDGE_TYPES_DICT
        kwargs["edge_type_map"] = EDGE_TYPE_MAP
    
    await graphiti.add_episode(**kwargs)


async def search_case(
    query: str,
    case_name: Optional[str] = None,
    num_results: int = 20,
) -> list:
    """
    Search the knowledge graph for relevant information.
    
    All case data is in a unified graph (CASE_DATA_GROUP_ID). To search within
    a specific case, include the case name in your query. Graphiti's semantic
    search will find results related to that case through entity relationships.
    
    Args:
        query: Natural language search query
        case_name: If provided, prepends to query for case-specific filtering
        num_results: Maximum number of results to return
    
    Returns:
        List of search results with facts, entities, and relationships
    """
    graphiti = await get_graphiti()
    
    # Prepend case name to query for case-specific filtering
    if case_name:
        full_query = f"For case {case_name}: {query}"
    else:
        full_query = query
    
    results = await graphiti.search(
        query=full_query,
        group_ids=[CASE_DATA_GROUP_ID],  # All case data in one group
        num_results=num_results,
    )
    
    return results


async def get_case_context(case_name: str) -> dict:
    """
    Get comprehensive context for a case from the knowledge graph.
    
    This retrieves all relevant facts about a case, organized by category,
    suitable for injecting into an LLM system prompt.
    
    Args:
        case_name: The case folder name
    
    Returns:
        Dictionary with categorized case information
    """
    graphiti = await get_graphiti()
    
    # Search for all case information - include case name in query for filtering
    results = await graphiti.search(
        query=f"All information about case {case_name} including client, insurance claims, medical providers, documents, and litigation status",
        group_ids=[CASE_DATA_GROUP_ID],  # All case data in one unified group
        num_results=100,
    )
    
    # Organize results by category
    context = {
        "case_name": case_name,
        "client": [],
        "insurance": [],
        "medical_providers": [],
        "documents": [],
        "litigation": [],
        "notes": [],
        "other": [],
    }
    
    for result in results:
        fact = result.fact.lower() if hasattr(result, 'fact') else str(result).lower()
        
        if any(term in fact for term in ["client", "plaintiff", "injured"]):
            context["client"].append(result)
        elif any(term in fact for term in ["insurance", "claim", "adjuster", "progressive", "state farm", "allstate", "geico"]):
            context["insurance"].append(result)
        elif any(term in fact for term in ["medical", "provider", "doctor", "chiropractic", "hospital", "records", "bills", "treatment"]):
            context["medical_providers"].append(result)
        elif any(term in fact for term in ["document", "file", "letter", "demand", "pleading"]):
            context["documents"].append(result)
        elif any(term in fact for term in ["court", "litigation", "attorney", "counsel", "filed", "complaint", "answer"]):
            context["litigation"].append(result)
        elif any(term in fact for term in ["note", "called", "spoke", "meeting"]):
            context["notes"].append(result)
        else:
            context["other"].append(result)
    
    return context


def format_context_for_prompt(context: dict) -> str:
    """
    Format case context dictionary into a string suitable for LLM prompt injection.

    Args:
        context: Dictionary from get_case_context()

    Returns:
        Formatted markdown string
    """
    lines = [f"## Case: {context['case_name']}\n"]

    if context["client"]:
        lines.append("### Client Information")
        for item in context["client"]:
            lines.append(f"- {getattr(item, 'fact', str(item))}")
        lines.append("")

    if context["insurance"]:
        lines.append("### Insurance Claims")
        for item in context["insurance"]:
            lines.append(f"- {getattr(item, 'fact', str(item))}")
        lines.append("")

    if context["medical_providers"]:
        lines.append("### Medical Providers")
        for item in context["medical_providers"]:
            lines.append(f"- {getattr(item, 'fact', str(item))}")
        lines.append("")

    if context["litigation"]:
        lines.append("### Litigation")
        for item in context["litigation"]:
            lines.append(f"- {getattr(item, 'fact', str(item))}")
        lines.append("")

    if context["documents"]:
        lines.append("### Documents")
        for item in context["documents"][:10]:  # Limit to 10 most relevant
            lines.append(f"- {getattr(item, 'fact', str(item))}")
        lines.append("")

    if context["notes"]:
        lines.append("### Recent Activity")
        for item in context["notes"][:5]:  # Limit to 5 most recent
            lines.append(f"- {getattr(item, 'fact', str(item))}")
        lines.append("")

    return "\n".join(lines)


async def generate_case_summary(case_name: str) -> dict:
    """
    Generate case summary on-demand from graph data.

    Computes fresh summary from current graph state - no stored fields.
    This replaces the old SQL computed columns (total_medical_bills, total_expenses,
    total_liens, case_summary, current_status) with real-time graph queries.

    Args:
        case_name: Case name/identifier

    Returns:
        Dictionary with comprehensive case information computed from graph
    """
    # Get case basic info
    case_query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})
    RETURN c.case_type, c.accident_date, c.sol_date
    """
    case_info = await run_cypher_query(case_query, {"case_name": case_name})

    # Get current phase
    phase = await get_case_phase(case_name)

    # Get client
    client_query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[:HAS_CLIENT]->(client:Entity {entity_type: 'Client'})
    RETURN client.name, client.phone, client.email
    """
    client = await run_cypher_query(client_query, {"case_name": case_name})

    # Get total medical bills (computed)
    bills_query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[]-(p:Entity {entity_type: 'MedicalProvider'})
    OPTIONAL MATCH (p)-[:HAS_BILL]->(b:Entity)
    RETURN COALESCE(SUM(b.amount), 0) as total_bills
    """
    bills = await run_cypher_query(bills_query, {"case_name": case_name})

    # Get total liens (computed)
    liens_query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[:HAS_LIEN]->(l:Entity {entity_type: 'Lien'})
    RETURN COALESCE(SUM(l.amount), 0) as total_liens
    """
    liens = await run_cypher_query(liens_query, {"case_name": case_name})

    # Get total expenses (computed)
    expenses_query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[:HAS_EXPENSE]->(e:Entity {entity_type: 'Expense'})
    RETURN COALESCE(SUM(e.amount), 0) as total_expenses
    """
    expenses = await run_cypher_query(expenses_query, {"case_name": case_name})

    # Get active claims with demands
    claims_query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[]-(claim:Entity)
    WHERE claim.entity_type IN ['BIClaim', 'UMClaim', 'UIMClaim', 'WCClaim', 'PIPClaim', 'MedPayClaim']
    OPTIONAL MATCH (claim)-[:INSURED_BY]->(insurer:Entity {entity_type: 'Insurer'})
    OPTIONAL MATCH (claim)-[:ASSIGNED_ADJUSTER]->(adj:Entity {entity_type: 'Adjuster'})
    RETURN claim.entity_type as claim_type,
           claim.claim_number,
           insurer.name as insurer,
           adj.name as adjuster,
           claim.demand_amount,
           claim.current_offer,
           claim.settlement_amount,
           claim.exhausted,
           claim.is_active_negotiation,
           claim.coverage_confirmation
    """
    claims = await run_cypher_query(claims_query, {"case_name": case_name})

    # Get recent notes (last 10)
    notes_query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[:HAS_NOTE]->(n:Entity {entity_type: 'Note'})
    RETURN n.note_date, n.content, n.category, n.author
    ORDER BY n.note_date DESC
    LIMIT 10
    """
    notes = await run_cypher_query(notes_query, {"case_name": case_name})

    # Compute phase progress
    phase_progress = None
    if phase:
        advance_check = await check_phase_can_advance(case_name, phase.get("name"))
        landmarks = await get_case_landmark_statuses(case_name, phase.get("name"))
        if landmarks:
            completed = len([l for l in landmarks if l.get("status") == "complete"])
            total = len(landmarks)
            phase_progress = f"{int(completed/total*100)}% ({completed}/{total} landmarks complete)"

    return {
        "case_name": case_name,
        "case_type": case_info[0].get("case_type") if case_info else None,
        "accident_date": case_info[0].get("accident_date") if case_info else None,
        "sol_date": case_info[0].get("sol_date") if case_info else None,
        "client": client[0] if client else None,
        "current_phase": phase.get("display_name") if phase else None,
        "phase_progress": phase_progress,
        "total_medical_bills": bills[0].get("total_bills") if bills else 0,
        "total_liens": liens[0].get("total_liens") if liens else 0,
        "total_expenses": expenses[0].get("total_expenses") if expenses else 0,
        "active_claims": claims,
        "recent_activity": notes,
    }


# =============================================================================
# Direct Graph Queries (Cypher)
# =============================================================================
# These functions bypass Graphiti's semantic search and query FalkorDB directly
# using Cypher. Use these for structural/relationship queries where you know
# exactly what you're looking for.

async def run_cypher_query(query: str, parameters: Optional[dict] = None) -> list:
    """
    Execute a raw Cypher query against FalkorDB.
    
    This bypasses Graphiti's semantic search and queries the graph directly.
    Use for structural queries like finding relationships, traversing the graph,
    or aggregating data.
    
    Args:
        query: Cypher query string
        parameters: Optional query parameters (for parameterized queries)
    
    Returns:
        List of result records
    
    Example:
        # Find all cases for a medical provider
        results = await run_cypher_query('''
            MATCH (p:Entity {name: 'Allstar Chiropractic'})-[r]-(c:Entity)
            WHERE c.entity_type = 'Case'
            RETURN c.name as case_name, type(r) as relationship
        ''')
    """
    graphiti = await get_graphiti()
    
    # Access the underlying FalkorDB driver (async client)
    driver = graphiti.driver
    graph = driver.client.select_graph("roscoe_graph")
    
    # Execute query - async FalkorDB graph query
    result = await graph.query(query, parameters or {})
    
    # Convert to list of dicts
    records = []
    if result.result_set:
        headers = result.header
        for row in result.result_set:
            record = {}
            for i, header in enumerate(headers):
                # Header format in FalkorDB async: [type_code, column_name]
                if isinstance(header, (list, tuple)) and len(header) >= 2:
                    col_name = header[1]
                else:
                    col_name = str(header)
                record[col_name] = row[i]
            records.append(record)
    
    return records


async def get_cases_by_provider(provider_name: str) -> list:
    """
    Get all cases associated with a medical provider.
    
    With the unified graph, this query finds all Case entities connected to
    the specified provider - enabling cross-case provider lookups.
    
    Args:
        provider_name: Name of the medical provider (partial match supported)
    
    Returns:
        List of case names connected to this provider
    """
    query = """
        MATCH (p:Entity)-[r]-(c:Entity)
        WHERE p.name CONTAINS $provider_name
        AND c.entity_type = 'Case'
        RETURN DISTINCT c.name as case_name
        ORDER BY c.name
    """
    results = await run_cypher_query(query, {"provider_name": provider_name})
    return results


async def get_cases_by_insurer(insurer_name: str) -> list:
    """
    Get all cases with claims against a specific insurer.
    
    Args:
        insurer_name: Name of the insurance company (e.g., "State Farm", "Progressive")
    
    Returns:
        List of cases with their claim types
    """
    query = """
        MATCH (i:Entity)-[r]-(c:Entity)
        WHERE i.name CONTAINS $insurer_name
        AND c.entity_type = 'Case'
        RETURN DISTINCT c.name as case_name, i.entity_type as claim_type
        ORDER BY c.name
    """
    results = await run_cypher_query(query, {"insurer_name": insurer_name})
    return results


async def get_provider_stats() -> list:
    """
    Get statistics on medical providers across all cases.
    
    Returns:
        List of providers with case counts, sorted by frequency
    """
    query = """
        MATCH (p:Entity {entity_type: 'MedicalProvider'})-[r]-(c:Entity {entity_type: 'Case'})
        RETURN p.name as provider_name, 
               COUNT(DISTINCT c) as case_count
        ORDER BY case_count DESC
    """
    return await run_cypher_query(query)


async def get_insurer_stats() -> list:
    """
    Get statistics on insurance companies across all cases.
    
    Returns:
        List of insurers with claim counts by type
    """
    query = """
        MATCH (i:Entity)-[r]-(c:Entity {entity_type: 'Case'})
        WHERE i.entity_type IN ['PIPClaim', 'BIClaim', 'UMClaim', 'UIMClaim', 'WCClaim', 'MedPayClaim', 'Insurer']
        RETURN i.name as entity_name,
               i.entity_type as entity_type,
               COUNT(DISTINCT c) as case_count
        ORDER BY case_count DESC
    """
    return await run_cypher_query(query)


async def get_entity_relationships(entity_name: str, depth: int = 1) -> list:
    """
    Get all relationships for an entity up to a certain depth.
    
    Args:
        entity_name: Name of the entity to start from
        depth: How many relationship hops to traverse (default 1)
    
    Returns:
        List of related entities and their relationships
    """
    query = f"""
        MATCH path = (start:Entity {{name: $entity_name}})-[*1..{depth}]-(related:Entity)
        RETURN start.name as source,
               [r IN relationships(path) | type(r)] as relationships,
               related.name as target,
               related.entity_type as target_type
    """
    return await run_cypher_query(query, {"entity_name": entity_name})


async def get_case_graph(case_name: str) -> dict:
    """
    Get the full graph structure for a case - all entities and relationships.
    
    Args:
        case_name: The case folder name
    
    Returns:
        Dictionary with nodes and edges for visualization
    """
    # Get the Case entity and all entities connected to it
    # With unified group, we find entities by their relationship to the Case entity
    nodes_query = """
        MATCH (c:Entity {entity_type: 'Case'})
        WHERE c.name = $case_name OR c.name CONTAINS $case_name
        OPTIONAL MATCH (c)-[*1..2]-(related:Entity)
        WITH COLLECT(DISTINCT c) + COLLECT(DISTINCT related) as all_nodes
        UNWIND all_nodes as e
        RETURN DISTINCT e.uuid as id, e.name as name, e.entity_type as type
    """
    nodes = await run_cypher_query(nodes_query, {"case_name": case_name})
    
    # Get all relationships between entities connected to this case
    edges_query = """
        MATCH (c:Entity {entity_type: 'Case'})
        WHERE c.name = $case_name OR c.name CONTAINS $case_name
        OPTIONAL MATCH (c)-[*1..2]-(related:Entity)
        WITH COLLECT(DISTINCT c) + COLLECT(DISTINCT related) as case_entities
        MATCH (e1:Entity)-[r]->(e2:Entity)
        WHERE e1 IN case_entities AND e2 IN case_entities
        RETURN DISTINCT e1.uuid as source, e2.uuid as target, type(r) as relationship
    """
    edges = await run_cypher_query(edges_query, {"case_name": case_name})
    
    return {
        "case_name": case_name,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


async def find_common_providers(case_names: list = None) -> list:
    """
    Find medical providers that appear across multiple cases.
    
    With the unified graph, providers are deduplicated - one provider entity
    can be linked to multiple Case entities.
    
    Args:
        case_names: Optional list of case names to filter. If None, checks all cases.
    
    Returns:
        Providers that appear in multiple cases with their case connections
    """
    if case_names:
        query = """
            MATCH (p:Entity {entity_type: 'MedicalProvider'})-[r]-(c:Entity {entity_type: 'Case'})
            WHERE c.name IN $case_names
            WITH p.name as provider, COLLECT(DISTINCT c.name) as cases
            WHERE SIZE(cases) > 1
            RETURN provider, cases, SIZE(cases) as case_count
            ORDER BY case_count DESC
        """
        return await run_cypher_query(query, {"case_names": case_names})
    else:
        # Find providers across ALL cases
        query = """
            MATCH (p:Entity {entity_type: 'MedicalProvider'})-[r]-(c:Entity {entity_type: 'Case'})
            WITH p.name as provider, COLLECT(DISTINCT c.name) as cases
            WHERE SIZE(cases) > 1
            RETURN provider, cases, SIZE(cases) as case_count
            ORDER BY case_count DESC
            LIMIT 50
        """
        return await run_cypher_query(query, {})


# =============================================================================
# Workflow Definition Queries
# =============================================================================
# These functions query the workflow structure (phases, workflows, steps, 
# landmarks, skills, templates) that was ingested from workflow_engine/ 
# and workflows/ folders.

WORKFLOW_GROUP_ID = "__workflow_definitions__"

# Group ID for all case data - using a single group enables:
# - Entity deduplication across cases (e.g., one "Jewish Hospital" node linked to many cases)
# - Cross-case queries (e.g., "which cases involve Progressive Insurance?")
# - Proper graph relationships between shared entities
CASE_DATA_GROUP_ID = "roscoe_graph"


async def get_all_phases() -> list:
    """
    Get all phases in order.
    
    Returns:
        List of phases with name, display_name, description, track
    """
    query = """
        MATCH (p:Entity)
        WHERE p.entity_type = 'Phase' AND p.group_id = $group_id
        RETURN p.name as name, 
               p.display_name as display_name, 
               p.description as description,
               p.track as track,
               p.order as order,
               p.next_phase as next_phase
        ORDER BY p.order
    """
    return await run_cypher_query(query, {"group_id": WORKFLOW_GROUP_ID})


async def get_phase_info(phase_name: str) -> dict:
    """
    Get detailed information about a specific phase.
    
    Args:
        phase_name: Phase identifier (e.g., 'file_setup', 'treatment')
    
    Returns:
        Phase information including workflows and landmarks
    """
    # Get phase details
    phase_query = """
        MATCH (p:Entity)
        WHERE p.name = $phase_name AND p.entity_type = 'Phase' AND p.group_id = $group_id
        RETURN p.name as name,
               p.display_name as display_name,
               p.description as description,
               p.track as track,
               p.order as order,
               p.next_phase as next_phase
    """
    phase_results = await run_cypher_query(phase_query, {
        "phase_name": phase_name, 
        "group_id": WORKFLOW_GROUP_ID
    })
    
    if not phase_results:
        return None
    
    phase = phase_results[0]
    
    # Get workflows for this phase
    workflows = await get_phase_workflows(phase_name)
    
    # Get landmarks for this phase
    landmarks = await get_phase_landmarks(phase_name)
    
    return {
        **phase,
        "workflows": workflows,
        "landmarks": landmarks,
    }


async def get_phase_workflows(phase_name: str) -> list:
    """
    Get all workflows for a specific phase.
    
    Args:
        phase_name: Phase identifier (e.g., 'file_setup', 'treatment')
    
    Returns:
        List of workflows with name, description, instructions_path
    """
    query = """
        MATCH (p:Entity)-[:HAS_WORKFLOW]->(w:Entity)
        WHERE p.name = $phase_name AND p.entity_type = 'Phase' AND p.group_id = $group_id
              AND w.entity_type = 'WorkflowDef'
        RETURN w.name as name,
               w.display_name as display_name,
               w.description as description,
               w.instructions_path as instructions_path,
               w.trigger as trigger
        ORDER BY w.name
    """
    return await run_cypher_query(query, {
        "phase_name": phase_name,
        "group_id": WORKFLOW_GROUP_ID
    })


async def get_phase_landmarks(phase_name: str) -> list:
    """
    Get all landmarks for a specific phase.
    
    Args:
        phase_name: Phase identifier
    
    Returns:
        List of landmarks with sub-landmarks
    """
    query = """
        MATCH (p:Entity)-[:HAS_LANDMARK]->(l:Entity)
        WHERE p.name = $phase_name AND p.entity_type = 'Phase' AND p.group_id = $group_id
              AND l.entity_type = 'Landmark' AND l.parent_landmark IS NULL
        OPTIONAL MATCH (l)-[:HAS_SUB_LANDMARK]->(sub:Entity)
        WHERE sub.entity_type = 'Landmark'
        RETURN l.landmark_id as landmark_id,
               l.name as name,
               l.description as description,
               l.mandatory as mandatory,
               l.verification_fields as verification_fields,
               l.order as order,
               COLLECT(CASE WHEN sub IS NOT NULL THEN sub.name END) as sub_landmarks
        ORDER BY l.order
    """
    return await run_cypher_query(query, {
        "phase_name": phase_name,
        "group_id": WORKFLOW_GROUP_ID
    })


async def get_workflow_info(workflow_name: str) -> dict:
    """
    Get detailed information about a specific workflow.
    
    Args:
        workflow_name: Workflow identifier (e.g., 'insurance_bi_claim', 'intake')
    
    Returns:
        Workflow information including steps, skills, templates
    """
    # Get workflow details
    wf_query = """
        MATCH (w:Entity)
        WHERE w.name = $workflow_name AND w.entity_type = 'WorkflowDef' AND w.group_id = $group_id
        RETURN w.name as name,
               w.display_name as display_name,
               w.description as description,
               w.phase as phase,
               w.instructions_path as instructions_path,
               w.trigger as trigger,
               w.prerequisites as prerequisites
    """
    wf_results = await run_cypher_query(wf_query, {
        "workflow_name": workflow_name,
        "group_id": WORKFLOW_GROUP_ID
    })
    
    if not wf_results:
        return None
    
    workflow = wf_results[0]
    
    # Get steps
    steps = await get_workflow_steps(workflow_name)
    
    # Get skills
    skills_query = """
        MATCH (w:Entity)-[:USES_SKILL]->(s:Entity)
        WHERE w.name = $workflow_name AND w.entity_type = 'WorkflowDef' AND w.group_id = $group_id
              AND s.entity_type = 'WorkflowSkill'
        RETURN s.name as name, s.path as path, s.agent_ready as agent_ready
    """
    skills = await run_cypher_query(skills_query, {
        "workflow_name": workflow_name,
        "group_id": WORKFLOW_GROUP_ID
    })
    
    # Get templates
    templates_query = """
        MATCH (w:Entity)-[:USES_TEMPLATE]->(t:Entity)
        WHERE w.name = $workflow_name AND w.entity_type = 'WorkflowDef' AND w.group_id = $group_id
              AND t.entity_type = 'WorkflowTemplate'
        RETURN t.name as name, t.path as path, t.file_type as file_type
    """
    templates = await run_cypher_query(templates_query, {
        "workflow_name": workflow_name,
        "group_id": WORKFLOW_GROUP_ID
    })
    
    return {
        **workflow,
        "steps": steps,
        "skills": skills,
        "templates": templates,
    }


async def get_workflow_steps(workflow_name: str) -> list:
    """
    Get all steps for a workflow in order.
    
    Args:
        workflow_name: Workflow identifier
    
    Returns:
        List of steps with name, owner, can_automate, prompt_user
    """
    query = """
        MATCH (w:Entity)-[r:HAS_STEP]->(s:Entity)
        WHERE w.name = $workflow_name AND w.entity_type = 'WorkflowDef' AND w.group_id = $group_id
              AND s.entity_type = 'WorkflowStep'
        RETURN s.step_id as step_id,
               s.name as name,
               s.description as description,
               s.owner as owner,
               s.can_automate as can_automate,
               s.prompt_user as prompt_user,
               s.completion_check as completion_check,
               s.order as order
        ORDER BY s.order
    """
    return await run_cypher_query(query, {
        "workflow_name": workflow_name,
        "group_id": WORKFLOW_GROUP_ID
    })


async def get_step_resources(workflow_name: str, step_id: str) -> dict:
    """
    Get all resources (skills, checklists, templates, tools) for a step.
    
    Args:
        workflow_name: Workflow identifier
        step_id: Step identifier within the workflow
    
    Returns:
        Dictionary with skills, checklists, templates, tools
    """
    # Get skills
    skills_query = """
        MATCH (w:Entity)-[:HAS_STEP]->(s:Entity)-[:USES_SKILL]->(sk:Entity)
        WHERE w.name = $workflow_name AND w.entity_type = 'WorkflowDef' AND w.group_id = $group_id
              AND s.step_id = $step_id AND s.entity_type = 'WorkflowStep'
        RETURN sk.name as name, sk.path as path
    """
    skills = await run_cypher_query(skills_query, {
        "workflow_name": workflow_name,
        "step_id": step_id,
        "group_id": WORKFLOW_GROUP_ID
    })
    
    # Get checklists
    checklists_query = """
        MATCH (w:Entity)-[:HAS_STEP]->(s:Entity)-[:USES_CHECKLIST]->(c:Entity)
        WHERE w.name = $workflow_name AND w.entity_type = 'WorkflowDef' AND w.group_id = $group_id
              AND s.step_id = $step_id AND s.entity_type = 'WorkflowStep'
        RETURN c.name as name, c.path as path
    """
    checklists = await run_cypher_query(checklists_query, {
        "workflow_name": workflow_name,
        "step_id": step_id,
        "group_id": WORKFLOW_GROUP_ID
    })
    
    # Get templates
    templates_query = """
        MATCH (w:Entity)-[:HAS_STEP]->(s:Entity)-[:USES_TEMPLATE]->(t:Entity)
        WHERE w.name = $workflow_name AND w.entity_type = 'WorkflowDef' AND w.group_id = $group_id
              AND s.step_id = $step_id AND s.entity_type = 'WorkflowStep'
        RETURN t.name as name, t.path as path
    """
    templates = await run_cypher_query(templates_query, {
        "workflow_name": workflow_name,
        "step_id": step_id,
        "group_id": WORKFLOW_GROUP_ID
    })
    
    # Get tools
    tools_query = """
        MATCH (w:Entity)-[:HAS_STEP]->(s:Entity)-[:USES_TOOL]->(t:Entity)
        WHERE w.name = $workflow_name AND w.entity_type = 'WorkflowDef' AND w.group_id = $group_id
              AND s.step_id = $step_id AND s.entity_type = 'WorkflowStep'
        RETURN t.name as name, t.path as path
    """
    tools = await run_cypher_query(tools_query, {
        "workflow_name": workflow_name,
        "step_id": step_id,
        "group_id": WORKFLOW_GROUP_ID
    })
    
    return {
        "skills": skills,
        "checklists": checklists,
        "templates": templates,
        "tools": tools,
    }


async def get_applicable_skills(phase_name: str) -> list:
    """
    Get all skills that apply to a specific phase.
    
    Args:
        phase_name: Phase identifier
    
    Returns:
        List of skills with capabilities
    """
    query = """
        MATCH (s:Entity)-[:APPLIES_TO_PHASE]->(p:Entity)
        WHERE s.entity_type = 'WorkflowSkill' AND s.group_id = $group_id
              AND p.name = $phase_name
        RETURN s.name as name,
               s.path as path,
               s.description as description,
               s.capabilities as capabilities,
               s.agent_ready as agent_ready,
               s.quality_score as quality_score
        ORDER BY s.quality_score DESC
    """
    return await run_cypher_query(query, {
        "phase_name": phase_name,
        "group_id": WORKFLOW_GROUP_ID
    })


async def get_all_checklists() -> list:
    """
    Get all available checklists.
    
    Returns:
        List of checklists with name, path, when_to_use
    """
    query = """
        MATCH (c:Entity)
        WHERE c.entity_type = 'WorkflowChecklist' AND c.group_id = $group_id
        RETURN c.name as name,
               c.path as path,
               c.when_to_use as when_to_use
        ORDER BY c.name
    """
    return await run_cypher_query(query, {"group_id": WORKFLOW_GROUP_ID})


async def get_workflow_by_landmark(landmark_id: str) -> list:
    """
    Find workflows related to completing a specific landmark.
    
    Args:
        landmark_id: Landmark identifier
    
    Returns:
        List of related workflows
    """
    # First get the phase for this landmark
    phase_query = """
        MATCH (l:Entity)
        WHERE l.landmark_id = $landmark_id AND l.entity_type = 'Landmark' AND l.group_id = $group_id
        RETURN l.phase as phase
    """
    phase_results = await run_cypher_query(phase_query, {
        "landmark_id": landmark_id,
        "group_id": WORKFLOW_GROUP_ID
    })
    
    if not phase_results:
        return []
    
    phase = phase_results[0].get('phase')
    
    # Get workflows for that phase
    return await get_phase_workflows(phase)


# =============================================================================
# Case Workflow State Queries (Deterministic Model)
# =============================================================================
# These functions query and update the deterministic workflow state for cases.
# The state is stored explicitly in the graph via:
# - Case -[IN_PHASE]-> Phase
# - Case -[LANDMARK_STATUS]-> Landmark

import json


async def get_case_phase(case_name: str) -> dict:
    """
    Get the current phase for a case.
    
    This returns the phase the case is currently in, via the IN_PHASE relationship.
    
    Args:
        case_name: Case name/identifier
    
    Returns:
        Dictionary with phase info: {name, display_name, order, track, entered_at}
        Returns None if case not found or no phase set.
    """
    query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[r:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
    RETURN p.name as name,
           p.display_name as display_name,
           p.order as phase_order,
           p.track as track,
           p.next_phase_name as next_phase,
           r.entered_at as entered_at
    """
    results = await run_cypher_query(query, {"case_name": case_name})
    return results[0] if results else None


async def get_case_landmark_statuses(case_name: str, phase_name: str = None) -> list:
    """
    Get all landmark statuses for a case.
    
    Args:
        case_name: Case name/identifier
        phase_name: Optional - filter to landmarks for a specific phase
    
    Returns:
        List of landmark statuses with:
        - landmark_id, display_name, landmark_type, is_hard_blocker
        - status, sub_steps, notes, completed_at
    """
    if phase_name:
        query = """
        MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[r:LANDMARK_STATUS]->(l:Entity {entity_type: 'Landmark', phase: $phase_name})
        RETURN l.name as landmark_id,
               l.display_name as display_name,
               l.phase as phase,
               l.landmark_type as landmark_type,
               l.is_hard_blocker as is_hard_blocker,
               l.can_override as can_override,
               l.sub_steps as landmark_sub_steps,
               r.status as status,
               r.sub_steps as case_sub_steps,
               r.notes as notes,
               r.completed_at as completed_at,
               r.updated_at as updated_at
        ORDER BY l.name
        """
        return await run_cypher_query(query, {"case_name": case_name, "phase_name": phase_name})
    else:
        query = """
        MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[r:LANDMARK_STATUS]->(l:Entity {entity_type: 'Landmark'})
        RETURN l.name as landmark_id,
               l.display_name as display_name,
               l.phase as phase,
               l.landmark_type as landmark_type,
               l.is_hard_blocker as is_hard_blocker,
               l.can_override as can_override,
               l.sub_steps as landmark_sub_steps,
               r.status as status,
               r.sub_steps as case_sub_steps,
               r.notes as notes,
               r.completed_at as completed_at,
               r.updated_at as updated_at
        ORDER BY l.phase, l.name
        """
        return await run_cypher_query(query, {"case_name": case_name})


async def get_landmark_status(case_name: str, landmark_id: str) -> dict:
    """
    Get status for a specific landmark on a case.
    
    Args:
        case_name: Case name/identifier
        landmark_id: Landmark identifier
    
    Returns:
        Landmark status info or None if not found
    """
    query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[r:LANDMARK_STATUS]->(l:Entity {entity_type: 'Landmark', name: $landmark_id})
    RETURN l.name as landmark_id,
           l.display_name as display_name,
           l.phase as phase,
           l.landmark_type as landmark_type,
           l.is_hard_blocker as is_hard_blocker,
           l.sub_steps as landmark_sub_steps,
           r.status as status,
           r.sub_steps as case_sub_steps,
           r.notes as notes,
           r.completed_at as completed_at
    """
    results = await run_cypher_query(query, {"case_name": case_name, "landmark_id": landmark_id})
    return results[0] if results else None


# DEPRECATED: Use graph_manager.update_landmark_status() instead
# This function modifies structured workflow state, which should be handled by graph_manager.py
async def update_case_landmark_status(
    case_name: str,
    landmark_id: str,
    status: str,
    sub_steps: dict = None,
    notes: str = None
) -> bool:
    """
    Update a landmark's status for a case.
    
    Args:
        case_name: Case name/identifier
        landmark_id: Landmark identifier
        status: New status ('complete', 'incomplete', 'in_progress', 'not_applicable')
        sub_steps: Optional dict of sub-step completions
        notes: Optional notes about the status
    
    Returns:
        True if updated successfully
    """
    from datetime import datetime
    
    sub_steps_json = json.dumps(sub_steps) if sub_steps else None
    now = datetime.now().isoformat()
    
    # If status is complete, set completed_at
    if status == "complete":
        query = """
        MATCH (c:Entity {entity_type: 'Case', name: $case_name})
        MATCH (l:Entity {entity_type: 'Landmark', name: $landmark_id})
        MERGE (c)-[r:LANDMARK_STATUS]->(l)
        SET r.status = $status,
            r.sub_steps = $sub_steps,
            r.notes = $notes,
            r.completed_at = $completed_at,
            r.updated_at = $updated_at
        RETURN c.name, l.name
        """
        params = {
            "case_name": case_name,
            "landmark_id": landmark_id,
            "status": status,
            "sub_steps": sub_steps_json,
            "notes": notes,
            "completed_at": now,
            "updated_at": now
        }
    else:
        query = """
        MATCH (c:Entity {entity_type: 'Case', name: $case_name})
        MATCH (l:Entity {entity_type: 'Landmark', name: $landmark_id})
        MERGE (c)-[r:LANDMARK_STATUS]->(l)
        SET r.status = $status,
            r.sub_steps = $sub_steps,
            r.notes = $notes,
            r.updated_at = $updated_at
        RETURN c.name, l.name
        """
        params = {
            "case_name": case_name,
            "landmark_id": landmark_id,
            "status": status,
            "sub_steps": sub_steps_json,
            "notes": notes,
            "updated_at": now
        }
    
    results = await run_cypher_query(query, params)
    return len(results) > 0


async def check_phase_can_advance(case_name: str, current_phase: str = None) -> dict:
    """
    Check if a case can advance to the next phase.
    
    This checks that all hard blockers for the current phase are complete.
    
    Args:
        case_name: Case name/identifier
        current_phase: Optional - phase to check (defaults to case's current phase)
    
    Returns:
        Dictionary with:
        - can_advance: bool
        - blocking_landmarks: list of incomplete hard blockers
        - next_phase: name of next phase
    """
    # Get current phase if not provided
    if not current_phase:
        phase_info = await get_case_phase(case_name)
        if not phase_info:
            return {"can_advance": False, "error": "Case not found or no phase set"}
        current_phase = phase_info.get("name")
        next_phase = phase_info.get("next_phase")
    else:
        # Get next phase from phase definition
        phase_query = """
        MATCH (p:Entity {entity_type: 'Phase', name: $phase_name})
        RETURN p.next_phase_name as next_phase
        """
        results = await run_cypher_query(phase_query, {"phase_name": current_phase})
        next_phase = results[0].get("next_phase") if results else None
    
    # Find all hard blockers that are not complete
    blocker_query = """
    MATCH (p:Entity {entity_type: 'Phase', name: $phase_name})-[:HAS_LANDMARK]->(l:Entity {entity_type: 'Landmark', is_hard_blocker: true})
    OPTIONAL MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[r:LANDMARK_STATUS]->(l)
    WITH l, r
    WHERE r IS NULL OR r.status <> 'complete'
    RETURN l.name as landmark_id,
           l.display_name as display_name,
           COALESCE(r.status, 'not_started') as current_status
    """
    blocking = await run_cypher_query(blocker_query, {
        "case_name": case_name,
        "phase_name": current_phase
    })
    
    return {
        "can_advance": len(blocking) == 0,
        "blocking_landmarks": blocking,
        "current_phase": current_phase,
        "next_phase": next_phase
    }


# DEPRECATED: Use graph_manager.advance_phase() instead
# This function modifies structured workflow state, which should be handled by graph_manager.py
async def advance_case_to_phase(case_name: str, target_phase: str, force: bool = False) -> dict:
    """
    Advance a case to a new phase.
    
    Args:
        case_name: Case name/identifier
        target_phase: Phase to advance to
        force: If True, skip hard blocker checks (for admin override)
    
    Returns:
        Dictionary with result info
    """
    from datetime import datetime
    
    # Check current phase
    current = await get_case_phase(case_name)
    current_phase = current.get("name") if current else None
    
    # If not forcing, check hard blockers
    if not force and current_phase:
        check = await check_phase_can_advance(case_name, current_phase)
        if not check.get("can_advance"):
            return {
                "success": False,
                "error": "Cannot advance - incomplete hard blockers",
                "blocking_landmarks": check.get("blocking_landmarks")
            }
    
    # Update the phase
    now = datetime.now().isoformat()
    
    # Remove old IN_PHASE relationship and create new one
    query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})
    OPTIONAL MATCH (c)-[old:IN_PHASE]->(:Entity)
    DELETE old
    WITH c
    MATCH (p:Entity {entity_type: 'Phase', name: $target_phase})
    MERGE (c)-[r:IN_PHASE]->(p)
    SET r.entered_at = $entered_at,
        r.previous_phase = $previous_phase
    RETURN c.name as case_name, p.name as new_phase
    """
    
    results = await run_cypher_query(query, {
        "case_name": case_name,
        "target_phase": target_phase,
        "entered_at": now,
        "previous_phase": current_phase
    })
    
    if results:
        return {
            "success": True,
            "case_name": case_name,
            "previous_phase": current_phase,
            "new_phase": target_phase,
            "entered_at": now
        }
    else:
        return {
            "success": False,
            "error": "Failed to update phase relationship"
        }


async def get_case_workflow_state(case_name: str) -> dict:
    """
    Get the complete deterministic workflow state for a case.
    
    This is the main query function for the GraphWorkflowStateComputer.
    
    Args:
        case_name: Case name/identifier
    
    Returns:
        Complete state dictionary including:
        - current_phase with metadata
        - all landmark statuses grouped by phase
        - blocking landmarks
        - next actions
    """
    # Get current phase
    phase = await get_case_phase(case_name)
    if not phase:
        return {
            "case_name": case_name,
            "error": "Case not found or no phase set",
            "current_phase": None,
            "landmarks": {},
            "blocking_landmarks": [],
            "can_advance": False
        }
    
    current_phase = phase.get("name")
    
    # Get all landmark statuses
    all_landmarks = await get_case_landmark_statuses(case_name)
    
    # Group landmarks by phase
    landmarks_by_phase = {}
    for lm in all_landmarks:
        phase_name = lm.get("phase")
        if phase_name not in landmarks_by_phase:
            landmarks_by_phase[phase_name] = []
        landmarks_by_phase[phase_name].append(lm)
    
    # Check if can advance
    advance_check = await check_phase_can_advance(case_name, current_phase)
    
    # Get incomplete landmarks for current phase
    current_phase_landmarks = landmarks_by_phase.get(current_phase, [])
    incomplete_landmarks = [
        lm for lm in current_phase_landmarks 
        if lm.get("status") not in ["complete", "not_applicable"]
    ]
    
    # Find workflows to complete incomplete landmarks
    workflows_needed = []
    for lm in incomplete_landmarks:
        wf_query = """
        MATCH (l:Entity {entity_type: 'Landmark', name: $landmark_id})-[:ACHIEVED_BY]->(w:Entity {entity_type: 'WorkflowDef'})
        RETURN w.name as workflow_name, w.display_name as display_name, w.description as description
        """
        workflows = await run_cypher_query(wf_query, {"landmark_id": lm.get("landmark_id")})
        if workflows:
            workflows_needed.append({
                "landmark": lm.get("landmark_id"),
                "landmark_display": lm.get("display_name"),
                "workflows": workflows
            })
    
    return {
        "case_name": case_name,
        "current_phase": {
            "name": current_phase,
            "display_name": phase.get("display_name"),
            "track": phase.get("track"),
            "entered_at": phase.get("entered_at")
        },
        "next_phase": advance_check.get("next_phase"),
        "can_advance": advance_check.get("can_advance"),
        "blocking_landmarks": advance_check.get("blocking_landmarks", []),
        "landmarks_by_phase": landmarks_by_phase,
        "current_phase_landmarks": {
            "total": len(current_phase_landmarks),
            "complete": len([l for l in current_phase_landmarks if l.get("status") == "complete"]),
            "incomplete": len(incomplete_landmarks),
            "landmarks": current_phase_landmarks
        },
        "workflows_needed": workflows_needed
    }
