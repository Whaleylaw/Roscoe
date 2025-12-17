#!/usr/bin/env python3
"""
Case Data Adapter

Unified adapter for reading/writing to existing JSON data structures.
Connects new tools to the legacy data stored in Database/ folder.

Data Sources:
- medical_providers.json - Provider tracking, records/bills dates
- insurance.json - Claims, negotiations, adjusters
- liens.json - Lien holders and amounts
- notes.json - Activity log
- case_overview.json - Case metadata

Usage:
    from _adapters.case_data import CaseData
    
    # Load case data
    case = CaseData("Smith-MVA-01-15-2024")
    
    # Access data
    providers = case.medical_providers
    insurance = case.insurance_claims
    liens = case.liens
    
    # Update data
    case.update_provider("Dr. Smith", {"date_medical_records_requested": "2024-01-20"})
    case.add_note("Requested records from Dr. Smith", note_type="Medical Records")
    
    # Save changes
    case.save()
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field


def get_workspace_path() -> Path:
    """Get workspace root path."""
    # Check common locations
    if Path("/workspace_paralegal").exists():
        return Path("/workspace_paralegal")
    
    # Try relative to script
    script_dir = Path(__file__).parent.parent.parent
    if (script_dir / "Database").exists():
        return script_dir
    
    # Fallback
    return Path(".")


def get_database_path() -> Path:
    """Get database folder path."""
    workspace = get_workspace_path()
    db_path = workspace / "Database"
    if db_path.exists():
        return db_path
    
    # Try alternate location
    alt_path = Path("/Volumes/X10 Pro/Roscoe/Document_templates/existing_json")
    if alt_path.exists():
        return alt_path
    
    return db_path


def excel_date_to_str(excel_date: Union[str, float, int, None]) -> Optional[str]:
    """Convert Excel serial date to ISO date string."""
    if excel_date is None:
        return None
    
    # Already a date string
    if isinstance(excel_date, str):
        if "-" in excel_date and len(excel_date) >= 10:
            return excel_date[:10]
        try:
            # Try parsing as float string
            excel_date = float(excel_date)
        except ValueError:
            return excel_date
    
    if isinstance(excel_date, (int, float)):
        try:
            # Excel epoch is 1899-12-30
            base_date = datetime(1899, 12, 30)
            result_date = base_date + timedelta(days=int(excel_date))
            return result_date.strftime("%Y-%m-%d")
        except:
            return str(excel_date)
    
    return str(excel_date) if excel_date else None


def str_to_excel_date(date_str: Optional[str]) -> Optional[str]:
    """Convert ISO date string to ISO format (we don't use Excel dates for new data)."""
    # Just return the string - we're not converting back to Excel format
    return date_str


def load_json_file(filepath: Path) -> List[Dict]:
    """Load a JSON file, handling various formats."""
    if not filepath.exists():
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
        
        # Handle jsonb_agg wrapper
        if isinstance(data, list) and len(data) > 0:
            first = data[0]
            if isinstance(first, dict) and "jsonb_agg" in first:
                return first["jsonb_agg"] or []
            return data
        
        return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return []


def save_json_file(filepath: Path, data: List[Dict]):
    """Save data to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@dataclass
class CaseData:
    """
    Adapter for accessing case data from existing JSON structures.
    """
    project_name: str
    _medical_providers: List[Dict] = field(default_factory=list)
    _insurance: List[Dict] = field(default_factory=list)
    _liens: List[Dict] = field(default_factory=list)
    _notes: List[Dict] = field(default_factory=list)
    _overview: Dict = field(default_factory=dict)
    _modified: bool = False
    _db_path: Path = field(default_factory=get_database_path)
    
    def __post_init__(self):
        """Load data for this case."""
        self._load_all()
    
    def _load_all(self):
        """Load all data sources."""
        self._load_medical_providers()
        self._load_insurance()
        self._load_liens()
        self._load_notes()
        self._load_overview()
    
    def _filter_by_project(self, data: List[Dict]) -> List[Dict]:
        """Filter records by project name."""
        result = []
        for record in data:
            project = record.get("project_name", "")
            applies_to = record.get("applies_to_projects", [])
            
            if project.lower() == self.project_name.lower():
                result.append(record)
            elif self.project_name in applies_to:
                result.append(record)
            elif any(self.project_name.lower() in p.lower() for p in ([project] + applies_to)):
                result.append(record)
        
        return result
    
    def _load_medical_providers(self):
        """Load medical providers for this case."""
        all_providers = load_json_file(self._db_path / "medical_providers.json")
        self._medical_providers = self._filter_by_project(all_providers)
        
        # Normalize dates
        for provider in self._medical_providers:
            for date_field in ["date_treatment_started", "date_treatment_completed",
                             "date_medical_records_requested", "date_medical_records_received",
                             "date_medical_bills_requested", "medical_bills_received_date",
                             "medical_bills_follow_up_date"]:
                if date_field in provider:
                    provider[date_field] = excel_date_to_str(provider.get(date_field))
    
    def _load_insurance(self):
        """Load insurance claims for this case."""
        all_insurance = load_json_file(self._db_path / "insurance.json")
        self._insurance = self._filter_by_project(all_insurance)
        
        # Normalize dates
        for claim in self._insurance:
            for date_field in ["date_demand_sent", "date_demand_acknowledged",
                             "settlement_date", "date_coots_letter_sent",
                             "date_coots_letter_acknowledged", "date_of_pip_exhausted_notice"]:
                if date_field in claim:
                    claim[date_field] = excel_date_to_str(claim.get(date_field))
    
    def _load_liens(self):
        """Load liens for this case."""
        all_liens = load_json_file(self._db_path / "liens.json")
        self._liens = self._filter_by_project(all_liens)
        
        # Normalize dates
        for lien in self._liens:
            for date_field in ["date_notice_received", "date_lien_notice_sent",
                             "date_final_lien_requested", "date_of_final_lien_received",
                             "date_lien_paid"]:
                if date_field in lien:
                    lien[date_field] = excel_date_to_str(lien.get(date_field))
    
    def _load_notes(self):
        """Load notes for this case."""
        all_notes = load_json_file(self._db_path / "notes.json")
        self._notes = self._filter_by_project(all_notes)
    
    def _load_overview(self):
        """Load case overview."""
        all_overviews = load_json_file(self._db_path / "case_overview.json")
        for overview in all_overviews:
            if overview.get("project_name", "").lower() == self.project_name.lower():
                self._overview = overview
                break
    
    # === Properties ===
    
    @property
    def medical_providers(self) -> List[Dict]:
        """Get medical providers for this case."""
        return self._medical_providers
    
    @property
    def insurance_claims(self) -> List[Dict]:
        """Get insurance claims for this case."""
        return self._insurance
    
    @property
    def bi_claims(self) -> List[Dict]:
        """Get BI claims only."""
        return [c for c in self._insurance if "Bodily Injury" in c.get("insurance_type", "")]
    
    @property
    def pip_claims(self) -> List[Dict]:
        """Get PIP claims only."""
        return [c for c in self._insurance if "PIP" in c.get("insurance_type", "")]
    
    @property
    def uim_claims(self) -> List[Dict]:
        """Get UM/UIM claims only."""
        return [c for c in self._insurance if "UIM" in c.get("insurance_type", "") or "UM" in c.get("insurance_type", "")]
    
    @property
    def liens(self) -> List[Dict]:
        """Get liens for this case."""
        return self._liens
    
    @property
    def notes(self) -> List[Dict]:
        """Get notes for this case (most recent first)."""
        return sorted(self._notes, key=lambda x: x.get("last_activity", ""), reverse=True)
    
    @property
    def overview(self) -> Dict:
        """Get case overview."""
        return self._overview
    
    @property
    def client_name(self) -> str:
        """Get client name."""
        return self._overview.get("client_full_name", self.project_name.replace("-", " "))
    
    # === Provider Methods ===
    
    def get_provider(self, provider_name: str) -> Optional[Dict]:
        """Get a provider by name."""
        for provider in self._medical_providers:
            if provider.get("provider_full_name", "").lower() == provider_name.lower():
                return provider
        return None
    
    def get_provider_status(self, provider: Dict) -> str:
        """Derive provider status from data."""
        if provider.get("date_treatment_completed"):
            if provider.get("date_medical_records_received"):
                return "COMPLETE_WITH_RECORDS"
            elif provider.get("date_medical_records_requested"):
                return "COMPLETE_AWAITING_RECORDS"
            else:
                return "COMPLETE_NEEDS_RECORDS"
        elif provider.get("date_treatment_started"):
            return "ACTIVE"
        else:
            return "PENDING_SETUP"
    
    def update_provider(self, provider_name: str, updates: Dict) -> bool:
        """Update a provider's data."""
        for provider in self._medical_providers:
            if provider.get("provider_full_name", "").lower() == provider_name.lower():
                provider.update(updates)
                provider["updated_at"] = datetime.now().isoformat()
                self._modified = True
                return True
        return False
    
    def add_provider(self, provider_data: Dict) -> Dict:
        """Add a new provider."""
        provider_data["project_name"] = self.project_name
        provider_data["created_at"] = datetime.now().isoformat()
        provider_data["updated_at"] = datetime.now().isoformat()
        self._medical_providers.append(provider_data)
        self._modified = True
        return provider_data
    
    # === Insurance Methods ===
    
    def get_insurance_claim(self, claim_type: str = None, claim_number: str = None) -> Optional[Dict]:
        """Get an insurance claim by type or number."""
        for claim in self._insurance:
            if claim_number and claim.get("claim_number") == claim_number:
                return claim
            if claim_type and claim_type.lower() in claim.get("insurance_type", "").lower():
                return claim
        return None
    
    def update_insurance(self, claim_number: str, updates: Dict) -> bool:
        """Update an insurance claim."""
        for claim in self._insurance:
            if claim.get("claim_number") == claim_number:
                claim.update(updates)
                self._modified = True
                return True
        return False
    
    def update_insurance_by_type(self, claim_type: str, updates: Dict) -> bool:
        """Update insurance claim by type (BI, PIP, UIM)."""
        for claim in self._insurance:
            if claim_type.lower() in claim.get("insurance_type", "").lower():
                claim.update(updates)
                self._modified = True
                return True
        return False
    
    # === Lien Methods ===
    
    def get_lien(self, holder_name: str) -> Optional[Dict]:
        """Get a lien by holder name."""
        for lien in self._liens:
            if lien.get("lien_holder_name", "").lower() == holder_name.lower():
                return lien
        return None
    
    def update_lien(self, holder_name: str, updates: Dict) -> bool:
        """Update a lien."""
        for lien in self._liens:
            if lien.get("lien_holder_name", "").lower() == holder_name.lower():
                lien.update(updates)
                self._modified = True
                return True
        return False
    
    # === Note Methods ===
    
    def add_note(self, note_text: str, note_type: str = "Case Update", 
                 author: str = "Roscoe (AI Paralegal)") -> Dict:
        """Add a note to the activity log."""
        now = datetime.now()
        note = {
            "note": note_text,
            "time": now.strftime("%H:%M:%S"),
            "note_type": note_type,
            "author_name": author,
            "note_summary": note_text[:100] + "..." if len(note_text) > 100 else note_text,
            "project_name": self.project_name,
            "summary_done": True,
            "created_by_id": None,
            "last_activity": now.strftime("%Y-%m-%d"),
            "applies_to_projects": [self.project_name],
            "id": int(now.timestamp() * 1000)
        }
        self._notes.insert(0, note)
        self._modified = True
        return note
    
    # === Calculation Methods ===
    
    def total_medical_bills(self) -> float:
        """Calculate total medical bills."""
        return sum(p.get("billed_amount", 0) or 0 for p in self._medical_providers)
    
    def total_liens(self) -> float:
        """Calculate total liens."""
        return sum(l.get("final_lien_amount", 0) or l.get("amount_owed_from_settlement", 0) or 0 
                   for l in self._liens)
    
    def active_negotiation(self) -> Optional[Dict]:
        """Get the active negotiation (if any)."""
        for claim in self._insurance:
            if claim.get("is_active_negotiation"):
                return claim
        return None
    
    # === Save Methods ===
    
    def save(self):
        """Save all modified data back to JSON files."""
        if not self._modified:
            return
        
        # Note: In a full implementation, we'd merge back into master files
        # For now, save to case-specific files
        case_folder = get_workspace_path() / self.project_name
        case_folder.mkdir(parents=True, exist_ok=True)
        
        save_json_file(case_folder / "medical_providers.json", self._medical_providers)
        save_json_file(case_folder / "insurance.json", self._insurance)
        save_json_file(case_folder / "liens.json", self._liens)
        save_json_file(case_folder / "notes.json", self._notes)
        
        self._modified = False
        print(f"Saved case data to {case_folder}", file=sys.stderr)
    
    # === Summary Methods ===
    
    def summary(self) -> Dict:
        """Get a summary of the case data."""
        return {
            "project_name": self.project_name,
            "client_name": self.client_name,
            "providers": {
                "count": len(self._medical_providers),
                "active": len([p for p in self._medical_providers if self.get_provider_status(p) == "ACTIVE"]),
                "complete": len([p for p in self._medical_providers if "COMPLETE" in self.get_provider_status(p)]),
                "total_billed": self.total_medical_bills()
            },
            "insurance": {
                "count": len(self._insurance),
                "bi": len(self.bi_claims),
                "pip": len(self.pip_claims),
                "uim": len(self.uim_claims),
                "active_negotiation": self.active_negotiation() is not None
            },
            "liens": {
                "count": len(self._liens),
                "total": self.total_liens()
            },
            "notes_count": len(self._notes)
        }


def main():
    """CLI for testing the adapter."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Case Data Adapter")
    parser.add_argument("--case", "-c", required=True, help="Case/project name")
    parser.add_argument("--summary", "-s", action="store_true", help="Show case summary")
    parser.add_argument("--providers", action="store_true", help="List providers")
    parser.add_argument("--insurance", action="store_true", help="List insurance claims")
    parser.add_argument("--liens", action="store_true", help="List liens")
    parser.add_argument("--notes", type=int, default=0, help="Show N recent notes")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print")
    
    args = parser.parse_args()
    
    case = CaseData(args.case)
    
    if args.summary:
        output = case.summary()
    elif args.providers:
        output = {"providers": case.medical_providers}
    elif args.insurance:
        output = {"insurance": case.insurance_claims}
    elif args.liens:
        output = {"liens": case.liens}
    elif args.notes > 0:
        output = {"notes": case.notes[:args.notes]}
    else:
        output = case.summary()
    
    print(json.dumps(output, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()

