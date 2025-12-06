"use client";

import React, { useState } from "react";

// Type definitions
interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  time?: string;
  end_time?: string;
  type: "deadline" | "task" | "hearing" | "deposition" | "meeting" | "reminder";
  project_name?: string;
  priority: "high" | "normal" | "low";
  status: "pending" | "completed" | "cancelled";
  description?: string;
  created_by?: string;
  created_at?: string;
}

interface DayMetadata {
  day_name: string;
  day_short: string;
  month_name: string;
  day_number: number;
  relative?: string;
  is_today: boolean;
  is_past: boolean;
  is_weekend: boolean;
}

interface CalendarDay {
  date: string;
  metadata: DayMetadata;
  events: CalendarEvent[];
  event_count: number;
}

interface CalendarSummary {
  total_events: number;
  by_type: Record<string, number>;
  by_priority: Record<string, number>;
  by_project: Record<string, number>;
}

interface CalendarData {
  view: "week" | "month" | "list";
  date_range: {
    start: string;
    end: string;
  };
  days: CalendarDay[];
  summary: CalendarSummary;
}

interface CalendarViewProps {
  data: CalendarData;
}

// Event type colors and icons
const eventTypeConfig: Record<string, { color: string; icon: string; label: string }> = {
  deadline: { color: "bg-red-500/20 text-red-400 border-red-500/30", icon: "⏰", label: "Deadline" },
  task: { color: "bg-blue-500/20 text-blue-400 border-blue-500/30", icon: "📋", label: "Task" },
  hearing: { color: "bg-purple-500/20 text-purple-400 border-purple-500/30", icon: "⚖️", label: "Hearing" },
  deposition: { color: "bg-amber-500/20 text-amber-400 border-amber-500/30", icon: "📝", label: "Deposition" },
  meeting: { color: "bg-green-500/20 text-green-400 border-green-500/30", icon: "👥", label: "Meeting" },
  reminder: { color: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30", icon: "🔔", label: "Reminder" },
};

// Priority colors
const priorityConfig: Record<string, { dot: string; label: string }> = {
  high: { dot: "bg-red-500", label: "High" },
  normal: { dot: "bg-yellow-500", label: "Normal" },
  low: { dot: "bg-green-500", label: "Low" },
};

// Event Card Component
const EventCard: React.FC<{ event: CalendarEvent; expanded?: boolean }> = ({ event, expanded = false }) => {
  const [isExpanded, setIsExpanded] = useState(expanded);
  const typeConfig = eventTypeConfig[event.type] || eventTypeConfig.task;
  const priority = priorityConfig[event.priority] || priorityConfig.normal;

  return (
    <div
      className={`rounded-lg border p-3 cursor-pointer transition-all hover:border-zinc-600 ${typeConfig.color}`}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-lg">{typeConfig.icon}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${priority.dot}`} title={priority.label} />
              <span className="font-medium truncate">{event.title}</span>
            </div>
            {event.time && (
              <div className="text-xs text-zinc-400 mt-0.5">
                {event.time}
                {event.end_time && ` - ${event.end_time}`}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1">
          {event.status === "completed" && (
            <span className="text-green-400 text-sm">✓</span>
          )}
          {event.status === "cancelled" && (
            <span className="text-zinc-500 text-sm">✗</span>
          )}
        </div>
      </div>

      {event.project_name && (
        <div className="mt-2 text-xs text-zinc-400 truncate">
          📁 {event.project_name}
        </div>
      )}

      {isExpanded && event.description && (
        <div className="mt-3 pt-3 border-t border-zinc-700/50 text-sm text-zinc-300">
          {event.description}
        </div>
      )}
    </div>
  );
};

// Day Column Component (for week view)
const DayColumn: React.FC<{ day: CalendarDay }> = ({ day }) => {
  const { metadata, events } = day;
  
  return (
    <div className={`flex-1 min-w-[140px] ${metadata.is_weekend ? 'opacity-80' : ''}`}>
      <div
        className={`text-center p-3 rounded-t-lg border-b border-zinc-700 ${
          metadata.is_today
            ? "bg-emerald-500/20 border-emerald-500/30"
            : metadata.is_past
            ? "bg-zinc-800/50"
            : "bg-zinc-800"
        }`}
      >
        <div className="text-xs text-zinc-400 uppercase tracking-wide">
          {metadata.day_short}
        </div>
        <div className={`text-2xl font-bold ${metadata.is_today ? 'text-emerald-400' : ''}`}>
          {metadata.day_number}
        </div>
        {metadata.relative && (
          <div className="text-xs text-zinc-500">{metadata.relative}</div>
        )}
      </div>
      <div className="p-2 space-y-2 min-h-[200px] bg-zinc-900/30 rounded-b-lg">
        {events.length === 0 ? (
          <div className="text-center text-zinc-600 text-xs py-4">No events</div>
        ) : (
          events.map((event) => (
            <EventCard key={event.id} event={event} />
          ))
        )}
      </div>
    </div>
  );
};

// List View Component
const ListView: React.FC<{ days: CalendarDay[] }> = ({ days }) => {
  // Filter to only days with events
  const daysWithEvents = days.filter(d => d.events.length > 0);

  if (daysWithEvents.length === 0) {
    return (
      <div className="text-center py-12 text-zinc-500">
        <div className="text-4xl mb-3">📅</div>
        <div>No events scheduled</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {daysWithEvents.map((day) => (
        <div key={day.date}>
          <div className={`flex items-center gap-3 mb-3 ${day.metadata.is_today ? 'text-emerald-400' : 'text-zinc-300'}`}>
            <div className="text-lg font-semibold">
              {day.metadata.day_name}, {day.metadata.month_name} {day.metadata.day_number}
            </div>
            {day.metadata.relative && (
              <span className="text-xs bg-zinc-800 px-2 py-0.5 rounded">
                {day.metadata.relative}
              </span>
            )}
            <span className="text-xs text-zinc-500">
              {day.event_count} event{day.event_count !== 1 ? 's' : ''}
            </span>
          </div>
          <div className="space-y-2 pl-4 border-l-2 border-zinc-700">
            {day.events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

// Summary Stats Component
const SummaryStats: React.FC<{ summary: CalendarSummary }> = ({ summary }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      <div className="bg-zinc-800/50 rounded-lg p-3 text-center">
        <div className="text-2xl font-bold text-emerald-400">{summary.total_events}</div>
        <div className="text-xs text-zinc-400">Total Events</div>
      </div>
      
      {summary.by_type.deadline && (
        <div className="bg-red-500/10 rounded-lg p-3 text-center border border-red-500/20">
          <div className="text-2xl font-bold text-red-400">{summary.by_type.deadline}</div>
          <div className="text-xs text-zinc-400">Deadlines</div>
        </div>
      )}
      
      {summary.by_priority.high && (
        <div className="bg-orange-500/10 rounded-lg p-3 text-center border border-orange-500/20">
          <div className="text-2xl font-bold text-orange-400">{summary.by_priority.high}</div>
          <div className="text-xs text-zinc-400">High Priority</div>
        </div>
      )}
      
      <div className="bg-zinc-800/50 rounded-lg p-3 text-center">
        <div className="text-2xl font-bold text-zinc-300">
          {Object.keys(summary.by_project).length}
        </div>
        <div className="text-xs text-zinc-400">Cases</div>
      </div>
    </div>
  );
};

// Main CalendarView Component
const CalendarView: React.FC<CalendarViewProps> = ({ data }) => {
  const [viewMode, setViewMode] = useState<"week" | "list">(data.view === "list" ? "list" : "week");

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-zinc-100 flex items-center gap-2">
            <span>📅</span> Calendar
          </h2>
          <p className="text-sm text-zinc-400 mt-1">
            {data.date_range.start} to {data.date_range.end}
          </p>
        </div>
        
        {/* View Toggle */}
        <div className="flex items-center gap-1 bg-zinc-800 rounded-lg p-1">
          <button
            onClick={() => setViewMode("week")}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              viewMode === "week"
                ? "bg-emerald-500/20 text-emerald-400"
                : "text-zinc-400 hover:text-zinc-300"
            }`}
          >
            Week
          </button>
          <button
            onClick={() => setViewMode("list")}
            className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
              viewMode === "list"
                ? "bg-emerald-500/20 text-emerald-400"
                : "text-zinc-400 hover:text-zinc-300"
            }`}
          >
            List
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <SummaryStats summary={data.summary} />

      {/* Calendar Content */}
      {viewMode === "week" ? (
        <div className="flex gap-2 overflow-x-auto pb-4">
          {data.days.slice(0, 7).map((day) => (
            <DayColumn key={day.date} day={day} />
          ))}
        </div>
      ) : (
        <ListView days={data.days} />
      )}

      {/* Legend */}
      <div className="flex flex-wrap gap-3 pt-4 border-t border-zinc-800">
        {Object.entries(eventTypeConfig).map(([type, config]) => (
          <div key={type} className="flex items-center gap-1.5 text-xs text-zinc-400">
            <span>{config.icon}</span>
            <span>{config.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CalendarView;

