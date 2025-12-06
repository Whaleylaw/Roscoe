"use client";

import React, { useState } from "react";

// File with view and download URLs
interface FileEntry {
  filename: string;
  view_url?: string | null;
  download_url?: string | null;
  file_type?: string;
}

// Categories of files for a provider
interface FileCategories {
  "Medical Records"?: FileEntry[];
  "Medical Bills"?: FileEntry[];
  "Correspondence"?: FileEntry[];
}

interface Provider {
  name: string;
  specialty?: string | null;
  total_billed: number;
  total_paid?: number | null;
  dates_of_service?: string[];
  categories?: FileCategories;
  notes?: string | null;
}

interface MedicalTreatmentData {
  client_name: string;
  case_name: string;
  accident_date?: string | null;
  total_billed: number;
  total_settlement?: number | null;
  total_paid?: number | null;
  providers: Provider[];
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function MiniBarChart({ values, color = "emerald" }: { values: number[]; color?: string }) {
  const max = Math.max(...values, 1);
  return (
    <div className="flex items-end gap-1 h-8">
      {values.map((v, i) => (
        <div
          key={i}
          className={`w-2 bg-${color}-500 rounded-t opacity-80`}
          style={{ height: `${(v / max) * 100}%`, minHeight: "2px" }}
        />
      ))}
    </div>
  );
}

// File icon based on type
function FileIcon({ type }: { type?: string }) {
  switch (type?.toLowerCase()) {
    case "pdf":
      return <span className="text-red-400">📄</span>;
    case "md":
      return <span className="text-blue-400">📝</span>;
    case "eml":
      return <span className="text-yellow-400">✉️</span>;
    default:
      return <span className="text-zinc-400">📁</span>;
  }
}

// File list component with clickable links
function FileList({ files, categoryName }: { files: FileEntry[]; categoryName: string }) {
  if (!files || files.length === 0) return null;

  return (
    <div className="mt-3">
      <div className="text-sm font-medium text-zinc-400 mb-2 flex items-center gap-2">
        {categoryName === "Medical Records" && <span>📋</span>}
        {categoryName === "Medical Bills" && <span>💵</span>}
        {categoryName === "Correspondence" && <span>📬</span>}
        {categoryName}
        <span className="text-xs text-zinc-500">({files.length})</span>
      </div>
      <div className="space-y-1 pl-2">
        {files.map((file, i) => (
          <div key={i} className="flex items-center justify-between group hover:bg-zinc-700/30 rounded px-2 py-1 -mx-2">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <FileIcon type={file.file_type} />
              {file.view_url ? (
                <a
                  href={file.view_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-400 hover:text-blue-300 hover:underline truncate"
                  title={file.filename}
                >
                  {file.filename}
                </a>
              ) : (
                <span className="text-sm text-zinc-400 truncate" title={file.filename}>
                  {file.filename}
                </span>
              )}
            </div>
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              {file.view_url && (
                <a
                  href={file.view_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1 rounded hover:bg-zinc-600 text-zinc-400 hover:text-zinc-200"
                  title="View in browser"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </a>
              )}
              {file.download_url && (
                <a
                  href={file.download_url}
                  className="p-1 rounded hover:bg-zinc-600 text-zinc-400 hover:text-zinc-200"
                  title="Download"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ProviderCard({ provider, isExpanded, onToggle }: { 
  provider: Provider; 
  isExpanded: boolean; 
  onToggle: () => void;
}) {
  // Count total files
  const totalFiles = Object.values(provider.categories || {}).reduce(
    (sum, files) => sum + (files?.length || 0), 
    0
  );

  return (
    <div className="border border-zinc-700 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
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
            {totalFiles > 0 && (
              <div className="text-xs text-zinc-500">{totalFiles} files</div>
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
        <div className="p-4 bg-zinc-900/50 border-t border-zinc-700 space-y-4">
          {/* Dates of Service */}
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
          
          {/* Notes */}
          {provider.notes && (
            <div>
              <div className="text-sm font-medium text-zinc-400 mb-1">Notes</div>
              <p className="text-sm text-zinc-500 italic">{provider.notes}</p>
            </div>
          )}
          
          {/* File Categories */}
          {provider.categories && (
            <div className="border-t border-zinc-700 pt-3 mt-3">
              <FileList 
                files={provider.categories["Medical Records"] || []} 
                categoryName="Medical Records" 
              />
              <FileList 
                files={provider.categories["Medical Bills"] || []} 
                categoryName="Medical Bills" 
              />
              <FileList 
                files={provider.categories["Correspondence"] || []} 
                categoryName="Correspondence" 
              />
            </div>
          )}
          
          {/* No files message */}
          {(!provider.categories || totalFiles === 0) && (
            <div className="text-sm text-zinc-500 italic">
              No files found for this provider
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function MedicalTreatmentOverview({ data }: { data: MedicalTreatmentData }) {
  const [expandedProviders, setExpandedProviders] = useState<Set<number>>(new Set());

  const toggleProvider = (index: number) => {
    setExpandedProviders((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  // Calculate chart data from providers
  const chartData = data.providers.slice(0, 6).map((p) => p.total_billed / 1000);

  // Count total files across all providers
  const totalFiles = data.providers.reduce((sum, p) => {
    const providerFiles = Object.values(p.categories || {}).reduce(
      (pSum, files) => pSum + (files?.length || 0), 
      0
    );
    return sum + providerFiles;
  }, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-zinc-700 pb-4">
        <h2 className="text-2xl font-bold text-zinc-100">Medical Treatment Overview</h2>
        <p className="text-zinc-400 mt-1">
          Client: <span className="text-zinc-200">{data.client_name}</span>
          {data.case_name && (
            <> · Case: <span className="text-zinc-200">{data.case_name}</span></>
          )}
        </p>
        {data.accident_date && (
          <p className="text-zinc-500 text-sm mt-1">Accident Date: {data.accident_date}</p>
        )}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total Billed */}
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold text-emerald-400">
                {formatCurrency(data.total_billed)}
              </div>
              <div className="text-sm text-zinc-500 mt-1">Total Billed</div>
            </div>
            <div className="text-4xl opacity-50">💵</div>
          </div>
          <div className="mt-3">
            <MiniBarChart values={chartData} color="emerald" />
          </div>
        </div>

        {/* Total Settlement */}
        {data.total_settlement != null && data.total_settlement > 0 && (
          <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-3xl font-bold text-blue-400">
                  {formatCurrency(data.total_settlement)}
                </div>
                <div className="text-sm text-zinc-500 mt-1">Total Settlement</div>
              </div>
              <div className="text-4xl opacity-50">✅</div>
            </div>
          </div>
        )}

        {/* Provider Count */}
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold text-purple-400">
                {data.providers.length}
              </div>
              <div className="text-sm text-zinc-500 mt-1">Medical Providers</div>
            </div>
            <div className="text-4xl opacity-50">🏥</div>
          </div>
        </div>

        {/* Total Files */}
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold text-amber-400">
                {totalFiles}
              </div>
              <div className="text-sm text-zinc-500 mt-1">Documents</div>
            </div>
            <div className="text-4xl opacity-50">📁</div>
          </div>
        </div>
      </div>

      {/* Provider List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-zinc-200">Providers</h3>
          <button
            onClick={() => {
              if (expandedProviders.size === data.providers.length) {
                setExpandedProviders(new Set());
              } else {
                setExpandedProviders(new Set(data.providers.map((_, i) => i)));
              }
            }}
            className="text-sm text-emerald-400 hover:text-emerald-300"
          >
            {expandedProviders.size === data.providers.length ? "Collapse All" : "Expand All"}
          </button>
        </div>
        <div className="space-y-2">
          {data.providers.map((provider, index) => (
            <ProviderCard
              key={index}
              provider={provider}
              isExpanded={expandedProviders.has(index)}
              onToggle={() => toggleProvider(index)}
            />
          ))}
        </div>
      </div>

      {/* URL Expiration Notice */}
      <div className="text-xs text-zinc-600 text-center pt-4 border-t border-zinc-800">
        Document links expire in 60 minutes. Refresh to generate new links.
      </div>
    </div>
  );
}
