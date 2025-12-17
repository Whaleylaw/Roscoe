#!/usr/bin/env python3
"""
Settlement Statement Calculator and Generator

Calculates settlement distributions and generates DocuSign-ready settlement statements
for personal injury cases. Handles:
- Attorney fees (percentage-based)
- Medical bills with reductions
- Case expenses
- Liens with reductions
- Net to client calculation

Usage:
    # Interactive mode
    python settlement_calculator.py --interactive
    
    # From JSON file with case data
    python settlement_calculator.py --from-json /path/to/settlement_data.json
    
    # Direct input
    python settlement_calculator.py --settlement 50000 --fee-percent 33.33 \
        --bills '[{"provider": "Dr. Smith", "amount": 5000, "reduction": 1000}]' \
        --liens '[{"holder": "Medicare", "amount": 3000, "reduction": 500}]'

Output:
    - JSON with all calculations
    - Markdown settlement statement (DocuSign-ready)
    - Summary for client communication
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from pathlib import Path


def money(value) -> Decimal:
    """Convert to Decimal and round to 2 places."""
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@dataclass
class MedicalBill:
    provider: str
    amount: Decimal
    reduction: Decimal = Decimal('0')
    pip_payment: Decimal = Decimal('0')
    health_ins_payment: Decimal = Decimal('0')
    writeoff: Decimal = Decimal('0')
    client_payment: Decimal = Decimal('0')
    
    @property
    def net_amount(self) -> Decimal:
        return self.amount - self.reduction
    
    def to_dict(self):
        return {
            "provider": self.provider,
            "amount": float(self.amount),
            "reduction": float(self.reduction),
            "net_amount": float(self.net_amount),
            "pip_payment": float(self.pip_payment),
            "health_ins_payment": float(self.health_ins_payment),
            "writeoff": float(self.writeoff),
            "client_payment": float(self.client_payment)
        }


@dataclass
class Expense:
    description: str
    amount: Decimal
    
    def to_dict(self):
        return {
            "description": self.description,
            "amount": float(self.amount)
        }


@dataclass
class Lien:
    holder: str
    amount: Decimal
    reduction: Decimal = Decimal('0')
    
    @property
    def net_amount(self) -> Decimal:
        return self.amount - self.reduction
    
    def to_dict(self):
        return {
            "holder": self.holder,
            "amount": float(self.amount),
            "reduction": float(self.reduction),
            "net_amount": float(self.net_amount)
        }


@dataclass
class SettlementCalculation:
    """Complete settlement calculation results."""
    # Input values
    client_name: str
    settlement_amount: Decimal
    attorney_fee_percent: Decimal
    
    # Calculated values
    attorney_fee: Decimal = Decimal('0')
    total_medical_bills: Decimal = Decimal('0')
    total_medical_reductions: Decimal = Decimal('0')
    net_medical_bills: Decimal = Decimal('0')
    total_expenses: Decimal = Decimal('0')
    total_liens: Decimal = Decimal('0')
    total_lien_reductions: Decimal = Decimal('0')
    net_liens: Decimal = Decimal('0')
    total_to_client: Decimal = Decimal('0')
    
    # Detail items
    medical_bills: list = field(default_factory=list)
    expenses: list = field(default_factory=list)
    liens: list = field(default_factory=list)
    
    # Metadata
    case_name: str = ""
    date_prepared: str = ""
    prepared_by: str = "Aaron G. Whaley, Esq."
    
    def to_dict(self):
        return {
            "client_name": self.client_name,
            "case_name": self.case_name,
            "date_prepared": self.date_prepared,
            "prepared_by": self.prepared_by,
            "settlement_amount": float(self.settlement_amount),
            "attorney_fee_percent": float(self.attorney_fee_percent),
            "attorney_fee": float(self.attorney_fee),
            "total_medical_bills": float(self.total_medical_bills),
            "total_medical_reductions": float(self.total_medical_reductions),
            "net_medical_bills": float(self.net_medical_bills),
            "total_expenses": float(self.total_expenses),
            "total_liens": float(self.total_liens),
            "total_lien_reductions": float(self.total_lien_reductions),
            "net_liens": float(self.net_liens),
            "total_to_client": float(self.total_to_client),
            "medical_bills": [b.to_dict() for b in self.medical_bills],
            "expenses": [e.to_dict() for e in self.expenses],
            "liens": [l.to_dict() for l in self.liens]
        }


def calculate_settlement(
    client_name: str,
    settlement_amount: float,
    attorney_fee_percent: float,
    medical_bills: list[dict],
    expenses: list[dict],
    liens: list[dict],
    case_name: str = "",
    prepared_by: str = "Aaron G. Whaley, Esq."
) -> SettlementCalculation:
    """
    Calculate complete settlement distribution.
    
    Args:
        client_name: Client's full name
        settlement_amount: Total settlement amount
        attorney_fee_percent: Attorney fee percentage (e.g., 33.33)
        medical_bills: List of {"provider": str, "amount": float, "reduction": float, ...}
        expenses: List of {"description": str, "amount": float}
        liens: List of {"holder": str, "amount": float, "reduction": float}
        case_name: Optional case name
        prepared_by: Attorney name
        
    Returns:
        SettlementCalculation with all computed values
    """
    calc = SettlementCalculation(
        client_name=client_name,
        settlement_amount=money(settlement_amount),
        attorney_fee_percent=money(attorney_fee_percent),
        case_name=case_name,
        date_prepared=datetime.now().strftime("%B %d, %Y"),
        prepared_by=prepared_by
    )
    
    # Calculate attorney fee
    calc.attorney_fee = money(calc.settlement_amount * calc.attorney_fee_percent / 100)
    
    # Process medical bills
    for bill_data in medical_bills:
        bill = MedicalBill(
            provider=bill_data.get("provider", "Unknown Provider"),
            amount=money(bill_data.get("amount", 0)),
            reduction=money(bill_data.get("reduction", 0)),
            pip_payment=money(bill_data.get("pip_payment", 0)),
            health_ins_payment=money(bill_data.get("health_ins_payment", 0)),
            writeoff=money(bill_data.get("writeoff", 0)),
            client_payment=money(bill_data.get("client_payment", 0))
        )
        calc.medical_bills.append(bill)
        calc.total_medical_bills += bill.amount
        calc.total_medical_reductions += bill.reduction
    
    calc.net_medical_bills = calc.total_medical_bills - calc.total_medical_reductions
    
    # Process expenses
    for exp_data in expenses:
        exp = Expense(
            description=exp_data.get("description", "Expense"),
            amount=money(exp_data.get("amount", 0))
        )
        calc.expenses.append(exp)
        calc.total_expenses += exp.amount
    
    # Process liens
    for lien_data in liens:
        lien = Lien(
            holder=lien_data.get("holder", "Unknown Lien Holder"),
            amount=money(lien_data.get("amount", 0)),
            reduction=money(lien_data.get("reduction", 0))
        )
        calc.liens.append(lien)
        calc.total_liens += lien.amount
        calc.total_lien_reductions += lien.reduction
    
    calc.net_liens = calc.total_liens - calc.total_lien_reductions
    
    # Calculate total to client
    calc.total_to_client = (
        calc.settlement_amount 
        - calc.attorney_fee 
        - calc.net_medical_bills 
        - calc.total_expenses 
        - calc.net_liens
    )
    
    return calc


def format_currency(amount) -> str:
    """Format as currency string."""
    return f"${float(amount):,.2f}"


def generate_markdown_statement(calc: SettlementCalculation) -> str:
    """Generate DocuSign-ready markdown settlement statement."""
    
    # Build medical bills table
    bills_rows = ""
    for bill in calc.medical_bills:
        bills_rows += f"| {bill.provider} | {format_currency(bill.amount)} | {format_currency(bill.reduction)} | {format_currency(bill.net_amount)} |\n"
    
    if not bills_rows:
        bills_rows = "| *No medical bills* | - | - | - |\n"
    
    # Build expenses table
    expenses_rows = ""
    for exp in calc.expenses:
        expenses_rows += f"| {exp.description} | {format_currency(exp.amount)} |\n"
    
    if not expenses_rows:
        expenses_rows = "| *No expenses* | $0.00 |\n"
    
    # Build liens table
    liens_rows = ""
    for lien in calc.liens:
        liens_rows += f"| {lien.holder} | {format_currency(lien.amount)} | {format_currency(lien.reduction)} | {format_currency(lien.net_amount)} |\n"
    
    if not liens_rows:
        liens_rows = "| *No liens* | - | - | - |\n"
    
    template = f"""---
title: Settlement Statement
document_type: settlement_statement
client_name: {calc.client_name}
case_name: {calc.case_name}
date_prepared: {calc.date_prepared}
prepared_by: {calc.prepared_by}
requires_signature: true
signature_type: single_signer
anchors:
  - /sig1/ (client signature)
  - /date1/ (date signed)
---

<div align="center">

# SETTLEMENT STATEMENT

**Aaron G. Whaley, Esq.**  
712 Lyndon Lane  
Louisville, KY 40222  
Ph: (502) 583-4022

</div>

---

**Client:** {calc.client_name}  
**Case:** {calc.case_name}  
**Date Prepared:** {calc.date_prepared}

---

## Settlement Summary

| Description | Amount |
|-------------|--------|
| **Final Settlement** | {format_currency(calc.settlement_amount)} |
| Less: Attorney Fee ({calc.attorney_fee_percent}%) | ({format_currency(calc.attorney_fee)}) |
| Less: Medical Bills (Net) | ({format_currency(calc.net_medical_bills)}) |
| Less: Expenses | ({format_currency(calc.total_expenses)}) |
| Less: Liens (Net) | ({format_currency(calc.net_liens)}) |
| **TOTAL TO CLIENT** | **{format_currency(calc.total_to_client)}** |

---

## Medical Bills Detail

**Total Gross:** {format_currency(calc.total_medical_bills)}  
**Total Reductions:** {format_currency(calc.total_medical_reductions)}  
**Net Medical Bills:** {format_currency(calc.net_medical_bills)}

| Provider | Amount | Reduction | Net Amount |
|----------|--------|-----------|------------|
{bills_rows}

---

## Expenses Detail

**Total Expenses:** {format_currency(calc.total_expenses)}

| Description | Amount |
|-------------|--------|
{expenses_rows}

---

## Liens Detail

**Total Gross:** {format_currency(calc.total_liens)}  
**Total Reductions:** {format_currency(calc.total_lien_reductions)}  
**Net Liens:** {format_currency(calc.net_liens)}

| Lien Holder | Amount | Reduction | Net Amount |
|-------------|--------|-----------|------------|
{liens_rows}

---

## Client Acknowledgment

I, **{calc.client_name}**, having been fully advised of my rights, have now read the entire Settlement Statement and concur with those calculations as stated herein and above, and accept the Net to Client as full and final settlement of this matter. I also understand that the above calculations representing reduction requests are subject to approval by the respective subject providers.

I agree to hold the Law Firm harmless from any and all medical, dental, hospitals, nurses or other liens or claims which may currently exist or which may come into existence. I confirm that I have not received services concerning this cause of action with any other service providers.

I understand that unpaid medical bills, or any other obligation arising out of this claim not itemized under Medical Bill Detail are my responsibility - not my attorney's responsibility - and I assume full responsibility for payment of the same.

I have been advised that settlements on account of physical sickness or injury are not taxable income except that portion received for "lost earnings" if any. I understand my attorneys have not given any tax advice and I will consult with my accountant or other tax advisor if I have any questions regarding this issue.

I give my attorney authority to sign any document including checks necessary to complete this settlement. Any signed documents will be available for my inspection upon request.

---

**UNDERSTOOD, AGREED AND RECEIVED**

Client Signature: /sig1/

Date: /date1/

**{calc.client_name}**

---

Attorney: {calc.prepared_by}
"""
    
    return template


def generate_client_summary(calc: SettlementCalculation) -> str:
    """Generate a simple summary for client communication."""
    return f"""Settlement Summary for {calc.client_name}
{'='*50}

Settlement Amount:     {format_currency(calc.settlement_amount)}
Less Attorney Fee:    -{format_currency(calc.attorney_fee)}
Less Medical Bills:   -{format_currency(calc.net_medical_bills)}
Less Expenses:        -{format_currency(calc.total_expenses)}
Less Liens:           -{format_currency(calc.net_liens)}
{'='*50}
YOUR NET AMOUNT:       {format_currency(calc.total_to_client)}

This statement will be sent to you for electronic signature via DocuSign.
"""


def interactive_input() -> dict:
    """Gather settlement data interactively."""
    print("\n" + "="*60)
    print("SETTLEMENT STATEMENT CALCULATOR")
    print("="*60)
    
    data = {}
    
    # Basic info
    data["client_name"] = input("\nClient Name: ").strip()
    data["case_name"] = input("Case Name (or press Enter to skip): ").strip() or data["client_name"]
    data["settlement_amount"] = float(input("Settlement Amount: $").replace(",", ""))
    data["attorney_fee_percent"] = float(input("Attorney Fee Percentage (e.g., 33.33): "))
    
    # Medical bills
    print("\n--- MEDICAL BILLS ---")
    print("Enter medical bills (press Enter with empty provider to finish)")
    data["medical_bills"] = []
    while True:
        provider = input("\nProvider Name (or Enter to finish): ").strip()
        if not provider:
            break
        amount = float(input("  Amount: $").replace(",", ""))
        reduction = float(input("  Reduction (or 0): $").replace(",", "") or "0")
        data["medical_bills"].append({
            "provider": provider,
            "amount": amount,
            "reduction": reduction
        })
    
    # Expenses
    print("\n--- EXPENSES ---")
    print("Enter expenses (press Enter with empty description to finish)")
    data["expenses"] = []
    while True:
        desc = input("\nExpense Description (or Enter to finish): ").strip()
        if not desc:
            break
        amount = float(input("  Amount: $").replace(",", ""))
        data["expenses"].append({
            "description": desc,
            "amount": amount
        })
    
    # Liens
    print("\n--- LIENS ---")
    print("Enter liens (press Enter with empty holder to finish)")
    data["liens"] = []
    while True:
        holder = input("\nLien Holder (or Enter to finish): ").strip()
        if not holder:
            break
        amount = float(input("  Amount: $").replace(",", ""))
        reduction = float(input("  Reduction (or 0): $").replace(",", "") or "0")
        data["liens"].append({
            "holder": holder,
            "amount": amount,
            "reduction": reduction
        })
    
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Settlement Statement Calculator and Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Input modes
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive mode")
    parser.add_argument("--from-json", type=str,
                        help="Load settlement data from JSON file")
    
    # Direct input
    parser.add_argument("--client-name", type=str, help="Client name")
    parser.add_argument("--case-name", type=str, help="Case name")
    parser.add_argument("--settlement", type=float, help="Settlement amount")
    parser.add_argument("--fee-percent", type=float, default=33.33,
                        help="Attorney fee percentage (default: 33.33)")
    parser.add_argument("--bills", type=str, 
                        help='Medical bills JSON array')
    parser.add_argument("--expenses", type=str,
                        help='Expenses JSON array')
    parser.add_argument("--liens", type=str,
                        help='Liens JSON array')
    
    # Output options
    parser.add_argument("--pretty", "-p", action="store_true",
                        help="Pretty print output")
    parser.add_argument("--output-json", type=str,
                        help="Save calculation JSON to file")
    parser.add_argument("--output-md", type=str,
                        help="Save markdown statement to file")
    parser.add_argument("--format", choices=["json", "markdown", "summary", "all"],
                        default="all", help="Output format")
    
    args = parser.parse_args()
    
    # Gather data
    if args.interactive:
        data = interactive_input()
    elif args.from_json:
        with open(args.from_json) as f:
            data = json.load(f)
    else:
        if not args.client_name or not args.settlement:
            parser.error("--client-name and --settlement are required unless using --interactive or --from-json")
        
        data = {
            "client_name": args.client_name,
            "case_name": args.case_name or args.client_name,
            "settlement_amount": args.settlement,
            "attorney_fee_percent": args.fee_percent,
            "medical_bills": json.loads(args.bills) if args.bills else [],
            "expenses": json.loads(args.expenses) if args.expenses else [],
            "liens": json.loads(args.liens) if args.liens else []
        }
    
    # Calculate
    calc = calculate_settlement(
        client_name=data["client_name"],
        settlement_amount=data["settlement_amount"],
        attorney_fee_percent=data.get("attorney_fee_percent", 33.33),
        medical_bills=data.get("medical_bills", []),
        expenses=data.get("expenses", []),
        liens=data.get("liens", []),
        case_name=data.get("case_name", "")
    )
    
    # Generate outputs
    calc_dict = calc.to_dict()
    markdown = generate_markdown_statement(calc)
    summary = generate_client_summary(calc)
    
    # Print based on format
    if args.format == "json":
        print(json.dumps(calc_dict, indent=2 if args.pretty else None))
    elif args.format == "markdown":
        print(markdown)
    elif args.format == "summary":
        print(summary)
    else:  # all
        if args.interactive or args.pretty:
            print("\n" + "="*60)
            print("CALCULATION RESULTS")
            print("="*60)
            print(summary)
            print("\n" + "-"*60)
            print("JSON Output:")
            print(json.dumps(calc_dict, indent=2))
        else:
            # Machine output
            output = {
                "calculation": calc_dict,
                "markdown": markdown,
                "summary": summary
            }
            print(json.dumps(output, indent=2 if args.pretty else None))
    
    # Save files if requested
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(calc_dict, f, indent=2)
        print(f"\nJSON saved to: {args.output_json}", file=sys.stderr)
    
    if args.output_md:
        with open(args.output_md, 'w') as f:
            f.write(markdown)
        print(f"Markdown saved to: {args.output_md}", file=sys.stderr)
    
    # Exit with success
    sys.exit(0)


if __name__ == "__main__":
    main()

