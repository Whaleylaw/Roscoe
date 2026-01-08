"""
Graphiti Knowledge Graph Client

Provides a singleton Graphiti client for the Roscoe platform, configured with:
- FalkorDB as the graph database backend
- OpenAI for LLM inference and embeddings (defaults: gpt-4o-mini, text-embedding-3-small)
- Custom entity types for legal case management
"""

import os
from typing import Optional
from datetime import date, datetime, timezone
from pydantic import BaseModel, Field

# Graphiti imports

# FalkorDB connection config
FALKORDB_HOST = os.getenv("FALKORDB_HOST", "roscoe-graphdb")
FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", "6379"))

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
    """A personal injury case - immutable facts only. Name is set explicitly (not auto-generated) (e.g., 'Christopher-Lanier-MVA-6-28-2025')."""
    case_type: Optional[str] = Field(default=None, description="Type: MVA, Premise, WC, Med-Mal, Dog-Bite, Slip-Fall")
    accident_date: Optional[date] = Field(default=None, description="Date of accident/incident")
    sol_date: Optional[date] = Field(default=None, description="Statute of limitations deadline")
    # Everything else (phase, client, totals, status) is relationships or computed from graph


class Client(BaseModel):
    """A client/plaintiff in a personal injury case. Name is set explicitly (not auto-generated)."""
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    address: Optional[str] = Field(default=None, description="Mailing address")
    date_of_birth: Optional[date] = Field(default=None, description="Date of birth")


class Defendant(BaseModel):
    """The at-fault party in a case. Name is set explicitly (not auto-generated)."""
    insurer: Optional[str] = Field(default=None, description="Defendant's insurance company")
    policy_number: Optional[str] = Field(default=None, description="Policy number for defendant's coverage")
    driver_license: Optional[str] = Field(default=None, description="Driver's license number")
    phone: Optional[str] = Field(default=None, description="Phone number")
    address: Optional[str] = Field(default=None, description="Address")
    project_name: Optional[str] = Field(default=None, description="Associated case name")


class Organization(BaseModel):
    """A generic organization not fitting other specific types. Name is set explicitly (not auto-generated)."""
    org_type: Optional[str] = Field(default=None, description="Type: law_firm, medical_practice, insurance_company, government, vendor, trucking, other")
    phone: Optional[str] = Field(default=None, description="Main phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Address")


class Community(BaseModel):
    """Group of related entities for collective queries (Graphiti-inspired). Name is set explicitly (not auto-generated)."""
    community_type: Optional[str] = Field(default=None, description="Type: provider_group, attorney_network, related_cases, injury_type, defendant_group")
    description: Optional[str] = Field(default=None, description="What this community represents")
    created_date: Optional[date] = Field(default=None, description="When community was created")
    member_count: Optional[int] = Field(default=None, description="Number of members")


# --- Insurance Entities ---

class Insurer(BaseModel):
    """An insurance company. Name is set explicitly (not auto-generated) (e.g., State Farm, Progressive)."""
    phone: Optional[str] = Field(default=None, description="Main phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Mailing address")


class Adjuster(BaseModel):
    """An insurance adjuster handling a claim. Name is set explicitly (not auto-generated)."""
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")


class InsurancePolicy(BaseModel):
    """An insurance policy providing coverage. One policy can have multiple claim types. Name is set explicitly (policy number or identifier)."""
    policy_number: str = Field(description="Policy number - REQUIRED")
    insurer_name: str = Field(description="Insurance company name")
    policyholder_name: str = Field(description="Who owns the policy (may be client or defendant)")

    # Coverage limits by type
    pip_limit: Optional[float] = Field(default=None, description="PIP coverage limit")
    bi_limit: Optional[float] = Field(default=None, description="BI liability limit per person/occurrence")
    pd_limit: Optional[float] = Field(default=None, description="Property damage limit")
    um_limit: Optional[float] = Field(default=None, description="UM coverage limit")
    uim_limit: Optional[float] = Field(default=None, description="UIM coverage limit")
    medpay_limit: Optional[float] = Field(default=None, description="MedPay coverage limit")

    # Policy dates
    effective_date: Optional[date] = Field(default=None, description="Policy effective/start date")
    expiration_date: Optional[date] = Field(default=None, description="Policy expiration date")

    # Policy type
    policy_type: Optional[str] = Field(default=None, description="auto | health | workers_comp | homeowners | umbrella")

    # Metadata
    source: Optional[str] = Field(default=None, description="dec_page | verbal | email | case_data")
    validation_state: Optional[str] = Field(default=None, description="verified | unverified | needs_review")


class InsurancePayment(BaseModel):
    """Individual payment from insurance company (PIP advance, BI settlement payment, etc.). Name is set explicitly."""
    payment_date: date = Field(description="Date payment received - REQUIRED")
    amount: float = Field(description="Payment amount - REQUIRED")
    payment_type: str = Field(description="partial | final | advance | medpay | pip | bi_settlement | um_settlement")
    check_number: Optional[str] = Field(default=None, description="Check number or transaction reference")
    memo: Optional[str] = Field(default=None, description="Payment memo or description")

    # What this payment is for
    for_medical_bills: Optional[bool] = Field(default=None, description="Whether payment is for medical bills")
    for_settlement: Optional[bool] = Field(default=None, description="Whether payment is settlement")
    for_lost_wages: Optional[bool] = Field(default=None, description="Whether payment is for lost wages")

    # Metadata
    notes: Optional[str] = Field(default=None, description="Free-form notes about payment")


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

    # Denial and appeal tracking
    denial_reason: Optional[str] = Field(default=None, description="Reason for denial if coverage denied")
    denial_date: Optional[date] = Field(default=None, description="Date of denial")
    appeal_filed: Optional[bool] = Field(default=None, description="Whether appeal was filed")
    appeal_date: Optional[date] = Field(default=None, description="Date appeal filed")
    appeal_outcome: Optional[str] = Field(default=None, description="granted | denied | pending")


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

    # Denial and appeal tracking
    denial_reason: Optional[str] = Field(default=None, description="Reason for denial if coverage denied")
    denial_date: Optional[date] = Field(default=None, description="Date of denial")
    appeal_filed: Optional[bool] = Field(default=None, description="Whether appeal was filed")
    appeal_date: Optional[date] = Field(default=None, description="Date appeal filed")
    appeal_outcome: Optional[str] = Field(default=None, description="granted | denied | pending")


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

    # Denial and appeal tracking
    denial_reason: Optional[str] = Field(default=None, description="Reason for denial if coverage denied")
    denial_date: Optional[date] = Field(default=None, description="Date of denial")
    appeal_filed: Optional[bool] = Field(default=None, description="Whether appeal was filed")
    appeal_date: Optional[date] = Field(default=None, description="Date appeal filed")
    appeal_outcome: Optional[str] = Field(default=None, description="granted | denied | pending")


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

    # Denial and appeal tracking
    denial_reason: Optional[str] = Field(default=None, description="Reason for denial if coverage denied")
    denial_date: Optional[date] = Field(default=None, description="Date of denial")
    appeal_filed: Optional[bool] = Field(default=None, description="Whether appeal was filed")
    appeal_date: Optional[date] = Field(default=None, description="Date appeal filed")
    appeal_outcome: Optional[str] = Field(default=None, description="granted | denied | pending")


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

    # Denial and appeal tracking
    denial_reason: Optional[str] = Field(default=None, description="Reason for denial if coverage denied")
    denial_date: Optional[date] = Field(default=None, description="Date of denial")
    appeal_filed: Optional[bool] = Field(default=None, description="Whether appeal was filed")
    appeal_date: Optional[date] = Field(default=None, description="Date appeal filed")
    appeal_outcome: Optional[str] = Field(default=None, description="granted | denied | pending")


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

class HealthSystem(BaseModel):
    """Parent healthcare organization (UofL Health, Norton Healthcare, etc.). Individual locations connect via PART_OF. Name is set explicitly (not auto-generated)."""
    medical_records_endpoint: Optional[str] = Field(default=None, description="Central endpoint for medical records requests")
    billing_endpoint: Optional[str] = Field(default=None, description="Central endpoint for billing/medical bills")
    phone: Optional[str] = Field(default=None, description="Main phone number")
    fax: Optional[str] = Field(default=None, description="Main fax number")
    email: Optional[str] = Field(default=None, description="Contact email")
    address: Optional[str] = Field(default=None, description="Corporate headquarters address")
    website: Optional[str] = Field(default=None, description="Website URL")

    # Records request fields (centralized for all facilities/locations in system)
    records_request_method: Optional[str] = Field(default=None, description="mail | fax | portal | online")
    records_request_url: Optional[str] = Field(default=None, description="URL for online records request")
    records_request_address: Optional[str] = Field(default=None, description="Mailing address for records requests")
    records_request_fax: Optional[str] = Field(default=None, description="Fax number for records requests")
    records_request_phone: Optional[str] = Field(default=None, description="Phone for records requests")
    records_request_notes: Optional[str] = Field(default=None, description="Special instructions for records requests")

    # Billing request fields
    billing_request_method: Optional[str] = Field(default=None, description="mail | fax | portal | online")
    billing_request_address: Optional[str] = Field(default=None, description="Billing department address")
    billing_request_phone: Optional[str] = Field(default=None, description="Billing department phone")

    # Metadata
    source: Optional[str] = Field(default=None, description="official_website | csv | case_data | manual")
    validation_state: Optional[str] = Field(default=None, description="verified | unverified | needs_review")
    last_verified: Optional[datetime] = Field(default=None, description="Last verification timestamp")


class Facility(BaseModel):
    """Treatment facility or medical group - conceptual unit (Norton Orthopedic Institute, Baptist Medical Group). Can have multiple locations or be standalone. Name is set explicitly (not auto-generated)."""
    parent_system: Optional[str] = Field(default=None, description="Parent HealthSystem name if applicable (null for independent)")
    location_count: Optional[int] = Field(default=None, description="Number of locations for this facility")

    # Records request (facility-level override - if different from HealthSystem)
    records_request_method: Optional[str] = Field(default=None, description="mail | fax | portal | online")
    records_request_url: Optional[str] = None
    records_request_address: Optional[str] = None
    records_request_fax: Optional[str] = None
    records_request_phone: Optional[str] = None
    records_request_notes: Optional[str] = None

    # Billing request (facility-level)
    billing_request_method: Optional[str] = None
    billing_request_address: Optional[str] = None
    billing_request_phone: Optional[str] = None

    # Contact
    main_phone: Optional[str] = Field(default=None, description="Main contact phone")
    website: Optional[str] = None

    # Classification
    facility_type: Optional[str] = Field(default=None, description="hospital | clinic | imaging_center | urgent_care | chiropractic")
    specialty: Optional[str] = Field(default=None, description="orthopedics | cardiology | primary_care | etc.")

    # Metadata
    source: Optional[str] = Field(default=None, description="official_website | csv | case_data | manual")
    validation_state: Optional[str] = Field(default=None, description="verified | unverified | needs_review | duplicate | archived")
    last_verified: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, description="Free-form paralegal notes")


class Location(BaseModel):
    """Specific physical location with street address. Part of a Facility (or standalone). Name is set explicitly (not auto-generated)."""
    # Address (REQUIRED for locations)
    address: str = Field(description="Street address - REQUIRED")
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

    # Contact
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None

    # Hierarchy
    parent_facility: Optional[str] = Field(default=None, description="Parent Facility name")
    parent_system: Optional[str] = Field(default=None, description="Parent HealthSystem name (for reference)")

    # Classification
    location_type: Optional[str] = Field(default=None, description="main_campus | satellite | department")
    specialty: Optional[str] = None

    # Records request (location-specific override - rare)
    records_request_method: Optional[str] = None
    records_request_url: Optional[str] = None
    records_request_address: Optional[str] = None
    records_request_fax: Optional[str] = None
    records_request_phone: Optional[str] = None
    records_request_notes: Optional[str] = None

    # Metadata
    source: Optional[str] = None
    validation_state: Optional[str] = None
    last_verified: Optional[datetime] = None


class MedicalProvider(BaseModel):
    """A specific medical provider location (hospital, clinic, imaging center, etc.). Connected to HealthSystem via PART_OF if part of larger system. Name is set explicitly (not auto-generated)."""
    specialty: Optional[str] = Field(default=None, description="Medical specialty: chiropractic, orthopedic, PT, pain management, primary care, ER, imaging, etc.")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Address")
    provider_type: Optional[str] = Field(default=None, description="Type: hospital, clinic, imaging_center, therapy_center, etc.")
    parent_system: Optional[str] = Field(default=None, description="Parent HealthSystem name if applicable")
    medical_records_endpoint: Optional[str] = Field(default=None, description="Where to request records (overrides parent HealthSystem if set)")
    billing_endpoint: Optional[str] = Field(default=None, description="Where to request bills (overrides parent HealthSystem if set)")


class Doctor(BaseModel):
    """An individual physician. Name is set explicitly (not auto-generated). Connected to MedicalProvider via WORKS_AT."""
    specialty: Optional[str] = Field(default=None, description="Medical specialty: orthopedic, neurology, pain management, etc.")
    credentials: Optional[str] = Field(default=None, description="Credentials: MD, DO, DC, PT, etc.")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    npi: Optional[str] = Field(default=None, description="National Provider Identifier")


class Lien(BaseModel):
    """A lien on a specific case. Name is set explicitly (not auto-generated). Lienholder identified via HELD_BY relationship."""
    amount: Optional[float] = Field(default=None, description="Original lien amount")
    account_number: Optional[str] = Field(default=None, description="Account or reference number")
    project_name: Optional[str] = Field(default=None, description="Associated case name")
    date_notice_received: Optional[date] = Field(default=None, description="When lien notice was received")
    date_lien_paid: Optional[date] = Field(default=None, description="When lien was satisfied")
    reduction_amount: Optional[float] = Field(default=None, description="Negotiated reduction amount")
    # lien_type removed - that's on LienHolder entity (via HELD_BY relationship)
    # lienholder_name removed - that's the HELD_BY relationship target


class LienHolder(BaseModel):
    """An entity holding a lien (hospital, ERISA plan, Medicare, collection agency, litigation funding company, etc.). Name is set explicitly (not auto-generated)."""
    lien_type: Optional[str] = Field(default=None, description="Primary lien type: medical, ERISA, Medicare, Medicaid, child_support, case_funding, workers_comp, collection, other")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Address")


# --- Document Entity ---

class Document(BaseModel):
    """A document in the case file system. Name is set explicitly (not auto-generated) (filename)."""
    path: Optional[str] = Field(default=None, description="Path relative to case folder")
    document_type: Optional[str] = Field(default=None, description="Type: letter_of_rep, demand_package, medical_records, medical_bills, records_request, hipaa, retainer, pleading, discovery, correspondence, evidence")
    file_type: Optional[str] = Field(default=None, description="File extension: pdf, docx, jpg, etc.")
    description: Optional[str] = Field(default=None, description="Brief description of document contents")


# --- Document Subtypes (Specific document entities) ---

class MedicalRecords(BaseModel):
    """Medical records received from provider. Name is set explicitly (not auto-generated)."""
    received_date: Optional[date] = Field(default=None, description="Date records received")
    date_range_start: Optional[date] = Field(default=None, description="Records cover from this date")
    date_range_end: Optional[date] = Field(default=None, description="Records cover to this date")
    pages: Optional[int] = Field(default=None, description="Number of pages")
    format: Optional[str] = Field(default=None, description="Format: pdf, paper, cd, electronic")
    provider_name: Optional[str] = Field(default=None, description="Provider who sent records")


class MedicalBills(BaseModel):
    """Medical bills received from provider. Name is set explicitly (not auto-generated)."""
    received_date: Optional[date] = Field(default=None, description="Date bills received")
    total_billed: Optional[float] = Field(default=None, description="Total amount billed")
    provider_name: Optional[str] = Field(default=None, description="Provider who billed")
    bill_ids: Optional[str] = Field(default=None, description="Associated Bill entity IDs (JSON list)")


class MedicalRecordsRequest(BaseModel):
    """Outgoing medical records request. Name is set explicitly (not auto-generated)."""
    sent_date: Optional[date] = Field(default=None, description="Date request sent")
    request_number: Optional[int] = Field(default=None, description="Request number: 1 (initial), 2 (follow-up), etc.")
    via: Optional[str] = Field(default=None, description="Method: email, fax, mail, chartswap, nextrequest")
    response_deadline: Optional[date] = Field(default=None, description="Expected response date")
    provider_name: Optional[str] = Field(default=None, description="Provider request sent to")


class LetterOfRepresentation(BaseModel):
    """Letter of representation sent to insurer or provider. Name is set explicitly (not auto-generated)."""
    sent_date: Optional[date] = Field(default=None, description="Date letter sent")
    sent_to_name: Optional[str] = Field(default=None, description="Entity name (insurer/provider)")
    sent_to_type: Optional[str] = Field(default=None, description="Entity type: insurer, medical_provider, lienholder")
    acknowledged: Optional[bool] = Field(default=None, description="Whether acknowledgement received")
    acknowledged_date: Optional[date] = Field(default=None, description="Date acknowledgement received")


class InsuranceDocument(BaseModel):
    """Insurance-related document. Name is set explicitly (not auto-generated)."""
    doc_subtype: Optional[str] = Field(default=None, description="Type: dec_page, eob, denial_letter, coverage_letter, policy")
    received_date: Optional[date] = Field(default=None, description="Date received")
    insurer_name: Optional[str] = Field(default=None, description="Insurance company")


class CorrespondenceDocument(BaseModel):
    """General correspondence. Name is set explicitly (not auto-generated)."""
    correspondence_type: Optional[str] = Field(default=None, description="Type: email, letter, fax, text")
    direction: Optional[str] = Field(default=None, description="Direction: inbound, outbound")
    from_entity: Optional[str] = Field(default=None, description="Sender name")
    to_entity: Optional[str] = Field(default=None, description="Recipient name")
    sent_date: Optional[date] = Field(default=None, description="Date sent/received")


# --- Legal/Litigation Entities ---

class LawFirm(BaseModel):
    """A law firm. Name is set explicitly (not auto-generated)."""
    phone: Optional[str] = Field(default=None, description="Main phone number")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Main office address")
    website: Optional[str] = Field(default=None, description="Firm website")


class LawFirmOffice(BaseModel):
    """Specific office/branch of a law firm. Similar to Location for medical providers. Name is set explicitly."""
    office_name: str = Field(description="Office identifier (e.g., 'Louisville Office', 'Lexington Office')")
    parent_firm: str = Field(description="Parent law firm name")

    # Address
    address: str = Field(description="Office address - REQUIRED")
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

    # Contact
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None

    # Office details
    office_type: Optional[str] = Field(default=None, description="main | branch | satellite")

    # Metadata
    source: Optional[str] = None
    validation_state: Optional[str] = None


class Attorney(BaseModel):
    """An attorney on a case. Name is set explicitly (not auto-generated)."""
    role: Optional[str] = Field(default=None, description="Role: plaintiff_counsel, defense_counsel, co_counsel, referring_attorney")
    bar_number: Optional[str] = Field(default=None, description="State bar number")
    firm_name: Optional[str] = Field(default=None, description="Law firm name")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")

    # Additional professional details
    practice_areas: Optional[str] = Field(default=None, description="Practice areas (comma-separated or list)")
    bar_admission_date: Optional[date] = Field(default=None, description="Date admitted to bar")
    bar_states: Optional[str] = Field(default=None, description="States where licensed (comma-separated)")
    office_address: Optional[str] = Field(default=None, description="Attorney's office address (may differ from firm main office)")
    direct_phone: Optional[str] = Field(default=None, description="Direct dial number (vs firm main number)")
    preferred_contact: Optional[str] = Field(default=None, description="email | phone | text | fax")


class CaseManager(BaseModel):
    """Law firm case manager or paralegal. Name is set explicitly."""
    role: Optional[str] = Field(default=None, description="Role: case_manager, paralegal, legal_assistant")
    firm_name: Optional[str] = Field(default=None, description="Law firm name")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")


class Court(BaseModel):
    """A court where a case is filed. Name is set explicitly (not auto-generated)."""
    county: Optional[str] = Field(default=None, description="County")
    state: Optional[str] = Field(default=None, description="State")
    case_number: Optional[str] = Field(default=None, description="Court case number")
    division: Optional[str] = Field(default=None, description="Division: civil, circuit, district, etc.")
    phone: Optional[str] = Field(default=None, description="Court clerk phone number")
    email: Optional[str] = Field(default=None, description="Court clerk email")
    address: Optional[str] = Field(default=None, description="Court mailing address")


class CircuitDivision(BaseModel):
    """Circuit court division. Name format: 'County Circuit Court, Division II'. Connected to Court via PART_OF, Judge via PRESIDES_OVER."""
    division_number: Optional[str] = Field(default=None, description="Division number: 01, 02, etc.")
    court_name: Optional[str] = Field(default=None, description="Parent court name")
    circuit_number: Optional[str] = Field(default=None, description="Circuit number: 30, 18, etc.")
    local_rules: Optional[str] = Field(default=None, description="Division-specific local rules")
    scheduling_preferences: Optional[str] = Field(default=None, description="Judge's scheduling preferences")
    mediation_required: Optional[bool] = Field(default=None, description="Whether mediation is required before trial")


class DistrictDivision(BaseModel):
    """District court division. Name format: 'County District Court, Division 1'. Connected to Court via PART_OF, Judge via PRESIDES_OVER."""
    division_number: Optional[str] = Field(default=None, description="Division number: 01, 02, etc.")
    court_name: Optional[str] = Field(default=None, description="Parent court name")
    district_number: Optional[str] = Field(default=None, description="District number: 30, 18, etc.")


class AppellateDistrict(BaseModel):
    """Court of Appeals district. Connected to Court of Appeals via PART_OF, Judge via PRESIDES_OVER."""
    district_number: Optional[str] = Field(default=None, description="Appellate district number")
    region: Optional[str] = Field(default=None, description="Geographic region served")
    counties: Optional[str] = Field(default=None, description="Counties in district")


class SupremeCourtDistrict(BaseModel):
    """Kentucky Supreme Court district. Justices are elected from districts. Connected to Supreme Court via PART_OF, Justice via PRESIDES_OVER."""
    district_number: Optional[str] = Field(default=None, description="Supreme Court district number (1-7)")
    counties: Optional[str] = Field(default=None, description="Counties in district")
    region: Optional[str] = Field(default=None, description="Geographic region")


class CircuitJudge(BaseModel):
    """Circuit court judge. Name is set explicitly (not auto-generated). Connected to Court via PRESIDES_OVER."""
    county: Optional[str] = Field(default=None, description="County or multi-county area served")
    circuit: Optional[str] = Field(default=None, description="Circuit number (e.g., Cir. 18, Div. 01)")
    division: Optional[str] = Field(default=None, description="Division number")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    address: Optional[str] = Field(default=None, description="Chambers address")


class DistrictJudge(BaseModel):
    """District court judge. Name is set explicitly (not auto-generated). Connected to Court via PRESIDES_OVER."""
    county: Optional[str] = Field(default=None, description="County or multi-county area served")
    district: Optional[str] = Field(default=None, description="District number (e.g., Dist. 18, Div. 01)")
    division: Optional[str] = Field(default=None, description="Division number")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    address: Optional[str] = Field(default=None, description="Chambers address")


class AppellateJudge(BaseModel):
    """Court of Appeals judge. Name is set explicitly (not auto-generated)."""
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    address: Optional[str] = Field(default=None, description="Chambers address")


class SupremeCourtJustice(BaseModel):
    """Kentucky Supreme Court justice. Name is set explicitly (not auto-generated)."""
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    address: Optional[str] = Field(default=None, description="Chambers address")


class CourtClerk(BaseModel):
    """Circuit or district court clerk. Name is set explicitly (not auto-generated). Connected to Court via WORKS_AT."""
    clerk_type: Optional[str] = Field(default=None, description="Type: circuit, district")
    county: Optional[str] = Field(default=None, description="County served")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    address: Optional[str] = Field(default=None, description="Office address")


class MasterCommissioner(BaseModel):
    """Court-appointed master commissioner. Name is set explicitly (not auto-generated). Connected to Court via APPOINTED_BY."""
    county: Optional[str] = Field(default=None, description="County served")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    address: Optional[str] = Field(default=None, description="Office address")


class CourtAdministrator(BaseModel):
    """Court administrator or staff. Name is set explicitly (not auto-generated). Connected to Court via WORKS_AT."""
    role: Optional[str] = Field(default=None, description="Specific role or title")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    address: Optional[str] = Field(default=None, description="Office address")


class Pleading(BaseModel):
    """A litigation pleading or court filing. Name is set explicitly (not auto-generated) (title)."""
    pleading_type: Optional[str] = Field(default=None, description="Type: complaint, answer, motion, discovery_request, discovery_response, subpoena, order, judgment")
    filed_date: Optional[date] = Field(default=None, description="Date filed")
    due_date: Optional[date] = Field(default=None, description="Response due date if applicable")
    filed_by: Optional[str] = Field(default=None, description="Who filed it: plaintiff, defendant")

    # Discovery-specific fields (if pleading_type is discovery)
    discovery_type: Optional[str] = Field(default=None, description="interrogatories | rfp | rfa | deposition_notice | subpoena (if pleading_type is discovery)")
    propounded_to: Optional[str] = Field(default=None, description="plaintiff | defendant | third_party")
    response_due: Optional[date] = Field(default=None, description="When discovery response is due")
    response_received: Optional[bool] = Field(default=None, description="Whether response has been received")
    response_date: Optional[date] = Field(default=None, description="Date response was received")


class CourtEvent(BaseModel):
    """Court hearing, trial, mediation, or other scheduled event. Name is set explicitly (event description)."""
    event_type: str = Field(description="hearing | trial | mediation | status_conference | pretrial | motion_hearing | deposition | docket_call")
    event_date: date = Field(description="Date of event - REQUIRED")
    event_time: Optional[str] = Field(default=None, description="Time of event (e.g., '9:00 AM', '2:00 PM')")

    # Location
    location: Optional[str] = Field(default=None, description="Courtroom number or location (e.g., 'Courtroom 5A', 'Zoom', 'Mediator Office')")
    virtual: Optional[bool] = Field(default=None, description="Whether event is virtual/remote")

    # Event details
    purpose: Optional[str] = Field(default=None, description="Purpose or subject of event")
    outcome: Optional[str] = Field(default=None, description="Outcome: continued, heard, settled, dismissed, granted, denied")
    continued_to: Optional[date] = Field(default=None, description="If continued, new event date")

    # Metadata
    notes: Optional[str] = Field(default=None, description="Free-form notes about event")
    source: Optional[str] = Field(default=None, description="calendar | court_notice | case_data")


# --- Vendor Entities ---

class Expert(BaseModel):
    """An expert witness (vocational, medical, accident reconstruction, life care planner, etc.). Name is set explicitly (not auto-generated)."""
    expert_type: Optional[str] = Field(default=None, description="Type: vocational, medical, accident_reconstruction, life_care_planner, economist, engineering, biomechanics, other")
    credentials: Optional[str] = Field(default=None, description="Professional credentials")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    firm_name: Optional[str] = Field(default=None, description="Expert firm/organization if applicable")
    hourly_rate: Optional[float] = Field(default=None, description="Hourly rate for services")


class Mediator(BaseModel):
    """A mediator or arbitrator. Name is set explicitly (not auto-generated)."""
    credentials: Optional[str] = Field(default=None, description="Credentials: Retired Judge, Esq., etc.")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    firm_name: Optional[str] = Field(default=None, description="Mediation service organization if applicable")
    hourly_rate: Optional[float] = Field(default=None, description="Hourly rate for mediation services")


class Witness(BaseModel):
    """A fact witness (not expert). Name is set explicitly (not auto-generated)."""
    witness_type: Optional[str] = Field(default=None, description="Type: eyewitness, scene_witness, character_witness, treating_witness, other")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    address: Optional[str] = Field(default=None, description="Address")
    relationship_to_case: Optional[str] = Field(default=None, description="How they relate to case: bystander, passenger, coworker, etc.")


class Vendor(BaseModel):
    """A vendor/service provider used in case management (non-professional services). Name is set explicitly (not auto-generated)."""
    vendor_type: Optional[str] = Field(default=None, description="Type: towing, court_reporting, investigation, moving, records_retrieval, process_server, litigation_funding, medical_equipment, claims_services, legal_software, other")
    phone: Optional[str] = Field(default=None, description="Phone number")
    email: Optional[str] = Field(default=None, description="Email address")
    fax: Optional[str] = Field(default=None, description="Fax number")
    address: Optional[str] = Field(default=None, description="Address")


# --- Financial Entities ---

class Expense(BaseModel):
    """A case expense. Name is set explicitly (not auto-generated) (description)."""
    amount: Optional[float] = Field(default=None, description="Amount in dollars")
    expense_date: Optional[date] = Field(default=None, description="Date of expense")
    category: Optional[str] = Field(default=None, description="Category: filing_fee, service_fee, medical_records, expert, travel, other")
    vendor: Optional[str] = Field(default=None, description="Vendor/payee name")


class Bill(BaseModel):
    """Medical bill or other bill (different from lien). Name is set explicitly (not auto-generated)."""
    bill_type: Optional[str] = Field(default=None, description="Type: medical, legal_fee, expert_fee, filing_fee, vendor, other")
    amount: Optional[float] = Field(default=None, description="Billed amount")
    bill_date: Optional[date] = Field(default=None, description="Date of bill")
    due_date: Optional[date] = Field(default=None, description="Payment due date")
    paid_date: Optional[date] = Field(default=None, description="Date paid")
    paid_amount: Optional[float] = Field(default=None, description="Amount actually paid")
    balance: Optional[float] = Field(default=None, description="Outstanding balance")
    provider_name: Optional[str] = Field(default=None, description="Who sent the bill")


class MedicalVisit(BaseModel):
    """Individual medical visit/appointment on specific date. Each visit date separated into its own PDF in medical chronology. Name is set explicitly (not auto-generated)."""
    visit_date: date = Field(description="Date of visit - REQUIRED for chronology ordering")

    # CRITICAL for lien negotiations - determines if bill should be repaid
    related_to_injury: bool = Field(default=True, description="Whether visit is related to case injury (vs unrelated like cold, routine checkup)")
    unrelated_reason: Optional[str] = Field(default=None, description="If unrelated, explain why (e.g., 'upper respiratory infection', 'annual physical', 'pre-existing condition')")

    # Visit details
    diagnosis: Optional[str] = Field(default=None, description="Diagnosis or chief complaint for this visit")
    treatment_type: Optional[str] = Field(default=None, description="Type: ER, surgery, follow-up, imaging, physical_therapy, chiropractic, etc.")
    visit_number: Optional[int] = Field(default=None, description="Sequential visit number in treatment timeline")

    # Provider info (redundant with relationships but helpful for queries)
    provider_name: Optional[str] = Field(default=None, description="Where patient was seen (Location or Facility name)")
    doctor_name: Optional[str] = Field(default=None, description="Doctor who saw patient")

    # Notes and metadata
    notes: Optional[str] = Field(default=None, description="Free-form paralegal notes about visit")
    duration_minutes: Optional[int] = Field(default=None, description="Visit duration if known")

    # Source tracking
    source: Optional[str] = Field(default=None, description="medical_records | case_notes | episode")
    validation_state: Optional[str] = Field(default=None, description="verified | unverified | needs_review")


class Negotiation(BaseModel):
    """Active settlement negotiation with insurer (before final settlement). Name is set explicitly (not auto-generated)."""
    claim_type: Optional[str] = Field(default=None, description="Which claim type: PIP, BI, UM, UIM, WC")
    demand_amount: Optional[float] = Field(default=None, description="Initial demand amount")
    demand_sent_date: Optional[date] = Field(default=None, description="Date demand sent")
    current_offer: Optional[float] = Field(default=None, description="Latest offer from insurer")
    offer_date: Optional[date] = Field(default=None, description="Date of latest offer")
    counter_offer: Optional[float] = Field(default=None, description="Our counter-offer")
    counter_date: Optional[date] = Field(default=None, description="Date of counter-offer")
    is_active: Optional[bool] = Field(default=None, description="Whether negotiation is ongoing")
    final_amount: Optional[float] = Field(default=None, description="Final agreed amount if settled")
    settled_date: Optional[date] = Field(default=None, description="Date agreement reached")


class Settlement(BaseModel):
    """Final settlement breakdown for a resolved case. Name is set explicitly (not auto-generated)."""
    gross_amount: Optional[float] = Field(default=None, description="Gross settlement amount")
    attorney_fee: Optional[float] = Field(default=None, description="Attorney fee amount")
    expenses_total: Optional[float] = Field(default=None, description="Total case expenses")
    liens_total: Optional[float] = Field(default=None, description="Total liens paid")
    net_to_client: Optional[float] = Field(default=None, description="Net amount to client")
    settlement_date: Optional[date] = Field(default=None, description="Date of settlement")


class Episode(BaseModel):
    """
    A note/communication/event in the case timeline (the 'why/how' narrative).

    Episodes explain WHY things happened and HOW they were accomplished.
    The graph structure (Case, Provider, Insurance) represents WHAT currently exists.

    Examples:
    - "Called State Farm to confirm coverage - adjuster unavailable"
    - "Sent medical records request to UK Hospital via fax"
    - "Client reported new pain symptoms, referred to orthopedic specialist"

    Episodes link to entities they discuss (ABOUT relationships) and to other
    related episodes (FOLLOWS relationships for sequential/topical grouping).
    """
    content: str = Field(description="Natural language narrative (LLM-converted for readability and semantic search)")
    valid_at: datetime = Field(description="When episode occurred (timestamp)")
    invalid_at: Optional[datetime] = Field(default=None, description="When info became outdated (usually null)")
    author: str = Field(description="Who created: agent, user, or staff name")
    episode_type: str = Field(description="Type: call, email, fax, meeting, document, internal_note, etc.")
    case_name: str = Field(description="Case this episode belongs to (required - no orphan episodes)")
    source_description: Optional[str] = Field(default=None, description="Original source if imported from legacy system")
    embedding: Optional[list[float]] = Field(default=None, description="Semantic embedding (enriched with entity context)")


# =============================================================================
# Workflow Definition Entities
# =============================================================================
# These entities represent the workflow structure itself, not case data.
# They are ingested once from workflow_engine/ and workflows/ folders.
# NOTE: 'name' is a protected Graphiti attribute - do NOT include it.

class Phase(BaseModel):
    """A case lifecycle phase (e.g., file_setup, treatment, negotiation). Name is set explicitly."""
    display_name: Optional[str] = Field(default=None, description="Human-readable phase name")
    description: Optional[str] = Field(default=None, description="Description of the phase")
    order: Optional[int] = Field(default=None, description="Phase order in lifecycle (0-8)")
    track: Optional[str] = Field(default=None, description="Track: pre_litigation, litigation, settlement, closed")
    next_phase: Optional[str] = Field(default=None, description="Default next phase name")


class SubPhase(BaseModel):
    """A sub-phase within litigation (e.g., complaint, discovery, trial). Name is set explicitly."""
    display_name: Optional[str] = Field(default=None, description="Human-readable sub-phase name")
    parent_phase: Optional[str] = Field(default=None, description="Parent phase name (litigation)")
    order: Optional[int] = Field(default=None, description="Sub-phase order (1-5)")
    description: Optional[str] = Field(default=None, description="Description of the sub-phase")


class Landmark(BaseModel):
    """A checkpoint within a phase that must be verified before advancing. Name is set explicitly."""
    # Basic info
    landmark_id: Optional[str] = Field(default=None, description="Unique landmark identifier (e.g., 'retainer_signed')")
    display_name: Optional[str] = Field(default=None, description="Human-readable name")
    phase: Optional[str] = Field(default=None, description="Phase this landmark belongs to")
    subphase: Optional[str] = Field(default=None, description="SubPhase this landmark belongs to (for litigation landmarks)")
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
    """A workflow definition within a phase. Name is set explicitly."""
    display_name: Optional[str] = Field(default=None, description="Human-readable workflow name")
    phase: Optional[str] = Field(default=None, description="Phase this workflow belongs to")
    subphase: Optional[str] = Field(default=None, description="SubPhase this workflow belongs to (for litigation workflows)")
    description: Optional[str] = Field(default=None, description="What this workflow accomplishes")
    trigger: Optional[str] = Field(default=None, description="When this workflow is triggered")
    prerequisites: Optional[str] = Field(default=None, description="What must be complete before starting")
    instructions_path: Optional[str] = Field(default=None, description="Path to workflow.md with detailed instructions")


class WorkflowStep(BaseModel):
    """A step within a workflow. Name is set explicitly."""
    step_id: Optional[str] = Field(default=None, description="Step identifier within workflow")
    workflow: Optional[str] = Field(default=None, description="Parent workflow name")
    description: Optional[str] = Field(default=None, description="What this step does")
    owner: Optional[str] = Field(default=None, description="Who executes: 'agent' or 'user'")
    can_automate: Optional[bool] = Field(default=None, description="Whether agent can execute without user")
    prompt_user: Optional[str] = Field(default=None, description="Question to ask user if needed")
    completion_check: Optional[str] = Field(default=None, description="Condition to verify step completion")
    order: Optional[int] = Field(default=None, description="Step order within workflow")


class WorkflowChecklist(BaseModel):
    """A procedural checklist for completing a task. Name is set explicitly."""
    path: Optional[str] = Field(default=None, description="Path to checklist file")
    when_to_use: Optional[str] = Field(default=None, description="When to use this checklist")
    related_workflow: Optional[str] = Field(default=None, description="Associated workflow name")


class WorkflowSkill(BaseModel):
    """An agent skill that can be used in workflows. Name is set explicitly."""
    path: Optional[str] = Field(default=None, description="Path to skill.md file")
    description: Optional[str] = Field(default=None, description="What this skill does")
    capabilities: Optional[str] = Field(default=None, description="List of capabilities")
    agent_ready: Optional[bool] = Field(default=None, description="Whether skill is ready for agent use")
    quality_score: Optional[float] = Field(default=None, description="Quality score 0-5")


class WorkflowTemplate(BaseModel):
    """A document template used in workflows. Name is set explicitly."""
    path: Optional[str] = Field(default=None, description="Path to template file")
    purpose: Optional[str] = Field(default=None, description="What this template is for")
    file_type: Optional[str] = Field(default=None, description="File type: docx, pdf, md")
    placeholders: Optional[str] = Field(default=None, description="Placeholder fields in template")


class WorkflowTool(BaseModel):
    """A Python tool used in workflows. Name is set explicitly."""
    path: Optional[str] = Field(default=None, description="Path to Python script")
    purpose: Optional[str] = Field(default=None, description="What this tool does")


class LandmarkStatus(BaseModel):
    """Tracks completion status of a landmark for a specific case. Name is set explicitly."""
    case_name: Optional[str] = Field(default=None, description="Case this status belongs to")
    landmark_id: Optional[str] = Field(default=None, description="Landmark this status tracks")
    status: Optional[str] = Field(default=None, description="Status: complete, incomplete, in_progress, not_started, not_applicable")
    sub_steps: Optional[str] = Field(default=None, description="JSON dict tracking sub-step completion for composite landmarks")
    notes: Optional[str] = Field(default=None, description="Notes about current status or blockers")
    completed_at: Optional[datetime] = Field(default=None, description="When landmark was completed")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    updated_by: Optional[str] = Field(default=None, description="Who updated: agent, user, system")
    version: Optional[int] = Field(default=None, description="Version number for audit trail")
    archived_at: Optional[datetime] = Field(default=None, description="When this version was superseded")


# =============================================================================
# All Entity Types for Graphiti
# =============================================================================

ENTITY_TYPES = [
    # Core case entities
    Case,
    Client,
    Defendant,       # At-fault party
    Episode,         # Timeline narrative (why/how documentation) - replaces Note
    Organization,    # Generic organizations
    Community,       # Groups of related entities (Graphiti-inspired)
    # Insurance claim types (each is distinct)
    PIPClaim,        # Personal Injury Protection - first-party no-fault
    BIClaim,         # Bodily Injury - third-party liability
    UMClaim,         # Uninsured Motorist
    UIMClaim,        # Underinsured Motorist
    WCClaim,         # Workers Compensation
    MedPayClaim,     # Medical Payments coverage
    Insurer,         # Insurance company
    Adjuster,        # Insurance adjuster
    InsurancePolicy, # Insurance policy providing coverage - NEW
    InsurancePayment,# Individual payment from insurer - NEW
    # Medical entities
    HealthSystem,    # Parent healthcare organization (UofL Health, Norton Healthcare, etc.)
    Facility,        # Treatment facility/program (Norton Orthopedic Institute) - NEW
    Location,        # Specific physical location with address - NEW
    MedicalProvider, # DEPRECATED - being replaced by Facility/Location structure
    Doctor,          # Individual physician (WORKS_AT -> Location)
    Lien,
    LienHolder,      # Entity holding a lien
    # Document tracking
    Document,        # Generic document
    MedicalRecords,  # Received medical records
    MedicalBills,    # Received medical bills
    MedicalRecordsRequest,  # Outgoing records request
    LetterOfRepresentation,  # Letter of rep sent
    InsuranceDocument,  # Insurance docs (dec pages, EOBs, etc.)
    CorrespondenceDocument,  # General correspondence
    # Legal/litigation entities
    LawFirm,
    LawFirmOffice,   # Specific office/branch of law firm - NEW
    Attorney,
    CaseManager,     # Law firm case managers and paralegals
    Court,
    CircuitDivision,  # Circuit court divisions (PART_OF -> Court)
    DistrictDivision, # District court divisions (PART_OF -> Court)
    AppellateDistrict, # Court of Appeals districts (PART_OF -> Court of Appeals)
    SupremeCourtDistrict, # Supreme Court districts (PART_OF -> Supreme Court)
    CircuitJudge,    # Circuit court judges (PRESIDES_OVER -> CircuitDivision)
    DistrictJudge,   # District court judges (PRESIDES_OVER -> DistrictDivision)
    AppellateJudge,  # Court of Appeals judges (PRESIDES_OVER -> AppellateDistrict)
    SupremeCourtJustice,  # Kentucky Supreme Court justices (PRESIDES_OVER -> SupremeCourtDistrict)
    CourtClerk,      # Circuit/district court clerks (WORKS_AT -> Court)
    MasterCommissioner,  # Court-appointed master commissioners (APPOINTED_BY -> Court)
    CourtAdministrator,  # Court administrators (WORKS_AT -> Court)
    Pleading,
    CourtEvent,      # Court hearings, trials, mediations, conferences - NEW
    # Professional services / Expert witnesses
    Expert,          # Expert witness (WORKS_AT -> Organization if applicable)
    Mediator,        # Mediator/arbitrator (WORKS_AT -> Organization if applicable)
    Witness,         # Fact witness (eyewitness, scene witness, etc.)
    Vendor,
    # Financial
    Bill,            # Medical bills and other bills (separate from liens)
    MedicalVisit,    # Individual medical visit/appointment by date (for chronology)
    Expense,         # Case expenses
    Negotiation,     # Active settlement negotiation process
    Settlement,      # Final settlement breakdown
    # Workflow definition entities (structural, not case data)
    Phase,
    SubPhase,         # Litigation sub-phases
    Landmark,
    WorkflowDef,
    WorkflowStep,
    WorkflowChecklist,
    WorkflowSkill,
    WorkflowTemplate,
    WorkflowTool,
    # Workflow state entities (case-specific state)
    LandmarkStatus,   # Tracks landmark completion per case
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


class RelatedAccident(BaseModel):
    """Links cases from the same accident/incident."""
    accident_date: Optional[date] = Field(default=None, description="Date of the shared accident")
    relationship_type: Optional[str] = Field(default=None, description="Type: same_incident, same_defendant, family_members")
    notes: Optional[str] = Field(default=None, description="Additional context about the relationship")


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


class HasStatus(BaseModel):
    """Case has a landmark status tracking node."""
    pass  # Status details are on the LandmarkStatus entity


class ForLandmark(BaseModel):
    """LandmarkStatus node tracks a specific Landmark."""
    pass  # Links status tracking node to its landmark definition


class HasSubPhase(BaseModel):
    """Phase has sub-phases (used for litigation phase breakdown)."""
    order: Optional[int] = Field(default=None, description="SubPhase order within parent phase")


class UsesTemplate(BaseModel):
    """Workflow uses a document template."""
    template_type: Optional[str] = Field(default=None, description="Type: letter, form, pleading, agreement")


class About(BaseModel):
    """Episode discusses/references an entity (provider, claim, attorney, etc.)."""
    relevance: Optional[str] = Field(default=None, description="How entity relates to episode content")
    extracted_method: Optional[str] = Field(default=None, description="How link was determined: llm_extraction, manual, semantic_match")


class Follows(BaseModel):
    """Episode follows another episode (sequential or topically related)."""
    relationship_type: Optional[str] = Field(default="sequential", description="Type: sequential, same_topic, same_workflow")
    similarity_score: Optional[float] = Field(default=None, description="Semantic similarity score if auto-linked")


class PartOfWorkflow(BaseModel):
    """Episode is part of workflow execution."""
    step_id: Optional[str] = Field(default=None, description="Which workflow step this episode documents")
    workflow_name: Optional[str] = Field(default=None, description="Workflow name")


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
    "HasStatus": HasStatus,
    "ForLandmark": ForLandmark,
    # Workflow structure relationships
    "BelongsToPhase": BelongsToPhase,
    "HasLandmark": HasLandmark,
    "HasSubLandmark": HasSubLandmark,
    "HasSubPhase": HasSubPhase,
    "AchievedBy": AchievedBy,
    "Achieves": Achieves,
    "DefinedInPhase": DefinedInPhase,
    "HasWorkflow": HasWorkflow,
    "HasStep": HasStep,
    "StepOf": StepOf,
    "NextPhase": NextPhase,
    "CanSkipTo": CanSkipTo,
    "UsesTemplate": UsesTemplate,
    # Note relationships
    "HasNote": HasNote,
    "NotedOn": NotedOn,
    # Episode relationships (timeline narrative)
    "About": About,
    "Follows": Follows,
    "PartOfWorkflow": PartOfWorkflow,
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
    # Case to Case (related accidents)
    ("Case", "Case"): ["RelatedAccident"],

    # =========================================================================
    # Client relationships (bidirectional where needed)
    # =========================================================================
    ("Client", "Case"): ["PlaintiffIn"],
    ("Client", "MedicalProvider"): ["TreatingAt"],
    
    # =========================================================================
    # Facility and Location relationships (NEW - 3-tier hierarchy)
    # =========================================================================
    # Hierarchy relationships
    ("Location", "Facility"): ["PartOf"],
    ("Facility", "HealthSystem"): ["PartOf"],
    ("Facility", "Location"): ["HasLocation"],      # Reverse for convenience
    ("HealthSystem", "Facility"): ["HasFacility"],  # Reverse for convenience

    # Treatment relationships (multi-level - can link to Facility OR Location)
    ("Client", "Location"): ["TreatedAt"],   # Specific location known
    ("Client", "Facility"): ["TreatedAt"],   # Location unknown, link to facility
    ("Case", "Location"): ["TreatingAt"],
    ("Case", "Facility"): ["TreatingAt"],

    # Multi-role relationships (same entity, different roles)
    ("Case", "Location"): ["Defendant", "VendorFor", "TreatingAt"],  # Location can be provider, defendant, or vendor
    ("Case", "Facility"): ["Defendant", "VendorFor", "TreatingAt"],  # Facility can be provider, defendant, or vendor
    ("Case", "HealthSystem"): ["Defendant"],  # Rare but possible (suing entire system)

    # Staff relationships
    ("Doctor", "Location"): ["WorksAt"],           # Doctor works at specific location
    ("Doctor", "Facility"): ["AffiliatedWith"],    # Doctor affiliated with facility (multiple locations)

    # Document relationships
    ("Document", "Location"): ["From"],
    ("Document", "Facility"): ["From"],

    # =========================================================================
    # Medical Provider relationships (DEPRECATED - use Facility/Location instead)
    # =========================================================================
    ("MedicalProvider", "Client"): ["HasTreated"],  # Provider treated client
    ("Client", "MedicalProvider"): ["TreatedBy"],   # Client treated by provider
    ("Case", "MedicalProvider"): ["TreatingAt"],    # Case involves treatment at provider

    # =========================================================================
    # Doctor relationships (UPDATED to use Location)
    # =========================================================================
    ("Doctor", "Location"): ["WorksAt"],         # Doctor works at specific location (NEW)
    ("Doctor", "Facility"): ["AffiliatedWith"],  # Doctor affiliated with facility (NEW)
    ("Doctor", "MedicalProvider"): ["WorksAt"],  # DEPRECATED - use Location instead
    ("Doctor", "Client"): ["HasTreated"],        # Doctor treated client
    ("Client", "Doctor"): ["TreatedBy"],         # Client treated by doctor
    
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
    # Client to insurance/claims
    ("Client", "Insurer"): ["HasInsurance"],  # Client has insurance policy with
    ("Client", "PIPClaim"): ["FiledClaim"],   # Client filed this claim
    ("Client", "BIClaim"): ["FiledClaim"],
    ("Client", "UMClaim"): ["FiledClaim"],
    ("Client", "UIMClaim"): ["FiledClaim"],
    ("Client", "WCClaim"): ["FiledClaim"],
    # Claims cover client (bidirectional)
    ("PIPClaim", "Client"): ["Covers"],
    ("BIClaim", "Client"): ["Covers"],
    ("UMClaim", "Client"): ["Covers"],
    ("UIMClaim", "Client"): ["Covers"],
    ("WCClaim", "Client"): ["Covers"],
    
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
    # Insurance Policy relationships (NEW)
    # =========================================================================
    ("Client", "InsurancePolicy"): ["HasPolicy"],
    ("Defendant", "InsurancePolicy"): ["HasPolicy"],
    ("InsurancePolicy", "Insurer"): ["WithInsurer"],
    ("PIPClaim", "InsurancePolicy"): ["UnderPolicy"],
    ("BIClaim", "InsurancePolicy"): ["UnderPolicy"],
    ("UMClaim", "InsurancePolicy"): ["UnderPolicy"],
    ("UIMClaim", "InsurancePolicy"): ["UnderPolicy"],
    ("WCClaim", "InsurancePolicy"): ["UnderPolicy"],
    ("MedPayClaim", "InsurancePolicy"): ["UnderPolicy"],

    # =========================================================================
    # Insurance Payment relationships (NEW)
    # =========================================================================
    ("PIPClaim", "InsurancePayment"): ["MadePayment"],
    ("BIClaim", "InsurancePayment"): ["MadePayment"],
    ("UMClaim", "InsurancePayment"): ["MadePayment"],
    ("UIMClaim", "InsurancePayment"): ["MadePayment"],
    ("WCClaim", "InsurancePayment"): ["MadePayment"],
    ("InsurancePayment", "Insurer"): ["From"],
    ("InsurancePayment", "Bill"): ["PaidBill"],

    # =========================================================================
    # Defendant Insurance relationships (NEW)
    # =========================================================================
    ("Defendant", "Insurer"): ["HasInsurance"],
    ("BIClaim", "Defendant"): ["CoversDefendant"],

    # =========================================================================
    # Lien and Bill relationships
    # =========================================================================
    ("Case", "Lien"): ["HasLien"],  # Case has lien
    ("Case", "LienHolder"): ["HasLienFrom"],  # Case has lien from holder
    ("Lien", "LienHolder"): ["HeldBy"],  # Lien held by lienholder (kept for now)
    ("Lien", "Bill"): ["ForBill"],   # Lien is for specific bill
    ("Lien", "Bill"): ["PaidBill"],  # Lien holder paid this bill (for tracking what they paid)
    # Bills
    ("Case", "Bill"): ["HasBill"],  # Case has bill
    ("Bill", "Location"): ["BilledBy"],      # Bill from specific location (NEW)
    ("Bill", "Facility"): ["BilledBy"],      # Bill from facility (NEW)
    ("Bill", "MedicalProvider"): ["BilledBy"],  # Bill from provider (DEPRECATED)
    ("Bill", "Vendor"): ["BilledBy"],  # Bill from vendor
    ("Bill", "Attorney"): ["BilledBy"],  # Bill from attorney/expert

    # =========================================================================
    # Medical Visit relationships (NEW - for medical chronology)
    # =========================================================================
    ("Case", "MedicalVisit"): ["HasVisit"],           # Case has visit
    ("MedicalVisit", "Location"): ["AtLocation"],     # Visit at specific location
    ("MedicalVisit", "Facility"): ["AtLocation"],     # Visit at facility (location unknown)
    ("MedicalVisit", "Bill"): ["HasBill"],            # Visit has associated bill(s)
    ("MedicalVisit", "Document"): ["HasDocument"],    # Visit has PDF of records
    ("MedicalVisit", "Doctor"): ["SeenBy"],           # Doctor who saw patient
    ("Client", "MedicalVisit"): ["Had"],              # Client had visit (optional - can infer from Case)

    # =========================================================================
    # Negotiation relationships
    # =========================================================================
    ("Case", "Negotiation"): ["HasNegotiation"],
    ("Negotiation", "PIPClaim"): ["ForClaim"],
    ("Negotiation", "BIClaim"): ["ForClaim"],
    ("Negotiation", "UMClaim"): ["ForClaim"],
    ("Negotiation", "UIMClaim"): ["ForClaim"],
    ("Negotiation", "WCClaim"): ["ForClaim"],

    # =========================================================================
    # Legal/litigation relationships
    # =========================================================================
    ("Attorney", "Case"): ["RepresentsClient"],
    ("Attorney", "LawFirm"): ["WorksAt"],
    ("Attorney", "LawFirmOffice"): ["WorksAt"],  # NEW - can work at specific office
    ("CaseManager", "LawFirm"): ["WorksAt"],
    ("CaseManager", "LawFirmOffice"): ["WorksAt"],  # NEW - can work at specific office
    ("LawFirmOffice", "LawFirm"): ["PartOf"],  # NEW - office belongs to firm
    ("Case", "Attorney"): ["DefenseCounsel", "RepresentedBy"],
    ("Pleading", "Case"): ["FiledFor"],
    ("Pleading", "Court"): ["FiledIn"],
    ("Pleading", "Attorney"): ["FiledBy"],  # NEW - who filed this pleading

    # =========================================================================
    # Court Event relationships (NEW)
    # =========================================================================
    ("Case", "CourtEvent"): ["HasEvent"],
    ("CourtEvent", "Court"): ["In"],
    ("CourtEvent", "CircuitDivision"): ["In"],
    ("CourtEvent", "DistrictDivision"): ["In"],

    # =========================================================================
    # Court Division relationships
    # =========================================================================
    ("CircuitDivision", "Court"): ["PartOf"],  # Division belongs to court
    ("DistrictDivision", "Court"): ["PartOf"],
    ("AppellateDistrict", "Court"): ["PartOf"],
    ("SupremeCourtDistrict", "Court"): ["PartOf"],

    # =========================================================================
    # Court Personnel relationships
    # =========================================================================
    ("CircuitJudge", "CircuitDivision"): ["PresidesOver"],  # Judge presides over division
    ("DistrictJudge", "DistrictDivision"): ["PresidesOver"],
    ("AppellateJudge", "AppellateDistrict"): ["PresidesOver"],
    ("SupremeCourtJustice", "SupremeCourtDistrict"): ["PresidesOver"],
    ("CourtClerk", "Court"): ["WorksAt"],  # Clerk works at court (not division-specific)
    ("MasterCommissioner", "Court"): ["AppointedBy"],  # Commissioner appointed by court
    ("CourtAdministrator", "Court"): ["WorksAt"],  # Administrator works at court
    ("Case", "CircuitDivision"): ["FiledIn"],  # Case filed in division
    ("Case", "DistrictDivision"): ["FiledIn"],
    ("Case", "CircuitJudge"): ["AssignedTo"],  # Case assigned to judge (via division)
    ("Case", "DistrictJudge"): ["AssignedTo"],

    # =========================================================================
    # Expert, Mediator, and Witness relationships
    # =========================================================================
    ("Expert", "Organization"): ["WorksAt"],  # Expert works for firm/organization
    ("Expert", "Case"): ["RetainedFor"],
    ("Mediator", "Organization"): ["WorksAt"],  # Mediator with mediation service
    ("Mediator", "Case"): ["RetainedFor"],
    ("Witness", "Case"): ["WitnessFor"],  # Fact witness for case
    ("Case", "Expert"): ["RetainedExpert"],
    ("Case", "Mediator"): ["RetainedMediator"],
    ("Case", "Witness"): ["HasWitness"],
    
    # =========================================================================
    # Organization relationships
    # =========================================================================
    ("Organization", "Organization"): ["PartOf"],  # Hierarchies
    ("MedicalProvider", "HealthSystem"): ["PartOf"],  # Specific location belongs to health system
    ("HealthSystem", "Organization"): ["PartOf"],  # Health system can be part of larger org
    ("LawFirm", "Organization"): ["PartOf"],

    # =========================================================================
    # Document relationships
    # =========================================================================
    ("Case", "Document"): ["HasDocument"],  # Generic documents
    ("Document", "Case"): ["Regarding"],
    # Specific document types
    ("MedicalRecords", "MedicalProvider"): ["ReceivedFrom"],
    ("MedicalBills", "MedicalProvider"): ["ReceivedFrom"],
    ("MedicalRecordsRequest", "MedicalProvider"): ["SentTo"],
    ("LetterOfRepresentation", "Insurer"): ["SentTo"],
    ("LetterOfRepresentation", "MedicalProvider"): ["SentTo"],
    ("LetterOfRepresentation", "LienHolder"): ["SentTo"],
    ("InsuranceDocument", "Insurer"): ["From"],
    ("Case", "MedicalRecords"): ["HasDocument"],
    ("Case", "MedicalBills"): ["HasDocument"],
    ("Case", "MedicalRecordsRequest"): ["HasDocument"],
    ("Case", "LetterOfRepresentation"): ["HasDocument"],
    ("Case", "InsuranceDocument"): ["HasDocument"],
    ("Case", "CorrespondenceDocument"): ["HasDocument"],

    # =========================================================================
    # Community relationships
    # =========================================================================
    ("Community", "MedicalProvider"): ["HasMember"],
    ("Community", "Doctor"): ["HasMember"],
    ("Community", "Attorney"): ["HasMember"],
    ("Community", "Case"): ["HasMember"],
    ("Community", "Defendant"): ["HasMember"],
    ("MedicalProvider", "Community"): ["MemberOf"],
    ("Doctor", "Community"): ["MemberOf"],
    ("Attorney", "Community"): ["MemberOf"],
    ("Case", "Community"): ["MemberOf"],
    ("Defendant", "Community"): ["MemberOf"],

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
    # Episode relationships (timeline narrative - explains why/how)
    # =========================================================================
    # Episodes always link to their Case
    ("Episode", "Case"): ["RelatesTo"],  # Generic for case link
    # Episodes can discuss (ABOUT) any entity
    ("Episode", "Client"): ["About"],
    ("Episode", "HealthSystem"): ["About"],  # Parent healthcare organization
    ("Episode", "MedicalProvider"): ["About"],  # Specific location
    ("Episode", "Doctor"): ["About"],  # Individual physicians
    ("Episode", "Insurer"): ["About"],
    ("Episode", "Adjuster"): ["About"],
    ("Episode", "PIPClaim"): ["About"],
    ("Episode", "BIClaim"): ["About"],
    ("Episode", "UMClaim"): ["About"],
    ("Episode", "UIMClaim"): ["About"],
    ("Episode", "WCClaim"): ["About"],
    ("Episode", "MedPayClaim"): ["About"],
    ("Episode", "Lien"): ["About"],
    ("Episode", "LienHolder"): ["About"],
    ("Episode", "Attorney"): ["About"],
    ("Episode", "CaseManager"): ["About"],
    ("Episode", "Court"): ["About"],
    ("Episode", "CircuitDivision"): ["About"],  # Court divisions
    ("Episode", "DistrictDivision"): ["About"],
    ("Episode", "AppellateDistrict"): ["About"],
    ("Episode", "SupremeCourtDistrict"): ["About"],
    ("Episode", "CircuitJudge"): ["About"],  # Judges
    ("Episode", "DistrictJudge"): ["About"],
    ("Episode", "AppellateJudge"): ["About"],
    ("Episode", "SupremeCourtJustice"): ["About"],
    ("Episode", "CourtClerk"): ["About"],  # Court personnel
    ("Episode", "MasterCommissioner"): ["About"],
    ("Episode", "CourtAdministrator"): ["About"],
    ("Episode", "Defendant"): ["About"],
    ("Episode", "Pleading"): ["About"],
    ("Episode", "Organization"): ["About"],
    ("Episode", "Expert"): ["About"],  # Expert witnesses
    ("Episode", "Mediator"): ["About"],  # Mediators/arbitrators
    ("Episode", "Witness"): ["About"],  # Fact witnesses
    ("Episode", "Vendor"): ["About"],
    # Financial entities
    ("Episode", "Bill"): ["About"],
    ("Episode", "Negotiation"): ["About"],
    ("Episode", "Settlement"): ["About"],
    # Document entities
    ("Episode", "MedicalRecords"): ["About"],
    ("Episode", "MedicalBills"): ["About"],
    ("Episode", "MedicalRecordsRequest"): ["About"],
    ("Episode", "LetterOfRepresentation"): ["About"],
    ("Episode", "InsuranceDocument"): ["About"],
    ("Episode", "CorrespondenceDocument"): ["About"],
    # Community
    ("Episode", "Community"): ["About"],
    # Episodes can follow other episodes (topical/sequential)
    ("Episode", "Episode"): ["Follows"],
    # Episodes can document workflow execution
    ("Episode", "WorkflowDef"): ["PartOfWorkflow"],

    # =========================================================================
    # Fallback for any entity pair not explicitly mapped
    # =========================================================================
    ("Entity", "Entity"): ["RelatesTo", "Mentions"],
}


# =============================================================================
async def run_cypher_query_direct(query: str, parameters: Optional[dict] = None) -> list:
    """
    Execute a raw Cypher query directly against FalkorDB (sync client, no Graphiti).

    This is a lightweight query function that bypasses Graphiti initialization,
    avoiding index building and event loop issues. Use for simple structural queries.

    Args:
        query: Cypher query string
        parameters: Optional query parameters (for parameterized queries)

    Returns:
        List of result records
    """
    from falkordb import FalkorDB

    # Direct FalkorDB connection (sync client)
    db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
    graph = db.select_graph("roscoe_graph")

    # Execute query (sync)
    result = graph.query(query, parameters or {})

    # Convert to list of dicts
    records = []
    if result.result_set:
        headers = [h[1] if isinstance(h, (list, tuple)) else str(h) for h in result.header]
        for row in result.result_set:
            record = {headers[i]: row[i] for i in range(len(headers))}
            records.append(record)

    return records


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
    # Use the direct query function to avoid Graphiti initialization
    return await run_cypher_query_direct(query, parameters)


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
    Get the current phase (and sub-phase if applicable) for a case.

    This returns the phase the case is currently in via IN_PHASE relationship,
    and SubPhase via IN_SUBPHASE relationship (for litigation cases).

    Args:
        case_name: Case name/identifier

    Returns:
        Dictionary with phase info: {name, display_name, order, track, entered_at, subphase_name, subphase_display}
        Returns None if case not found or no phase set.
    """
    query = """
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[r:IN_PHASE]->(p:Entity {entity_type: 'Phase'})
    OPTIONAL MATCH (c)-[sr:IN_SUBPHASE]->(sp:Entity {entity_type: 'SubPhase'})
    RETURN p.name as name,
           p.display_name as display_name,
           p.order as phase_order,
           p.track as track,
           p.next_phase as next_phase,
           r.entered_at as entered_at,
           sp.name as subphase_name,
           sp.display_name as subphase_display,
           sp.order as subphase_order,
           sr.entered_at as subphase_entered_at
    """
    results = await run_cypher_query(query, {"case_name": case_name})
    return results[0] if results else None


async def get_case_landmark_statuses(case_name: str, phase_name: str = None) -> list:
    """
    Get ALL landmark statuses for a case, including landmarks without status set.

    This returns ALL landmarks (from phase definitions), with their status if set,
    or "not_started" if no LANDMARK_STATUS relationship exists yet.

    Args:
        case_name: Case name/identifier
        phase_name: Optional - filter to landmarks for a specific phase

    Returns:
        List of ALL landmarks with:
        - landmark_id, display_name, landmark_type, is_hard_blocker
        - status (actual or "not_started"), sub_steps, notes, completed_at
    """
    if phase_name:
        # Get ALL landmarks for the phase, LEFT JOIN with status via LandmarkStatus nodes
        query = """
        MATCH (p:Entity {entity_type: 'Phase', name: $phase_name})-[:HAS_LANDMARK]->(l:Entity {entity_type: 'Landmark'})
        OPTIONAL MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[:HAS_STATUS]->(ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l)
        WHERE ls IS NULL OR ls.archived_at IS NULL
        RETURN l.landmark_id as landmark_id,
               l.name as display_name,
               l.phase as phase,
               l.landmark_type as landmark_type,
               l.is_hard_blocker as is_hard_blocker,
               l.can_override as can_override,
               l.sub_steps as landmark_sub_steps,
               COALESCE(ls.status, 'not_started') as status,
               ls.sub_steps as case_sub_steps,
               ls.notes as notes,
               ls.completed_at as completed_at,
               ls.updated_at as updated_at,
               ls.version as version,
               ls.updated_by as updated_by,
               l.order as order
        ORDER BY l.order, l.landmark_id
        """
        return await run_cypher_query(query, {"case_name": case_name, "phase_name": phase_name})
    else:
        # Get ALL landmarks, LEFT JOIN with case's status via LandmarkStatus nodes
        query = """
        MATCH (l:Entity {entity_type: 'Landmark'})
        WHERE l.group_id = '__workflow_definitions__'
        OPTIONAL MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[:HAS_STATUS]->(ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l)
        WHERE ls IS NULL OR ls.archived_at IS NULL
        RETURN l.landmark_id as landmark_id,
               l.name as display_name,
               l.phase as phase,
               l.landmark_type as landmark_type,
               l.is_hard_blocker as is_hard_blocker,
               l.can_override as can_override,
               l.sub_steps as landmark_sub_steps,
               COALESCE(ls.status, 'not_started') as status,
               ls.sub_steps as case_sub_steps,
               ls.notes as notes,
               ls.completed_at as completed_at,
               ls.updated_at as updated_at,
               ls.version as version,
               ls.updated_by as updated_by,
               l.order as order
        ORDER BY l.phase, l.order, l.landmark_id
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
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[:HAS_STATUS]->(ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l:Entity {entity_type: 'Landmark', landmark_id: $landmark_id})
    WHERE ls.archived_at IS NULL
    RETURN l.landmark_id as landmark_id,
           l.name as display_name,
           l.phase as phase,
           l.landmark_type as landmark_type,
           l.is_hard_blocker as is_hard_blocker,
           l.sub_steps as landmark_sub_steps,
           ls.status as status,
           ls.sub_steps as case_sub_steps,
           ls.notes as notes,
           ls.completed_at as completed_at,
           ls.version as version,
           ls.updated_by as updated_by
    """
    results = await run_cypher_query(query, {"case_name": case_name, "landmark_id": landmark_id})
    return results[0] if results else None


async def update_case_landmark_status(
    case_name: str,
    landmark_id: str,
    status: str,
    sub_steps: dict = None,
    notes: str = None,
    updated_by: str = "agent"
) -> bool:
    """
    Update a landmark's status for a case using versioned LandmarkStatus nodes.

    Creates a new LandmarkStatus node with incremented version, archives old version.

    Args:
        case_name: Case name/identifier
        landmark_id: Landmark identifier
        status: New status ('complete', 'incomplete', 'in_progress', 'not_applicable')
        sub_steps: Optional dict of sub-step completions
        notes: Optional notes about the status
        updated_by: Who is updating ('agent', 'user', 'system')

    Returns:
        True if updated successfully
    """
    import hashlib
    import uuid as uuid_lib
    from datetime import datetime

    sub_steps_json = json.dumps(sub_steps) if sub_steps else None
    now = datetime.now().isoformat()
    completed_at = now if status == "complete" else None

    # Generate deterministic UUID for this case+landmark combination
    status_key = f"{case_name}_{landmark_id}"
    status_hash = hashlib.md5(status_key.encode()).hexdigest()
    status_uuid = str(uuid_lib.UUID(status_hash))

    query = """
    // Find case and landmark
    MATCH (c:Entity {entity_type: 'Case', name: $case_name})
    MATCH (l:Entity {entity_type: 'Landmark', landmark_id: $landmark_id})

    // Find current status (if exists)
    OPTIONAL MATCH (c)-[:HAS_STATUS]->(old_ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l)
    WHERE old_ls.archived_at IS NULL

    // Get current version
    WITH c, l, old_ls, COALESCE(old_ls.version, 0) as current_version

    // Create new LandmarkStatus node
    CREATE (new_ls:Entity {
      entity_type: 'LandmarkStatus',
      group_id: 'roscoe_graph',
      uuid: $uuid,
      case_name: $case_name,
      landmark_id: $landmark_id,
      status: $status,
      sub_steps: $sub_steps,
      notes: $notes,
      completed_at: $completed_at,
      created_at: $now,
      updated_at: $now,
      updated_by: $updated_by,
      version: current_version + 1
    })

    // Link new status
    MERGE (c)-[:HAS_STATUS]->(new_ls)
    MERGE (new_ls)-[:FOR_LANDMARK]->(l)

    // Archive old version (if exists)
    WITH old_ls, new_ls
    WHERE old_ls IS NOT NULL
    SET old_ls.archived_at = $now

    RETURN new_ls.version as new_version
    """

    params = {
        "case_name": case_name,
        "landmark_id": landmark_id,
        "uuid": status_uuid,
        "status": status,
        "sub_steps": sub_steps_json,
        "notes": notes,
        "completed_at": completed_at,
        "now": now,
        "updated_by": updated_by
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
    
    # Find all hard blockers that are not complete (via LandmarkStatus nodes)
    blocker_query = """
    MATCH (p:Entity {entity_type: 'Phase', name: $phase_name})-[:HAS_LANDMARK]->(l:Entity {entity_type: 'Landmark', is_hard_blocker: true})
    OPTIONAL MATCH (c:Entity {entity_type: 'Case', name: $case_name})-[:HAS_STATUS]->(ls:Entity {entity_type: 'LandmarkStatus'})-[:FOR_LANDMARK]->(l)
    WHERE ls.archived_at IS NULL OR ls IS NULL
    WITH l, ls
    WHERE ls IS NULL OR ls.status <> 'complete'
    RETURN l.name as landmark_id,
           l.display_name as display_name,
           COALESCE(ls.status, 'not_started') as current_status
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
