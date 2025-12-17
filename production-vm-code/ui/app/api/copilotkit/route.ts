import { NextRequest } from "next/server";

/**
 * CopilotKit API proxy to LangGraph backend
 * Forwards requests to the LangGraph server with proper headers
 */
export async function POST(request: NextRequest) {
  const langgraphUrl = process.env.COPILOTKIT_LANGGRAPH_URL || "http://roscoe:8000";
  const body = await request.text();

  try {
    // Forward Authorization and CopilotKit-specific headers
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      "Accept": "application/json",
    };

    // Forward Authorization header if present
    const authHeader = request.headers.get("Authorization");
    if (authHeader) {
      headers["Authorization"] = authHeader;
    }

    // Forward any x-copilotkit-* headers
    request.headers.forEach((value, key) => {
      if (key.toLowerCase().startsWith("x-copilotkit-")) {
        headers[key] = value;
      }
    });

    const response = await fetch(`${langgraphUrl}/copilotkit`, {
      method: "POST",
      headers,
      body,
    });

    // Stream the response body directly instead of buffering
    const responseHeaders = new Headers();
    responseHeaders.set("Content-Type", response.headers.get("Content-Type") || "application/json");

    // Preserve streaming-related headers
    const streamingHeaders = ["Transfer-Encoding", "Content-Encoding", "Cache-Control"];
    streamingHeaders.forEach(header => {
      const value = response.headers.get(header);
      if (value) {
        responseHeaders.set(header, value);
      }
    });

    return new Response(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error("CopilotKit proxy error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to connect to LangGraph backend" }),
      { status: 502, headers: { "Content-Type": "application/json" } }
    );
  }
}

export async function GET(_request: NextRequest) {
  return new Response(
    JSON.stringify({ status: "ok", service: "copilotkit-proxy" }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
}
