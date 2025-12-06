"use client";

import React, { useState } from "react";
import ContactCard from "./ContactCard";

interface ContactInfo {
  name?: string | null;
  roles?: string[];
  company?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
}

interface Provider {
  name: string;
  total_billed?: number | null;
}

interface Lien {
  lienholder_name: string;
  original_amount?: number | null;
}

interface Expense {
  description: string;
  amount?: number | null;
}

interface Claim {
  claim_number?: string | null;
  coverage_type?: string | null;
  date_demand_sent?: string | null;
  demand_amount?: number | null;
  current_offer?: number | null;
  settlement_amount?: number | null;
  notes?: string | null;
}

interface Negotiation {
  project_name: string;
  client_name: string;
  coverage_type?: string;
  insurance_company?: ContactInfo | null;
  adjuster?: ContactInfo | null;
  claim?: Claim;
  providers?: Provider[];
  liens?: Lien[];
  expenses?: Expense[];
  totals?: {
    medical_bills?: number;
    liens?: number;
    expenses?: number;
  };
}

interface NegotiationsViewData {
  title: string;
  count: number;
  negotiations: Negotiation[];
}

function formatCurrency(amount: number | null | undefined): string {
  if (amount == null) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function NegotiationCard({ negotiation }: { negotiation: Negotiation }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const totalDamages = (negotiation.totals?.medical_bills || 0) + 
    (negotiation.totals?.liens || 0) + 
    (negotiation.totals?.expenses || 0);

  return (
    <div className="border border-zinc-700 rounded-xl overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between bg-zinc-800/50 hover:bg-zinc-800 transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-500 to-orange-600 flex items-center justify-center text-white font-bold">
            {negotiation.client_name.charAt(0)}
          </div>
          <div className="text-left">
            <div className="font-semibold text-zinc-200">{negotiation.client_name}</div>
            <div className="text-sm text-zinc-500">{negotiation.project_name}</div>
            <div className="flex items-center gap-2 mt-1">
              <span className="px-2 py-0.5 text-xs rounded bg-yellow-500/20 text-yellow-400">
                {negotiation.coverage_type || "Negotiating"}
              </span>
              {negotiation.claim?.current_offer && (
                <span className="px-2 py-0.5 text-xs rounded bg-blue-500/20 text-blue-400">
                  Offer: {formatCurrency(negotiation.claim.current_offer)}
                </span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          {/* Key Figures */}
          <div className="text-right hidden md:block">
            {negotiation.claim?.demand_amount && (
              <div>
                <div className="text-lg font-bold text-emerald-400">
                  {formatCurrency(negotiation.claim.demand_amount)}
                </div>
                <div className="text-xs text-zinc-500">Demand</div>
              </div>
            )}
          </div>
          
          <div className="text-right hidden md:block">
            <div className="text-lg font-bold text-purple-400">
              {formatCurrency(totalDamages)}
            </div>
            <div className="text-xs text-zinc-500">Total Damages</div>
          </div>
          
          <svg
            className={`w-5 h-5 text-zinc-400 transition-transform ${isExpanded ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="p-4 bg-zinc-900/50 border-t border-zinc-700 space-y-6">
          {/* Contacts Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {negotiation.insurance_company && negotiation.insurance_company.name && (
              <div>
                <div className="text-sm font-medium text-zinc-400 mb-2">Insurance Company</div>
                <ContactCard data={{
                  name: negotiation.insurance_company.name,
                  roles: negotiation.insurance_company.roles,
                  company: negotiation.insurance_company.company,
                  email: negotiation.insurance_company.email,
                  phone: negotiation.insurance_company.phone,
                }} />
              </div>
            )}
            
            {negotiation.adjuster && negotiation.adjuster.name && (
              <div>
                <div className="text-sm font-medium text-zinc-400 mb-2">Adjuster</div>
                <ContactCard data={{
                  name: negotiation.adjuster.name,
                  roles: ["Insurance Adjuster"],
                  company: negotiation.insurance_company?.name || undefined,
                  email: negotiation.adjuster.email,
                  phone: negotiation.adjuster.phone,
                }} />
              </div>
            )}
          </div>

          {/* Claim Details */}
          {negotiation.claim && (
            <div className="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700">
              <div className="text-sm font-medium text-zinc-400 mb-3">Claim Details</div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {negotiation.claim.claim_number && (
                  <div>
                    <div className="text-xs text-zinc-500">Claim #</div>
                    <div className="text-sm text-zinc-200">{negotiation.claim.claim_number}</div>
                  </div>
                )}
                {negotiation.claim.date_demand_sent && (
                  <div>
                    <div className="text-xs text-zinc-500">Demand Sent</div>
                    <div className="text-sm text-zinc-200">{negotiation.claim.date_demand_sent}</div>
                  </div>
                )}
                {negotiation.claim.demand_amount && (
                  <div>
                    <div className="text-xs text-zinc-500">Demand Amount</div>
                    <div className="text-sm text-emerald-400">{formatCurrency(negotiation.claim.demand_amount)}</div>
                  </div>
                )}
                {negotiation.claim.current_offer && (
                  <div>
                    <div className="text-xs text-zinc-500">Current Offer</div>
                    <div className="text-sm text-blue-400">{formatCurrency(negotiation.claim.current_offer)}</div>
                  </div>
                )}
              </div>
              
              {negotiation.claim.notes && (
                <div className="mt-3 pt-3 border-t border-zinc-700">
                  <div className="text-xs text-zinc-500 mb-1">Notes</div>
                  <p className="text-sm text-zinc-400">{negotiation.claim.notes}</p>
                </div>
              )}
            </div>
          )}

          {/* Financial Summary */}
          <div className="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700">
            <div className="text-sm font-medium text-zinc-400 mb-3">Financial Summary</div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="text-2xl font-bold text-emerald-400">
                  {formatCurrency(negotiation.totals?.medical_bills)}
                </div>
                <div className="text-xs text-zinc-500">Medical Bills</div>
                {negotiation.providers && (
                  <div className="text-xs text-zinc-600 mt-1">
                    {negotiation.providers.length} provider{negotiation.providers.length !== 1 ? "s" : ""}
                  </div>
                )}
              </div>
              
              <div>
                <div className="text-2xl font-bold text-orange-400">
                  {formatCurrency(negotiation.totals?.liens)}
                </div>
                <div className="text-xs text-zinc-500">Liens</div>
                {negotiation.liens && (
                  <div className="text-xs text-zinc-600 mt-1">
                    {negotiation.liens.length} lien{negotiation.liens.length !== 1 ? "s" : ""}
                  </div>
                )}
              </div>
              
              <div>
                <div className="text-2xl font-bold text-purple-400">
                  {formatCurrency(negotiation.totals?.expenses)}
                </div>
                <div className="text-xs text-zinc-500">Expenses</div>
                {negotiation.expenses && (
                  <div className="text-xs text-zinc-600 mt-1">
                    {negotiation.expenses.length} item{negotiation.expenses.length !== 1 ? "s" : ""}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function NegotiationsView({ data }: { data: NegotiationsViewData }) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-zinc-700 pb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">🤝</span>
          <div>
            <h2 className="text-2xl font-bold text-zinc-100">{data.title}</h2>
            <p className="text-zinc-400 mt-1">
              {data.count} active negotiation{data.count !== 1 ? "s" : ""}
            </p>
          </div>
        </div>
      </div>

      {/* Negotiation Cards */}
      <div className="space-y-4">
        {data.negotiations.map((negotiation, i) => (
          <NegotiationCard key={i} negotiation={negotiation} />
        ))}
      </div>

      {data.negotiations.length === 0 && (
        <div className="text-center py-8 text-zinc-500">
          No active negotiations found
        </div>
      )}
    </div>
  );
}

