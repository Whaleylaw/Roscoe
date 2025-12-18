"use client";

import { useState } from "react";
import { MessageList, ChatMessage } from "./message-list";
import { MessageInput } from "./message-input";
import { streamLangGraphResponse } from "@/lib/langgraph-client";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { Loader2 } from "lucide-react";

export function ChatPanel() {
  const { messages, setMessages } = useWorkbenchStore();
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");

  const handleSendMessage = async (content: string) => {
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };

    // Add user message immediately
    const withUserMessage = [...messages, userMessage];
    setMessages(withUserMessage);
    setIsLoading(true);
    setStreamingContent("");

    // Create placeholder for assistant message
    const assistantId = `assistant-${Date.now()}`;
    const withAssistant = [...withUserMessage, {
      id: assistantId,
      role: "assistant" as const,
      content: "",
      timestamp: new Date().toISOString(),
    }];
    setMessages(withAssistant);

    try {
      // Build message history for LangGraph
      const messageHistory = messages
        .filter(m => m.id !== "welcome") // Don't send welcome message to agent
        .map(m => ({ role: m.role, content: m.content }));
      
      // Add current message
      messageHistory.push({ role: "user", content });

      let fullContent = "";
      
      // Stream from LangGraph
      // Note: LangGraph sends full accumulated content each chunk, not deltas
      for await (const chunk of streamLangGraphResponse(messageHistory)) {
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
        } else if (chunk.type === "tool_call") {
          // Could show tool execution status here
          console.log("[Tool Call]", chunk.tool_name, chunk.tool_args);
        } else if (chunk.type === "tool_result") {
          // Dispatch event for artifact listener
          console.log("[Tool Result]", chunk.tool_name, chunk.tool_result);
          
          // Check if this is a file write that created an HTML artifact
          // Result format: "Updated file /Reports/file.html" (string)
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
    }
  };

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header - Navy gradient with gold accent */}
      <div className="bg-navy-gradient border-b-[3px] border-[#c9a227] px-5 py-4">
        <h2 className="font-semibold text-white text-base">Roscoe AI Paralegal</h2>
        <p className="text-[#c9a227] text-xs italic mt-0.5">Legal Assistant</p>
        {isLoading && (
          <div className="flex items-center gap-2 text-sm text-white/70 mt-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Thinking...</span>
          </div>
        )}
      </div>
      
      {/* Messages */}
      <MessageList messages={messages} isStreaming={isLoading} />
      
      {/* Input */}
      <MessageInput onSend={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
