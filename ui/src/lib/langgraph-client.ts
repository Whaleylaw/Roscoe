export interface LangGraphMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ToolCallInfo {
  id: string;
  name: string;
  args: any;
  status: "pending" | "running" | "completed" | "error";
  result?: any;
  startTime?: number;
  endTime?: number;
}

export interface StreamChunk {
  type: "message" | "tool_call" | "tool_result" | "tool_start" | "tool_end" | "run_start" | "error";
  content?: string;
  tool_name?: string;
  tool_args?: any;
  tool_result?: any;
  tool_call_id?: string;
  run_id?: string;
}

export interface LangGraphThread {
  thread_id: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

/**
 * Fetch all threads from LangGraph API via Next.js API route
 */
export async function fetchThreads(): Promise<LangGraphThread[]> {
  try {
    // Use Next.js API route (server-side proxy to LangGraph)
    const response = await fetch("/api/threads", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.error("[LangGraph] Failed to fetch threads:", response.status);
      return [];
    }

    const data = await response.json();
    console.log("[LangGraph] Fetched threads:", data);

    // LangGraph returns threads in various formats, normalize it
    if (Array.isArray(data)) {
      return data;
    } else if (data.threads && Array.isArray(data.threads)) {
      return data.threads;
    }

    return [];
  } catch (error) {
    console.error("[LangGraph] Error fetching threads:", error);
    return [];
  }
}

/**
 * Create a new thread in LangGraph via Next.js API route
 */
export async function createThread(): Promise<string | null> {
  try {
    // Use Next.js API route (server-side proxy to LangGraph)
    const response = await fetch("/api/threads", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      console.error("[LangGraph] Failed to create thread:", response.status);
      return null;
    }

    const data = await response.json();
    console.log("[LangGraph] Created thread:", data);

    return data.thread_id || null;
  } catch (error) {
    console.error("[LangGraph] Error creating thread:", error);
    return null;
  }
}

// Helper to extract text content from various message formats
function extractTextContent(content: any): string {
  if (typeof content === "string") {
    return content;
  }
  if (Array.isArray(content)) {
    // Claude returns content as array of blocks: [{type: "text", text: "..."}, ...]
    return content
      .filter((block: any) => block.type === "text" && block.text)
      .map((block: any) => block.text)
      .join("");
  }
  if (content && typeof content === "object" && content.text) {
    return content.text;
  }
  return "";
}

export interface StreamResult {
  threadId: string | null;
  runId: string | null;
}

/**
 * Cancel a running agent
 */
export async function cancelRun(threadId: string, runId?: string): Promise<boolean> {
  try {
    const params = new URLSearchParams({ thread_id: threadId });
    if (runId) params.append("run_id", runId);

    const response = await fetch(`/api/chat?${params}`, {
      method: "DELETE",
    });

    const data = await response.json();
    console.log("[LangGraph] Cancel response:", data);
    return data.success === true;
  } catch (error) {
    console.error("[LangGraph] Cancel error:", error);
    return false;
  }
}

export async function* streamLangGraphResponse(
  messages: LangGraphMessage[],
  threadId?: string,
  onThreadCreated?: (threadId: string) => void,
  onRunStarted?: (runId: string) => void,
  signal?: AbortSignal,
  agentId?: string
): AsyncGenerator<StreamChunk> {
  // Use our API proxy to avoid CORS issues
  const endpoint = "/api/chat";

  console.log("[LangGraph] Streaming via proxy:", endpoint);
  console.log("[LangGraph] Thread ID:", threadId || "(new thread)");
  console.log("[LangGraph] Agent ID:", agentId || "roscoe_paralegal (default)");
  console.log("[LangGraph] Messages:", messages.length);

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ messages, thread_id: threadId, agent_id: agentId }),
    signal, // Allow aborting the fetch
  });

  // Get thread_id from response headers (for new threads)
  const responseThreadId = response.headers.get("X-Thread-Id");
  if (responseThreadId && onThreadCreated) {
    console.log("[LangGraph] Thread created/used:", responseThreadId);
    onThreadCreated(responseThreadId);
  }

  // Get run_id from response headers (LangGraph sets this)
  const responseRunId = response.headers.get("X-Run-Id");
  if (responseRunId && onRunStarted) {
    console.log("[LangGraph] Run ID from headers:", responseRunId);
    onRunStarted(responseRunId);
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: response.statusText }));
    console.error("[LangGraph] API error:", errorData);
    throw new Error(errorData.error || `API error: ${response.status}`);
  }

  if (!response.body) {
    throw new Error("No response body");
  }

  // Parse SSE stream
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let currentEventType = "";
  let lastYieldedContent = "";

  // Add timeout to prevent infinite hangs (2 minutes max)
  const STREAM_TIMEOUT_MS = 120000;
  const streamTimeout = setTimeout(() => {
    console.warn("[LangGraph] Stream timeout - force closing connection");
    reader.cancel().catch(() => {});
  }, STREAM_TIMEOUT_MS);

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        clearTimeout(streamTimeout);
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        // Track event type
        if (line.startsWith("event: ")) {
          currentEventType = line.slice(7).trim();
          continue;
        }

        if (line.startsWith("data: ")) {
          try {
            const jsonStr = line.slice(6).trim();
            if (!jsonStr || jsonStr === "[DONE]") continue;

            const data = JSON.parse(jsonStr);

            // Log all events for debugging (truncate long logs)
            const logStr = JSON.stringify(data).slice(0, 300);
            console.log(`[LangGraph] Event: ${currentEventType}`, logStr);

            // Handle metadata event - contains the LangGraph run_id
            if (currentEventType === "metadata" && data.run_id) {
              console.log("[LangGraph] Run ID from metadata:", data.run_id);
              if (onRunStarted) {
                onRunStarted(data.run_id);
              }
              yield { type: "run_start", run_id: data.run_id };
              continue;
            }

            // Handle "events" stream - contains detailed tool call info
            if (currentEventType === "events") {
              // Note: on_chain_start run_id is a LangChain internal trace ID, not the LangGraph run ID
              // The LangGraph run_id comes from the "metadata" event above

              // Tool start event
              if (data.event === "on_tool_start") {
                const toolName = data.name || data.data?.input?.name || "unknown";
                const toolArgs = data.data?.input || {};
                console.log("[LangGraph] Tool starting:", toolName, toolArgs);
                yield {
                  type: "tool_start",
                  tool_name: toolName,
                  tool_args: toolArgs,
                  tool_call_id: data.run_id,
                };
              }

              // Tool end event
              if (data.event === "on_tool_end") {
                const toolName = data.name || "unknown";
                const toolOutput = data.data?.output;
                console.log("[LangGraph] Tool ended:", toolName);
                yield {
                  type: "tool_end",
                  tool_name: toolName,
                  tool_result: toolOutput,
                  tool_call_id: data.run_id,
                };
              }

              continue;
            }

            // Check for tool results AND AI messages in "updates" stream
            if (currentEventType === "updates") {
              // LangGraph update format can be:
              // 1. { messages: [...] }
              // 2. { state: { messages: [...] } }
              // 3. { [nodeName]: { messages: [...] } } - e.g., { tools: { messages: [...] } }

              let messages: any[] = [];

              // Direct messages array
              if (data.messages && Array.isArray(data.messages)) {
                messages = data.messages;
              }
              // State with messages
              else if (data.state?.messages && Array.isArray(data.state.messages)) {
                messages = data.state.messages;
              }
              // Node-based updates (e.g., data.tools.messages, data.agent.messages)
              else {
                // Check all keys in data for objects with messages arrays
                for (const key in data) {
                  if (data[key]?.messages && Array.isArray(data[key].messages)) {
                    messages = data[key].messages;
                    break; // Take first match
                  }
                }
              }

              for (const msg of messages) {
                // Tool result format: { role: "tool", name: "write_file", content: "..." }
                if ((msg.role === "tool" || msg.type === "tool") && msg.name && msg.content) {
                  console.log("[LangGraph] Tool result found:", msg.name, msg.content);

                  // Keep content as-is (it's usually a string like "Updated file /path/to/file.html")
                  yield {
                    type: "tool_result",
                    tool_name: msg.name,
                    tool_result: msg.content,
                    tool_call_id: msg.tool_call_id,
                  };
                }

                // AI message in updates stream (final message after tool calls)
                // This is critical - the final AI response comes through updates, not messages/
                if (msg.type === "ai" && msg.content) {
                  const text = extractTextContent(msg.content);
                  if (text && text !== lastYieldedContent) {
                    console.log("[LangGraph] AI message in updates:", text.slice(0, 100) + (text.length > 100 ? "..." : ""));
                    lastYieldedContent = text;
                    yield { type: "message", content: text };
                  }

                  // Also check for tool_calls in AI messages
                  if (msg.tool_calls && Array.isArray(msg.tool_calls)) {
                    for (const tc of msg.tool_calls) {
                      console.log("[LangGraph] Tool call in updates:", tc.name);
                      yield {
                        type: "tool_call",
                        tool_name: tc.name,
                        tool_args: tc.args,
                        tool_call_id: tc.id,
                      };
                    }
                  }
                }
              }
              // Skip the rest of updates processing (avoid duplicate messages)
              continue;
            }

            // Handle messages/partial and messages/metadata events explicitly
            if (currentEventType.startsWith("messages/")) {
              // Format: array of message objects
              if (Array.isArray(data) && data.length > 0) {
                for (const item of data) {
                  // Check for AI message with content
                  if (item.content) {
                    const text = extractTextContent(item.content);
                    if (text) {
                      // Always yield new content from messages/ events
                      if (text.length > lastYieldedContent.length || text !== lastYieldedContent) {
                        lastYieldedContent = text;
                        console.log("[LangGraph] Message content:", text.slice(0, 100) + (text.length > 100 ? "..." : ""));
                        yield { type: "message", content: text };
                      }
                    }

                    // Check for tool_calls
                    if (item.tool_calls && Array.isArray(item.tool_calls)) {
                      for (const tc of item.tool_calls) {
                        console.log("[LangGraph] Tool call:", tc.name);
                        yield {
                          type: "tool_call",
                          tool_name: tc.name,
                          tool_args: tc.args,
                          tool_call_id: tc.id,
                        };
                      }
                    }
                    break; // Only process first message
                  }
                }
              }
              continue; // Skip generic processing for messages/ events
            }

            // Handle different LangGraph response formats
            let textToYield = "";

            // Format 1: Array with message objects (from "messages" stream)
            if (Array.isArray(data) && data.length > 0) {
              for (const item of data) {
                if ((item.type === "ai" || item.type === "AIMessageChunk") && item.content) {
                  textToYield = extractTextContent(item.content);

                  // Also check for tool_calls in AI messages
                  if (item.tool_calls && Array.isArray(item.tool_calls)) {
                    for (const tc of item.tool_calls) {
                      console.log("[LangGraph] Tool call from AI message:", tc.name);
                      yield {
                        type: "tool_call",
                        tool_name: tc.name,
                        tool_args: tc.args,
                        tool_call_id: tc.id,
                      };
                    }
                  }
                  break; // Only take first AI message
                }
              }
            }

            // Format 2: Direct message object
            else if (data.type === "ai" && data.content) {
              textToYield = extractTextContent(data.content);

              // Check for tool_calls
              if (data.tool_calls && Array.isArray(data.tool_calls)) {
                for (const tc of data.tool_calls) {
                  console.log("[LangGraph] Tool call from AI message:", tc.name);
                  yield {
                    type: "tool_call",
                    tool_name: tc.name,
                    tool_args: tc.args,
                    tool_call_id: tc.id,
                  };
                }
              }
            }

            // Yield if we have new content that's longer (accumulating) or completely new
            if (textToYield) {
              // Only yield if it's new content (longer or different)
              const isLonger = textToYield.length > lastYieldedContent.length;
              const isPrefix = textToYield.startsWith(lastYieldedContent) || lastYieldedContent.startsWith(textToYield);

              if (isLonger || (!isPrefix && textToYield !== lastYieldedContent)) {
                lastYieldedContent = textToYield;
                yield { type: "message", content: textToYield };
              }
            }

            // Handle tool calls (legacy format)
            if (data.tool_name || (data.name && !data.event)) {
              yield {
                type: "tool_call",
                tool_name: data.tool_name || data.name,
                tool_args: data.tool_args || data.args,
              };
            }

            // Also check for tool results in messages array (messages event)
            if (Array.isArray(data)) {
              for (const item of data) {
                // Tool result format: { role: "tool", name: "write_file", content: "..." }
                if ((item.role === "tool" || item.type === "tool") && item.name && item.content) {
                  console.log("[LangGraph] Tool result in messages:", item.name, item.content);
                  yield {
                    type: "tool_result",
                    tool_name: item.name,
                    tool_result: item.content,
                    tool_call_id: item.tool_call_id,
                  };
                }
              }
            }

          } catch (e) {
            // Ignore JSON parse errors for incomplete chunks
            if (!(e instanceof SyntaxError)) {
              console.error("[LangGraph] Error parsing SSE:", e);
            }
          }
        }
      }
    }
  } catch (e) {
    clearTimeout(streamTimeout);
    // Check if this was an abort
    if (signal?.aborted) {
      console.log("[LangGraph] Stream aborted by user");
      yield { type: "error", content: "Request cancelled" };
      return;
    }
    throw e;
  } finally {
    clearTimeout(streamTimeout);
    reader.releaseLock();
  }
}
