import { NextRequest, NextResponse } from "next/server";

/**
 * API route to start a background run that continues even after client disconnects.
 * 
 * Use this for long-running tasks like case file organization that should
 * continue running even if you switch to another thread.
 */

const LANGGRAPH_URL = process.env.ROSCOE_LANGGRAPH_URL || "http://localhost:8123";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { threadId, message, assistantId } = body;

    if (!message) {
      return NextResponse.json(
        { error: "message is required" },
        { status: 400 }
      );
    }

    // Create thread if not provided
    let actualThreadId = threadId;
    if (!actualThreadId) {
      const threadResponse = await fetch(`${LANGGRAPH_URL}/threads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (!threadResponse.ok) {
        return NextResponse.json(
          { error: "Failed to create thread" },
          { status: 500 }
        );
      }
      const thread = await threadResponse.json();
      actualThreadId = thread.thread_id;
    }

    // Start the run in background mode (don't wait for completion)
    // Using the runs endpoint with stream=false starts it in background
    const runResponse = await fetch(
      `${LANGGRAPH_URL}/threads/${actualThreadId}/runs`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          assistant_id: assistantId || "roscoe_paralegal",
          input: {
            messages: [
              {
                role: "user",
                content: message,
              },
            ],
          },
          // Don't stream - this makes it a background run
          stream_mode: [],
          // These settings ensure it continues running
          multitask_strategy: "enqueue",
        }),
      }
    );

    if (!runResponse.ok) {
      const error = await runResponse.text();
      console.error("Failed to start background run:", error);
      return NextResponse.json(
        { error: "Failed to start background run", details: error },
        { status: runResponse.status }
      );
    }

    const run = await runResponse.json();

    return NextResponse.json({
      success: true,
      thread_id: actualThreadId,
      run_id: run.run_id,
      message: "Background task started. It will continue running even if you switch threads.",
    });
  } catch (error) {
    console.error("Error starting background run:", error);
    return NextResponse.json(
      { error: "Failed to start background run" },
      { status: 500 }
    );
  }
}

