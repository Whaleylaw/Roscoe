"use client";

import React, { useState } from "react";

interface Lien {
  lienholder_name: string;
  lien_type?: string | null;
  original_amount?: number | null;
  negotiated_amount?: number | null;
  reduction_amount?: number | null;
  paid_amount?: number | null;
  status?: string | null;
  date_received?: string | null;
  date_resolved?: string | null;
  contact_name?: string | null;
  contact_phone?: string | null;
  contact_email?: string | null;
  notes?: string | null;
}

interface LienCardData {
  client_name?: string;
  case_name?: string;
  liens: Lien[];
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

function getStatusColor(status: string | null | undefined): string {
  if (!status) return "bg-zinc-500";
  const lower = status.toLowerCase();
  if (lower.includes("paid") || lower.includes("resolved")) return "bg-emerald-500";
  if (lower.includes("pending") || lower.includes("negotiating")) return "bg-yellow-500";
  if (lower.includes("disputed")) return "bg-red-500";
  return "bg-zinc-500";
}

function getLienTypeIcon(type: string | null | undefined): string {
  if (!type) return "📋";
  const lower = type.toLowerCase();
  if (lower.includes("medicaid") || lower.includes("medicare")) return "🏛️";
  if (lower.includes("health") || lower.includes("insurance")) return "🏥";
  if (lower.includes("hospital")) return "🏨";
  if (lower.includes("attorney")) return "⚖️";
  if (lower.includes("child") || lower.includes("support")) return "👶";
  return "📋";
}

function LienRow({ lien }: { lien: Lien }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const reduction = (lien.original_amount || 0) - (lien.negotiated_amount || lien.original_amount || 0);
  const reductionPercent = lien.original_amount && reduction > 0 
    ? Math.round((reduction / lien.original_amount) * 100) 
    : 0;

  return (
    <div className="border border-zinc-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between bg-zinc-800/50 hover:bg-zinc-800 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getLienTypeIcon(lien.lien_type)}</span>
          <div className="text-left">
            <div className="font-semibold text-zinc-200">{lien.lienholder_name}</div>
            {lien.lien_type && (
              <div className="text-sm text-zinc-500">{lien.lien_type}</div>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {lien.status && (
            <span className={`px-2 py-0.5 text-xs rounded text-white ${getStatusColor(lien.status)}`}>
              {lien.status}
            </span>
          )}
          
          <div className="text-right">
            {lien.negotiated_amount && lien.negotiated_amount !== lien.original_amount ? (
              <>
                <div className="text-lg font-bold text-emerald-400">
                  {formatCurrency(lien.negotiated_amount)}
                </div>
                <div className="text-xs text-zinc-500 line-through">
                  {formatCurrency(lien.original_amount)}
                </div>
              </>
            ) : (
              <div className="text-lg font-bold text-orange-400">
                {formatCurrency(lien.original_amount)}
              </div>
            )}
          </div>
          
          {reductionPercent > 0 && (
            <span className="px-2 py-0.5 text-xs rounded bg-emerald-500/20 text-emerald-400">
              -{reductionPercent}%
            </span>
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
        <div className="p-4 bg-zinc-900/50 border-t border-zinc-700 space-y-4">
          {/* Details Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-xs text-zinc-500">Original Amount</div>
              <div className="text-sm text-zinc-200">{formatCurrency(lien.original_amount)}</div>
            </div>
            {lien.negotiated_amount && lien.negotiated_amount !== lien.original_amount && (
              <div>
                <div className="text-xs text-zinc-500">Negotiated</div>
                <div className="text-sm text-emerald-400">{formatCurrency(lien.negotiated_amount)}</div>
              </div>
            )}
            {lien.reduction_amount && lien.reduction_amount > 0 && (
              <div>
                <div className="text-xs text-zinc-500">Reduction</div>
                <div className="text-sm text-emerald-400">{formatCurrency(lien.reduction_amount)}</div>
              </div>
            )}
            {lien.paid_amount && (
              <div>
                <div className="text-xs text-zinc-500">Paid</div>
                <div className="text-sm text-blue-400">{formatCurrency(lien.paid_amount)}</div>
              </div>
            )}
          </div>

          {/* Dates */}
          <div className="grid grid-cols-2 gap-4">
            {lien.date_received && (
              <div>
                <div className="text-xs text-zinc-500">Date Received</div>
                <div className="text-sm text-zinc-200">{lien.date_received}</div>
              </div>
            )}
            {lien.date_resolved && (
              <div>
                <div className="text-xs text-zinc-500">Date Resolved</div>
                <div className="text-sm text-zinc-200">{lien.date_resolved}</div>
              </div>
            )}
          </div>

          {/* Contact Info */}
          {(lien.contact_name || lien.contact_phone || lien.contact_email) && (
            <div className="pt-3 border-t border-zinc-700">
              <div className="text-sm font-medium text-zinc-400 mb-2">Contact</div>
              <div className="space-y-1">
                {lien.contact_name && (
                  <div className="text-sm text-zinc-200">👤 {lien.contact_name}</div>
                )}
                {lien.contact_phone && (
                  <a href={`tel:${lien.contact_phone}`} className="block text-sm text-blue-400 hover:underline">
                    📞 {lien.contact_phone}
                  </a>
                )}
                {lien.contact_email && (
                  <a href={`mailto:${lien.contact_email}`} className="block text-sm text-blue-400 hover:underline">
                    📧 {lien.contact_email}
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Notes */}
          {lien.notes && (
            <div className="pt-3 border-t border-zinc-700">
              <div className="text-xs text-zinc-500 mb-1">Notes</div>
              <p className="text-sm text-zinc-400 italic">{lien.notes}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function LienCard({ data }: { data: LienCardData }) {
  // Calculate totals
  const totalOriginal = data.liens.reduce((sum, l) => sum + (l.original_amount || 0), 0);
  const totalNegotiated = data.liens.reduce((sum, l) => sum + (l.negotiated_amount || l.original_amount || 0), 0);
  const totalReduction = totalOriginal - totalNegotiated;
  const totalPaid = data.liens.reduce((sum, l) => sum + (l.paid_amount || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-zinc-700 pb-4">
        <h2 className="text-2xl font-bold text-zinc-100">Liens</h2>
        {data.client_name && (
          <p className="text-zinc-400 mt-1">
            Client: <span className="text-zinc-200">{data.client_name}</span>
            {data.case_name && <> · Case: <span className="text-zinc-200">{data.case_name}</span></>}
          </p>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="text-2xl font-bold text-orange-400">{formatCurrency(totalOriginal)}</div>
          <div className="text-sm text-zinc-500 mt-1">Original Total</div>
        </div>
        
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="text-2xl font-bold text-emerald-400">{formatCurrency(totalNegotiated)}</div>
          <div className="text-sm text-zinc-500 mt-1">Negotiated Total</div>
        </div>
        
        {totalReduction > 0 && (
          <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
            <div className="text-2xl font-bold text-green-400">{formatCurrency(totalReduction)}</div>
            <div className="text-sm text-zinc-500 mt-1">Total Savings</div>
          </div>
        )}
        
        {totalPaid > 0 && (
          <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
            <div className="text-2xl font-bold text-blue-400">{formatCurrency(totalPaid)}</div>
            <div className="text-sm text-zinc-500 mt-1">Total Paid</div>
          </div>
        )}
        
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="text-2xl font-bold text-purple-400">{data.liens.length}</div>
          <div className="text-sm text-zinc-500 mt-1">Lien{data.liens.length !== 1 ? "s" : ""}</div>
        </div>
      </div>

      {/* Lien List */}
      <div className="space-y-3">
        {data.liens.map((lien, i) => (
          <LienRow key={i} lien={lien} />
        ))}
      </div>

      {data.liens.length === 0 && (
        <div className="text-center py-8 text-zinc-500">
          No liens found
        </div>
      )}
    </div>
  );
}

