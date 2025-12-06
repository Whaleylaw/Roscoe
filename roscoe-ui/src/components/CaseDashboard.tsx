"use client";

import React, { useState } from "react";
import CaseSnapshot from "./CaseSnapshot";
import InsuranceCoverageCard from "./InsuranceCoverageCard";
import LienCard from "./LienCard";
import ExpenseCard from "./ExpenseCard";

interface Provider {
  name: string;
  specialty?: string | null;
  total_billed: number;
  total_paid?: number | null;
  dates_of_service?: string[];
  notes?: string | null;
}

interface CoverageType {
  type: string;
  claims: Array<{
    company_name: string;
    claim_number?: string | null;
    adjuster?: {
      name?: string | null;
      email?: string | null;
      phone?: string | null;
    } | null;
    policy_limits?: string | null;
    demanded_amount?: number | null;
    current_offer?: number | null;
    settlement_amount?: number | null;
    is_active_negotiation?: boolean;
  }>;
}

interface Lien {
  lienholder_name: string;
  lien_type?: string | null;
  original_amount?: number | null;
  negotiated_amount?: number | null;
  status?: string | null;
}

interface Expense {
  description: string;
  category?: string | null;
  amount: number;
  status?: string | null;
}

interface CaseDashboardData {
  // Snapshot fields
  client_name: string;
  case_name: string;
  accident_date?: string | null;
  case_summary?: string | null;
  current_status?: string | null;
  last_status_update?: string | null;
  phase?: string | null;
  total_medical_bills?: number | null;
  total_liens?: number | null;
  total_expenses?: number | null;
  client_address?: string | null;
  client_phone?: string | null;
  client_email?: string | null;
  
  // Accordion sections
  insurance?: CoverageType[];
  providers?: Provider[];
  liens?: Lien[];
  expenses?: Expense[];
}

function formatCurrency(amount: number | null | undefined): string {
  if (amount == null) return "$0";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function ProviderRow({ provider }: { provider: Provider }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-zinc-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between bg-zinc-800/50 hover:bg-zinc-800 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center text-white font-bold">
            {provider.name.charAt(0)}
          </div>
          <div className="text-left">
            <div className="font-semibold text-zinc-200">{provider.name}</div>
            {provider.specialty && (
              <div className="text-sm text-zinc-500">{provider.specialty}</div>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-lg font-bold text-emerald-400">
              {formatCurrency(provider.total_billed)}
            </div>
            <div className="text-xs text-zinc-500">Billed</div>
          </div>
          {provider.total_paid != null && provider.total_paid > 0 && (
            <div className="text-right">
              <div className="text-lg font-bold text-blue-400">
                {formatCurrency(provider.total_paid)}
              </div>
              <div className="text-xs text-zinc-500">Paid</div>
            </div>
          )}
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
      
      {isExpanded && (
        <div className="p-4 bg-zinc-900/50 border-t border-zinc-700 space-y-3">
          {provider.dates_of_service && provider.dates_of_service.length > 0 && (
            <div>
              <div className="text-sm font-medium text-zinc-400 mb-2">Dates of Service</div>
              <div className="flex flex-wrap gap-2">
                {provider.dates_of_service.map((date, i) => (
                  <span key={i} className="px-2 py-1 bg-zinc-800 rounded text-xs text-zinc-300">
                    {date}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {provider.notes && (
            <div>
              <div className="text-sm font-medium text-zinc-400 mb-1">Notes</div>
              <p className="text-sm text-zinc-500 italic">{provider.notes}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

type SectionType = "insurance" | "providers" | "liens" | "expenses";

function AccordionSection({ 
  title, 
  icon, 
  count, 
  isOpen, 
  onToggle, 
  children 
}: { 
  title: string; 
  icon: string; 
  count: number; 
  isOpen: boolean; 
  onToggle: () => void; 
  children: React.ReactNode;
}) {
  return (
    <div className="border border-zinc-700 rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between bg-zinc-800/50 hover:bg-zinc-800 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <div className="text-left">
            <div className="font-semibold text-zinc-200">{title}</div>
            <div className="text-sm text-zinc-500">{count} item{count !== 1 ? "s" : ""}</div>
          </div>
        </div>
        <svg
          className={`w-5 h-5 text-zinc-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {isOpen && (
        <div className="p-4 bg-zinc-900/30 space-y-3">
          {children}
        </div>
      )}
    </div>
  );
}

export default function CaseDashboard({ data }: { data: CaseDashboardData }) {
  const [openSections, setOpenSections] = useState<Set<SectionType>>(new Set());

  const toggleSection = (section: SectionType) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  // Prepare snapshot data
  const snapshotData = {
    client_name: data.client_name,
    case_name: data.case_name,
    accident_date: data.accident_date,
    case_summary: data.case_summary,
    current_status: data.current_status,
    last_status_update: data.last_status_update,
    phase: data.phase,
    total_medical_bills: data.total_medical_bills,
    total_liens: data.total_liens,
    total_expenses: data.total_expenses,
    client_address: data.client_address,
    client_phone: data.client_phone,
    client_email: data.client_email,
  };

  return (
    <div className="space-y-6">
      {/* Case Snapshot (always visible) */}
      <CaseSnapshot data={snapshotData} />

      {/* Accordion Sections */}
      <div className="space-y-4">
        {/* Insurance */}
        {data.insurance && data.insurance.length > 0 && (
          <AccordionSection
            title="Insurance Coverage"
            icon="🛡️"
            count={data.insurance.length}
            isOpen={openSections.has("insurance")}
            onToggle={() => toggleSection("insurance")}
          >
            <InsuranceCoverageCard data={{ coverage_types: data.insurance }} />
          </AccordionSection>
        )}

        {/* Medical Providers */}
        {data.providers && data.providers.length > 0 && (
          <AccordionSection
            title="Medical Providers"
            icon="🏥"
            count={data.providers.length}
            isOpen={openSections.has("providers")}
            onToggle={() => toggleSection("providers")}
          >
            <div className="space-y-2">
              {data.providers.map((provider, i) => (
                <ProviderRow key={i} provider={provider} />
              ))}
            </div>
          </AccordionSection>
        )}

        {/* Liens */}
        {data.liens && data.liens.length > 0 && (
          <AccordionSection
            title="Liens"
            icon="📋"
            count={data.liens.length}
            isOpen={openSections.has("liens")}
            onToggle={() => toggleSection("liens")}
          >
            <LienCard data={{ liens: data.liens }} />
          </AccordionSection>
        )}

        {/* Expenses */}
        {data.expenses && data.expenses.length > 0 && (
          <AccordionSection
            title="Expenses"
            icon="💰"
            count={data.expenses.length}
            isOpen={openSections.has("expenses")}
            onToggle={() => toggleSection("expenses")}
          >
            <ExpenseCard data={{ expenses: data.expenses }} />
          </AccordionSection>
        )}
      </div>
    </div>
  );
}

