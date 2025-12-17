import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const maxDuration = 300; // 5 minutes max for long-running streams
export const dynamic = "force-dynamic"; // Disable caching

function getCorsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "*",
  };
}

async function handleRequest(req: NextRequest, method: string) {
  try {
    const path = req.nextUrl.pathname.replace(/^\/?api\//, "");
    const url = new URL(req.url);
    const searchParams = new URLSearchParams(url.search);
    searchParams.delete("_path");
    searchParams.delete("nxtP_path");
    const queryString = searchParams.toString()
      ? `?${searchParams.toString()}`
      : "";

    const options: RequestInit = {
      method,
      headers: {
        "x-api-key": process.env["LANGCHAIN_API_KEY"] || "",
        // Ensure we accept streaming responses
        "Accept": "text/event-stream, application/json",
      },
      // Disable keepalive to prevent connection hanging with SSE streams
      keepalive: false,
      // Add signal for abort controller (prevents infinite hangs)
      signal: AbortSignal.timeout(290000), // 290s (just under maxDuration)
    };

    if (["POST", "PUT", "PATCH"].includes(method)) {
      options.body = await req.text();
    }

    const res = await fetch(
      `${process.env["LANGGRAPH_API_URL"]}/${path}${queryString}`,
      options,
    );

    // Add streaming-friendly headers
    const responseHeaders = new Headers(res.headers);
    Object.entries(getCorsHeaders()).forEach(([key, value]) => {
      responseHeaders.set(key, value);
    });

    // Ensure proper streaming headers
    if (res.headers.get('content-type')?.includes('text/event-stream')) {
      responseHeaders.set('Content-Type', 'text/event-stream');
      responseHeaders.set('Cache-Control', 'no-cache');
      responseHeaders.set('Connection', 'keep-alive');
      responseHeaders.set('X-Accel-Buffering', 'no'); // Disable nginx buffering
    }

    return new NextResponse(res.body, {
      status: res.status,
      statusText: res.statusText,
      headers: responseHeaders,
    });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (e: any) {
    console.error('[API Proxy Error]', e);
    return NextResponse.json({ error: e.message }, { status: e.status ?? 500 });
  }
}

export const GET = (req: NextRequest) => handleRequest(req, "GET");
export const POST = (req: NextRequest) => handleRequest(req, "POST");
export const PUT = (req: NextRequest) => handleRequest(req, "PUT");
export const PATCH = (req: NextRequest) => handleRequest(req, "PATCH");
export const DELETE = (req: NextRequest) => handleRequest(req, "DELETE");

// Add a new OPTIONS handler
export const OPTIONS = () => {
  return new NextResponse(null, {
    status: 204,
    headers: {
      ...getCorsHeaders(),
    },
  });
};
