"use client";

import { useLocalRuntime } from "@assistant-ui/react";
import { useCallback, useState } from "react";

type LangGraphConfig = {
  apiUrl: string;
  assistantId: string;
};

export function useCustomLangGraphRuntime(config: LangGraphConfig) {
  const [threadId, setThreadId] = useState<string | null>(null);

  const createThread = useCallback(async () => {
    const response = await fetch(`${config.apiUrl}/threads`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const data = await response.json();
    setThreadId(data.thread_id);
    return data.thread_id;
  }, [config.apiUrl]);

  const chatAdapter = useCallback(
    async ({ messages, abortSignal }: { messages: readonly any[]; abortSignal: AbortSignal }) => {
      console.log("[Custom Runtime] run() called with", messages.length, "messages");

      // Create thread if needed
      let tid = threadId;
      if (!tid) {
        tid = await createThread();
      }

      // Convert messages to LangChain format
      const lcMessages = messages.map((m) => ({
        role: m.role,
        content: m.content
          .filter((c: any) => c.type === "text")
          .map((c: any) => c.text)
          .join(""),
      }));

      // Start SSE stream
      const response = await fetch(
        `${config.apiUrl}/threads/${tid}/runs/stream`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            assistant_id: config.assistantId,
            input: { messages: lcMessages },
            stream_mode: ["values"],
            if_not_exists: "create",
          }),
          signal: abortSignal || AbortSignal.timeout(290000),
        }
      );

      if (!response.ok) {
        throw new Error(`Stream failed: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      // Parse SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let lastState: any = null;
      let streamComplete = false;

      try {
        while (!streamComplete) {
          const { done, value } = await reader.read();
          if (done) {
            console.log("[Custom Runtime] Stream ended");
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
                console.log("[Custom Runtime] Received [DONE]");
                streamComplete = true;
                break;
              }

              try {
                const event = JSON.parse(data);

                // Process values events (complete state snapshots)
                if (event.event === "values") {
                  lastState = event.data;
                  console.log(
                    "[Custom Runtime] Got state with",
                    lastState?.messages?.length,
                    "messages"
                  );
                }

                // Ignore metadata
                if (event.event.includes("metadata")) {
                  console.log("[Custom Runtime] Ignoring metadata");
                }
              } catch (e) {
                console.error("[Custom Runtime] Parse error:", e);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      // Stream ended, return final state
      if (lastState?.messages) {
        const lastMessage = lastState.messages[lastState.messages.length - 1];
        const converted = convertMessage(lastMessage);
        console.log("[Custom Runtime] Returning:", converted);
        return converted;
      }

      // Fallback
      return {
        role: "assistant" as const,
        content: [{ type: "text" as const, text: "No response" }],
      };
    },
    [threadId, createThread, config.apiUrl, config.assistantId]
  );

  const runtime = useLocalRuntime({ run: chatAdapter });

  return runtime;
}

function convertMessage(msg: any) {
  const content: any[] = [];

  // Convert string content to text blocks
  if (typeof msg.content === "string") {
    if (msg.content) {
      content.push({ type: "text", text: msg.content });
    }
  } else if (Array.isArray(msg.content)) {
    content.push(...msg.content);
  }

  // Handle tool calls
  if (msg.tool_calls && Array.isArray(msg.tool_calls)) {
    for (const tc of msg.tool_calls) {
      content.push({
        type: "tool-call",
        toolCallId: tc.id,
        toolName: tc.function?.name || tc.name,
        args: typeof tc.function?.arguments === "string"
          ? JSON.parse(tc.function.arguments)
          : tc.function?.arguments || tc.args || {},
        result: undefined, // Will be filled by tool result message
      });
    }
  }

  // Handle tool results (separate tool message type)
  if (msg.role === "tool" && msg.tool_call_id) {
    content.push({
      type: "tool-result",
      toolCallId: msg.tool_call_id,
      toolName: msg.name,
      result: msg.content,
    });
  }

  return {
    id: msg.id || crypto.randomUUID(),
    role: msg.role as "user" | "assistant" | "system",
    content,
  };
}
