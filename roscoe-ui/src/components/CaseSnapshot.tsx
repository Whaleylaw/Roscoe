"use client";

import React from "react";

interface CaseSnapshotData {
  client_name: string;
  case_name: string;
  accident_date?: string | null;
  case_summary?: string | null;
  current_status?: string | null;
  last_status_update?: string | null;
  phase?: string | null;
  case_create_date?: string | null;
  case_last_activity?: string | null;
  total_medical_bills?: number | null;
  total_liens?: number | null;
  total_expenses?: number | null;
  client_address?: string | null;
  client_phone?: string | null;
  client_email?: string | null;
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

function getStatusColor(status: string | null | undefined): string {
  if (!status) return "bg-zinc-500";
  const lower = status.toLowerCase();
  if (lower.includes("active") || lower.includes("progress")) return "bg-emerald-500";
  if (lower.includes("pending") || lower.includes("waiting")) return "bg-yellow-500";
  if (lower.includes("closed") || lower.includes("settled")) return "bg-blue-500";
  if (lower.includes("urgent") || lower.includes("critical")) return "bg-red-500";
  return "bg-zinc-500";
}

function getPhaseIcon(phase: string | null | undefined): string {
  if (!phase) return "📋";
  const lower = phase.toLowerCase();
  if (lower.includes("intake") || lower.includes("initial")) return "📝";
  if (lower.includes("treatment") || lower.includes("medical")) return "🏥";
  if (lower.includes("discovery")) return "🔍";
  if (lower.includes("negotiation")) return "🤝";
  if (lower.includes("litigation")) return "⚖️";
  if (lower.includes("settlement")) return "✅";
  return "📋";
}

export default function CaseSnapshot({ data }: { data: CaseSnapshotData }) {
  const totalFinancials = 
    (data.total_medical_bills || 0) + 
    (data.total_liens || 0) + 
    (data.total_expenses || 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-zinc-100">{data.client_name}</h2>
          <p className="text-zinc-400 text-sm">{data.case_name}</p>
          {data.accident_date && (
            <p className="text-zinc-500 text-sm mt-1">
              <span className="text-zinc-600">Accident Date:</span> {data.accident_date}
            </p>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {data.phase && (
            <span className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-zinc-800 text-zinc-300 text-sm">
              {getPhaseIcon(data.phase)} {data.phase}
            </span>
          )}
          {data.current_status && (
            <span className={`px-3 py-1.5 rounded-full text-white text-sm ${getStatusColor(data.current_status)}`}>
              {data.current_status}
            </span>
          )}
        </div>
      </div>

      {/* Case Summary */}
      {data.case_summary && (
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <h3 className="text-sm font-medium text-zinc-400 mb-2">Case Summary</h3>
          <p className="text-zinc-200">{data.case_summary}</p>
        </div>
      )}

      {/* Financial Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="text-3xl font-bold text-emerald-400">
            {formatCurrency(data.total_medical_bills)}
          </div>
          <div className="text-sm text-zinc-500 mt-1">Medical Bills</div>
        </div>
        
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="text-3xl font-bold text-orange-400">
            {formatCurrency(data.total_liens)}
          </div>
          <div className="text-sm text-zinc-500 mt-1">Liens</div>
        </div>
        
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="text-3xl font-bold text-purple-400">
            {formatCurrency(data.total_expenses)}
          </div>
          <div className="text-sm text-zinc-500 mt-1">Expenses</div>
        </div>
        
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700 bg-gradient-to-br from-zinc-800/50 to-zinc-900/50">
          <div className="text-3xl font-bold text-zinc-100">
            {formatCurrency(totalFinancials)}
          </div>
          <div className="text-sm text-zinc-500 mt-1">Total</div>
        </div>
      </div>

      {/* Timeline & Contact Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Timeline */}
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <h3 className="text-sm font-medium text-zinc-400 mb-3">Timeline</h3>
          <div className="space-y-3">
            {data.case_create_date && (
              <div className="flex items-center gap-3">
                <span className="text-emerald-400">📅</span>
                <div>
                  <div className="text-sm text-zinc-200">Case Created</div>
                  <div className="text-xs text-zinc-500">{data.case_create_date}</div>
                </div>
              </div>
            )}
            {data.case_last_activity && (
              <div className="flex items-center gap-3">
                <span className="text-blue-400">🔄</span>
                <div>
                  <div className="text-sm text-zinc-200">Last Activity</div>
                  <div className="text-xs text-zinc-500">{data.case_last_activity}</div>
                </div>
              </div>
            )}
            {data.last_status_update && (
              <div className="flex items-center gap-3">
                <span className="text-yellow-400">📝</span>
                <div>
                  <div className="text-sm text-zinc-200">Status Updated</div>
                  <div className="text-xs text-zinc-500">{data.last_status_update}</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Client Contact */}
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <h3 className="text-sm font-medium text-zinc-400 mb-3">Client Contact</h3>
          <div className="space-y-3">
            {data.client_phone && (
              <div className="flex items-center gap-3">
                <span className="text-emerald-400">📞</span>
                <a href={`tel:${data.client_phone}`} className="text-sm text-blue-400 hover:underline">
                  {data.client_phone}
                </a>
              </div>
            )}
            {data.client_email && (
              <div className="flex items-center gap-3">
                <span className="text-blue-400">📧</span>
                <a href={`mailto:${data.client_email}`} className="text-sm text-blue-400 hover:underline truncate">
                  {data.client_email}
                </a>
              </div>
            )}
            {data.client_address && (
              <div className="flex items-center gap-3">
                <span className="text-orange-400">📍</span>
                <span className="text-sm text-zinc-300">{data.client_address}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

