"use client";

import { useState } from "react";
import { Avatar } from "@/components/ui/avatar";
import { User, Scale, ChevronDown, ChevronRight, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ToolCallInfo } from "./message-list";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  toolCalls?: ToolCallInfo[];
}

export function MessageBubble({ role, content, timestamp, toolCalls }: MessageBubbleProps) {
  const isUser = role === "user";
  const [expandedTools, setExpandedTools] = useState<Set<string>>(new Set());

  const toggleToolExpanded = (toolId: string) => {
    setExpandedTools(prev => {
      const next = new Set(prev);
      if (next.has(toolId)) {
        next.delete(toolId);
      } else {
        next.add(toolId);
      }
      return next;
    });
  };

  // Format tool args for display
  const formatToolArgs = (args: any): string => {
    if (!args) return "";
    try {
      const str = typeof args === "string" ? args : JSON.stringify(args, null, 2);
      return str.length > 500 ? str.slice(0, 500) + "..." : str;
    } catch {
      return String(args);
    }
  };

  const hasToolCalls = toolCalls && toolCalls.length > 0;

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <Avatar className={`h-8 w-8 shrink-0 flex items-center justify-center ${
        isUser ? "bg-[#c9a227]" : "bg-[#1e3a5f]"
      }`}>
        {isUser ? (
          <User className="h-4 w-4 text-[#1e3a5f]" />
        ) : (
          <Scale className="h-4 w-4 text-white" />
        )}
      </Avatar>

      <div className={`flex-1 ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        {/* Tool calls - rendered above the message content */}
        {hasToolCalls && (
          <div className="w-full max-w-[85%] mb-2 space-y-1">
            {toolCalls.map((tool) => (
              <div
                key={tool.id}
                className={`text-xs rounded-md border ${
                  tool.status === "running"
                    ? "border-[#c9a227]/40 bg-[#fef9e7]"
                    : "border-green-300/40 bg-green-50"
                }`}
              >
                {/* Tool header - clickable to expand */}
                <button
                  onClick={() => toggleToolExpanded(tool.id)}
                  className="w-full flex items-center gap-2 px-2 py-1.5 text-left hover:bg-black/5"
                >
                  {expandedTools.has(tool.id) ? (
                    <ChevronDown className="h-3 w-3 text-[#8b7355]" />
                  ) : (
                    <ChevronRight className="h-3 w-3 text-[#8b7355]" />
                  )}
                  {tool.status === "running" ? (
                    <Loader2 className="h-3 w-3 animate-spin text-[#c9a227]" />
                  ) : (
                    <span className="text-green-600">✓</span>
                  )}
                  <span className="font-mono text-[#5a4a3a]">{tool.name}</span>
                  {tool.status === "running" && (
                    <span className="text-[#8b7355] ml-auto">
                      {Math.round((Date.now() - tool.startTime) / 1000)}s
                    </span>
                  )}
                </button>

                {/* Expanded details */}
                {expandedTools.has(tool.id) && (
                  <div className="px-2 pb-2 border-t border-[#d4c5a9]/30">
                    {tool.args && (
                      <div className="mt-1">
                        <span className="text-[#8b7355]">Args:</span>
                        <pre className="mt-0.5 p-1.5 bg-[#f5f0e8] rounded text-[10px] overflow-x-auto whitespace-pre-wrap break-all">
                          {formatToolArgs(tool.args)}
                        </pre>
                      </div>
                    )}
                    {tool.result && (
                      <div className="mt-1">
                        <span className="text-[#8b7355]">Result:</span>
                        <pre className="mt-0.5 p-1.5 bg-[#f5f0e8] rounded text-[10px] overflow-x-auto max-h-32 whitespace-pre-wrap break-all">
                          {formatToolArgs(tool.result)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Message content */}
        <div className={`p-3 max-w-[85%] shadow-sm ${
          isUser
            ? "bg-[#c9a227] text-[#1e3a5f] rounded-[12px_12px_4px_12px]"
            : "bg-[#f5f3ed] border border-[#d4c5a9] text-[#2c3e50] rounded-[12px_12px_12px_4px]"
        }`}>
          {isUser ? (
            <p className="text-[13px] whitespace-pre-wrap leading-relaxed font-medium">{content}</p>
          ) : (
            <div className="text-[13px] leading-relaxed prose prose-sm max-w-none prose-p:my-1 prose-headings:my-2 prose-headings:font-serif prose-ul:my-1 prose-ol:my-1 prose-li:my-0 prose-code:bg-white/50 prose-code:px-1 prose-code:rounded prose-pre:bg-white/50 prose-pre:p-2 prose-strong:text-[#1e3a5f]">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content || "..."}
              </ReactMarkdown>
            </div>
          )}
        </div>
        {timestamp && (
          <span className="text-[11px] text-[#8b7355] mt-1.5 italic">
            {new Date(timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>
    </div>
  );
}
