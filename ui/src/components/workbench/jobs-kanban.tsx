"use client";

import { RefreshCw, Clock, Play, CheckCircle, XCircle, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  useAnalysisJobs,
  AnalysisJob,
  JobStatus,
  formatRelativeTime,
  getPhaseDisplayName,
  columnColors,
} from "@/hooks/use-analysis-jobs";
import { cn } from "@/lib/utils";
import { useState } from "react";

// Column configuration
const columns: Array<{ status: JobStatus; title: string; icon: React.ReactNode }> = [
  { status: "queued", title: "Queued", icon: <Clock className="h-4 w-4" /> },
  { status: "running", title: "In Progress", icon: <Play className="h-4 w-4" /> },
  { status: "completed", title: "Completed", icon: <CheckCircle className="h-4 w-4" /> },
  { status: "failed", title: "Failed", icon: <XCircle className="h-4 w-4" /> },
];

export function JobsKanban() {
  const { jobs, loading, error, refresh, getJobsByStatus } = useAnalysisJobs();
  const [expandedJobs, setExpandedJobs] = useState<Set<string>>(new Set());

  const toggleExpanded = (jobId: string) => {
    setExpandedJobs((prev) => {
      const next = new Set(prev);
      if (next.has(jobId)) {
        next.delete(jobId);
      } else {
        next.add(jobId);
      }
      return next;
    });
  };

  if (loading && jobs.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">
        <RefreshCw className="h-5 w-5 animate-spin mr-2" />
        Loading jobs...
      </div>
    );
  }

  if (error && jobs.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-muted-foreground">
        <p className="text-sm">Failed to load jobs</p>
        <Button size="sm" variant="outline" onClick={refresh}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  const hasJobs = jobs.length > 0;

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="shrink-0 border-b p-3 flex items-center justify-between bg-white">
        <div className="flex items-center gap-2">
          <Play className="h-4 w-4 text-[#1e3a5f]" />
          <span className="text-sm font-medium text-[#1e3a5f]">Background Agents</span>
          {hasJobs && (
            <span className="text-xs text-muted-foreground bg-gray-100 px-2 py-0.5 rounded-full">
              {jobs.length} job{jobs.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
        <Button size="sm" variant="ghost" onClick={refresh} disabled={loading}>
          <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
        </Button>
      </div>

      {/* Kanban Board */}
      {hasJobs ? (
        <ScrollArea className="flex-1">
          <div className="p-3 space-y-3">
            {columns.map((column) => {
              const columnJobs = getJobsByStatus(column.status);
              if (columnJobs.length === 0) return null;

              return (
                <KanbanColumn
                  key={column.status}
                  status={column.status}
                  title={column.title}
                  icon={column.icon}
                  jobs={columnJobs}
                  expandedJobs={expandedJobs}
                  onToggleExpand={toggleExpanded}
                />
              );
            })}
          </div>
        </ScrollArea>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-muted-foreground">
            <Play className="h-8 w-8 mx-auto mb-2 opacity-30" />
            <p className="text-sm">No background jobs</p>
            <p className="text-xs mt-1">
              Medical record analysis jobs will appear here
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

interface KanbanColumnProps {
  status: JobStatus;
  title: string;
  icon: React.ReactNode;
  jobs: AnalysisJob[];
  expandedJobs: Set<string>;
  onToggleExpand: (jobId: string) => void;
}

function KanbanColumn({
  status,
  title,
  icon,
  jobs,
  expandedJobs,
  onToggleExpand,
}: KanbanColumnProps) {
  const colors = columnColors[status];

  return (
    <div className={cn("rounded-lg border", colors.border, colors.bg)}>
      {/* Column Header */}
      <div className={cn("px-3 py-2 rounded-t-lg flex items-center gap-2", colors.header)}>
        {icon}
        <span className="text-sm font-medium">{title}</span>
        <span className="text-xs opacity-70">({jobs.length})</span>
      </div>

      {/* Column Content */}
      <div className="p-2 space-y-2">
        {jobs.map((job) => (
          <JobCard
            key={job.job_id}
            job={job}
            isExpanded={expandedJobs.has(job.job_id)}
            onToggle={() => onToggleExpand(job.job_id)}
          />
        ))}
      </div>
    </div>
  );
}

interface JobCardProps {
  job: AnalysisJob;
  isExpanded: boolean;
  onToggle: () => void;
}

function JobCard({ job, isExpanded, onToggle }: JobCardProps) {
  return (
    <div className="bg-white rounded-md border shadow-sm overflow-hidden">
      {/* Card Header */}
      <button
        onClick={onToggle}
        className="w-full px-3 py-2 flex items-start justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex-1 min-w-0 text-left">
          <p className="text-sm font-medium truncate text-[#1e3a5f]">
            {job.case_name || "Unknown Case"}
          </p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-muted-foreground">
              {getPhaseDisplayName(job.current_phase)}
            </span>
            <span className="text-xs text-muted-foreground">
              {formatRelativeTime(job.created_at)}
            </span>
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground shrink-0 ml-2" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground shrink-0 ml-2" />
        )}
      </button>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="px-3 pb-3 pt-1 border-t bg-gray-50/50 space-y-2">
          {/* Job ID */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Job ID</span>
            <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded font-mono">
              {job.job_id}
            </code>
          </div>

          {/* Case Folder */}
          <div className="flex items-start justify-between gap-2">
            <span className="text-xs text-muted-foreground shrink-0">Folder</span>
            <span className="text-xs text-right truncate max-w-[180px]" title={job.case_folder}>
              {job.case_folder}
            </span>
          </div>

          {/* Message */}
          {job.message && (
            <div>
              <span className="text-xs text-muted-foreground block mb-1">Status</span>
              <p className="text-xs">{job.message}</p>
            </div>
          )}

          {/* Error */}
          {job.error && (
            <div>
              <span className="text-xs text-red-600 block mb-1">Error</span>
              <p className="text-xs text-red-700 bg-red-50 p-2 rounded">
                {job.error}
              </p>
            </div>
          )}

          {/* Result Path */}
          {job.result_path && (
            <div className="flex items-start justify-between gap-2">
              <span className="text-xs text-muted-foreground shrink-0">Result</span>
              <span className="text-xs text-right truncate max-w-[180px]" title={job.result_path}>
                {job.result_path}
              </span>
            </div>
          )}

          {/* Phase History (last 3) */}
          {job.phase_history && job.phase_history.length > 0 && (
            <div>
              <span className="text-xs text-muted-foreground block mb-1">Recent Phases</span>
              <div className="space-y-1">
                {job.phase_history.slice(-3).map((ph, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span>{getPhaseDisplayName(ph.phase)}</span>
                    <span className="text-muted-foreground">
                      {formatRelativeTime(ph.timestamp)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Timestamps */}
          <div className="pt-2 border-t flex items-center justify-between text-xs text-muted-foreground">
            <span>Created {formatRelativeTime(job.created_at)}</span>
            {job.updated_at && (
              <span>Updated {formatRelativeTime(job.updated_at)}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
