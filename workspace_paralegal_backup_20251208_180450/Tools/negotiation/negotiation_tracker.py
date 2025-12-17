#!/usr/bin/env python3
"""
Negotiation Tracker Tool

Tracks offer/counteroffer history for personal injury negotiations.
Stores negotiation events, calculates positions, and provides status updates.

Usage:
    # View current negotiation status
    python negotiation_tracker.py --case "Smith-MVA" --status
    
    # Add an offer from insurance
    python negotiation_tracker.py --case "Smith-MVA" --add-offer 25000 --from insurance --notes "Initial offer"
    
    # Add a counteroffer/demand
    python negotiation_tracker.py --case "Smith-MVA" --add-offer 75000 --from client --notes "Counteroffer"
    
    # View full negotiation history
    python negotiation_tracker.py --case "Smith-MVA" --history
    
    # Record settlement
    python negotiation_tracker.py --case "Smith-MVA" --settle 45000

Data Storage:
    Negotiation data stored in case folder: /case_name/negotiation.json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from decimal import Decimal, ROUND_HALF_UP

# Try to import case data adapter
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _adapters.case_data import CaseData
    HAS_ADAPTER = True
except ImportError:
    HAS_ADAPTER = False


def money(value) -> float:
    """Convert to money format (2 decimal places)."""
    return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def format_currency(amount: float) -> str:
    """Format as currency string."""
    return f"${amount:,.2f}"


@dataclass
class NegotiationEvent:
    """A single offer or counteroffer in the negotiation."""
    date: str
    amount: float
    from_party: str  # "insurance" or "client"
    event_type: str  # "initial_demand", "offer", "counteroffer", "final_offer", "settlement"
    notes: str = ""
    adjuster_name: str = ""
    
    def to_dict(self):
        return asdict(self)


@dataclass
class NegotiationState:
    """Current state of a negotiation."""
    case_name: str
    claim_number: str = ""
    insurance_company: str = ""
    adjuster_name: str = ""
    adjuster_phone: str = ""
    adjuster_email: str = ""
    coverage_type: str = "BI"  # BI, PIP, UM, UIM
    policy_limits: float = 0.0
    
    # Demand info
    demand_date: str = ""
    demand_amount: float = 0.0
    demand_summary: str = ""
    
    # Current position
    current_offer: float = 0.0
    current_offer_date: str = ""
    last_counteroffer: float = 0.0
    last_counteroffer_date: str = ""
    
    # Status
    status: str = "pending"  # pending, active, stalled, settled, litigation
    status_notes: str = ""
    
    # Settlement
    settlement_amount: float = 0.0
    settlement_date: str = ""
    
    # History
    events: List[dict] = field(default_factory=list)
    
    # Timestamps
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self):
        return asdict(self)


def get_negotiation_file(case_name: str) -> Path:
    """Get path to negotiation.json for a case."""
    # Try to find the case folder
    workspace = Path("/workspace_paralegal") if Path("/workspace_paralegal").exists() else Path(".")
    
    # Look for case folder
    case_folder = workspace / case_name
    if not case_folder.exists():
        # Try finding it
        for folder in workspace.iterdir():
            if folder.is_dir() and case_name.lower() in folder.name.lower():
                case_folder = folder
                break
    
    case_folder.mkdir(parents=True, exist_ok=True)
    return case_folder / "negotiation.json"


def load_negotiation(case_name: str) -> NegotiationState:
    """Load negotiation state from file."""
    filepath = get_negotiation_file(case_name)
    
    if filepath.exists():
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            # Convert to NegotiationState
            events = data.pop("events", [])
            state = NegotiationState(**{k: v for k, v in data.items() if k in NegotiationState.__dataclass_fields__})
            state.events = events
            return state
        except Exception as e:
            print(f"Warning: Could not load existing negotiation: {e}", file=sys.stderr)
    
    # Return new state
    return NegotiationState(
        case_name=case_name,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )


def save_negotiation(state: NegotiationState):
    """Save negotiation state to file."""
    filepath = get_negotiation_file(state.case_name)
    state.updated_at = datetime.now().isoformat()
    
    with open(filepath, 'w') as f:
        json.dump(state.to_dict(), f, indent=2)
    
    print(f"Saved to: {filepath}", file=sys.stderr)


def add_event(state: NegotiationState, amount: float, from_party: str, 
              event_type: str, notes: str = "") -> NegotiationEvent:
    """Add a negotiation event."""
    event = NegotiationEvent(
        date=datetime.now().strftime("%Y-%m-%d"),
        amount=money(amount),
        from_party=from_party,
        event_type=event_type,
        notes=notes,
        adjuster_name=state.adjuster_name
    )
    
    state.events.append(event.to_dict())
    
    # Update current position based on event
    if from_party == "insurance":
        state.current_offer = money(amount)
        state.current_offer_date = event.date
        if state.status == "pending":
            state.status = "active"
    else:  # client
        state.last_counteroffer = money(amount)
        state.last_counteroffer_date = event.date
    
    if event_type == "settlement":
        state.settlement_amount = money(amount)
        state.settlement_date = event.date
        state.status = "settled"
    
    return event


def get_negotiation_summary(state: NegotiationState) -> dict:
    """Generate summary of negotiation status."""
    # Calculate gap
    gap = 0
    gap_percent = 0
    
    if state.current_offer > 0 and state.last_counteroffer > 0:
        gap = state.last_counteroffer - state.current_offer
        gap_percent = (gap / state.last_counteroffer) * 100 if state.last_counteroffer > 0 else 0
    
    # Count offers
    insurance_offers = [e for e in state.events if e.get("from_party") == "insurance"]
    client_offers = [e for e in state.events if e.get("from_party") == "client"]
    
    # Days since last activity
    days_since_activity = None
    if state.events:
        last_event_date = state.events[-1].get("date")
        if last_event_date:
            try:
                last_date = datetime.strptime(last_event_date, "%Y-%m-%d")
                days_since_activity = (datetime.now() - last_date).days
            except:
                pass
    
    return {
        "case_name": state.case_name,
        "status": state.status,
        "coverage_type": state.coverage_type,
        "insurance_company": state.insurance_company,
        "adjuster": state.adjuster_name,
        "claim_number": state.claim_number,
        "policy_limits": state.policy_limits,
        "demand": {
            "date": state.demand_date,
            "amount": state.demand_amount,
            "summary": state.demand_summary
        },
        "current_position": {
            "insurance_offer": state.current_offer,
            "insurance_offer_date": state.current_offer_date,
            "client_counteroffer": state.last_counteroffer,
            "client_counteroffer_date": state.last_counteroffer_date,
            "gap": gap,
            "gap_percent": round(gap_percent, 1)
        },
        "activity": {
            "total_events": len(state.events),
            "insurance_offers": len(insurance_offers),
            "client_offers": len(client_offers),
            "days_since_activity": days_since_activity
        },
        "settlement": {
            "settled": state.status == "settled",
            "amount": state.settlement_amount,
            "date": state.settlement_date
        } if state.status == "settled" else None
    }


def print_status(state: NegotiationState, pretty: bool = False):
    """Print current negotiation status."""
    summary = get_negotiation_summary(state)
    
    if pretty:
        print("\n" + "="*60)
        print(f"NEGOTIATION STATUS: {state.case_name}")
        print("="*60)
        
        print(f"\nStatus: {state.status.upper()}")
        print(f"Coverage: {state.coverage_type}")
        print(f"Insurance: {state.insurance_company}")
        print(f"Adjuster: {state.adjuster_name}")
        print(f"Claim #: {state.claim_number}")
        
        if state.policy_limits:
            print(f"Policy Limits: {format_currency(state.policy_limits)}")
        
        print(f"\n--- DEMAND ---")
        print(f"Date Sent: {state.demand_date or 'Not sent'}")
        print(f"Amount: {format_currency(state.demand_amount)}")
        
        print(f"\n--- CURRENT POSITION ---")
        print(f"Insurance Offer: {format_currency(state.current_offer)} ({state.current_offer_date or 'N/A'})")
        print(f"Our Position: {format_currency(state.last_counteroffer)} ({state.last_counteroffer_date or 'N/A'})")
        
        if state.current_offer > 0 and state.last_counteroffer > 0:
            gap = state.last_counteroffer - state.current_offer
            print(f"Gap: {format_currency(gap)} ({summary['current_position']['gap_percent']}%)")
        
        print(f"\n--- ACTIVITY ---")
        print(f"Total Events: {len(state.events)}")
        if summary['activity']['days_since_activity'] is not None:
            print(f"Days Since Last Activity: {summary['activity']['days_since_activity']}")
        
        if state.status == "settled":
            print(f"\n--- SETTLEMENT ---")
            print(f"Amount: {format_currency(state.settlement_amount)}")
            print(f"Date: {state.settlement_date}")
        
        print("\n" + "-"*60)
    
    print(json.dumps(summary, indent=2 if pretty else None))


def print_history(state: NegotiationState, pretty: bool = False):
    """Print full negotiation history."""
    if pretty:
        print("\n" + "="*60)
        print(f"NEGOTIATION HISTORY: {state.case_name}")
        print("="*60)
        
        if not state.events:
            print("\nNo negotiation events recorded.")
        else:
            for i, event in enumerate(state.events, 1):
                party = "INSURANCE" if event.get("from_party") == "insurance" else "CLIENT"
                print(f"\n{i}. [{event.get('date')}] {party}: {format_currency(event.get('amount', 0))}")
                print(f"   Type: {event.get('event_type', 'unknown')}")
                if event.get('notes'):
                    print(f"   Notes: {event.get('notes')}")
        
        print("\n" + "-"*60)
    
    output = {
        "case_name": state.case_name,
        "event_count": len(state.events),
        "events": state.events
    }
    print(json.dumps(output, indent=2 if pretty else None))


def main():
    parser = argparse.ArgumentParser(
        description="Negotiation Tracker for PI Cases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Case identifier
    parser.add_argument("--case", "-c", required=True,
                        help="Case name/folder")
    
    # Actions
    parser.add_argument("--status", "-s", action="store_true",
                        help="Show current negotiation status")
    parser.add_argument("--history", action="store_true",
                        help="Show full negotiation history")
    parser.add_argument("--add-offer", type=float,
                        help="Add an offer/counteroffer (amount)")
    parser.add_argument("--settle", type=float,
                        help="Record settlement amount")
    
    # Offer details
    parser.add_argument("--from", dest="from_party", choices=["insurance", "client"],
                        help="Who made the offer")
    parser.add_argument("--type", dest="event_type", 
                        choices=["initial_demand", "offer", "counteroffer", "final_offer"],
                        default="offer", help="Type of event")
    parser.add_argument("--notes", default="",
                        help="Notes about the offer")
    
    # Setup/update negotiation
    parser.add_argument("--set-demand", type=float,
                        help="Set/update demand amount")
    parser.add_argument("--set-demand-date",
                        help="Set demand date (YYYY-MM-DD)")
    parser.add_argument("--set-insurance",
                        help="Set insurance company name")
    parser.add_argument("--set-adjuster",
                        help="Set adjuster name")
    parser.add_argument("--set-claim",
                        help="Set claim number")
    parser.add_argument("--set-limits", type=float,
                        help="Set policy limits")
    parser.add_argument("--set-status",
                        choices=["pending", "active", "stalled", "settled", "litigation"],
                        help="Set negotiation status")
    
    # Output
    parser.add_argument("--pretty", "-p", action="store_true",
                        help="Pretty print output")
    parser.add_argument("--output", "-o",
                        help="Save to specific file")
    
    # Database sync
    parser.add_argument("--sync-from-db", action="store_true",
                        help="Sync initial data from case database (insurance.json)")
    
    args = parser.parse_args()
    
    # Load existing state
    state = load_negotiation(args.case)
    
    # Handle database sync
    if args.sync_from_db:
        if not HAS_ADAPTER:
            print("Error: Case data adapter not available", file=sys.stderr)
            sys.exit(1)
        
        case = CaseData(args.case)
        active_neg = case.active_negotiation()
        
        if active_neg:
            # Sync from active negotiation in database
            if active_neg.get("insurance_company_name"):
                state.insurance_company = active_neg["insurance_company_name"]
            if active_neg.get("insurance_adjuster_name"):
                state.adjuster_name = active_neg["insurance_adjuster_name"]
            if active_neg.get("claim_number"):
                state.claim_number = active_neg["claim_number"]
            if active_neg.get("demanded_amount"):
                state.demand_amount = money(active_neg["demanded_amount"])
            if active_neg.get("date_demand_sent"):
                state.demand_date = active_neg["date_demand_sent"]
            if active_neg.get("demand_summary"):
                state.demand_summary = active_neg["demand_summary"]
            if active_neg.get("current_offer"):
                state.current_offer = money(active_neg["current_offer"])
            if active_neg.get("current_negotiation_status"):
                state.status_notes = active_neg["current_negotiation_status"]
                state.status = "active"
            if active_neg.get("settlement_amount"):
                state.settlement_amount = money(active_neg["settlement_amount"])
                state.status = "settled"
            if active_neg.get("settlement_date"):
                state.settlement_date = active_neg["settlement_date"]
            
            # Determine coverage type
            ins_type = active_neg.get("insurance_type", "")
            if "BI" in ins_type or "Bodily" in ins_type:
                state.coverage_type = "BI"
            elif "PIP" in ins_type:
                state.coverage_type = "PIP"
            elif "UM" in ins_type or "UIM" in ins_type:
                state.coverage_type = "UIM"
            
            save_negotiation(state)
            if args.pretty:
                print(f"\n✅ Synced from database: {state.insurance_company} ({state.coverage_type})")
        else:
            print("No active negotiation found in database", file=sys.stderr)
    
    # Handle setup/updates
    modified = False
    
    if args.set_demand:
        state.demand_amount = money(args.set_demand)
        modified = True
    
    if args.set_demand_date:
        state.demand_date = args.set_demand_date
        modified = True
    
    if args.set_insurance:
        state.insurance_company = args.set_insurance
        modified = True
    
    if args.set_adjuster:
        state.adjuster_name = args.set_adjuster
        modified = True
    
    if args.set_claim:
        state.claim_number = args.set_claim
        modified = True
    
    if args.set_limits:
        state.policy_limits = money(args.set_limits)
        modified = True
    
    if args.set_status:
        state.status = args.set_status
        modified = True
    
    # Handle add offer
    if args.add_offer:
        if not args.from_party:
            parser.error("--from (insurance/client) is required when adding an offer")
        
        event = add_event(state, args.add_offer, args.from_party, args.event_type, args.notes)
        modified = True
        
        if args.pretty:
            print(f"\n✅ Added {args.event_type}: {format_currency(args.add_offer)} from {args.from_party}")
    
    # Handle settlement
    if args.settle:
        event = add_event(state, args.settle, "insurance", "settlement", args.notes or "Case settled")
        modified = True
        
        if args.pretty:
            print(f"\n✅ Settlement recorded: {format_currency(args.settle)}")
    
    # Save if modified
    if modified:
        save_negotiation(state)
    
    # Output
    if args.history:
        print_history(state, args.pretty)
    elif args.status or not (args.add_offer or args.settle):
        print_status(state, args.pretty)
    
    # Exit code
    sys.exit(0)


if __name__ == "__main__":
    main()

