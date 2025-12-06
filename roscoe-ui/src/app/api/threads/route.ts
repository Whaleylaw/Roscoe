import { NextRequest, NextResponse } from "next/server";

// Get LangGraph API URL
const LANGGRAPH_URL = process.env.ROSCOE_LANGGRAPH_URL || "http://localhost:8123";

interface Thread {
  thread_id: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
  status?: string;
  values?: Record<string, unknown>;
}

interface Run {
  run_id: string;
  thread_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export async function GET(req: NextRequest) {
  try {
    // Fetch threads from LangGraph API (limit to 20 most recent for performance)
    const threadsResponse = await fetch(`${LANGGRAPH_URL}/threads/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ limit: 20 }),
    });

    if (!threadsResponse.ok) {
      console.error("Failed to fetch threads:", threadsResponse.statusText);
      return NextResponse.json({ threads: [] });
    }

    const threads: Thread[] = await threadsResponse.json();

    // For each thread, get the latest run status
    const enrichedThreads = await Promise.all(
      threads.map(async (thread) => {
        try {
          // Get runs for this thread
          const runsResponse = await fetch(
            `${LANGGRAPH_URL}/threads/${thread.thread_id}/runs`,
            {
              method: "GET",
              headers: { "Content-Type": "application/json" },
            }
          );

          let runStatus: "running" | "complete" | "error" = "complete";
          let lastMessage = "";

          if (runsResponse.ok) {
            const runs: Run[] = await runsResponse.json();
            if (runs.length > 0) {
              const latestRun = runs[0];
              if (latestRun.status === "pending" || latestRun.status === "running") {
                runStatus = "running";
              } else if (latestRun.status === "error") {
                runStatus = "error";
              }
            }
          }

          // Try to get the last message from thread state
          try {
            const stateResponse = await fetch(
              `${LANGGRAPH_URL}/threads/${thread.thread_id}/state`,
              {
                method: "GET",
                headers: { "Content-Type": "application/json" },
              }
            );

            if (stateResponse.ok) {
              const state = await stateResponse.json();
              const messages = state.values?.messages || [];
              if (messages.length > 0) {
                const lastMsg = messages[messages.length - 1];
                if (typeof lastMsg.content === "string") {
                  lastMessage = lastMsg.content.slice(0, 50);
                } else if (Array.isArray(lastMsg.content)) {
                  const textBlock = lastMsg.content.find(
                    (b: { type: string }) => b.type === "text"
                  );
                  if (textBlock?.text) {
                    lastMessage = textBlock.text.slice(0, 50);
                  }
                }
              }
            }
          } catch (e) {
            // Ignore state fetch errors
          }

          return {
            ...thread,
            runStatus,
            lastMessage,
          };
        } catch (e) {
          return {
            ...thread,
            runStatus: "complete" as const,
            lastMessage: "",
          };
        }
      })
    );

    // Sort by updated_at descending
    enrichedThreads.sort((a, b) => {
      const dateA = new Date(a.updated_at || a.created_at).getTime();
      const dateB = new Date(b.updated_at || b.created_at).getTime();
      return dateB - dateA;
    });

    return NextResponse.json({ threads: enrichedThreads });
  } catch (error) {
    console.error("Error fetching threads:", error);
    return NextResponse.json({ threads: [], error: "Failed to fetch threads" });
  }
}

// Create a new thread
export async function POST(req: NextRequest) {
  try {
    const response = await fetch(`${LANGGRAPH_URL}/threads`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to create thread" },
        { status: response.status }
      );
    }

    const thread = await response.json();
    return NextResponse.json(thread);
  } catch (error) {
    console.error("Error creating thread:", error);
    return NextResponse.json(
      { error: "Failed to create thread" },
      { status: 500 }
    );
  }
}

// Delete a thread
export async function DELETE(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const threadId = searchParams.get("thread_id");

    if (!threadId) {
      return NextResponse.json(
        { error: "thread_id is required" },
        { status: 400 }
      );
    }

    const response = await fetch(`${LANGGRAPH_URL}/threads/${threadId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to delete thread" },
        { status: response.status }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Error deleting thread:", error);
    return NextResponse.json(
      { error: "Failed to delete thread" },
      { status: 500 }
    );
  }
}

