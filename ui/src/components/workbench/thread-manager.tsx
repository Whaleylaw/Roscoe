"use client";

import { useState, useRef, useEffect } from "react";
import { MessageSquare, Plus, Trash2, Circle, ArrowLeft, Pencil, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useSimpleThreads, SimpleThread } from "@/hooks/use-simple-threads";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { cn } from "@/lib/utils";

export function ThreadManager() {
  const { messages, setMessages } = useWorkbenchStore();
  const { threads, activeThreadId, createThread, switchThread, deleteThread, renameThread } = useSimpleThreads(messages, setMessages);

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
                onRename={(newTitle) => renameThread(thread.id, newTitle)}
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
  onRename: (newTitle: string) => void;
}

function ThreadItem({ thread, isActive, onSelect, onDelete, onRename }: ThreadItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(thread.title);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input when editing starts
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const statusColor = {
    active: "text-blue-500",
    complete: "text-green-500",
    error: "text-red-500",
  }[thread.status];

  const handleStartEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditTitle(thread.title);
    setIsEditing(true);
  };

  const handleSaveEdit = () => {
    const trimmed = editTitle.trim();
    if (trimmed && trimmed !== thread.title) {
      onRename(trimmed);
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditTitle(thread.title);
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSaveEdit();
    } else if (e.key === "Escape") {
      handleCancelEdit();
    }
  };

  return (
    <div
      className={cn(
        "group flex items-center gap-2 rounded-md px-2 py-2 hover:bg-accent cursor-pointer",
        isActive && "bg-accent"
      )}
      onClick={isEditing ? undefined : onSelect}
    >
      <Circle className={cn("h-2 w-2 fill-current shrink-0", statusColor)} />
      <div className="flex-1 min-w-0">
        {isEditing ? (
          <div className="flex items-center gap-1">
            <input
              ref={inputRef}
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={handleSaveEdit}
              className="h-6 text-sm px-1 flex-1 min-w-0 rounded border border-input bg-background"
              onClick={(e) => e.stopPropagation()}
            />
            <Button
              size="sm"
              variant="ghost"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                handleSaveEdit();
              }}
            >
              <Check className="h-3 w-3" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-6 w-6 p-0"
              onClick={(e) => {
                e.stopPropagation();
                handleCancelEdit();
              }}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        ) : (
          <>
            <p className="text-sm font-medium truncate">{thread.title}</p>
            <p className="text-xs text-muted-foreground">
              {thread.messageCount} messages
            </p>
          </>
        )}
      </div>
      {!isEditing && (
        <>
          <Button
            size="sm"
            variant="ghost"
            className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0"
            onClick={handleStartEdit}
            title="Rename"
          >
            <Pencil className="h-3 w-3" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="opacity-0 group-hover:opacity-100 h-6 w-6 p-0"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            title="Delete"
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </>
      )}
    </div>
  );
}
