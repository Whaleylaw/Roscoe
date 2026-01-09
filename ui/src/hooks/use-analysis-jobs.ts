"use client";

import { useState, useEffect, useCallback } from "react";

export type JobStatus = "queued" | "running" | "completed" | "failed";

export interface AnalysisJob {
  job_id: string;
  case_name: string;
  case_folder: string;
  status: JobStatus;
  current_phase: string;
  created_at: string;
  updated_at?: string;
  message?: string;
  error?: string;
  result_path?: string;
  phase_history?: Array<{ phase: string; timestamp: string }>;
}

interface UseAnalysisJobsResult {
  jobs: AnalysisJob[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  getJobsByStatus: (status: JobStatus) => AnalysisJob[];
}

// Polling interval in milliseconds (5 seconds for active jobs, 30 seconds when idle)
const ACTIVE_POLL_INTERVAL = 5000;
const IDLE_POLL_INTERVAL = 30000;

export function useAnalysisJobs(): UseAnalysisJobsResult {
  const [jobs, setJobs] = useState<AnalysisJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    try {
      const response = await fetch("/api/jobs");

      if (!response.ok) {
        throw new Error(`Failed to fetch jobs: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        console.warn("[useAnalysisJobs] API returned error:", data.error);
      }

      setJobs(data.jobs || []);
      setError(null);
    } catch (err) {
      console.error("[useAnalysisJobs] Error:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch jobs");
    } finally {
      setLoading(false);
    }
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    await fetchJobs();
  }, [fetchJobs]);

  const getJobsByStatus = useCallback(
    (status: JobStatus): AnalysisJob[] => {
      return jobs.filter((job) => job.status === status);
    },
    [jobs]
  );

  // Initial fetch
  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  // Polling - faster when there are active jobs
  useEffect(() => {
    const hasActiveJobs = jobs.some(
      (job) => job.status === "queued" || job.status === "running"
    );

    const interval = hasActiveJobs ? ACTIVE_POLL_INTERVAL : IDLE_POLL_INTERVAL;

    const pollTimer = setInterval(() => {
      fetchJobs();
    }, interval);

    return () => clearInterval(pollTimer);
  }, [jobs, fetchJobs]);

  return {
    jobs,
    loading,
    error,
    refresh,
    getJobsByStatus,
  };
}

// Helper function to format relative time
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

// Helper function to get phase display name
export function getPhaseDisplayName(phase: string): string {
  const phaseMap: Record<string, string> = {
    setup: "Setup",
    fact_investigation: "Fact Investigation",
    medical_organization: "Organizing Records",
    provider_extraction: "Extracting Providers",
    treatment_timeline: "Building Timeline",
    medical_analysis: "Medical Analysis",
    report_generation: "Generating Report",
    finalization: "Finalizing",
    complete: "Complete",
    failed: "Failed",
  };

  return phaseMap[phase] || phase;
}

// Status icons for display
export const statusIcons: Record<JobStatus, string> = {
  queued: "⏳",
  running: "🔄",
  completed: "✅",
  failed: "❌",
};

// Status colors for styling
export const statusColors: Record<JobStatus, string> = {
  queued: "text-yellow-600 bg-yellow-50 border-yellow-200",
  running: "text-blue-600 bg-blue-50 border-blue-200",
  completed: "text-green-600 bg-green-50 border-green-200",
  failed: "text-red-600 bg-red-50 border-red-200",
};

// Kanban column colors
export const columnColors: Record<JobStatus, { bg: string; border: string; header: string }> = {
  queued: {
    bg: "bg-yellow-50/50",
    border: "border-yellow-200",
    header: "bg-yellow-100 text-yellow-800",
  },
  running: {
    bg: "bg-blue-50/50",
    border: "border-blue-200",
    header: "bg-blue-100 text-blue-800",
  },
  completed: {
    bg: "bg-green-50/50",
    border: "border-green-200",
    header: "bg-green-100 text-green-800",
  },
  failed: {
    bg: "bg-red-50/50",
    border: "border-red-200",
    header: "bg-red-100 text-red-800",
  },
};
