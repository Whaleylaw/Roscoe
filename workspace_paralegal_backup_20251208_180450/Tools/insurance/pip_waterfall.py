#!/usr/bin/env python3
"""
Kentucky PIP Waterfall Determination Tool

Determines the correct PIP (Personal Injury Protection) insurer for a Kentucky
motor vehicle accident case based on the statutory waterfall priority rules.

Kentucky PIP Waterfall Logic:
1. Named insured on title of vehicle occupied → that vehicle's insurer
2. Vehicle occupied was insured → that vehicle's insurer  
3. Client has own auto insurance → client's insurer
4. Household member has auto insurance → household member's insurer
5. None of the above → Kentucky Assigned Claims Plan (KAC)

CRITICAL: If client is on title of an UNINSURED vehicle, they are DISQUALIFIED from PIP.

Usage:
    # Interactive mode (asks questions)
    python pip_waterfall.py --interactive
    
    # With pre-filled answers
    python pip_waterfall.py --client-on-title no --vehicle-insured yes --vehicle-insurer "State Farm"
    
    # From JSON file
    python pip_waterfall.py --from-json /path/to/pip_answers.json

Examples:
    python pip_waterfall.py --interactive --pretty
    python pip_waterfall.py --client-on-title yes --vehicle-insured yes --vehicle-insurer "GEICO" --policy "12345"
    python pip_waterfall.py --client-on-title no --vehicle-insured no --client-has-insurance yes --client-insurer "Progressive"
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class PIPDetermination:
    """Result of PIP waterfall analysis."""
    pip_insurer: Optional[str]
    pip_insurer_type: str  # "vehicle", "client", "household", "kac", "disqualified"
    policy_number: Optional[str]
    contact_info: Optional[str]
    is_kac: bool
    is_disqualified: bool
    disqualification_reason: Optional[str]
    waterfall_step: int
    waterfall_path: list[str]
    recommendation: str
    next_steps: list[str]
    template_to_use: str
    timestamp: str


def run_waterfall(
    client_on_title: Optional[bool] = None,
    vehicle_insured: Optional[bool] = None,
    vehicle_insurer: Optional[str] = None,
    vehicle_policy: Optional[str] = None,
    vehicle_insurer_contact: Optional[str] = None,
    client_has_insurance: Optional[bool] = None,
    client_insurer: Optional[str] = None,
    client_policy: Optional[str] = None,
    client_insurer_contact: Optional[str] = None,
    household_has_insurance: Optional[bool] = None,
    household_insurer: Optional[str] = None,
    household_policy: Optional[str] = None,
    household_insurer_contact: Optional[str] = None,
    household_member_name: Optional[str] = None,
) -> PIPDetermination:
    """
    Run the Kentucky PIP waterfall logic.
    
    Args:
        client_on_title: Is client's name on the TITLE of the vehicle they occupied?
        vehicle_insured: Was the vehicle the client occupied insured?
        vehicle_insurer: Name of vehicle's insurance company
        vehicle_policy: Vehicle's policy number
        vehicle_insurer_contact: Contact info for vehicle's insurer
        client_has_insurance: Does the client have their own auto insurance?
        client_insurer: Name of client's insurance company
        client_policy: Client's policy number
        client_insurer_contact: Contact info for client's insurer
        household_has_insurance: Does a household member have auto insurance?
        household_insurer: Name of household member's insurance company
        household_policy: Household member's policy number
        household_insurer_contact: Contact info for household insurer
        household_member_name: Name of household member with insurance
        
    Returns:
        PIPDetermination with the result
    """
    waterfall_path = []
    
    # Step 1: Is client on title of vehicle they were in?
    waterfall_path.append("Step 1: Check if client is named on vehicle title")
    
    if client_on_title is True:
        waterfall_path.append("→ Client IS on title of vehicle occupied")
        
        # Critical check: Is that vehicle insured?
        if vehicle_insured is False:
            # DISQUALIFIED - owned uninsured vehicle
            waterfall_path.append("→ Vehicle is UNINSURED")
            waterfall_path.append("⚠️ CLIENT DISQUALIFIED FROM PIP BENEFITS")
            
            return PIPDetermination(
                pip_insurer=None,
                pip_insurer_type="disqualified",
                policy_number=None,
                contact_info=None,
                is_kac=False,
                is_disqualified=True,
                disqualification_reason="Client was occupying a vehicle titled in their name that was uninsured. Under Kentucky law, the owner of an uninsured motor vehicle is not entitled to PIP benefits.",
                waterfall_step=1,
                waterfall_path=waterfall_path,
                recommendation="Client is NOT eligible for PIP benefits. Focus on BI claim against at-fault party.",
                next_steps=[
                    "Document the disqualification in case file",
                    "Advise client they must pay medical bills out-of-pocket or through health insurance",
                    "Focus recovery efforts on BI claim against at-fault party",
                    "Consider health insurance subrogation implications"
                ],
                template_to_use="N/A - No PIP claim available",
                timestamp=datetime.now().isoformat()
            )
        
        elif vehicle_insured is True:
            # Covered by vehicle's insurer
            waterfall_path.append("→ Vehicle IS insured")
            waterfall_path.append(f"✓ PIP insurer determined: {vehicle_insurer}")
            
            return PIPDetermination(
                pip_insurer=vehicle_insurer,
                pip_insurer_type="vehicle",
                policy_number=vehicle_policy,
                contact_info=vehicle_insurer_contact,
                is_kac=False,
                is_disqualified=False,
                disqualification_reason=None,
                waterfall_step=1,
                waterfall_path=waterfall_path,
                recommendation=f"Open PIP claim with {vehicle_insurer} (vehicle's insurer). Client is named insured on vehicle title.",
                next_steps=[
                    f"Open PIP claim with {vehicle_insurer}",
                    "Send LOR to PIP adjuster",
                    "Request PIP benefits pay medical bills directly",
                    "Reserve portion of PIP for future bills if needed"
                ],
                template_to_use="/forms/insurance/PIP/lor_to_pip_adjuster_TEMPLATE.md",
                timestamp=datetime.now().isoformat()
            )
    
    # Step 2: Was the vehicle occupied insured?
    waterfall_path.append("Step 2: Check if vehicle occupied was insured")
    
    if vehicle_insured is True:
        waterfall_path.append("→ Vehicle occupied WAS insured")
        waterfall_path.append(f"✓ PIP insurer determined: {vehicle_insurer}")
        
        return PIPDetermination(
            pip_insurer=vehicle_insurer,
            pip_insurer_type="vehicle",
            policy_number=vehicle_policy,
            contact_info=vehicle_insurer_contact,
            is_kac=False,
            is_disqualified=False,
            disqualification_reason=None,
            waterfall_step=2,
            waterfall_path=waterfall_path,
            recommendation=f"Open PIP claim with {vehicle_insurer} (vehicle's insurer). Client was occupant of insured vehicle.",
            next_steps=[
                f"Open PIP claim with {vehicle_insurer}",
                "Send LOR to PIP adjuster",
                "Request declaration page to confirm PIP limits",
                "Coordinate PIP payments with medical providers"
            ],
            template_to_use="/forms/insurance/PIP/lor_to_pip_adjuster_TEMPLATE.md",
            timestamp=datetime.now().isoformat()
        )
    
    waterfall_path.append("→ Vehicle occupied was NOT insured or unknown")
    
    # Step 3: Does client have their own auto insurance?
    waterfall_path.append("Step 3: Check if client has own auto insurance")
    
    if client_has_insurance is True:
        waterfall_path.append("→ Client HAS own auto insurance")
        waterfall_path.append(f"✓ PIP insurer determined: {client_insurer}")
        
        return PIPDetermination(
            pip_insurer=client_insurer,
            pip_insurer_type="client",
            policy_number=client_policy,
            contact_info=client_insurer_contact,
            is_kac=False,
            is_disqualified=False,
            disqualification_reason=None,
            waterfall_step=3,
            waterfall_path=waterfall_path,
            recommendation=f"Open PIP claim with {client_insurer} (client's own insurer). Vehicle occupied was uninsured but client has own coverage.",
            next_steps=[
                f"Open PIP claim with {client_insurer}",
                "Send LOR to PIP adjuster",
                "Explain client was in uninsured vehicle but has own policy",
                "Request declaration page to confirm PIP limits"
            ],
            template_to_use="/forms/insurance/PIP/lor_to_pip_adjuster_TEMPLATE.md",
            timestamp=datetime.now().isoformat()
        )
    
    waterfall_path.append("→ Client does NOT have own auto insurance")
    
    # Step 4: Does a household member have auto insurance?
    waterfall_path.append("Step 4: Check if household member has auto insurance")
    
    if household_has_insurance is True:
        waterfall_path.append(f"→ Household member ({household_member_name or 'unnamed'}) HAS auto insurance")
        waterfall_path.append(f"✓ PIP insurer determined: {household_insurer}")
        
        member_note = f" ({household_member_name})" if household_member_name else ""
        
        return PIPDetermination(
            pip_insurer=household_insurer,
            pip_insurer_type="household",
            policy_number=household_policy,
            contact_info=household_insurer_contact,
            is_kac=False,
            is_disqualified=False,
            disqualification_reason=None,
            waterfall_step=4,
            waterfall_path=waterfall_path,
            recommendation=f"Open PIP claim with {household_insurer} (household member's insurer{member_note}). Client qualifies as resident relative.",
            next_steps=[
                f"Open PIP claim with {household_insurer}",
                "Send LOR to PIP adjuster",
                f"Explain client is household member of policyholder{member_note}",
                "May need to provide proof of residence in same household"
            ],
            template_to_use="/forms/insurance/PIP/lor_to_pip_adjuster_TEMPLATE.md",
            timestamp=datetime.now().isoformat()
        )
    
    waterfall_path.append("→ NO household member has auto insurance")
    
    # Step 5: Kentucky Assigned Claims Plan (KAC)
    waterfall_path.append("Step 5: No coverage found - Kentucky Assigned Claims Plan (KAC)")
    waterfall_path.append("✓ Client must apply for KAC")
    
    return PIPDetermination(
        pip_insurer="Kentucky Assigned Claims Plan (KAC)",
        pip_insurer_type="kac",
        policy_number=None,
        contact_info="Kentucky Assigned Claims Plan\nP.O. Box 517\nFrankfort, KY 40602\nPhone: (502) 875-4460",
        is_kac=True,
        is_disqualified=False,
        disqualification_reason=None,
        waterfall_step=5,
        waterfall_path=waterfall_path,
        recommendation="Client has no available PIP coverage through normal channels. Must apply for Kentucky Assigned Claims Plan (KAC).",
        next_steps=[
            "Complete KAC Application form",
            "Submit to Kentucky Assigned Claims Plan",
            "KAC will assign an insurer to handle the claim",
            "Follow up within 30 days for assignment",
            "Note: KAC claims may have different processing times"
        ],
        template_to_use="/forms/insurance/PIP/KAC_Application.pdf",
        timestamp=datetime.now().isoformat()
    )


def interactive_waterfall() -> dict:
    """Run interactive questionnaire and return answers."""
    print("\n" + "="*60)
    print("KENTUCKY PIP WATERFALL DETERMINATION")
    print("="*60)
    print("\nThis tool will determine the correct PIP insurer for your case.")
    print("Answer the following questions:\n")
    
    answers = {}
    
    # Step 1: Client on title?
    print("-" * 40)
    print("STEP 1: Vehicle Title")
    print("-" * 40)
    response = input("Is the CLIENT'S NAME on the TITLE of the vehicle they were in? (yes/no): ").strip().lower()
    answers["client_on_title"] = response in ["yes", "y", "true", "1"]
    
    if answers["client_on_title"]:
        response = input("Was that vehicle INSURED? (yes/no): ").strip().lower()
        answers["vehicle_insured"] = response in ["yes", "y", "true", "1"]
        
        if answers["vehicle_insured"]:
            answers["vehicle_insurer"] = input("Insurance company name: ").strip()
            answers["vehicle_policy"] = input("Policy number (or press Enter to skip): ").strip() or None
            answers["vehicle_insurer_contact"] = input("Adjuster contact info (or press Enter to skip): ").strip() or None
            return answers
        else:
            # Disqualified - return immediately
            return answers
    
    # Step 2: Vehicle insured?
    print("\n" + "-" * 40)
    print("STEP 2: Vehicle Insurance")
    print("-" * 40)
    response = input("Was the VEHICLE the client was in INSURED? (yes/no/unknown): ").strip().lower()
    answers["vehicle_insured"] = response in ["yes", "y", "true", "1"]
    
    if answers["vehicle_insured"]:
        answers["vehicle_insurer"] = input("Insurance company name: ").strip()
        answers["vehicle_policy"] = input("Policy number (or press Enter to skip): ").strip() or None
        answers["vehicle_insurer_contact"] = input("Adjuster contact info (or press Enter to skip): ").strip() or None
        return answers
    
    # Step 3: Client has insurance?
    print("\n" + "-" * 40)
    print("STEP 3: Client's Own Insurance")
    print("-" * 40)
    response = input("Does the CLIENT have their OWN auto insurance? (yes/no): ").strip().lower()
    answers["client_has_insurance"] = response in ["yes", "y", "true", "1"]
    
    if answers["client_has_insurance"]:
        answers["client_insurer"] = input("Client's insurance company name: ").strip()
        answers["client_policy"] = input("Policy number (or press Enter to skip): ").strip() or None
        answers["client_insurer_contact"] = input("Contact info (or press Enter to skip): ").strip() or None
        return answers
    
    # Step 4: Household member has insurance?
    print("\n" + "-" * 40)
    print("STEP 4: Household Member Insurance")
    print("-" * 40)
    response = input("Does any HOUSEHOLD MEMBER have auto insurance? (yes/no): ").strip().lower()
    answers["household_has_insurance"] = response in ["yes", "y", "true", "1"]
    
    if answers["household_has_insurance"]:
        answers["household_member_name"] = input("Household member's name: ").strip() or None
        answers["household_insurer"] = input("Their insurance company name: ").strip()
        answers["household_policy"] = input("Policy number (or press Enter to skip): ").strip() or None
        answers["household_insurer_contact"] = input("Contact info (or press Enter to skip): ").strip() or None
        return answers
    
    # No coverage - KAC
    return answers


def main():
    parser = argparse.ArgumentParser(
        description="Kentucky PIP Waterfall Determination Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Mode selection
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive mode (asks questions)")
    parser.add_argument("--from-json", type=str,
                        help="Load answers from JSON file")
    
    # Direct answers
    parser.add_argument("--client-on-title", choices=["yes", "no"],
                        help="Is client on vehicle title?")
    parser.add_argument("--vehicle-insured", choices=["yes", "no"],
                        help="Was vehicle insured?")
    parser.add_argument("--vehicle-insurer", type=str,
                        help="Vehicle's insurance company")
    parser.add_argument("--vehicle-policy", type=str,
                        help="Vehicle's policy number")
    parser.add_argument("--client-has-insurance", choices=["yes", "no"],
                        help="Does client have own auto insurance?")
    parser.add_argument("--client-insurer", type=str,
                        help="Client's insurance company")
    parser.add_argument("--client-policy", type=str,
                        help="Client's policy number")
    parser.add_argument("--household-has-insurance", choices=["yes", "no"],
                        help="Does household member have insurance?")
    parser.add_argument("--household-insurer", type=str,
                        help="Household member's insurance company")
    parser.add_argument("--household-policy", type=str,
                        help="Household member's policy number")
    parser.add_argument("--household-member", type=str,
                        help="Name of household member with insurance")
    
    # Output options
    parser.add_argument("--pretty", "-p", action="store_true",
                        help="Pretty print output")
    parser.add_argument("--output", "-o", type=str,
                        help="Save result to file")
    
    args = parser.parse_args()
    
    # Collect answers
    if args.interactive:
        answers = interactive_waterfall()
    elif args.from_json:
        with open(args.from_json) as f:
            answers = json.load(f)
    else:
        # Build from command line args
        answers = {
            "client_on_title": args.client_on_title == "yes" if args.client_on_title else None,
            "vehicle_insured": args.vehicle_insured == "yes" if args.vehicle_insured else None,
            "vehicle_insurer": args.vehicle_insurer,
            "vehicle_policy": args.vehicle_policy,
            "client_has_insurance": args.client_has_insurance == "yes" if args.client_has_insurance else None,
            "client_insurer": args.client_insurer,
            "client_policy": args.client_policy,
            "household_has_insurance": args.household_has_insurance == "yes" if args.household_has_insurance else None,
            "household_insurer": args.household_insurer,
            "household_policy": args.household_policy,
            "household_member_name": args.household_member,
        }
    
    # Run waterfall
    result = run_waterfall(**answers)
    
    # Convert to dict for output
    output = asdict(result)
    
    # Print result
    if args.interactive or args.pretty:
        print("\n" + "="*60)
        print("PIP DETERMINATION RESULT")
        print("="*60)
        
        if result.is_disqualified:
            print("\n⚠️  CLIENT DISQUALIFIED FROM PIP BENEFITS")
            print(f"\nReason: {result.disqualification_reason}")
        elif result.is_kac:
            print("\n📋 KENTUCKY ASSIGNED CLAIMS PLAN (KAC) REQUIRED")
            print(f"\nContact:\n{result.contact_info}")
        else:
            print(f"\n✅ PIP INSURER: {result.pip_insurer}")
            print(f"   Type: {result.pip_insurer_type}")
            if result.policy_number:
                print(f"   Policy: {result.policy_number}")
        
        print(f"\n📝 Recommendation: {result.recommendation}")
        
        print("\n📋 Next Steps:")
        for i, step in enumerate(result.next_steps, 1):
            print(f"   {i}. {step}")
        
        print(f"\n📄 Template: {result.template_to_use}")
        
        print("\n🔍 Waterfall Path:")
        for step in result.waterfall_path:
            print(f"   {step}")
        
        print("\n" + "-"*60)
        print("JSON Output:")
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps(output, indent=2 if args.pretty else None))
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\nResult saved to: {args.output}", file=sys.stderr)
    
    # Exit code based on result
    if result.is_disqualified:
        sys.exit(2)  # Disqualified
    elif result.is_kac:
        sys.exit(1)  # KAC required (special handling)
    else:
        sys.exit(0)  # Normal PIP claim


if __name__ == "__main__":
    main()

