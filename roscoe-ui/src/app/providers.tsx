"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { useSearchParams, useRouter } from "next/navigation";
import { Suspense, createContext, useContext, useState, useCallback, useEffect, useRef } from "react";

// Context for thread management - exposes thread state to components outside CopilotKit's internal context
interface ThreadContextType {
  threadId: string | undefined;
  setThreadId: (id: string | undefined) => void;
}

const ThreadContext = createContext<ThreadContextType>({
  threadId: undefined,
  setThreadId: () => {},
});

export function useThreadContext() {
  return useContext(ThreadContext);
}

function CopilotProviderInner({ children }: { children: React.ReactNode }) {
  const searchParams = useSearchParams();
  const router = useRouter();
  
  // Get initial threadId from URL
  const initialThreadId = searchParams.get("thread") || undefined;
  
  // Manage threadId as state
  const [threadId, setThreadIdState] = useState<string | undefined>(initialThreadId);
  
  // Track programmatic URL updates to prevent re-entrancy
  const isProgrammaticUpdate = useRef(false);
  
  // Get the current URL thread param as a string (not the whole searchParams object)
  const urlThreadId = searchParams.get("thread") || undefined;
  
  // Sync state from URL changes (e.g., browser back/forward, manual URL edit)
  // Only runs when urlThreadId actually changes AND it wasn't a programmatic update
  useEffect(() => {
    // Skip if this was triggered by our own programmatic update
    if (isProgrammaticUpdate.current) {
      isProgrammaticUpdate.current = false;
      return;
    }
    
    // Only update state if URL actually differs from current state
    if (urlThreadId !== threadId) {
      console.log("[ThreadContext] URL changed externally, syncing state:", urlThreadId);
      setThreadIdState(urlThreadId);
    }
  }, [urlThreadId]); // Only depend on the string value, not the object
  
  // Function to change thread - updates state AND URL
  const setThreadId = useCallback((newThreadId: string | undefined) => {
    console.log("[ThreadContext] Setting thread to:", newThreadId);
    
    // Update state first
    setThreadIdState(newThreadId);
    
    // Mark that we're about to programmatically update the URL
    // This prevents the useEffect above from triggering a redundant state update
    isProgrammaticUpdate.current = true;
    
    // Update URL without page reload (for bookmarking)
    if (newThreadId) {
      router.push(`/?thread=${newThreadId}`, { scroll: false });
    } else {
      router.push("/", { scroll: false });
    }
  }, [router]);

  return (
    <ThreadContext.Provider value={{ threadId, setThreadId }}>
      <CopilotKit 
        runtimeUrl="/api/chat" 
        agent="roscoe_paralegal"
        threadId={threadId}
        // NOTE: Removed key={threadId} - this was causing CopilotKit to remount
        // and lose streaming state when switching threads. CopilotKit handles
        // thread switching internally via the threadId prop.
      >
        {children}
      </CopilotKit>
    </ThreadContext.Provider>
  );
}

export function CopilotProvider({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<div className="h-screen bg-zinc-950" />}>
      <CopilotProviderInner>{children}</CopilotProviderInner>
    </Suspense>
  );
}
