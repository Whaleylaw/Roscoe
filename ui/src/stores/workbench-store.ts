import { create } from "zustand";
import { CenterView, LeftView, OpenDocument, WorkspaceFile, Thread } from "@/types";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

type MessageUpdater = ChatMessage[] | ((prev: ChatMessage[]) => ChatMessage[]);

interface WorkbenchState {
  // View state
  centerView: CenterView;
  leftView: LeftView;
  setCenterView: (view: CenterView) => void;
  setLeftView: (view: LeftView) => void;

  // Document state
  openDocument: OpenDocument | null;
  setOpenDocument: (doc: OpenDocument | null) => void;

  // Workspace files
  workspaceFiles: WorkspaceFile[];
  setWorkspaceFiles: (files: WorkspaceFile[]) => void;
  currentPath: string;
  setCurrentPath: (path: string) => void;

  // Chat messages
  messages: ChatMessage[];
  setMessages: (messagesOrUpdater: MessageUpdater) => void;

  // Threads
  threads: Thread[];
  activeThreadId: string | null;
  setThreads: (threads: Thread[]) => void;
  setActiveThread: (id: string | null) => void;
  addThread: (thread: Thread) => void;
  updateThread: (id: string, updates: Partial<Thread>) => void;
}

export const useWorkbenchStore = create<WorkbenchState>((set, get) => ({
  // View state
  centerView: "viewer",
  leftView: "files",
  setCenterView: (view) => set({ centerView: view }),
  setLeftView: (view) => set({ leftView: view }),

  // Document state
  openDocument: null,
  setOpenDocument: (doc) => set({ openDocument: doc }),

  // Workspace files
  workspaceFiles: [],
  setWorkspaceFiles: (files) => set({ workspaceFiles: files }),
  currentPath: "/",
  setCurrentPath: (path) => set({ currentPath: path }),

  // Chat messages - supports both direct value and functional update
  messages: [],
  setMessages: (messagesOrUpdater) => {
    if (typeof messagesOrUpdater === "function") {
      set({ messages: messagesOrUpdater(get().messages) });
    } else {
      set({ messages: messagesOrUpdater });
    }
  },

  // Threads
  threads: [],
  activeThreadId: null,
  setThreads: (threads) => set({ threads }),
  setActiveThread: (id) => set({ activeThreadId: id }),
  addThread: (thread) => set((state) => ({ threads: [...state.threads, thread] })),
  updateThread: (id, updates) =>
    set((state) => ({
      threads: state.threads.map((t) => (t.id === id ? { ...t, ...updates } : t)),
    })),
}));
