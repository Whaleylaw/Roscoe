"use client";

import { useState, useEffect, useCallback, useRef } from "react";

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

  // Load from localStorage on mount
  useEffect(() => {
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
  useEffect(() => {
    if (!isInitialized || !activeThreadId || isSwitchingRef.current) return;
    if (currentMessages.length === 0) return;
    
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
  }, [currentMessages, activeThreadId, isInitialized]);

  // Save to localStorage whenever threads change
  useEffect(() => {
    if (!isInitialized || threads.length === 0) return;
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      threads,
      activeThreadId,
    }));
  }, [threads, activeThreadId, isInitialized]);

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
    setThreads(prev => [...prev, newThread]);
    
    // Switch to new thread
    isSwitchingRef.current = true;
    setActiveThreadId(newThread.id);
    setMessages(newThread.messages);
    setTimeout(() => { isSwitchingRef.current = false; }, 100);
  }, [setMessages]);

  const switchThread = useCallback((id: string) => {
    const thread = threads.find(t => t.id === id);
    if (thread && id !== activeThreadId) {
      isSwitchingRef.current = true;
      setActiveThreadId(id);
      setMessages(thread.messages);
      setTimeout(() => { isSwitchingRef.current = false; }, 100);
    }
  }, [threads, activeThreadId, setMessages]);

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

  return {
    threads,
    activeThreadId,
    createThread,
    switchThread,
    deleteThread,
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
