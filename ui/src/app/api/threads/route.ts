import { NextRequest } from "next/server";

const LANGGRAPH_URL = process.env.NEXT_PUBLIC_LANGGRAPH_URL || "http://localhost:8123";

export async function GET(request: NextRequest) {
  try {
    // Check if requesting a specific thread by ID
    const searchParams = request.nextUrl.searchParams;
    const threadId = searchParams.get("id");

    if (threadId) {
      // Fetch specific thread
      console.log("[Threads API] Fetching thread:", threadId);
      const response = await fetch(`${LANGGRAPH_URL}/threads/${threadId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        return new Response(
          JSON.stringify({ error: `Thread not found: ${threadId}` }),
          { status: 404, headers: { "Content-Type": "application/json" } }
        );
      }

      const data = await response.json();
      return new Response(JSON.stringify(data), {
        headers: { "Content-Type": "application/json" },
      });
    }

    // Otherwise fetch all threads with timeout
    console.log("[Threads API] Fetching all threads from:", LANGGRAPH_URL);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

    try {
      const response = await fetch(`${LANGGRAPH_URL}/threads/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ limit: 50, offset: 0 }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("[Threads API] LangGraph error:", response.status, errorText);
        return new Response(
          JSON.stringify({ error: `LangGraph error: ${response.status}`, threads: [] }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }

      const data = await response.json();
      console.log("[Threads API] Fetched threads:", data.length || 0);

      return new Response(JSON.stringify(data), {
        headers: { "Content-Type": "application/json" },
      });

    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        console.warn("[Threads API] Request timed out, returning empty");
        return new Response(
          JSON.stringify({ threads: [], error: "Request timed out" }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      throw fetchError;
    }

  } catch (error) {
    console.error("[Threads API] Error:", error);
    return new Response(
      JSON.stringify({ threads: [], error: "Failed to fetch threads", details: String(error) }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    console.log("[Threads API] Creating thread via:", LANGGRAPH_URL);

    // Create thread via LangGraph API
    const response = await fetch(`${LANGGRAPH_URL}/threads`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[Threads API] LangGraph error:", response.status, errorText);
      return new Response(
        JSON.stringify({ error: `LangGraph error: ${response.status}`, details: errorText }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    console.log("[Threads API] Created thread:", data);

    return new Response(JSON.stringify(data), {
      headers: { "Content-Type": "application/json" },
    });

  } catch (error) {
    console.error("[Threads API] Error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to create thread", details: String(error) }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const { thread_id, metadata } = body;

    if (!thread_id) {
      return new Response(
        JSON.stringify({ error: "thread_id is required" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    console.log("[Threads API] Updating thread metadata:", thread_id, metadata);

    // Update thread metadata via LangGraph API
    const response = await fetch(`${LANGGRAPH_URL}/threads/${thread_id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ metadata }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[Threads API] LangGraph error:", response.status, errorText);
      return new Response(
        JSON.stringify({ error: `LangGraph error: ${response.status}`, details: errorText }),
        { status: response.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await response.json();
    console.log("[Threads API] Updated thread:", data.thread_id);

    return new Response(JSON.stringify({ success: true, thread_id: data.thread_id, metadata: data.metadata }), {
      headers: { "Content-Type": "application/json" },
    });

  } catch (error) {
    console.error("[Threads API] Error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to update thread", details: String(error) }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
