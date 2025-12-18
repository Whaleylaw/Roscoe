"use client";

import { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "./message-bubble";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming?: boolean;
}

export function MessageList({ messages, isStreaming }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages or during streaming
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: isStreaming ? "auto" : "smooth" });
  }, [messages, isStreaming]);

  // Filter out empty assistant messages (unless streaming)
  const displayMessages = messages.filter(m => {
    if (m.role === "assistant" && !m.content) {
      // Only show empty assistant message if it's the last one and we're streaming
      const isLast = m === messages[messages.length - 1];
      return isLast && isStreaming;
    }
    return true;
  });

  return (
    <ScrollArea className="flex-1 p-4 bg-white" ref={scrollAreaRef}>
      <div className="space-y-4">
        {displayMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-40 text-center">
            <div className="w-12 h-12 mb-3 rounded-full bg-[#f5f3ed] border border-[#d4c5a9] flex items-center justify-center">
              <span className="text-xl">⚖️</span>
            </div>
            <p className="text-[#8b7355] text-sm">Start a conversation with Roscoe</p>
          </div>
        ) : (
          displayMessages.map((message) => (
            <MessageBubble
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
            />
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
