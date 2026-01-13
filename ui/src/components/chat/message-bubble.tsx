"use client";

import { useState } from "react";
import { Avatar } from "@/components/ui/avatar";
import { User, Scale, ChevronDown, ChevronRight, Loader2, FileText, Image as ImageIcon } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ToolCallInfo, FileAttachment } from "./message-list";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  toolCalls?: ToolCallInfo[];
  attachments?: FileAttachment[];
  messageType?: "text" | "tool_group";
}

export function MessageBubble({ role, content, timestamp, toolCalls, attachments, messageType }: MessageBubbleProps) {
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

  // For tool_group type, render only tool calls without avatar and message bubble
  if (messageType === "tool_group") {
    return (
      <div className="flex gap-3">
        {/* Spacer to align with message bubbles */}
        <div className="w-8 shrink-0" />
        <div className="flex-1">
          <div className="w-full max-w-[85%] space-y-1">
            {toolCalls?.map((tool) => (
              <div
                key={tool.id}
                className={`text-xs rounded-md border ${
                  tool.status === "running"
                    ? "border-[#c9a227]/40 bg-[#fef9e7]"
                    : "border-green-300/40 bg-green-50"
                }`}
              >
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
        </div>
      </div>
    );
  }

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
        {/* Tool calls - rendered above the message content (for non-tool_group messages) */}
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

        {/* File attachments - shown above message for user, inline for assistant */}
        {attachments && attachments.length > 0 && (
          <div className="max-w-[85%] mb-2 space-y-2">
            {attachments.map((file, index) => {
              const isImage = file.type.startsWith("image/");
              return (
                <div
                  key={index}
                  className={`rounded-lg border overflow-hidden ${
                    isUser ? "bg-white/10 border-[#c9a227]/30" : "bg-white border-[#d4c5a9]"
                  }`}
                >
                  {isImage ? (
                    <div className="p-2">
                      <img
                        src={`data:${file.type};base64,${file.data}`}
                        alt={file.name}
                        className="max-w-full max-h-[300px] rounded"
                      />
                      <div className="flex items-center gap-2 mt-2 text-xs text-[#8b7355]">
                        <ImageIcon className="h-3 w-3" />
                        <span>{file.name}</span>
                        <span>({(file.size / 1024).toFixed(1)}KB)</span>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 p-2 text-xs">
                      <FileText className="h-4 w-4 text-[#8b7355]" />
                      <span className="font-medium text-[#2c3e50]">{file.name}</span>
                      <span className="text-[#8b7355]">({(file.size / 1024).toFixed(1)}KB)</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Message content */}
        <div className={`max-w-[85%] shadow-sm ${
          isUser
            ? "px-6 py-3 min-w-[60px] bg-[#c9a227] text-[#1e3a5f] rounded-[14px_14px_4px_14px]"
            : "px-4 py-3 bg-[#f5f3ed] border border-[#d4c5a9] text-[#2c3e50] rounded-[14px_14px_14px_4px]"
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
