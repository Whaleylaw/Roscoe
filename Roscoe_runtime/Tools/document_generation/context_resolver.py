#!/usr/bin/env python3
"""
Context Resolver for Template Filling

Resolves context-dependent data like which insurance policy, lien holder, 
or medical provider to use when filling templates. Auto-detects when there's
only one option available.

Usage:
    resolver = ContextResolver(case_name="Smith-MVA-01-15-2024")
    
    # Auto-detect PIP insurance
    pip_context = resolver.resolve_insurance_context("pip")
    
    # Get specific lien holder
    lien_context = resolver.resolve_lien_context(lien_holder="Humana")
    
    # List available options
    options = resolver.get_available_insurance_types()
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


# Default paths
WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", os.environ.get("ROSCOE_ROOT", str(Path(__file__).resolve().parents[2]))))
DATABASE_DIR = WORKSPACE_ROOT / "Database"


class ContextResolver:
    """Resolves context for template placeholder filling."""
    
    def __init__(self, case_name: str, workspace_root: Path = None):
        """
        Initialize context resolver for a specific case.
        
        Args:
            case_name: The project/case name (e.g., "Smith-MVA-01-15-2024")
            workspace_root: Optional workspace root path override
        """
        self.case_name = case_name
        self.workspace_root = workspace_root or WORKSPACE_ROOT
        self.database_dir = self.workspace_root / "Database"
        
        # Cache loaded data
        self._case_overview = None
        self._insurance_records = None
        self._lien_records = None
        self._medical_provider_records = None
        self._directory = None
        self._litigation = None
        self._clients = None
    
    # ========== Data Loading ==========
    
    def _load_json(self, filename: str) -> List[Dict]:
        """Load a JSON database file."""
        path = self.database_dir / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _get_case_overview(self) -> Optional[Dict]:
        """Load and cache case overview for this case."""
        if self._case_overview is None:
            data = self._load_json("case_overview.json")
            for record in data:
                if record.get("project_name") == self.case_name:
                    self._case_overview = record
                    break
        return self._case_overview
    
    def _get_insurance_records(self) -> List[Dict]:
        """Load and cache insurance records for this case."""
        if self._insurance_records is None:
            data = self._load_json("insurance.json")
            self._insurance_records = [
                r for r in data 
                if r.get("project_name") == self.case_name
            ]
        return self._insurance_records
    
    def _get_lien_records(self) -> List[Dict]:
        """Load and cache lien records for this case."""
        if self._lien_records is None:
            data = self._load_json("liens.json")
            self._lien_records = [
                r for r in data 
                if r.get("project_name") == self.case_name
            ]
        return self._lien_records
    
    def _get_medical_provider_records(self) -> List[Dict]:
        """Load and cache medical provider records for this case."""
        if self._medical_provider_records is None:
            data = self._load_json("medical_providers.json")
            self._medical_provider_records = [
                r for r in data 
                if r.get("project_name") == self.case_name
            ]
        return self._medical_provider_records
    
    def _get_directory(self) -> List[Dict]:
        """Load and cache directory."""
        if self._directory is None:
            self._directory = self._load_json("directory.json")
        return self._directory
    
    def _get_litigation(self) -> Optional[Dict]:
        """Load and cache litigation data for this case."""
        if self._litigation is None:
            data = self._load_json("litigation.json")
            for record in data:
                if record.get("project_name") == self.case_name:
                    self._litigation = record
                    break
        return self._litigation
    
    def _get_clients(self) -> Optional[Dict]:
        """Load and cache client data for this case."""
        if self._clients is None:
            data = self._load_json("clients.json")
            for record in data:
                if record.get("project_name") == self.case_name:
                    self._clients = record
                    break
        return self._clients
    
    # ========== Directory Lookups ==========
    
    def lookup_in_directory(self, name: str) -> Optional[Dict]:
        """
        Look up a person/company in the directory by name.
        
        Args:
            name: Full name to search for
            
        Returns:
            Directory entry or None if not found
        """
        directory = self._get_directory()
        name_lower = name.lower().strip() if name else ""
        
        for entry in directory:
            full_name = entry.get("full_name", "").lower().strip()
            if full_name == name_lower or name_lower in full_name or full_name in name_lower:
                return entry
        
        return None
    
    def format_address_block(self, entry: Dict) -> str:
        """Format a directory entry as an address block."""
        if not entry:
            return ""
        
        lines = []
        if entry.get("full_name"):
            lines.append(entry["full_name"])
        if entry.get("address"):
            # Address might be multi-line already
            addr = entry["address"]
            if "," in addr:
                # Try to format nicely
                parts = addr.split(",")
                if len(parts) >= 2:
                    # First part is usually street
                    lines.append(parts[0].strip())
                    # Rest is city/state/zip
                    lines.append(",".join(parts[1:]).strip())
                else:
                    lines.append(addr)
            else:
                lines.append(addr)
        
        return "\n".join(lines)
    
    # ========== Insurance Context ==========
    
    def get_available_insurance_types(self) -> List[str]:
        """Get list of insurance types available for this case."""
        records = self._get_insurance_records()
        types = set()
        
        for record in records:
            ins_type = record.get("insurance_type", "").lower()
            if ins_type:
                types.add(ins_type)
        
        return list(types)
    
    def get_insurance_by_type(self, insurance_type: str) -> List[Dict]:
        """Get all insurance records of a specific type."""
        records = self._get_insurance_records()
        ins_type_lower = insurance_type.lower()
        
        return [
            r for r in records 
            if r.get("insurance_type", "").lower() == ins_type_lower
        ]
    
    def resolve_insurance_context(
        self, 
        insurance_type: str = None,
        company_name: str = None,
        adjuster_name: str = None
    ) -> Tuple[Optional[Dict], str]:
        """
        Resolve insurance context for template filling.
        
        Auto-detects if there's only one option. Returns error message
        if multiple options exist and none specified.
        
        Args:
            insurance_type: Type of insurance (pip, bi, um)
            company_name: Insurance company name (optional filter)
            adjuster_name: Adjuster name (optional filter)
            
        Returns:
            Tuple of (insurance_record, error_message)
            If successful, error_message is empty string
        """
        records = self._get_insurance_records()
        
        # Filter by type if specified
        if insurance_type:
            ins_type_lower = insurance_type.lower()
            records = [
                r for r in records 
                if r.get("insurance_type", "").lower() == ins_type_lower
            ]
        
        # Filter by company name if specified
        if company_name:
            company_lower = company_name.lower()
            records = [
                r for r in records 
                if company_lower in r.get("insurance_company_name", "").lower()
            ]
        
        # Filter by adjuster name if specified
        if adjuster_name:
            adjuster_lower = adjuster_name.lower()
            records = [
                r for r in records 
                if adjuster_lower in r.get("insurance_adjuster_name", "").lower()
            ]
        
        if len(records) == 0:
            return None, f"No insurance records found for type '{insurance_type}'"
        elif len(records) == 1:
            return records[0], ""
        else:
            # Multiple records - need more specific selection
            companies = [r.get("insurance_company_name", "Unknown") for r in records]
            return None, f"Multiple insurance records found. Please specify: {', '.join(companies)}"
    
    def get_insurance_context_data(self, insurance_record: Dict) -> Dict[str, Any]:
        """
        Build context data dictionary from an insurance record.
        Includes directory lookups for adjuster and company info.
        """
        context = {
            "claim_number": insurance_record.get("claim_number", ""),
            "insurance_type": insurance_record.get("insurance_type", ""),
            "insurance_company_name": insurance_record.get("insurance_company_name", ""),
            "insurance_adjuster_name": insurance_record.get("insurance_adjuster_name", ""),
            "coverage_confirmation": insurance_record.get("coverage_confirmation", ""),
            "date_demand_sent": insurance_record.get("date_demand_sent", ""),
        }
        
        # Look up adjuster in directory
        adjuster_name = insurance_record.get("insurance_adjuster_name")
        if adjuster_name:
            adjuster_entry = self.lookup_in_directory(adjuster_name)
            if adjuster_entry:
                context["adjuster_email"] = adjuster_entry.get("email", "")
                context["adjuster_phone"] = adjuster_entry.get("phone", "")
                context["adjuster_address"] = adjuster_entry.get("address", "")
                context["adjuster_address_block"] = self.format_address_block(adjuster_entry)
        
        # Look up company in directory
        company_name = insurance_record.get("insurance_company_name")
        if company_name:
            company_entry = self.lookup_in_directory(company_name)
            if company_entry:
                context["company_address"] = company_entry.get("address", "")
                context["company_address_block"] = self.format_address_block(company_entry)
                context["company_phone"] = company_entry.get("phone", "")
        
        return context
    
    # ========== Lien Context ==========
    
    def get_available_lien_holders(self) -> List[str]:
        """Get list of lien holders for this case."""
        records = self._get_lien_records()
        return [r.get("lien_holder_name", "") for r in records if r.get("lien_holder_name")]
    
    def resolve_lien_context(
        self, 
        lien_holder: str = None
    ) -> Tuple[Optional[Dict], str]:
        """
        Resolve lien context for template filling.
        
        Args:
            lien_holder: Lien holder name (optional if only one exists)
            
        Returns:
            Tuple of (lien_record, error_message)
        """
        records = self._get_lien_records()
        
        if lien_holder:
            holder_lower = lien_holder.lower()
            records = [
                r for r in records 
                if holder_lower in r.get("lien_holder_name", "").lower()
            ]
        
        if len(records) == 0:
            return None, "No lien records found"
        elif len(records) == 1:
            return records[0], ""
        else:
            holders = [r.get("lien_holder_name", "Unknown") for r in records]
            return None, f"Multiple lien holders found. Please specify: {', '.join(holders)}"
    
    def get_lien_context_data(self, lien_record: Dict) -> Dict[str, Any]:
        """Build context data dictionary from a lien record."""
        context = {
            "lien_holder_name": lien_record.get("lien_holder_name", ""),
            "lien_id": lien_record.get("id", ""),
            "final_lien_amount": lien_record.get("final_lien_amount", ""),
            "date_lien_notice_sent": lien_record.get("date_lien_notice_sent", ""),
            "date_final_lien_requested": lien_record.get("date_final_lien_requested", ""),
        }
        
        # Look up lienholder in directory
        holder_name = lien_record.get("lien_holder_name")
        if holder_name:
            holder_entry = self.lookup_in_directory(holder_name)
            if holder_entry:
                context["lienholder_address"] = holder_entry.get("address", "")
                context["lienholder_address_block"] = self.format_address_block(holder_entry)
                context["lienholder_phone"] = holder_entry.get("phone", "")
                context["lienholder_email"] = holder_entry.get("email", "")
        
        return context
    
    # ========== Medical Provider Context ==========
    
    def get_available_medical_providers(self) -> List[str]:
        """Get list of medical providers for this case."""
        records = self._get_medical_provider_records()
        return [r.get("provider_full_name", "") for r in records if r.get("provider_full_name")]
    
    def resolve_medical_provider_context(
        self, 
        provider_name: str = None
    ) -> Tuple[Optional[Dict], str]:
        """
        Resolve medical provider context for template filling.
        
        Args:
            provider_name: Provider name (optional if only one exists)
            
        Returns:
            Tuple of (provider_record, error_message)
        """
        records = self._get_medical_provider_records()
        
        if provider_name:
            provider_lower = provider_name.lower()
            records = [
                r for r in records 
                if provider_lower in r.get("provider_full_name", "").lower()
            ]
        
        if len(records) == 0:
            return None, "No medical provider records found"
        elif len(records) == 1:
            return records[0], ""
        else:
            providers = [r.get("provider_full_name", "Unknown") for r in records]
            return None, f"Multiple providers found. Please specify: {', '.join(providers)}"
    
    def get_medical_provider_context_data(self, provider_record: Dict) -> Dict[str, Any]:
        """Build context data dictionary from a medical provider record."""
        context = {
            "provider_name": provider_record.get("provider_full_name", ""),
            "billed_amount": provider_record.get("billed_amount", ""),
            "date_treatment_started": provider_record.get("date_treatment_started", ""),
            "date_treatment_completed": provider_record.get("date_treatment_completed", ""),
        }
        
        # Look up provider in directory
        provider_name = provider_record.get("provider_full_name")
        if provider_name:
            provider_entry = self.lookup_in_directory(provider_name)
            if provider_entry:
                context["provider_address"] = provider_entry.get("address", "")
                context["provider_address_block"] = self.format_address_block(provider_entry)
                context["provider_phone"] = provider_entry.get("phone", "")
                context["provider_email"] = provider_entry.get("email", "")
        
        return context
    
    # ========== Case Base Data ==========
    
    def get_case_base_data(self) -> Dict[str, Any]:
        """Get base case data that doesn't require context selection."""
        overview = self._get_case_overview() or {}
        clients = self._get_clients() or {}
        litigation = self._get_litigation() or {}
        
        # Extract incident type from project name
        project_name = overview.get("project_name", "")
        incident_type = "incident"
        if "MVA" in project_name:
            incident_type = "motor vehicle collision"
        elif "S&F" in project_name or "SF" in project_name:
            incident_type = "slip and fall incident"
        elif "WC" in project_name:
            incident_type = "workplace injury"
        
        # Format client name components
        client_name = overview.get("client_name", "")
        first_name = client_name.split()[0] if client_name else ""
        
        # Format SSN masked
        ssn = clients.get("ssn", "")
        if ssn and len(ssn) >= 4:
            ssn_masked = f"XXX-XX-{ssn[-4:]}"
        else:
            ssn_masked = ssn
        
        # Format accident date
        accident_date = overview.get("accident_date", "")
        accident_date_formatted = accident_date
        if accident_date:
            try:
                from datetime import datetime as dt
                parsed = dt.strptime(accident_date, "%Y-%m-%d")
                accident_date_formatted = parsed.strftime("%B %d, %Y")
            except:
                pass
        
        return {
            # Case identifiers
            "project_name": project_name,
            "case_type": incident_type,
            "id": project_name,
            
            # Client info
            "client_name": client_name,
            "client_firstname": first_name,
            "client_address": overview.get("client_address", ""),
            "client_address1Block": overview.get("client_address", ""),
            "client_addressBlock": overview.get("client_address", ""),
            "client_phone": overview.get("client_phone", ""),
            "client_email": overview.get("client_email", ""),
            "client_dob": clients.get("dob", ""),
            "client_birthDate": clients.get("dob", ""),
            "client_ssn": ssn,
            "client_ssn_masked": ssn_masked,
            
            # Case info
            "accident_date": accident_date,
            "incidentDate": accident_date_formatted,  # Formatted version
            "incident_type": incident_type,
            "phase": overview.get("phase", ""),
            
            # Intake-style aliases
            "intake_incidenttype": incident_type,
            "intake_clientInformation_name": client_name,
            
            # Litigation info
            "client_deposition_date": litigation.get("client_deposition_date", ""),
            "client_deposition_time": litigation.get("client_deposition_time", ""),
            "litigation_clientDepositionDate": litigation.get("client_deposition_date", ""),
            "litigation_clientDepositionTime": litigation.get("client_deposition_time", ""),
            "sol_date": litigation.get("sol_date", ""),
            
            # Computed dates
            "today_long": datetime.now().strftime("%B %d, %Y"),
            "today_short": datetime.now().strftime("%m/%d/%Y"),
            "TODAY_LONG": datetime.now().strftime("%B %d, %Y"),
            "TODAY": datetime.now().strftime("%B %d, %Y"),
        }
    
    # ========== Full Context Resolution ==========
    
    def resolve_full_context(
        self,
        required_context: List[str],
        insurance_type: str = None,
        lien_holder: str = None,
        provider_name: str = None
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Resolve all context needed for a template.
        
        Args:
            required_context: List of required context types from template registry
            insurance_type: Insurance type if needed
            lien_holder: Lien holder name if needed
            provider_name: Provider name if needed
            
        Returns:
            Tuple of (context_data_dict, list_of_errors)
        """
        context = self.get_case_base_data()
        errors = []
        
        for ctx_type in required_context:
            if ctx_type.startswith("insurance_"):
                # Insurance context required
                ins_type = ctx_type.replace("insurance_", "")
                if ins_type == "selected":
                    ins_type = insurance_type
                
                record, error = self.resolve_insurance_context(insurance_type=ins_type)
                if error:
                    errors.append(error)
                elif record:
                    ins_data = self.get_insurance_context_data(record)
                    context["insurance"] = ins_data
                    
            elif ctx_type == "lien":
                # Lien context required
                record, error = self.resolve_lien_context(lien_holder=lien_holder)
                if error:
                    errors.append(error)
                elif record:
                    lien_data = self.get_lien_context_data(record)
                    context["lien"] = lien_data
                    
            elif ctx_type == "medical_provider":
                # Medical provider context required
                record, error = self.resolve_medical_provider_context(provider_name=provider_name)
                if error:
                    errors.append(error)
                elif record:
                    provider_data = self.get_medical_provider_context_data(record)
                    context["medical_provider"] = provider_data
                    
            elif ctx_type == "litigation":
                # Litigation context - already included in base data
                pass
        
        return context, errors


def main():
    """Test the context resolver."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python context_resolver.py <case_name>")
        sys.exit(1)
    
    case_name = sys.argv[1]
    resolver = ContextResolver(case_name)
    
    print(f"=== Context for {case_name} ===\n")
    
    # Base data
    base = resolver.get_case_base_data()
    print("Base Case Data:")
    for k, v in base.items():
        if v:
            print(f"  {k}: {v}")
    
    # Insurance types
    print("\nAvailable Insurance Types:")
    for ins_type in resolver.get_available_insurance_types():
        print(f"  - {ins_type}")
        records = resolver.get_insurance_by_type(ins_type)
        for r in records:
            print(f"    Company: {r.get('insurance_company_name', 'N/A')}")
            print(f"    Adjuster: {r.get('insurance_adjuster_name', 'N/A')}")
    
    # Lien holders
    print("\nAvailable Lien Holders:")
    for holder in resolver.get_available_lien_holders():
        print(f"  - {holder}")
    
    # Medical providers
    print("\nAvailable Medical Providers:")
    for provider in resolver.get_available_medical_providers():
        print(f"  - {provider}")


if __name__ == "__main__":
    main()

