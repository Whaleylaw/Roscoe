"use client";

import { Avatar } from "@/components/ui/avatar";
import { User, Scale } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export function MessageBubble({ role, content, timestamp }: MessageBubbleProps) {
  const isUser = role === "user";

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
        <div className={`p-3 max-w-[85%] shadow-sm ${
          isUser 
            ? "bg-[#1e3a5f] text-white rounded-[12px_12px_4px_12px]" 
            : "bg-[#f5f3ed] border border-[#d4c5a9] text-[#2c3e50] rounded-[12px_12px_12px_4px]"
        }`}>
          {isUser ? (
            <p className="text-[13px] whitespace-pre-wrap leading-relaxed">{content}</p>
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
