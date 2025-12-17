import { NextRequest } from "next/server";

/**
 * CopilotKit API proxy to LangGraph backend
 * Forwards requests to the LangGraph server with proper headers
 */
export async function POST(request: NextRequest) {
  const langgraphUrl = process.env.COPILOTKIT_LANGGRAPH_URL || "http://roscoe:8000";
  const body = await request.text();

  try {
    const response = await fetch(`${langgraphUrl}/copilotkit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body,
    });

    const data = await response.text();

    return new Response(data, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") || "application/json",
      },
    });
  } catch (error) {
    console.error("CopilotKit proxy error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to connect to LangGraph backend" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function GET(request: NextRequest) {
  return new Response(
    JSON.stringify({ status: "ok", service: "copilotkit-proxy" }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
}
