"use client";

import { useState, useCallback, useRef } from "react";
import { MessageList, ChatMessage, ToolCallInfo } from "./message-list";
import { MessageInput } from "./message-input";
import { streamLangGraphResponse, cancelRun } from "@/lib/langgraph-client";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { Loader2, Square } from "lucide-react";

export function ChatPanel() {
  const { messages, setMessages, langGraphThreadId, setLangGraphThreadId, setOpenDocument } = useWorkbenchStore();
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [currentRunId, setCurrentRunId] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Callback when a new thread is created by the backend
  const handleThreadCreated = useCallback((threadId: string) => {
    console.log("[ChatPanel] LangGraph thread created:", threadId);
    setLangGraphThreadId(threadId);
  }, [setLangGraphThreadId]);

  // Callback when a run starts
  const handleRunStarted = useCallback((runId: string) => {
    console.log("[ChatPanel] Run started:", runId);
    setCurrentRunId(runId);
  }, []);

  // Cancel the current run
  const handleCancel = useCallback(async () => {
    console.log("[ChatPanel] Cancel requested");

    // Abort the fetch request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Also send cancel request to backend
    if (langGraphThreadId) {
      await cancelRun(langGraphThreadId, currentRunId || undefined);
    }

    setIsLoading(false);
    setCurrentRunId(null);
  }, [langGraphThreadId, currentRunId]);

  const handleSendMessage = async (content: string, attachments?: Array<{name: string; size: number; type: string; data: string}>) => {
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date().toISOString(),
      attachments,
    };

    // Add user message immediately
    const withUserMessage = [...messages, userMessage];
    setMessages(withUserMessage);
    setIsLoading(true);
    setStreamingContent("");
    setCurrentRunId(null);

    // Create AbortController for this request
    abortControllerRef.current = new AbortController();

    // Create placeholder for assistant message with empty toolCalls array
    const assistantId = `assistant-${Date.now()}`;
    const withAssistant = [...withUserMessage, {
      id: assistantId,
      role: "assistant" as const,
      content: "",
      timestamp: new Date().toISOString(),
      toolCalls: [] as ToolCallInfo[],
    }];
    setMessages(withAssistant);

    try {
      // Build message history for LangGraph with attachments
      const messageHistory = messages
        .filter(m => m.id !== "welcome") // Don't send welcome message to agent
        .map(m => ({
          role: m.role,
          content: m.content,
          attachments: m.attachments
        }));

      // Add current message with attachments
      messageHistory.push({ role: "user", content, attachments });

      let fullContent = "";

      // Stream from LangGraph with thread tracking
      // Pass existing thread ID if available, get new thread ID via callback
      console.log("[ChatPanel] Starting stream with thread:", langGraphThreadId || "(new)");
      for await (const chunk of streamLangGraphResponse(
        messageHistory,
        langGraphThreadId || undefined,
        handleThreadCreated,
        handleRunStarted,
        abortControllerRef.current.signal
      )) {
        // Handle run_start event
        if (chunk.type === "run_start" && chunk.run_id) {
          setCurrentRunId(chunk.run_id);
        }

        // Handle message content
        if (chunk.type === "message" && chunk.content) {
          // Replace content, don't append (LangGraph sends full content each time)
          // Check if new content is longer (accumulating) or completely different
          if (chunk.content.length > fullContent.length && chunk.content.startsWith(fullContent)) {
            // Incremental streaming - take the new longer content
            fullContent = chunk.content;
          } else if (!fullContent.includes(chunk.content)) {
            // Completely new content - replace
            fullContent = chunk.content;
          }
          // If chunk.content is a subset of fullContent, ignore it (duplicate)

          setStreamingContent(fullContent);

          // Update the assistant message in place
          setMessages((prev) => prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: fullContent }
              : m
          ));
        }

        // Handle tool_start (from events stream)
        else if (chunk.type === "tool_start") {
          const toolId = chunk.tool_call_id || `tool-${Date.now()}`;
          console.log("[Tool Start]", chunk.tool_name, chunk.tool_args);
          // Add tool call to the assistant message's toolCalls array
          setMessages((prev) => prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  toolCalls: [...(m.toolCalls || []), {
                    id: toolId,
                    name: chunk.tool_name || "unknown",
                    args: chunk.tool_args,
                    status: "running" as const,
                    startTime: Date.now(),
                  }],
                }
              : m
          ));
        }

        // Handle tool_end (from events stream)
        else if (chunk.type === "tool_end") {
          const toolId = chunk.tool_call_id;
          console.log("[Tool End]", chunk.tool_name, chunk.tool_result);
          // Update the tool call status in the message
          setMessages((prev) => prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  toolCalls: (m.toolCalls || []).map(t =>
                    t.id === toolId || (toolId === undefined && t.name === chunk.tool_name && t.status === "running")
                      ? { ...t, status: "completed" as const, result: chunk.tool_result }
                      : t
                  ),
                }
              : m
          ));
        }

        // Handle tool_call (from messages stream - fallback)
        else if (chunk.type === "tool_call") {
          const toolId = chunk.tool_call_id || `tool-${Date.now()}`;
          console.log("[Tool Call]", chunk.tool_name, chunk.tool_args);
          // Add tool call to message if not already tracked
          setMessages((prev) => prev.map((m) => {
            if (m.id !== assistantId) return m;
            const toolCalls = m.toolCalls || [];
            const exists = toolCalls.some(t => t.id === toolId || (t.name === chunk.tool_name && t.status === "running"));
            if (exists) return m;
            return {
              ...m,
              toolCalls: [...toolCalls, {
                id: toolId,
                name: chunk.tool_name || "unknown",
                args: chunk.tool_args,
                status: "running" as const,
                startTime: Date.now(),
              }],
            };
          }));
        }

        // Handle tool_result (from updates stream)
        else if (chunk.type === "tool_result") {
          console.log("[Tool Result]", chunk.tool_name, "Type:", typeof chunk.tool_result);
          console.log("[Tool Result] Full result:", chunk.tool_result);

          // Update tool call status in the message
          setMessages((prev) => prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  toolCalls: (m.toolCalls || []).map(t =>
                    (t.id === chunk.tool_call_id) || (t.name === chunk.tool_name && t.status === "running")
                      ? { ...t, status: "completed" as const, result: chunk.tool_result }
                      : t
                  ),
                }
              : m
          ));

          // Check if this is a file write that created an HTML artifact
          const result = chunk.tool_result;
          const isHTMLWrite = chunk.tool_name === "write_file" &&
            typeof result === "string" &&
            result.includes(".html");

          if (isHTMLWrite) {
            console.log("[Tool Result] HTML artifact detected, dispatching event");
            window.dispatchEvent(
              new CustomEvent("langgraph:tool_result", {
                detail: {
                  tool_name: chunk.tool_name,
                  tool_result: result,
                },
              })
            );
          }

          // Check if this is a display_document request (from any tool)
          // Tools like generate_directory_browser internally call display_document()
          // and include the JSON marker in their return value
          console.log("[Tool Result] Checking for __display_document__, result type:", typeof result);
          if (typeof result === "string") {
            console.log("[Tool Result] Result is string, length:", result.length);
            console.log("[Tool Result] First 500 chars:", result.substring(0, 500));
            try {
              // Try to find JSON with __display_document__ marker anywhere in the result
              // Look for the pattern starting with { and containing "__display_document__": true
              // Extract the entire JSON object (may span multiple lines)
              const jsonMatch = result.match(/\{[\s\S]*?"__display_document__"[\s\S]*?\}/);
              console.log("[Tool Result] JSON match found:", jsonMatch ? "YES" : "NO");
              if (jsonMatch) {
                console.log("[Tool Result] Matched JSON:", jsonMatch[0]);
                const parsed = JSON.parse(jsonMatch[0]);
                console.log("[Tool Result] Parsed JSON:", parsed);
                if (parsed.__display_document__) {
                  console.log("[Tool Result] ✅ Display document requested:", parsed);
                  // Map tool's type to OpenDocument type
                  const typeMap: Record<string, "pdf" | "docx" | "md" | "html"> = {
                    pdf: "pdf",
                    docx: "docx",
                    md: "md",
                    html: "html",
                    image: "pdf", // Images can be displayed in PDF viewer or we need to add image type
                    txt: "md", // Text files render as markdown
                  };
                  const docType = typeMap[parsed.type] || "md";
                  console.log("[Tool Result] Opening document:", parsed.path, "Type:", docType);
                  setOpenDocument({
                    path: parsed.path,
                    type: docType,
                  });
                }
              } else {
                console.log("[Tool Result] No __display_document__ marker found in result");
              }
            } catch (e) {
              // Not JSON or parse error, log and ignore
              console.error("[Tool Result] Failed to parse display_document JSON:", e);
            }
          } else {
            console.log("[Tool Result] Result is not a string, it's:", typeof result);
          }
        }

        // Handle errors
        else if (chunk.type === "error") {
          console.log("[Error]", chunk.content);
          // User cancelled - update message to show cancelled
          if (chunk.content === "Request cancelled") {
            setMessages((prev) => prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: fullContent + "\n\n*[Cancelled by user]*" }
                : m
            ));
          }
        }
      }

      // Final update with complete content
      if (fullContent) {
        setMessages((prev) => prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: fullContent, timestamp: new Date().toISOString() }
            : m
        ));
      }
      
    } catch (error) {
      console.error("Error streaming:", error);
      setMessages((prev) => prev.map((m) =>
        m.id === assistantId
          ? { ...m, content: "Sorry, I encountered an error. Please check your connection and try again." }
          : m
      ));
    } finally {
      setIsLoading(false);
      setStreamingContent("");
      setCurrentRunId(null);
      abortControllerRef.current = null;
    }
  };

  return (
    <div className="flex h-full flex-col bg-[#f8f7f4]">
      {/* Messages - tool calls now render inline within messages */}
      <MessageList messages={messages} isStreaming={isLoading} />

      {/* Input */}
      <div className="border-t border-[#d4c5a9] bg-white px-4 py-3">
        {/* Status bar with cancel button */}
        {isLoading && (
          <div className="flex items-center justify-between text-xs text-[#8b7355] mb-2">
            <div className="flex items-center gap-2">
              <Loader2 className="h-3 w-3 animate-spin" />
              <span>Working...</span>
            </div>
            <button
              onClick={handleCancel}
              className="flex items-center gap-1 px-2 py-1 rounded hover:bg-red-100 text-red-600 transition-colors"
              title="Cancel request"
            >
              <Square className="h-3 w-3 fill-current" />
              <span>Cancel</span>
            </button>
          </div>
        )}
        <MessageInput onSend={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}
