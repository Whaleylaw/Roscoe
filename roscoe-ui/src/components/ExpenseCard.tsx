"use client";

import React, { useState } from "react";

interface Expense {
  description: string;
  category?: string | null;
  vendor?: string | null;
  amount: number;
  date_incurred?: string | null;
  date_paid?: string | null;
  status?: string | null;
  reimbursable?: boolean | null;
  notes?: string | null;
}

interface ExpenseCardData {
  client_name?: string;
  case_name?: string;
  expenses: Expense[];
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

function getCategoryIcon(category: string | null | undefined): string {
  if (!category) return "💰";
  const lower = category.toLowerCase();
  if (lower.includes("medical") || lower.includes("record")) return "🏥";
  if (lower.includes("filing") || lower.includes("court")) return "⚖️";
  if (lower.includes("expert") || lower.includes("witness")) return "👨‍⚕️";
  if (lower.includes("travel") || lower.includes("mileage")) return "🚗";
  if (lower.includes("copy") || lower.includes("print")) return "📄";
  if (lower.includes("service") || lower.includes("process")) return "📬";
  if (lower.includes("deposition")) return "🎤";
  if (lower.includes("investigation")) return "🔍";
  return "💰";
}

function getStatusColor(status: string | null | undefined): string {
  if (!status) return "bg-zinc-500";
  const lower = status.toLowerCase();
  if (lower.includes("paid")) return "bg-emerald-500";
  if (lower.includes("pending")) return "bg-yellow-500";
  if (lower.includes("submitted")) return "bg-blue-500";
  return "bg-zinc-500";
}

function ExpenseRow({ expense }: { expense: Expense }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-zinc-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between bg-zinc-800/50 hover:bg-zinc-800 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getCategoryIcon(expense.category)}</span>
          <div className="text-left">
            <div className="font-semibold text-zinc-200">{expense.description}</div>
            {expense.vendor && (
              <div className="text-sm text-zinc-500">{expense.vendor}</div>
            )}
            {expense.category && (
              <span className="text-xs px-2 py-0.5 rounded bg-zinc-700 text-zinc-400">
                {expense.category}
              </span>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {expense.reimbursable && (
            <span className="px-2 py-0.5 text-xs rounded bg-purple-500/20 text-purple-400">
              Reimbursable
            </span>
          )}
          
          {expense.status && (
            <span className={`px-2 py-0.5 text-xs rounded text-white ${getStatusColor(expense.status)}`}>
              {expense.status}
            </span>
          )}
          
          <div className="text-lg font-bold text-emerald-400">
            {formatCurrency(expense.amount)}
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

      {isExpanded && (
        <div className="p-4 bg-zinc-900/50 border-t border-zinc-700 space-y-4">
          {/* Details Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <div className="text-xs text-zinc-500">Amount</div>
              <div className="text-sm text-zinc-200">{formatCurrency(expense.amount)}</div>
            </div>
            {expense.date_incurred && (
              <div>
                <div className="text-xs text-zinc-500">Date Incurred</div>
                <div className="text-sm text-zinc-200">{expense.date_incurred}</div>
              </div>
            )}
            {expense.date_paid && (
              <div>
                <div className="text-xs text-zinc-500">Date Paid</div>
                <div className="text-sm text-emerald-400">{expense.date_paid}</div>
              </div>
            )}
          </div>

          {/* Notes */}
          {expense.notes && (
            <div className="pt-3 border-t border-zinc-700">
              <div className="text-xs text-zinc-500 mb-1">Notes</div>
              <p className="text-sm text-zinc-400 italic">{expense.notes}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ExpenseCard({ data }: { data: ExpenseCardData }) {
  // Calculate totals
  const totalExpenses = data.expenses.reduce((sum, e) => sum + (e.amount || 0), 0);
  const reimbursableTotal = data.expenses
    .filter(e => e.reimbursable)
    .reduce((sum, e) => sum + (e.amount || 0), 0);
  const paidTotal = data.expenses
    .filter(e => e.status?.toLowerCase().includes("paid"))
    .reduce((sum, e) => sum + (e.amount || 0), 0);
  const pendingTotal = totalExpenses - paidTotal;

  // Group by category
  const byCategory = data.expenses.reduce((acc, e) => {
    const cat = e.category || "Other";
    acc[cat] = (acc[cat] || 0) + (e.amount || 0);
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-zinc-700 pb-4">
        <h2 className="text-2xl font-bold text-zinc-100">Expenses</h2>
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
          <div className="text-2xl font-bold text-emerald-400">{formatCurrency(totalExpenses)}</div>
          <div className="text-sm text-zinc-500 mt-1">Total Expenses</div>
        </div>
        
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="text-2xl font-bold text-blue-400">{formatCurrency(paidTotal)}</div>
          <div className="text-sm text-zinc-500 mt-1">Paid</div>
        </div>
        
        {pendingTotal > 0 && (
          <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
            <div className="text-2xl font-bold text-yellow-400">{formatCurrency(pendingTotal)}</div>
            <div className="text-sm text-zinc-500 mt-1">Pending</div>
          </div>
        )}
        
        {reimbursableTotal > 0 && (
          <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
            <div className="text-2xl font-bold text-purple-400">{formatCurrency(reimbursableTotal)}</div>
            <div className="text-sm text-zinc-500 mt-1">Reimbursable</div>
          </div>
        )}
      </div>

      {/* Category Breakdown */}
      {Object.keys(byCategory).length > 1 && (
        <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700">
          <div className="text-sm font-medium text-zinc-400 mb-3">By Category</div>
          <div className="space-y-2">
            {Object.entries(byCategory)
              .sort(([, a], [, b]) => b - a)
              .map(([cat, amount]) => (
                <div key={cat} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{getCategoryIcon(cat)}</span>
                    <span className="text-sm text-zinc-300">{cat}</span>
                  </div>
                  <span className="text-sm font-medium text-zinc-200">{formatCurrency(amount)}</span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Expense List */}
      <div className="space-y-3">
        {data.expenses.map((expense, i) => (
          <ExpenseRow key={i} expense={expense} />
        ))}
      </div>

      {data.expenses.length === 0 && (
        <div className="text-center py-8 text-zinc-500">
          No expenses found
        </div>
      )}
    </div>
  );
}

