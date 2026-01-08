import { useEffect } from "react";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { Thread } from "@/types";
import { fetchThreads } from "@/lib/langgraph-client";

export function useThreads() {
  const { threads, activeThreadId, setThreads, setActiveThread, addThread, updateThread } =
    useWorkbenchStore();

  // Load threads from LangGraph API on mount
  useEffect(() => {
    const loadThreads = async () => {
      try {
        // Fetch threads from LangGraph API
        const apiThreads = await fetchThreads();

        if (apiThreads && apiThreads.length > 0) {
          // Convert LangGraph threads to UI Thread format
          const uiThreads: Thread[] = apiThreads.map((t) => ({
            id: t.thread_id,
            title: t.metadata?.title || `Thread ${t.thread_id.slice(0, 8)}`,
            status: "active",
            created: t.created_at,
            updated: t.updated_at,
            messageCount: t.metadata?.message_count || 0,
          }));

          console.log("[Threads] Loaded from LangGraph API:", uiThreads.length);
          setThreads(uiThreads);

          // Also save to localStorage as backup
          localStorage.setItem("roscoe-threads", JSON.stringify(uiThreads));
        } else {
          // Fallback to localStorage if API fails
          console.log("[Threads] API returned no threads, trying localStorage");
          const savedThreads = localStorage.getItem("roscoe-threads");
          if (savedThreads) {
            const parsed = JSON.parse(savedThreads);
            setThreads(parsed);
          }
        }
      } catch (error) {
        console.error("[Threads] Error loading from API, using localStorage:", error);
        // Fallback to localStorage
        const savedThreads = localStorage.getItem("roscoe-threads");
        if (savedThreads) {
          try {
            const parsed = JSON.parse(savedThreads);
            setThreads(parsed);
          } catch (e) {
            console.error("Error loading threads from localStorage:", e);
          }
        }
      }
    };

    loadThreads();
  }, [setThreads]);

  // Save threads to localStorage whenever they change
  useEffect(() => {
    if (threads.length > 0) {
      localStorage.setItem("roscoe-threads", JSON.stringify(threads));
    }
  }, [threads]);

  const createNewThread = async () => {
    try {
      // Try to create thread via LangGraph API
      const { createThread } = await import("@/lib/langgraph-client");
      const threadId = await createThread();

      if (threadId) {
        const newThread: Thread = {
          id: threadId,
          title: "New Conversation",
          status: "active",
          created: new Date().toISOString(),
          updated: new Date().toISOString(),
          messageCount: 0,
        };

        addThread(newThread);
        setActiveThread(newThread.id);
        return newThread;
      }
    } catch (error) {
      console.error("[Threads] Error creating thread via API:", error);
    }

    // Fallback to local ID if API fails
    const newThread: Thread = {
      id: `thread-${Date.now()}`,
      title: "New Conversation",
      status: "active",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      messageCount: 0,
    };

    addThread(newThread);
    setActiveThread(newThread.id);
    return newThread;
  };

  const deleteThread = (id: string) => {
    const updatedThreads = threads.filter((t) => t.id !== id);
    setThreads(updatedThreads);

    if (activeThreadId === id) {
      setActiveThread(updatedThreads[0]?.id || null);
    }
  };

  return {
    threads,
    activeThreadId,
    setActiveThread,
    createNewThread,
    updateThread,
    deleteThread,
  };
}
