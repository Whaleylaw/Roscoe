"use client";

import React, { useState } from "react";

interface FileEntry {
  filename: string;
  view_url?: string | null;
  download_url?: string | null;
  file_type?: string;
}

interface AdjusterInfo {
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
}

interface Claim {
  company_name: string;
  claim_number?: string | null;
  adjuster?: AdjusterInfo | null;
  coverage_confirmation?: string | null;
  policy_limits?: string | null;
  demanded_amount?: number | null;
  current_offer?: number | null;
  settlement_amount?: number | null;
  settlement_date?: string | null;
  is_active_negotiation?: boolean;
  notes?: string | null;
  documents?: FileEntry[];
}

interface CoverageType {
  type: string;
  claims: Claim[];
  documents?: FileEntry[];
}

interface InsuranceCoverageData {
  client_name?: string;
  case_name?: string;
  coverage_types?: CoverageType[];
  // Single coverage type format
  type?: string;
  claims?: Claim[];
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

function getCoverageTypeIcon(type: string): string {
  const lower = type.toLowerCase();
  if (lower.includes("pip") || lower.includes("personal injury")) return "🏥";
  if (lower.includes("bi") || lower.includes("bodily injury")) return "🚗";
  if (lower.includes("uim") || lower.includes("underinsured")) return "⚠️";
  if (lower.includes("um") || lower.includes("uninsured")) return "🚫";
  if (lower.includes("medpay") || lower.includes("medical pay")) return "💊";
  if (lower.includes("pd") || lower.includes("property")) return "🏠";
  return "📋";
}

function FileList({ files }: { files: FileEntry[] }) {
  if (!files || files.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-zinc-700">
      <div className="text-sm font-medium text-zinc-400 mb-2">📁 Documents ({files.length})</div>
      <div className="space-y-1">
        {files.map((file, i) => (
          <div key={i} className="flex items-center justify-between group hover:bg-zinc-700/30 rounded px-2 py-1">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <span className="text-red-400">📄</span>
              {file.view_url ? (
                <a
                  href={file.view_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-400 hover:text-blue-300 hover:underline truncate"
                >
                  {file.filename}
                </a>
              ) : (
                <span className="text-sm text-zinc-400 truncate">{file.filename}</span>
              )}
            </div>
            {file.download_url && (
              <a
                href={file.download_url}
                className="p-1 rounded hover:bg-zinc-600 text-zinc-400 hover:text-zinc-200 opacity-0 group-hover:opacity-100"
                title="Download"
              >
                ⬇️
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function ClaimCard({ claim }: { claim: Claim }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-zinc-900/50 rounded-lg border border-zinc-700 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 text-left hover:bg-zinc-800/50 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm">
              {claim.company_name.charAt(0)}
            </div>
            <div>
              <div className="font-semibold text-zinc-200">{claim.company_name}</div>
              {claim.claim_number && (
                <div className="text-xs text-zinc-500">Claim #{claim.claim_number}</div>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {claim.is_active_negotiation && (
              <span className="px-2 py-0.5 text-xs rounded bg-yellow-500/20 text-yellow-400">
                Active Negotiation
              </span>
            )}
            {claim.settlement_amount ? (
              <div className="text-right">
                <div className="text-lg font-bold text-emerald-400">{formatCurrency(claim.settlement_amount)}</div>
                <div className="text-xs text-zinc-500">Settled</div>
              </div>
            ) : claim.current_offer ? (
              <div className="text-right">
                <div className="text-lg font-bold text-blue-400">{formatCurrency(claim.current_offer)}</div>
                <div className="text-xs text-zinc-500">Current Offer</div>
              </div>
            ) : null}
            <svg
              className={`w-5 h-5 text-zinc-400 transition-transform ${isExpanded ? "rotate-180" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </button>

      {isExpanded && (
        <div className="p-4 bg-zinc-900 border-t border-zinc-700 space-y-4">
          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-4">
            {claim.policy_limits && (
              <div>
                <div className="text-xs text-zinc-500">Policy Limits</div>
                <div className="text-sm text-zinc-200">{claim.policy_limits}</div>
              </div>
            )}
            {claim.demanded_amount && (
              <div>
                <div className="text-xs text-zinc-500">Demand Amount</div>
                <div className="text-sm text-zinc-200">{formatCurrency(claim.demanded_amount)}</div>
              </div>
            )}
            {claim.current_offer && (
              <div>
                <div className="text-xs text-zinc-500">Current Offer</div>
                <div className="text-sm text-zinc-200">{formatCurrency(claim.current_offer)}</div>
              </div>
            )}
            {claim.coverage_confirmation && (
              <div>
                <div className="text-xs text-zinc-500">Coverage Status</div>
                <div className="text-sm text-zinc-200">{claim.coverage_confirmation}</div>
              </div>
            )}
            {claim.settlement_date && (
              <div>
                <div className="text-xs text-zinc-500">Settlement Date</div>
                <div className="text-sm text-zinc-200">{claim.settlement_date}</div>
              </div>
            )}
          </div>

          {/* Adjuster Info */}
          {claim.adjuster && claim.adjuster.name && (
            <div className="pt-3 border-t border-zinc-700">
              <div className="text-sm font-medium text-zinc-400 mb-2">Adjuster</div>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center text-white text-sm font-bold">
                  {claim.adjuster.name.charAt(0)}
                </div>
                <div>
                  <div className="text-sm text-zinc-200">{claim.adjuster.name}</div>
                  {claim.adjuster.phone && (
                    <a href={`tel:${claim.adjuster.phone}`} className="text-xs text-blue-400 hover:underline">
                      {claim.adjuster.phone}
                    </a>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Notes */}
          {claim.notes && (
            <div className="pt-3 border-t border-zinc-700">
              <div className="text-xs text-zinc-500 mb-1">Notes</div>
              <p className="text-sm text-zinc-400 italic">{claim.notes}</p>
            </div>
          )}

          {/* Documents */}
          {claim.documents && claim.documents.length > 0 && (
            <FileList files={claim.documents} />
          )}
        </div>
      )}
    </div>
  );
}

function CoverageSection({ coverage }: { coverage: CoverageType }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const totalClaims = coverage.claims.length;
  const hasSettlement = coverage.claims.some(c => c.settlement_amount);

  return (
    <div className="border border-zinc-700 rounded-xl overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between bg-zinc-800/50 hover:bg-zinc-800 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getCoverageTypeIcon(coverage.type)}</span>
          <div className="text-left">
            <div className="font-semibold text-zinc-200">{coverage.type}</div>
            <div className="text-sm text-zinc-500">
              {totalClaims} claim{totalClaims !== 1 ? "s" : ""}
              {hasSettlement && " · Has settlements"}
            </div>
          </div>
        </div>
        <svg
          className={`w-5 h-5 text-zinc-400 transition-transform ${isExpanded ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="p-4 space-y-3 bg-zinc-900/30">
          {coverage.claims.map((claim, i) => (
            <ClaimCard key={i} claim={claim} />
          ))}
          
          {coverage.documents && coverage.documents.length > 0 && (
            <div className="pt-3 border-t border-zinc-700">
              <div className="text-sm font-medium text-zinc-400 mb-2">
                📁 Coverage Documents ({coverage.documents.length})
              </div>
              <FileList files={coverage.documents} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function InsuranceCoverageCard({ data }: { data: InsuranceCoverageData }) {
  // Handle both single coverage and multiple coverage types format
  const coverageTypes: CoverageType[] = data.coverage_types || 
    (data.type && data.claims ? [{ type: data.type, claims: data.claims }] : []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-zinc-700 pb-4">
        <h2 className="text-2xl font-bold text-zinc-100">Insurance Coverage</h2>
        {data.client_name && (
          <p className="text-zinc-400 mt-1">
            Client: <span className="text-zinc-200">{data.client_name}</span>
            {data.case_name && <> · Case: <span className="text-zinc-200">{data.case_name}</span></>}
          </p>
        )}
      </div>

      {/* Coverage Sections */}
      <div className="space-y-4">
        {coverageTypes.map((coverage, i) => (
          <CoverageSection key={i} coverage={coverage} />
        ))}
      </div>

      {coverageTypes.length === 0 && (
        <div className="text-center py-8 text-zinc-500">
          No insurance coverage found
        </div>
      )}
    </div>
  );
}

