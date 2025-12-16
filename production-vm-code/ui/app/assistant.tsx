"use client";

import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useLangGraphRuntime } from "@assistant-ui/react-langgraph";

import { createThread, getThreadState, sendMessage } from "@/lib/chatApi";
import { Thread } from "@/components/assistant-ui/thread";

export function Assistant() {
  const runtime = useLangGraphRuntime({
    stream: async function* (messages, { initialize, command }) {
      const { externalId } = await initialize();
      if (!externalId) throw new Error("Thread not found");

      const generator = await sendMessage({
        threadId: externalId,
        messages,
        command,
      });

      yield* generator;
    },
    create: async () => {
      const { thread_id } = await createThread();
      return { externalId: thread_id };
    },
    load: async (externalId) => {
      try {
        const state = await getThreadState(externalId);
        const interrupts =
          state.tasks?.flatMap((t) => t.interrupts ?? [])?.filter(Boolean) ?? [];
        return {
          messages: state.values.messages,
          // Restore LangGraph interrupts (human-in-the-loop) if present.
          // ThreadState does not expose a thread-level `interrupts`; interrupts are attached to tasks.
          interrupts: interrupts.length ? interrupts : undefined,
        };
      } catch {
        return { messages: [] };
      }
    },
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <Thread />
    </AssistantRuntimeProvider>
  );
}
