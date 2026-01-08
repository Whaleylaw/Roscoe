#!/usr/bin/env python3
"""
Ingest All Landmarks into Graph

This script creates Landmark entities and their relationships:
- Phase -HAS_LANDMARK-> Landmark
- Landmark -ACHIEVED_BY-> Workflow

It also enhances Phase entities with additional metadata.

Usage:
    python -m roscoe.scripts.ingest_all_landmarks
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Any


# Define all landmarks with their metadata
# This is the canonical definition based on the landmarks.md files
LANDMARKS = {
    # Phase 1: File Setup
    "file_setup": {
        "retainer_signed": {
            "display_name": "Retainer Signed",
            "landmark_type": "hard_blocker",
            "is_hard_blocker": True,
            "can_override": False,
            "description": "Client must sign retainer agreement",
            "verification_field": "documents.retainer.status",
            "required_value": "signed",
            "achieved_by": ["intake", "send_documents_for_signature"],
            "sub_steps": {}
        },
        "hipaa_signed": {
            "display_name": "HIPAA Authorization Signed",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "override_consequence": "Cannot request medical records without HIPAA",
            "description": "HIPAA authorization signed (needed for records)",
            "verification_field": "documents.hipaa.status",
            "required_value": "signed",
            "achieved_by": ["send_documents_for_signature"],
            "sub_steps": {}
        },
        "full_intake_complete": {
            "display_name": "Full Intake Complete",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "description": "Complete client and case information has been collected",
            "achieved_by": ["intake"],
            "sub_steps": {
                "demographics_complete": "Full client demographics captured",
                "incident_details_complete": "Complete incident details documented",
                "injuries_documented": "All injuries and treatment to date recorded",
                "employment_info": "Employment information (if wage loss claim)",
                "parties_documented": "All involved parties documented"
            }
        },
        "accident_report_obtained": {
            "display_name": "Accident Report Obtained",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "override_consequence": "May be missing party/insurance info",
            "description": "Police/accident report has been requested, received, and analyzed",
            "condition": "accident.type == 'mva'",
            "achieved_by": ["accident_report"],
            "sub_steps": {
                "report_requested": "Report requested",
                "report_received": "Report received",
                "report_analyzed": "Report analyzed for parties and insurance",
                "liability_documented": "Liability indicators documented"
            }
        },
        "insurance_claims_setup": {
            "display_name": "Insurance Claims Set Up",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "override_consequence": "May miss recovery sources",
            "description": "All applicable insurance claims have been opened with acknowledgment",
            "achieved_by": ["open_insurance_claims"],
            "sub_steps": {
                "bi_insurance_identified": "At-fault insurance identified",
                "bi_lor_sent": "BI Letter of Rep sent",
                "bi_claim_acknowledged": "BI claim acknowledged",
                "bi_liability_status": "Liability status obtained",
                "bi_coverage_confirmed": "Coverage confirmed",
                "pip_carrier_determined": "PIP carrier determined",
                "pip_application_sent": "PIP application submitted",
                "pip_lor_sent": "PIP Letter of Rep sent",
                "pip_claim_acknowledged": "PIP claim acknowledged",
                "pip_ready_to_pay": "PIP ready to pay bills"
            }
        },
        "providers_setup": {
            "display_name": "Providers Set Up",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "description": "All known medical providers have been added to the case file",
            "achieved_by": ["medical_provider_setup"],
            "sub_steps": {
                "providers_identified": "All treating providers identified",
                "contact_verified": "Provider contact information verified",
                "records_requested": "Records requested for completed treatment"
            }
        }
    },
    
    # Phase 2: Treatment
    "treatment": {
        "client_checkin_current": {
            "display_name": "Client Check-In Current",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Bi-weekly check-in with client is current",
            "achieved_by": ["client_check_in"],
            "sub_steps": {
                "last_contact_within_14_days": "Last contact within 14 days",
                "next_checkin_scheduled": "Next check-in scheduled"
            }
        },
        "providers_monitored": {
            "display_name": "All Providers Being Monitored",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "All active providers are being monitored for treatment status",
            "achieved_by": ["medical_provider_status"],
            "sub_steps": {
                "active_providers_tracked": "Active providers tracked",
                "status_current": "Treatment status is current"
            }
        },
        "treatment_progress_documented": {
            "display_name": "Treatment Progress Documented",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Treatment progress is documented in notes",
            "achieved_by": ["client_check_in"],
            "sub_steps": {}
        },
        "records_requested_completed": {
            "display_name": "Records Requested for Completed Providers",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Records have been requested for all providers with completed treatment",
            "achieved_by": ["request_records_bills"],
            "sub_steps": {}
        },
        "treatment_complete": {
            "display_name": "Treatment Complete or Discharged",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "override_consequence": "May settle before Maximum Medical Improvement",
            "description": "Client reports done treating OR discharged from all providers",
            "achieved_by": ["client_check_in", "medical_provider_status"],
            "sub_steps": {
                "all_discharged": "All providers have discharged client",
                "client_reports_done": "Client reports treatment complete"
            }
        }
    },
    
    # Phase 3: Demand in Progress
    "demand_in_progress": {
        "all_records_received": {
            "display_name": "All Records Received",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "override_consequence": "Demand may be incomplete",
            "description": "Medical records received from all providers",
            "achieved_by": ["gather_demand_materials", "request_records_bills"],
            "sub_steps": {}
        },
        "all_bills_received": {
            "display_name": "All Bills Received",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "override_consequence": "May undervalue case",
            "description": "Medical bills received from all providers",
            "achieved_by": ["gather_demand_materials", "request_records_bills"],
            "sub_steps": {}
        },
        "specials_calculated": {
            "display_name": "Specials Calculated",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Total of all medical bills and expenses calculated",
            "achieved_by": ["gather_demand_materials"],
            "sub_steps": {}
        },
        "chronology_finalized": {
            "display_name": "Chronology Finalized",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Medical chronology finalized for demand",
            "achieved_by": ["gather_demand_materials"],
            "sub_steps": {}
        },
        "liens_identified": {
            "display_name": "Liens Identified",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "override_consequence": "May have surprise liens at settlement",
            "description": "All liens identified and conditional amounts requested",
            "achieved_by": ["gather_demand_materials", "lien_identification"],
            "sub_steps": {}
        },
        "wage_loss_documented": {
            "display_name": "Wage Loss Documented",
            "landmark_type": "conditional",
            "is_hard_blocker": False,
            "condition": "client.employer.missed_work == true",
            "description": "Lost wages are documented with supporting evidence",
            "achieved_by": ["gather_demand_materials"],
            "sub_steps": {}
        },
        "demand_draft_prepared": {
            "display_name": "Demand Draft Prepared",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Initial demand letter draft has been created",
            "achieved_by": ["draft_demand"],
            "sub_steps": {}
        },
        "exhibits_compiled": {
            "display_name": "Exhibits Compiled",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "All supporting exhibits have been compiled",
            "achieved_by": ["draft_demand"],
            "sub_steps": {}
        },
        "attorney_approved": {
            "display_name": "Attorney Approved",
            "landmark_type": "gate",
            "is_hard_blocker": False,
            "description": "Attorney has reviewed and approved the demand letter",
            "achieved_by": ["draft_demand"],
            "sub_steps": {}
        },
        "demand_sent": {
            "display_name": "Demand Sent",
            "landmark_type": "hard_blocker",
            "is_hard_blocker": True,
            "can_override": False,
            "description": "Demand letter and package sent to all BI adjusters",
            "achieved_by": ["send_demand"],
            "sub_steps": {}
        },
        "client_notified_demand": {
            "display_name": "Client Notified",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Client has been notified that demand was sent",
            "achieved_by": ["send_demand"],
            "sub_steps": {}
        },
        "followup_scheduled": {
            "display_name": "Follow-Up Scheduled",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "30-day follow-up has been scheduled for demand response",
            "achieved_by": ["send_demand"],
            "sub_steps": {}
        }
    },
    
    # Phase 4: Negotiation
    "negotiation": {
        "one_week_followup": {
            "display_name": "One-Week Follow-Up",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Follow-up conducted one week after demand to confirm receipt",
            "achieved_by": ["negotiate_claim"],
            "sub_steps": {}
        },
        "deficiencies_addressed": {
            "display_name": "Deficiencies Addressed",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Any deficiencies or information requests from insurance addressed",
            "achieved_by": ["negotiate_claim"],
            "sub_steps": {}
        },
        "thirty_day_followup": {
            "display_name": "Thirty-Day Follow-Up",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Follow-up conducted 30 days after demand if no response",
            "achieved_by": ["negotiate_claim"],
            "sub_steps": {}
        },
        "initial_offer_received": {
            "display_name": "Initial Offer Received",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Insurance company has made an initial offer",
            "achieved_by": ["negotiate_claim"],
            "sub_steps": {}
        },
        "net_calculated": {
            "display_name": "Net to Client Calculated",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Net to client has been calculated for current offer",
            "achieved_by": ["negotiate_claim"],
            "sub_steps": {}
        },
        "offer_evaluated": {
            "display_name": "Offer Evaluated by Attorney",
            "landmark_type": "gate",
            "is_hard_blocker": False,
            "description": "Attorney has evaluated the current offer and provided recommendation",
            "achieved_by": ["negotiate_claim"],
            "sub_steps": {}
        },
        "client_authorized": {
            "display_name": "Client Authorized Decision",
            "landmark_type": "gate",
            "is_hard_blocker": False,
            "description": "Client has been informed and authorized the response to offer",
            "achieved_by": ["negotiate_claim"],
            "sub_steps": {}
        },
        "negotiation_documented": {
            "display_name": "Negotiation Documented",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "All rounds of negotiation are documented with offers/counters",
            "achieved_by": ["track_offers"],
            "sub_steps": {}
        },
        "settlement_reached": {
            "display_name": "Settlement Reached",
            "landmark_type": "exit_condition",
            "is_hard_blocker": False,
            "description": "Settlement agreement reached with insurance",
            "achieved_by": ["negotiate_claim"],
            "triggers_phase": "settlement",
            "sub_steps": {}
        },
        "impasse_reached": {
            "display_name": "Impasse Reached",
            "landmark_type": "exit_condition",
            "is_hard_blocker": False,
            "description": "Impasse reached - proceeding to litigation or closing",
            "achieved_by": ["negotiate_claim"],
            "triggers_phase": "complaint",
            "sub_steps": {}
        }
    },
    
    # Phase 5: Settlement
    "settlement": {
        "statement_prepared": {
            "display_name": "Settlement Statement Prepared",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Settlement breakdown has been prepared",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        },
        "auth_prepared": {
            "display_name": "Authorization Prepared",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Authorization to settle document has been prepared",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        },
        "auth_signed": {
            "display_name": "Client Signed Authorization",
            "landmark_type": "gate",
            "is_hard_blocker": False,
            "description": "Client has signed the authorization to settle",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        },
        "adjuster_notified": {
            "display_name": "Adjuster Notified",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Adjuster has been notified of acceptance and release requested",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        },
        "release_received": {
            "display_name": "Release Received",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Insurance company's release document has been received",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        },
        "release_signed": {
            "display_name": "Release Signed by Client",
            "landmark_type": "gate",
            "is_hard_blocker": False,
            "description": "Client has signed the insurance release",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        },
        "release_returned": {
            "display_name": "Release Returned",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Signed release has been sent back to insurance company",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        },
        "check_received": {
            "display_name": "Settlement Check Received",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Settlement check has been received from insurance",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        },
        "check_cleared": {
            "display_name": "Check Deposited and Cleared",
            "landmark_type": "gate",
            "is_hard_blocker": False,
            "description": "Settlement check has been deposited and cleared",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        },
        "liens_paid": {
            "display_name": "Liens Paid",
            "landmark_type": "conditional",
            "is_hard_blocker": False,
            "condition": "liens.length > 0",
            "description": "All liens have been paid from settlement proceeds",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        },
        "client_paid": {
            "display_name": "Client Received Funds",
            "landmark_type": "hard_blocker",
            "is_hard_blocker": True,
            "can_override": False,
            "description": "Client has received their distribution check",
            "achieved_by": ["settlement_processing"],
            "sub_steps": {}
        }
    },
    
    # Phase 6: Lien Phase
    "lien_phase": {
        "outstanding_liens_identified": {
            "display_name": "Outstanding Liens Identified",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "All liens requiring resolution have been identified",
            "achieved_by": ["get_final_lien"],
            "sub_steps": {}
        },
        "final_amounts_requested": {
            "display_name": "Final Amounts Requested",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Final lien amounts have been requested from all holders",
            "achieved_by": ["get_final_lien"],
            "sub_steps": {}
        },
        "medicare_final_demand": {
            "display_name": "Medicare Final Demand",
            "landmark_type": "conditional",
            "is_hard_blocker": False,
            "condition": "liens.has_medicare == true",
            "description": "Medicare has issued final demand letter",
            "achieved_by": ["get_final_lien"],
            "sub_steps": {}
        },
        "negotiations_complete": {
            "display_name": "Lien Negotiations Complete",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "All negotiable liens have been negotiated",
            "achieved_by": ["negotiate_lien"],
            "sub_steps": {}
        },
        "all_liens_paid": {
            "display_name": "All Liens Paid",
            "landmark_type": "hard_blocker",
            "is_hard_blocker": True,
            "can_override": False,
            "description": "All outstanding liens have been paid",
            "achieved_by": ["negotiate_lien"],
            "sub_steps": {}
        },
        "supp_statement_prepared": {
            "display_name": "Supplemental Statement Prepared",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Final settlement statement prepared showing lien resolution",
            "achieved_by": ["final_distribution"],
            "sub_steps": {}
        },
        "final_distribution": {
            "display_name": "Final Distribution Complete",
            "landmark_type": "hard_blocker",
            "is_hard_blocker": True,
            "can_override": False,
            "description": "Additional funds distributed to client",
            "achieved_by": ["final_distribution"],
            "sub_steps": {}
        }
    },
    
    # Phase 7: Complaint
    "complaint": {
        "complaint_filed": {
            "display_name": "Complaint Filed",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Complaint has been filed with the court",
            "achieved_by": ["draft_file_complaint"],
            "sub_steps": {}
        },
        "defendant_served": {
            "display_name": "Defendant Served",
            "landmark_type": "hard_blocker",
            "is_hard_blocker": True,
            "can_override": False,
            "description": "All defendants served with complaint",
            "achieved_by": ["serve_defendant"],
            "sub_steps": {}
        },
        "answer_received": {
            "display_name": "Answer Received",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "override_consequence": "Seek default judgment",
            "description": "Answer received from defendant(s)",
            "achieved_by": ["process_answer"],
            "sub_steps": {}
        }
    },
    
    # Phase 8: Discovery
    "discovery": {
        "discovery_propounded": {
            "display_name": "Discovery Propounded",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Initial discovery requests sent to defendant",
            "achieved_by": ["propound_discovery"],
            "sub_steps": {}
        },
        "discovery_responded": {
            "display_name": "Discovery Responded",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Responded to defendant's discovery requests",
            "achieved_by": ["respond_to_discovery"],
            "sub_steps": {}
        },
        "depositions_complete": {
            "display_name": "Depositions Complete",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "All party depositions completed",
            "achieved_by": ["party_depositions"],
            "sub_steps": {}
        },
        "discovery_complete": {
            "display_name": "Discovery Complete",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "description": "Discovery deadline passed or all needed discovery obtained",
            "achieved_by": ["review_responses"],
            "sub_steps": {}
        }
    },
    
    # Phase 9: Mediation
    "mediation": {
        "mediation_prepared": {
            "display_name": "Mediation Prepared",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Mediation materials prepared",
            "achieved_by": ["prepare_mediation"],
            "sub_steps": {}
        },
        "mediation_occurred": {
            "display_name": "Mediation Occurred",
            "landmark_type": "hard_blocker",
            "is_hard_blocker": True,
            "can_override": False,
            "description": "Mediation attended (regardless of outcome)",
            "achieved_by": ["attend_mediation"],
            "sub_steps": {}
        }
    },
    
    # Phase 10: Trial Prep
    "trial_prep": {
        "experts_disclosed": {
            "display_name": "Experts Disclosed",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": False,
            "description": "All expert witnesses disclosed by deadline",
            "achieved_by": ["expert_management"],
            "sub_steps": {}
        },
        "exhibits_prepared": {
            "display_name": "Exhibits Prepared",
            "landmark_type": "soft_blocker",
            "is_hard_blocker": False,
            "can_override": True,
            "description": "Trial exhibits prepared and exchanged",
            "achieved_by": ["trial_materials"],
            "sub_steps": {}
        },
        "trial_begins": {
            "display_name": "Trial Begins",
            "landmark_type": "hard_blocker",
            "is_hard_blocker": True,
            "can_override": False,
            "description": "Trial date arrived",
            "achieved_by": [],
            "sub_steps": {}
        }
    },
    
    # Phase 11: Trial
    "trial": {
        "verdict_rendered": {
            "display_name": "Verdict Rendered",
            "landmark_type": "hard_blocker",
            "is_hard_blocker": True,
            "can_override": False,
            "description": "Jury has returned verdict",
            "achieved_by": ["conduct_trial"],
            "sub_steps": {}
        }
    },
    
    # Phase 12: Closed
    "closed": {
        "obligations_verified": {
            "display_name": "All Obligations Verified",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "All financial and legal obligations verified complete",
            "achieved_by": ["close_case"],
            "sub_steps": {}
        },
        "final_letter_sent": {
            "display_name": "Final Letter Sent",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Final closing letter sent to client",
            "achieved_by": ["close_case"],
            "sub_steps": {}
        },
        "review_requested": {
            "display_name": "Review Requested",
            "landmark_type": "conditional",
            "is_hard_blocker": False,
            "condition": "good_outcome AND good_relationship",
            "description": "Google review requested from satisfied client",
            "achieved_by": ["close_case"],
            "sub_steps": {}
        },
        "file_archived": {
            "display_name": "File Archived",
            "landmark_type": "progress",
            "is_hard_blocker": False,
            "description": "Physical and digital file archived",
            "achieved_by": ["close_case"],
            "sub_steps": {}
        }
    }
}


# Phase metadata
PHASES = {
    "file_setup": {"display_name": "File Setup", "order": 1, "track": "pre_litigation", "next_phase": "treatment"},
    "treatment": {"display_name": "Treatment", "order": 2, "track": "pre_litigation", "next_phase": "demand_in_progress"},
    "demand_in_progress": {"display_name": "Demand in Progress", "order": 3, "track": "pre_litigation", "next_phase": "negotiation"},
    "negotiation": {"display_name": "Negotiation", "order": 4, "track": "pre_litigation", "next_phase": "settlement"},
    "settlement": {"display_name": "Settlement", "order": 5, "track": "pre_litigation", "next_phase": "closed"},
    "lien_phase": {"display_name": "Lien Phase", "order": 6, "track": "pre_litigation", "next_phase": "closed"},
    "complaint": {"display_name": "Complaint", "order": 7, "track": "litigation", "next_phase": "discovery"},
    "discovery": {"display_name": "Discovery", "order": 8, "track": "litigation", "next_phase": "mediation"},
    "mediation": {"display_name": "Mediation", "order": 9, "track": "litigation", "next_phase": "trial_prep"},
    "trial_prep": {"display_name": "Trial Prep", "order": 10, "track": "litigation", "next_phase": "trial"},
    "trial": {"display_name": "Trial", "order": 11, "track": "litigation", "next_phase": "closed"},
    "closed": {"display_name": "Closed / Archived", "order": 12, "track": "terminal", "next_phase": None}
}


async def run_query(query: str, params: dict = None):
    """Execute a Cypher query."""
    from roscoe.core.graphiti_client import run_cypher_query
    try:
        return await run_cypher_query(query, params or {})
    except Exception as e:
        print(f"  Error: {e}")
        return []


async def create_landmark_entity(phase_name: str, landmark_id: str, landmark_data: dict):
    """Create a Landmark entity."""
    # Serialize sub_steps to JSON string if present
    sub_steps_json = json.dumps(landmark_data.get("sub_steps", {})) if landmark_data.get("sub_steps") else "{}"
    
    query = """
    MERGE (l:Entity {name: $name, entity_type: 'Landmark'})
    ON CREATE SET 
        l.display_name = $display_name,
        l.phase = $phase,
        l.landmark_type = $landmark_type,
        l.is_hard_blocker = $is_hard_blocker,
        l.can_override = $can_override,
        l.override_consequence = $override_consequence,
        l.description = $description,
        l.verification_field = $verification_field,
        l.required_value = $required_value,
        l.condition = $condition,
        l.triggers_phase = $triggers_phase,
        l.sub_steps = $sub_steps
    ON MATCH SET
        l.display_name = $display_name,
        l.phase = $phase,
        l.landmark_type = $landmark_type,
        l.is_hard_blocker = $is_hard_blocker,
        l.can_override = $can_override,
        l.override_consequence = $override_consequence,
        l.description = $description,
        l.verification_field = $verification_field,
        l.required_value = $required_value,
        l.condition = $condition,
        l.triggers_phase = $triggers_phase,
        l.sub_steps = $sub_steps
    RETURN l.name as name
    """
    
    params = {
        "name": landmark_id,
        "display_name": landmark_data.get("display_name", landmark_id),
        "phase": phase_name,
        "landmark_type": landmark_data.get("landmark_type", "progress"),
        "is_hard_blocker": landmark_data.get("is_hard_blocker", False),
        "can_override": landmark_data.get("can_override", True),
        "override_consequence": landmark_data.get("override_consequence"),
        "description": landmark_data.get("description", ""),
        "verification_field": landmark_data.get("verification_field"),
        "required_value": landmark_data.get("required_value"),
        "condition": landmark_data.get("condition"),
        "triggers_phase": landmark_data.get("triggers_phase"),
        "sub_steps": sub_steps_json
    }
    
    await run_query(query, params)
    return True


async def create_phase_landmark_relationship(phase_name: str, landmark_id: str):
    """Create Phase -HAS_LANDMARK-> Landmark relationship."""
    query = """
    MATCH (p:Entity {name: $phase_name, entity_type: 'Phase'})
    MATCH (l:Entity {name: $landmark_id, entity_type: 'Landmark'})
    MERGE (p)-[r:HAS_LANDMARK]->(l)
    RETURN p.name, l.name
    """
    
    result = await run_query(query, {"phase_name": phase_name, "landmark_id": landmark_id})
    return len(result) > 0


async def create_landmark_workflow_relationship(landmark_id: str, workflow_name: str):
    """Create Landmark -ACHIEVED_BY-> Workflow relationship."""
    query = """
    MATCH (l:Entity {name: $landmark_id, entity_type: 'Landmark'})
    MATCH (w:Entity {name: $workflow_name, entity_type: 'WorkflowDef'})
    MERGE (l)-[r:ACHIEVED_BY]->(w)
    RETURN l.name, w.name
    """
    
    result = await run_query(query, {"landmark_id": landmark_id, "workflow_name": workflow_name})
    return len(result) > 0


async def update_phase_metadata(phase_name: str, metadata: dict):
    """Update Phase entity with additional metadata."""
    query = """
    MATCH (p:Entity {name: $phase_name, entity_type: 'Phase'})
    SET p.display_name = $display_name,
        p.track = $track,
        p.next_phase_name = $next_phase
    RETURN p.name
    """
    
    params = {
        "phase_name": phase_name,
        "display_name": metadata.get("display_name", phase_name),
        "track": metadata.get("track", "pre_litigation"),
        "next_phase": metadata.get("next_phase")
    }
    
    await run_query(query, params)


async def ingest_all_landmarks():
    """Main function to ingest all landmarks."""
    print("=" * 60)
    print("INGESTING ALL LANDMARKS INTO GRAPH")
    print("=" * 60)
    
    stats = {
        "landmarks_created": 0,
        "phase_landmark_rels": 0,
        "landmark_workflow_rels": 0,
        "phases_updated": 0
    }
    
    # First, update phase metadata
    print("\n=== Updating Phase Metadata ===")
    for phase_name, metadata in PHASES.items():
        await update_phase_metadata(phase_name, metadata)
        stats["phases_updated"] += 1
        print(f"  Updated: {phase_name}")
    
    # Create landmarks and relationships
    print("\n=== Creating Landmarks ===")
    for phase_name, landmarks in LANDMARKS.items():
        print(f"\nPhase: {phase_name}")
        
        for landmark_id, landmark_data in landmarks.items():
            # Create landmark entity
            await create_landmark_entity(phase_name, landmark_id, landmark_data)
            stats["landmarks_created"] += 1
            
            is_hard = "HARD" if landmark_data.get("is_hard_blocker") else ""
            print(f"  Created: {landmark_id} ({landmark_data.get('landmark_type', 'progress')}) {is_hard}")
            
            # Create Phase -> Landmark relationship
            if await create_phase_landmark_relationship(phase_name, landmark_id):
                stats["phase_landmark_rels"] += 1
            
            # Create Landmark -> Workflow relationships
            for workflow_name in landmark_data.get("achieved_by", []):
                if await create_landmark_workflow_relationship(landmark_id, workflow_name):
                    stats["landmark_workflow_rels"] += 1
                    print(f"    -> achieved by: {workflow_name}")
    
    # Summary
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"  Phases updated:              {stats['phases_updated']}")
    print(f"  Landmarks created:           {stats['landmarks_created']}")
    print(f"  Phase->Landmark relations:   {stats['phase_landmark_rels']}")
    print(f"  Landmark->Workflow relations: {stats['landmark_workflow_rels']}")
    print("=" * 60)
    
    # Verification query
    print("\n=== Verification ===")
    verify_query = """
    MATCH (p:Entity {entity_type: 'Phase'})-[:HAS_LANDMARK]->(l:Entity {entity_type: 'Landmark'})
    WITH p.name as phase, count(l) as landmark_count, 
         sum(CASE WHEN l.is_hard_blocker = true THEN 1 ELSE 0 END) as hard_blockers
    RETURN phase, landmark_count, hard_blockers
    ORDER BY p.order
    """
    
    results = await run_query(verify_query)
    print("\nLandmarks per phase:")
    for r in results:
        print(f"  {r.get('phase')}: {r.get('landmark_count')} landmarks ({r.get('hard_blockers')} hard blockers)")
    
    return stats


def main():
    asyncio.run(ingest_all_landmarks())


if __name__ == "__main__":
    main()
