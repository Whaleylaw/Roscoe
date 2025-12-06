"use client";

import React from "react";
import CaseSnapshot from "./CaseSnapshot";
import InsuranceCoverageCard from "./InsuranceCoverageCard";
import LienCard from "./LienCard";
import ExpenseCard from "./ExpenseCard";
import ContactCard from "./ContactCard";

// Section types that the agent can compose
type SectionType = "snapshot" | "insurance" | "providers" | "liens" | "expenses" | "contact" | "custom";

interface Section {
  type: SectionType;
  title?: string;
  data?: unknown;
  content?: string; // For custom sections
}

interface ComposedViewData {
  title: string;
  subtitle?: string;
  sections: Section[];
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

// Simple provider card for composed views (without documents)
function SimpleProviderCard({ provider }: { provider: {
  name: string;
  total_billed?: number | null;
  total_paid?: number | null;
  dates_of_service?: string[];
  notes?: string | null;
}}) {
  return (
    <div className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg border border-zinc-700">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center text-white font-bold">
          {provider.name.charAt(0)}
        </div>
        <div>
          <div className="font-semibold text-zinc-200">{provider.name}</div>
          {provider.dates_of_service && provider.dates_of_service.length > 0 && (
            <div className="text-xs text-zinc-500">
              {provider.dates_of_service.join(" - ")}
            </div>
          )}
        </div>
      </div>
      <div className="text-right">
        <div className="text-lg font-bold text-emerald-400">
          {formatCurrency(provider.total_billed)}
        </div>
        <div className="text-xs text-zinc-500">Billed</div>
      </div>
    </div>
  );
}

// Render a single section based on its type
function RenderSection({ section }: { section: Section }) {
  const { type, title, data, content } = section;

  const wrapper = (children: React.ReactNode) => (
    <div className="space-y-3">
      {title && (
        <h3 className="text-lg font-semibold text-zinc-200 border-b border-zinc-700 pb-2">
          {title}
        </h3>
      )}
      {children}
    </div>
  );

  switch (type) {
    case "snapshot":
      return wrapper(
        <CaseSnapshot data={data as Parameters<typeof CaseSnapshot>[0]["data"]} />
      );

    case "insurance":
      // Handle both array and object format
      const insuranceData = Array.isArray(data) 
        ? { coverage_types: data }
        : data;
      return wrapper(
        <InsuranceCoverageCard data={insuranceData as Parameters<typeof InsuranceCoverageCard>[0]["data"]} />
      );

    case "providers":
      const providers = data as Array<{
        name: string;
        total_billed?: number | null;
        total_paid?: number | null;
        dates_of_service?: string[];
        notes?: string | null;
      }>;
      return wrapper(
        <div className="space-y-2">
          {providers.map((provider, i) => (
            <SimpleProviderCard key={i} provider={provider} />
          ))}
        </div>
      );

    case "liens":
      // Handle both array and object format
      const lienData = Array.isArray(data)
        ? { liens: data }
        : data;
      return wrapper(
        <LienCard data={lienData as Parameters<typeof LienCard>[0]["data"]} />
      );

    case "expenses":
      // Handle both array and object format
      const expenseData = Array.isArray(data)
        ? { expenses: data }
        : data;
      return wrapper(
        <ExpenseCard data={expenseData as Parameters<typeof ExpenseCard>[0]["data"]} />
      );

    case "contact":
      return wrapper(
        <ContactCard data={data as Parameters<typeof ContactCard>[0]["data"]} />
      );

    case "custom":
      return wrapper(
        <div className="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700">
          <div className="text-sm text-zinc-300 whitespace-pre-wrap">
            {content || (typeof data === "string" ? data : JSON.stringify(data, null, 2))}
          </div>
        </div>
      );

    default:
      console.warn(`Unknown section type: ${type}`);
      return null;
  }
}

export default function ComposedView({ data }: { data: ComposedViewData }) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-zinc-700 pb-4">
        <h2 className="text-2xl font-bold text-zinc-100">{data.title}</h2>
        {data.subtitle && (
          <p className="text-zinc-400 mt-1">{data.subtitle}</p>
        )}
      </div>

      {/* Sections */}
      <div className="space-y-6">
        {data.sections.map((section, i) => (
          <RenderSection key={i} section={section} />
        ))}
      </div>

      {data.sections.length === 0 && (
        <div className="text-center py-8 text-zinc-500">
          No sections to display
        </div>
      )}
    </div>
  );
}

