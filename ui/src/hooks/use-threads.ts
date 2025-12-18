import { useEffect } from "react";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { Thread } from "@/types";

export function useThreads() {
  const { threads, activeThreadId, setThreads, setActiveThread, addThread, updateThread } =
    useWorkbenchStore();

  // Load threads from localStorage on mount
  useEffect(() => {
    const savedThreads = localStorage.getItem("roscoe-threads");
    if (savedThreads) {
      try {
        const parsed = JSON.parse(savedThreads);
        setThreads(parsed);
      } catch (error) {
        console.error("Error loading threads:", error);
      }
    }
  }, [setThreads]);

  // Save threads to localStorage whenever they change
  useEffect(() => {
    if (threads.length > 0) {
      localStorage.setItem("roscoe-threads", JSON.stringify(threads));
    }
  }, [threads]);

  const createNewThread = () => {
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
