"use client";

/**
 * Custom LangGraph SSE stream consumer
 *
 * This bypasses @assistant-ui/react-langgraph which has issues handling
 * certain LangGraph event types (messages/metadata, values events).
 *
 * We consume the SSE stream directly and update state manually.
 */

export async function* streamLangGraphMessages(config: {
  apiUrl: string;
  assistantId: string;
  threadId: string;
  messages: any[];
}) {
  const response = await fetch(
    `${config.apiUrl}/threads/${config.threadId}/runs/stream`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        assistant_id: config.assistantId,
        input: { messages: config.messages },
        stream_mode: ["values"], // Use only values mode for complete snapshots
        if_not_exists: "create",
      }),
      signal: AbortSignal.timeout(290000), // 290s timeout
    }
  );

  if (!response.ok) {
    throw new Error(`Stream failed: ${response.status} ${response.statusText}`);
  }

  if (!response.body) {
    throw new Error("No response body");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let lastMessageCount = 0;

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log("[Custom SSE] Stream ended");
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.trim() || line.startsWith(":")) continue;

        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") {
            console.log("[Custom SSE] Received [DONE]");
            return;
          }

          try {
            const event = JSON.parse(data);
            console.log("[Custom SSE] Event:", event.event);

            // Only process "values" events (complete state snapshots)
            if (event.event === "values") {
              const stateMessages = event.data?.messages || [];

              // Only yield if we have new messages
              if (stateMessages.length > lastMessageCount) {
                lastMessageCount = stateMessages.length;
                const lastMessage = stateMessages[stateMessages.length - 1];

                if (lastMessage) {
                  console.log("[Custom SSE] Yielding message:", lastMessage.role);
                  yield lastMessage;
                }
              }
            }

            // Ignore metadata events that cause freezing
            if (event.event === "messages/metadata" || event.event === "metadata") {
              console.log("[Custom SSE] Ignoring metadata event");
            }
          } catch (e) {
            console.error("[Custom SSE] Parse error:", e);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
    console.log("[Custom SSE] Stream fully consumed");
  }
}
