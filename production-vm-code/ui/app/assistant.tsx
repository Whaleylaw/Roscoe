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

      // Consume with logging to debug
      let count = 0;
      try {
        for await (const chunk of generator) {
          count++;
          console.log(`[Stream ${count}]`, chunk.event);
          yield chunk;
        }
        console.log(`[Stream Done] ${count} chunks`);
      } catch (error) {
        console.error("[Stream Error]", error);
        throw error;
      }
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
