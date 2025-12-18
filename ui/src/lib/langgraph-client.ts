export interface LangGraphMessage {
  role: "user" | "assistant";
  content: string;
}

export interface StreamChunk {
  type: "message" | "tool_call" | "tool_result" | "error";
  content?: string;
  tool_name?: string;
  tool_args?: any;
  tool_result?: any;
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

export async function* streamLangGraphResponse(
  messages: LangGraphMessage[],
  threadId?: string
): AsyncGenerator<StreamChunk> {
  // Use our API proxy to avoid CORS issues
  const endpoint = "/api/chat";
  
  console.log("[LangGraph] Streaming via proxy:", endpoint);
  console.log("[LangGraph] Messages:", messages);

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ messages }),
  });

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

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

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
            
            // Log all events for debugging
            console.log(`[LangGraph] Event: ${currentEventType}`, JSON.stringify(data).slice(0, 500));
            
            // Check for tool results in "updates" stream (tool outputs)
            if (currentEventType === "updates") {
              // Look for tool messages in various formats
              const messages = data.messages || data.state?.messages || [];
              
              for (const msg of messages) {
                // Tool result format: { role: "tool", name: "write_file", content: "..." }
                if ((msg.role === "tool" || msg.type === "tool") && msg.name && msg.content) {
                  console.log("[LangGraph] Tool result found:", msg.name, msg.content);
                  
                  // Keep content as-is (it's usually a string like "Updated file /path/to/file.html")
                  yield {
                    type: "tool_result",
                    tool_name: msg.name,
                    tool_result: msg.content,
                  };
                }
              }
              // Skip the rest of updates processing (avoid duplicate messages)
              continue;
            }

            // Handle different LangGraph response formats
            let textToYield = "";
            
            // Format 1: Array with message objects (from "messages" stream)
            if (Array.isArray(data) && data.length > 0) {
              for (const item of data) {
                if ((item.type === "ai" || item.type === "AIMessageChunk") && item.content) {
                  textToYield = extractTextContent(item.content);
                  break; // Only take first AI message
                }
              }
            }
            
            // Format 2: Direct message object
            else if (data.type === "ai" && data.content) {
              textToYield = extractTextContent(data.content);
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

            // Handle tool calls
            if (data.tool_name || data.name) {
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
  } finally {
    reader.releaseLock();
  }
}
