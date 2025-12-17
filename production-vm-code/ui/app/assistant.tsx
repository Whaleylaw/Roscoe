"use client";

import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useCustomLangGraphRuntime } from "@/lib/useCustomLangGraphRuntime";
import { Thread } from "@/components/assistant-ui/thread";

export function Assistant() {
  const apiUrl = typeof window !== 'undefined'
    ? new URL("/api", window.location.href).href
    : "/api";

  const runtime = useCustomLangGraphRuntime({
    apiUrl,
    assistantId: process.env.NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID || "roscoe_paralegal",
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <Thread />
    </AssistantRuntimeProvider>
  );
}
