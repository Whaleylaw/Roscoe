"use client";

import React from "react";

interface ContactData {
  name: string;
  roles?: string[];
  company?: string | null;
  email?: string | null;
  phone?: string | null;
  fax?: string | null;
  address?: string | null;
  notes?: string | null;
}

function getAvatarColor(name: string): string {
  const colors = [
    "from-emerald-500 to-teal-600",
    "from-blue-500 to-indigo-600",
    "from-purple-500 to-pink-600",
    "from-orange-500 to-red-600",
    "from-yellow-500 to-amber-600",
    "from-cyan-500 to-blue-600",
    "from-rose-500 to-pink-600",
    "from-violet-500 to-purple-600",
  ];
  const index = name.charCodeAt(0) % colors.length;
  return colors[index];
}

function getRoleIcon(role: string): string {
  const lower = role.toLowerCase();
  if (lower.includes("attorney") || lower.includes("lawyer")) return "⚖️";
  if (lower.includes("adjuster")) return "📋";
  if (lower.includes("doctor") || lower.includes("physician") || lower.includes("dr.")) return "👨‍⚕️";
  if (lower.includes("nurse")) return "👩‍⚕️";
  if (lower.includes("paralegal")) return "📝";
  if (lower.includes("client")) return "👤";
  if (lower.includes("expert") || lower.includes("witness")) return "🎓";
  if (lower.includes("insurance")) return "🏢";
  if (lower.includes("medical")) return "🏥";
  return "👤";
}

export default function ContactCard({ data }: { data: ContactData }) {
  const initials = data.name
    .split(" ")
    .map(n => n.charAt(0))
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="bg-zinc-800/50 rounded-xl border border-zinc-700 overflow-hidden max-w-md">
      {/* Header with Avatar */}
      <div className="p-6 flex items-center gap-4">
        <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${getAvatarColor(data.name)} flex items-center justify-center text-white text-xl font-bold shadow-lg`}>
          {initials}
        </div>
        <div className="flex-1">
          <h2 className="text-xl font-bold text-zinc-100">{data.name}</h2>
          {data.company && (
            <p className="text-zinc-400 text-sm">{data.company}</p>
          )}
          {data.roles && data.roles.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {data.roles.map((role, i) => (
                <span 
                  key={i}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-zinc-700 text-zinc-300"
                >
                  {getRoleIcon(role)} {role}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Contact Details */}
      <div className="px-6 pb-6 space-y-3">
        {data.phone && (
          <a 
            href={`tel:${data.phone}`}
            className="flex items-center gap-3 p-3 rounded-lg bg-zinc-900/50 hover:bg-zinc-900 transition-colors group"
          >
            <span className="text-emerald-400 text-xl">📞</span>
            <div className="flex-1">
              <div className="text-xs text-zinc-500">Phone</div>
              <div className="text-sm text-blue-400 group-hover:underline">{data.phone}</div>
            </div>
          </a>
        )}

        {data.email && (
          <a 
            href={`mailto:${data.email}`}
            className="flex items-center gap-3 p-3 rounded-lg bg-zinc-900/50 hover:bg-zinc-900 transition-colors group"
          >
            <span className="text-blue-400 text-xl">📧</span>
            <div className="flex-1">
              <div className="text-xs text-zinc-500">Email</div>
              <div className="text-sm text-blue-400 group-hover:underline truncate">{data.email}</div>
            </div>
          </a>
        )}

        {data.fax && (
          <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-900/50">
            <span className="text-purple-400 text-xl">📠</span>
            <div className="flex-1">
              <div className="text-xs text-zinc-500">Fax</div>
              <div className="text-sm text-zinc-300">{data.fax}</div>
            </div>
          </div>
        )}

        {data.address && (
          <div className="flex items-center gap-3 p-3 rounded-lg bg-zinc-900/50">
            <span className="text-orange-400 text-xl">📍</span>
            <div className="flex-1">
              <div className="text-xs text-zinc-500">Address</div>
              <div className="text-sm text-zinc-300">{data.address}</div>
            </div>
          </div>
        )}

        {data.notes && (
          <div className="pt-3 border-t border-zinc-700">
            <div className="text-xs text-zinc-500 mb-1">Notes</div>
            <p className="text-sm text-zinc-400 italic">{data.notes}</p>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="px-6 pb-6 flex gap-2">
        {data.phone && (
          <a 
            href={`tel:${data.phone}`}
            className="flex-1 py-2 px-4 rounded-lg bg-emerald-500/20 text-emerald-400 text-center text-sm font-medium hover:bg-emerald-500/30 transition-colors"
          >
            Call
          </a>
        )}
        {data.email && (
          <a 
            href={`mailto:${data.email}`}
            className="flex-1 py-2 px-4 rounded-lg bg-blue-500/20 text-blue-400 text-center text-sm font-medium hover:bg-blue-500/30 transition-colors"
          >
            Email
          </a>
        )}
      </div>
    </div>
  );
}

