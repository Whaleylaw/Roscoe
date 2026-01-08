"use client";

import { MessageSquare, Plus, Trash2, Circle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useSimpleThreads, SimpleThread } from "@/hooks/use-simple-threads";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { cn } from "@/lib/utils";

export function ThreadManager() {
  const { messages, setMessages } = useWorkbenchStore();
  const { threads, activeThreadId, createThread, switchThread, deleteThread } = useSimpleThreads(messages, setMessages);

  // Deselect thread (go back to thread list view)
  const deselectThread = () => {
    switchThread(""); // Switch to empty ID (no thread selected)
    setMessages([]); // Clear chat
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {activeThreadId && (
              <Button size="sm" variant="ghost" onClick={deselectThread} title="Back to thread list">
                <ArrowLeft className="h-4 w-4" />
              </Button>
            )}
            <MessageSquare className="h-4 w-4" />
            <span className="text-sm font-medium">Conversations</span>
          </div>
          <Button size="sm" variant="ghost" onClick={createThread}>
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Thread list */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {threads.length === 0 ? (
            <p className="text-sm text-muted-foreground p-2">No conversations yet</p>
          ) : (
            threads.map((thread) => (
              <ThreadItem
                key={thread.id}
                thread={thread}
                isActive={thread.id === activeThreadId}
                onSelect={() => switchThread(thread.id)}
                onDelete={() => deleteThread(thread.id)}
              />
            ))
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t p-2">
        <p className="text-xs text-muted-foreground">
          {threads.length} conversation{threads.length !== 1 ? "s" : ""}
        </p>
      </div>
    </div>
  );
}

interface ThreadItemProps {
  thread: SimpleThread;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

function ThreadItem({ thread, isActive, onSelect, onDelete }: ThreadItemProps) {
  const statusColor = {
    active: "text-blue-500",
    complete: "text-green-500",
    error: "text-red-500",
  }[thread.status];

  return (
    <div
      className={cn(
        "group flex items-center gap-2 rounded-md px-2 py-2 hover:bg-accent cursor-pointer",
        isActive && "bg-accent"
      )}
      onClick={onSelect}
    >
      <Circle className={cn("h-2 w-2 fill-current shrink-0", statusColor)} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{thread.title}</p>
        <p className="text-xs text-muted-foreground">
          {thread.messageCount} messages
        </p>
      </div>
      <Button
        size="sm"
        variant="ghost"
        className="opacity-0 group-hover:opacity-100"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
      >
        <Trash2 className="h-3 w-3" />
      </Button>
    </div>
  );
}
