import { NextRequest } from "next/server";
import { promises as fs } from "fs";
import path from "path";

// Jobs are stored in LOCAL_WORKSPACE/analysis_jobs/ on the host
// The docker container maps /home/aaronwhaley/workspace_local -> /app/workspace_local
// When running on the host (VM), we read directly from /home/aaronwhaley/workspace_local
const LOCAL_WORKSPACE = process.env.LOCAL_WORKSPACE_HOST || "/home/aaronwhaley/workspace_local";
const ANALYSIS_JOBS_DIR = path.join(LOCAL_WORKSPACE, "analysis_jobs");

export interface AnalysisJob {
  job_id: string;
  case_name: string;
  case_folder: string;
  status: "queued" | "running" | "completed" | "failed";
  current_phase: string;
  created_at: string;
  updated_at?: string;
  message?: string;
  error?: string;
  result_path?: string;
  phase_history?: Array<{ phase: string; timestamp: string }>;
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const jobId = searchParams.get("id");

    if (jobId) {
      // Get specific job status
      console.log("[Jobs API] Fetching job:", jobId);

      const statusPath = path.join(ANALYSIS_JOBS_DIR, jobId, "status.json");

      try {
        const content = await fs.readFile(statusPath, "utf-8");
        const job = JSON.parse(content);
        return new Response(
          JSON.stringify(job),
          { headers: { "Content-Type": "application/json" } }
        );
      } catch (err) {
        console.error(`[Jobs API] Failed to read job ${jobId}:`, err);
        return new Response(
          JSON.stringify({ error: "Job not found", job_id: jobId }),
          { status: 404, headers: { "Content-Type": "application/json" } }
        );
      }
    }

    // List all jobs by reading the analysis_jobs directory directly
    console.log("[Jobs API] Listing all jobs from:", ANALYSIS_JOBS_DIR);

    const jobs: AnalysisJob[] = [];

    try {
      // Check if directory exists
      await fs.access(ANALYSIS_JOBS_DIR);

      // Read directory entries
      const entries = await fs.readdir(ANALYSIS_JOBS_DIR, { withFileTypes: true });

      // For each job directory, read the status.json
      for (const entry of entries) {
        if (entry.isDirectory() && entry.name.startsWith("med-analysis-")) {
          const statusPath = path.join(ANALYSIS_JOBS_DIR, entry.name, "status.json");

          try {
            const content = await fs.readFile(statusPath, "utf-8");
            const job = JSON.parse(content);
            jobs.push(job);
          } catch (err) {
            console.error(`[Jobs API] Failed to read status for ${entry.name}:`, err);
          }
        }
      }

      // Sort by created_at descending (newest first)
      jobs.sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );

      console.log(`[Jobs API] Found ${jobs.length} jobs`);

    } catch (err: any) {
      if (err.code === "ENOENT") {
        // Directory doesn't exist yet - that's OK, no jobs have been created
        console.log("[Jobs API] No analysis_jobs directory found (no jobs yet)");
      } else {
        console.error("[Jobs API] Error reading jobs directory:", err);
      }
    }

    return new Response(
      JSON.stringify({ jobs }),
      { headers: { "Content-Type": "application/json" } }
    );

  } catch (error) {
    console.error("[Jobs API] Error:", error);
    return new Response(
      JSON.stringify({ jobs: [], error: "Failed to fetch jobs", details: String(error) }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }
}
