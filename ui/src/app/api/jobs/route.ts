import { NextRequest } from "next/server";

const LANGGRAPH_URL = process.env.NEXT_PUBLIC_LANGGRAPH_URL || "http://localhost:8123";

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

    // Call the agent to list or get job status
    // We need to invoke the appropriate tool through the LangGraph API

    if (jobId) {
      // Get specific job status
      console.log("[Jobs API] Fetching job:", jobId);

      const response = await fetch(`${LANGGRAPH_URL}/threads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        throw new Error(`Failed to create thread: ${response.status}`);
      }

      const thread = await response.json();

      // Run the agent with get_medical_analysis_status tool
      const runResponse = await fetch(
        `${LANGGRAPH_URL}/threads/${thread.thread_id}/runs`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assistant_id: "roscoe_paralegal",
            input: {
              messages: [
                {
                  role: "user",
                  content: `Get status of analysis job ${jobId}. Use the get_medical_analysis_status tool.`,
                },
              ],
            },
            config: {
              configurable: {
                tool_call_only: true,
              },
            },
          }),
        }
      );

      if (!runResponse.ok) {
        const errorText = await runResponse.text();
        console.error("[Jobs API] Run error:", errorText);
        throw new Error(`Failed to run agent: ${runResponse.status}`);
      }

      const runResult = await runResponse.json();

      // Parse the tool result to extract job data
      // For now, return a placeholder that will be populated by the tool
      return new Response(
        JSON.stringify({
          job_id: jobId,
          status: "unknown",
          message: "Fetching status..."
        }),
        { headers: { "Content-Type": "application/json" } }
      );
    }

    // List all jobs - call the workspace file API to read analysis_jobs directory
    console.log("[Jobs API] Listing all jobs");

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
      // Read the analysis_jobs directory from workspace
      const listResponse = await fetch(
        `${request.nextUrl.origin}/api/workspace/list?path=/analysis_jobs`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
        }
      );

      clearTimeout(timeoutId);

      if (!listResponse.ok) {
        // Directory might not exist yet
        console.log("[Jobs API] No analysis_jobs directory found");
        return new Response(
          JSON.stringify({ jobs: [] }),
          { headers: { "Content-Type": "application/json" } }
        );
      }

      const files = await listResponse.json();

      // For each job directory, read the status.json
      const jobs: AnalysisJob[] = [];

      for (const file of files) {
        if (file.type === "directory" && file.name.startsWith("med-analysis-")) {
          try {
            const statusResponse = await fetch(
              `${request.nextUrl.origin}/api/workspace/file?path=/analysis_jobs/${file.name}/status.json`,
              {
                method: "GET",
                headers: { "Content-Type": "application/json" },
              }
            );

            if (statusResponse.ok) {
              const statusData = await statusResponse.json();
              jobs.push(statusData);
            }
          } catch (err) {
            console.error(`[Jobs API] Failed to read status for ${file.name}:`, err);
          }
        }
      }

      // Sort by created_at descending (newest first)
      jobs.sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );

      return new Response(
        JSON.stringify({ jobs }),
        { headers: { "Content-Type": "application/json" } }
      );

    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === "AbortError") {
        console.warn("[Jobs API] Request timed out");
        return new Response(
          JSON.stringify({ jobs: [], error: "Request timed out" }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      throw fetchError;
    }

  } catch (error) {
    console.error("[Jobs API] Error:", error);
    return new Response(
      JSON.stringify({ jobs: [], error: "Failed to fetch jobs", details: String(error) }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }
}
