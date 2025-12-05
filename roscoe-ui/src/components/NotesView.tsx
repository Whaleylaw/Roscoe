"use client";

import React, { useState } from "react";
import {
  MessageSquare,
  Calendar,
  User,
  Tag,
  Filter,
  ChevronDown,
  ChevronUp,
  Clock,
} from "lucide-react";

interface Note {
  date: string;
  time: string;
  author: string;
  type: string;
  summary: string;
  content: string;
  id?: number;
}

interface NotesViewData {
  project_name: string;
  total_notes: number;
  filtered_count: number;
  days_filter?: number;
  type_filter?: string;
  date_range: {
    oldest: string | null;
    newest: string | null;
  };
  available_types: string[];
  notes: Note[];
}

interface NotesViewProps {
  data: NotesViewData;
}

const NoteCard: React.FC<{ note: Note; isExpanded: boolean; onToggle: () => void }> = ({
  note,
  isExpanded,
  onToggle,
}) => {
  // Determine card accent color based on note type
  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      "File Organization": "border-l-violet-500",
      "Client Contact": "border-l-emerald-500",
      "Medical": "border-l-blue-500",
      "Insurance": "border-l-amber-500",
      "Settlement": "border-l-green-500",
      "Litigation": "border-l-red-500",
      "General": "border-l-zinc-500",
    };
    return colors[type] || "border-l-zinc-500";
  };

  const getTypeBadgeColor = (type: string) => {
    const colors: Record<string, string> = {
      "File Organization": "bg-violet-500/20 text-violet-300",
      "Client Contact": "bg-emerald-500/20 text-emerald-300",
      "Medical": "bg-blue-500/20 text-blue-300",
      "Insurance": "bg-amber-500/20 text-amber-300",
      "Settlement": "bg-green-500/20 text-green-300",
      "Litigation": "bg-red-500/20 text-red-300",
      "General": "bg-zinc-500/20 text-zinc-300",
    };
    return colors[type] || "bg-zinc-500/20 text-zinc-300";
  };

  // Truncate content for preview
  const contentPreview = note.content.length > 200 
    ? note.content.substring(0, 200) + "..." 
    : note.content;

  return (
    <div 
      className={`bg-zinc-800/50 rounded-lg border border-zinc-700/50 border-l-4 ${getTypeColor(note.type)} overflow-hidden transition-all duration-200 hover:border-zinc-600`}
    >
      {/* Header - always visible */}
      <div 
        className="p-4 cursor-pointer"
        onClick={onToggle}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {/* Date and Type Row */}
            <div className="flex items-center gap-3 mb-2">
              <div className="flex items-center gap-1.5 text-xs text-zinc-400">
                <Calendar className="w-3.5 h-3.5" />
                <span>{note.date}</span>
              </div>
              {note.time && (
                <div className="flex items-center gap-1 text-xs text-zinc-500">
                  <Clock className="w-3 h-3" />
                  <span>{note.time}</span>
                </div>
              )}
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getTypeBadgeColor(note.type)}`}>
                {note.type}
              </span>
            </div>
            
            {/* Author */}
            <div className="flex items-center gap-1.5 text-sm text-zinc-300 mb-2">
              <User className="w-3.5 h-3.5 text-zinc-500" />
              <span>{note.author}</span>
            </div>
            
            {/* Summary or Content Preview */}
            <p className="text-sm text-zinc-400 line-clamp-2">
              {note.summary || contentPreview}
            </p>
          </div>
          
          {/* Expand/Collapse Button */}
          <button className="p-1 text-zinc-500 hover:text-zinc-300 transition-colors">
            {isExpanded ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
      
      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-zinc-700/50">
          <div className="pt-4">
            {note.summary && (
              <div className="mb-3">
                <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wide mb-1">Summary</h4>
                <p className="text-sm text-zinc-300">{note.summary}</p>
              </div>
            )}
            <div>
              <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wide mb-1">Full Note</h4>
              <div className="text-sm text-zinc-300 whitespace-pre-wrap bg-zinc-900/50 rounded-lg p-3 max-h-96 overflow-y-auto">
                {note.content}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const NotesView: React.FC<NotesViewProps> = ({ data }) => {
  const [expandedNotes, setExpandedNotes] = useState<Set<number>>(new Set());
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const toggleNote = (index: number) => {
    setExpandedNotes((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  // Apply local filters
  const filteredNotes = data.notes.filter((note) => {
    if (typeFilter && note.type !== typeFilter) return false;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        note.content.toLowerCase().includes(query) ||
        note.summary.toLowerCase().includes(query) ||
        note.author.toLowerCase().includes(query)
      );
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/20 rounded-lg">
            <MessageSquare className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-white">Case Notes</h2>
            <p className="text-sm text-zinc-400">{data.project_name}</p>
          </div>
        </div>
        
        {/* Stats */}
        <div className="flex items-center gap-4 text-sm">
          <div className="text-zinc-400">
            <span className="text-white font-medium">{data.filtered_count}</span> of{" "}
            <span className="text-white font-medium">{data.total_notes}</span> notes
          </div>
          {data.days_filter && (
            <span className="px-2 py-1 bg-zinc-800 rounded text-zinc-400">
              Last {data.days_filter} days
            </span>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 bg-zinc-800/30 rounded-lg p-3">
        <div className="flex items-center gap-2 text-zinc-400">
          <Filter className="w-4 h-4" />
          <span className="text-sm">Filters:</span>
        </div>
        
        {/* Search */}
        <input
          type="text"
          placeholder="Search notes..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 bg-zinc-900/50 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-600"
        />
        
        {/* Type Filter */}
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-zinc-900/50 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-zinc-600"
        >
          <option value="">All Types</option>
          {data.available_types.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      {/* Date Range Info */}
      {data.date_range.oldest && data.date_range.newest && (
        <div className="flex items-center gap-2 text-xs text-zinc-500">
          <Calendar className="w-3.5 h-3.5" />
          <span>
            Showing notes from {data.date_range.oldest} to {data.date_range.newest}
          </span>
        </div>
      )}

      {/* Notes List */}
      <div className="space-y-3">
        {filteredNotes.length === 0 ? (
          <div className="text-center py-12 text-zinc-500">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No notes found</p>
            {(typeFilter || searchQuery) && (
              <p className="text-sm mt-1">Try adjusting your filters</p>
            )}
          </div>
        ) : (
          filteredNotes.map((note, index) => (
            <NoteCard
              key={note.id || index}
              note={note}
              isExpanded={expandedNotes.has(index)}
              onToggle={() => toggleNote(index)}
            />
          ))
        )}
      </div>

      {/* Footer Stats */}
      <div className="flex items-center justify-between text-xs text-zinc-500 pt-4 border-t border-zinc-800">
        <span>
          Showing {filteredNotes.length} note{filteredNotes.length !== 1 ? "s" : ""}
        </span>
        <span>
          {data.available_types.length} note type{data.available_types.length !== 1 ? "s" : ""} in case
        </span>
      </div>
    </div>
  );
};

export default NotesView;

