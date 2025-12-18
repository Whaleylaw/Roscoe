import { NextRequest } from "next/server";

const LANGGRAPH_URL = process.env.NEXT_PUBLIC_LANGGRAPH_URL || "http://localhost:2024";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { messages } = body;

    console.log("[Chat API] Forwarding to LangGraph:", LANGGRAPH_URL);
    console.log("[Chat API] Messages:", messages);

    // Forward to LangGraph
    const response = await fetch(`${LANGGRAPH_URL}/runs/stream`, {
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
        stream_mode: ["messages", "updates"],
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

    // Stream the response back
    const headers = new Headers({
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
    });

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
