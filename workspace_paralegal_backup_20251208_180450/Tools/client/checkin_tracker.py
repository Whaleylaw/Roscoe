#!/usr/bin/env python3
"""
Client Check-in Tracker Tool

Tracks bi-weekly client check-ins during treatment phase.
Records treatment status, new providers, and flags important changes.

Usage:
    # Schedule next check-in
    python checkin_tracker.py --case "Smith-MVA" --schedule --days 14
    
    # Record a check-in
    python checkin_tracker.py --case "Smith-MVA" --checkin \
      --still-treating \
      --providers "Dr. Smith (ortho), PT Plus" \
      --new-provider "Pain Management Associates" \
      --notes "Client reports improvement but still has neck pain"
    
    # View check-in history
    python checkin_tracker.py --case "Smith-MVA" --history
    
    # View treatment status
    python checkin_tracker.py --case "Smith-MVA" --status

Data Storage:
    Check-in data stored in case folder: /case_name/checkins.json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

# Try to import case data adapter
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _adapters.case_data import CaseData
    HAS_ADAPTER = True
except ImportError:
    HAS_ADAPTER = False


@dataclass
class CheckInRecord:
    """A single client check-in."""
    date: str
    still_treating: bool
    current_providers: List[str] = field(default_factory=list)
    new_providers: List[str] = field(default_factory=list)
    discharged_providers: List[str] = field(default_factory=list)
    treatment_notes: str = ""
    pain_level: Optional[int] = None  # 1-10 scale
    working: Optional[bool] = None
    flags: List[str] = field(default_factory=list)
    next_checkin: str = ""
    recorded_by: str = "agent"
    
    def to_dict(self):
        return asdict(self)


@dataclass
class CheckInState:
    """Client check-in tracking state."""
    case_name: str
    client_name: str = ""
    accident_date: str = ""
    
    # Current treatment status
    treatment_status: str = "active"  # active, discharged, gap, unknown
    last_treatment_date: str = ""
    days_since_treatment: int = 0
    
    # Provider tracking
    all_providers: List[str] = field(default_factory=list)
    active_providers: List[str] = field(default_factory=list)
    
    # Check-in schedule
    last_checkin: str = ""
    next_checkin: str = ""
    checkin_interval_days: int = 14
    
    # History
    checkins: List[dict] = field(default_factory=list)
    
    # Flags and alerts
    active_flags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self):
        return asdict(self)


def get_checkin_file(case_name: str) -> Path:
    """Get path to checkins.json for a case."""
    workspace = Path("/workspace_paralegal") if Path("/workspace_paralegal").exists() else Path(".")
    
    case_folder = workspace / case_name
    if not case_folder.exists():
        for folder in workspace.iterdir():
            if folder.is_dir() and case_name.lower() in folder.name.lower():
                case_folder = folder
                break
    
    case_folder.mkdir(parents=True, exist_ok=True)
    return case_folder / "checkins.json"


def load_checkin_state(case_name: str) -> CheckInState:
    """Load check-in state from file."""
    filepath = get_checkin_file(case_name)
    
    if filepath.exists():
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            checkins = data.pop("checkins", [])
            state = CheckInState(**{k: v for k, v in data.items() if k in CheckInState.__dataclass_fields__})
            state.checkins = checkins
            return state
        except Exception as e:
            print(f"Warning: Could not load existing check-ins: {e}", file=sys.stderr)
    
    return CheckInState(
        case_name=case_name,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )


def save_checkin_state(state: CheckInState):
    """Save check-in state to file."""
    filepath = get_checkin_file(state.case_name)
    state.updated_at = datetime.now().isoformat()
    
    with open(filepath, 'w') as f:
        json.dump(state.to_dict(), f, indent=2)
    
    print(f"Saved to: {filepath}", file=sys.stderr)


def calculate_days_since(date_str: str) -> int:
    """Calculate days since a date."""
    if not date_str:
        return -1
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return (datetime.now() - date).days
    except:
        return -1


def check_for_flags(state: CheckInState, record: CheckInRecord) -> List[str]:
    """Check for important flags that need attention."""
    flags = []
    
    # New provider added
    if record.new_providers:
        flags.append(f"NEW_PROVIDER: {', '.join(record.new_providers)}")
    
    # Provider discharged
    if record.discharged_providers:
        flags.append(f"DISCHARGED: {', '.join(record.discharged_providers)}")
    
    # Treatment ended
    if not record.still_treating:
        flags.append("TREATMENT_COMPLETE: Client reports no longer treating")
    
    # High pain level
    if record.pain_level and record.pain_level >= 8:
        flags.append(f"HIGH_PAIN: Client reports {record.pain_level}/10 pain")
    
    # Not working
    if record.working is False:
        flags.append("NOT_WORKING: Client still out of work")
    
    # Treatment gap (check if > 30 days since last check-in with active treatment)
    if state.last_checkin:
        days_since_last = calculate_days_since(state.last_checkin)
        if days_since_last > 30:
            flags.append(f"TREATMENT_GAP: {days_since_last} days since last check-in")
    
    return flags


def record_checkin(state: CheckInState, 
                   still_treating: bool,
                   providers: List[str] = None,
                   new_providers: List[str] = None,
                   discharged: List[str] = None,
                   notes: str = "",
                   pain_level: int = None,
                   working: bool = None,
                   next_days: int = 14) -> CheckInRecord:
    """Record a client check-in."""
    
    today = datetime.now().strftime("%Y-%m-%d")
    next_date = (datetime.now() + timedelta(days=next_days)).strftime("%Y-%m-%d")
    
    record = CheckInRecord(
        date=today,
        still_treating=still_treating,
        current_providers=providers or [],
        new_providers=new_providers or [],
        discharged_providers=discharged or [],
        treatment_notes=notes,
        pain_level=pain_level,
        working=working,
        next_checkin=next_date
    )
    
    # Check for flags
    record.flags = check_for_flags(state, record)
    
    # Update state
    state.checkins.append(record.to_dict())
    state.last_checkin = today
    state.next_checkin = next_date
    
    # Update treatment status
    if still_treating:
        state.treatment_status = "active"
        state.last_treatment_date = today
    else:
        state.treatment_status = "discharged"
    
    # Update provider lists
    if new_providers:
        for p in new_providers:
            if p not in state.all_providers:
                state.all_providers.append(p)
            if p not in state.active_providers:
                state.active_providers.append(p)
    
    if discharged:
        for p in discharged:
            if p in state.active_providers:
                state.active_providers.remove(p)
    
    if providers:
        state.active_providers = providers
    
    # Update active flags
    state.active_flags = record.flags
    
    return record


def schedule_checkin(state: CheckInState, days: int = 14):
    """Schedule the next check-in."""
    next_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    state.next_checkin = next_date
    state.checkin_interval_days = days
    return next_date


def get_checkin_questions() -> List[str]:
    """Return standard check-in questions."""
    return [
        "Are you still treating for your injuries?",
        "Which providers are you currently seeing?",
        "Have you started with any new providers since we last spoke?",
        "Have you been discharged from any providers?",
        "On a scale of 1-10, how would you rate your pain today?",
        "Are you currently working?",
        "Do you have any upcoming appointments scheduled?",
        "Is there anything else you'd like me to know about your treatment?"
    ]


def print_status(state: CheckInState, pretty: bool = False):
    """Print current check-in status."""
    
    # Calculate days
    days_since_checkin = calculate_days_since(state.last_checkin)
    days_until_next = calculate_days_since(state.next_checkin) * -1 if state.next_checkin else None
    
    summary = {
        "case_name": state.case_name,
        "treatment_status": state.treatment_status,
        "active_providers": state.active_providers,
        "all_providers_count": len(state.all_providers),
        "last_checkin": state.last_checkin,
        "days_since_checkin": days_since_checkin,
        "next_checkin": state.next_checkin,
        "days_until_next": days_until_next,
        "total_checkins": len(state.checkins),
        "active_flags": state.active_flags,
        "checkin_overdue": days_until_next is not None and days_until_next < 0
    }
    
    if pretty:
        print("\n" + "="*60)
        print(f"CHECK-IN STATUS: {state.case_name}")
        print("="*60)
        
        status_emoji = {"active": "🟢", "discharged": "✅", "gap": "⚠️", "unknown": "❓"}
        print(f"\nTreatment Status: {status_emoji.get(state.treatment_status, '')} {state.treatment_status.upper()}")
        
        print(f"\n--- PROVIDERS ---")
        print(f"Active: {', '.join(state.active_providers) if state.active_providers else 'None'}")
        print(f"Total Seen: {len(state.all_providers)}")
        
        print(f"\n--- CHECK-IN SCHEDULE ---")
        print(f"Last Check-in: {state.last_checkin or 'Never'}")
        if days_since_checkin >= 0:
            print(f"Days Since: {days_since_checkin}")
        print(f"Next Scheduled: {state.next_checkin or 'Not scheduled'}")
        if days_until_next is not None:
            if days_until_next < 0:
                print(f"⚠️  OVERDUE by {abs(days_until_next)} days!")
            else:
                print(f"Due in: {days_until_next} days")
        
        print(f"\n--- HISTORY ---")
        print(f"Total Check-ins: {len(state.checkins)}")
        
        if state.active_flags:
            print(f"\n--- ⚠️  ACTIVE FLAGS ---")
            for flag in state.active_flags:
                print(f"  • {flag}")
        
        print("\n" + "-"*60)
    
    print(json.dumps(summary, indent=2 if pretty else None))


def print_history(state: CheckInState, pretty: bool = False):
    """Print check-in history."""
    
    if pretty:
        print("\n" + "="*60)
        print(f"CHECK-IN HISTORY: {state.case_name}")
        print("="*60)
        
        if not state.checkins:
            print("\nNo check-ins recorded.")
        else:
            for i, checkin in enumerate(state.checkins, 1):
                status = "🟢 Still Treating" if checkin.get("still_treating") else "✅ Treatment Complete"
                print(f"\n{i}. [{checkin.get('date')}] {status}")
                
                if checkin.get("current_providers"):
                    print(f"   Providers: {', '.join(checkin['current_providers'])}")
                
                if checkin.get("new_providers"):
                    print(f"   ➕ New: {', '.join(checkin['new_providers'])}")
                
                if checkin.get("discharged_providers"):
                    print(f"   ➖ Discharged: {', '.join(checkin['discharged_providers'])}")
                
                if checkin.get("pain_level"):
                    print(f"   Pain Level: {checkin['pain_level']}/10")
                
                if checkin.get("treatment_notes"):
                    print(f"   Notes: {checkin['treatment_notes']}")
                
                if checkin.get("flags"):
                    print(f"   ⚠️  Flags: {', '.join(checkin['flags'])}")
        
        print("\n" + "-"*60)
    
    output = {
        "case_name": state.case_name,
        "checkin_count": len(state.checkins),
        "checkins": state.checkins
    }
    print(json.dumps(output, indent=2 if pretty else None))


def print_questions(pretty: bool = False):
    """Print standard check-in questions."""
    questions = get_checkin_questions()
    
    if pretty:
        print("\n" + "="*60)
        print("STANDARD CHECK-IN QUESTIONS")
        print("="*60 + "\n")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
        print("\n" + "-"*60)
    
    print(json.dumps({"questions": questions}, indent=2 if pretty else None))


def main():
    parser = argparse.ArgumentParser(
        description="Client Check-in Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Case identifier
    parser.add_argument("--case", "-c",
                        help="Case name/folder")
    
    # Actions
    parser.add_argument("--status", "-s", action="store_true",
                        help="Show current check-in status")
    parser.add_argument("--history", action="store_true",
                        help="Show check-in history")
    parser.add_argument("--checkin", action="store_true",
                        help="Record a new check-in")
    parser.add_argument("--schedule", action="store_true",
                        help="Schedule next check-in")
    parser.add_argument("--questions", action="store_true",
                        help="Show standard check-in questions")
    
    # Check-in details
    parser.add_argument("--still-treating", action="store_true",
                        help="Client is still treating")
    parser.add_argument("--treatment-complete", action="store_true",
                        help="Client has completed treatment")
    parser.add_argument("--providers", 
                        help="Current providers (comma-separated)")
    parser.add_argument("--new-provider",
                        help="New provider(s) added (comma-separated)")
    parser.add_argument("--discharged",
                        help="Provider(s) client discharged from (comma-separated)")
    parser.add_argument("--notes",
                        help="Treatment notes")
    parser.add_argument("--pain", type=int, choices=range(1, 11),
                        help="Pain level 1-10")
    parser.add_argument("--working", action="store_true",
                        help="Client is working")
    parser.add_argument("--not-working", action="store_true",
                        help="Client is not working")
    
    # Scheduling
    parser.add_argument("--days", type=int, default=14,
                        help="Days until next check-in (default: 14)")
    
    # Setup
    parser.add_argument("--set-client",
                        help="Set client name")
    parser.add_argument("--set-accident-date",
                        help="Set accident date (YYYY-MM-DD)")
    
    # Output
    parser.add_argument("--pretty", "-p", action="store_true",
                        help="Pretty print output")
    
    # Database sync
    parser.add_argument("--sync-providers", action="store_true",
                        help="Sync provider list from case database (medical_providers.json)")
    
    args = parser.parse_args()
    
    # Questions don't need a case
    if args.questions:
        print_questions(args.pretty)
        sys.exit(0)
    
    # All other actions need a case
    if not args.case:
        parser.error("--case is required")
    
    # Load state
    state = load_checkin_state(args.case)
    modified = False
    
    # Handle database sync
    if args.sync_providers:
        if not HAS_ADAPTER:
            print("Error: Case data adapter not available", file=sys.stderr)
            sys.exit(1)
        
        case = CaseData(args.case)
        
        # Get client name from overview
        if case.client_name and case.client_name != args.case:
            state.client_name = case.client_name
        
        # Get accident date from overview
        if case.overview.get("accident_date"):
            state.accident_date = case.overview["accident_date"]
        
        # Get provider info
        active_providers = []
        for provider in case.medical_providers:
            status = case.get_provider_status(provider)
            if status == "ACTIVE":
                active_providers.append(provider.get("provider_full_name", "Unknown"))
        
        if active_providers:
            state.all_providers = list(set(state.all_providers + active_providers))
        
        state.active_providers = active_providers
        
        modified = True
        if args.pretty:
            print(f"\n✅ Synced from database: {len(active_providers)} active providers, {len(case.medical_providers)} total")
    
    # Handle setup
    if args.set_client:
        state.client_name = args.set_client
        modified = True
    
    if args.set_accident_date:
        state.accident_date = args.set_accident_date
        modified = True
    
    # Handle scheduling
    if args.schedule:
        next_date = schedule_checkin(state, args.days)
        modified = True
        if args.pretty:
            print(f"\n✅ Next check-in scheduled for: {next_date}")
    
    # Handle check-in recording
    if args.checkin:
        still_treating = args.still_treating or not args.treatment_complete
        
        providers = [p.strip() for p in args.providers.split(",")] if args.providers else None
        new_providers = [p.strip() for p in args.new_provider.split(",")] if args.new_provider else None
        discharged = [p.strip() for p in args.discharged.split(",")] if args.discharged else None
        
        working = None
        if args.working:
            working = True
        elif args.not_working:
            working = False
        
        record = record_checkin(
            state,
            still_treating=still_treating,
            providers=providers,
            new_providers=new_providers,
            discharged=discharged,
            notes=args.notes or "",
            pain_level=args.pain,
            working=working,
            next_days=args.days
        )
        modified = True
        
        if args.pretty:
            print(f"\n✅ Check-in recorded for {args.case}")
            if record.flags:
                print("\n⚠️  FLAGS DETECTED:")
                for flag in record.flags:
                    print(f"  • {flag}")
    
    # Save if modified
    if modified:
        save_checkin_state(state)
    
    # Output
    if args.history:
        print_history(state, args.pretty)
    elif args.status or not (args.checkin or args.schedule):
        print_status(state, args.pretty)
    
    sys.exit(0)


if __name__ == "__main__":
    main()

