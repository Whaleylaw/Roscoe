"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useWorkbenchStore } from "@/stores/workbench-store";

export interface SimpleThread {
  id: string;
  title: string;
  messageCount: number;
  status: "active" | "complete" | "error";
  created: string;
  updated: string;
  messages: Array<{id: string; role: string; content: string; timestamp: string}>;
}

const STORAGE_KEY = "roscoe-threads-v2";

export function useSimpleThreads(
  currentMessages: any[],
  setMessages: (msgs: any[]) => void
) {
  const [threads, setThreads] = useState<SimpleThread[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Use ref to track if we're in the middle of a switch
  const isSwitchingRef = useRef(false);

  // Get the store setter for langGraphThreadId
  const setLangGraphThreadId = useWorkbenchStore((state) => state.setLangGraphThreadId);

  // Load from API and localStorage on mount
  useEffect(() => {
    const loadThreads = async () => {
      try {
        // Try fetching from API first
        const response = await fetch("/api/threads");
        if (response.ok) {
          const apiThreads = await response.json();

          if (Array.isArray(apiThreads) && apiThreads.length > 0) {
            // Helper to extract text from message content
            const extractContent = (content: any): string => {
              if (typeof content === "string") return content;
              if (Array.isArray(content)) {
                // Claude format: [{type: "text", text: "..."}, ...]
                return content
                  .filter((block: any) => block.type === "text" && block.text)
                  .map((block: any) => block.text)
                  .join("");
              }
              if (content && typeof content === "object" && content.text) {
                return content.text;
              }
              return String(content || "");
            };

            // Convert API threads to SimpleThread format
            const simpleThreads: SimpleThread[] = apiThreads.map((t: any) => {
              // Normalize messages to have string content
              const allMessages = (t.values?.messages || []).map((msg: any) => ({
                id: msg.id || `msg-${Date.now()}`,
                role: msg.type === "human" ? "user" : msg.type === "ai" ? "assistant" : msg.role || "assistant",
                content: extractContent(msg.content),
                timestamp: msg.created_at || new Date().toISOString(),
              }));

              // Only keep last 20 messages to prevent UI freeze
              // User can load more by scrolling up (future feature)
              const recentMessages = allMessages.slice(-20);

              return {
                id: t.thread_id,
                title: t.metadata?.title || `Thread ${t.thread_id.slice(0, 8)}`,
                messageCount: allMessages.length, // Show total count
                status: t.status === "error" ? "error" : "complete",
                created: t.created_at,
                updated: t.updated_at,
                messages: recentMessages, // Only last 20 messages loaded
              };
            });

            console.log("[Threads] Loaded from API:", simpleThreads.length);

            // Sort threads by updated_at descending (newest first)
            simpleThreads.sort((a, b) => new Date(b.updated).getTime() - new Date(a.updated).getTime());

            // Clear old localStorage to prevent conflicts
            localStorage.removeItem(STORAGE_KEY);

            setThreads(simpleThreads);
            // Don't auto-select first thread - let user choose
            setActiveThreadId(null);

            // Don't auto-load messages - only load when user clicks a thread
            // This prevents overwhelming the UI with 350+ message threads
            console.log("[Threads] Using API data (messages load on click)");

            setIsInitialized(true);
            return;
          }
        }
      } catch (error) {
        console.error("[Threads] API fetch failed, using localStorage:", error);
      }

      // Fallback to localStorage
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          if (parsed.threads && parsed.activeThreadId) {
            setThreads(parsed.threads);
            setActiveThreadId(parsed.activeThreadId);

            // Load the active thread's messages
            const activeThread = parsed.threads.find((t: SimpleThread) => t.id === parsed.activeThreadId);
            if (activeThread) {
              setMessages(activeThread.messages);
            }
          }
        } catch (e) {
          console.error("Error loading threads:", e);
          createInitialThread();
        }
      } else {
        createInitialThread();
      }
      setIsInitialized(true);
    };

    loadThreads();
  }, []);

  // Helper to create initial thread
  const createInitialThread = useCallback(() => {
    const defaultThread: SimpleThread = {
      id: `thread-${Date.now()}`,
      title: "New Conversation",
      messageCount: 1,
      status: "active",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      messages: [{
        id: "welcome",
        role: "assistant",
        content: "How can I assist you with your legal work today?",
        timestamp: new Date().toISOString(),
      }],
    };
    setThreads([defaultThread]);
    setActiveThreadId(defaultThread.id);
    setMessages(defaultThread.messages);
  }, [setMessages]);

  // Save current messages to active thread (but not during switch)
  // Debounced to prevent infinite update loops during streaming
  useEffect(() => {
    if (!isInitialized || !activeThreadId || isSwitchingRef.current) return;
    if (currentMessages.length === 0) return;

    // Debounce thread updates to avoid rapid re-renders during streaming
    const timeoutId = setTimeout(() => {
      setThreads(prev => prev.map(t =>
        t.id === activeThreadId
          ? {
              ...t,
              messages: currentMessages,
              messageCount: currentMessages.length,
              updated: new Date().toISOString(),
              // Update title based on first user message
              title: getThreadTitle(currentMessages, t.title),
              // Update status based on last message
              status: getThreadStatus(currentMessages),
            }
          : t
      ));
    }, 300); // 300ms debounce

    return () => clearTimeout(timeoutId);
  }, [currentMessages, activeThreadId, isInitialized]);

  // Save to localStorage whenever threads change
  // DISABLED: Causes QuotaExceededError with 50+ threads from API
  // Threads are fetched fresh from API on each page load instead
  // useEffect(() => {
  //   // Auto-save disabled - API is source of truth
  // }, [threads, activeThreadId, isInitialized]);

  const createThread = useCallback(() => {
    const newThread: SimpleThread = {
      id: `thread-${Date.now()}`,
      title: "New Conversation",
      messageCount: 1,
      status: "active",
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      messages: [{
        id: "welcome",
        role: "assistant",
        content: "How can I assist you with your legal work today?",
        timestamp: new Date().toISOString(),
      }],
    };
    setThreads(prev => [newThread, ...prev]); // Add to front (newest first)

    // Switch to new thread
    isSwitchingRef.current = true;
    setActiveThreadId(newThread.id);
    setMessages(newThread.messages);

    // Clear the langGraphThreadId since this is a new local thread
    // A LangGraph thread will be created on first message
    setLangGraphThreadId(null);
    console.log("[Threads] Created new local thread:", newThread.id);

    setTimeout(() => { isSwitchingRef.current = false; }, 100);
  }, [setMessages, setLangGraphThreadId]);

  const switchThread = useCallback((id: string) => {
    const thread = threads.find(t => t.id === id);
    if (thread && id !== activeThreadId) {
      isSwitchingRef.current = true;
      setActiveThreadId(id);
      setMessages(thread.messages);

      // Update the store's langGraphThreadId if this is a LangGraph thread (UUID format)
      // Local threads start with "thread-", LangGraph threads are UUIDs
      if (id && !id.startsWith("thread-")) {
        console.log("[Threads] Switching to LangGraph thread:", id);
        setLangGraphThreadId(id);
      } else {
        console.log("[Threads] Switching to local thread (no LangGraph ID yet)");
        setLangGraphThreadId(null);
      }

      setTimeout(() => { isSwitchingRef.current = false; }, 100);
    }
  }, [threads, activeThreadId, setMessages, setLangGraphThreadId]);

  const deleteThread = useCallback((id: string) => {
    const remaining = threads.filter(t => t.id !== id);
    
    if (remaining.length === 0) {
      // If deleting last thread, create a new one
      createThread();
      setThreads(prev => prev.filter(t => t.id !== id));
    } else {
      setThreads(remaining);
      if (activeThreadId === id) {
        // Switch to another thread
        switchThread(remaining[0].id);
      }
    }
  }, [threads, activeThreadId, createThread, switchThread]);

  // Update a thread's LangGraph ID (when backend creates the real thread)
  const updateThreadLangGraphId = useCallback((localId: string, langGraphId: string) => {
    console.log("[Threads] Updating thread LangGraph ID:", localId, "->", langGraphId);
    setThreads(prev => prev.map(t =>
      t.id === localId ? { ...t, id: langGraphId } : t
    ));
    if (activeThreadId === localId) {
      setActiveThreadId(langGraphId);
    }
  }, [activeThreadId]);

  // Get the LangGraph thread ID for the active thread (if it's a real LangGraph thread)
  const getLangGraphThreadId = useCallback((): string | undefined => {
    if (!activeThreadId) return undefined;
    // Local threads start with "thread-" prefix, LangGraph threads are UUIDs
    if (activeThreadId.startsWith("thread-")) {
      return undefined; // Not yet synced to LangGraph
    }
    return activeThreadId;
  }, [activeThreadId]);

  return {
    threads,
    activeThreadId,
    createThread,
    switchThread,
    deleteThread,
    updateThreadLangGraphId,
    getLangGraphThreadId,
  };
}

// Helper to generate thread title from messages
function getThreadTitle(messages: any[], currentTitle: string): string {
  if (currentTitle !== "New Conversation") return currentTitle;
  
  const firstUserMessage = messages.find(m => m.role === "user");
  if (firstUserMessage) {
    // Truncate to 30 chars
    const content = firstUserMessage.content;
    return content.length > 30 ? content.slice(0, 30) + "..." : content;
  }
  return currentTitle;
}

// Helper to determine thread status from messages
function getThreadStatus(messages: any[]): "active" | "complete" | "error" {
  if (messages.length === 0) return "active";
  
  const lastMessage = messages[messages.length - 1];
  
  // Check for error messages
  if (lastMessage.content?.toLowerCase().includes("error") || 
      lastMessage.content?.toLowerCase().includes("sorry, i encountered")) {
    return "error";
  }
  
  // If last message is from assistant, consider it complete for now
  if (lastMessage.role === "assistant" && messages.length > 1) {
    return "complete";
  }
  
  return "active";
}
