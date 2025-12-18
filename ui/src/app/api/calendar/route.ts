import { NextRequest, NextResponse } from "next/server";

const LANGGRAPH_URL = process.env.NEXT_PUBLIC_LANGGRAPH_URL || "http://localhost:8123";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const startDate = searchParams.get("start");
    const endDate = searchParams.get("end");

    // Forward to LangGraph agent's calendar tool
    const response = await fetch(
      `${LANGGRAPH_URL}/tools/list_events?start=${startDate}&end=${endDate}`
    );

    if (!response.ok) {
      throw new Error("Failed to fetch calendar events");
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Calendar API error:", error);
    return NextResponse.json(
      { error: "Failed to load calendar events" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Forward to LangGraph agent's create_event tool
    const response = await fetch(`${LANGGRAPH_URL}/tools/create_event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error("Failed to create calendar event");
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Calendar create error:", error);
    return NextResponse.json(
      { error: "Failed to create calendar event" },
      { status: 500 }
    );
  }
}
