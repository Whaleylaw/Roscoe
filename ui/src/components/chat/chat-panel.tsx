"use client";

import { useState, useCallback, useRef } from "react";
import { MessageList, ChatMessage, ToolCallInfo } from "./message-list";
import { MessageInput } from "./message-input";
import { streamLangGraphResponse, cancelRun } from "@/lib/langgraph-client";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { Loader2, Square, ChevronDown } from "lucide-react";

// Available agents
const AGENTS = [
  { id: "roscoe_paralegal", name: "Paralegal", description: "Legal research, case management, documents" },
  { id: "roscoe_second_brain", name: "Second Brain", description: "Tasks, notes, reminders, memory" },
];

export function ChatPanel() {
  const { messages, setMessages, langGraphThreadId, setLangGraphThreadId, setOpenDocument, selectedAgent, setSelectedAgent } = useWorkbenchStore();
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [currentRunId, setCurrentRunId] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Trace-like rendering: turn tracking state
  const [currentTurnId, setCurrentTurnId] = useState<string | null>(null);
  const [activeMessageId, setActiveMessageId] = useState<string | null>(null);
  const [toolGroupId, setToolGroupId] = useState<string | null>(null);

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

    // Create turn ID for trace-like rendering
    const turnId = `turn-${Date.now()}`;
    setCurrentTurnId(turnId);
    setToolGroupId(null); // Reset tool group

    // Local tracking variables (state updates don't work in async loops due to closures)
    let currentActiveMessageId: string;
    let currentToolGroupId: string | null = null;

    // Create placeholder for assistant message with empty toolCalls array
    const assistantId = `assistant-${Date.now()}`;
    currentActiveMessageId = assistantId;
    setActiveMessageId(assistantId);
    const withAssistant = [...withUserMessage, {
      id: assistantId,
      role: "assistant" as const,
      content: "",
      timestamp: new Date().toISOString(),
      toolCalls: [] as ToolCallInfo[],
      // Trace-like rendering fields
      turnId,
      messageType: "text" as const,
      isComplete: false,
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
      console.log("[ChatPanel] Starting stream with thread:", langGraphThreadId || "(new)", "agent:", selectedAgent);
      for await (const chunk of streamLangGraphResponse(
        messageHistory,
        langGraphThreadId || undefined,
        handleThreadCreated,
        handleRunStarted,
        abortControllerRef.current.signal,
        selectedAgent
      )) {
        // Handle run_start event
        if (chunk.type === "run_start" && chunk.run_id) {
          setCurrentRunId(chunk.run_id);
        }

        // Handle message content
        if (chunk.type === "message" && chunk.content) {
          const newContent = chunk.content;

          // If there's an active tool group, mark it as complete before adding text
          if (currentToolGroupId) {
            setMessages((prev) => prev.map((m) =>
              m.id === currentToolGroupId ? { ...m, isComplete: true } : m
            ));
            currentToolGroupId = null;
            setToolGroupId(null);
          }

          // Detect if this is a NEW message segment (trace-like behavior)
          const isNewSegment =
            fullContent.length > 0 &&
            !newContent.startsWith(fullContent) &&
            !fullContent.startsWith(newContent);

          if (isNewSegment) {
            // Create a new message bubble for this segment
            const newMessageId = `assistant-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
            console.log("[ChatPanel] New message segment detected, creating:", newMessageId);

            setMessages((prev) => {
              // Mark previous message as complete
              const updated = prev.map((m) =>
                m.id === currentActiveMessageId ? { ...m, isComplete: true } : m
              );
              // Add new message
              return [...updated, {
                id: newMessageId,
                role: "assistant" as const,
                content: newContent,
                timestamp: new Date().toISOString(),
                toolCalls: [],
                turnId,
                messageType: "text" as const,
                isComplete: false,
              }];
            });

            currentActiveMessageId = newMessageId;
            setActiveMessageId(newMessageId);
            fullContent = newContent;
          } else if (newContent.length > fullContent.length && newContent.startsWith(fullContent)) {
            // Accumulating - update in place
            fullContent = newContent;
            setMessages((prev) => prev.map((m) =>
              m.id === currentActiveMessageId
                ? { ...m, content: fullContent }
                : m
            ));
          } else if (newContent.length > fullContent.length) {
            // Content is longer but doesn't start with fullContent - still update
            fullContent = newContent;
            setMessages((prev) => prev.map((m) =>
              m.id === currentActiveMessageId
                ? { ...m, content: fullContent }
                : m
            ));
          }
          // If chunk.content is a subset of fullContent, ignore it (duplicate)

          setStreamingContent(fullContent);
        }

        // Handle tool_start (from events stream)
        else if (chunk.type === "tool_start") {
          const toolId = chunk.tool_call_id || `tool-${Date.now()}`;
          console.log("[Tool Start]", chunk.tool_name, chunk.tool_args);

          // Mark current text message as complete before tool calls
          if (currentActiveMessageId && fullContent.length > 0) {
            setMessages((prev) => prev.map((m) =>
              m.id === currentActiveMessageId ? { ...m, isComplete: true } : m
            ));
          }

          // Create or update tool group message
          if (!currentToolGroupId) {
            // Create new tool group message
            const newToolGroupId = `tool-group-${Date.now()}`;
            currentToolGroupId = newToolGroupId;
            setToolGroupId(newToolGroupId);

            setMessages((prev) => [...prev, {
              id: newToolGroupId,
              role: "assistant" as const,
              content: "",
              timestamp: new Date().toISOString(),
              toolCalls: [{
                id: toolId,
                name: chunk.tool_name || "unknown",
                args: chunk.tool_args,
                status: "running" as const,
                startTime: Date.now(),
              }],
              turnId,
              messageType: "tool_group" as const,
              isComplete: false,
            }]);
          } else {
            // Add to existing tool group
            setMessages((prev) => prev.map((m) =>
              m.id === currentToolGroupId
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
        }

        // Handle tool_end (from events stream)
        else if (chunk.type === "tool_end") {
          const toolId = chunk.tool_call_id;
          console.log("[Tool End]", chunk.tool_name, chunk.tool_result);
          // Update the tool call status in the tool group (or any message that has it)
          setMessages((prev) => prev.map((m) => {
            // Look for the tool in this message's toolCalls
            const hasThisTool = (m.toolCalls || []).some(t =>
              t.id === toolId || (toolId === undefined && t.name === chunk.tool_name && t.status === "running")
            );
            if (!hasThisTool) return m;
            return {
              ...m,
              toolCalls: (m.toolCalls || []).map(t =>
                t.id === toolId || (toolId === undefined && t.name === chunk.tool_name && t.status === "running")
                  ? { ...t, status: "completed" as const, result: chunk.tool_result }
                  : t
              ),
            };
          }));
        }

        // Handle tool_call (from messages stream - fallback)
        else if (chunk.type === "tool_call") {
          const toolId = chunk.tool_call_id || `tool-${Date.now()}`;
          console.log("[Tool Call]", chunk.tool_name, chunk.tool_args);

          // Create or update tool group if needed
          if (!currentToolGroupId) {
            const newToolGroupId = `tool-group-${Date.now()}`;
            currentToolGroupId = newToolGroupId;
            setToolGroupId(newToolGroupId);

            setMessages((prev) => [...prev, {
              id: newToolGroupId,
              role: "assistant" as const,
              content: "",
              timestamp: new Date().toISOString(),
              toolCalls: [{
                id: toolId,
                name: chunk.tool_name || "unknown",
                args: chunk.tool_args,
                status: "running" as const,
                startTime: Date.now(),
              }],
              turnId,
              messageType: "tool_group" as const,
              isComplete: false,
            }]);
          } else {
            // Add to existing tool group if not already tracked
            setMessages((prev) => prev.map((m) => {
              if (m.id !== currentToolGroupId) return m;
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
        }

        // Handle tool_result (from updates stream)
        else if (chunk.type === "tool_result") {
          console.log("[Tool Result]", chunk.tool_name, "Type:", typeof chunk.tool_result);
          console.log("[Tool Result] Full result:", chunk.tool_result);

          // Update tool call status in the tool group (or any message that has it)
          setMessages((prev) => prev.map((m) => {
            const hasThisTool = (m.toolCalls || []).some(t =>
              (t.id === chunk.tool_call_id) || (t.name === chunk.tool_name && t.status === "running")
            );
            if (!hasThisTool) return m;
            return {
              ...m,
              toolCalls: (m.toolCalls || []).map(t =>
                (t.id === chunk.tool_call_id) || (t.name === chunk.tool_name && t.status === "running")
                  ? { ...t, status: "completed" as const, result: chunk.tool_result }
                  : t
              ),
            };
          }));

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
          // User cancelled - update the active message to show cancelled
          if (chunk.content === "Request cancelled") {
            setMessages((prev) => prev.map((m) =>
              m.id === currentActiveMessageId
                ? { ...m, content: fullContent + "\n\n*[Cancelled by user]*", isComplete: true }
                : m
            ));
          }
        }
      }

      // Final update with complete content
      if (fullContent) {
        setMessages((prev) => prev.map((m) =>
          m.id === currentActiveMessageId
            ? { ...m, content: fullContent, timestamp: new Date().toISOString() }
            : m
        ));
      }

    } catch (error) {
      console.error("Error streaming:", error);
      setMessages((prev) => prev.map((m) =>
        m.id === currentActiveMessageId
          ? { ...m, content: "Sorry, I encountered an error. Please check your connection and try again.", isComplete: true }
          : m
      ));
    } finally {
      setIsLoading(false);
      setStreamingContent("");
      setCurrentRunId(null);
      abortControllerRef.current = null;

      // Mark all messages in this turn as complete (hides tool groups)
      if (currentTurnId) {
        setMessages((prev) => prev.map((m) =>
          m.turnId === currentTurnId
            ? { ...m, isComplete: true }
            : m
        ));
      }
      setCurrentTurnId(null);
      setActiveMessageId(null);
      setToolGroupId(null);
    }
  };

  // Get current agent info
  const currentAgent = AGENTS.find(a => a.id === selectedAgent) || AGENTS[0];

  // Handle agent change - also reset thread for new agent context
  const handleAgentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newAgent = e.target.value;
    setSelectedAgent(newAgent);
    // Reset thread when switching agents so they start fresh
    setLangGraphThreadId(null);
    setMessages([]);
  };

  return (
    <div className="flex h-full flex-col bg-[#f8f7f4]">
      {/* Agent selector header */}
      <div className="shrink-0 border-b border-[#d4c5a9] bg-white px-4 py-2">
        <div className="flex items-center gap-2">
          <label className="text-xs text-[#8b7355] font-medium">Agent:</label>
          <div className="relative">
            <select
              value={selectedAgent}
              onChange={handleAgentChange}
              disabled={isLoading}
              className="appearance-none bg-[#f8f7f4] border border-[#d4c5a9] rounded px-3 py-1.5 pr-8 text-sm text-[#3d3929] cursor-pointer hover:bg-[#f0ede4] focus:outline-none focus:ring-2 focus:ring-[#8b7355] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {AGENTS.map(agent => (
                <option key={agent.id} value={agent.id}>
                  {agent.name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-[#8b7355] pointer-events-none" />
          </div>
          <span className="text-xs text-[#a89a7c] ml-2">{currentAgent.description}</span>
        </div>
      </div>

      {/* Messages - tool calls now render inline within messages */}
      <MessageList messages={messages} isStreaming={isLoading} />

      {/* Input */}
      <div className="shrink-0 border-t border-[#d4c5a9] bg-white px-4 py-3">
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
