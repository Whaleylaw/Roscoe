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
  // Layout state (ChatGPT/Claude style)
  leftSidebarOpen: boolean;
  rightPanelOpen: boolean;
  panelsSwapped: boolean; // When true, artifact in center, chat in right panel
  toggleLeftSidebar: () => void;
  toggleRightPanel: () => void;
  setRightPanelOpen: (open: boolean) => void;
  togglePanelsSwapped: () => void;
  setPanelsSwapped: (swapped: boolean) => void;

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

  // LangGraph thread ID (the real backend thread ID)
  langGraphThreadId: string | null;
  setLangGraphThreadId: (id: string | null) => void;
}

export const useWorkbenchStore = create<WorkbenchState>((set, get) => ({
  // Layout state (ChatGPT/Claude style) - left OPEN by default (changed from false)
  leftSidebarOpen: true,
  rightPanelOpen: false,
  panelsSwapped: false,
  toggleLeftSidebar: () => set((state) => ({ leftSidebarOpen: !state.leftSidebarOpen })),
  toggleRightPanel: () => set((state) => ({ rightPanelOpen: !state.rightPanelOpen })),
  setRightPanelOpen: (open) => set({ rightPanelOpen: open }),
  togglePanelsSwapped: () => set((state) => ({ panelsSwapped: !state.panelsSwapped, rightPanelOpen: true })),
  setPanelsSwapped: (swapped) => set({ panelsSwapped: swapped }),

  // View state
  centerView: "viewer",
  leftView: "files",
  setCenterView: (view) => set({ centerView: view }),
  setLeftView: (view) => set({ leftView: view }),

  // Document state - also opens right panel when document is set
  openDocument: null,
  setOpenDocument: (doc) => set({ openDocument: doc, rightPanelOpen: doc !== null }),

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

  // LangGraph thread ID
  langGraphThreadId: null,
  setLangGraphThreadId: (id) => set({ langGraphThreadId: id }),
}));
