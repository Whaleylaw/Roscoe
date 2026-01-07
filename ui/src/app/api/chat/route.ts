import { NextRequest } from "next/server";

const LANGGRAPH_URL = process.env.NEXT_PUBLIC_LANGGRAPH_URL || "http://localhost:2024";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { messages, thread_id } = body;

    console.log("[Chat API] Forwarding to LangGraph:", LANGGRAPH_URL);
    console.log("[Chat API] Thread ID:", thread_id || "(new thread)");
    console.log("[Chat API] Messages:", messages?.length || 0, "messages");

    // Create a thread if one wasn't provided
    let threadId = thread_id;
    if (!threadId) {
      console.log("[Chat API] Creating new thread...");
      const threadResponse = await fetch(`${LANGGRAPH_URL}/threads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });

      if (!threadResponse.ok) {
        const errorText = await threadResponse.text();
        console.error("[Chat API] Failed to create thread:", threadResponse.status, errorText);
        return new Response(
          JSON.stringify({ error: `Failed to create thread: ${threadResponse.status}`, details: errorText }),
          { status: threadResponse.status, headers: { "Content-Type": "application/json" } }
        );
      }

      const threadData = await threadResponse.json();
      threadId = threadData.thread_id;
      console.log("[Chat API] Created thread:", threadId);
    }

    // Forward to LangGraph with thread_id
    // Include "events" stream mode to capture tool calls in real-time
    const response = await fetch(`${LANGGRAPH_URL}/threads/${threadId}/runs/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        assistant_id: "roscoe_paralegal",
        input: {
          messages: messages.map((m: { role: string; content: string }) => ({
            type: m.role === "user" ? "human" : "ai",
            content: m.content,
          })),
        },
        stream_mode: ["messages", "updates", "events"],
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[Chat API] LangGraph error:", response.status, errorText);
      return new Response(
        JSON.stringify({ error: `LangGraph error: ${response.status}`, details: errorText }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    // Stream the response back with thread_id and run_id in headers
    const runId = response.headers.get("X-Run-Id") || "";
    const headers = new Headers({
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "X-Thread-Id": threadId,
    });

    // Forward the run ID if present
    if (runId) {
      headers.set("X-Run-Id", runId);
      console.log("[Chat API] Run ID:", runId);
    }

    // Pass through the SSE stream
    return new Response(response.body, { headers });

  } catch (error) {
    console.error("[Chat API] Error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to connect to LangGraph", details: String(error) }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

/**
 * Interrupt a running agent
 * DELETE /api/chat?thread_id=xxx&run_id=yyy
 */
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const threadId = searchParams.get("thread_id");
    const runId = searchParams.get("run_id");

    if (!threadId) {
      return new Response(
        JSON.stringify({ error: "thread_id is required" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    console.log("[Chat API] Cancelling run:", { threadId, runId });

    // If we have a specific run_id, cancel that run
    // Otherwise, cancel all runs on the thread
    let cancelUrl: string;
    if (runId) {
      cancelUrl = `${LANGGRAPH_URL}/threads/${threadId}/runs/${runId}/cancel`;
    } else {
      // Cancel the current run on the thread
      cancelUrl = `${LANGGRAPH_URL}/threads/${threadId}/runs/cancel`;
    }

    const response = await fetch(cancelUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      // 404 might mean no active run, which is fine
      if (response.status === 404) {
        return new Response(
          JSON.stringify({ success: true, message: "No active run to cancel" }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      const errorText = await response.text();
      console.error("[Chat API] Failed to cancel:", response.status, errorText);
      return new Response(
        JSON.stringify({ error: `Failed to cancel: ${response.status}`, details: errorText }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json().catch(() => ({}));
    console.log("[Chat API] Run cancelled:", data);

    return new Response(
      JSON.stringify({ success: true, ...data }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );

  } catch (error) {
    console.error("[Chat API] Cancel error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to cancel run", details: String(error) }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
